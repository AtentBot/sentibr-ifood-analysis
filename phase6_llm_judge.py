"""
SentiBR - LLM-as-Judge
GPT-4o-mini avalia predições do BERT (DIFERENCIAL!)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import time
from openai import OpenAI
from tqdm import tqdm


class LLMJudge:
    """GPT-4o-mini como juiz para avaliar predições do BERT"""
    
    def __init__(self, api_key: str = None, model: str = 'gpt-4o-mini'):
        """
        Inicializa LLM Judge
        
        Args:
            api_key: OpenAI API key (ou usa variável de ambiente)
            model: Modelo do OpenAI a usar
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.label_map = {0: 'negativo', 1: 'neutro', 2: 'positivo'}
        
        print(f"🤖 LLM Judge inicializado com modelo: {model}")
    
    def create_evaluation_prompt(self, text: str, bert_prediction: str, 
                                bert_confidence: float) -> str:
        """
        Cria prompt para GPT avaliar predição do BERT
        
        Args:
            text: Texto do review
            bert_prediction: Predição do BERT (negativo/neutro/positivo)
            bert_confidence: Confiança da predição
            
        Returns:
            Prompt formatado
        """
        prompt = f"""Você é um especialista em análise de sentimento de reviews de restaurantes brasileiros (estilo iFood).

Sua tarefa é avaliar se o modelo BERT classificou corretamente o sentimento deste review.

**REVIEW:**
"{text}"

**PREDIÇÃO DO BERT:**
- Sentimento: {bert_prediction}
- Confiança: {bert_confidence:.2%}

**SUA AVALIAÇÃO:**

1. Qual é o sentimento REAL deste review? (negativo, neutro ou positivo)
2. A predição do BERT está correta? (sim ou não)
3. Se incorreta, qual deveria ser? (negativo, neutro ou positivo)
4. Nível de concordância com o BERT (1-5, onde 5 = concordo totalmente)
5. Justificativa breve (1-2 frases)

**IMPORTANTE:**
- Considere o contexto brasileiro e expressões coloquiais
- Reviews sobre comida/delivery/atendimento/preço
- Seja rigoroso: neutro significa realmente neutro, não misto
- Considere sarcasmo e ironia

Responda APENAS no formato JSON:
{{
  "real_sentiment": "negativo|neutro|positivo",
  "bert_correct": true|false,
  "should_be": "negativo|neutro|positivo",
  "agreement_level": 1-5,
  "justification": "sua justificativa aqui"
}}"""
        
        return prompt
    
    def evaluate_single_prediction(self, text: str, bert_prediction: str, 
                                   bert_confidence: float, 
                                   retry_attempts: int = 3) -> Dict:
        """
        Avalia uma única predição usando GPT
        
        Args:
            text: Texto do review
            bert_prediction: Predição do BERT
            bert_confidence: Confiança da predição
            retry_attempts: Tentativas em caso de erro
            
        Returns:
            Dict com avaliação do GPT
        """
        prompt = self.create_evaluation_prompt(text, bert_prediction, bert_confidence)
        
        for attempt in range(retry_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Você é um especialista em análise de sentimento."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Baixa temperatura para consistência
                    max_tokens=300,
                    response_format={"type": "json_object"}  # Força resposta JSON
                )
                
                # Parse resposta
                result = json.loads(response.choices[0].message.content)
                
                # Valida campos obrigatórios
                required_fields = ['real_sentiment', 'bert_correct', 'should_be', 
                                 'agreement_level', 'justification']
                if all(field in result for field in required_fields):
                    return result
                else:
                    raise ValueError("Campos obrigatórios faltando na resposta")
                
            except Exception as e:
                if attempt < retry_attempts - 1:
                    print(f"⚠️  Tentativa {attempt + 1} falhou: {e}. Tentando novamente...")
                    time.sleep(1)
                else:
                    print(f"❌ Erro após {retry_attempts} tentativas: {e}")
                    return {
                        'real_sentiment': 'error',
                        'bert_correct': False,
                        'should_be': 'error',
                        'agreement_level': 0,
                        'justification': f'Erro na API: {str(e)}'
                    }
        
        return None
    
    def evaluate_batch(self, predictions_df: pd.DataFrame, 
                      n_samples: int = 100,
                      random_seed: int = 42) -> pd.DataFrame:
        """
        Avalia um batch de predições
        
        Args:
            predictions_df: DataFrame com predições do BERT
            n_samples: Número de samples a avaliar
            random_seed: Seed para reprodutibilidade
            
        Returns:
            DataFrame com avaliações do GPT
        """
        print(f"\n🤖 Iniciando avaliação LLM-as-Judge...")
        print(f"📊 Avaliando {n_samples} predições...")
        
        # Sample estratificado (balance entre classes e acertos/erros)
        if len(predictions_df) > n_samples:
            # 50% corretos, 50% incorretos
            correct = predictions_df[predictions_df['correct']].sample(
                n=n_samples//2, random_state=random_seed
            )
            incorrect = predictions_df[~predictions_df['correct']].sample(
                n=n_samples - n_samples//2, random_state=random_seed
            )
            sample_df = pd.concat([correct, incorrect]).sample(frac=1, random_state=random_seed)
        else:
            sample_df = predictions_df.copy()
        
        # Avalia cada predição
        gpt_evaluations = []
        total_cost = 0.0
        
        for idx, row in tqdm(sample_df.iterrows(), total=len(sample_df), 
                            desc="Avaliando com GPT"):
            
            # Avalia
            start_time = time.time()
            gpt_eval = self.evaluate_single_prediction(
                text=row['text'],
                bert_prediction=row['pred_label'],
                bert_confidence=row['confidence']
            )
            latency = time.time() - start_time
            
            # Adiciona metadados
            gpt_eval['text'] = row['text']
            gpt_eval['bert_prediction'] = row['pred_label']
            gpt_eval['bert_confidence'] = row['confidence']
            gpt_eval['ground_truth'] = row['true_label']
            gpt_eval['bert_was_correct'] = row['correct']
            gpt_eval['latency_seconds'] = latency
            
            # Estima custo (aproximado para gpt-4o-mini)
            # Input: ~150 tokens, Output: ~100 tokens
            # Custo: $0.150 / 1M input tokens, $0.600 / 1M output tokens
            estimated_cost = (150 * 0.150 / 1_000_000) + (100 * 0.600 / 1_000_000)
            gpt_eval['estimated_cost_usd'] = estimated_cost
            total_cost += estimated_cost
            
            gpt_evaluations.append(gpt_eval)
            
            # Rate limiting (opcional)
            time.sleep(0.1)
        
        eval_df = pd.DataFrame(gpt_evaluations)
        
        print(f"\n✅ Avaliação concluída!")
        print(f"💰 Custo estimado total: ${total_cost:.4f}")
        print(f"⏱️  Latência média: {eval_df['latency_seconds'].mean():.2f}s")
        
        return eval_df
    
    def analyze_agreement(self, eval_df: pd.DataFrame) -> Dict:
        """
        Analisa concordância entre BERT, GPT e Ground Truth
        
        Args:
            eval_df: DataFrame com avaliações
            
        Returns:
            Dict com análise de concordância
        """
        print("\n🔍 Analisando concordância BERT vs GPT vs Ground Truth...")
        
        # Remove erros de API
        valid_df = eval_df[eval_df['real_sentiment'] != 'error'].copy()
        
        if len(valid_df) == 0:
            return {'error': 'No valid evaluations'}
        
        # Agreement GPT com Ground Truth
        gpt_correct = (valid_df['real_sentiment'] == valid_df['ground_truth']).sum()
        gpt_accuracy = gpt_correct / len(valid_df)
        
        # Agreement BERT com GPT
        bert_gpt_agreement = valid_df['bert_correct'].sum() / len(valid_df)
        
        # Agreement BERT com Ground Truth
        bert_gt_correct = valid_df['bert_was_correct'].sum()
        bert_gt_accuracy = bert_gt_correct / len(valid_df)
        
        # Casos onde GPT discorda do BERT
        disagreements = valid_df[~valid_df['bert_correct']].copy()
        
        # Agreement level distribution
        agreement_dist = valid_df['agreement_level'].value_counts().to_dict()
        
        analysis = {
            'n_samples': len(valid_df),
            'gpt_accuracy': float(gpt_accuracy),
            'bert_accuracy': float(bert_gt_accuracy),
            'bert_gpt_agreement': float(bert_gpt_agreement),
            'n_disagreements': len(disagreements),
            'disagreement_rate': float(len(disagreements) / len(valid_df)),
            'agreement_level_distribution': agreement_dist,
            'avg_agreement_level': float(valid_df['agreement_level'].mean()),
            'total_cost_usd': float(valid_df['estimated_cost_usd'].sum()),
            'avg_latency_seconds': float(valid_df['latency_seconds'].mean())
        }
        
        return analysis
    
    def get_disagreement_cases(self, eval_df: pd.DataFrame, 
                               n_examples: int = 10) -> List[Dict]:
        """
        Extrai casos onde GPT discorda do BERT
        
        Args:
            eval_df: DataFrame com avaliações
            n_examples: Número de exemplos a retornar
            
        Returns:
            Lista de casos de discordância
        """
        disagreements = eval_df[~eval_df['bert_correct']].copy()
        
        # Ordena por agreement_level (discordâncias mais fortes primeiro)
        disagreements = disagreements.sort_values('agreement_level')
        
        cases = []
        for _, row in disagreements.head(n_examples).iterrows():
            cases.append({
                'text': row['text'][:200] + '...' if len(row['text']) > 200 else row['text'],
                'ground_truth': row['ground_truth'],
                'bert_predicted': row['bert_prediction'],
                'bert_confidence': float(row['bert_confidence']),
                'gpt_says_should_be': row['should_be'],
                'agreement_level': int(row['agreement_level']),
                'justification': row['justification']
            })
        
        return cases
    
    def save_results(self, eval_df: pd.DataFrame, analysis: Dict, 
                    output_dir: str = 'evaluation_results'):
        """
        Salva resultados da avaliação LLM
        
        Args:
            eval_df: DataFrame com avaliações
            analysis: Dict com análise de concordância
            output_dir: Diretório de saída
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salva DataFrame completo
        csv_path = output_path / f'llm_judge_evaluations_{timestamp}.csv'
        eval_df.to_csv(csv_path, index=False)
        print(f"\n💾 Avaliações LLM salvas em: {csv_path}")
        
        # Salva análise
        json_path = output_path / f'llm_judge_analysis_{timestamp}.json'
        
        # Adiciona casos de discordância
        disagreement_cases = self.get_disagreement_cases(eval_df)
        analysis['disagreement_examples'] = disagreement_cases
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Análise salva em: {json_path}")
        
        return csv_path, json_path
    
    def print_summary(self, analysis: Dict):
        """Imprime sumário da avaliação LLM"""
        print("\n" + "="*60)
        print("🤖 SUMÁRIO - LLM-AS-JUDGE (GPT-4o-mini)")
        print("="*60)
        
        print(f"\n📊 Métricas de Concordância:")
        print(f"  • Samples avaliados:        {analysis['n_samples']}")
        print(f"  • GPT Accuracy:             {analysis['gpt_accuracy']:.2%}")
        print(f"  • BERT Accuracy:            {analysis['bert_accuracy']:.2%}")
        print(f"  • BERT-GPT Agreement:       {analysis['bert_gpt_agreement']:.2%}")
        print(f"  • Taxa de Discordância:     {analysis['disagreement_rate']:.2%}")
        print(f"  • Agreement Level médio:    {analysis['avg_agreement_level']:.2f}/5")
        
        print(f"\n💰 Custos e Performance:")
        print(f"  • Custo total:              ${analysis['total_cost_usd']:.4f}")
        print(f"  • Latência média:           {analysis['avg_latency_seconds']:.2f}s")
        
        print("\n" + "="*60)


def run_llm_judge_evaluation(predictions_csv: str, api_key: str = None, 
                             n_samples: int = 100):
    """
    Executa avaliação LLM-as-Judge completa
    
    Args:
        predictions_csv: CSV com predições do BERT
        api_key: OpenAI API key
        n_samples: Número de samples a avaliar
    """
    print("\n🚀 INICIANDO LLM-AS-JUDGE EVALUATION\n")
    
    # Carrega predições
    print(f"📂 Carregando predições de {predictions_csv}...")
    predictions_df = pd.read_csv(predictions_csv)
    print(f"✅ {len(predictions_df)} predições carregadas")
    
    # Inicializa LLM Judge
    judge = LLMJudge(api_key=api_key)
    
    # Avalia batch
    eval_df = judge.evaluate_batch(predictions_df, n_samples=n_samples)
    
    # Analisa concordância
    analysis = judge.analyze_agreement(eval_df)
    
    # Imprime sumário
    judge.print_summary(analysis)
    
    # Salva resultados
    csv_path, json_path = judge.save_results(eval_df, analysis)
    
    print(f"\n✅ LLM Judge evaluation finalizada!")
    
    return eval_df, analysis


if __name__ == '__main__':
    import os
    
    # Configuração
    PREDICTIONS_CSV = 'evaluation_results/predictions_20250106_120000.csv'
    API_KEY = os.getenv('OPENAI_API_KEY')  # Ou passe diretamente
    N_SAMPLES = 100
    
    if not API_KEY:
        print("❌ OPENAI_API_KEY não encontrada!")
        print("Configure: export OPENAI_API_KEY='sua-key-aqui'")
    else:
        eval_df, analysis = run_llm_judge_evaluation(
            PREDICTIONS_CSV, 
            api_key=API_KEY,
            n_samples=N_SAMPLES
        )
