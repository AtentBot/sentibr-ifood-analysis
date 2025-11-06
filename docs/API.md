# API Documentation

## Sentiment Analysis API v1.0.0

Production-ready REST API for sentiment analysis using fine-tuned BERT model.

---

## 🚀 Quick Start

### 1. Start the API

```bash
# From project root
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. Test the API

```bash
python test_api.py
```

---

## 📡 Endpoints

### Core Endpoints

#### 1. Health Check
```
GET /health
```

Returns service health status and model information.

**Response Example:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "bert-sentiment-v1.0",
  "uptime_seconds": 3600.5,
  "gpu_available": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

---

#### 2. Single Prediction
```
POST /api/v1/predict
```

Predict sentiment for a single text.

**Request Body:**
```json
{
  "text": "Eu adorei o produto, a entrega foi muito rápida!",
  "return_probabilities": true
}
```

**Response Example:**
```json
{
  "sentiment": "positive",
  "score": 0.98,
  "probabilities": {
    "positive": 0.98,
    "negative": 0.01,
    "neutral": 0.01
  },
  "processing_time_ms": 45.2,
  "model_version": "bert-sentiment-v1.0"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Produto excelente!", "return_probabilities": true}'
```

---

#### 3. Batch Prediction
```
POST /api/v1/predict/batch
```

Predict sentiment for multiple texts efficiently.

**Request Body:**
```json
{
  "texts": [
    "Produto excelente!",
    "Muito ruim",
    "É ok"
  ],
  "return_probabilities": false
}
```

**Response Example:**
```json
{
  "predictions": [
    {
      "sentiment": "positive",
      "score": 0.95,
      "processing_time_ms": 15.3,
      "model_version": "bert-sentiment-v1.0"
    },
    {
      "sentiment": "negative",
      "score": 0.92,
      "processing_time_ms": 14.8,
      "model_version": "bert-sentiment-v1.0"
    },
    {
      "sentiment": "neutral",
      "score": 0.78,
      "processing_time_ms": 15.1,
      "model_version": "bert-sentiment-v1.0"
    }
  ],
  "total_processing_time_ms": 45.2,
  "batch_size": 3
}
```

**Benefits:**
- ~3x faster than individual requests
- Optimized batch processing
- Better resource utilization

---

#### 4. Model Information
```
GET /api/v1/models/info
```

Get detailed model metadata.

**Response Example:**
```json
{
  "model_name": "BERT Sentiment Classifier",
  "model_version": "bert-sentiment-v1.0",
  "model_type": "bert",
  "training_date": "2024-01-15",
  "num_parameters": 110617091,
  "classes": ["positive", "negative", "neutral"],
  "metrics": {
    "accuracy": 0.92,
    "f1_score": 0.91
  }
}
```

---

### Advanced Endpoints (Differentials)

#### 5. Model Comparison
```
POST /api/v1/predict/compare
```

🌟 **DIFFERENTIAL FEATURE**: Compare BERT with GPT predictions

**Request Body:**
```json
{
  "text": "O produto é muito bom",
  "gpt_model": "gpt-3.5-turbo"
}
```

**Use Cases:**
- Validate model predictions
- Compare different approaches
- Ensemble methods
- A/B testing

---

#### 6. Explainability
```
POST /api/v1/explain
```

🌟 **DIFFERENTIAL FEATURE**: Get prediction explanations

**Request Body:**
```json
{
  "text": "Produto excelente, recomendo!",
  "method": "attention"
}
```

**Response Example:**
```json
{
  "text": "Produto excelente, recomendo!",
  "sentiment": "positive",
  "score": 0.95,
  "explanation": {
    "method": "attention",
    "word_importance": {
      "excelente": 0.82,
      "recomendo": 0.65,
      "produto": 0.12
    }
  },
  "method": "attention"
}
```

**Supported Methods:**
- `attention`: BERT attention weights (default)
- `lime`: LIME explanations (coming soon)
- `shap`: SHAP values (coming soon)

---

#### 7. Human Feedback
```
POST /api/v1/feedback
```

🌟 **DIFFERENTIAL FEATURE**: Human-in-the-loop feedback

**Request Body:**
```json
{
  "text": "O produto é ok",
  "predicted_sentiment": "positive",
  "predicted_score": 0.65,
  "correct_sentiment": "neutral",
  "user_id": "user123",
  "comments": "Deveria ser neutro"
}
```

**Benefits:**
- Collect training data
- Identify model errors
- Continuous improvement
- Error analysis

---

#### 8. Metrics
```
GET /api/v1/metrics
```

🌟 **DIFFERENTIAL FEATURE**: Comprehensive metrics

**Response Example:**
```json
{
  "total_predictions": 1000,
  "predictions_by_sentiment": {
    "positive": 450,
    "negative": 300,
    "neutral": 250
  },
  "average_confidence": 0.87,
  "average_latency_ms": 45.2,
  "error_rate": 0.01,
  "uptime_seconds": 86400
}
```

---

#### 9. Prometheus Metrics
```
GET /api/v1/metrics/prometheus
```

🌟 **DIFFERENTIAL FEATURE**: Prometheus integration

Returns metrics in Prometheus text format for monitoring.

**Example Output:**
```
# HELP total_predictions Total number of predictions made
# TYPE total_predictions counter
total_predictions 1000

# HELP average_confidence Average confidence score of predictions
# TYPE average_confidence gauge
average_confidence 0.87
```

---

## 🔒 Security & Rate Limiting

### Rate Limits
- **Default**: 100 requests per minute per IP
- **Batch endpoint**: Max 100 texts per request
- **Response headers**:
  - `X-RateLimit-Limit`: Total limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

### Error Responses

All errors follow this format:

```json
{
  "error": "Error Type",
  "message": "Human-readable message",
  "detail": "Detailed error information",
  "timestamp": "2024-01-15T10:30:00",
  "path": "/api/v1/predict"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request
- `422`: Validation Error
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error
- `503`: Service Unavailable

---

## 🎯 Best Practices

### 1. Use Batch Predictions
```python
# ❌ Bad: Multiple individual requests
for text in texts:
    response = requests.post("/api/v1/predict", json={"text": text})

# ✅ Good: Single batch request
response = requests.post("/api/v1/predict/batch", json={"texts": texts})
```

### 2. Handle Errors Gracefully
```python
try:
    response = requests.post("/api/v1/predict", json={"text": text})
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 3. Monitor Performance
```python
# Check health regularly
health = requests.get("/health").json()
if not health["model_loaded"]:
    print("Model not loaded!")

# Monitor metrics
metrics = requests.get("/api/v1/metrics").json()
if metrics["error_rate"] > 0.05:
    print("High error rate detected!")
```

---

## 📊 Performance

### Latency
- **Single prediction**: ~45ms (CPU) / ~20ms (GPU)
- **Batch prediction (10 texts)**: ~80ms (CPU) / ~35ms (GPU)
- **Average per text in batch**: ~8ms (CPU) / ~3.5ms (GPU)

### Throughput
- **Single requests**: ~20 req/s (CPU) / ~50 req/s (GPU)
- **Batch requests**: ~120 texts/s (CPU) / ~280 texts/s (GPU)

### Resource Usage
- **Memory**: ~2GB (model + API)
- **CPU**: 1-2 cores recommended
- **GPU**: Optional, 4GB+ VRAM

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1

# Model Configuration
MODEL_PATH=/path/to/model
MODEL_VERSION=v1.0

# Rate Limiting
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# OpenAI (optional, for comparison)
OPENAI_API_KEY=your_key_here
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t sentiment-api:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/models \
  -e MODEL_PATH=/models/bert_finetuned \
  sentiment-api:latest
```

---

## 📈 Monitoring Integration

### Prometheus
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'sentiment-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics/prometheus'
    scrape_interval: 15s
```

### Grafana
Import the dashboard from `monitoring/grafana-dashboard.json`

---

## 🧪 Testing

### Unit Tests
```bash
pytest tests/unit/test_api_endpoints.py -v
```

### Integration Tests
```bash
pytest tests/integration/test_api_workflow.py -v
```

### Load Tests
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## 📚 Additional Resources

- **Swagger UI**: Interactive API documentation
- **ReDoc**: Alternative documentation
- **GitHub**: Source code and examples
- **Issues**: Bug reports and feature requests

---

## 🆘 Support

For issues or questions:
1. Check the documentation
2. Review examples in `test_api.py`
3. Open an issue on GitHub
4. Contact: sentiment@example.com

---

## 📝 Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Core prediction endpoints
- Batch processing
- Model comparison
- Explainability
- Human feedback
- Prometheus metrics
- Rate limiting
- Comprehensive error handling
