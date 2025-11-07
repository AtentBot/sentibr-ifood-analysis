"""
MLflow Integration Module
Integração do MLflow com a API SentiBR
"""
import mlflow
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configuração
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
EXPERIMENT_NAME = "sentibr-sentiment-analysis"

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLflowTracker:
    """Classe para rastreamento de experimentos com MLflow"""
    
    def __init__(self, tracking_uri: str = MLFLOW_TRACKING_URI):
        """
        Inicializa o tracker do MLflow
        
        Args:
            tracking_uri: URI do servidor MLflow
        """
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        self._setup_experiment()
        
    def _setup_experiment(self):
        """Configura ou cria o experimento padrão"""
        try:
            # Tentar obter experimento existente
            experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
            
            if experiment is None:
                # Criar novo experimento
                experiment_id = mlflow.create_experiment(
                    EXPERIMENT_NAME,
                    tags={
                        "project": "SentiBR",
                        "model": "BERT",
                        "task": "sentiment-analysis"
                    }
                )
                logger.info(f"Experimento criado: {EXPERIMENT_NAME} (ID: {experiment_id})")
            else:
                logger.info(f"Experimento existente: {EXPERIMENT_NAME}")
                
            mlflow.set_experiment(EXPERIMENT_NAME)
            
        except Exception as e:
            logger.error(f"Erro ao configurar experimento: {str(e)}")
            raise
    
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """
        Inicia uma nova run
        
        Args:
            run_name: Nome da run (opcional)
            tags: Tags adicionais (opcional)
            
        Returns:
            Objeto ActiveRun do MLflow
        """
        try:
            # Tags padrão
            default_tags = {
                "timestamp": datetime.now().isoformat(),
                "environment": os.getenv("ENVIRONMENT", "development")
            }
            
            if tags:
                default_tags.update(tags)
            
            # Iniciar run
            run = mlflow.start_run(run_name=run_name)
            
            # Adicionar tags
            for key, value in default_tags.items():
                mlflow.set_tag(key, value)
            
            logger.info(f"Run iniciada: {run.info.run_id}")
            return run
            
        except Exception as e:
            logger.error(f"Erro ao iniciar run: {str(e)}")
            raise
    
    def log_params(self, params: Dict[str, Any]):
        """
        Loga parâmetros do modelo
        
        Args:
            params: Dicionário de parâmetros
        """
        try:
            for key, value in params.items():
                mlflow.log_param(key, value)
            logger.info(f"Parâmetros logados: {len(params)}")
        except Exception as e:
            logger.error(f"Erro ao logar parâmetros: {str(e)}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Loga métricas do modelo
        
        Args:
            metrics: Dicionário de métricas
            step: Step atual (para métricas progressivas)
        """
        try:
            for key, value in metrics.items():
                mlflow.log_metric(key, value, step=step)
            logger.info(f"Métricas logadas: {len(metrics)}")
        except Exception as e:
            logger.error(f"Erro ao logar métricas: {str(e)}")
    
    def log_model(self, model, artifact_path: str = "model"):
        """
        Loga o modelo treinado
        
        Args:
            model: Modelo a ser salvo
            artifact_path: Caminho do artifact
        """
        try:
            # Salvar modelo PyTorch
            import torch
            
            mlflow.pytorch.log_model(
                model,
                artifact_path=artifact_path,
                registered_model_name=f"{EXPERIMENT_NAME}-model"
            )
            logger.info(f"Modelo logado: {artifact_path}")
        except Exception as e:
            logger.error(f"Erro ao logar modelo: {str(e)}")
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """
        Loga um artifact (arquivo)
        
        Args:
            local_path: Caminho local do arquivo
            artifact_path: Caminho no artifact store (opcional)
        """
        try:
            mlflow.log_artifact(local_path, artifact_path)
            logger.info(f"Artifact logado: {local_path}")
        except Exception as e:
            logger.error(f"Erro ao logar artifact: {str(e)}")
    
    def log_confusion_matrix(self, y_true, y_pred, labels: list):
        """
        Loga matriz de confusão
        
        Args:
            y_true: Labels verdadeiros
            y_pred: Predições do modelo
            labels: Lista de labels
        """
        try:
            from sklearn.metrics import confusion_matrix
            import matplotlib.pyplot as plt
            import seaborn as sns
            import tempfile
            import os
            
            # Calcular matriz de confusão
            cm = confusion_matrix(y_true, y_pred)
            
            # Plotar
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=labels, yticklabels=labels)
            plt.title('Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            
            # Salvar temporariamente
            with tempfile.TemporaryDirectory() as tmpdir:
                img_path = os.path.join(tmpdir, 'confusion_matrix.png')
                plt.savefig(img_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Logar como artifact
                mlflow.log_artifact(img_path)
            
            logger.info("Matriz de confusão logada")
            
        except Exception as e:
            logger.error(f"Erro ao logar matriz de confusão: {str(e)}")
    
    def log_training_curves(self, train_losses: list, val_losses: list, 
                           train_accs: list, val_accs: list):
        """
        Loga curvas de treinamento
        
        Args:
            train_losses: Lista de losses de treino
            val_losses: Lista de losses de validação
            train_accs: Lista de acurácias de treino
            val_accs: Lista de acurácias de validação
        """
        try:
            import matplotlib.pyplot as plt
            import tempfile
            import os
            
            # Criar figura com 2 subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # Plot Loss
            epochs = range(1, len(train_losses) + 1)
            ax1.plot(epochs, train_losses, 'b-', label='Train Loss')
            ax1.plot(epochs, val_losses, 'r-', label='Val Loss')
            ax1.set_title('Loss over Epochs')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True)
            
            # Plot Accuracy
            ax2.plot(epochs, train_accs, 'b-', label='Train Accuracy')
            ax2.plot(epochs, val_accs, 'r-', label='Val Accuracy')
            ax2.set_title('Accuracy over Epochs')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Accuracy')
            ax2.legend()
            ax2.grid(True)
            
            # Salvar
            with tempfile.TemporaryDirectory() as tmpdir:
                img_path = os.path.join(tmpdir, 'training_curves.png')
                plt.savefig(img_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Logar
                mlflow.log_artifact(img_path)
            
            logger.info("Curvas de treinamento logadas")
            
        except Exception as e:
            logger.error(f"Erro ao logar curvas: {str(e)}")
    
    def end_run(self, status: str = "FINISHED"):
        """
        Finaliza a run atual
        
        Args:
            status: Status final (FINISHED, FAILED, KILLED)
        """
        try:
            mlflow.end_run(status=status)
            logger.info(f"Run finalizada: {status}")
        except Exception as e:
            logger.error(f"Erro ao finalizar run: {str(e)}")

# Exemplo de uso
def example_training_with_mlflow():
    """Exemplo de como usar o MLflowTracker durante treinamento"""
    
    # Inicializar tracker
    tracker = MLflowTracker()
    
    # Iniciar run
    run = tracker.start_run(
        run_name="bert_training_example",
        tags={
            "dataset": "ifood_reviews",
            "version": "1.0.0"
        }
    )
    
    try:
        # Logar parâmetros
        params = {
            "model": "neuralmind/bert-base-portuguese-cased",
            "epochs": 3,
            "batch_size": 32,
            "learning_rate": 2e-5,
            "max_length": 256,
            "optimizer": "AdamW",
            "scheduler": "linear"
        }
        tracker.log_params(params)
        
        # Simular treinamento
        train_losses = [0.8, 0.5, 0.3]
        val_losses = [0.85, 0.55, 0.35]
        train_accs = [0.75, 0.85, 0.92]
        val_accs = [0.73, 0.83, 0.90]
        
        # Logar métricas progressivas
        for epoch in range(3):
            metrics = {
                "train_loss": train_losses[epoch],
                "val_loss": val_losses[epoch],
                "train_accuracy": train_accs[epoch],
                "val_accuracy": val_accs[epoch]
            }
            tracker.log_metrics(metrics, step=epoch+1)
        
        # Logar métricas finais
        final_metrics = {
            "final_accuracy": 0.923,
            "final_f1": 0.918,
            "final_precision": 0.925,
            "final_recall": 0.912
        }
        tracker.log_metrics(final_metrics)
        
        # Logar curvas
        tracker.log_training_curves(
            train_losses, val_losses,
            train_accs, val_accs
        )
        
        # Finalizar com sucesso
        tracker.end_run(status="FINISHED")
        
        print("✅ Experimento logado com sucesso no MLflow!")
        print(f"   Run ID: {run.info.run_id}")
        print(f"   URL: {MLFLOW_TRACKING_URI}/#/experiments/1/runs/{run.info.run_id}")
        
    except Exception as e:
        # Em caso de erro, marcar run como falha
        tracker.end_run(status="FAILED")
        raise

if __name__ == "__main__":
    # Executar exemplo
    print("🔬 Testando integração com MLflow...")
    example_training_with_mlflow()
