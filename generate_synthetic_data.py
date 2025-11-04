"""
Script para gerar dataset sintético de reviews de restaurantes/iFood usando GPT-4
Este script complementa o B2W dataset com reviews específicas de delivery/restaurantes
"""

import os
import json
import pandas as pd
from openai import OpenAI
from typing import List, Dict
import logging
from pathlib import Path
from tqdm import tqdm
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """
    Gerador de reviews sintéticas de iFood/restaurantes usando GPT-4
    """
    
    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"  # Mais econômico
        
    def generate_review(
        self, 
        sentiment: str, 
        aspects: Dict[str, str] = None
    ) -> Dict:
        """
        Gera uma review sintética com sentimento e aspectos específicos
        
        Args:
            sentiment: 'positivo', 'negativo', ou 'misto'
            aspects: dict com aspectos como {'comida': 'positivo', 'entrega': 'negativo'}
        """
        
        # Prompt engineering para reviews realistas
        prompt = f"""Você é um cliente brasileiro escrevendo uma avaliação de um pedido do iFood.

Instruções:
- Escreva UMA review autêntica e natural em português brasileiro
- Sentimento geral: {sentiment}
- Use linguagem coloquial brasileira (pode incluir gírias leves)
- Comprimento: 30-150 palavras
- Seja específico sobre a experiência
"""
        
        if aspects:
            prompt += "\n- Mencione os seguintes aspectos:\n"
            for aspect, aspect_sentiment in aspects.items():
                prompt += f"  * {aspect}: {aspect_sentiment}\n"
        
        prompt += """
Retorne APENAS um objeto JSON com esta estrutura:
{
    "review_text": "texto da review",
    "review_title": "título curto (3-8 palavras)",
    "rating": <1-5>,
    "sentiment": "positivo/negativo/neutro",
    "aspects": {
        "comida": "positivo/negativo/neutro/null",
        "entrega": "positivo/negativo/neutro/null",
        "atendimento": "positivo/negativo/neutro/null",
        "preco": "positivo/negativo/neutro/null"
    }
}

Exemplo de review positiva:
{
    "review_text": "Pedi uma pizza de calabresa e chegou quentinha em 25 minutos! A massa estava crocante e o recheio muito saboroso. O entregador foi super educado. Só achei um pouco caro, mas valeu a pena pela qualidade. Com certeza vou pedir de novo!",
    "review_title": "Pizza excelente, entrega rápida!",
    "rating": 4,
    "sentiment": "positivo",
    "aspects": {
        "comida": "positivo",
        "entrega": "positivo",
        "atendimento": "positivo",
        "preco": "negativo"
    }
}

Agora gere uma review DIFERENTE:
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates realistic Brazilian Portuguese restaurant reviews in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # Alta temperatura para variedade
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            review_data = json.loads(response.choices[0].message.content)
            return review_data
            
        except Exception as e:
            logger.error(f"Erro ao gerar review: {e}")
            return None
    
    def generate_batch(
        self, 
        n_reviews: int,
        sentiment_distribution: Dict[str, float] = None
    ) -> List[Dict]:
        """
        Gera um batch de reviews
        
        Args:
            n_reviews: Número de reviews a gerar
            sentiment_distribution: ex: {'positivo': 0.6, 'negativo': 0.3, 'misto': 0.1}
        """
        if sentiment_distribution is None:
            sentiment_distribution = {
                'positivo': 0.50,
                'negativo': 0.30,
                'misto': 0.20
            }
        
        reviews = []
        sentiments = []
        
        # Criar lista de sentimentos baseada na distribuição
        for sentiment, proportion in sentiment_distribution.items():
            count = int(n_reviews * proportion)
            sentiments.extend([sentiment] * count)
        
        # Ajustar para atingir exatamente n_reviews
        while len(sentiments) < n_reviews:
            sentiments.append('positivo')
        sentiments = sentiments[:n_reviews]
        
        logger.info(f"Gerando {n_reviews} reviews sintéticas...")
        
        for sentiment in tqdm(sentiments, desc="Gerando reviews"):
            # Definir aspectos baseados no sentimento
            if sentiment == 'positivo':
                aspects = {
                    'comida': 'positivo',
                    'entrega': 'positivo'
                }
            elif sentiment == 'negativo':
                aspects = {
                    'comida': 'negativo',
                    'entrega': 'negativo'
                }
            else:  # misto
                aspects = {
                    'comida': 'positivo',
                    'entrega': 'negativo'
                }
            
            review = self.generate_review(sentiment, aspects)
            
            if review:
                reviews.append(review)
            
            # Rate limiting (evitar exceder limites da API)
            time.sleep(0.5)  # 2 requests/segundo
        
        logger.info(f"✅ {len(reviews)} reviews geradas com sucesso!")
        return reviews
    
    def save_to_csv(self, reviews: List[Dict], filename: str = "synthetic_ifood_reviews.csv"):
        """
        Salva reviews em CSV
        """
        # Flatten aspects para colunas separadas
        flattened = []
        for review in reviews:
            flat_review = {
                'review_text': review['review_text'],
                'review_title': review['review_title'],
                'overall_rating': review['rating'],
                'sentiment': review['sentiment']
            }
            
            # Adicionar aspectos
            if 'aspects' in review:
                for aspect, value in review['aspects'].items():
                    flat_review[f'aspect_{aspect}'] = value
            
            flattened.append(flat_review)
        
        df = pd.DataFrame(flattened)
        
        # Adicionar label numérico
        sentiment_map = {'negativo': 0, 'neutro': 1, 'positivo': 2, 'misto': 1}
        df['label'] = df['sentiment'].map(sentiment_map)
        
        # Salvar
        output_path = Path("data/raw") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        logger.info(f"📁 Dataset salvo em: {output_path}")
        logger.info(f"📊 Estatísticas:")
        logger.info(f"  - Total de reviews: {len(df)}")
        logger.info(f"  - Distribuição de sentimentos:\n{df['sentiment'].value_counts()}")
        logger.info(f"  - Rating médio: {df['overall_rating'].mean():.2f}")
        
        return output_path


def main():
    """
    Função principal
    """
    logger.info("=" * 60)
    logger.info("SENTIBR - Synthetic Data Generator (iFood Reviews)")
    logger.info("=" * 60)
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY não encontrada no .env")
        logger.info("   Crie um arquivo .env com: OPENAI_API_KEY=your_key_here")
        return
    
    # Inicializar gerador
    generator = SyntheticDataGenerator()
    
    # Gerar reviews
    n_reviews = 500  # Comece com poucas para testar
    reviews = generator.generate_batch(
        n_reviews=n_reviews,
        sentiment_distribution={
            'positivo': 0.45,
            'negativo': 0.35,
            'misto': 0.20
        }
    )
    
    # Salvar
    if reviews:
        generator.save_to_csv(reviews)
        logger.info("\n✅ Dataset sintético gerado com sucesso!")
        logger.info("\n💡 Próximos passos:")
        logger.info("   1. Revisar algumas reviews geradas")
        logger.info("   2. Ajustar prompts se necessário")
        logger.info("   3. Gerar mais reviews (~2000-5000)")
        logger.info("   4. Combinar com B2W dataset para treinamento")


if __name__ == "__main__":
    main()
