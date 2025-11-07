"""
SentiBR - LLM-as-Judge

Sistema de avaliação usando LLM (GPT-4o-mini) como juiz.

Features:
- Avaliação qualitativa de predições
- Comparação BERT vs GPT
- Análise de casos edge
- Detecção de nuances
- Explicações detalhadas
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

from openai import OpenAI, AsyncOpenAI
import pandas as pd
from tqdm import tqdm


@dataclass
class JudgmentResult:
    """Resultado de julgamento do LLM"""
    
    text: str
    bert_prediction: str
    gpt_prediction: str
    llm_judgment: str
    explanation: str
    confidence: float
    agreement_with_bert: bool
    agreement_with_gpt: bool
    is_edge_case: bool
    aspects: Dict[str, str]
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return asdict(self)


class LLMJudge:
    """
    LLM-as-Judge: Usa GPT-4o-mini para avaliar predições
    
    Features:
    - Avaliação de qualidade das predições
    - Comparação entre modelos
    - Identificação de casos edge
    - Análise de aspectos (comida, entrega, serviço, preço)
    - Explicações detalhadas
    
    Example:
        >>> judge = LLMJudge(api_key="your-key")
        >>> result = judge.judge_single(
        ...     text="A comida estava péssima!",
        ...     bert_pred="negativo",
        ...     gpt_pred="negativo"
        ... )
        >>> print(result.explanation)
    """
    
    SYSTEM_PROMPT = """Você é um especialista em análise de sentimentos de reviews de restaurantes do iFood.

Sua tarefa é avaliar predições de modelos de IA e determinar se elas estão corretas.

Para cada review, você deve:
1. Analisar o sentimento geral (positivo, neutro ou negativo)
2. Identificar os aspectos mencionados:
   - Comida (qualidade, sabor, temperatura)
   - Entrega (rapidez, estado da comida, embalagem)
   - Serviço (atendimento, cordialidade)
   - Preço (custo-benefício, valor)
3. Avaliar se as predições dos modelos estão corretas
4. Identificar casos ambíguos ou difíceis (edge cases)
5. Fornecer uma explicação detalhada

Seja objetivo, preciso e considere nuances da língua portuguesa brasileira."""
    
    USER_PROMPT_TEMPLATE = """Review: "{text}"

Predição BERT: {bert_pred}
Predição GPT: {gpt_pred}

Por favor, analise este review e responda em JSON com o seguinte formato:

{{
    "sentiment": "positivo|neutro|negativo",
    "confidence": 0.0-1.0,
    "bert_correct": true|false,
    "gpt_correct": true|false,
    "is_edge_case": true|false,
    "aspects": {{
        "food": "positivo|neutro|negativo|não mencionado",
        "delivery": "positivo|neutro|negativo|não mencionado",
        "service": "positivo|neutro|negativo|não mencionado",
        "price": "positivo|neutro|negativo|não mencionado"
    }},
    "explanation": "Explicação detalhada da sua análise"
}}

Responda APENAS com o JSON, sem texto adicional."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        output_dir: Optional[Path] = None
    ):
        """
        Inicializa LLM Judge
        
        Args:
            api_key: OpenAI API key (ou usa OPENAI_API_KEY env var)
            model: Modelo a usar (default: gpt-4o-mini)
            temperature: Temperatura para sampling (0-1)
            max_tokens: Máximo de tokens na resposta
            output_dir: Diretório para salvar resultados
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key não encontrada. "
                "Defina OPENAI_API_KEY ou passe api_key"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.output_dir = output_dir or Path("logs/llm_judge")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clients
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        # Stats
        self.total_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        
        print(f"✅ LLM Judge inicializado com modelo: {self.model}")
    
    def judge_single(
        self,
        text: str,
        bert_pred: str,
        gpt_pred: Optional[str] = None
    ) -> JudgmentResult:
        """
        Avalia uma única predição
        
        Args:
            text: Texto do review
            bert_pred: Predição do BERT
            gpt_pred: Predição do GPT (opcional)
            
        Returns:
            JudgmentResult com análise completa
        """
        # Se não tem predição GPT, gera uma
        if gpt_pred is None:
            gpt_pred = self._get_gpt_prediction(text)
        
        # Criar prompt
        user_prompt = self.USER_PROMPT_TEMPLATE.format(
            text=text,
            bert_pred=bert_pred,
            gpt_pred=gpt_pred
        )
        
        # Chamar API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Parse resposta
            judgment_data = json.loads(response.choices[0].message.content)
            
            # Atualizar stats
            self.total_calls += 1
            self.total_tokens += response.usage.total_tokens
            self.total_cost += self._calculate_cost(response.usage.total_tokens)
            
            # Criar resultado
            result = JudgmentResult(
                text=text,
                bert_prediction=bert_pred,
                gpt_prediction=gpt_pred,
                llm_judgment=judgment_data['sentiment'],
                explanation=judgment_data['explanation'],
                confidence=judgment_data['confidence'],
                agreement_with_bert=judgment_data['bert_correct'],
                agreement_with_gpt=judgment_data['gpt_correct'],
                is_edge_case=judgment_data['is_edge_case'],
                aspects=judgment_data['aspects'],
                timestamp=datetime.now().isoformat()
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao julgar: {e}")
            # Retornar resultado de erro
            return JudgmentResult(
                text=text,
                bert_prediction=bert_pred,
                gpt_prediction=gpt_pred or "error",
                llm_judgment="error",
                explanation=f"Erro: {str(e)}",
                confidence=0.0,
                agreement_with_bert=False,
                agreement_with_gpt=False,
                is_edge_case=True,
                aspects={},
                timestamp=datetime.now().isoformat()
            )
    
    def judge_batch(
        self,
        texts: List[str],
        bert_preds: List[str],
        gpt_preds: Optional[List[str]] = None,
        max_samples: Optional[int] = None,
        save_results: bool = True
    ) -> Tuple[List[JudgmentResult], Dict[str, Any]]:
        """
        Avalia um lote de predições
        
        Args:
            texts: Lista de textos
            bert_preds: Lista de predições BERT
            gpt_preds: Lista de predições GPT (opcional)
            max_samples: Máximo de samples a avaliar
            save_results: Se deve salvar resultados em JSON
            
        Returns:
            Tuple de (resultados, métricas agregadas)
        """
        if gpt_preds is None:
            gpt_preds = [None] * len(texts)
        
        # Limitar samples se necessário
        if max_samples:
            texts = texts[:max_samples]
            bert_preds = bert_preds[:max_samples]
            gpt_preds = gpt_preds[:max_samples]
        
        print(f"🔍 Julgando {len(texts)} samples com LLM...")
        
        results = []
        for text, bert_pred, gpt_pred in tqdm(
            zip(texts, bert_preds, gpt_preds),
            total=len(texts),
            desc="Julgando"
        ):
            result = self.judge_single(text, bert_pred, gpt_pred)
            results.append(result)
            
            # Rate limiting básico
            time.sleep(0.1)
        
        # Calcular métricas agregadas
        metrics = self._calculate_aggregate_metrics(results)
        
        # Salvar resultados
        if save_results:
            self._save_results(results, metrics)
        
        return results, metrics
    
    def _get_gpt_prediction(self, text: str) -> str:
        """
        Obtém predição do GPT para um texto
        
        Args:
            text: Texto do review
            
        Returns:
            Predição (positivo/neutro/negativo)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um classificador de sentimentos. "
                                   "Responda apenas: positivo, neutro ou negativo."
                    },
                    {
                        "role": "user",
                        "content": f"Classifique o sentimento: {text}"
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            prediction = response.choices[0].message.content.strip().lower()
            
            # Normalizar resposta
            if 'positivo' in prediction or 'positiva' in prediction:
                return 'positivo'
            elif 'negativo' in prediction or 'negativa' in prediction:
                return 'negativo'
            else:
                return 'neutro'
                
        except Exception as e:
            print(f"⚠️ Erro ao obter predição GPT: {e}")
            return 'neutro'
    
    def _calculate_cost(self, tokens: int) -> float:
        """
        Calcula custo da chamada
        
        GPT-4o-mini pricing (Nov 2024):
        - Input: $0.15 / 1M tokens
        - Output: $0.60 / 1M tokens
        
        Assumindo 50/50 split
        """
        input_tokens = tokens * 0.5
        output_tokens = tokens * 0.5
        
        cost = (input_tokens * 0.15 / 1_000_000) + \
               (output_tokens * 0.60 / 1_000_000)
        
        return cost
    
    def _calculate_aggregate_metrics(
        self,
        results: List[JudgmentResult]
    ) -> Dict[str, Any]:
        """
        Calcula métricas agregadas dos resultados
        
        Returns:
            Dict com métricas
        """
        total = len(results)
        
        # Acordos
        bert_agreements = sum(r.agreement_with_bert for r in results)
        gpt_agreements = sum(r.agreement_with_gpt for r in results)
        
        # Edge cases
        edge_cases = sum(r.is_edge_case for r in results)
        
        # Distribuição de sentimentos
        sentiments = [r.llm_judgment for r in results]
        sentiment_dist = {
            'positivo': sentiments.count('positivo'),
            'neutro': sentiments.count('neutro'),
            'negativo': sentiments.count('negativo')
        }
        
        # Confiança média
        avg_confidence = sum(r.confidence for r in results) / total
        
        return {
            'total_samples': total,
            'bert_agreement_rate': bert_agreements / total,
            'gpt_agreement_rate': gpt_agreements / total,
            'edge_case_rate': edge_cases / total,
            'sentiment_distribution': sentiment_dist,
            'average_confidence': avg_confidence,
            'total_api_calls': self.total_calls,
            'total_tokens_used': self.total_tokens,
            'estimated_cost_usd': self.total_cost
        }
    
    def _save_results(
        self,
        results: List[JudgmentResult],
        metrics: Dict[str, Any]
    ) -> None:
        """Salva resultados em JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salvar resultados individuais
        results_file = self.output_dir / f"judgments_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(
                [r.to_dict() for r in results],
                f,
                indent=2,
                ensure_ascii=False
            )
        
        # Salvar métricas
        metrics_file = self.output_dir / f"metrics_{timestamp}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados salvos:")
        print(f"   - {results_file}")
        print(f"   - {metrics_file}")
    
    def print_summary(self, metrics: Dict[str, Any]) -> None:
        """Imprime resumo das métricas"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  LLM JUDGE SUMMARY                           ║
╚══════════════════════════════════════════════════════════════╝

📊 Samples: {metrics['total_samples']}

🤝 Agreement Rates:
   • BERT: {metrics['bert_agreement_rate']:.2%}
   • GPT:  {metrics['gpt_agreement_rate']:.2%}

🎯 Edge Cases: {metrics['edge_case_rate']:.2%}

💯 Average Confidence: {metrics['average_confidence']:.3f}

📈 Sentiment Distribution:
   • Positivo: {metrics['sentiment_distribution']['positivo']}
   • Neutro:   {metrics['sentiment_distribution']['neutro']}
   • Negativo: {metrics['sentiment_distribution']['negativo']}

💰 API Usage:
   • Calls:  {metrics['total_api_calls']}
   • Tokens: {metrics['total_tokens_used']:,}
   • Cost:   ${metrics['estimated_cost_usd']:.4f}

""")


def main():
    """Exemplo de uso"""
    print("🎯 SentiBR LLM Judge - Example")
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY não encontrada!")
        print("   Configure: export OPENAI_API_KEY='your-key'")
        return
    
    # Criar judge
    judge = LLMJudge(model="gpt-4o-mini")
    
    # Exemplos de teste
    test_cases = [
        {
            "text": "A pizza estava simplesmente divina! Chegou quentinha e o sabor estava perfeito. Super recomendo!",
            "bert": "positivo"
        },
        {
            "text": "Comida horrível, fria e sem sabor. Péssima experiência!",
            "bert": "negativo"
        },
        {
            "text": "A comida estava boa, mas demorou muito. Preço ok.",
            "bert": "neutro"
        },
        {
            "text": "Não era exatamente o que eu esperava, mas também não posso reclamar.",
            "bert": "neutro"
        }
    ]
    
    print(f"\n🔍 Julgando {len(test_cases)} casos de teste...\n")
    
    results = []
    for i, case in enumerate(test_cases, 1):
        print(f"{'='*70}")
        print(f"Caso {i}/{len(test_cases)}")
        print(f"{'='*70}")
        print(f"Text: {case['text']}")
        print(f"BERT: {case['bert']}")
        
        result = judge.judge_single(
            text=case['text'],
            bert_pred=case['bert']
        )
        
        results.append(result)
        
        print(f"GPT:  {result.gpt_prediction}")
        print(f"LLM:  {result.llm_judgment}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Edge Case: {result.is_edge_case}")
        print(f"\nExplanation: {result.explanation}")
        print()
    
    # Calcular e mostrar métricas
    metrics = judge._calculate_aggregate_metrics(results)
    judge.print_summary(metrics)


if __name__ == "__main__":
    main()
