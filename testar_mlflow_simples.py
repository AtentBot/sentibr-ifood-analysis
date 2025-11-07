"""
Script de Teste Simples do MLflow
Usa apenas requests HTTP (sem biblioteca MLflow)
"""
import requests
import json
import time
from datetime import datetime

# Configuração
MLFLOW_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_health():
    """Teste 1: Health Check"""
    print_header("Teste 1: Health Check")
    
    try:
        response = requests.get(f"{MLFLOW_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ MLflow está ONLINE!")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_api_version():
    """Teste 2: Versão da API"""
    print_header("Teste 2: Versão da API")
    
    try:
        response = requests.get(f"{MLFLOW_URL}/version", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Versão: {response.text}")
            return True
        else:
            print(f"⚠️  Status: {response.status_code}")
            return True  # Não crítico
    except Exception as e:
        print(f"⚠️  Não foi possível obter versão: {str(e)}")
        return True  # Não crítico

def test_list_experiments():
    """Teste 3: Listar Experimentos"""
    print_header("Teste 3: Listar Experimentos")
    
    try:
        response = requests.get(
            f"{MLFLOW_URL}/api/2.0/mlflow/experiments/search",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            experiments = data.get('experiments', [])
            print(f"✅ Encontrados {len(experiments)} experimentos")
            
            for exp in experiments[:3]:
                print(f"   - ID: {exp['experiment_id']} | Nome: {exp['name']}")
            
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_create_experiment():
    """Teste 4: Criar Experimento"""
    print_header("Teste 4: Criar Experimento")
    
    exp_name = f"teste_api_{int(time.time())}"
    
    try:
        payload = {"name": exp_name}
        
        response = requests.post(
            f"{MLFLOW_URL}/api/2.0/mlflow/experiments/create",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            exp_id = data.get('experiment_id')
            print(f"✅ Experimento criado!")
            print(f"   Nome: {exp_name}")
            print(f"   ID: {exp_id}")
            return True, exp_id
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False, None

def test_create_run(exp_id):
    """Teste 5: Criar Run"""
    print_header("Teste 5: Criar Run")
    
    if not exp_id:
        print("⚠️  Pulando (experimento não criado)")
        return False
    
    try:
        payload = {
            "experiment_id": exp_id,
            "start_time": int(time.time() * 1000),
            "tags": [
                {"key": "mlflow.user", "value": "teste"},
                {"key": "ambiente", "value": "teste"}
            ]
        }
        
        response = requests.post(
            f"{MLFLOW_URL}/api/2.0/mlflow/runs/create",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            run_id = data['run']['info']['run_id']
            print(f"✅ Run criada!")
            print(f"   Run ID: {run_id}")
            print(f"   URL: {MLFLOW_URL}/#/experiments/{exp_id}/runs/{run_id}")
            return True, run_id
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False, None

def test_log_param(run_id):
    """Teste 6: Logar Parâmetro"""
    print_header("Teste 6: Logar Parâmetro")
    
    if not run_id:
        print("⚠️  Pulando (run não criada)")
        return False
    
    try:
        payload = {
            "run_id": run_id,
            "key": "epochs",
            "value": "3"
        }
        
        response = requests.post(
            f"{MLFLOW_URL}/api/2.0/mlflow/runs/log-parameter",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Parâmetro logado!")
            print("   Key: epochs")
            print("   Value: 3")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_log_metric(run_id):
    """Teste 7: Logar Métrica"""
    print_header("Teste 7: Logar Métrica")
    
    if not run_id:
        print("⚠️  Pulando (run não criada)")
        return False
    
    try:
        payload = {
            "run_id": run_id,
            "key": "accuracy",
            "value": 0.923,
            "timestamp": int(time.time() * 1000),
            "step": 1
        }
        
        response = requests.post(
            f"{MLFLOW_URL}/api/2.0/mlflow/runs/log-metric",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Métrica logada!")
            print("   Key: accuracy")
            print("   Value: 0.923")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_ui():
    """Teste 8: Interface Web"""
    print_header("Teste 8: Interface Web")
    
    try:
        response = requests.get(MLFLOW_URL, timeout=5)
        
        if response.status_code == 200:
            print("✅ Interface web acessível!")
            print(f"   URL: {MLFLOW_URL}")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def print_summary(results):
    """Resumo dos testes"""
    print_header("RESUMO DOS TESTES")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\nTotal: {total} testes")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"\nTaxa de sucesso: {passed/total*100:.1f}%\n")
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print("\n" + "="*60)
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"\nAcesse: {MLFLOW_URL}")
    else:
        print(f"\n⚠️  {failed} TESTE(S) FALHARAM")
        print("\nVerifique:")
        print("  docker logs sentibr-mlflow")
    
    print("="*60 + "\n")

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("  🔬 MLflow - Script de Teste Simples")
    print("="*60)
    print(f"\nMLflow URL: {MLFLOW_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Teste 1: Health
    results["Health Check"] = test_health()
    if not results["Health Check"]:
        print("\n❌ MLflow não está acessível!")
        print("   Execute: docker-compose up -d mlflow")
        return
    
    time.sleep(1)
    
    # Teste 2: Versão
    results["Versão API"] = test_api_version()
    time.sleep(1)
    
    # Teste 3: Listar
    results["Listar Experimentos"] = test_list_experiments()
    time.sleep(1)
    
    # Teste 4: Criar experimento
    success, exp_id = test_create_experiment()
    results["Criar Experimento"] = success
    time.sleep(1)
    
    # Teste 5: Criar run
    success, run_id = test_create_run(exp_id)
    results["Criar Run"] = success
    time.sleep(1)
    
    # Teste 6: Log param
    results["Log Parâmetro"] = test_log_param(run_id)
    time.sleep(1)
    
    # Teste 7: Log metric
    results["Log Métrica"] = test_log_metric(run_id)
    time.sleep(1)
    
    # Teste 8: UI
    results["Interface Web"] = test_ui()
    
    # Resumo
    print_summary(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido")
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {str(e)}")
