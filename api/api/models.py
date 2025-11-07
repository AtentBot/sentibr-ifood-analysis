"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class SentimentLabel(str, Enum):
    """Sentiment labels"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class PredictionRequest(BaseModel):
    """Single text prediction request"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to analyze for sentiment",
        example="Eu adorei o produto, a entrega foi muito rápida!"
    )
    return_probabilities: bool = Field(
        default=False,
        description="Return probability scores for all classes"
    )
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Text cannot be empty or only whitespace")
        return v.strip()


class PredictionResponse(BaseModel):
    """Single text prediction response"""
    sentiment: SentimentLabel = Field(..., description="Predicted sentiment label")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Probability scores for all classes"
    )
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_version: str = Field(..., description="Model version used for prediction")
    
    class Config:
        schema_extra = {
            "example": {
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
        }


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    texts: List[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="List of texts to analyze"
    )
    return_probabilities: bool = Field(
        default=False,
        description="Return probability scores for all classes"
    )
    
    @validator('texts')
    def texts_not_empty(cls, v):
        if not v:
            raise ValueError("Texts list cannot be empty")
        for i, text in enumerate(v):
            if not text or text.strip() == "":
                raise ValueError(f"Text at index {i} is empty")
        return [text.strip() for text in v]


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    predictions: List[PredictionResponse] = Field(..., description="List of predictions")
    total_processing_time_ms: float = Field(..., description="Total processing time")
    batch_size: int = Field(..., description="Number of predictions")


class ComparisonRequest(BaseModel):
    """Request for BERT vs GPT comparison"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to analyze with both models"
    )
    gpt_model: str = Field(
        default="gpt-3.5-turbo",
        description="GPT model to use for comparison"
    )


class ComparisonResponse(BaseModel):
    """BERT vs GPT comparison response"""
    text: str = Field(..., description="Input text")
    bert_prediction: PredictionResponse = Field(..., description="BERT model prediction")
    gpt_prediction: Optional[Dict[str, Any]] = Field(
        default=None,
        description="GPT model prediction (if available)"
    )
    agreement: bool = Field(..., description="Whether models agree")
    processing_time_ms: float = Field(..., description="Total processing time")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_version: str = Field(..., description="Loaded model version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)
    gpu_available: bool = Field(..., description="Whether GPU is available")


class ModelInfoResponse(BaseModel):
    """Model information response"""
    model_name: str = Field(..., description="Model name")
    model_version: str = Field(..., description="Model version")
    model_type: str = Field(..., description="Model architecture")
    training_date: Optional[str] = Field(None, description="Training date")
    num_parameters: Optional[int] = Field(None, description="Number of parameters")
    classes: List[str] = Field(..., description="Output classes")
    metrics: Optional[Dict[str, float]] = Field(None, description="Model metrics")


class FeedbackRequest(BaseModel):
    """Human feedback request"""
    text: str = Field(..., description="Original text")
    predicted_sentiment: SentimentLabel = Field(..., description="Model prediction")
    predicted_score: float = Field(..., ge=0.0, le=1.0)
    correct_sentiment: SentimentLabel = Field(..., description="Human-corrected sentiment")
    user_id: Optional[str] = Field(None, description="User identifier")
    comments: Optional[str] = Field(None, description="Additional comments")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "O produto é ok",
                "predicted_sentiment": "positive",
                "predicted_score": 0.65,
                "correct_sentiment": "neutral",
                "user_id": "user123",
                "comments": "Deveria ser neutro, não positivo"
            }
        }


class FeedbackResponse(BaseModel):
    """Feedback submission response"""
    status: str = Field(..., description="Submission status")
    feedback_id: str = Field(..., description="Feedback identifier")
    message: str = Field(..., description="Confirmation message")
    timestamp: datetime = Field(default_factory=datetime.now)


class MetricsResponse(BaseModel):
    """Prometheus-style metrics response"""
    total_predictions: int = Field(..., description="Total predictions made")
    predictions_by_sentiment: Dict[str, int] = Field(..., description="Predictions per class")
    average_confidence: float = Field(..., description="Average confidence score")
    average_latency_ms: float = Field(..., description="Average processing time")
    error_rate: float = Field(..., description="Error rate")
    uptime_seconds: float = Field(..., description="Service uptime")


class ExplainRequest(BaseModel):
    """Explainability request"""
    text: str = Field(..., min_length=1, max_length=5000)
    method: str = Field(
        default="attention",
        description="Explanation method: attention, lime, or shap"
    )
    
    @validator('method')
    def validate_method(cls, v):
        allowed = ["attention", "lime", "shap"]
        if v.lower() not in allowed:
            raise ValueError(f"Method must be one of {allowed}")
        return v.lower()


class ExplainResponse(BaseModel):
    """Explainability response"""
    text: str = Field(..., description="Original text")
    sentiment: SentimentLabel = Field(..., description="Predicted sentiment")
    score: float = Field(..., description="Confidence score")
    explanation: Dict[str, Any] = Field(..., description="Explanation data")
    method: str = Field(..., description="Method used for explanation")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Produto excelente, recomendo!",
                "sentiment": "positive",
                "score": 0.95,
                "explanation": {
                    "word_importance": {
                        "excelente": 0.82,
                        "recomendo": 0.65,
                        "produto": 0.12
                    }
                },
                "method": "attention"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = Field(None, description="Request path")
