"""
Script de Teste Completo do MLflow
Testa todas as funcionalidades críticas
"""
import mlflow
import requests
import time
import sys
from datetime import datetime

# Configuração
MLFLOW_URL = "http://localhost:5000"
TIMEOUT = 10

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_health():
    """Teste 1: Health Check"""
    print_header("Teste 1: Health Check")
    
    try:
        response = requests.get(f"{MLFLOW_URL}/health", timeout=TIMEOUT)
        
        if response.status_code == 200:
            print("✅ MLflow está ONLINE!")
            print(f"   Status: {response.json()}")
            return True
        else:
            print(f"❌ MLflow respondeu com status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao MLflow")
        print(f"   URL: {MLFLOW_URL}")
        print("   Verifique se o container está rodando:")
        print("   docker ps | grep mlflow")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

def test_connection():
    """Teste 2: Conexão com API"""
    print_header("Teste 2: Conexão com API")
    
    try:
        mlflow.set_tracking_uri(MLFLOW_URL)
        tracking_uri = mlflow.get_tracking_uri()
        
        print(f"✅ Tracking URI configurado: {tracking_uri}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar tracking URI: {str(e)}")
        return False

def test_list_experiments():
    """Teste 3: Listar Experimentos"""
    print_header("Teste 3: Listar Experimentos")
    
    try:
        client = mlflow.tracking.MlflowClient(tracking_uri=MLFLOW_URL)
        experiments = client.search_experiments()
        
        print(f"✅ Encontrados {len(experiments)} experimentos")
        
        for exp in experiments[:5]:  # Mostrar apenas os 5 primeiros
            print(f"   - ID: {exp.experiment_id} | Nome: {exp.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao listar experimentos: {str(e)}")
        return False

def test_create_experiment():
    """Teste 4: Criar Experimento"""
    print_header("Teste 4: Criar Experimento")
    
    exp_name = f"teste_diagnostico_{int(time.time())}"
    
    try:
        mlflow.set_tracking_uri(MLFLOW_URL)
        
        # Tentar criar experimento
        exp_id = mlflow.create_experiment(exp_name)
        
        print(f"✅ Experimento criado com sucesso!")
        print(f"   Nome: {exp_name}")
        print(f"   ID: {exp_id}")
        
        return True, exp_id
        
    except Exception as e:
        print(f"❌ Erro ao criar experimento: {str(e)}")
        return False, None

def test_create_run(exp_id):
    """Teste 5: Criar Run"""
    print_header("Teste 5: Criar Run")
    
    if not exp_id:
        print("⚠️  Pulando (experimento não foi criado)")
        return False
    
    try:
        mlflow.set_tracking_uri(MLFLOW_URL)
        mlflow.set_experiment(experiment_id=exp_id)
        
        # Criar run
        with mlflow.start_run() as run:
            # Log params
            mlflow.log_param("modelo", "BERT")
            mlflow.log_param("epochs", 3)
            mlflow.log_param("batch_size", 32)
            mlflow.log_param("learning_rate", 2e-5)
            
            # Log metrics
            mlflow.log_metric("accuracy", 0.923)
            mlflow.log_metric("f1_score", 0.918)
            mlflow.log_metric("precision", 0.925)
            mlflow.log_metric("recall", 0.912)
            
            # Log metrics progressivos (simular épocas)
            for epoch in range(1, 4):
                mlflow.log_metric("train_loss", 0.5 / epoch, step=epoch)
                mlflow.log_metric("val_loss", 0.6 / epoch, step=epoch)
            
            # Log tags
            mlflow.set_tag("ambiente", "teste")
            mlflow.set_tag("versao", "1.0.0")
            mlflow.set_tag("data", datetime.now().strftime("%Y-%m-%d"))
            
            run_id = run.info.run_id
        
        print("✅ Run criado com sucesso!")
        print(f"   Run ID: {run_id}")
        print(f"   URL: {MLFLOW_URL}/#/experiments/{exp_id}/runs/{run_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar run: {str(e)}")
        return False

def test_log_artifact(exp_id):
    """Teste 6: Salvar Artifact"""
    print_header("Teste 6: Salvar Artifact")
    
    if not exp_id:
        print("⚠️  Pulando (experimento não foi criado)")
        return False
    
    try:
        mlflow.set_tracking_uri(MLFLOW_URL)
        mlflow.set_experiment(experiment_id=exp_id)
        
        # Criar arquivo temporário
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar arquivo de teste
            test_file = os.path.join(tmpdir, "teste.txt")
            with open(test_file, "w") as f:
                f.write("Teste de artifact do MLflow\n")
                f.write(f"Timestamp: {datetime.now()}\n")
                f.write("Status: Funcionando!\n")
            
            # Log artifact
            with mlflow.start_run():
                mlflow.log_artifact(test_file)
                run_id = mlflow.active_run().info.run_id
        
        print("✅ Artifact salvo com sucesso!")
        print(f"   Arquivo: teste.txt")
        print(f"   Run ID: {run_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar artifact: {str(e)}")
        return False

def test_search_runs(exp_id):
    """Teste 7: Buscar Runs"""
    print_header("Teste 7: Buscar Runs")
    
    if not exp_id:
        print("⚠️  Pulando (experimento não foi criado)")
        return False
    
    try:
        client = mlflow.tracking.MlflowClient(tracking_uri=MLFLOW_URL)
        runs = client.search_runs(experiment_ids=[exp_id])
        
        print(f"✅ Encontrados {len(runs)} runs no experimento")
        
        for run in runs[:3]:  # Mostrar apenas 3
            print(f"   - Run ID: {run.info.run_id}")
            print(f"     Status: {run.info.status}")
            print(f"     Métricas: {dict(run.data.metrics)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao buscar runs: {str(e)}")
        return False

def test_ui_access():
    """Teste 8: Acesso à UI"""
    print_header("Teste 8: Acesso à Interface Web")
    
    try:
        response = requests.get(MLFLOW_URL, timeout=TIMEOUT)
        
        if response.status_code == 200:
            print("✅ Interface web acessível!")
            print(f"   URL: {MLFLOW_URL}")
            print("   Abra no navegador para visualizar os experimentos")
            return True
        else:
            print(f"❌ Interface respondeu com status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao acessar interface: {str(e)}")
        return False

def print_summary(results):
    """Imprime resumo dos testes"""
    print_header("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\nTotal de testes: {total}")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"\nTaxa de sucesso: {passed/total*100:.1f}%\n")
    
    print("Detalhes:")
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\nMLflow está funcionando perfeitamente!")
        print(f"\nAcesse: {MLFLOW_URL}")
    else:
        print(f"\n⚠️  {failed} TESTE(S) FALHARAM")
        print("\nVerifique:")
        print("  1. Container está rodando: docker ps | grep mlflow")
        print("  2. Logs do container: docker logs sentibr-mlflow")
        print("  3. Permissões dos diretórios: ls -la mlflow/")
        print("  4. Arquivo mlflow.db existe: ls -la mlflow/mlruns/mlflow.db")
    
    print("="*60 + "\n")

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("  🔬 MLflow - Script de Teste Completo")
    print("="*60)
    print(f"\nMLflow URL: {MLFLOW_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Teste 1: Health Check
    results["Health Check"] = test_health()
    if not results["Health Check"]:
        print("\n❌ ERRO CRÍTICO: MLflow não está acessível!")
        print("   Execute primeiro: docker-compose up -d mlflow")
        sys.exit(1)
    
    time.sleep(1)
    
    # Teste 2: Conexão
    results["Conexão API"] = test_connection()
    time.sleep(1)
    
    # Teste 3: Listar experimentos
    results["Listar Experimentos"] = test_list_experiments()
    time.sleep(1)
    
    # Teste 4: Criar experimento
    success, exp_id = test_create_experiment()
    results["Criar Experimento"] = success
    time.sleep(1)
    
    # Teste 5: Criar run
    results["Criar Run"] = test_create_run(exp_id)
    time.sleep(1)
    
    # Teste 6: Salvar artifact
    results["Salvar Artifact"] = test_log_artifact(exp_id)
    time.sleep(1)
    
    # Teste 7: Buscar runs
    results["Buscar Runs"] = test_search_runs(exp_id)
    time.sleep(1)
    
    # Teste 8: UI
    results["Interface Web"] = test_ui_access()
    
    # Resumo
    print_summary(results)
    
    # Exit code baseado no resultado
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {str(e)}")
        sys.exit(1)
