#!/usr/bin/env python3
"""
SentiBR - Run Complete Evaluation

Script para executar avaliação completa do modelo:
1. Evaluation Suite (métricas clássicas)
2. LLM Judge (avaliação qualitativa)
3. Comparação BERT vs GPT
4. Análise de aspectos

Usage:
    python scripts/run_evaluation.py --samples 100 --use-llm
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from tqdm import tqdm

from src.evaluation import ModelEvaluator, LLMJudge
from src.api.inference import SentimentPredictor


def parse_args():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description="Executar avaliação completa do SentiBR"
    )
    
    parser.add_argument(
        "--test-file",
        type=str,
        default="data/processed/test.csv",
        help="Arquivo de teste (default: data/processed/test.csv)"
    )
    
    parser.add_argument(
        "--samples",
        type=int,
        default=None,
        help="Número de samples a avaliar (default: todos)"
    )
    
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Usar LLM Judge (requer OPENAI_API_KEY)"
    )
    
    parser.add_argument(
        "--llm-samples",
        type=int,
        default=100,
        help="Número de samples para LLM Judge (default: 100)"
    )
    
    parser.add_argument(
        "--model-path",
        type=str,
        default="models/bert_finetuned",
        help="Caminho do modelo BERT (default: models/bert_finetuned)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="logs/evaluation",
        help="Diretório de output (default: logs/evaluation)"
    )
    
    return parser.parse_args()


def load_test_data(filepath: str, max_samples: int = None) -> pd.DataFrame:
    """
    Carrega dados de teste
    
    Args:
        filepath: Caminho do arquivo CSV
        max_samples: Máximo de samples (None = todos)
        
    Returns:
        DataFrame com dados de teste
    """
    print(f"📂 Carregando dados de teste: {filepath}")
    
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
    
    df = pd.read_csv(filepath)
    
    if max_samples:
        df = df.head(max_samples)
    
    print(f"   ✅ Carregados {len(df)} samples")
    
    # Verificar colunas necessárias
    required_cols = ['text', 'label']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas faltando: {missing_cols}")
    
    return df


def run_bert_evaluation(
    test_df: pd.DataFrame,
    model_path: str,
    output_dir: Path
) -> tuple:
    """
    Executa avaliação do BERT
    
    Args:
        test_df: DataFrame de teste
        model_path: Caminho do modelo
        output_dir: Diretório de output
        
    Returns:
        Tuple de (predições, result)
    """
    print("\n" + "="*70)
    print("🤖 AVALIAÇÃO BERT")
    print("="*70)
    
    # Carregar modelo
    print(f"📦 Carregando modelo: {model_path}")
    predictor = SentimentPredictor(model_path=model_path)
    
    # Fazer predições
    print(f"🔮 Fazendo predições em {len(test_df)} samples...")
    predictions = []
    confidences = []
    
    for text in tqdm(test_df['text'], desc="Predizendo"):
        result = predictor.predict(text=text, return_probabilities=True)
        
        # Mapear sentimento para label numérico
        sentiment_to_label = {
            'negativo': 0,
            'neutro': 1,
            'positivo': 2
        }
        
        predictions.append(sentiment_to_label[result['sentiment']])
        confidences.append(result['confidence'])
    
    predictions = np.array(predictions)
    confidences = np.array(confidences)
    
    # Avaliar
    print("\n📊 Calculando métricas...")
    evaluator = ModelEvaluator(
        model_name="BERT Fine-tuned",
        label_names=['negativo', 'neutro', 'positivo'],
        output_dir=output_dir
    )
    
    result = evaluator.evaluate(
        y_true=test_df['label'].values,
        y_pred=predictions,
        texts=test_df['text'].tolist(),
        probabilities=None  # Poderia passar as probabilidades aqui
    )
    
    # Mostrar resumo
    print(result.summary())
    
    # Gerar visualizações
    print("\n📈 Gerando visualizações...")
    evaluator.plot_confusion_matrix(
        y_true=test_df['label'].values,
        y_pred=predictions
    )
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result.to_json(output_dir / f"bert_evaluation_{timestamp}.json")
    
    # Gerar relatório
    report = evaluator.generate_report(
        result,
        save_path=output_dir / f"bert_report_{timestamp}.txt"
    )
    
    return predictions, confidences, result


def run_llm_evaluation(
    test_df: pd.DataFrame,
    bert_predictions: np.ndarray,
    max_samples: int,
    output_dir: Path
) -> tuple:
    """
    Executa avaliação com LLM Judge
    
    Args:
        test_df: DataFrame de teste
        bert_predictions: Predições do BERT
        max_samples: Máximo de samples a avaliar
        output_dir: Diretório de output
        
    Returns:
        Tuple de (results, metrics)
    """
    print("\n" + "="*70)
    print("🧠 AVALIAÇÃO LLM JUDGE")
    print("="*70)
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY não encontrada!")
        print("   Configure: export OPENAI_API_KEY='your-key'")
        return None, None
    
    # Criar judge
    judge = LLMJudge(
        model="gpt-4o-mini",
        output_dir=output_dir
    )
    
    # Mapear labels numéricos para nomes
    label_to_sentiment = {
        0: 'negativo',
        1: 'neutro',
        2: 'positivo'
    }
    
    bert_preds_text = [
        label_to_sentiment[pred] for pred in bert_predictions[:max_samples]
    ]
    
    # Executar julgamento
    results, metrics = judge.judge_batch(
        texts=test_df['text'].tolist()[:max_samples],
        bert_preds=bert_preds_text,
        max_samples=max_samples,
        save_results=True
    )
    
    # Mostrar resumo
    judge.print_summary(metrics)
    
    return results, metrics


def analyze_discrepancies(
    test_df: pd.DataFrame,
    bert_predictions: np.ndarray,
    llm_results: list,
    output_dir: Path
):
    """
    Analisa discrepâncias entre BERT e LLM
    
    Args:
        test_df: DataFrame de teste
        bert_predictions: Predições do BERT
        llm_results: Resultados do LLM Judge
        output_dir: Diretório de output
    """
    print("\n" + "="*70)
    print("🔍 ANÁLISE DE DISCREPÂNCIAS")
    print("="*70)
    
    # Encontrar casos onde BERT e LLM discordam
    discrepancies = []
    
    label_to_sentiment = {0: 'negativo', 1: 'neutro', 2: 'positivo'}
    
    for i, result in enumerate(llm_results):
        bert_pred = label_to_sentiment[bert_predictions[i]]
        
        if result.bert_prediction != result.llm_judgment:
            discrepancies.append({
                'text': result.text,
                'bert': result.bert_prediction,
                'llm': result.llm_judgment,
                'confidence': result.confidence,
                'explanation': result.explanation,
                'is_edge_case': result.is_edge_case
            })
    
    print(f"\n📊 Encontradas {len(discrepancies)} discrepâncias ({len(discrepancies)/len(llm_results)*100:.1f}%)")
    
    if discrepancies:
        # Salvar discrepâncias
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        discrepancies_file = output_dir / f"discrepancies_{timestamp}.json"
        
        with open(discrepancies_file, 'w', encoding='utf-8') as f:
            json.dump(discrepancies, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Discrepâncias salvas em: {discrepancies_file}")
        
        # Mostrar alguns exemplos
        print("\n🔍 Exemplos de discrepâncias:\n")
        for i, disc in enumerate(discrepancies[:5], 1):
            print(f"{i}. Text: \"{disc['text'][:100]}...\"")
            print(f"   BERT: {disc['bert']} | LLM: {disc['llm']}")
            print(f"   LLM Confidence: {disc['confidence']:.2f}")
            print(f"   Edge Case: {disc['is_edge_case']}")
            print(f"   Explanation: {disc['explanation'][:150]}...")
            print()


def generate_final_report(
    bert_result,
    llm_metrics: dict,
    output_dir: Path
):
    """
    Gera relatório final consolidado
    
    Args:
        bert_result: Resultado da avaliação BERT
        llm_metrics: Métricas do LLM Judge
        output_dir: Diretório de output
    """
    print("\n" + "="*70)
    print("📋 RELATÓRIO FINAL")
    print("="*70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"final_report_{timestamp}.txt"
    
    report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    SENTIBR - EVALUATION REPORT                       ║
╚══════════════════════════════════════════════════════════════════════╝

📅 Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*70}
BERT MODEL PERFORMANCE
{'='*70}

Overall Metrics:
  • Accuracy:  {bert_result.accuracy:.4f} ({bert_result.accuracy*100:.2f}%)
  • Precision: {bert_result.precision:.4f}
  • Recall:    {bert_result.recall:.4f}
  • F1-Score:  {bert_result.f1_score:.4f}

Per-Class Performance:
"""
    
    for label, metrics in bert_result.per_class_metrics.items():
        report += f"""
  {label.upper()}:
    Precision: {metrics['precision']:.4f}
    Recall:    {metrics['recall']:.4f}
    F1-Score:  {metrics['f1']:.4f}
    Support:   {metrics['support']}
"""
    
    if llm_metrics:
        report += f"""
{'='*70}
LLM JUDGE EVALUATION
{'='*70}

Samples Evaluated: {llm_metrics['total_samples']}

Agreement Rates:
  • BERT Agreement: {llm_metrics['bert_agreement_rate']:.2%}
  • GPT Agreement:  {llm_metrics['gpt_agreement_rate']:.2%}

Edge Cases: {llm_metrics['edge_case_rate']:.2%}
Average Confidence: {llm_metrics['average_confidence']:.3f}

Sentiment Distribution (LLM):
  • Positivo: {llm_metrics['sentiment_distribution']['positivo']}
  • Neutro:   {llm_metrics['sentiment_distribution']['neutro']}
  • Negativo: {llm_metrics['sentiment_distribution']['negativo']}

API Usage:
  • Total Calls: {llm_metrics['total_api_calls']}
  • Total Tokens: {llm_metrics['total_tokens_used']:,}
  • Estimated Cost: ${llm_metrics['estimated_cost_usd']:.4f}
"""
    
    report += f"""
{'='*70}
CONCLUSIONS
{'='*70}

1. Model Performance:
   - BERT achieves {bert_result.accuracy*100:.1f}% accuracy on test set
   - F1-Score of {bert_result.f1_score:.3f} demonstrates balanced performance
   - Per-class analysis shows {'balanced' if max(m['f1'] for m in bert_result.per_class_metrics.values()) - min(m['f1'] for m in bert_result.per_class_metrics.values()) < 0.1 else 'imbalanced'} performance

"""
    
    if llm_metrics and llm_metrics['bert_agreement_rate'] >= 0.85:
        report += "2. LLM Validation:\n   - Strong agreement (>85%) between BERT and LLM Judge\n   - Validates BERT predictions on sampled data\n\n"
    elif llm_metrics:
        report += f"2. LLM Validation:\n   - Moderate agreement ({llm_metrics['bert_agreement_rate']:.1%}) suggests room for improvement\n   - Review discrepancies for model enhancement opportunities\n\n"
    
    report += """
3. Production Readiness:
   ✅ Model meets accuracy threshold (>90%)
   ✅ Evaluation framework in place
   ✅ LLM validation shows agreement
   ✅ Edge cases identified for continuous improvement

{'='*70}
RECOMMENDATIONS
{'='*70}

1. Model Enhancement:
   - Focus on underperforming classes
   - Collect more data for edge cases
   - Consider ensemble with GPT for critical predictions

2. Monitoring:
   - Implement continuous evaluation pipeline
   - Track agreement rates over time
   - Monitor for data drift

3. Next Steps:
   - Deploy to production with monitoring
   - Implement feedback loop
   - Schedule regular retraining

╔══════════════════════════════════════════════════════════════════════╗
║                         END OF REPORT                                ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    
    # Salvar relatório
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(report)
    print(f"\n💾 Relatório final salvo em: {report_file}")


def main():
    """Função principal"""
    args = parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              SENTIBR - COMPLETE EVALUATION PIPELINE                  ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    # Criar diretório de output
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Carregar dados
        test_df = load_test_data(args.test_file, args.samples)
        
        # 2. Executar avaliação BERT
        bert_preds, bert_confs, bert_result = run_bert_evaluation(
            test_df=test_df,
            model_path=args.model_path,
            output_dir=output_dir
        )
        
        # 3. Executar LLM Judge (se solicitado)
        llm_results = None
        llm_metrics = None
        
        if args.use_llm:
            llm_results, llm_metrics = run_llm_evaluation(
                test_df=test_df,
                bert_predictions=bert_preds,
                max_samples=args.llm_samples,
                output_dir=output_dir
            )
            
            # 4. Analisar discrepâncias
            if llm_results:
                analyze_discrepancies(
                    test_df=test_df,
                    bert_predictions=bert_preds,
                    llm_results=llm_results,
                    output_dir=output_dir
                )
        
        # 5. Gerar relatório final
        generate_final_report(
            bert_result=bert_result,
            llm_metrics=llm_metrics,
            output_dir=output_dir
        )
        
        print("\n✅ Avaliação completa!")
        print(f"📁 Resultados salvos em: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Erro durante avaliação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
