"""
SentiBR - BERT vs GPT Comparison
Comparação completa: latência, custo, qualidade
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import time
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from openai import OpenAI
from tqdm import tqdm
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


class BERTvsGPTComparison:
    """Comparação detalhada BERT vs GPT-4o-mini"""
    
    def __init__(self, bert_model_path: str, openai_api_key: str = None,
                 gpt_model: str = 'gpt-4o-mini'):
        """
        Inicializa comparador
        
        Args:
            bert_model_path: Caminho para modelo BERT
            openai_api_key: OpenAI API key
            gpt_model: Modelo GPT a usar
        """
        # BERT setup
        print("📦 Carregando BERT...")
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tokenizer = BertTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
        self.bert_model = BertForSequenceClassification.from_pretrained(bert_model_path)
        self.bert_model.to(self.device)
        self.bert_model.eval()
        
        # GPT setup
        print("🤖 Configurando GPT...")
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.gpt_model = gpt_model
        
        self.label_map = {0: 'negativo', 1: 'neutro', 2: 'positivo'}
        self.reverse_label_map = {'negativo': 0, 'neutro': 1, 'positivo': 2}
        
        print(f"✅ Modelos carregados! BERT no {self.device}, GPT: {gpt_model}")
    
    def predict_bert(self, text: str) -> Dict:
        """
        Predição com BERT
        
        Args:
            text: Texto do review
            
        Returns:
            Dict com predição, probabilidades e latência
        """
        start_time = time.time()
        
        with torch.no_grad():
            # Tokeniza
            encodings = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors='pt'
            )
            
            input_ids = encodings['input_ids'].to(self.device)
            attention_mask = encodings['attention_mask'].to(self.device)
            
            # Predição
            outputs = self.bert_model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            
            # Probabilidades
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
            pred = logits.argmax(dim=-1).cpu().numpy()[0]
        
        latency = time.time() - start_time
        
        return {
            'prediction': self.label_map[pred],
            'prediction_id': int(pred),
            'probabilities': {
                'negativo': float(probs[0]),
                'neutro': float(probs[1]),
                'positivo': float(probs[2])
            },
            'confidence': float(probs[pred]),
            'latency_seconds': latency,
            'cost_usd': 0.0  # BERT é gratuito após treinamento
        }
    
    def create_gpt_prompt(self, text: str) -> str:
        """
        Cria prompt para GPT classificar sentimento
        
        Args:
            text: Texto do review
            
        Returns:
            Prompt formatado
        """
        prompt = f"""Você é um especialista em análise de sentimento de reviews de restaurantes brasileiros.

Classifique o sentimento deste review em uma das categorias:
- negativo: Cliente insatisfeito, reclamação, experiência ruim
- neutro: Experiência mediana, sem opinião forte, ou misto balanceado
- positivo: Cliente satisfeito, elogio, experiência boa

**REVIEW:**
"{text}"

**IMPORTANTE:**
- Considere o contexto brasileiro e expressões coloquiais
- Reviews sobre comida, delivery, atendimento e preço
- Seja preciso: neutro significa realmente neutro, não misto positivo
- Considere sarcasmo e ironia

Responda APENAS no formato JSON:
{{
  "sentiment": "negativo|neutro|positivo",
  "confidence": 0.0-1.0,
  "reasoning": "breve justificativa (1 frase)"
}}"""
        
        return prompt
    
    def predict_gpt(self, text: str, retry_attempts: int = 3) -> Dict:
        """
        Predição com GPT
        
        Args:
            text: Texto do review
            retry_attempts: Tentativas em caso de erro
            
        Returns:
            Dict com predição, confiança e latência
        """
        prompt = self.create_gpt_prompt(text)
        start_time = time.time()
        
        for attempt in range(retry_attempts):
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.gpt_model,
                    messages=[
                        {"role": "system", "content": "Você é um especialista em análise de sentimento."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=150,
                    response_format={"type": "json_object"}
                )
                
                latency = time.time() - start_time
                
                # Parse resposta
                result = json.loads(response.choices[0].message.content)
                
                # Calcula custo estimado
                # gpt-4o-mini: $0.150 / 1M input tokens, $0.600 / 1M output tokens
                # Estima ~200 input tokens, ~50 output tokens
                input_tokens = 200
                output_tokens = 50
                cost = (input_tokens * 0.150 / 1_000_000) + (output_tokens * 0.600 / 1_000_000)
                
                return {
                    'prediction': result['sentiment'],
                    'prediction_id': self.reverse_label_map.get(result['sentiment'], -1),
                    'confidence': float(result.get('confidence', 0.0)),
                    'reasoning': result.get('reasoning', ''),
                    'latency_seconds': latency,
                    'cost_usd': cost
                }
                
            except Exception as e:
                if attempt < retry_attempts - 1:
                    time.sleep(1)
                else:
                    latency = time.time() - start_time
                    return {
                        'prediction': 'error',
                        'prediction_id': -1,
                        'confidence': 0.0,
                        'reasoning': f'Erro: {str(e)}',
                        'latency_seconds': latency,
                        'cost_usd': 0.0
                    }
    
    def compare_batch(self, test_df: pd.DataFrame, 
                     n_samples: int = 100,
                     random_seed: int = 42) -> pd.DataFrame:
        """
        Compara BERT vs GPT em um batch
        
        Args:
            test_df: DataFrame com test data
            n_samples: Número de samples
            random_seed: Seed para reprodutibilidade
            
        Returns:
            DataFrame com comparação
        """
        print(f"\n🔬 Iniciando comparação BERT vs GPT...")
        print(f"📊 Testando {n_samples} reviews...")
        
        # Sample
        if len(test_df) > n_samples:
            sample_df = test_df.sample(n=n_samples, random_state=random_seed)
        else:
            sample_df = test_df.copy()
        
        comparisons = []
        
        for idx, row in tqdm(sample_df.iterrows(), total=len(sample_df),
                            desc="Comparando modelos"):
            
            text = row['text']
            true_label = row['label']
            true_label_str = self.label_map[true_label]
            
            # BERT prediction
            bert_result = self.predict_bert(text)
            
            # GPT prediction
            gpt_result = self.predict_gpt(text)
            
            # Registra comparação
            comparison = {
                'text': text,
                'true_label': true_label_str,
                'true_label_id': true_label,
                
                # BERT
                'bert_prediction': bert_result['prediction'],
                'bert_confidence': bert_result['confidence'],
                'bert_latency': bert_result['latency_seconds'],
                'bert_cost': bert_result['cost_usd'],
                'bert_correct': bert_result['prediction'] == true_label_str,
                
                # GPT
                'gpt_prediction': gpt_result['prediction'],
                'gpt_confidence': gpt_result['confidence'],
                'gpt_reasoning': gpt_result['reasoning'],
                'gpt_latency': gpt_result['latency_seconds'],
                'gpt_cost': gpt_result['cost_usd'],
                'gpt_correct': gpt_result['prediction'] == true_label_str,
                
                # Concordância
                'models_agree': bert_result['prediction'] == gpt_result['prediction'],
                
                # Probabilidades BERT
                'bert_prob_neg': bert_result['probabilities']['negativo'],
                'bert_prob_neu': bert_result['probabilities']['neutro'],
                'bert_prob_pos': bert_result['probabilities']['positivo']
            }
            
            comparisons.append(comparison)
            
            # Rate limiting para GPT
            time.sleep(0.1)
        
        comp_df = pd.DataFrame(comparisons)
        
        print(f"\n✅ Comparação concluída!")
        
        return comp_df
    
    def analyze_comparison(self, comp_df: pd.DataFrame) -> Dict:
        """
        Analisa resultados da comparação
        
        Args:
            comp_df: DataFrame com comparações
            
        Returns:
            Dict com análise completa
        """
        print("\n📊 Analisando resultados da comparação...")
        
        # Remove erros GPT
        valid_df = comp_df[comp_df['gpt_prediction'] != 'error'].copy()
        
        # Métricas BERT
        bert_accuracy = valid_df['bert_correct'].mean()
        bert_avg_latency = valid_df['bert_latency'].mean()
        bert_p95_latency = valid_df['bert_latency'].quantile(0.95)
        bert_total_cost = valid_df['bert_cost'].sum()
        
        # Métricas GPT
        gpt_accuracy = valid_df['gpt_correct'].mean()
        gpt_avg_latency = valid_df['gpt_latency'].mean()
        gpt_p95_latency = valid_df['gpt_latency'].quantile(0.95)
        gpt_total_cost = valid_df['gpt_cost'].sum()
        
        # Concordância
        agreement_rate = valid_df['models_agree'].mean()
        both_correct = (valid_df['bert_correct'] & valid_df['gpt_correct']).sum()
        both_wrong = (~valid_df['bert_correct'] & ~valid_df['gpt_correct']).sum()
        bert_right_gpt_wrong = (valid_df['bert_correct'] & ~valid_df['gpt_correct']).sum()
        gpt_right_bert_wrong = (~valid_df['bert_correct'] & valid_df['gpt_correct']).sum()
        
        # Análise de trade-offs
        latency_ratio = gpt_avg_latency / bert_avg_latency if bert_avg_latency > 0 else 0
        accuracy_diff = gpt_accuracy - bert_accuracy
        
        analysis = {
            'n_samples': len(valid_df),
            
            'bert_metrics': {
                'accuracy': float(bert_accuracy),
                'avg_latency_ms': float(bert_avg_latency * 1000),
                'p95_latency_ms': float(bert_p95_latency * 1000),
                'total_cost_usd': float(bert_total_cost),
                'cost_per_request': 0.0
            },
            
            'gpt_metrics': {
                'accuracy': float(gpt_accuracy),
                'avg_latency_ms': float(gpt_avg_latency * 1000),
                'p95_latency_ms': float(gpt_p95_latency * 1000),
                'total_cost_usd': float(gpt_total_cost),
                'cost_per_request': float(gpt_total_cost / len(valid_df))
            },
            
            'comparison': {
                'agreement_rate': float(agreement_rate),
                'both_correct': int(both_correct),
                'both_wrong': int(both_wrong),
                'bert_right_gpt_wrong': int(bert_right_gpt_wrong),
                'gpt_right_bert_wrong': int(gpt_right_bert_wrong),
                'latency_ratio': float(latency_ratio),
                'accuracy_difference': float(accuracy_diff),
                'gpt_is_better': gpt_accuracy > bert_accuracy
            },
            
            'trade_off_analysis': self._analyze_tradeoffs(
                bert_accuracy, gpt_accuracy,
                bert_avg_latency, gpt_avg_latency,
                bert_total_cost, gpt_total_cost,
                len(valid_df)
            )
        }
        
        return analysis
    
    def _analyze_tradeoffs(self, bert_acc, gpt_acc, bert_lat, gpt_lat,
                          bert_cost, gpt_cost, n_samples) -> Dict:
        """Analisa trade-offs detalhados"""
        
        # Calcula custo anual estimado para diferentes volumes
        volumes = [1000, 10000, 100000, 1000000]  # requests/dia
        
        tradeoffs = {
            'quality_vs_cost': {
                'accuracy_gain': float(gpt_acc - bert_acc),
                'accuracy_gain_pct': float((gpt_acc - bert_acc) / bert_acc * 100) if bert_acc > 0 else 0,
                'cost_increase': 'infinite' if bert_cost == 0 else f"{(gpt_cost / bert_cost - 1) * 100:.0f}%"
            },
            
            'quality_vs_latency': {
                'accuracy_gain': float(gpt_acc - bert_acc),
                'latency_increase_ms': float((gpt_lat - bert_lat) * 1000),
                'latency_multiplier': float(gpt_lat / bert_lat) if bert_lat > 0 else 0
            },
            
            'cost_projections': {}
        }
        
        for vol in volumes:
            requests_per_year = vol * 365
            bert_annual = 0.0  # BERT é grátis (assumindo infra existente)
            gpt_annual = (gpt_cost / n_samples) * requests_per_year
            
            tradeoffs['cost_projections'][f'{vol}_req_per_day'] = {
                'bert_annual_usd': float(bert_annual),
                'gpt_annual_usd': float(gpt_annual),
                'difference_usd': float(gpt_annual - bert_annual)
            }
        
        # Recomendação
        if gpt_acc - bert_acc > 0.05:  # 5% better
            recommendation = "GPT recomendado se budget permitir - ganho significativo de qualidade"
        elif gpt_acc - bert_acc > 0.02:  # 2% better
            recommendation = "GPT para casos críticos, BERT para volume - ganho moderado"
        elif gpt_acc > bert_acc:
            recommendation = "BERT recomendado - GPT tem ganho marginal que não justifica custo"
        else:
            recommendation = "BERT claramente superior - use GPT apenas para validação"
        
        tradeoffs['recommendation'] = recommendation
        
        return tradeoffs
    
    def save_results(self, comp_df: pd.DataFrame, analysis: Dict,
                    output_dir: str = 'evaluation_results'):
        """Salva resultados da comparação"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salva comparações
        csv_path = output_path / f'bert_vs_gpt_comparison_{timestamp}.csv'
        comp_df.to_csv(csv_path, index=False)
        print(f"\n💾 Comparações salvas em: {csv_path}")
        
        # Salva análise
        json_path = output_path / f'bert_vs_gpt_analysis_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"💾 Análise salva em: {json_path}")
        
        # Plota comparações
        self.plot_comparison(comp_df, analysis, output_path, timestamp)
        
        return csv_path, json_path
    
    def plot_comparison(self, comp_df: pd.DataFrame, analysis: Dict,
                       output_dir: Path, timestamp: str):
        """Cria visualizações da comparação"""
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Accuracy comparison
        ax1 = axes[0, 0]
        models = ['BERT', 'GPT-4o-mini']
        accuracies = [
            analysis['bert_metrics']['accuracy'],
            analysis['gpt_metrics']['accuracy']
        ]
        colors = ['#4CAF50', '#2196F3']
        ax1.bar(models, accuracies, color=colors)
        ax1.set_ylabel('Accuracy')
        ax1.set_title('Accuracy Comparison')
        ax1.set_ylim([0, 1])
        for i, v in enumerate(accuracies):
            ax1.text(i, v + 0.02, f'{v:.2%}', ha='center', fontweight='bold')
        
        # 2. Latency comparison
        ax2 = axes[0, 1]
        latencies = [
            analysis['bert_metrics']['avg_latency_ms'],
            analysis['gpt_metrics']['avg_latency_ms']
        ]
        ax2.bar(models, latencies, color=colors)
        ax2.set_ylabel('Latency (ms)')
        ax2.set_title('Average Latency Comparison')
        for i, v in enumerate(latencies):
            ax2.text(i, v + max(latencies)*0.02, f'{v:.0f}ms', ha='center', fontweight='bold')
        
        # 3. Cost comparison
        ax3 = axes[1, 0]
        costs_per_1k = [
            0.0,  # BERT
            analysis['gpt_metrics']['cost_per_request'] * 1000
        ]
        ax3.bar(models, costs_per_1k, color=colors)
        ax3.set_ylabel('Cost (USD)')
        ax3.set_title('Cost per 1,000 Requests')
        for i, v in enumerate(costs_per_1k):
            ax3.text(i, v + max(costs_per_1k)*0.02, f'${v:.2f}', ha='center', fontweight='bold')
        
        # 4. Agreement analysis
        ax4 = axes[1, 1]
        categories = ['Both\nCorrect', 'Both\nWrong', 'Only\nBERT', 'Only\nGPT']
        values = [
            analysis['comparison']['both_correct'],
            analysis['comparison']['both_wrong'],
            analysis['comparison']['bert_right_gpt_wrong'],
            analysis['comparison']['gpt_right_bert_wrong']
        ]
        colors_agree = ['#4CAF50', '#F44336', '#FFC107', '#2196F3']
        ax4.bar(categories, values, color=colors_agree)
        ax4.set_ylabel('Number of Samples')
        ax4.set_title('Agreement Analysis')
        for i, v in enumerate(values):
            ax4.text(i, v + max(values)*0.02, str(v), ha='center', fontweight='bold')
        
        plt.tight_layout()
        
        plot_path = output_dir / f'bert_vs_gpt_plots_{timestamp}.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Plots salvos em: {plot_path}")
    
    def print_summary(self, analysis: Dict):
        """Imprime sumário da comparação"""
        print("\n" + "="*70)
        print("⚖️  BERT vs GPT-4o-mini - COMPARAÇÃO COMPLETA")
        print("="*70)
        
        print(f"\n🎯 QUALIDADE:")
        print(f"  BERT Accuracy:      {analysis['bert_metrics']['accuracy']:.2%}")
        print(f"  GPT Accuracy:       {analysis['gpt_metrics']['accuracy']:.2%}")
        print(f"  Diferença:          {analysis['comparison']['accuracy_difference']:+.2%}")
        print(f"  Concordância:       {analysis['comparison']['agreement_rate']:.2%}")
        
        print(f"\n⚡ LATÊNCIA:")
        print(f"  BERT média:         {analysis['bert_metrics']['avg_latency_ms']:.0f}ms")
        print(f"  GPT média:          {analysis['gpt_metrics']['avg_latency_ms']:.0f}ms")
        print(f"  GPT é {analysis['comparison']['latency_ratio']:.1f}x mais lento")
        
        print(f"\n💰 CUSTO:")
        print(f"  BERT total:         ${analysis['bert_metrics']['total_cost_usd']:.4f}")
        print(f"  GPT total:          ${analysis['gpt_metrics']['total_cost_usd']:.4f}")
        print(f"  GPT por request:    ${analysis['gpt_metrics']['cost_per_request']:.6f}")
        
        print(f"\n📊 TRADE-OFF ANALYSIS:")
        tradeoff = analysis['trade_off_analysis']
        print(f"  Ganho de qualidade: {tradeoff['quality_vs_cost']['accuracy_gain']:+.2%}")
        print(f"  Aumento de latência: {tradeoff['quality_vs_latency']['latency_increase_ms']:.0f}ms")
        
        print(f"\n💡 RECOMENDAÇÃO:")
        print(f"  {tradeoff['recommendation']}")
        
        print("\n" + "="*70)


def run_bert_vs_gpt_comparison(bert_model_path: str, test_data_path: str,
                               openai_api_key: str, n_samples: int = 100):
    """
    Executa comparação completa BERT vs GPT
    
    Args:
        bert_model_path: Caminho para modelo BERT
        test_data_path: Caminho para test data
        openai_api_key: OpenAI API key
        n_samples: Número de samples
    """
    print("\n🚀 INICIANDO COMPARAÇÃO BERT vs GPT-4o-mini\n")
    
    # Carrega test data
    print(f"📂 Carregando test data de {test_data_path}...")
    test_df = pd.read_csv(test_data_path)
    print(f"✅ {len(test_df)} exemplos carregados")
    
    # Inicializa comparador
    comparator = BERTvsGPTComparison(bert_model_path, openai_api_key)
    
    # Executa comparação
    comp_df = comparator.compare_batch(test_df, n_samples=n_samples)
    
    # Analisa resultados
    analysis = comparator.analyze_comparison(comp_df)
    
    # Imprime sumário
    comparator.print_summary(analysis)
    
    # Salva resultados
    csv_path, json_path = comparator.save_results(comp_df, analysis)
    
    print(f"\n✅ Comparação completa finalizada!")
    
    return comp_df, analysis


if __name__ == '__main__':
    import os
    
    # Configuração
    BERT_MODEL_PATH = 'models/bert_finetuned'
    TEST_DATA_PATH = 'data/processed/test.csv'
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    N_SAMPLES = 100
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY não encontrada!")
        print("Configure: export OPENAI_API_KEY='sua-key-aqui'")
    else:
        comp_df, analysis = run_bert_vs_gpt_comparison(
            BERT_MODEL_PATH,
            TEST_DATA_PATH,
            OPENAI_API_KEY,
            n_samples=N_SAMPLES
        )
