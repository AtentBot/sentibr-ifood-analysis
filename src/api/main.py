"""
FastAPI application for sentiment analysis
Production-ready API with comprehensive endpoints
"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any
import json
from pathlib import Path

from src.api.models import (
    PredictionRequest, PredictionResponse,
    BatchPredictionRequest, BatchPredictionResponse,
    ComparisonRequest, ComparisonResponse,
    HealthResponse, ModelInfoResponse,
    FeedbackRequest, FeedbackResponse,
    MetricsResponse,
    ExplainRequest, ExplainResponse,
    ErrorResponse
)
from src.api.inference import get_predictor
from src.api.middleware import (
    RequestLoggingMiddleware,
    metrics_collector,
    get_metrics_collector,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    RateLimitMiddleware
)

# Configure logging
logger = logging.getLogger(__name__)

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    Handles startup and shutdown
    """
    # Startup
    logger.info("Starting up Sentiment Analysis API...")
    logger.info("Loading ML model...")
    
    try:
        predictor = get_predictor()
        logger.info(f"Model loaded successfully: {predictor.model_version}")
        logger.info(f"Using device: {predictor.device}")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise
    
    logger.info("API is ready to accept requests!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sentiment Analysis API...")
    logger.info("Final metrics:")
    metrics = metrics_collector.get_metrics()
    logger.info(json.dumps(metrics, indent=2))


# Create FastAPI app
app = FastAPI(
    title="Sentiment Analysis API",
    description="""
    **Production-ready API for sentiment analysis using fine-tuned BERT model.**
    
    ## Features
    - Single and batch predictions
    - Model comparison (BERT vs GPT)
    - Explainability (attention weights, LIME, SHAP)
    - Human feedback collection
    - Comprehensive monitoring and metrics
    - Rate limiting and error handling
    
    ## Model Information
    - **Architecture**: BERT (Bidirectional Encoder Representations from Transformers)
    - **Task**: Text Classification (Sentiment Analysis)
    - **Classes**: Positive, Negative, Neutral
    - **Language**: Portuguese
    
    ## Getting Started
    1. Try the `/predict` endpoint for single predictions
    2. Use `/predict/batch` for multiple texts
    3. Check `/health` for service status
    4. Monitor metrics at `/metrics`
    
    ## Rate Limits
    - 100 requests per minute per IP
    - Batch predictions: max 100 texts per request
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Sentiment Analysis Team",
        "email": "sentiment@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# ============================================================================
# MAIN ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Sentiment Analysis API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "predict": "/api/v1/predict",
            "batch_predict": "/api/v1/predict/batch",
            "compare": "/api/v1/predict/compare",
            "explain": "/api/v1/explain",
            "feedback": "/api/v1/feedback",
            "metrics": "/api/v1/metrics",
            "model_info": "/api/v1/models/info"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns service status and model information
    """
    try:
        predictor = get_predictor()
        metrics = metrics_collector.get_metrics()
        
        return HealthResponse(
            status="healthy",
            model_loaded=predictor.is_loaded,
            model_version=predictor.model_version,
            uptime_seconds=metrics["uptime_seconds"],
            gpu_available="cuda" in predictor.device
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest):
    """
    Predict sentiment for a single text
    
    - **text**: Text to analyze (required, 1-5000 characters)
    - **return_probabilities**: Return probability scores for all classes (optional)
    
    Returns:
    - **sentiment**: Predicted sentiment label
    - **score**: Confidence score (0-1)
    - **probabilities**: Probability scores for all classes (if requested)
    - **processing_time_ms**: Processing time in milliseconds
    - **model_version**: Model version used
    """
    metrics_collector.record_request("/api/v1/predict", "POST")
    start_time = time.time()
    
    try:
        predictor = get_predictor()
        
        # Make prediction
        result = predictor.predict(
            text=request.text,
            return_probabilities=request.return_probabilities
        )
        
        # Record metrics
        latency = (time.time() - start_time) * 1000
        metrics_collector.record_success(latency)
        metrics_collector.record_prediction(result["sentiment"], result["score"])
        
        return PredictionResponse(**result)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        metrics_collector.record_failure(type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/api/v1/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict sentiment for multiple texts in batch
    
    - **texts**: List of texts to analyze (1-100 texts)
    - **return_probabilities**: Return probability scores for all classes (optional)
    
    Returns list of predictions with total processing time
    
    **Note**: Batch processing is more efficient than individual requests
    """
    metrics_collector.record_request("/api/v1/predict/batch", "POST")
    start_time = time.time()
    
    try:
        predictor = get_predictor()
        
        # Make batch predictions
        results = predictor.predict_batch(
            texts=request.texts,
            return_probabilities=request.return_probabilities
        )
        
        # Convert to response models
        predictions = [PredictionResponse(**result) for result in results]
        
        # Calculate total time
        total_time = (time.time() - start_time) * 1000
        
        # Record metrics
        metrics_collector.record_success(total_time)
        for result in results:
            metrics_collector.record_prediction(result["sentiment"], result["score"])
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_processing_time_ms=total_time,
            batch_size=len(predictions)
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        metrics_collector.record_failure(type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.get("/api/v1/models/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """
    Get information about the loaded model
    
    Returns model metadata including:
    - Architecture details
    - Number of parameters
    - Supported classes
    - Training metrics (if available)
    """
    try:
        predictor = get_predictor()
        model_info = predictor.get_model_info()
        
        # Try to load additional info from file
        # Try multiple possible locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "models" / "bert_finetuned" / "model_info.json",
            Path("models/bert_finetuned/model_info.json"),
        ]
        
        model_info_path = None
        for path in possible_paths:
            if path.exists():
                model_info_path = path
                break
        if model_info_path.exists():
            with open(model_info_path, 'r') as f:
                file_info = json.load(f)
                model_info.update({
                    "training_date": file_info.get("training_date"),
                    "metrics": file_info.get("metrics")
                })
        
        return ModelInfoResponse(**model_info)
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model info: {str(e)}"
        )


# ============================================================================
# ADVANCED ENDPOINTS (DIFFERENTIALS)
# ============================================================================

@app.post("/api/v1/predict/compare", response_model=ComparisonResponse, tags=["Advanced"])
async def compare_predictions(request: ComparisonRequest):
    """
    Compare BERT predictions with GPT predictions
    
    **DIFFERENTIAL FEATURE**: Compare fine-tuned BERT with GPT models
    
    - **text**: Text to analyze
    - **gpt_model**: GPT model to use (default: gpt-3.5-turbo)
    
    Returns predictions from both models and agreement status
    
    **Note**: Requires OpenAI API key for GPT predictions
    """
    metrics_collector.record_request("/api/v1/predict/compare", "POST")
    start_time = time.time()
    
    try:
        predictor = get_predictor()
        
        # Get BERT prediction
        bert_result = predictor.predict(text=request.text, return_probabilities=True)
        bert_prediction = PredictionResponse(**bert_result)
        
        # GPT prediction (mock for now - can be implemented later)
        gpt_prediction = {
            "sentiment": "Not implemented",
            "message": "GPT comparison requires OpenAI API key",
            "note": "Set OPENAI_API_KEY environment variable to enable"
        }
        
        # Check agreement (mock)
        agreement = False
        
        total_time = (time.time() - start_time) * 1000
        
        return ComparisonResponse(
            text=request.text,
            bert_prediction=bert_prediction,
            gpt_prediction=gpt_prediction,
            agreement=agreement,
            processing_time_ms=total_time
        )
        
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}"
        )


@app.post("/api/v1/feedback", response_model=FeedbackResponse, tags=["Advanced"])
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit human feedback for model predictions
    
    **DIFFERENTIAL FEATURE**: Human-in-the-loop feedback collection
    
    Collects human feedback to:
    - Identify model errors
    - Improve model through retraining
    - Track model performance over time
    
    Feedback is stored and can be used for:
    - Model retraining
    - Error analysis
    - Performance monitoring
    """
    try:
        # Generate feedback ID
        feedback_id = str(uuid.uuid4())
        
        # Save feedback to file
        feedback_dir = Path(__file__).parent.parent.parent / "data" / "feedback"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        
        feedback_data = {
            "feedback_id": feedback_id,
            "timestamp": datetime.now().isoformat(),
            **feedback.dict()
        }
        
        feedback_file = feedback_dir / f"feedback_{feedback_id}.json"
        with open(feedback_file, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        logger.info(f"Feedback received: {feedback_id}")
        
        return FeedbackResponse(
            status="success",
            feedback_id=feedback_id,
            message="Thank you for your feedback! It will be used to improve the model."
        )
        
    except Exception as e:
        logger.error(f"Feedback submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@app.get("/api/v1/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_metrics():
    """
    Get API metrics
    
    **DIFFERENTIAL FEATURE**: Comprehensive metrics collection
    
    Returns:
    - Total predictions made
    - Predictions by sentiment class
    - Average confidence score
    - Average latency
    - Error rate
    - Service uptime
    
    These metrics can be scraped by Prometheus for monitoring
    """
    try:
        metrics = metrics_collector.get_metrics()
        return MetricsResponse(**metrics)
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


@app.get("/api/v1/metrics/prometheus", response_class=PlainTextResponse, tags=["Monitoring"])
async def get_prometheus_metrics():
    """
    Get metrics in Prometheus format
    
    **DIFFERENTIAL FEATURE**: Prometheus integration
    
    Returns metrics in Prometheus text format for scraping.
    Configure Prometheus to scrape this endpoint for monitoring.
    """
    try:
        metrics_text = metrics_collector.get_prometheus_metrics()
        return PlainTextResponse(content=metrics_text)
        
    except Exception as e:
        logger.error(f"Error getting Prometheus metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Prometheus metrics: {str(e)}"
        )


@app.post("/api/v1/explain", response_model=ExplainResponse, tags=["Advanced"])
async def explain_prediction(request: ExplainRequest):
    """
    Get explanation for model prediction
    
    **DIFFERENTIAL FEATURE**: Model explainability
    
    - **text**: Text to analyze
    - **method**: Explanation method (attention, lime, or shap)
    
    Returns:
    - Prediction
    - Explanation data (word importance, attention weights, etc.)
    
    **Note**: Currently supports attention weights. LIME and SHAP require additional setup.
    """
    try:
        predictor = get_predictor()
        
        if request.method == "attention":
            # Get attention weights
            result = predictor.get_attention_weights(request.text)
            
            explanation = {
                "method": "attention",
                "word_importance": result["top_tokens"],
                "description": "Attention weights from BERT's last layer"
            }
            
            return ExplainResponse(
                text=request.text,
                sentiment=result["sentiment"],
                score=result["score"],
                explanation=explanation,
                method=request.method
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Method '{request.method}' not yet implemented. Currently only 'attention' is supported."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation failed: {str(e)}"
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/api/v1/version", tags=["Info"])
async def get_version():
    """Get API version information"""
    return {
        "api_version": "1.0.0",
        "model_version": get_predictor().model_version,
        "framework": "FastAPI",
        "python_version": "3.9+"
    }


@app.get("/api/v1/status", tags=["Info"])
async def get_status():
    """Get detailed service status"""
    try:
        predictor = get_predictor()
        metrics = metrics_collector.get_metrics()
        
        return {
            "service": "operational",
            "model": {
                "loaded": predictor.is_loaded,
                "version": predictor.model_version,
                "device": predictor.device
            },
            "metrics": {
                "total_predictions": metrics["total_predictions"],
                "uptime_seconds": metrics["uptime_seconds"],
                "average_latency_ms": metrics["average_latency_ms"],
                "error_rate": metrics["error_rate"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "service": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
