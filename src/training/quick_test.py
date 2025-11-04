"""
Script de teste rápido do pipeline de treinamento
Use este script para testar rapidamente se o pipeline está funcionando
antes de fazer o treinamento completo
"""

import torch
from pathlib import Path
import logging
import sys

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import config
from src.training.train import BERTTrainer
from src.training.dataset import load_data_for_training, create_data_loaders

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def quick_test(n_samples: int = 100, n_epochs: int = 1):
    """
    Teste rápido do pipeline de treinamento
    
    Args:
        n_samples: Número de samples para usar (default: 100)
        n_epochs: Número de épocas para treinar (default: 1)
    """
    logger.info("=" * 60)
    logger.info("🧪 TESTE RÁPIDO DO PIPELINE DE TREINAMENTO")
    logger.info("=" * 60)
    logger.info(f"Usando {n_samples} samples por split")
    logger.info(f"Treinando por {n_epochs} época(s)")
    
    # Verificar se os dados existem
    if not config.training.train_data_path.exists():
        logger.error(f"❌ Arquivo de treino não encontrado: {config.training.train_data_path}")
        logger.info("\n💡 Execute primeiro:")
        logger.info("   1. python src/data/quick_test_data.py (para dados de teste)")
        logger.info("   2. python src/data/split_dataset.py")
        return
    
    # Carregar dados
    logger.info("\n📊 Carregando dados...")
    data = load_data_for_training(
        train_path=str(config.training.train_data_path),
        val_path=str(config.training.val_data_path),
        test_path=str(config.training.test_data_path)
    )
    
    # Usar apenas subset dos dados
    data['train'] = data['train'].head(n_samples)
    data['val'] = data['val'].head(n_samples // 5)
    data['test'] = data['test'].head(n_samples // 5)
    
    logger.info(f"  Train: {len(data['train'])} samples")
    logger.info(f"  Val:   {len(data['val'])} samples")
    logger.info(f"  Test:  {len(data['test'])} samples")
    
    # Inicializar trainer com configurações de teste
    logger.info("\n🤖 Inicializando modelo...")
    trainer = BERTTrainer(
        model_name=config.model.model_name,
        num_labels=config.model.num_labels,
        learning_rate=2e-5,
        num_epochs=n_epochs,
        batch_size=8,  # Batch size menor para teste rápido
        max_length=128,  # Max length menor para teste rápido
        warmup_steps=0,
        weight_decay=0.01
    )
    
    # Inicializar modelo
    trainer.initialize_model()
    
    # Criar data loaders
    logger.info("\n📦 Criando data loaders...")
    loaders = create_data_loaders(
        train_df=data['train'],
        val_df=data['val'],
        test_df=data['test'],
        tokenizer=trainer.tokenizer,
        max_length=trainer.max_length,
        batch_size=trainer.batch_size
    )
    
    # Inicializar optimizer (IMPORTANTE!)
    logger.info("\n⚙️ Inicializando optimizer...")
    num_training_steps = len(loaders['train']) * n_epochs
    trainer.initialize_optimizer(num_training_steps)
    
    # Treinar
    logger.info("\n🚀 Iniciando treinamento de teste...")
    logger.info("(Este é apenas um teste rápido, não salvaremos o modelo)")
    
    # Fazer um epoch de treino sem salvar
    train_loss, train_acc = trainer.train_epoch(loaders['train'], epoch=0)
    
    logger.info(f"\n✅ Train Loss: {train_loss:.4f}")
    logger.info(f"✅ Train Acc: {train_acc:.4f}")
    
    # Validar
    logger.info("\n🔍 Validando...")
    val_metrics = trainer.evaluate(loaders['val'])
    
    logger.info(f"✅ Val Loss: {val_metrics['loss']:.4f}")
    logger.info(f"✅ Val Acc: {val_metrics['accuracy']:.4f}")
    logger.info(f"✅ Val F1: {val_metrics['f1']:.4f}")
    
    # Testar
    logger.info("\n🧪 Testando...")
    test_metrics = trainer.evaluate(loaders['test'])
    
    logger.info(f"✅ Test Loss: {test_metrics['loss']:.4f}")
    logger.info(f"✅ Test Acc: {test_metrics['accuracy']:.4f}")
    logger.info(f"✅ Test F1: {test_metrics['f1']:.4f}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ TESTE CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 60)
    logger.info("\n💡 O pipeline está funcionando corretamente!")
    logger.info("   Agora você pode executar o treinamento completo:")
    logger.info("   python src/training/train.py")
    
    # Verificar GPU
    if torch.cuda.is_available():
        logger.info(f"\n🎉 GPU detectada: {torch.cuda.get_device_name(0)}")
        logger.info(f"   Memória disponível: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        logger.info("\n⚠️  Rodando em CPU (o treinamento completo será lento)")
        logger.info("   Considere usar Google Colab ou AWS para GPU")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste rápido do pipeline de treinamento')
    parser.add_argument('--samples', type=int, default=100, help='Número de samples para usar')
    parser.add_argument('--epochs', type=int, default=1, help='Número de épocas para treinar')
    
    args = parser.parse_args()
    
    quick_test(n_samples=args.samples, n_epochs=args.epochs)
