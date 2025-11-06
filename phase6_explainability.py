"""
SentiBR - Explainability Module
LIME para interpretabilidade das predições do BERT
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from lime.lime_text import LimeTextExplainer
import matplotlib.pyplot as plt
import seaborn as sns


class SentimentExplainer:
    """Explica predições do modelo BERT usando LIME"""
    
    def __init__(self, model_path: str, device: str = None):
        """
        Inicializa explainer
        
        Args:
            model_path: Caminho para modelo BERT
            device: Device (cuda/cpu)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"📦 Carregando modelo de {model_path}...")
        self.tokenizer = BertTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
        
        # LIME explainer
        self.explainer = LimeTextExplainer(
            class_names=['negativo', 'neutro', 'positivo'],
            split_expression=r'\W+',  # Split em tokens
            random_state=42
        )
        
        print(f"✅ Explainer inicializado no device: {self.device}")
    
    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """
        Predição batch para LIME
        
        Args:
            texts: Lista de textos
            
        Returns:
            Array [n_samples, 3] com probabilidades
        """
        probabilities = []
        
        with torch.no_grad():
            for text in texts:
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
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
                probabilities.append(probs)
        
        return np.array(probabilities)
    
    def explain_prediction(self, text: str, num_features: int = 10,
                          num_samples: int = 1000) -> Dict:
        """
        Explica uma predição usando LIME
        
        Args:
            text: Texto a explicar
            num_features: Número de features a mostrar
            num_samples: Número de samples para LIME
            
        Returns:
            Dict com explicação
        """
        print(f"\n🔍 Explicando predição para: '{text[:100]}...'")
        
        # Predição original
        probs = self.predict_proba([text])[0]
        prediction = probs.argmax()
        confidence = probs[prediction]
        
        label_map = {0: 'negativo', 1: 'neutro', 2: 'positivo'}
        
        print(f"📊 Predição: {label_map[prediction]} ({confidence:.2%} confiança)")
        print(f"🔬 Gerando explicação LIME com {num_samples} samples...")
        
        # Gera explicação
        explanation = self.explainer.explain_instance(
            text,
            self.predict_proba,
            num_features=num_features,
            num_samples=num_samples,
            top_labels=3
        )
        
        # Extrai features importantes
        feature_importance = {}
        
        for label_id in range(3):
            label = label_map[label_id]
            features = explanation.as_list(label=label_id)
            
            feature_importance[label] = [
                {
                    'feature': feat,
                    'weight': float(weight),
                    'direction': 'positive' if weight > 0 else 'negative'
                }
                for feat, weight in features
            ]
        
        result = {
            'text': text,
            'prediction': label_map[prediction],
            'confidence': float(confidence),
            'probabilities': {
                'negativo': float(probs[0]),
                'neutro': float(probs[1]),
                'positivo': float(probs[2])
            },
            'feature_importance': feature_importance,
            'top_features_predicted_class': feature_importance[label_map[prediction]]
        }
        
        print(f"✅ Explicação gerada!")
        
        return result
    
    def explain_batch(self, texts: List[str], predictions: List[str] = None,
                     num_features: int = 10) -> List[Dict]:
        """
        Explica múltiplas predições
        
        Args:
            texts: Lista de textos
            predictions: Predições (opcional, senão prediz)
            num_features: Features por explicação
            
        Returns:
            Lista de explicações
        """
        print(f"\n🔬 Explicando {len(texts)} predições...")
        
        explanations = []
        for i, text in enumerate(texts, 1):
            print(f"\n[{i}/{len(texts)}]", end=" ")
            explanation = self.explain_prediction(text, num_features=num_features)
            explanations.append(explanation)
        
        print(f"\n✅ {len(explanations)} explicações geradas!")
        
        return explanations
    
    def visualize_explanation(self, explanation: Dict, save_path: str = None):
        """
        Visualiza explicação como gráfico
        
        Args:
            explanation: Dict com explicação
            save_path: Caminho para salvar plot (opcional)
        """
        predicted_class = explanation['prediction']
        features = explanation['top_features_predicted_class']
        
        # Prepara dados
        feature_names = [f['feature'] for f in features]
        weights = [f['weight'] for f in features]
        colors = ['#4CAF50' if w > 0 else '#F44336' for w in weights]
        
        # Cria plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        y_pos = np.arange(len(feature_names))
        ax.barh(y_pos, weights, color=colors)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(feature_names)
        ax.set_xlabel('Weight (Contribution to prediction)')
        ax.set_title(f'Feature Importance - Predicted: {predicted_class} '
                    f'({explanation["confidence"]:.1%} confidence)')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # Adiciona grid
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Plot salvo em: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def get_global_feature_importance(self, explanations: List[Dict]) -> Dict:
        """
        Agrega importância de features através de múltiplas explicações
        
        Args:
            explanations: Lista de explicações
            
        Returns:
            Dict com importância global
        """
        print("\n📊 Calculando importância global de features...")
        
        # Agrega features por classe
        global_importance = {
            'negativo': {},
            'neutro': {},
            'positivo': {}
        }
        
        for expl in explanations:
            predicted_class = expl['prediction']
            
            for feat_info in expl['top_features_predicted_class']:
                feature = feat_info['feature']
                weight = feat_info['weight']
                
                if feature not in global_importance[predicted_class]:
                    global_importance[predicted_class][feature] = []
                
                global_importance[predicted_class][feature].append(weight)
        
        # Calcula estatísticas
        global_stats = {}
        
        for sentiment, features in global_importance.items():
            feature_stats = []
            
            for feature, weights in features.items():
                feature_stats.append({
                    'feature': feature,
                    'mean_weight': float(np.mean(weights)),
                    'std_weight': float(np.std(weights)),
                    'frequency': len(weights),
                    'total_weight': float(np.sum(weights))
                })
            
            # Ordena por peso absoluto médio
            feature_stats.sort(key=lambda x: abs(x['mean_weight']), reverse=True)
            
            global_stats[sentiment] = feature_stats[:20]  # Top 20
        
        return global_stats
    
    def plot_global_importance(self, global_stats: Dict, 
                              save_path: str = None):
        """
        Plota importância global de features
        
        Args:
            global_stats: Estatísticas globais
            save_path: Caminho para salvar
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for idx, (sentiment, features) in enumerate(global_stats.items()):
            ax = axes[idx]
            
            if len(features) == 0:
                continue
            
            # Top 15 features
            top_features = features[:15]
            feature_names = [f['feature'] for f in top_features]
            mean_weights = [f['mean_weight'] for f in top_features]
            colors = ['#4CAF50' if w > 0 else '#F44336' for w in mean_weights]
            
            y_pos = np.arange(len(feature_names))
            ax.barh(y_pos, mean_weights, color=colors)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(feature_names, fontsize=9)
            ax.set_xlabel('Mean Weight')
            ax.set_title(f'Top Features - {sentiment.upper()}')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Global importance plot salvo em: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_explanation_report(self, explanation: Dict) -> str:
        """
        Cria relatório textual da explicação
        
        Args:
            explanation: Explicação
            
        Returns:
            String com relatório formatado
        """
        report = []
        report.append("="*60)
        report.append("🔍 EXPLICAÇÃO DA PREDIÇÃO")
        report.append("="*60)
        
        report.append(f"\n📝 TEXTO:")
        report.append(f"  {explanation['text'][:200]}...")
        
        report.append(f"\n🎯 PREDIÇÃO:")
        report.append(f"  Sentimento: {explanation['prediction'].upper()}")
        report.append(f"  Confiança: {explanation['confidence']:.2%}")
        
        report.append(f"\n📊 PROBABILIDADES:")
        for sentiment, prob in explanation['probabilities'].items():
            bar = "█" * int(prob * 20)
            report.append(f"  {sentiment:8s}: {bar:20s} {prob:.2%}")
        
        report.append(f"\n⚖️  TOP FEATURES INFLUENCIANDO A PREDIÇÃO:")
        for feat in explanation['top_features_predicted_class'][:10]:
            direction = "➕" if feat['weight'] > 0 else "➖"
            report.append(f"  {direction} {feat['feature']:20s} | {feat['weight']:+.3f}")
        
        report.append("\n" + "="*60)
        
        return "\n".join(report)
    
    def save_explanations(self, explanations: List[Dict], 
                         output_path: str = 'evaluation_results/explanations.json'):
        """
        Salva explicações em JSON
        
        Args:
            explanations: Lista de explicações
            output_path: Caminho de saída
        """
        import json
        from datetime import datetime
        
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'n_explanations': len(explanations),
            'explanations': explanations
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Explicações salvas em: {output_file}")


def run_explainability_analysis(model_path: str, test_data_path: str,
                                n_samples: int = 20):
    """
    Executa análise de explainability
    
    Args:
        model_path: Caminho para modelo
        test_data_path: Caminho para test data
        n_samples: Número de samples a explicar
    """
    print("\n🚀 INICIANDO ANÁLISE DE EXPLAINABILITY\n")
    
    # Carrega test data
    print(f"📂 Carregando test data de {test_data_path}...")
    test_df = pd.read_csv(test_data_path)
    
    # Sample diversificado
    sample_df = test_df.groupby('label').sample(
        n=n_samples // 3, 
        random_state=42
    )
    
    print(f"✅ {len(sample_df)} exemplos selecionados")
    
    # Inicializa explainer
    explainer = SentimentExplainer(model_path)
    
    # Gera explicações
    explanations = explainer.explain_batch(sample_df['text'].tolist())
    
    # Análise global
    global_stats = explainer.get_global_feature_importance(explanations)
    
    # Visualizações
    output_dir = Path('evaluation_results/explainability')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Plot global
    explainer.plot_global_importance(
        global_stats,
        save_path=output_dir / 'global_feature_importance.png'
    )
    
    # Plots individuais (primeiros 5)
    for i, explanation in enumerate(explanations[:5], 1):
        explainer.visualize_explanation(
            explanation,
            save_path=output_dir / f'explanation_{i}.png'
        )
        
        # Imprime relatório
        report = explainer.create_explanation_report(explanation)
        print(f"\n{report}")
    
    # Salva todas explicações
    explainer.save_explanations(explanations, output_dir / 'all_explanations.json')
    
    print(f"\n✅ Análise de explainability concluída!")
    print(f"📁 Resultados em: {output_dir}")
    
    return explanations, global_stats


if __name__ == '__main__':
    # Configuração
    MODEL_PATH = 'models/bert_finetuned'
    TEST_DATA_PATH = 'data/processed/test.csv'
    N_SAMPLES = 20
    
    explanations, global_stats = run_explainability_analysis(
        MODEL_PATH,
        TEST_DATA_PATH,
        n_samples=N_SAMPLES
    )
