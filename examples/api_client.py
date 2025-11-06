"""
Python client for Sentiment Analysis API
Simplifies API usage with a clean interface
"""
import requests
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


class SentimentAPIClient:
    """
    Client for interacting with Sentiment Analysis API
    
    Example:
        client = SentimentAPIClient("http://localhost:8000")
        result = client.predict("Produto excelente!")
        print(result['sentiment'], result['score'])
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.json() if e.response.text else {}
            raise Exception(
                f"API Error {e.response.status_code}: {error_detail.get('message', str(e))}"
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def health(self) -> Dict[str, Any]:
        """
        Check API health
        
        Returns:
            Health status
        """
        return self._request("GET", "/health")
    
    def predict(
        self,
        text: str,
        return_probabilities: bool = False
    ) -> Dict[str, Any]:
        """
        Predict sentiment for a single text
        
        Args:
            text: Text to analyze
            return_probabilities: Return probability scores for all classes
            
        Returns:
            Prediction result with sentiment, score, and optional probabilities
        """
        data = {
            "text": text,
            "return_probabilities": return_probabilities
        }
        
        return self._request("POST", "/api/v1/predict", data=data)
    
    def predict_batch(
        self,
        texts: List[str],
        return_probabilities: bool = False
    ) -> Dict[str, Any]:
        """
        Predict sentiment for multiple texts
        
        Args:
            texts: List of texts to analyze
            return_probabilities: Return probability scores for all classes
            
        Returns:
            Batch prediction results
        """
        data = {
            "texts": texts,
            "return_probabilities": return_probabilities
        }
        
        return self._request("POST", "/api/v1/predict/batch", data=data)
    
    def compare(
        self,
        text: str,
        gpt_model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """
        Compare BERT prediction with GPT
        
        Args:
            text: Text to analyze
            gpt_model: GPT model to use
            
        Returns:
            Comparison results
        """
        data = {
            "text": text,
            "gpt_model": gpt_model
        }
        
        return self._request("POST", "/api/v1/predict/compare", data=data)
    
    def explain(
        self,
        text: str,
        method: str = "attention"
    ) -> Dict[str, Any]:
        """
        Get explanation for prediction
        
        Args:
            text: Text to analyze
            method: Explanation method (attention, lime, shap)
            
        Returns:
            Explanation results
        """
        data = {
            "text": text,
            "method": method
        }
        
        return self._request("POST", "/api/v1/explain", data=data)
    
    def submit_feedback(
        self,
        text: str,
        predicted_sentiment: str,
        predicted_score: float,
        correct_sentiment: str,
        user_id: Optional[str] = None,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit human feedback
        
        Args:
            text: Original text
            predicted_sentiment: Model prediction
            predicted_score: Prediction confidence
            correct_sentiment: Correct sentiment
            user_id: Optional user identifier
            comments: Optional comments
            
        Returns:
            Feedback submission result
        """
        data = {
            "text": text,
            "predicted_sentiment": predicted_sentiment,
            "predicted_score": predicted_score,
            "correct_sentiment": correct_sentiment,
            "user_id": user_id,
            "comments": comments
        }
        
        return self._request("POST", "/api/v1/feedback", data=data)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get API metrics
        
        Returns:
            Metrics data
        """
        return self._request("GET", "/api/v1/metrics")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Model metadata
        """
        return self._request("GET", "/api/v1/models/info")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed service status
        
        Returns:
            Service status
        """
        return self._request("GET", "/api/v1/status")
    
    # Convenience methods
    
    def is_healthy(self) -> bool:
        """
        Check if API is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            health = self.health()
            return health.get("status") == "healthy"
        except:
            return False
    
    def predict_sentiment(self, text: str) -> str:
        """
        Get just the sentiment label (shortcut)
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment label (positive, negative, neutral)
        """
        result = self.predict(text)
        return result['sentiment']
    
    def predict_with_confidence(self, text: str) -> tuple:
        """
        Get sentiment and confidence (shortcut)
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment, confidence_score)
        """
        result = self.predict(text)
        return result['sentiment'], result['score']


# Exemplo de uso
if __name__ == "__main__":
    # Criar cliente
    client = SentimentAPIClient("http://localhost:8000")
    
    print("="*80)
    print("🤖 SENTIMENT ANALYSIS API - CLIENT EXAMPLE")
    print("="*80)
    
    # 1. Health Check
    print("\n1️⃣ Health Check")
    print("-" * 80)
    try:
        health = client.health()
        print(f"Status: {health['status']}")
        print(f"Model Version: {health['model_version']}")
        print(f"GPU Available: {health['gpu_available']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Single Prediction
    print("\n2️⃣ Single Prediction")
    print("-" * 80)
    text = "Eu adorei o produto, a entrega foi muito rápida!"
    print(f"Text: {text}")
    try:
        result = client.predict(text, return_probabilities=True)
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['score']:.2%}")
        print(f"Processing Time: {result['processing_time_ms']:.2f}ms")
        if result['probabilities']:
            print("Probabilities:")
            for label, prob in result['probabilities'].items():
                print(f"  {label}: {prob:.2%}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Batch Prediction
    print("\n3️⃣ Batch Prediction")
    print("-" * 80)
    texts = [
        "Produto excelente!",
        "Muito ruim, não recomendo",
        "É ok, nada de especial"
    ]
    print(f"Texts: {len(texts)} samples")
    try:
        result = client.predict_batch(texts)
        print(f"Batch Size: {result['batch_size']}")
        print(f"Total Time: {result['total_processing_time_ms']:.2f}ms")
        print(f"Avg per text: {result['total_processing_time_ms']/result['batch_size']:.2f}ms")
        print("\nResults:")
        for i, pred in enumerate(result['predictions']):
            print(f"  {i+1}. {pred['sentiment']} (score: {pred['score']:.2%})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 4. Explanation
    print("\n4️⃣ Explainability")
    print("-" * 80)
    text = "Produto excelente, recomendo muito!"
    print(f"Text: {text}")
    try:
        result = client.explain(text)
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confidence: {result['score']:.2%}")
        print("Top Important Words:")
        if 'explanation' in result and 'word_importance' in result['explanation']:
            for word, importance in list(result['explanation']['word_importance'].items())[:5]:
                print(f"  {word}: {importance:.4f}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 5. Metrics
    print("\n5️⃣ Metrics")
    print("-" * 80)
    try:
        metrics = client.get_metrics()
        print(f"Total Predictions: {metrics['total_predictions']}")
        print(f"Average Confidence: {metrics['average_confidence']:.2%}")
        print(f"Average Latency: {metrics['average_latency_ms']:.2f}ms")
        print(f"Error Rate: {metrics['error_rate']:.2%}")
        print(f"Uptime: {metrics['uptime_seconds']:.2f}s")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 6. Convenience Methods
    print("\n6️⃣ Convenience Methods")
    print("-" * 80)
    try:
        # Just get sentiment
        sentiment = client.predict_sentiment("Ótimo produto!")
        print(f"Quick sentiment: {sentiment}")
        
        # Get sentiment + confidence
        sentiment, confidence = client.predict_with_confidence("Péssimo serviço")
        print(f"Quick prediction: {sentiment} ({confidence:.2%})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ Example completed!")
    print("="*80)
