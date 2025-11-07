"""
Middleware for logging, metrics, and error handling
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
import json
from typing import Dict, Any
from datetime import datetime
import traceback
from collections import defaultdict
import asyncio

from api.api.models import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses
    Logs in structured JSON format
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}"
        
        # Start time
        start_time = time.time()
        
        # Log request
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        logger.info(f"REQUEST: {json.dumps(request_data)}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            response_data = {
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            }
            
            logger.info(f"RESPONSE: {json.dumps(response_data)}")
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error
            error_data = {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "process_time_ms": round(process_time * 1000, 2),
                "traceback": traceback.format_exc()
            }
            
            logger.error(f"ERROR: {json.dumps(error_data)}")
            
            # Re-raise the exception
            raise


class MetricsCollector:
    """
    Singleton class for collecting metrics
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize metrics storage"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.predictions_by_sentiment = defaultdict(int)
        self.total_processing_time = 0.0
        self.request_latencies = []
        self.start_time = time.time()
        self.endpoint_counters = defaultdict(int)
        self.error_counters = defaultdict(int)
        self.confidence_scores = []
    
    def record_request(self, endpoint: str, method: str):
        """Record a request"""
        self.total_requests += 1
        self.endpoint_counters[f"{method}:{endpoint}"] += 1
    
    def record_success(self, latency_ms: float):
        """Record a successful request"""
        self.successful_requests += 1
        self.total_processing_time += latency_ms
        self.request_latencies.append(latency_ms)
        
        # Keep only last 1000 latencies
        if len(self.request_latencies) > 1000:
            self.request_latencies = self.request_latencies[-1000:]
    
    def record_failure(self, error_type: str):
        """Record a failed request"""
        self.failed_requests += 1
        self.error_counters[error_type] += 1
    
    def record_prediction(self, sentiment: str, confidence: float):
        """Record a prediction"""
        self.predictions_by_sentiment[sentiment] += 1
        self.confidence_scores.append(confidence)
        
        # Keep only last 1000 confidence scores
        if len(self.confidence_scores) > 1000:
            self.confidence_scores = self.confidence_scores[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time
        avg_latency = (
            sum(self.request_latencies) / len(self.request_latencies)
            if self.request_latencies else 0.0
        )
        avg_confidence = (
            sum(self.confidence_scores) / len(self.confidence_scores)
            if self.confidence_scores else 0.0
        )
        error_rate = (
            self.failed_requests / self.total_requests
            if self.total_requests > 0 else 0.0
        )
        
        return {
            "total_predictions": self.total_requests,
            "predictions_by_sentiment": dict(self.predictions_by_sentiment),
            "average_confidence": round(avg_confidence, 4),
            "average_latency_ms": round(avg_latency, 2),
            "error_rate": round(error_rate, 4),
            "uptime_seconds": round(uptime, 2),
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "endpoints": dict(self.endpoint_counters),
            "errors": dict(self.error_counters)
        }
    
    def get_prometheus_metrics(self) -> str:
        """
        Get metrics in Prometheus format
        
        Returns:
            String with Prometheus-formatted metrics
        """
        metrics = self.get_metrics()
        
        lines = [
            "# HELP total_predictions Total number of predictions made",
            "# TYPE total_predictions counter",
            f"total_predictions {metrics['total_predictions']}",
            "",
            "# HELP successful_requests Total number of successful requests",
            "# TYPE successful_requests counter",
            f"successful_requests {metrics['successful_requests']}",
            "",
            "# HELP failed_requests Total number of failed requests",
            "# TYPE failed_requests counter",
            f"failed_requests {metrics['failed_requests']}",
            "",
            "# HELP average_confidence Average confidence score of predictions",
            "# TYPE average_confidence gauge",
            f"average_confidence {metrics['average_confidence']}",
            "",
            "# HELP average_latency_ms Average request latency in milliseconds",
            "# TYPE average_latency_ms gauge",
            f"average_latency_ms {metrics['average_latency_ms']}",
            "",
            "# HELP error_rate Request error rate",
            "# TYPE error_rate gauge",
            f"error_rate {metrics['error_rate']}",
            "",
            "# HELP uptime_seconds Service uptime in seconds",
            "# TYPE uptime_seconds counter",
            f"uptime_seconds {metrics['uptime_seconds']}",
            ""
        ]
        
        # Add predictions by sentiment
        for sentiment, count in metrics['predictions_by_sentiment'].items():
            lines.extend([
                f"# HELP predictions_{sentiment} Number of {sentiment} predictions",
                f"# TYPE predictions_{sentiment} counter",
                f"predictions_{sentiment} {count}",
                ""
            ])
        
        return "\n".join(lines)


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Exception handlers
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    metrics_collector.record_failure(f"HTTP_{exc.status_code}")
    
    error_response = ErrorResponse(
        error=f"HTTP {exc.status_code}",
        message=exc.detail,
        detail=None,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    metrics_collector.record_failure("ValidationError")
    
    error_response = ErrorResponse(
        error="Validation Error",
        message="Request validation failed",
        detail=str(exc.errors()),
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    metrics_collector.record_failure(type(exc).__name__)
    
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    
    error_response = ErrorResponse(
        error="Internal Server Error",
        message="An unexpected error occurred",
        detail=str(exc) if logger.level == logging.DEBUG else None,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    Limits requests per IP address
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(list)
        self._cleanup_task = None
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        now = time.time()
        
        # Clean old requests
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if now - timestamp < self.period
        ]
        
        # Check if limit exceeded
        if len(self.clients[client_ip]) >= self.calls:
            error_response = ErrorResponse(
                error="Rate Limit Exceeded",
                message=f"Too many requests. Limit: {self.calls} per {self.period} seconds",
                detail=f"Please wait {self.period} seconds before making more requests",
                path=request.url.path
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=error_response.dict(),
                headers={"Retry-After": str(self.period)}
            )
        
        # Add current request
        self.clients[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.calls - len(self.clients[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + self.period))
        
        return response


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return metrics_collector
