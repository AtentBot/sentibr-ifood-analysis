"""
SentiBR - Evaluation Suite

Framework completo de avaliação de modelos de sentimento.

Features:
- Métricas clássicas (Accuracy, Precision, Recall, F1)
- Confusion Matrix
- Análise por classe
- Análise de erros
- Relatórios em JSON e HTML
- Integration com MLflow
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns


@dataclass
class EvaluationResult:
    """Resultado completo de uma avaliação"""
    
    # Métricas principais
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    
    # Métricas por classe
    per_class_metrics: Dict[str, Dict[str, float]]
    
    # Confusion Matrix
    confusion_matrix: List[List[int]]
    
    # Análise de erros
    error_analysis: Dict[str, Any]
    
    # Metadata
    timestamp: str
    num_samples: int
    model_name: str
    
    # Métricas adicionais
    macro_avg: Dict[str, float]
    weighted_avg: Dict[str, float]
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return asdict(self)
    
    def to_json(self, filepath: Path) -> None:
        """Salva resultado em JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def summary(self) -> str:
        """Retorna resumo formatado"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              EVALUATION SUMMARY - {self.model_name}              
╚══════════════════════════════════════════════════════════════╝

📊 Overall Metrics:
   • Accuracy:  {self.accuracy:.4f}
   • Precision: {self.precision:.4f}
   • Recall:    {self.recall:.4f}
   • F1-Score:  {self.f1_score:.4f}

📈 Per-Class Performance:
{self._format_per_class_metrics()}

🔍 Dataset Info:
   • Samples: {self.num_samples}
   • Timestamp: {self.timestamp}
"""
    
    def _format_per_class_metrics(self) -> str:
        """Formata métricas por classe"""
        lines = []
        for label, metrics in self.per_class_metrics.items():
            lines.append(f"   {label}:")
            lines.append(f"      Precision: {metrics['precision']:.4f}")
            lines.append(f"      Recall:    {metrics['recall']:.4f}")
            lines.append(f"      F1-Score:  {metrics['f1']:.4f}")
            lines.append(f"      Support:   {metrics['support']}")
        return "\n".join(lines)


class ModelEvaluator:
    """
    Avaliador completo de modelos de sentimento
    
    Features:
    - Métricas clássicas
    - Confusion Matrix
    - Análise de erros
    - Visualizações
    - Export em múltiplos formatos
    
    Example:
        >>> evaluator = ModelEvaluator(model_name="BERT Fine-tuned")
        >>> result = evaluator.evaluate(y_true, y_pred, texts)
        >>> print(result.summary())
        >>> result.to_json("evaluation_results.json")
    """
    
    def __init__(
        self,
        model_name: str = "Model",
        label_names: Optional[List[str]] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Inicializa avaliador
        
        Args:
            model_name: Nome do modelo sendo avaliado
            label_names: Nomes das classes (ex: ['negativo', 'neutro', 'positivo'])
            output_dir: Diretório para salvar resultados
        """
        self.model_name = model_name
        self.label_names = label_names or ['negativo', 'neutro', 'positivo']
        self.output_dir = output_dir or Path("logs/evaluation")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        texts: Optional[List[str]] = None,
        probabilities: Optional[np.ndarray] = None
    ) -> EvaluationResult:
        """
        Executa avaliação completa
        
        Args:
            y_true: Labels verdadeiros
            y_pred: Predições do modelo
            texts: Textos originais (opcional, para análise de erros)
            probabilities: Probabilidades das predições (opcional)
            
        Returns:
            EvaluationResult com todas as métricas
        """
        print(f"🔍 Avaliando {self.model_name}...")
        start_time = time.time()
        
        # Calcular métricas principais
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        
        # Métricas macro e weighted
        macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='macro', zero_division=0
        )
        
        # Métricas por classe
        per_class_p, per_class_r, per_class_f1, per_class_support = \
            precision_recall_fscore_support(
                y_true, y_pred, average=None, zero_division=0
            )
        
        per_class_metrics = {}
        for i, label in enumerate(self.label_names):
            per_class_metrics[label] = {
                'precision': float(per_class_p[i]),
                'recall': float(per_class_r[i]),
                'f1': float(per_class_f1[i]),
                'support': int(per_class_support[i])
            }
        
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Análise de erros
        error_analysis = self._analyze_errors(
            y_true, y_pred, texts, probabilities
        )
        
        # Criar resultado
        result = EvaluationResult(
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1_score=float(f1),
            per_class_metrics=per_class_metrics,
            confusion_matrix=cm.tolist(),
            error_analysis=error_analysis,
            timestamp=datetime.now().isoformat(),
            num_samples=len(y_true),
            model_name=self.model_name,
            macro_avg={
                'precision': float(macro_p),
                'recall': float(macro_r),
                'f1': float(macro_f1)
            },
            weighted_avg={
                'precision': float(precision),
                'recall': float(recall),
                'f1': float(f1)
            }
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Avaliação concluída em {elapsed:.2f}s")
        
        return result
    
    def _analyze_errors(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        texts: Optional[List[str]],
        probabilities: Optional[np.ndarray]
    ) -> Dict[str, Any]:
        """
        Analisa erros do modelo
        
        Returns:
            Dict com análise de erros
        """
        errors = y_true != y_pred
        num_errors = errors.sum()
        error_rate = num_errors / len(y_true)
        
        analysis = {
            'total_errors': int(num_errors),
            'error_rate': float(error_rate),
            'error_distribution': {}
        }
        
        # Distribuição de erros por tipo
        for true_label in range(len(self.label_names)):
            for pred_label in range(len(self.label_names)):
                if true_label != pred_label:
                    mask = (y_true == true_label) & (y_pred == pred_label)
                    count = mask.sum()
                    if count > 0:
                        key = f"{self.label_names[true_label]}_as_{self.label_names[pred_label]}"
                        analysis['error_distribution'][key] = int(count)
        
        # Exemplos de erros (se textos fornecidos)
        if texts is not None and num_errors > 0:
            error_indices = np.where(errors)[0]
            sample_size = min(10, len(error_indices))
            sample_indices = np.random.choice(
                error_indices, sample_size, replace=False
            )
            
            error_examples = []
            for idx in sample_indices:
                example = {
                    'text': texts[idx][:200],  # Primeiros 200 chars
                    'true_label': self.label_names[y_true[idx]],
                    'pred_label': self.label_names[y_pred[idx]]
                }
                
                if probabilities is not None:
                    example['confidence'] = float(probabilities[idx].max())
                
                error_examples.append(example)
            
            analysis['error_examples'] = error_examples
        
        return analysis
    
    def plot_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        save_path: Optional[Path] = None
    ) -> None:
        """
        Plota confusion matrix
        
        Args:
            y_true: Labels verdadeiros
            y_pred: Predições
            save_path: Caminho para salvar imagem
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.label_names,
            yticklabels=self.label_names,
            cbar_kws={'label': 'Count'}
        )
        plt.title(f'Confusion Matrix - {self.model_name}', fontsize=16, pad=20)
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Confusion matrix salva em: {save_path}")
        else:
            plt.savefig(
                self.output_dir / f"confusion_matrix_{self.model_name.replace(' ', '_')}.png",
                dpi=300,
                bbox_inches='tight'
            )
        
        plt.close()
    
    def plot_metrics_comparison(
        self,
        results: List[EvaluationResult],
        save_path: Optional[Path] = None
    ) -> None:
        """
        Plota comparação de métricas entre modelos
        
        Args:
            results: Lista de resultados de avaliação
            save_path: Caminho para salvar imagem
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        titles = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
        
        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[idx // 2, idx % 2]
            
            values = [getattr(r, metric) for r in results]
            models = [r.model_name for r in results]
            
            bars = ax.bar(models, values, color=['#1f77b4', '#ff7f0e', '#2ca02c'][:len(models)])
            ax.set_ylabel(title, fontsize=12)
            ax.set_ylim(0, 1.0)
            ax.grid(axis='y', alpha=0.3)
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height,
                    f'{height:.3f}',
                    ha='center',
                    va='bottom',
                    fontsize=10
                )
        
        plt.suptitle('Model Performance Comparison', fontsize=16, y=1.00)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Comparação salva em: {save_path}")
        else:
            plt.savefig(
                self.output_dir / "metrics_comparison.png",
                dpi=300,
                bbox_inches='tight'
            )
        
        plt.close()
    
    def generate_report(
        self,
        result: EvaluationResult,
        save_path: Optional[Path] = None
    ) -> str:
        """
        Gera relatório detalhado em formato texto
        
        Args:
            result: Resultado da avaliação
            save_path: Caminho para salvar relatório
            
        Returns:
            String com relatório formatado
        """
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    EVALUATION REPORT - {result.model_name}                    
╚══════════════════════════════════════════════════════════════════════╝

📅 Timestamp: {result.timestamp}
📊 Samples: {result.num_samples}

┌─────────────────────────────────────────────────────────────────┐
│  OVERALL METRICS                                                │
└─────────────────────────────────────────────────────────────────┘

   • Accuracy:  {result.accuracy:.4f} ({result.accuracy*100:.2f}%)
   • Precision: {result.precision:.4f}
   • Recall:    {result.recall:.4f}
   • F1-Score:  {result.f1_score:.4f}

┌─────────────────────────────────────────────────────────────────┐
│  MACRO AVERAGES                                                 │
└─────────────────────────────────────────────────────────────────┘

   • Precision: {result.macro_avg['precision']:.4f}
   • Recall:    {result.macro_avg['recall']:.4f}
   • F1-Score:  {result.macro_avg['f1']:.4f}

┌─────────────────────────────────────────────────────────────────┐
│  PER-CLASS METRICS                                              │
└─────────────────────────────────────────────────────────────────┘

"""
        
        for label, metrics in result.per_class_metrics.items():
            report += f"""   📌 {label.upper()}:
      Precision: {metrics['precision']:.4f}
      Recall:    {metrics['recall']:.4f}
      F1-Score:  {metrics['f1']:.4f}
      Support:   {metrics['support']} samples
      
"""
        
        report += f"""┌─────────────────────────────────────────────────────────────────┐
│  ERROR ANALYSIS                                                 │
└─────────────────────────────────────────────────────────────────┘

   • Total Errors: {result.error_analysis['total_errors']}
   • Error Rate:   {result.error_analysis['error_rate']:.4f} ({result.error_analysis['error_rate']*100:.2f}%)

   Error Distribution:
"""
        
        for error_type, count in result.error_analysis['error_distribution'].items():
            report += f"      • {error_type}: {count}\n"
        
        if 'error_examples' in result.error_analysis:
            report += "\n   Example Errors:\n"
            for i, example in enumerate(result.error_analysis['error_examples'][:5], 1):
                report += f"""
      {i}. Text: "{example['text']}..."
         True: {example['true_label']} | Predicted: {example['pred_label']}
"""
                if 'confidence' in example:
                    report += f"         Confidence: {example['confidence']:.4f}\n"
        
        report += """
╔══════════════════════════════════════════════════════════════════════╗
║                         END OF REPORT                                ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"💾 Relatório salvo em: {save_path}")
        
        return report


def main():
    """Exemplo de uso"""
    print("🎯 SentiBR Evaluation Suite - Example")
    
    # Criar dados de exemplo
    np.random.seed(42)
    n_samples = 1000
    
    y_true = np.random.randint(0, 3, n_samples)
    y_pred = y_true.copy()
    
    # Introduzir alguns erros
    error_indices = np.random.choice(n_samples, size=100, replace=False)
    y_pred[error_indices] = np.random.randint(0, 3, len(error_indices))
    
    # Criar textos de exemplo
    texts = [f"Review de exemplo número {i}" for i in range(n_samples)]
    
    # Criar probabilidades de exemplo
    probabilities = np.random.dirichlet(np.ones(3), n_samples)
    
    # Executar avaliação
    evaluator = ModelEvaluator(
        model_name="BERT Fine-tuned",
        label_names=['negativo', 'neutro', 'positivo']
    )
    
    result = evaluator.evaluate(y_true, y_pred, texts, probabilities)
    
    # Mostrar resumo
    print(result.summary())
    
    # Gerar visualizações
    evaluator.plot_confusion_matrix(y_true, y_pred)
    
    # Salvar resultado
    result.to_json(Path("logs/evaluation/example_result.json"))
    
    # Gerar relatório
    report = evaluator.generate_report(result)
    print(report)


if __name__ == "__main__":
    main()
