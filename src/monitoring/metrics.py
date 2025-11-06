"""
Sistema de Métricas Prometheus para SentiBR
Instrumentação completa da API e do modelo
"""
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from typing import Optional, Dict, Any
import time
from functools import wraps


# ============================================
# Registry Global
# ============================================
REGISTRY = CollectorRegistry()


# ============================================
# API Metrics
# ============================================

# Contador de requisições HTTP
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

# Histograma de latência HTTP
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=REGISTRY
)

# Gauge de requisições em andamento
http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Número de requisições HTTP em andamento',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Contador de erros
http_errors_total = Counter(
    'http_errors_total',
    'Total de erros HTTP',
    ['method', 'endpoint', 'error_type'],
    registry=REGISTRY
)


# ============================================
# Model Metrics
# ============================================

# Contador de predições
model_predictions_total = Counter(
    'model_predictions_total',
    'Total de predições do modelo',
    ['sentiment', 'confidence_level'],
    registry=REGISTRY
)

# Histograma de tempo de inferência
model_inference_duration_seconds = Histogram(
    'model_inference_duration_seconds',
    'Tempo de inferência do modelo em segundos',
    ['model_type'],  # bert, gpt
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
    registry=REGISTRY
)

# Gauge de confiança média
model_prediction_confidence_avg = Gauge(
    'model_prediction_confidence_avg',
    'Confiança média das predições (últimos 5 min)',
    ['sentiment'],
    registry=REGISTRY
)

# Contador de predições por batch
model_batch_predictions_total = Counter(
    'model_batch_predictions_total',
    'Total de predições em batch',
    ['batch_size_range'],
    registry=REGISTRY
)

# Summary de confiança
model_confidence_summary = Summary(
    'model_confidence',
    'Summary estatístico da confiança',
    ['sentiment'],
    registry=REGISTRY
)


# ============================================
# Drift Metrics
# ============================================

# Gauge de drift score
model_data_drift_score = Gauge(
    'model_data_drift_score',
    'Score de drift dos dados (0-1)',
    registry=REGISTRY
)

# Gauge de KS statistic
model_feature_distribution_ks_statistic = Gauge(
    'model_feature_distribution_ks_statistic',
    'Kolmogorov-Smirnov statistic para distribuição de features',
    ['feature'],
    registry=REGISTRY
)

# Timestamp do último check de drift
model_last_drift_check_timestamp = Gauge(
    'model_last_drift_check_timestamp',
    'Timestamp do último check de drift',
    registry=REGISTRY
)


# ============================================
# Feedback Metrics
# ============================================

# Contador de feedbacks
feedback_submissions_total = Counter(
    'feedback_submissions_total',
    'Total de feedbacks submetidos',
    ['is_correct'],
    registry=REGISTRY
)

# Gauge de taxa de correção
feedback_correction_rate = Gauge(
    'feedback_correction_rate',
    'Taxa de correções via feedback',
    registry=REGISTRY
)


# ============================================
# Business Metrics
# ============================================

# Gauge de reviews processadas hoje
business_reviews_processed_today = Gauge(
    'business_reviews_processed_today',
    'Número de reviews processadas hoje',
    registry=REGISTRY
)

# Contador de sentimentos por categoria
business_sentiment_distribution = Counter(
    'business_sentiment_distribution',
    'Distribuição de sentimentos',
    ['sentiment', 'source'],  # ifood, b2w, etc
    registry=REGISTRY
)


# ============================================
# System Metrics
# ============================================

# Info do sistema
system_info = Info(
    'sentibr_system',
    'Informações do sistema SentiBR',
    registry=REGISTRY
)

# Gauge de uptime
system_uptime_seconds = Gauge(
    'system_uptime_seconds',
    'Tempo de uptime do sistema em segundos',
    registry=REGISTRY
)


# ============================================
# Helper Functions
# ============================================

def track_request_metrics(method: str, endpoint: str, status_code: int):
    """
    Registra métricas de uma requisição HTTP
    
    Args:
        method: HTTP method (GET, POST, etc)
        endpoint: Endpoint path
        status_code: HTTP status code
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status_code)
    ).inc()


def track_prediction_metrics(
    sentiment: str,
    confidence: float,
    inference_time: float,
    model_type: str = "bert"
):
    """
    Registra métricas de uma predição
    
    Args:
        sentiment: Sentimento predito (positive, negative, neutral)
        confidence: Confiança da predição (0-1)
        inference_time: Tempo de inferência em segundos
        model_type: Tipo do modelo (bert, gpt)
    """
    # Classificar nível de confiança
    if confidence >= 0.9:
        confidence_level = "high"
    elif confidence >= 0.7:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    # Incrementar contador
    model_predictions_total.labels(
        sentiment=sentiment,
        confidence_level=confidence_level
    ).inc()
    
    # Registrar tempo de inferência
    model_inference_duration_seconds.labels(
        model_type=model_type
    ).observe(inference_time)
    
    # Atualizar summary de confiança
    model_confidence_summary.labels(
        sentiment=sentiment
    ).observe(confidence)


def track_feedback_metrics(is_correct: bool):
    """
    Registra métricas de feedback
    
    Args:
        is_correct: Se a predição estava correta
    """
    feedback_submissions_total.labels(
        is_correct=str(is_correct).lower()
    ).inc()


def track_drift_metrics(drift_score: float, ks_statistics: Dict[str, float]):
    """
    Registra métricas de drift
    
    Args:
        drift_score: Score geral de drift (0-1)
        ks_statistics: Dict com KS statistic por feature
    """
    model_data_drift_score.set(drift_score)
    
    for feature, ks_stat in ks_statistics.items():
        model_feature_distribution_ks_statistic.labels(
            feature=feature
        ).set(ks_stat)
    
    model_last_drift_check_timestamp.set(time.time())


def update_business_metrics(sentiment_counts: Dict[str, int]):
    """
    Atualiza métricas de negócio
    
    Args:
        sentiment_counts: Dict com contagem de sentimentos
    """
    total = sum(sentiment_counts.values())
    business_reviews_processed_today.set(total)


def set_system_info(version: str, model_version: str, environment: str):
    """
    Define informações do sistema
    
    Args:
        version: Versão da aplicação
        model_version: Versão do modelo
        environment: Ambiente (dev, staging, production)
    """
    system_info.info({
        'version': version,
        'model_version': model_version,
        'environment': environment,
        'python_version': '3.10+'
    })


# ============================================
# Decorators
# ============================================

def track_time(metric_name: str = "function_duration"):
    """
    Decorator para medir tempo de execução de funções
    
    Args:
        metric_name: Nome da métrica
    """
    def decorator(func):
        # Criar métrica se não existir
        if not hasattr(track_time, f'_{metric_name}_histogram'):
            histogram = Histogram(
                f'{metric_name}_seconds',
                f'Duração de execução de {func.__name__}',
                registry=REGISTRY
            )
            setattr(track_time, f'_{metric_name}_histogram', histogram)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                histogram = getattr(track_time, f'_{metric_name}_histogram')
                histogram.observe(duration)
        
        return wrapper
    return decorator


def count_calls(metric_name: str = "function_calls"):
    """
    Decorator para contar chamadas de funções
    
    Args:
        metric_name: Nome da métrica
    """
    def decorator(func):
        # Criar métrica se não existir
        if not hasattr(count_calls, f'_{metric_name}_counter'):
            counter = Counter(
                f'{metric_name}_total',
                f'Total de chamadas de {func.__name__}',
                ['status'],
                registry=REGISTRY
            )
            setattr(count_calls, f'_{metric_name}_counter', counter)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            counter = getattr(count_calls, f'_{metric_name}_counter')
            try:
                result = func(*args, **kwargs)
                counter.labels(status='success').inc()
                return result
            except Exception as e:
                counter.labels(status='error').inc()
                raise
        
        return wrapper
    return decorator


# ============================================
# Export Functions
# ============================================

def get_metrics() -> bytes:
    """
    Retorna métricas em formato Prometheus
    
    Returns:
        Métricas serializadas em formato Prometheus
    """
    return generate_latest(REGISTRY)


def get_content_type() -> str:
    """
    Retorna o content type das métricas Prometheus
    
    Returns:
        Content type string
    """
    return CONTENT_TYPE_LATEST


# ============================================
# Inicialização
# ============================================

def init_metrics(version: str = "1.0.0", model_version: str = "bert-v1"):
    """
    Inicializa métricas do sistema
    
    Args:
        version: Versão da aplicação
        model_version: Versão do modelo
    """
    # Set system info
    set_system_info(
        version=version,
        model_version=model_version,
        environment="production"
    )
    
    # Inicializar uptime
    system_uptime_seconds.set_to_current_time()
    
    print(f"✅ Métricas Prometheus inicializadas")
    print(f"   - Versão: {version}")
    print(f"   - Modelo: {model_version}")
    print(f"   - Registry: {len(REGISTRY._collector_to_names)} métricas")
