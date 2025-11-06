"""
Sistema de Logging Estruturado para SentiBR
Logging em formato JSON com contexto e metadata
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import traceback


class JSONFormatter(logging.Formatter):
    """
    Formatter que serializa logs em JSON
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formata log record em JSON
        
        Args:
            record: Log record
        
        Returns:
            String JSON
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Adicionar exception info se houver
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': ''.join(traceback.format_exception(*record.exc_info))
            }
        
        # Adicionar campos extras
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """
    Logger estruturado com contexto e metadata
    """
    
    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        log_file: Optional[Path] = None,
        console_output: bool = True
    ):
        """
        Inicializa logger estruturado
        
        Args:
            name: Nome do logger
            level: Nível de logging
            log_file: Caminho para arquivo de log
            console_output: Se deve logar no console
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Limpar handlers existentes
        
        # Formatter JSON
        json_formatter = JSONFormatter()
        
        # Handler para console
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(json_formatter)
            self.logger.addHandler(console_handler)
        
        # Handler para arquivo
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)
        
        self.context = {}
    
    def set_context(self, **kwargs):
        """
        Define contexto para todos os logs subsequentes
        
        Args:
            **kwargs: Pares chave-valor de contexto
        """
        self.context.update(kwargs)
    
    def clear_context(self):
        """Limpa contexto"""
        self.context = {}
    
    def _log(
        self,
        level: int,
        message: str,
        **extra_fields
    ):
        """
        Log interno com contexto
        
        Args:
            level: Nível de logging
            message: Mensagem
            **extra_fields: Campos extras
        """
        # Merge context com extra fields
        fields = {**self.context, **extra_fields}
        
        # Criar log record
        extra = {'extra_fields': fields}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **extra_fields):
        """Log debug"""
        self._log(logging.DEBUG, message, **extra_fields)
    
    def info(self, message: str, **extra_fields):
        """Log info"""
        self._log(logging.INFO, message, **extra_fields)
    
    def warning(self, message: str, **extra_fields):
        """Log warning"""
        self._log(logging.WARNING, message, **extra_fields)
    
    def error(self, message: str, **extra_fields):
        """Log error"""
        self._log(logging.ERROR, message, **extra_fields)
    
    def critical(self, message: str, **extra_fields):
        """Log critical"""
        self._log(logging.CRITICAL, message, **extra_fields)
    
    def exception(self, message: str, **extra_fields):
        """
        Log exception com traceback
        
        Args:
            message: Mensagem
            **extra_fields: Campos extras
        """
        fields = {**self.context, **extra_fields}
        extra = {'extra_fields': fields}
        self.logger.exception(message, extra=extra)


# ============================================
# Loggers Globais
# ============================================

# API Logger
api_logger = StructuredLogger(
    name='sentibr.api',
    level=logging.INFO,
    log_file=Path('logs/api.log')
)

# Model Logger
model_logger = StructuredLogger(
    name='sentibr.model',
    level=logging.INFO,
    log_file=Path('logs/model.log')
)

# Monitoring Logger
monitoring_logger = StructuredLogger(
    name='sentibr.monitoring',
    level=logging.INFO,
    log_file=Path('logs/monitoring.log')
)

# System Logger
system_logger = StructuredLogger(
    name='sentibr.system',
    level=logging.INFO,
    log_file=Path('logs/system.log')
)


# ============================================
# Helper Functions
# ============================================

def log_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Log de requisição HTTP
    
    Args:
        method: HTTP method
        endpoint: Endpoint
        status_code: Status code
        duration_ms: Duração em ms
        user_id: ID do usuário (opcional)
        error: Mensagem de erro (opcional)
    """
    fields = {
        'type': 'http_request',
        'method': method,
        'endpoint': endpoint,
        'status_code': status_code,
        'duration_ms': duration_ms,
    }
    
    if user_id:
        fields['user_id'] = user_id
    
    if error:
        fields['error'] = error
        api_logger.error(f"Request failed: {method} {endpoint}", **fields)
    else:
        api_logger.info(f"Request: {method} {endpoint}", **fields)


def log_prediction(
    text: str,
    sentiment: str,
    confidence: float,
    inference_time_ms: float,
    model_type: str = "bert",
    request_id: Optional[str] = None
):
    """
    Log de predição do modelo
    
    Args:
        text: Texto analisado
        sentiment: Sentimento predito
        confidence: Confiança
        inference_time_ms: Tempo de inferência em ms
        model_type: Tipo do modelo
        request_id: ID da requisição
    """
    fields = {
        'type': 'prediction',
        'text_length': len(text),
        'sentiment': sentiment,
        'confidence': confidence,
        'inference_time_ms': inference_time_ms,
        'model_type': model_type,
    }
    
    if request_id:
        fields['request_id'] = request_id
    
    model_logger.info(f"Prediction: {sentiment}", **fields)


def log_feedback(
    text: str,
    predicted_sentiment: str,
    correct_sentiment: str,
    is_correct: bool,
    user_id: Optional[str] = None
):
    """
    Log de feedback do usuário
    
    Args:
        text: Texto
        predicted_sentiment: Sentimento predito
        correct_sentiment: Sentimento correto
        is_correct: Se estava correto
        user_id: ID do usuário
    """
    fields = {
        'type': 'feedback',
        'text_length': len(text),
        'predicted_sentiment': predicted_sentiment,
        'correct_sentiment': correct_sentiment,
        'is_correct': is_correct,
    }
    
    if user_id:
        fields['user_id'] = user_id
    
    model_logger.info(f"Feedback: {'correct' if is_correct else 'corrected'}", **fields)


def log_drift(
    drift_score: float,
    severity: str,
    features_affected: list,
    n_samples: int
):
    """
    Log de detecção de drift
    
    Args:
        drift_score: Score de drift
        severity: Severidade (normal, warning, critical)
        features_affected: Features com drift
        n_samples: Número de amostras
    """
    fields = {
        'type': 'drift_detection',
        'drift_score': drift_score,
        'severity': severity,
        'features_affected': features_affected,
        'n_samples': n_samples,
    }
    
    if severity == 'critical':
        monitoring_logger.critical(f"Critical drift detected: {drift_score:.2%}", **fields)
    elif severity == 'warning':
        monitoring_logger.warning(f"Drift warning: {drift_score:.2%}", **fields)
    else:
        monitoring_logger.info(f"Drift check: {drift_score:.2%}", **fields)


def log_system_event(
    event: str,
    details: Dict[str, Any],
    severity: str = "info"
):
    """
    Log de evento do sistema
    
    Args:
        event: Nome do evento
        details: Detalhes do evento
        severity: Severidade (info, warning, error, critical)
    """
    fields = {
        'type': 'system_event',
        'event': event,
        **details
    }
    
    if severity == 'critical':
        system_logger.critical(event, **fields)
    elif severity == 'error':
        system_logger.error(event, **fields)
    elif severity == 'warning':
        system_logger.warning(event, **fields)
    else:
        system_logger.info(event, **fields)


def log_startup(version: str, environment: str, config: Dict[str, Any]):
    """
    Log de startup da aplicação
    
    Args:
        version: Versão da aplicação
        environment: Ambiente (dev, staging, production)
        config: Configurações
    """
    system_logger.info(
        "Application started",
        type='startup',
        version=version,
        environment=environment,
        config=config
    )


def log_shutdown(reason: str = "normal"):
    """
    Log de shutdown da aplicação
    
    Args:
        reason: Razão do shutdown
    """
    system_logger.info(
        "Application shutdown",
        type='shutdown',
        reason=reason
    )


# ============================================
# Context Manager para Request Logging
# ============================================

class RequestContext:
    """
    Context manager para logging de request
    """
    
    def __init__(self, request_id: str, user_id: Optional[str] = None):
        """
        Inicializa context
        
        Args:
            request_id: ID da requisição
            user_id: ID do usuário
        """
        self.request_id = request_id
        self.user_id = user_id
    
    def __enter__(self):
        """Entra no context"""
        api_logger.set_context(
            request_id=self.request_id,
            user_id=self.user_id
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sai do context"""
        if exc_type is not None:
            api_logger.exception(
                f"Request failed: {exc_type.__name__}",
                error_message=str(exc_val)
            )
        api_logger.clear_context()


# ============================================
# Exemplo de Uso
# ============================================

if __name__ == "__main__":
    # Exemplo 1: Log simples
    api_logger.info("API started", port=8000, version="1.0.0")
    
    # Exemplo 2: Log com contexto
    with RequestContext(request_id="req-123", user_id="user-456"):
        api_logger.info("Processing request")
        log_prediction(
            text="A comida estava excelente!",
            sentiment="positive",
            confidence=0.95,
            inference_time_ms=42.5,
            model_type="bert"
        )
    
    # Exemplo 3: Log de erro
    try:
        raise ValueError("Erro de teste")
    except Exception:
        api_logger.exception("Erro ao processar requisição")
    
    # Exemplo 4: Log de drift
    log_drift(
        drift_score=0.18,
        severity="warning",
        features_affected=["text_length", "sentiment_distribution"],
        n_samples=1000
    )
    
    print("✅ Logs gerados em logs/")
