"""
Script de teste rápido - Cria dataset sintético pequeno para testar o pipeline
Use este script se quiser testar o sistema antes de baixar o dataset completo
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_dataset(n_samples: int = 1000) -> pd.DataFrame:
    """
    Cria um dataset sintético pequeno para testes
    """
    logger.info(f"Criando dataset sintético com {n_samples} amostras...")
    
    # Templates de reviews por sentimento
    positive_templates = [
        "Produto excelente, superou minhas expectativas! Entrega rápida.",
        "Adorei a qualidade! Recomendo muito, chegou antes do prazo.",
        "Muito bom, vale cada centavo. Atendimento perfeito!",
        "Perfeito! Qualidade top e preço justo. Voltarei a comprar.",
        "Maravilhoso! Produto de ótima qualidade, entrega super rápida.",
    ]
    
    negative_templates = [
        "Produto horrível, veio com defeito. Muito decepcionado.",
        "Péssima qualidade, não recomendo. Entrega atrasou 2 semanas.",
        "Terrível! Não vale o preço. Atendimento ruim.",
        "Decepcionante. Produto quebrado e atendimento péssimo.",
        "Não comprem! Qualidade horrível, dinheiro jogado fora.",
    ]
    
    neutral_templates = [
        "Produto ok, nada de especial. Entrega dentro do prazo.",
        "Atende ao básico. Preço razoável, qualidade média.",
        "Normal. Nem bom nem ruim. Entrega normal.",
        "Comum. Produto adequado mas nada excepcional.",
        "Mediano. Serve para o que preciso mas poderia ser melhor.",
    ]
    
    # Distribuição: 45% positivo, 35% negativo, 20% neutro
    n_pos = int(n_samples * 0.45)
    n_neg = int(n_samples * 0.35)
    n_neu = n_samples - n_pos - n_neg
    
    data = []
    
    # Gerar positivos
    for i in range(n_pos):
        review = np.random.choice(positive_templates)
        data.append({
            'review_text': review,
            'review_title': 'Excelente produto',
            'overall_rating': np.random.choice([4, 5]),
            'sentiment': 'positivo',
            'label': 2,
            'recommend_to_a_friend': 'Sim',
            'has_produto': True,
            'has_entrega': np.random.choice([True, False]),
            'has_atendimento': np.random.choice([True, False]),
            'has_preco': np.random.choice([True, False]),
        })
    
    # Gerar negativos
    for i in range(n_neg):
        review = np.random.choice(negative_templates)
        data.append({
            'review_text': review,
            'review_title': 'Decepcionante',
            'overall_rating': np.random.choice([1, 2]),
            'sentiment': 'negativo',
            'label': 0,
            'recommend_to_a_friend': 'Não',
            'has_produto': True,
            'has_entrega': np.random.choice([True, False]),
            'has_atendimento': np.random.choice([True, False]),
            'has_preco': np.random.choice([True, False]),
        })
    
    # Gerar neutros
    for i in range(n_neu):
        review = np.random.choice(neutral_templates)
        data.append({
            'review_text': review,
            'review_title': 'Normal',
            'overall_rating': 3,
            'sentiment': 'neutro',
            'label': 1,
            'recommend_to_a_friend': np.random.choice(['Sim', 'Não']),
            'has_produto': True,
            'has_entrega': np.random.choice([True, False]),
            'has_atendimento': np.random.choice([True, False]),
            'has_preco': np.random.choice([True, False]),
        })
    
    df = pd.DataFrame(data)
    
    # Embaralhar
    df = df.sample(frac=1).reset_index(drop=True)
    
    logger.info(f"✅ Dataset criado: {len(df)} reviews")
    logger.info(f"   - Positivo: {(df['sentiment']=='positivo').sum()}")
    logger.info(f"   - Negativo: {(df['sentiment']=='negativo').sum()}")
    logger.info(f"   - Neutro: {(df['sentiment']=='neutro').sum()}")
    
    return df


def main():
    logger.info("=" * 60)
    logger.info("SENTIBR - Quick Test Dataset Generator")
    logger.info("=" * 60)
    
    # Criar dataset sintético
    df = create_sample_dataset(n_samples=1000)
    
    # Salvar
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "processed_reviews.csv"
    df.to_csv(output_path, index=False)
    
    logger.info(f"\n✅ Dataset salvo em: {output_path}")
    logger.info(f"📊 Total: {len(df)} reviews")
    logger.info("\n💡 Próximo passo:")
    logger.info("   jupyter notebook notebooks/01_eda.ipynb")
    logger.info("\nOu para usar o dataset real:")
    logger.info("   python src/data/load_data.py")


if __name__ == "__main__":
    main()
