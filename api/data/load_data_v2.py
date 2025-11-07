"""
Script atualizado para carregar o dataset B2W-Reviews01
Corrige o erro de "Dataset scripts are no longer supported"
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Tuple, Dict
import sys
import requests
from io import StringIO

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
        
    def load_from_github_direct(self) -> pd.DataFrame:
        """
        Carrega o dataset diretamente do GitHub (alternativa ao HuggingFace)
        """
        logger.info("Carregando dataset B2W-Reviews01 diretamente do GitHub...")
        
        # URL direta do GitHub
        url = "https://raw.githubusercontent.com/b2wdigital/b2w-reviews01/master/B2W-Reviews01.csv"
        
        try:
            logger.info(f"Baixando de: {url}")
            logger.info("⏳ Isso pode demorar alguns minutos...")
            
            # Baixar o arquivo
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            
            # Ler como CSV
            df = pd.read_csv(StringIO(response.text), sep=';', encoding='utf-8')
            
            logger.info(f"✅ Dataset carregado com sucesso: {len(df)} reviews")
            logger.info(f"📊 Colunas disponíveis: {df.columns.tolist()}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro ao baixar dataset do GitHub: {e}")
            logger.info("\n💡 Alternativa: Use o dataset de teste rápido")
            logger.info("   python src/data/quick_test_data.py")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao processar dataset: {e}")
            raise
    
    def load_from_url_parquet(self) -> pd.DataFrame:
        """
        Tenta carregar do HuggingFace usando URL direta do parquet
        """
        logger.info("Tentando carregar dataset via HuggingFace (Parquet)...")
        
        try:
            # URL do arquivo parquet no HuggingFace
            url = "https://huggingface.co/datasets/ruanchaves/b2w-reviews01/resolve/main/data/train-00000-of-00001.parquet"
            
            logger.info(f"Baixando de: {url}")
            df = pd.read_parquet(url)
            
            logger.info(f"✅ Dataset carregado com sucesso: {len(df)} reviews")
            return df
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar via Parquet: {e}")
            raise
    
    def prepare_for_sentiment_analysis(
        self, 
        df: pd.DataFrame,
        min_rating_negative: int = 2,
        max_rating_positive: int = 4
    ) -> pd.DataFrame:
        """
        Prepara o dataset para análise de sentimento
        """
        logger.info("Preparando dataset para análise de sentimento...")
        
        df = df.copy()
        
        # Normalizar nomes das colunas (pode variar entre fontes)
        column_mapping = {
            'review_text': ['review_text', 'reviewText', 'text', 'review'],
            'review_title': ['review_title', 'reviewTitle', 'title'],
            'overall_rating': ['overall_rating', 'overallRating', 'rating', 'nota'],
            'recommend_to_a_friend': ['recommend_to_a_friend', 'recommendToAFriend', 'recommend']
        }
        
        for standard_name, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    if possible_name != standard_name:
                        df = df.rename(columns={possible_name: standard_name})
                    break
        
        # Verificar se temos a coluna de texto
        if 'review_text' not in df.columns:
            # Tentar encontrar coluna de texto
            text_cols = [col for col in df.columns if 'text' in col.lower() or 'review' in col.lower()]
            if text_cols:
                df = df.rename(columns={text_cols[0]: 'review_text'})
                logger.info(f"ℹ️ Usando coluna '{text_cols[0]}' como review_text")
        
        # Remover reviews sem texto
        if 'review_text' in df.columns:
            df = df[df['review_text'].notna()]
            df = df[df['review_text'].astype(str).str.strip() != '']
        else:
            logger.error("❌ Não foi possível encontrar coluna de texto!")
            raise ValueError("Coluna de texto não encontrada no dataset")
        
        # Criar label de sentimento baseado no rating
        if 'overall_rating' in df.columns:
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
        else:
            logger.warning("⚠️ Coluna 'overall_rating' não encontrada. Criando sentimentos aleatórios.")
            df['sentiment'] = np.random.choice(['positivo', 'neutro', 'negativo'], size=len(df))
        
        # Remover rows com sentiment None
        df = df[df['sentiment'].notna()]
        
        # Criar label numérico
        sentiment_map = {'negativo': 0, 'neutro': 1, 'positivo': 2}
        df['label'] = df['sentiment'].map(sentiment_map)
        
        # Selecionar colunas relevantes
        columns_to_keep = [
            'review_text',
            'review_title',
            'overall_rating',
            'recommend_to_a_friend',
            'sentiment',
            'label'
        ]
        
        # Adicionar outras colunas que existirem
        optional_columns = ['reviewer_gender', 'reviewer_age', 'reviewer_state']
        columns_to_keep.extend([col for col in optional_columns if col in df.columns])
        
        # Filtrar apenas colunas que existem
        columns_to_keep = [col for col in columns_to_keep if col in df.columns]
        df = df[columns_to_keep]
        
        logger.info(f"Dataset preparado: {len(df)} reviews")
        logger.info(f"\n📊 Distribuição de sentimentos:")
        logger.info(f"{df['sentiment'].value_counts()}")
        
        return df
    
    def create_aspect_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria labels de aspectos usando keywords
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
        logger.info(f"💾 Dataset salvo em: {output_path}")
        
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
        }
        
        if 'overall_rating' in df.columns:
            stats['avg_rating'] = df['overall_rating'].mean()
        
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
    logger.info("SENTIBR - Data Loading Pipeline (v2)")
    logger.info("=" * 60)
    
    # Inicializar loader
    loader = DatasetLoader()
    
    # Tentar múltiplas fontes
    df = None
    
    # Método 1: Parquet do HuggingFace
    try:
        logger.info("\n🔄 Método 1: Tentando carregar via HuggingFace Parquet...")
        df = loader.load_from_url_parquet()
    except Exception as e:
        logger.warning(f"⚠️ Método 1 falhou: {e}")
    
    # Método 2: GitHub direto
    if df is None:
        try:
            logger.info("\n🔄 Método 2: Tentando carregar via GitHub...")
            df = loader.load_from_github_direct()
        except Exception as e:
            logger.error(f"❌ Método 2 falhou: {e}")
    
    # Se tudo falhou
    if df is None:
        logger.error("\n" + "=" * 60)
        logger.error("❌ Não foi possível carregar o dataset!")
        logger.error("=" * 60)
        logger.info("\n💡 ALTERNATIVA: Use o dataset de teste rápido:")
        logger.info("   python src/data/quick_test_data.py")
        logger.info("\nIsso criará um dataset sintético pequeno para você começar.")
        sys.exit(1)
    
    # Preparar para análise de sentimento
    df = loader.prepare_for_sentiment_analysis(df)
    
    # Criar labels de aspectos
    df = loader.create_aspect_labels(df)
    
    # Salvar dataset processado
    output_path = loader.save_processed_data(df)
    
    # Estatísticas
    stats = loader.get_statistics(df)
    logger.info("\n" + "=" * 60)
    logger.info("📊 ESTATÍSTICAS DO DATASET")
    logger.info("=" * 60)
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Pipeline concluído com sucesso!")
    logger.info(f"📁 Dataset salvo em: {output_path}")
    logger.info("=" * 60)
    
    logger.info("\n💡 Próximos passos:")
    logger.info("   1. Explorar dados: jupyter notebook notebooks/01_eda.ipynb")
    logger.info("   2. Split dataset: python src/data/split_dataset.py")


if __name__ == "__main__":
    main()
