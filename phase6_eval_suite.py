"""
SentiBR - Evaluation Framework
Avaliação robusta do modelo BERT com métricas completas
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import torch
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    classification_report, confusion_matrix, roc_auc_score
)
import matplotlib.pyplot as plt
import seaborn as sns


class ModelEvaluator:
    """Avaliador robusto de modelos de sentimento"""
    
    def __init__(self, model_path: str, device: str = None):
        """
        Inicializa o avaliador
        
        Args:
            model_path: Caminho para o modelo treinado
            device: Device para inferência (cuda/cpu)
        """
        self.model_path = Path(model_path)
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Carrega modelo e tokenizer
        print(f"📦 Carregando modelo de {model_path}...")
        self.tokenizer = BertTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # Labels
        self.label_map = {0: 'negativo', 1: 'neutro', 2: 'positivo'}
        
        print(f"✅ Modelo carregado no device: {self.device}")
    
    def predict_batch(self, texts: List[str], batch_size: int = 16) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prediz sentimento para um batch de textos
        
        Args:
            texts: Lista de textos
            batch_size: Tamanho do batch
            
        Returns:
            predictions: Array com predições (0, 1, 2)
            probabilities: Array com probabilidades [n_samples, 3]
        """
        all_predictions = []
        all_probabilities = []
        
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Tokeniza
                encodings = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=128,
                    return_tensors='pt'
                )
                
                # Move para device
                input_ids = encodings['input_ids'].to(self.device)
                attention_mask = encodings['attention_mask'].to(self.device)
                
                # Predição
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                
                # Softmax para probabilidades
                probs = torch.softmax(logits, dim=-1).cpu().numpy()
                preds = logits.argmax(dim=-1).cpu().numpy()
                
                all_predictions.extend(preds)
                all_probabilities.extend(probs)
        
        return np.array(all_predictions), np.array(all_probabilities)
    
    def evaluate_test_set(self, test_data: pd.DataFrame) -> Dict:
        """
        Avalia modelo no test set completo
        
        Args:
            test_data: DataFrame com colunas 'text' e 'label'
            
        Returns:
            Dict com todas as métricas
        """
        print("\n📊 Iniciando avaliação no test set...")
        
        texts = test_data['text'].tolist()
        y_true = test_data['label'].values
        
        # Predições
        print(f"🔮 Gerando predições para {len(texts)} exemplos...")
        y_pred, y_proba = self.predict_batch(texts)
        
        # Métricas globais
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average='weighted'
        )
        
        # Métricas por classe
        precision_per_class, recall_per_class, f1_per_class, support = \
            precision_recall_fscore_support(y_true, y_pred, average=None)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # ROC AUC (one-vs-rest)
        try:
            auc_scores = {}
            for i in range(3):
                y_true_binary = (y_true == i).astype(int)
                auc_scores[self.label_map[i]] = roc_auc_score(
                    y_true_binary, y_proba[:, i]
                )
            auc_macro = np.mean(list(auc_scores.values()))
        except:
            auc_scores = {'negativo': 0.0, 'neutro': 0.0, 'positivo': 0.0}
            auc_macro = 0.0
        
        # Monta resultado
        results = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'n_samples': len(texts),
            'metrics': {
                'accuracy': float(accuracy),
                'precision_weighted': float(precision),
                'recall_weighted': float(recall),
                'f1_weighted': float(f1),
                'auc_macro': float(auc_macro)
            },
            'per_class_metrics': {
                self.label_map[i]: {
                    'precision': float(precision_per_class[i]),
                    'recall': float(recall_per_class[i]),
                    'f1': float(f1_per_class[i]),
                    'support': int(support[i]),
                    'auc': float(auc_scores[self.label_map[i]])
                }
                for i in range(3)
            },
            'confusion_matrix': cm.tolist(),
            'classification_report': classification_report(
                y_true, y_pred, 
                target_names=['negativo', 'neutro', 'positivo'],
                output_dict=True
            )
        }
        
        # Adiciona predições ao DataFrame
        test_data['prediction'] = y_pred
        test_data['pred_label'] = [self.label_map[p] for p in y_pred]
        test_data['true_label'] = [self.label_map[t] for t in y_true]
        test_data['confidence'] = y_proba.max(axis=1)
        test_data['correct'] = (y_pred == y_true)
        
        # Adiciona probabilidades
        for i, label in self.label_map.items():
            test_data[f'prob_{label}'] = y_proba[:, i]
        
        results['predictions_df'] = test_data
        
        return results
    
    def analyze_by_aspect(self, test_data: pd.DataFrame, results: Dict) -> Dict:
        """
        Analisa performance por aspecto (comida, entrega, serviço, preço)
        
        Args:
            test_data: DataFrame com predições
            results: Dict com resultados da avaliação
            
        Returns:
            Dict com análise por aspecto
        """
        print("\n🔍 Analisando performance por aspecto...")
        
        aspect_keywords = {
            'comida': ['comida', 'prato', 'sabor', 'tempero', 'delicioso', 'gostoso', 
                      'horrível', 'ruim', 'péssimo', 'excelente', 'maravilhoso'],
            'entrega': ['entrega', 'entregar', 'atrasado', 'rápido', 'demorou', 
                       'tempo', 'chegou', 'pontual', 'atraso'],
            'servico': ['atendimento', 'serviço', 'garçom', 'educado', 'grosseiro', 
                       'atenção', 'cordial', 'simpático'],
            'preco': ['preço', 'caro', 'barato', 'valor', 'custo', 'cobrar', 
                     'cobrou', 'vale', 'pena']
        }
        
        aspect_analysis = {}
        
        for aspect, keywords in aspect_keywords.items():
            # Filtra reviews que mencionam o aspecto
            mask = test_data['text'].str.lower().str.contains(
                '|'.join(keywords), na=False
            )
            aspect_df = test_data[mask]
            
            if len(aspect_df) > 0:
                y_true = aspect_df['label'].values
                y_pred = aspect_df['prediction'].values
                
                accuracy = accuracy_score(y_true, y_pred)
                precision, recall, f1, _ = precision_recall_fscore_support(
                    y_true, y_pred, average='weighted'
                )
                
                aspect_analysis[aspect] = {
                    'n_samples': len(aspect_df),
                    'accuracy': float(accuracy),
                    'precision': float(precision),
                    'recall': float(recall),
                    'f1': float(f1),
                    'distribution': {
                        'negativo': int((y_true == 0).sum()),
                        'neutro': int((y_true == 1).sum()),
                        'positivo': int((y_true == 2).sum())
                    }
                }
            else:
                aspect_analysis[aspect] = {
                    'n_samples': 0,
                    'accuracy': 0.0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'f1': 0.0,
                    'distribution': {'negativo': 0, 'neutro': 0, 'positivo': 0}
                }
        
        results['aspect_analysis'] = aspect_analysis
        return results
    
    def analyze_confidence(self, test_data: pd.DataFrame, results: Dict) -> Dict:
        """
        Analisa relação entre confiança e acurácia
        
        Args:
            test_data: DataFrame com predições
            results: Dict com resultados da avaliação
            
        Returns:
            Dict atualizado com análise de confiança
        """
        print("\n🎯 Analisando confiança do modelo...")
        
        # Agrupa por bins de confiança
        confidence_bins = [0.0, 0.5, 0.7, 0.85, 0.95, 1.0]
        bin_labels = ['0-50%', '50-70%', '70-85%', '85-95%', '95-100%']
        
        test_data['confidence_bin'] = pd.cut(
            test_data['confidence'],
            bins=confidence_bins,
            labels=bin_labels,
            include_lowest=True
        )
        
        confidence_analysis = {}
        for bin_label in bin_labels:
            bin_df = test_data[test_data['confidence_bin'] == bin_label]
            
            if len(bin_df) > 0:
                confidence_analysis[bin_label] = {
                    'n_samples': len(bin_df),
                    'accuracy': float((bin_df['correct']).mean()),
                    'avg_confidence': float(bin_df['confidence'].mean())
                }
            else:
                confidence_analysis[bin_label] = {
                    'n_samples': 0,
                    'accuracy': 0.0,
                    'avg_confidence': 0.0
                }
        
        results['confidence_analysis'] = confidence_analysis
        return results
    
    def get_error_analysis(self, test_data: pd.DataFrame, n_samples: int = 20) -> Dict:
        """
        Analisa os erros mais confiantes do modelo
        
        Args:
            test_data: DataFrame com predições
            n_samples: Número de exemplos a analisar
            
        Returns:
            Dict com análise de erros
        """
        print(f"\n❌ Analisando top {n_samples} erros mais confiantes...")
        
        # Filtra erros
        errors = test_data[~test_data['correct']].copy()
        
        if len(errors) == 0:
            return {'error_analysis': 'No errors found!'}
        
        # Ordena por confiança (erros mais confiantes primeiro)
        errors = errors.sort_values('confidence', ascending=False).head(n_samples)
        
        error_samples = []
        for _, row in errors.iterrows():
            error_samples.append({
                'text': row['text'][:200] + '...' if len(row['text']) > 200 else row['text'],
                'true_label': row['true_label'],
                'predicted_label': row['pred_label'],
                'confidence': float(row['confidence']),
                'prob_negativo': float(row['prob_negativo']),
                'prob_neutro': float(row['prob_neutro']),
                'prob_positivo': float(row['prob_positivo'])
            })
        
        return {
            'total_errors': len(test_data[~test_data['correct']]),
            'error_rate': float((~test_data['correct']).mean()),
            'top_confident_errors': error_samples
        }
    
    def save_results(self, results: Dict, output_dir: str = 'evaluation_results'):
        """
        Salva resultados da avaliação
        
        Args:
            results: Dict com resultados
            output_dir: Diretório de saída
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Salva JSON (sem DataFrame)
        results_json = {k: v for k, v in results.items() if k != 'predictions_df'}
        json_path = output_path / f'evaluation_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results_json, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {json_path}")
        
        # Salva CSV com predições
        if 'predictions_df' in results:
            csv_path = output_path / f'predictions_{timestamp}.csv'
            results['predictions_df'].to_csv(csv_path, index=False)
            print(f"💾 Predições salvas em: {csv_path}")
        
        # Plota confusion matrix
        self.plot_confusion_matrix(
            results['confusion_matrix'],
            output_path / f'confusion_matrix_{timestamp}.png'
        )
        
        return json_path
    
    def plot_confusion_matrix(self, cm: np.ndarray, save_path: Path):
        """Plota e salva confusion matrix"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Negativo', 'Neutro', 'Positivo'],
            yticklabels=['Negativo', 'Neutro', 'Positivo']
        )
        plt.title('Confusion Matrix - BERT Model')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 Confusion matrix salva em: {save_path}")
    
    def print_summary(self, results: Dict):
        """Imprime sumário dos resultados"""
        print("\n" + "="*60)
        print("📊 SUMÁRIO DA AVALIAÇÃO - MODELO BERT")
        print("="*60)
        
        metrics = results['metrics']
        print(f"\n🎯 Métricas Globais:")
        print(f"  • Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  • Precision: {metrics['precision_weighted']:.4f}")
        print(f"  • Recall:    {metrics['recall_weighted']:.4f}")
        print(f"  • F1-Score:  {metrics['f1_weighted']:.4f}")
        print(f"  • AUC Macro: {metrics['auc_macro']:.4f}")
        
        print(f"\n📈 Métricas por Classe:")
        for label, class_metrics in results['per_class_metrics'].items():
            print(f"\n  {label.upper()}:")
            print(f"    • Precision: {class_metrics['precision']:.4f}")
            print(f"    • Recall:    {class_metrics['recall']:.4f}")
            print(f"    • F1-Score:  {class_metrics['f1']:.4f}")
            print(f"    • Support:   {class_metrics['support']}")
        
        if 'aspect_analysis' in results:
            print(f"\n🔍 Performance por Aspecto:")
            for aspect, aspect_metrics in results['aspect_analysis'].items():
                if aspect_metrics['n_samples'] > 0:
                    print(f"\n  {aspect.upper()}:")
                    print(f"    • Samples:   {aspect_metrics['n_samples']}")
                    print(f"    • Accuracy:  {aspect_metrics['accuracy']:.4f}")
                    print(f"    • F1-Score:  {aspect_metrics['f1']:.4f}")
        
        print("\n" + "="*60)


def run_full_evaluation(model_path: str, test_data_path: str):
    """
    Executa avaliação completa do modelo
    
    Args:
        model_path: Caminho para o modelo treinado
        test_data_path: Caminho para o test set
    """
    print("\n🚀 INICIANDO AVALIAÇÃO COMPLETA DO MODELO BERT\n")
    
    # Carrega test data
    print(f"📂 Carregando test data de {test_data_path}...")
    test_df = pd.read_csv(test_data_path)
    print(f"✅ {len(test_df)} exemplos carregados")
    
    # Inicializa evaluator
    evaluator = ModelEvaluator(model_path)
    
    # Avaliação principal
    results = evaluator.evaluate_test_set(test_df)
    
    # Análises adicionais
    results = evaluator.analyze_by_aspect(results['predictions_df'], results)
    results = evaluator.analyze_confidence(results['predictions_df'], results)
    
    # Análise de erros
    error_analysis = evaluator.get_error_analysis(results['predictions_df'])
    results['error_analysis'] = error_analysis
    
    # Imprime sumário
    evaluator.print_summary(results)
    
    # Salva resultados
    json_path = evaluator.save_results(results)
    
    print(f"\n✅ Avaliação completa finalizada!")
    print(f"📁 Resultados disponíveis em: evaluation_results/")
    
    return results


if __name__ == '__main__':
    # Exemplo de uso
    MODEL_PATH = 'models/bert_finetuned'
    TEST_DATA_PATH = 'data/processed/test.csv'
    
    results = run_full_evaluation(MODEL_PATH, TEST_DATA_PATH)
