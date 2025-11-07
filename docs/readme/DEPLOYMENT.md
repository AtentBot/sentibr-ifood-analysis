# 🚀 DEPLOYMENT GUIDE - Fase 6

Guia completo para integrar a Fase 6 ao seu projeto SentiBR.

## 📋 Pré-requisitos

Antes de começar, certifique-se que você tem:

✅ Python 3.10+  
✅ Projeto SentiBR configurado (Fases 1-5)  
✅ OpenAI API key  
✅ Modelo BERT treinado em `models/bert_finetuned/`  
✅ Dados de teste em `data/processed/test.csv`  

---

## 🔧 Passo 1: Estrutura de Diretórios

### 1.1 Verificar Estrutura Atual

```bash
cd seu-projeto-sentibr
tree -L 2
```

Você deve ter algo como:
```
sentibr/
├── data/
├── models/
├── src/
│   ├── api/
│   ├── training/
│   ├── monitoring/
│   └── data/
├── scripts/
├── logs/
└── requirements.txt
```

### 1.2 Criar Estrutura para Fase 6

```bash
# Criar diretórios necessários
mkdir -p src/evaluation
mkdir -p logs/evaluation
mkdir -p logs/llm_judge
```

---

## 📦 Passo 2: Copiar Arquivos

### 2.1 Módulo de Evaluation

```bash
# Copiar módulo completo
cp -r fase6_eval_llm/evaluation/* src/evaluation/

# Verificar
ls -lh src/evaluation/
# Deve mostrar: __init__.py, eval_suite.py, llm_judge.py, README.md
```

### 2.2 Script de Execução

```bash
# Copiar script
cp fase6_eval_llm/run_evaluation.py scripts/

# Dar permissão de execução
chmod +x scripts/run_evaluation.py

# Verificar
ls -lh scripts/run_evaluation.py
```

### 2.3 Configurações

```bash
# Copiar requirements
cat fase6_eval_llm/requirements-evaluation.txt >> requirements.txt

# Copiar .env example (se não tiver)
if [ ! -f .env ]; then
    cp fase6_eval_llm/.env.example .env
    echo "⚠️  ATENÇÃO: Edite .env e adicione sua OPENAI_API_KEY"
fi
```

---

## 🔐 Passo 3: Configurar Variáveis de Ambiente

### 3.1 Editar .env

```bash
nano .env
```

Adicione:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-key-here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000

# Evaluation Configuration
EVAL_OUTPUT_DIR=logs/evaluation
EVAL_MAX_SAMPLES=1000
LLM_JUDGE_SAMPLES=100
```

### 3.2 Verificar Configuração

```bash
# Carregar variáveis
source .env

# Testar
echo $OPENAI_API_KEY
# Deve mostrar sua API key
```

---

## 📚 Passo 4: Instalar Dependências

### 4.1 Instalar Novas Dependências

```bash
# Instalar requirements
pip install -r requirements.txt

# Ou instalar apenas as novas
pip install openai>=1.0.0 matplotlib>=3.7.0 seaborn>=0.12.0
```

### 4.2 Verificar Instalação

```bash
# Testar imports
python -c "from src.evaluation import ModelEvaluator, LLMJudge; print('✅ Imports OK')"

# Testar OpenAI
python -c "import openai; print('✅ OpenAI OK')"
```

---

## ✅ Passo 5: Validar Integração

### 5.1 Teste Rápido - Evaluation Suite

```bash
# Testar eval_suite standalone
python src/evaluation/eval_suite.py
```

**Esperado:** Ver exemplo de avaliação com métricas.

### 5.2 Teste Rápido - LLM Judge

```bash
# Testar llm_judge standalone (requer API key)
export OPENAI_API_KEY='your-key'
python src/evaluation/llm_judge.py
```

**Esperado:** Ver 4 casos de teste sendo julgados pelo GPT-4o-mini.

### 5.3 Teste de Integração

```bash
# Executar avaliação em 10 samples (sem LLM, para teste rápido)
python scripts/run_evaluation.py --samples 10

# Ver resultados
ls -lh logs/evaluation/
cat logs/evaluation/bert_report_*.txt
```

**Esperado:** 
- ✅ Script executa sem erros
- ✅ Métricas calculadas
- ✅ Confusion matrix gerada
- ✅ Relatório criado

### 5.4 Teste com LLM (Cuidado: Custa ~$0.001)

```bash
# Executar com LLM Judge em 5 samples
python scripts/run_evaluation.py --samples 10 --use-llm --llm-samples 5

# Ver resultados LLM
cat logs/evaluation/final_report_*.txt
```

**Esperado:**
- ✅ LLM Judge executa
- ✅ Julgamentos salvos em JSON
- ✅ Métricas de agreement calculadas
- ✅ Relatório final gerado

---

## 🔗 Passo 6: Integrar com API Existente

### 6.1 Adicionar Endpoint de Avaliação (Opcional)

Edite `src/api/main.py` e adicione:

```python
from src.evaluation import ModelEvaluator, LLMJudge

@app.post("/api/v1/evaluate", tags=["Evaluation"])
async def evaluate_model(
    test_samples: int = 100,
    use_llm: bool = False
):
    """
    Executa avaliação do modelo em test set
    
    **Diferencial:** Permite avaliação on-demand via API
    """
    try:
        # Carregar test data
        test_df = pd.read_csv("data/processed/test.csv").head(test_samples)
        
        # Fazer predições
        predictor = get_predictor()
        predictions = []
        for text in test_df['text']:
            result = predictor.predict(text)
            predictions.append(result['sentiment'])
        
        # Avaliar com BERT
        evaluator = ModelEvaluator(model_name="BERT Fine-tuned")
        result = evaluator.evaluate(
            y_true=test_df['label'].values,
            y_pred=np.array(predictions)
        )
        
        response = {
            "model": "BERT Fine-tuned",
            "samples_evaluated": test_samples,
            "accuracy": result.accuracy,
            "f1_score": result.f1_score,
            "precision": result.precision,
            "recall": result.recall
        }
        
        # Avaliar com LLM se solicitado
        if use_llm and os.getenv("OPENAI_API_KEY"):
            judge = LLMJudge()
            llm_results, metrics = judge.judge_batch(
                texts=test_df['text'].tolist()[:10],
                bert_preds=predictions[:10],
                max_samples=10
            )
            response["llm_agreement"] = metrics['bert_agreement_rate']
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 6.2 Testar Novo Endpoint

```bash
# Iniciar API
uvicorn src.api.main:app --reload

# Testar endpoint
curl -X POST "http://localhost:8000/api/v1/evaluate?test_samples=50&use_llm=false"
```

---

## 📊 Passo 7: Adicionar ao Frontend (Opcional)

### 7.1 Criar Página de Avaliação

Crie `frontend/pages/4_📊_Avaliação.py`:

```python
import streamlit as st
import requests
import pandas as pd

st.title("📊 Avaliação do Modelo")

# Botão para executar avaliação
if st.button("🚀 Executar Avaliação"):
    with st.spinner("Executando avaliação..."):
        response = requests.post(
            "http://localhost:8000/api/v1/evaluate",
            params={"test_samples": 100, "use_llm": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Mostrar métricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Accuracy", f"{data['accuracy']:.3f}")
            col2.metric("Precision", f"{data['precision']:.3f}")
            col3.metric("Recall", f"{data['recall']:.3f}")
            col4.metric("F1-Score", f"{data['f1_score']:.3f}")
```

---

## 🧪 Passo 8: Criar Testes

### 8.1 Testes Unitários

Crie `tests/unit/test_eval_suite.py`:

```python
import pytest
import numpy as np
from src.evaluation import ModelEvaluator

def test_evaluator_creation():
    evaluator = ModelEvaluator(model_name="Test")
    assert evaluator.model_name == "Test"

def test_evaluate_perfect_predictions():
    evaluator = ModelEvaluator(model_name="Test")
    y_true = np.array([0, 1, 2])
    y_pred = np.array([0, 1, 2])
    
    result = evaluator.evaluate(y_true, y_pred)
    
    assert result.accuracy == 1.0
    assert result.f1_score == 1.0
```

### 8.2 Executar Testes

```bash
pytest tests/unit/test_eval_suite.py -v
```

---

## 📝 Passo 9: Atualizar Documentação

### 9.1 Atualizar README Principal

Adicione ao `README.md`:

```markdown
## 📊 Fase 6: Avaliação e LLM Integration

Sistema completo de avaliação com:
- ✅ Métricas clássicas (Accuracy, F1, etc)
- ✅ LLM-as-Judge com GPT-4o-mini
- ✅ Comparação BERT vs GPT
- ✅ Análise de edge cases

### Executar Avaliação

\```bash
python scripts/run_evaluation.py --samples 100 --use-llm
\```

### Documentação

Ver [src/evaluation/README.md](src/evaluation/README.md)
```

### 9.2 Atualizar Changelog

Adicione ao `CHANGELOG.md`:

```markdown
## [1.6.0] - 2024-11-06

### Added
- ✨ Evaluation Suite completo
- ✨ LLM-as-Judge com GPT-4o-mini
- ✨ Comparação BERT vs GPT
- ✨ Script de avaliação end-to-end
- 📚 Documentação extensiva

### Features
- Métricas clássicas (Accuracy, Precision, Recall, F1)
- Confusion Matrix e visualizações
- Análise detalhada de erros
- Identificação de edge cases
- Análise por aspectos
- Tracking de custos
```

---

## 🎯 Passo 10: Executar Avaliação Completa

### 10.1 Avaliação de Produção

```bash
# Avaliação completa no test set
python scripts/run_evaluation.py \
    --test-file data/processed/test.csv \
    --samples 1000 \
    --use-llm \
    --llm-samples 100 \
    --output-dir logs/evaluation/production

# Estimar custo: ~$0.015
```

### 10.2 Verificar Resultados

```bash
# Ver todos os outputs
ls -lh logs/evaluation/production/

# Ler relatório final
cat logs/evaluation/production/final_report_*.txt

# Verificar métricas BERT
cat logs/evaluation/production/bert_evaluation_*.json | jq '.accuracy, .f1_score'

# Verificar métricas LLM
cat logs/evaluation/production/metrics_*.json | jq '.bert_agreement_rate'
```

---

## ✅ Checklist de Deployment

Use este checklist para garantir que tudo está funcionando:

### Estrutura
- [ ] `src/evaluation/` criado com todos os arquivos
- [ ] `scripts/run_evaluation.py` copiado
- [ ] `logs/evaluation/` e `logs/llm_judge/` criados

### Configuração
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] `.env` configurado com `OPENAI_API_KEY`
- [ ] Variáveis de ambiente carregadas

### Testes Básicos
- [ ] `python src/evaluation/eval_suite.py` executa sem erros
- [ ] `python src/evaluation/llm_judge.py` executa com API key
- [ ] `python scripts/run_evaluation.py --samples 10` funciona

### Integração
- [ ] Imports funcionam: `from src.evaluation import ModelEvaluator`
- [ ] API predictor acessível
- [ ] Test data disponível em `data/processed/test.csv`

### Avaliação Completa
- [ ] Avaliação BERT completa executada
- [ ] LLM Judge testado (pelo menos 10 samples)
- [ ] Relatórios gerados corretamente
- [ ] Visualizações criadas (confusion matrix)

### Documentação
- [ ] README principal atualizado
- [ ] CHANGELOG atualizado
- [ ] Documentação da Fase 6 lida

### Validação Final
- [ ] Accuracy > 0.90 ✅
- [ ] F1-Score > 0.88 ✅
- [ ] LLM Agreement > 0.85 ✅
- [ ] Custos sob controle ✅

---

## 🐛 Troubleshooting Comum

### Problema 1: Import Error

**Erro:**
```
ImportError: cannot import name 'ModelEvaluator' from 'src.evaluation'
```

**Solução:**
```bash
# Verificar estrutura
ls -lh src/evaluation/__init__.py

# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Problema 2: OpenAI API Key

**Erro:**
```
ValueError: OpenAI API key não encontrada
```

**Solução:**
```bash
# Exportar temporariamente
export OPENAI_API_KEY='your-key'

# Ou adicionar ao .env
echo "OPENAI_API_KEY=your-key" >> .env
source .env
```

### Problema 3: Model Not Found

**Erro:**
```
FileNotFoundError: models/bert_finetuned not found
```

**Solução:**
```bash
# Verificar se modelo existe
ls -lh models/bert_finetuned/

# Se não existe, treinar
python src/training/train.py
```

### Problema 4: Test Data Missing

**Erro:**
```
FileNotFoundError: data/processed/test.csv not found
```

**Solução:**
```bash
# Preparar dados
python src/data/load_data_v2.py
python src/data/split_dataset.py
```

---

## 🚀 Próximos Passos

Após deployment bem-sucedido:

### Imediato
1. ✅ Executar avaliação completa no test set
2. ✅ Documentar métricas obtidas
3. ✅ Integrar com CI/CD (se aplicável)

### Fase 7: Docker
1. Containerizar aplicação completa
2. Docker Compose com todos os serviços
3. Deploy em produção

### Fase 8: Testes
1. Unit tests completos
2. Integration tests
3. Load tests com Locust

---

## 💡 Dicas de Uso em Produção

### 1. Continuous Evaluation

Crie um cron job para avaliar periodicamente:

```bash
# Adicionar ao crontab
0 0 * * 0 cd /path/to/sentibr && python scripts/run_evaluation.py --samples 500 --use-llm --llm-samples 50
```

### 2. Alert em Quedas de Performance

```python
# Em scripts/run_evaluation.py
if result.accuracy < 0.90:
    send_alert(f"Accuracy dropped to {result.accuracy}")
```

### 3. Cost Control

```python
# Limitar gastos LLM
MAX_COST = 1.00  # USD
if judge.total_cost > MAX_COST:
    raise ValueError(f"Cost limit exceeded: ${judge.total_cost}")
```

---

## 📊 Métricas de Sucesso

Após deployment, você deve ter:

- ✅ Accuracy > 90% no test set
- ✅ F1-Score > 88%
- ✅ LLM Agreement > 85%
- ✅ Tempo de avaliação < 10min para 1000 samples
- ✅ Custo LLM < $0.20 para avaliação completa

---

## 🎉 Conclusão

Parabéns! Você integrou com sucesso a **Fase 6: EVAL E LLM INTEGRATION** ao seu projeto SentiBR.

Agora você tem:
- ✅ Sistema completo de avaliação
- ✅ LLM-as-Judge funcional
- ✅ Comparação BERT vs GPT
- ✅ Análise de edge cases
- ✅ Tracking de custos
- ✅ Documentação completa

**Próximo passo:** [Fase 7 - Docker + Deploy](../docker/README.md)

---

**Desenvolvido com ❤️ para o desafio técnico de IA Sênior**
