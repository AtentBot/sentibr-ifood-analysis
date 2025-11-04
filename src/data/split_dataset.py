"""
Script para dividir o dataset em train/validation/test
Mantém o balanceamento de classes em cada split
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging
from typing import Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def split_dataset(
    df: pd.DataFrame,
    train_size: float = 0.7,
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = 42,
    stratify_column: str = 'sentiment'
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Divide o dataset em train/val/test mantendo proporção de classes
    
    Args:
        df: DataFrame com os dados
        train_size: Proporção para treino (default: 0.7)
        val_size: Proporção para validação (default: 0.15)
        test_size: Proporção para teste (default: 0.15)
        random_state: Seed para reprodutibilidade
        stratify_column: Coluna para estratificação
    
    Returns:
        Tuple com (train_df, val_df, test_df)
    """
    
    # Validar splits
    assert abs((train_size + val_size + test_size) - 1.0) < 0.01, \
        "Splits devem somar 1.0"
    
    # Primeiro split: train vs (val+test)
    train_df, temp_df = train_test_split(
        df,
        train_size=train_size,
        random_state=random_state,
        stratify=df[stratify_column] if stratify_column else None
    )
    
    # Segundo split: val vs test
    val_ratio = val_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df,
        train_size=val_ratio,
        random_state=random_state,
        stratify=temp_df[stratify_column] if stratify_column else None
    )
    
    return train_df, val_df, test_df


def print_split_statistics(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    sentiment_col: str = 'sentiment'
):
    """
    Imprime estatísticas dos splits
    """
    logger.info("\n" + "=" * 60)
    logger.info("ESTATÍSTICAS DOS SPLITS")
    logger.info("=" * 60)
    
    total = len(train_df) + len(val_df) + len(test_df)
    
    logger.info(f"\n📊 Tamanhos:")
    logger.info(f"   Total: {total:,} reviews")
    logger.info(f"   Train: {len(train_df):,} ({len(train_df)/total*100:.1f}%)")
    logger.info(f"   Val:   {len(val_df):,} ({len(val_df)/total*100:.1f}%)")
    logger.info(f"   Test:  {len(test_df):,} ({len(test_df)/total*100:.1f}%)")
    
    logger.info(f"\n🎯 Distribuição de Sentimentos:")
    
    for split_name, split_df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        logger.info(f"\n   {split_name}:")
        sentiment_counts = split_df[sentiment_col].value_counts()
        for sentiment, count in sentiment_counts.items():
            pct = count / len(split_df) * 100
            logger.info(f"      {sentiment}: {count:,} ({pct:.1f}%)")


def main():
    """
    Função principal
    """
    logger.info("=" * 60)
    logger.info("SENTIBR - Dataset Splitter")
    logger.info("=" * 60)
    
    # Carregar dataset processado
    input_path = Path("data/processed/processed_reviews.csv")
    
    if not input_path.exists():
        logger.error(f"❌ Dataset não encontrado: {input_path}")
        logger.info("\n💡 Execute primeiro:")
        logger.info("   python src/data/load_data.py")
        logger.info("   ou")
        logger.info("   python src/data/quick_test_data.py")
        return
    
    logger.info(f"\n📁 Carregando dataset: {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"✅ Carregado: {len(df):,} reviews")
    
    # Split do dataset
    logger.info("\n🔪 Dividindo dataset...")
    train_df, val_df, test_df = split_dataset(
        df,
        train_size=0.7,
        val_size=0.15,
        test_size=0.15,
        random_state=42,
        stratify_column='sentiment'
    )
    
    # Estatísticas
    print_split_statistics(train_df, val_df, test_df)
    
    # Salvar splits
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\n💾 Salvando splits...")
    
    train_path = output_dir / "train.csv"
    val_path = output_dir / "val.csv"
    test_path = output_dir / "test.csv"
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    logger.info(f"   ✅ Train: {train_path}")
    logger.info(f"   ✅ Val:   {val_path}")
    logger.info(f"   ✅ Test:  {test_path}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Splits criados com sucesso!")
    logger.info("=" * 60)
    
    logger.info("\n💡 Próximo passo:")
    logger.info("   python src/training/train.py")


if __name__ == "__main__":
    main()
