#!/usr/bin/env python3
"""
Script "One-Click Training" - Executa todo o pipeline automaticamente
Perfeito para demonstrações e testes rápidos
"""

import subprocess
import sys
import logging
from pathlib import Path
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_command(command: list, description: str, critical: bool = True) -> bool:
    """
    Executa um comando e loga o resultado
    
    Args:
        command: Lista com o comando a executar
        description: Descrição do que está sendo executado
        critical: Se True, para a execução em caso de erro
    
    Returns:
        True se sucesso, False se erro
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"📌 {description}")
    logger.info(f"{'='*60}")
    logger.info(f"Comando: {' '.join(command)}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command,
            check=True,
            capture_output=False,
            text=True
        )
        elapsed = time.time() - start_time
        
        logger.info(f"✅ {description} - Completo em {elapsed:.1f}s")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} - FALHOU")
        logger.error(f"   Erro: {e}")
        
        if critical:
            logger.error("\n🛑 Parando execução devido a erro crítico")
            sys.exit(1)
        
        return False


def check_prerequisites():
    """Verifica se os pré-requisitos estão instalados"""
    logger.info("\n🔍 Verificando pré-requisitos...")
    
    # Python version
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        logger.info(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        logger.error(f"   ❌ Python {version.major}.{version.minor} (requer 3.10+)")
        return False
    
    # Requirements file
    if not Path("requirements.txt").exists():
        logger.error("   ❌ requirements.txt não encontrado")
        return False
    else:
        logger.info("   ✅ requirements.txt encontrado")
    
    return True


def main(
    use_quick_data: bool = True,
    quick_test_first: bool = True,
    full_training: bool = True,
    evaluate: bool = True,
    open_mlflow: bool = True
):
    """
    Pipeline completo de treinamento
    
    Args:
        use_quick_data: Se True, usa dados de teste rápidos (1k samples)
        quick_test_first: Se True, executa teste rápido antes do treino completo
        full_training: Se True, executa treinamento completo
        evaluate: Se True, executa avaliação detalhada
        open_mlflow: Se True, abre MLflow UI no final
    """
    logger.info("=" * 60)
    logger.info("🚀 SENTIBR - ONE-CLICK TRAINING PIPELINE")
    logger.info("=" * 60)
    logger.info(f"\nConfiguração:")
    logger.info(f"  - Dados de teste rápidos: {use_quick_data}")
    logger.info(f"  - Teste rápido antes do treino: {quick_test_first}")
    logger.info(f"  - Treinamento completo: {full_training}")
    logger.info(f"  - Avaliação detalhada: {evaluate}")
    logger.info(f"  - Abrir MLflow UI: {open_mlflow}")
    
    # Verificar pré-requisitos
    if not check_prerequisites():
        logger.error("\n❌ Pré-requisitos não atendidos!")
        return False
    
    start_total = time.time()
    
    # Passo 1: Instalar dependências
    run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"],
        "Instalando dependências",
        critical=True
    )
    
    # Passo 2: Criar diretórios
    logger.info("\n📁 Criando diretórios...")
    for dir_path in ["data/raw", "data/processed", "models/bert_finetuned", "logs", "mlruns"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    logger.info("   ✅ Diretórios criados")
    
    # Passo 3: Preparar dados
    if use_quick_data:
        run_command(
            [sys.executable, "src/data/quick_test_data.py"],
            "Criando dados de teste rápidos",
            critical=True
        )
    else:
        run_command(
            [sys.executable, "src/data/load_data_v2.py"],
            "Carregando dataset B2W-Reviews01",
            critical=True
        )
    
    # Passo 4: Dividir dados
    run_command(
        [sys.executable, "src/data/split_dataset.py"],
        "Dividindo dados em train/val/test",
        critical=True
    )
    
    # Passo 5: Teste rápido (opcional)
    if quick_test_first:
        run_command(
            [sys.executable, "src/training/quick_test.py", "--samples", "50", "--epochs", "1"],
            "Executando teste rápido do pipeline",
            critical=False
        )
    
    # Passo 6: Treinamento completo
    if full_training:
        run_command(
            [sys.executable, "src/training/train.py"],
            "🚀 TREINAMENTO COMPLETO DO MODELO",
            critical=True
        )
    
    # Passo 7: Avaliação
    if evaluate:
        run_command(
            [sys.executable, "src/training/evaluate.py"],
            "Avaliação detalhada do modelo",
            critical=False
        )
    
    # Tempo total
    elapsed_total = time.time() - start_total
    
    # Resumo final
    logger.info("\n" + "=" * 60)
    logger.info("🎉 PIPELINE COMPLETO!")
    logger.info("=" * 60)
    logger.info(f"⏱️  Tempo total: {elapsed_total/60:.1f} minutos")
    
    logger.info("\n📁 Arquivos gerados:")
    logger.info("   - Modelo: models/bert_finetuned/")
    logger.info("   - Métricas: logs/evaluation_report.json")
    logger.info("   - Confusion Matrix: logs/confusion_matrix.png")
    logger.info("   - MLflow: mlruns/")
    
    logger.info("\n💡 Próximos passos:")
    logger.info("   1. Ver experimentos MLflow:")
    logger.info("      mlflow ui")
    logger.info("      Acesse: http://localhost:5000")
    logger.info("\n   2. Testar o modelo:")
    logger.info("      python -c \"from transformers import pipeline; nlp = pipeline('sentiment-analysis', model='models/bert_finetuned'); print(nlp('Adorei!'))\"")
    logger.info("\n   3. Criar API REST:")
    logger.info("      python src/api/main.py")
    
    # Abrir MLflow (opcional)
    if open_mlflow:
        logger.info("\n🌐 Abrindo MLflow UI...")
        logger.info("   Acesse: http://localhost:5000")
        logger.info("   (Pressione Ctrl+C para parar)")
        try:
            subprocess.run(["mlflow", "ui"])
        except KeyboardInterrupt:
            logger.info("\n✋ MLflow UI fechado pelo usuário")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='One-click training pipeline')
    parser.add_argument(
        '--full-data',
        action='store_true',
        help='Usar dataset completo B2W ao invés de dados de teste'
    )
    parser.add_argument(
        '--skip-quick-test',
        action='store_true',
        help='Pular teste rápido e ir direto para o treino'
    )
    parser.add_argument(
        '--skip-training',
        action='store_true',
        help='Pular treinamento (útil para testar apenas preparação de dados)'
    )
    parser.add_argument(
        '--skip-eval',
        action='store_true',
        help='Pular avaliação detalhada'
    )
    parser.add_argument(
        '--no-mlflow',
        action='store_true',
        help='Não abrir MLflow UI no final'
    )
    
    args = parser.parse_args()
    
    success = main(
        use_quick_data=not args.full_data,
        quick_test_first=not args.skip_quick_test,
        full_training=not args.skip_training,
        evaluate=not args.skip_eval,
        open_mlflow=not args.no_mlflow
    )
    
    sys.exit(0 if success else 1)
