"""
Script de avaliação detalhada do modelo treinado
"""

import torch
from transformers import BertTokenizer, BertForSequenceClassification
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, classification_report,
    accuracy_score, precision_recall_fscore_support,
    roc_auc_score, roc_curve
)
from pathlib import Path
import logging
import json
import sys

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.config import config
from api.training.dataset import SentimentDataset

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Classe para avaliação detalhada do modelo
    """
    
    def __init__(self, model_path: Path, device: str = None):
        """
        Inicializa o evaluator
        
        Args:
            model_path: Caminho para o modelo salvo
            device: Device a usar (cuda/cpu)
        """
        self.model_path = Path(model_path)
        
        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"🖥️  Usando device: {self.device}")
        
        # Carregar modelo e tokenizer
        self.load_model()
    
    def load_model(self):
        """
        Carrega o modelo e tokenizer
        """
        logger.info(f"📂 Carregando modelo de: {self.model_path}")
        
        self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
        self.model = BertForSequenceClassification.from_pretrained(self.model_path)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info("  ✅ Modelo carregado com sucesso")
    
    def predict(self, texts: list, max_length: int = 512) -> tuple:
        """
        Faz predições em batch
        
        Returns:
            Tuple com (predictions, probabilities)
        """
        dataset = SentimentDataset(
            texts=texts,
            labels=[0] * len(texts),  # Dummy labels
            tokenizer=self.tokenizer,
            max_length=max_length
        )
        
        dataloader = torch.utils.data.DataLoader(
            dataset,
            batch_size=32,
            shuffle=False
        )
        
        all_predictions = []
        all_probabilities = []
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )
                
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)
                preds = torch.argmax(probs, dim=1)
                
                all_predictions.extend(preds.cpu().numpy())
                all_probabilities.extend(probs.cpu().numpy())
        
        return np.array(all_predictions), np.array(all_probabilities)
    
    def evaluate_on_dataset(
        self,
        test_df: pd.DataFrame,
        text_column: str = 'review_text',
        label_column: str = 'label'
    ) -> dict:
        """
        Avalia o modelo em um dataset
        
        Returns:
            Dict com todas as métricas
        """
        logger.info("🔍 Avaliando modelo...")
        
        texts = test_df[text_column].tolist()
        true_labels = test_df[label_column].tolist()
        
        # Fazer predições
        predictions, probabilities = self.predict(texts)
        
        # Calcular métricas
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, support = precision_recall_fscore_support(
            true_labels, predictions, average='weighted', zero_division=0
        )
        
        # Métricas por classe
        precision_per_class, recall_per_class, f1_per_class, support_per_class = \
            precision_recall_fscore_support(
                true_labels, predictions, average=None, zero_division=0
            )
        
        # ROC AUC (se multiclass)
        try:
            roc_auc = roc_auc_score(
                true_labels, probabilities, multi_class='ovr', average='weighted'
            )
        except:
            roc_auc = None
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'roc_auc': roc_auc,
            'per_class': {
                'precision': precision_per_class.tolist(),
                'recall': recall_per_class.tolist(),
                'f1': f1_per_class.tolist(),
                'support': support_per_class.tolist()
            },
            'predictions': predictions.tolist(),
            'true_labels': true_labels,
            'probabilities': probabilities.tolist()
        }
        
        return metrics
    
    def plot_confusion_matrix(
        self,
        true_labels: list,
        predictions: list,
        class_names: list = None,
        save_path: Path = None
    ):
        """
        Plota matriz de confusão
        """
        if class_names is None:
            class_names = ['Negativo', 'Neutro', 'Positivo']
        
        cm = confusion_matrix(true_labels, predictions)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=class_names,
            yticklabels=class_names,
            cbar_kws={'label': 'Número de Amostras'}
        )
        plt.title('Matriz de Confusão', fontsize=16, fontweight='bold')
        plt.ylabel('Verdadeiro', fontsize=12)
        plt.xlabel('Predito', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"  💾 Confusion matrix salva em: {save_path}")
        
        plt.show()
    
    def analyze_errors(
        self,
        test_df: pd.DataFrame,
        predictions: list,
        text_column: str = 'review_text',
        label_column: str = 'label',
        n_examples: int = 10
    ):
        """
        Analisa os erros do modelo
        """
        logger.info("\n🔍 ANÁLISE DE ERROS")
        logger.info("=" * 60)
        
        test_df = test_df.copy()
        test_df['prediction'] = predictions
        test_df['correct'] = test_df[label_column] == test_df['prediction']
        
        # Estatísticas de erros
        errors = test_df[~test_df['correct']]
        accuracy = test_df['correct'].mean()
        
        logger.info(f"Accuracy: {accuracy:.4f}")
        logger.info(f"Total de erros: {len(errors)} / {len(test_df)} ({len(errors)/len(test_df)*100:.1f}%)")
        
        # Tipos de erros
        sentiment_map = {0: 'negativo', 1: 'neutro', 2: 'positivo'}
        
        logger.info("\n📊 Distribuição de Erros por Tipo:")
        error_types = errors.groupby([label_column, 'prediction']).size()
        for (true_label, pred_label), count in error_types.items():
            true_name = sentiment_map[true_label]
            pred_name = sentiment_map[pred_label]
            pct = count / len(errors) * 100
            logger.info(f"  {true_name} → {pred_name}: {count} ({pct:.1f}%)")
        
        # Exemplos de erros
        logger.info(f"\n📝 Exemplos de Erros (até {n_examples}):")
        logger.info("-" * 60)
        
        for idx, (_, row) in enumerate(errors.head(n_examples).iterrows()):
            true_name = sentiment_map[row[label_column]]
            pred_name = sentiment_map[row['prediction']]
            
            logger.info(f"\nErro {idx + 1}:")
            logger.info(f"  Texto: {row[text_column][:150]}...")
            logger.info(f"  Verdadeiro: {true_name}")
            logger.info(f"  Predito: {pred_name}")
        
        return errors
    
    def save_detailed_report(
        self,
        metrics: dict,
        save_path: Path
    ):
        """
        Salva relatório detalhado
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remover listas grandes para JSON
        report = {
            'overall': {
                'accuracy': metrics['accuracy'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1': metrics['f1'],
                'roc_auc': metrics['roc_auc']
            },
            'per_class': metrics['per_class']
        }
        
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"  💾 Relatório salvo em: {save_path}")


def main():
    """
    Função principal
    """
    logger.info("=" * 60)
    logger.info("SENTIBR - Model Evaluation")
    logger.info("=" * 60)
    
    # Verificar se modelo existe
    if not config.model.model_save_path.exists():
        logger.error(f"❌ Modelo não encontrado: {config.model.model_save_path}")
        logger.info("\n💡 Execute primeiro:")
        logger.info("   python src/training/train.py")
        return
    
    # Carregar test data
    test_df = pd.read_csv(config.training.test_data_path)
    logger.info(f"📊 Test set: {len(test_df)} samples")
    
    # Inicializar evaluator
    evaluator = ModelEvaluator(model_path=config.model.model_save_path)
    
    # Avaliar
    metrics = evaluator.evaluate_on_dataset(test_df)
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 MÉTRICAS DE AVALIAÇÃO")
    logger.info("=" * 60)
    logger.info(f"Accuracy:  {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall:    {metrics['recall']:.4f}")
    logger.info(f"F1-Score:  {metrics['f1']:.4f}")
    if metrics['roc_auc']:
        logger.info(f"ROC AUC:   {metrics['roc_auc']:.4f}")
    
    logger.info("\n📊 Métricas por Classe:")
    class_names = ['Negativo', 'Neutro', 'Positivo']
    for i, name in enumerate(class_names):
        logger.info(f"\n  {name}:")
        logger.info(f"    Precision: {metrics['per_class']['precision'][i]:.4f}")
        logger.info(f"    Recall:    {metrics['per_class']['recall'][i]:.4f}")
        logger.info(f"    F1-Score:  {metrics['per_class']['f1'][i]:.4f}")
        logger.info(f"    Support:   {metrics['per_class']['support'][i]}")
    
    # Classification Report
    logger.info("\n📋 Classification Report:")
    report = classification_report(
        metrics['true_labels'],
        metrics['predictions'],
        target_names=class_names
    )
    logger.info(f"\n{report}")
    
    # Confusion Matrix
    logger.info("\n📊 Gerando Confusion Matrix...")
    evaluator.plot_confusion_matrix(
        true_labels=metrics['true_labels'],
        predictions=metrics['predictions'],
        class_names=class_names,
        save_path=config.LOGS_DIR / 'confusion_matrix.png'
    )
    
    # Análise de erros
    errors = evaluator.analyze_errors(
        test_df=test_df,
        predictions=metrics['predictions']
    )
    
    # Salvar relatório
    evaluator.save_detailed_report(
        metrics=metrics,
        save_path=config.LOGS_DIR / 'evaluation_report.json'
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ AVALIAÇÃO CONCLUÍDA COM SUCESSO!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
