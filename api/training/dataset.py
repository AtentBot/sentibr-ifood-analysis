"""
Dataset PyTorch customizado para análise de sentimento
"""

import torch
from torch.utils.data import Dataset
import pandas as pd
from typing import Dict, List
from transformers import BertTokenizer
import logging

logger = logging.getLogger(__name__)


class SentimentDataset(Dataset):
    """
    Dataset customizado para fine-tuning do BERT em análise de sentimento
    """
    
    def __init__(
        self,
        texts: List[str],
        labels: List[int],
        tokenizer: BertTokenizer,
        max_length: int = 512
    ):
        """
        Args:
            texts: Lista de textos (reviews)
            labels: Lista de labels (0=negativo, 1=neutro, 2=positivo)
            tokenizer: Tokenizer do BERT
            max_length: Comprimento máximo do texto
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self) -> int:
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Retorna um item do dataset já tokenizado
        """
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenizar
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }


def load_data_for_training(
    train_path: str,
    val_path: str,
    test_path: str,
    text_column: str = 'review_text',
    label_column: str = 'label'
) -> Dict[str, pd.DataFrame]:
    """
    Carrega os datasets de treino, validação e teste
    
    Args:
        train_path: Caminho para train.csv
        val_path: Caminho para val.csv
        test_path: Caminho para test.csv
        text_column: Nome da coluna com o texto
        label_column: Nome da coluna com o label
    
    Returns:
        Dict com 'train', 'val', 'test' DataFrames
    """
    logger.info("Carregando datasets...")
    
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)
    
    logger.info(f"  Train: {len(train_df)} samples")
    logger.info(f"  Val:   {len(val_df)} samples")
    logger.info(f"  Test:  {len(test_df)} samples")
    
    # Verificar colunas necessárias
    for df_name, df in [('train', train_df), ('val', val_df), ('test', test_df)]:
        if text_column not in df.columns:
            raise ValueError(f"Coluna '{text_column}' não encontrada em {df_name}")
        if label_column not in df.columns:
            raise ValueError(f"Coluna '{label_column}' não encontrada em {df_name}")
    
    return {
        'train': train_df,
        'val': val_df,
        'test': test_df
    }


def create_data_loaders(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    tokenizer: BertTokenizer,
    max_length: int = 512,
    batch_size: int = 16,
    text_column: str = 'review_text',
    label_column: str = 'label'
) -> Dict[str, torch.utils.data.DataLoader]:
    """
    Cria DataLoaders para treino, validação e teste
    
    Args:
        train_df: DataFrame de treino
        val_df: DataFrame de validação
        test_df: DataFrame de teste
        tokenizer: Tokenizer do BERT
        max_length: Comprimento máximo do texto
        batch_size: Tamanho do batch
        text_column: Nome da coluna com o texto
        label_column: Nome da coluna com o label
    
    Returns:
        Dict com 'train', 'val', 'test' DataLoaders
    """
    logger.info("Criando datasets e dataloaders...")
    
    # Criar datasets
    train_dataset = SentimentDataset(
        texts=train_df[text_column].tolist(),
        labels=train_df[label_column].tolist(),
        tokenizer=tokenizer,
        max_length=max_length
    )
    
    val_dataset = SentimentDataset(
        texts=val_df[text_column].tolist(),
        labels=val_df[label_column].tolist(),
        tokenizer=tokenizer,
        max_length=max_length
    )
    
    test_dataset = SentimentDataset(
        texts=test_df[text_column].tolist(),
        labels=test_df[label_column].tolist(),
        tokenizer=tokenizer,
        max_length=max_length
    )
    
    # Criar dataloaders
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0  # 0 para evitar problemas no Windows/Mac
    )
    
    val_loader = torch.utils.data.DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )
    
    logger.info("  ✅ DataLoaders criados com sucesso")
    
    return {
        'train': train_loader,
        'val': val_loader,
        'test': test_loader
    }
