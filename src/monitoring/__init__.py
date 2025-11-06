"""
SentiBR Monitoring Module
Sistema completo de observabilidade e monitoring
"""

from .metrics import (
    # Registry
    REGISTRY,
    
    # Tracking functions
    track_request_metrics,
    track_prediction_metrics,
    track_feedback_metrics,
    track_drift_metrics,
    update_business_metrics,
    
    # Decorators
    track_time,
    count_calls,
    
    # Export
    get_metrics,
    get_content_type,
    init_metrics,
    
    # Individual metrics (para uso direto se necessário)
    http_requests_total,
    http_request_duration_seconds,
    model_predictions_total,
    model_inference_duration_seconds,
    model_data_drift_score,
    feedback_submissions_total,
)

from .drift_detector import DriftDetector, create_mock_baseline

from .logger import (
    # Loggers
    api_logger,
    model_logger,
    monitoring_logger,
    system_logger,
    
    # Helper functions
    log_request,
    log_prediction,
    log_feedback,
    log_drift,
    log_system_event,
    log_startup,
    log_shutdown,
    
    # Context
    RequestContext,
    
    # Base class
    StructuredLogger,
)

__version__ = "1.0.0"
__all__ = [
    # Metrics
    "REGISTRY",
    "track_request_metrics",
    "track_prediction_metrics",
    "track_feedback_metrics",
    "track_drift_metrics",
    "update_business_metrics",
    "track_time",
    "count_calls",
    "get_metrics",
    "get_content_type",
    "init_metrics",
    
    # Drift
    "DriftDetector",
    "create_mock_baseline",
    
    # Logging
    "api_logger",
    "model_logger",
    "monitoring_logger",
    "system_logger",
    "log_request",
    "log_prediction",
    "log_feedback",
    "log_drift",
    "log_system_event",
    "log_startup",
    "log_shutdown",
    "RequestContext",
    "StructuredLogger",
]
