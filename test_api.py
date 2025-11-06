"""
Test script for API endpoints
Run this after starting the API server
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def print_response(response, title="Response"):
    """Pretty print response"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200


def test_model_info():
    """Test model info endpoint"""
    print("\n📊 Testing Model Info...")
    response = requests.get(f"{BASE_URL}/api/v1/models/info")
    print_response(response, "Model Info")
    return response.status_code == 200


def test_predict():
    """Test single prediction"""
    print("\n🔮 Testing Single Prediction...")
    
    test_cases = [
        {
            "text": "Eu adorei o produto, a entrega foi muito rápida!",
            "return_probabilities": True
        },
        {
            "text": "Péssimo atendimento, nunca mais compro aqui",
            "return_probabilities": True
        },
        {
            "text": "O produto é ok, nada de especial",
            "return_probabilities": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Text: {test_case['text']}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/predict",
            json=test_case
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sentiment: {result['sentiment']}")
            print(f"   Score: {result['score']:.4f}")
            print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")
            if result.get('probabilities'):
                print(f"   Probabilities:")
                for label, prob in result['probabilities'].items():
                    print(f"      {label}: {prob:.4f}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    return True


def test_batch_predict():
    """Test batch prediction"""
    print("\n📦 Testing Batch Prediction...")
    
    batch_request = {
        "texts": [
            "Produto excelente!",
            "Muito ruim, não recomendo",
            "É aceitável",
            "Adorei a experiência",
            "Péssimo serviço"
        ],
        "return_probabilities": False
    }
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/predict/batch",
        json=batch_request
    )
    elapsed_time = (time.time() - start_time) * 1000
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Batch Size: {result['batch_size']}")
        print(f"   Total Time: {result['total_processing_time_ms']:.2f}ms")
        print(f"   Network Time: {elapsed_time:.2f}ms")
        print(f"   Avg per text: {result['total_processing_time_ms']/result['batch_size']:.2f}ms")
        print("\n   Predictions:")
        for i, pred in enumerate(result['predictions'], 1):
            print(f"      {i}. {pred['sentiment']} (score: {pred['score']:.4f})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return response.status_code == 200


def test_explain():
    """Test explainability endpoint"""
    print("\n🔍 Testing Explainability...")
    
    explain_request = {
        "text": "Produto excelente, recomendo muito!",
        "method": "attention"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/explain",
        json=explain_request
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sentiment: {result['sentiment']}")
        print(f"   Score: {result['score']:.4f}")
        print(f"   Method: {result['method']}")
        print("\n   Top Important Words:")
        if 'explanation' in result and 'word_importance' in result['explanation']:
            for word, importance in list(result['explanation']['word_importance'].items())[:5]:
                print(f"      {word}: {importance:.4f}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return response.status_code == 200


def test_feedback():
    """Test feedback endpoint"""
    print("\n💬 Testing Feedback Submission...")
    
    feedback_request = {
        "text": "O produto é ok",
        "predicted_sentiment": "positive",
        "predicted_score": 0.65,
        "correct_sentiment": "neutral",
        "user_id": "test_user",
        "comments": "Deveria ser neutro, não positivo"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/feedback",
        json=feedback_request
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Feedback ID: {result['feedback_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return response.status_code == 200


def test_metrics():
    """Test metrics endpoint"""
    print("\n📈 Testing Metrics...")
    
    response = requests.get(f"{BASE_URL}/api/v1/metrics")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Total Predictions: {result['total_predictions']}")
        print(f"   Average Confidence: {result['average_confidence']:.4f}")
        print(f"   Average Latency: {result['average_latency_ms']:.2f}ms")
        print(f"   Error Rate: {result['error_rate']:.4f}")
        print(f"   Uptime: {result['uptime_seconds']:.2f}s")
        print("\n   Predictions by Sentiment:")
        for sentiment, count in result['predictions_by_sentiment'].items():
            print(f"      {sentiment}: {count}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return response.status_code == 200


def test_error_handling():
    """Test error handling"""
    print("\n⚠️  Testing Error Handling...")
    
    # Test 1: Empty text
    print("\n--- Test: Empty Text ---")
    response = requests.post(
        f"{BASE_URL}/api/v1/predict",
        json={"text": ""}
    )
    print(f"Status: {response.status_code} (expected: 422)")
    
    # Test 2: Missing field
    print("\n--- Test: Missing Field ---")
    response = requests.post(
        f"{BASE_URL}/api/v1/predict",
        json={}
    )
    print(f"Status: {response.status_code} (expected: 422)")
    
    # Test 3: Invalid JSON
    print("\n--- Test: Invalid JSON ---")
    response = requests.post(
        f"{BASE_URL}/api/v1/predict",
        data="invalid json"
    )
    print(f"Status: {response.status_code} (expected: 422)")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🚀 SENTIMENT ANALYSIS API - TEST SUITE")
    print("="*80)
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ API is not running or not accessible")
            print("Please start the API with: uvicorn src.api.main:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at", BASE_URL)
        print("Please start the API with: uvicorn src.api.main:app --reload")
        return
    
    print("✅ API is running")
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Single Prediction", test_predict),
        ("Batch Prediction", test_batch_predict),
        ("Explainability", test_explain),
        ("Feedback", test_feedback),
        ("Metrics", test_metrics),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} failed with error: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()
