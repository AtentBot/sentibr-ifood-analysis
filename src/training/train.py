"""
Script principal para fine-tuning do BERT em análise de sentimento
"""

import torch
import torch.nn as nn
from torch.optim import AdamW
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import get_linear_schedule_with_warmup
import mlflow
import mlflow.pytorch
from pathlib import Path
import logging
from tqdm import tqdm
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import json
from typing import Dict, Tuple
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import config
from src.training.dataset import load_data_for_training, create_data_loaders

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BERTTrainer:
    """
    Classe para treinar o modelo BERT
    """
    
    def __init__(
        self,
        model_name: str = None,
        num_labels: int = 3,
        learning_rate: float = 2e-5,
        num_epochs: int = 3,
        batch_size: int = 16,
        max_length: int = 512,
        warmup_steps: int = 0,
        weight_decay: float = 0.01,
        device: str = None
    ):
        """
        Inicializa o trainer
        """
        # Usar configuração global se não especificado
        self.model_name = model_name or config.model.model_name
        self.num_labels = num_labels
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.max_length = max_length
        self.warmup_steps = warmup_steps
        self.weight_decay = weight_decay
        
        # Device (GPU ou CPU)
        if device:
            self.device = torch.device(device)
        else:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"🖥️  Usando device: {self.device}")
        
        # Modelo e tokenizer (serão inicializados depois)
        self.model = None
        self.tokenizer = None
        self.optimizer = None
        self.scheduler = None
        
        # Métricas
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        self.patience_counter = 0
        
    def initialize_model(self):
        """
        Inicializa o modelo BERT e tokenizer
        """
        logger.info(f"🤖 Inicializando modelo: {self.model_name}")
        
        # Tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        
        # Modelo
        self.model = BertForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=self.num_labels
        )
        
        self.model.to(self.device)
        
        logger.info(f"  ✅ Modelo carregado: {sum(p.numel() for p in self.model.parameters()):,} parâmetros")
        
    def initialize_optimizer(self, num_training_steps: int):
        """
        Inicializa otimizador e scheduler
        """
        # Otimizador AdamW
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )
        
        # Learning rate scheduler com warmup
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=self.warmup_steps,
            num_training_steps=num_training_steps
        )
        
        logger.info(f"  ✅ Otimizador configurado (lr={self.learning_rate})")
        
    def train_epoch(
        self,
        train_loader: torch.utils.data.DataLoader,
        epoch: int
    ) -> Tuple[float, float]:
        """
        Treina por uma época
        
        Returns:
            Tuple com (loss médio, accuracy)
        """
        self.model.train()
        
        total_loss = 0
        predictions = []
        true_labels = []
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{self.num_epochs}")
        
        for batch in progress_bar:
            # Mover para device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['label'].to(self.device)
            
            # Forward pass
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            logits = outputs.logits
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            self.scheduler.step()
            
            # Métricas
            total_loss += loss.item()
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            predictions.extend(preds)
            true_labels.extend(labels.cpu().numpy())
            
            # Atualizar progress bar
            progress_bar.set_postfix({'loss': loss.item()})
        
        # Calcular métricas da época
        avg_loss = total_loss / len(train_loader)
        accuracy = accuracy_score(true_labels, predictions)
        
        return avg_loss, accuracy
    
    def evaluate(
        self,
        data_loader: torch.utils.data.DataLoader
    ) -> Dict[str, float]:
        """
        Avalia o modelo
        
        Returns:
            Dict com métricas (loss, accuracy, precision, recall, f1)
        """
        self.model.eval()
        
        total_loss = 0
        predictions = []
        true_labels = []
        
        with torch.no_grad():
            for batch in tqdm(data_loader, desc="Evaluating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                logits = outputs.logits
                
                total_loss += loss.item()
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                predictions.extend(preds)
                true_labels.extend(labels.cpu().numpy())
        
        # Calcular métricas
        avg_loss = total_loss / len(data_loader)
        accuracy = accuracy_score(true_labels, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='weighted', zero_division=0
        )
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'predictions': predictions,
            'true_labels': true_labels
        }
    
    def save_model(self, save_path: Path, metrics: Dict = None):
        """
        Salva o modelo e tokenizer
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Salvar modelo e tokenizer
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        # Salvar métricas (converter numpy types para Python natives)
        if metrics:
            # Função helper para converter numpy types
            def convert_to_native(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_to_native(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_native(item) for item in obj]
                return obj
            
            metrics_clean = convert_to_native(metrics)
            
            # Remover predictions e true_labels (muito grandes para JSON)
            if 'predictions' in metrics_clean:
                del metrics_clean['predictions']
            if 'true_labels' in metrics_clean:
                del metrics_clean['true_labels']
            if 'probabilities' in metrics_clean:
                del metrics_clean['probabilities']
            
            with open(save_path / 'metrics.json', 'w') as f:
                json.dump(metrics_clean, f, indent=2)
        
        # Salvar config
        config_dict = {
            'model_name': self.model_name,
            'num_labels': self.num_labels,
            'max_length': self.max_length,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'num_epochs': self.num_epochs
        }
        
        with open(save_path / 'training_config.json', 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"💾 Modelo salvo em: {save_path}")
    
    def train(
        self,
        train_loader: torch.utils.data.DataLoader,
        val_loader: torch.utils.data.DataLoader,
        patience: int = 3,
        save_path: Path = None
    ):
        """
        Loop principal de treinamento com early stopping
        """
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO TREINAMENTO")
        logger.info("=" * 60)
        
        # Configurar MLflow
        mlflow.set_tracking_uri(config.mlflow.tracking_uri)
        mlflow.set_experiment(config.mlflow.experiment_name)
        
        with mlflow.start_run():
            # Log de hyperparameters
            mlflow.log_params({
                'model_name': self.model_name,
                'learning_rate': self.learning_rate,
                'batch_size': self.batch_size,
                'num_epochs': self.num_epochs,
                'max_length': self.max_length,
                'warmup_steps': self.warmup_steps,
                'weight_decay': self.weight_decay
            })
            
            # Inicializar otimizador
            num_training_steps = len(train_loader) * self.num_epochs
            self.initialize_optimizer(num_training_steps)
            
            # Loop de treinamento
            for epoch in range(self.num_epochs):
                logger.info(f"\n📊 Época {epoch + 1}/{self.num_epochs}")
                
                # Treinar
                train_loss, train_acc = self.train_epoch(train_loader, epoch)
                
                logger.info(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
                
                # Validar
                val_metrics = self.evaluate(val_loader)
                val_loss = val_metrics['loss']
                val_acc = val_metrics['accuracy']
                
                logger.info(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
                logger.info(f"  Val F1: {val_metrics['f1']:.4f}")
                
                # Log no MLflow
                mlflow.log_metrics({
                    'train_loss': train_loss,
                    'train_acc': train_acc,
                    'val_loss': val_loss,
                    'val_acc': val_acc,
                    'val_f1': val_metrics['f1']
                }, step=epoch)
                
                # Early stopping
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.best_val_acc = val_acc
                    self.patience_counter = 0
                    
                    # Salvar melhor modelo
                    if save_path:
                        self.save_model(save_path, val_metrics)
                    
                    logger.info("  ✅ Melhor modelo até agora!")
                else:
                    self.patience_counter += 1
                    logger.info(f"  ⚠️  Patience: {self.patience_counter}/{patience}")
                    
                    if self.patience_counter >= patience:
                        logger.info("  🛑 Early stopping!")
                        break
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ TREINAMENTO CONCLUÍDO")
            logger.info("=" * 60)
            logger.info(f"Melhor Val Loss: {self.best_val_loss:.4f}")
            logger.info(f"Melhor Val Acc: {self.best_val_acc:.4f}")


def main():
    """
    Função principal
    """
    logger.info("=" * 60)
    logger.info("SENTIBR - BERT Fine-tuning Pipeline")
    logger.info("=" * 60)
    
    # Verificar se os dados existem
    if not config.training.train_data_path.exists():
        logger.error(f"❌ Arquivo de treino não encontrado: {config.training.train_data_path}")
        logger.info("\n💡 Execute primeiro:")
        logger.info("   1. python src/data/load_data.py (ou load_data_v2.py)")
        logger.info("   2. python src/data/split_dataset.py")
        return
    
    # Carregar dados
    data = load_data_for_training(
        train_path=str(config.training.train_data_path),
        val_path=str(config.training.val_data_path),
        test_path=str(config.training.test_data_path)
    )
    
    # Inicializar trainer
    trainer = BERTTrainer(
        model_name=config.model.model_name,
        num_labels=config.model.num_labels,
        learning_rate=config.training.learning_rate,
        num_epochs=config.training.num_epochs,
        batch_size=config.training.batch_size,
        max_length=config.model.max_length,
        warmup_steps=config.training.warmup_steps,
        weight_decay=config.training.weight_decay
    )
    
    # Inicializar modelo
    trainer.initialize_model()
    
    # Criar data loaders
    loaders = create_data_loaders(
        train_df=data['train'],
        val_df=data['val'],
        test_df=data['test'],
        tokenizer=trainer.tokenizer,
        max_length=trainer.max_length,
        batch_size=trainer.batch_size
    )
    
    # Treinar
    trainer.train(
        train_loader=loaders['train'],
        val_loader=loaders['val'],
        patience=3,
        save_path=config.model.model_save_path
    )
    
    # Avaliar no test set
    logger.info("\n" + "=" * 60)
    logger.info("📊 AVALIAÇÃO NO TEST SET")
    logger.info("=" * 60)
    
    test_metrics = trainer.evaluate(loaders['test'])
    
    logger.info(f"Test Loss: {test_metrics['loss']:.4f}")
    logger.info(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
    logger.info(f"Test Precision: {test_metrics['precision']:.4f}")
    logger.info(f"Test Recall: {test_metrics['recall']:.4f}")
    logger.info(f"Test F1: {test_metrics['f1']:.4f}")
    
    # Classification report
    logger.info("\n📋 Classification Report:")
    report = classification_report(
        test_metrics['true_labels'],
        test_metrics['predictions'],
        target_names=['negativo', 'neutro', 'positivo']
    )
    logger.info(f"\n{report}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 60)
    logger.info(f"\n📁 Modelo salvo em: {config.model.model_save_path}")
    logger.info("\n💡 Próximo passo:")
    logger.info("   python src/api/main.py")


if __name__ == "__main__":
    main()
