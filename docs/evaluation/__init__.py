"""
SentiBR - Evaluation Module

Sistema completo de avaliação de modelos de sentimento.
Inclui:
- Métricas clássicas (Accuracy, Precision, Recall, F1)
- LLM-as-Judge para avaliação qualitativa
- Comparação BERT vs GPT
- Análise de erros e casos edge
"""

from .eval_suite import ModelEvaluator, EvaluationResult
from .llm_judge import LLMJudge, JudgmentResult

__all__ = [
    'ModelEvaluator',
    'EvaluationResult',
    'LLMJudge',
    'JudgmentResult'
]

__version__ = '1.0.0'
