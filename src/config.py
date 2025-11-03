"""
Configurações centralizadas do projeto SentiBR
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Criar diretórios se não existirem
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


@dataclass
class ModelConfig:
    """Configurações do modelo BERT"""
    
    model_name: str = os.getenv("MODEL_NAME", "neuralmind/bert-base-portuguese-cased")
    max_length: int = int(os.getenv("MAX_LENGTH", "512"))
    num_labels: int = int(os.getenv("NUM_LABELS", "3"))
    dropout: float = 0.1
    
    # Paths
    model_save_path: Path = MODELS_DIR / "bert_finetuned"
    tokenizer_save_path: Path = MODELS_DIR / "bert_finetuned"


@dataclass
class TrainingConfig:
    """Configurações de treinamento"""
    
    learning_rate: float = float(os.getenv("LEARNING_RATE", "2e-5"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "16"))
    num_epochs: int = int(os.getenv("NUM_EPOCHS", "3"))
    warmup_steps: int = int(os.getenv("WARMUP_STEPS", "500"))
    weight_decay: float = float(os.getenv("WEIGHT_DECAY", "0.01"))
    seed: int = int(os.getenv("SEED", "42"))
    
    # Split ratios
    train_split: float = float(os.getenv("TRAIN_SPLIT", "0.7"))
    val_split: float = float(os.getenv("VAL_SPLIT", "0.15"))
    test_split: float = float(os.getenv("TEST_SPLIT", "0.15"))
    
    # Paths
    train_data_path: Path = DATA_DIR / "processed" / "train.csv"
    val_data_path: Path = DATA_DIR / "processed" / "val.csv"
    test_data_path: Path = DATA_DIR / "processed" / "test.csv"


@dataclass
class APIConfig:
    """Configurações da API"""
    
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    workers: int = int(os.getenv("API_WORKERS", "1"))
    
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Model
    model_path: Path = MODELS_DIR / "bert_finetuned"


@dataclass
class OpenAIConfig:
    """Configurações da OpenAI API"""
    
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
    temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))


@dataclass
class MLflowConfig:
    """Configurações do MLflow"""
    
    tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    experiment_name: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "sentibr-sentiment-analysis")


@dataclass
class MonitoringConfig:
    """Configurações de monitoramento"""
    
    enable_prometheus: bool = os.getenv("ENABLE_PROMETHEUS", "true").lower() == "true"
    prometheus_port: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    
    # Drift detection
    drift_check_interval: int = int(os.getenv("DRIFT_CHECK_INTERVAL", "3600"))
    drift_threshold: float = float(os.getenv("DRIFT_THRESHOLD", "0.05"))


@dataclass
class Config:
    """Configuração global do projeto"""
    
    project_name: str = os.getenv("PROJECT_NAME", "SentiBR")
    version: str = os.getenv("VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Sub-configurações
    model: ModelConfig = ModelConfig()
    training: TrainingConfig = TrainingConfig()
    api: APIConfig = APIConfig()
    openai: OpenAIConfig = OpenAIConfig()
    mlflow: MLflowConfig = MLflowConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if self.environment not in ["development", "staging", "production"]:
            raise ValueError(f"Invalid environment: {self.environment}")
        
        # Verificar se splits somam 1.0
        total_split = (
            self.training.train_split +
            self.training.val_split +
            self.training.test_split
        )
        if not 0.99 <= total_split <= 1.01:
            raise ValueError(
                f"Train/val/test splits must sum to 1.0, got {total_split}"
            )


# Instância global de configuração
config = Config()


# Função helper para obter configuração
def get_config() -> Config:
    """Retorna a configuração global"""
    return config


if __name__ == "__main__":
    # Teste de configuração
    print("=" * 60)
    print("SENTIBR - Configurações")
    print("=" * 60)
    print(f"\n📌 Projeto: {config.project_name} v{config.version}")
    print(f"📌 Ambiente: {config.environment}")
    print(f"\n📁 Diretórios:")
    print(f"   - Base: {BASE_DIR}")
    print(f"   - Dados: {DATA_DIR}")
    print(f"   - Modelos: {MODELS_DIR}")
    print(f"   - Logs: {LOGS_DIR}")
    print(f"\n🤖 Modelo:")
    print(f"   - Nome: {config.model.model_name}")
    print(f"   - Max Length: {config.model.max_length}")
    print(f"   - Num Labels: {config.model.num_labels}")
    print(f"\n🎓 Treinamento:")
    print(f"   - Learning Rate: {config.training.learning_rate}")
    print(f"   - Batch Size: {config.training.batch_size}")
    print(f"   - Epochs: {config.training.num_epochs}")
    print(f"   - Splits: {config.training.train_split}/{config.training.val_split}/{config.training.test_split}")
    print(f"\n🌐 API:")
    print(f"   - Host: {config.api.host}")
    print(f"   - Port: {config.api.port}")
    print(f"   - Workers: {config.api.workers}")
    print(f"\n🤖 OpenAI:")
    print(f"   - API Key configurada: {'✅' if config.openai.api_key else '❌'}")
    print(f"   - Modelo: {config.openai.model}")
    print(f"\n📊 MLflow:")
    print(f"   - Tracking URI: {config.mlflow.tracking_uri}")
    print(f"   - Experiment: {config.mlflow.experiment_name}")
    print("\n" + "=" * 60)
