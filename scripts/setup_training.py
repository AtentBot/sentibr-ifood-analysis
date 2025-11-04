#!/usr/bin/env python3
"""
Script de setup do ambiente de treinamento
Verifica e instala dependências necessárias
"""

import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_python_version():
    """Verifica se a versão do Python é adequada"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"❌ Python {version.major}.{version.minor} (requer 3.10+)")
        return False


def install_requirements():
    """Instala as dependências do requirements.txt"""
    logger.info("📦 Instalando dependências...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        logger.error("❌ requirements.txt não encontrado!")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        logger.info("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao instalar dependências: {e}")
        return False


def check_gpu():
    """Verifica disponibilidade de GPU"""
    try:
        import torch
        if torch.cuda.is_available():
            logger.info(f"✅ GPU disponível: {torch.cuda.get_device_name(0)}")
            logger.info(f"   Memória: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return True
        else:
            logger.warning("⚠️  GPU não disponível (treinamento será em CPU)")
            return False
    except ImportError:
        logger.error("❌ PyTorch não instalado!")
        return False


def create_directories():
    """Cria diretórios necessários"""
    logger.info("📁 Criando diretórios...")
    
    directories = [
        "data/raw",
        "data/processed",
        "models/bert_finetuned",
        "logs",
        "mlruns"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ Diretórios criados")


def check_env_file():
    """Verifica arquivo .env"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            logger.warning("⚠️  .env não encontrado, copiando de .env.example...")
            env_file.write_text(env_example.read_text())
            logger.info("✅ .env criado")
        else:
            logger.warning("⚠️  .env e .env.example não encontrados")
    else:
        logger.info("✅ .env encontrado")


def download_test_data():
    """Baixa ou cria dados de teste"""
    logger.info("📊 Verificando dados de teste...")
    
    test_data = Path("data/processed/processed_reviews.csv")
    
    if test_data.exists():
        logger.info("✅ Dados de teste já existem")
        return True
    
    logger.info("💡 Criando dados de teste sintéticos...")
    try:
        subprocess.check_call([sys.executable, "src/data/quick_test_data.py"])
        subprocess.check_call([sys.executable, "src/data/split_dataset.py"])
        logger.info("✅ Dados de teste criados")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao criar dados de teste: {e}")
        return False


def run_quick_test():
    """Executa teste rápido do pipeline"""
    logger.info("\n🧪 Executando teste rápido do pipeline...")
    
    try:
        subprocess.check_call([
            sys.executable, "src/training/quick_test.py",
            "--samples", "50",
            "--epochs", "1"
        ])
        logger.info("✅ Teste rápido passou!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Teste rápido falhou: {e}")
        return False


def main():
    """Função principal"""
    logger.info("=" * 60)
    logger.info("🚀 SENTIBR - Setup do Ambiente de Treinamento")
    logger.info("=" * 60)
    
    checks = []
    
    # 1. Verificar Python
    logger.info("\n1️⃣ Verificando Python...")
    checks.append(("Python 3.10+", check_python_version()))
    
    # 2. Instalar dependências
    logger.info("\n2️⃣ Instalando dependências...")
    checks.append(("Dependências", install_requirements()))
    
    # 3. Verificar GPU
    logger.info("\n3️⃣ Verificando GPU...")
    checks.append(("GPU (opcional)", check_gpu()))
    
    # 4. Criar diretórios
    logger.info("\n4️⃣ Criando diretórios...")
    create_directories()
    checks.append(("Diretórios", True))
    
    # 5. Verificar .env
    logger.info("\n5️⃣ Verificando configurações...")
    check_env_file()
    checks.append(("Configurações", True))
    
    # 6. Criar dados de teste
    logger.info("\n6️⃣ Preparando dados de teste...")
    checks.append(("Dados de teste", download_test_data()))
    
    # 7. Teste rápido (opcional)
    logger.info("\n7️⃣ Teste rápido do pipeline...")
    response = input("Executar teste rápido agora? (s/n): ").lower()
    if response == 's':
        checks.append(("Teste rápido", run_quick_test()))
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMO DO SETUP")
    logger.info("=" * 60)
    
    for name, passed in checks:
        status = "✅" if passed else "❌"
        logger.info(f"{status} {name}")
    
    all_passed = all(result for _, result in checks if not _.endswith("(opcional)"))
    
    if all_passed:
        logger.info("\n🎉 Setup concluído com sucesso!")
        logger.info("\n💡 Próximos passos:")
        logger.info("   1. Configure API keys no .env (se necessário)")
        logger.info("   2. Execute: python src/training/train.py")
    else:
        logger.info("\n⚠️  Alguns problemas encontrados. Corrija-os antes de continuar.")
    
    logger.info("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
