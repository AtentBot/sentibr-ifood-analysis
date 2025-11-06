# 🔧 Troubleshooting Guide - Phase 6

Guia rápido de soluções para problemas comuns da Fase 6.

---

## 🚨 Problemas de Instalação

### ❌ "No module named 'X'"

**Problema:** Pacote Python não instalado

**Solução:**
```bash
# Instalar todos os requirements
pip install -r requirements_phase6.txt

# Ou instalar pacote específico
pip install nome-do-pacote
```

**Pacotes essenciais:**
- torch
- transformers
- openai
- lime
- scikit-learn
- pandas
- numpy
- matplotlib
- seaborn
- tqdm

---

### ❌ "CUDA out of memory"

**Problema:** GPU sem memória suficiente

**Soluções:**

1. **Reduzir batch size:**
```python
# Em phase6_eval_suite.py, linha ~50
y_pred, y_proba = self.predict_batch(texts, batch_size=8)  # Era 16
```

2. **Forçar CPU:**
```python
# Adicionar ao inicializar
evaluator = ModelEvaluator(model_path, device='cpu')
```

3. **Liberar memória GPU:**
```bash
# Matar processos usando GPU
nvidia-smi
kill -9 <PID>
```

---

### ❌ "Could not load BERT model"

**Problema:** Modelo BERT não encontrado ou corrompido

**Verificações:**
```bash
# Verifica se modelo existe
ls -la models/bert_finetuned/

# Deve ter:
# - config.json
# - pytorch_model.bin (ou model.safetensors)
# - tokenizer_config.json
```

**Solução:**
- Execute o treinamento (Fase 2) primeiro
- Ou baixe modelo pré-treinado do HuggingFace
- Verifique se o caminho está correto

---

## 🔑 Problemas com OpenAI API

### ❌ "OPENAI_API_KEY not found"

**Problema:** API key não configurada

**Solução:**

**Linux/Mac:**
```bash
export OPENAI_API_KEY='sk-proj-...'
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='sk-proj-...'
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=sk-proj-...
```

**Persistente (arquivo .env):**
```bash
# Crie arquivo .env
echo "OPENAI_API_KEY=sk-proj-..." > .env

# Instale python-dotenv
pip install python-dotenv

# Use no código
from dotenv import load_dotenv
load_dotenv()
```

---

### ❌ "RateLimitError: Rate limit exceeded"

**Problema:** Muitas requisições à API OpenAI

**Soluções:**

1. **Aumentar delay entre requests:**
```python
# Em phase6_llm_judge.py, linha ~150
time.sleep(0.5)  # Era 0.1
```

2. **Reduzir número de samples:**
```bash
python run_phase6.py --llm-samples 50  # Ao invés de 100
```

3. **Upgrade do plano OpenAI:**
- Tier 1: 500 RPM
- Tier 2: 5000 RPM
- https://platform.openai.com/account/limits

---

### ❌ "AuthenticationError: Invalid API key"

**Problema:** API key incorreta ou expirada

**Verificações:**
```bash
# Ver key configurada (primeiros 10 chars)
echo $OPENAI_API_KEY | cut -c1-10

# Testar key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Soluções:**
- Gere nova key em: https://platform.openai.com/api-keys
- Verifique se não há espaços extras
- Confirme que key começa com "sk-"

---

### ❌ "OpenAI API error: Insufficient quota"

**Problema:** Sem créditos na conta OpenAI

**Solução:**
- Adicione créditos: https://platform.openai.com/account/billing
- Ou pule componentes LLM:
```bash
python run_phase6.py --skip-llm-judge --skip-comparison
```

---

## 📁 Problemas com Arquivos

### ❌ "predictions_*.csv not found"

**Problema:** Arquivo de predições não existe

**Solução:**
```bash
# Execute primeiro a avaliação básica
python phase6_eval_suite.py

# Ou execute Fase 6 completa
python run_phase6.py
```

---

### ❌ "Test data not found"

**Problema:** data/processed/test.csv não existe

**Solução:**
- Execute preparação de dados (Fase 1)
- Ou crie test.csv manualmente com colunas: `text`, `label`

---

### ❌ "Permission denied" ao executar setup

**Problema:** Script setup sem permissão de execução

**Solução:**
```bash
chmod +x setup_phase6.sh
./setup_phase6.sh
```

---

## 🐛 Problemas de Execução

### ❌ "LIME explainer takes too long"

**Problema:** LIME muito lento

**Soluções:**

1. **Reduzir num_samples:**
```python
explanation = explainer.explain_prediction(
    text="...",
    num_samples=500  # Era 1000
)
```

2. **Reduzir número de explicações:**
```bash
python run_phase6.py --explainability-samples 10  # Ao invés de 20
```

---

### ❌ "JSON decode error" em LLM Judge

**Problema:** GPT retornou resposta não-JSON

**Causa:** Temperatura muito alta ou modelo hallucinating

**Solução:**
```python
# Em phase6_llm_judge.py, ajustar temperatura
response = self.client.chat.completions.create(
    model=self.model,
    temperature=0.1,  # Era 0.3 - mais determinístico
    ...
)
```

---

### ❌ "Comparison shows BERT worse than GPT"

**Problema:** BERT com accuracy menor que GPT (inesperado)

**Causas possíveis:**
1. Modelo BERT não foi treinado corretamente
2. Sample muito pequeno (estatisticamente não significativo)
3. Test set com distribuição diferente do treino

**Verificações:**
```bash
# 1. Verifica se modelo foi treinado
ls -la models/bert_finetuned/

# 2. Aumenta sample size
python run_phase6.py --comparison-samples 200

# 3. Verifica distribuição do test set
import pandas as pd
df = pd.read_csv('data/processed/test.csv')
print(df['label'].value_counts())
```

---

## 📊 Problemas de Visualização

### ❌ "Matplotlib display error"

**Problema:** Plots não aparecem

**Soluções:**

**Sem display (servidor):**
```python
# Adicionar no início do arquivo
import matplotlib
matplotlib.use('Agg')  # Backend sem display
```

**Com display:**
```python
import matplotlib.pyplot as plt
plt.show()  # Força exibição
```

---

### ❌ "Figure too large to save"

**Problema:** Plot muito grande

**Solução:**
```python
# Reduzir DPI
plt.savefig(path, dpi=150)  # Era 300

# Ou reduzir tamanho
fig, ax = plt.subplots(figsize=(8, 6))  # Era (14, 10)
```

---

## 💾 Problemas de Memória

### ❌ "MemoryError: Unable to allocate"

**Problema:** RAM insuficiente

**Soluções:**

1. **Processar em batches menores:**
```python
# Reduzir batch_size
for i in range(0, len(texts), 8):  # Era 16
```

2. **Limpar memória:**
```python
import gc
import torch

# Após cada batch
gc.collect()
torch.cuda.empty_cache()
```

3. **Usar menos samples:**
```bash
python run_phase6.py \
    --llm-samples 50 \
    --comparison-samples 50 \
    --explainability-samples 10
```

---

## ⚡ Problemas de Performance

### ❌ "Phase 6 takes too long"

**Problema:** Execução muito lenta

**Tempos esperados:**
- Eval Framework: 2-5 min (1000 samples)
- LLM Judge: 5-10 min (100 samples)
- BERT vs GPT: 5-10 min (100 samples)
- Explainability: 10-20 min (20 samples)

**Total esperado:** 20-45 min

**Otimizações:**

1. **Usar GPU:**
```python
# Verificar se está usando GPU
import torch
print(torch.cuda.is_available())
```

2. **Reduzir samples:**
```bash
python run_phase6.py \
    --llm-samples 50 \
    --comparison-samples 50 \
    --explainability-samples 10
```

3. **Pular etapas demoradas:**
```bash
python run_phase6.py \
    --skip-explainability  # Mais demorada
```

---

## 🔍 Debug Avançado

### Ativar logs detalhados

```python
# Adicionar no início do script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testar componente isolado

```bash
# Teste rápido
python test_phase6.py

# Teste individual
python -c "from phase6_eval_suite import ModelEvaluator; print('OK')"
```

### Ver stack trace completo

```bash
# Executar com verbose
python run_phase6.py 2>&1 | tee phase6_debug.log
```

---

## 🆘 Problemas Não Resolvidos?

### Checklist de debug:

1. ✅ Todos os pacotes instalados?
   ```bash
   pip list | grep -E "torch|transformers|openai|lime"
   ```

2. ✅ Modelo BERT existe e está completo?
   ```bash
   ls -la models/bert_finetuned/
   ```

3. ✅ Test data existe e está formatado?
   ```bash
   head -n 5 data/processed/test.csv
   ```

4. ✅ OpenAI key válida? (se usar LLM)
   ```bash
   echo $OPENAI_API_KEY | cut -c1-10
   ```

5. ✅ Memória suficiente?
   ```bash
   free -h  # Linux
   # Ou no Python:
   import psutil; print(f"RAM: {psutil.virtual_memory().percent}%")
   ```

6. ✅ GPU disponível? (opcional)
   ```bash
   nvidia-smi  # Se CUDA
   ```

### Ainda com problemas?

1. Execute teste completo:
   ```bash
   python test_phase6.py
   ```

2. Verifique logs em:
   ```bash
   tail -n 100 evaluation_results/phase6_summary.json
   ```

3. Tente execução mínima:
   ```bash
   python run_phase6.py \
       --skip-llm-judge \
       --skip-comparison \
       --skip-explainability
   ```

4. Documente o erro:
   - Mensagem de erro completa
   - Arquivo/linha onde ocorreu
   - O que estava tentando fazer
   - Logs relevantes

---

## 📚 Recursos Adicionais

- **README Principal:** `README_PHASE6.md`
- **Resumo Executivo:** `EXECUTIVE_SUMMARY_PHASE6.md`
- **Test Suite:** `test_phase6.py`
- **Setup Script:** `setup_phase6.sh`

---

## 💡 Dicas Gerais

### Execução passo a passo
```bash
# 1. Teste básico primeiro
python test_phase6.py

# 2. Eval framework isolado
python phase6_eval_suite.py

# 3. LLM judge (com key)
export OPENAI_API_KEY='...'
python phase6_llm_judge.py

# 4. Comparação
python phase6_bert_vs_gpt.py

# 5. Explainability
python phase6_explainability.py

# 6. Tudo junto
python run_phase6.py
```

### Começar simples
```bash
# Versão rápida (5-10 min)
python run_phase6.py \
    --skip-llm-judge \
    --skip-comparison \
    --explainability-samples 5
```

### Aumentar gradualmente
```bash
# Versão completa mas rápida (15-20 min)
python run_phase6.py \
    --llm-samples 50 \
    --comparison-samples 50 \
    --explainability-samples 10

# Versão completa padrão (30-45 min)
python run_phase6.py \
    --llm-samples 100 \
    --comparison-samples 100 \
    --explainability-samples 20
```

---

**Lembre-se:** A maioria dos problemas vem de:
1. ❌ Dependências não instaladas
2. ❌ Modelo BERT não treinado
3. ❌ OpenAI key não configurada
4. ❌ Memória insuficiente

Execute `python test_phase6.py` para identificar o problema! 🔍

---

*SentiBR - Phase 6 Troubleshooting Guide*
