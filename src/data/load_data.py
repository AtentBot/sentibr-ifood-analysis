"""
Script para carregar e preparar o dataset B2W-Reviews01
Dataset de reviews de e-commerce brasileiro (Americanas.com)
"""

import pandas as pd
import numpy as np
from datasets import load_dataset
from pathlib import Path
import logging
from typing import Tuple, Dict
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetLoader:
    """
    Classe para carregar e preparar o dataset B2W-Reviews01
    """
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_from_huggingface(self) -> pd.DataFrame:
        """
        Carrega o dataset do HuggingFace
        """
        logger.info("Carregando dataset B2W-Reviews01 do HuggingFace...")
        
        try:
            dataset = load_dataset("ruanchaves/b2w-reviews01")
            
            # Converter para DataFrame
            df = pd.DataFrame(dataset['train'])
            
            logger.info(f"Dataset carregado com sucesso: {len(df)} reviews")
            logger.info(f"Colunas disponíveis: {df.columns.tolist()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar dataset: {e}")
            raise
    
    def prepare_for_sentiment_analysis(
        self, 
        df: pd.DataFrame,
        min_rating_negative: int = 2,
        max_rating_positive: int = 4
    ) -> pd.DataFrame:
        """
        Prepara o dataset para análise de sentimento
        
        Cria labels baseados em:
        - overall_rating: 1-2 = Negativo, 3 = Neutro, 4-5 = Positivo
        - recommend_to_a_friend: Sim/Não
        """
        logger.info("Preparando dataset para análise de sentimento...")
        
        df = df.copy()
        
        # Remover reviews sem texto
        df = df[df['review_text'].notna()]
        df = df[df['review_text'].str.strip() != '']
        
        # Criar label de sentimento baseado no rating
        def rating_to_sentiment(rating):
            if pd.isna(rating):
                return None
            if rating <= min_rating_negative:
                return 'negativo'
            elif rating >= max_rating_positive:
                return 'positivo'
            else:
                return 'neutro'
        
        df['sentiment'] = df['overall_rating'].apply(rating_to_sentiment)
        
        # Remover rows com sentiment None
        df = df[df['sentiment'].notna()]
        
        # Criar label numérico
        sentiment_map = {'negativo': 0, 'neutro': 1, 'positivo': 2}
        df['label'] = df['sentiment'].map(sentiment_map)
        
        # Colunas relevantes
        columns_to_keep = [
            'review_text',
            'review_title',
            'overall_rating',
            'recommend_to_a_friend',
            'sentiment',
            'label',
            'reviewer_gender',
            'reviewer_age',
            'reviewer_state'
        ]
        
        # Filtrar apenas colunas que existem
        columns_to_keep = [col for col in columns_to_keep if col in df.columns]
        df = df[columns_to_keep]
        
        logger.info(f"Dataset preparado: {len(df)} reviews")
        logger.info(f"\nDistribuição de sentimentos:")
        logger.info(f"{df['sentiment'].value_counts()}")
        
        return df
    
    def create_aspect_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria labels de aspectos (comida, entrega, atendimento, preço)
        usando keywords simples
        
        NOTA: Em produção, isso seria feito com anotação manual ou modelo
        """
        logger.info("Criando labels de aspectos (heurística)...")
        
        df = df.copy()
        
        # Keywords para cada aspecto
        aspects_keywords = {
            'produto': ['produto', 'qualidade', 'material', 'defeito', 'quebrado', 'ruim', 'excelente', 'bom'],
            'entrega': ['entrega', 'prazo', 'rápido', 'lento', 'atrasado', 'chegou', 'demorou', 'tempo'],
            'atendimento': ['atendimento', 'vendedor', 'loja', 'suporte', 'ajuda', 'resposta'],
            'preco': ['preço', 'caro', 'barato', 'valor', 'custo', 'benefício', 'promoção']
        }
        
        for aspect, keywords in aspects_keywords.items():
            pattern = '|'.join(keywords)
            df[f'has_{aspect}'] = df['review_text'].str.lower().str.contains(pattern, regex=True, na=False)
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str = "processed_reviews.csv"):
        """
        Salva o dataset processado
        """
        output_path = Path("data/processed") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        logger.info(f"Dataset salvo em: {output_path}")
        
        return output_path
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Retorna estatísticas do dataset
        """
        stats = {
            'total_reviews': len(df),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
            'avg_review_length': df['review_text'].str.len().mean(),
            'median_review_length': df['review_text'].str.len().median(),
            'avg_rating': df['overall_rating'].mean() if 'overall_rating' in df.columns else None,
        }
        
        # Estatísticas por gênero (se disponível)
        if 'reviewer_gender' in df.columns:
            stats['gender_distribution'] = df['reviewer_gender'].value_counts().to_dict()
        
        # Estatísticas de aspectos
        aspect_cols = [col for col in df.columns if col.startswith('has_')]
        if aspect_cols:
            stats['aspect_coverage'] = {
                col.replace('has_', ''): df[col].sum() 
                for col in aspect_cols
            }
        
        return stats


def main():
    """
    Função principal para executar o pipeline
    """
    logger.info("=" * 60)
    logger.info("SENTIBR - Data Loading Pipeline")
    logger.info("=" * 60)
    
    # Inicializar loader
    loader = DatasetLoader()
    
    # Carregar dataset
    df = loader.load_from_huggingface()
    
    # Preparar para análise de sentimento
    df = loader.prepare_for_sentiment_analysis(df)
    
    # Criar labels de aspectos
    df = loader.create_aspect_labels(df)
    
    # Salvar dataset processado
    output_path = loader.save_processed_data(df)
    
    # Estatísticas
    stats = loader.get_statistics(df)
    logger.info("\n" + "=" * 60)
    logger.info("ESTATÍSTICAS DO DATASET")
    logger.info("=" * 60)
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Pipeline concluído com sucesso!")
    logger.info(f"📁 Dataset salvo em: {output_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
