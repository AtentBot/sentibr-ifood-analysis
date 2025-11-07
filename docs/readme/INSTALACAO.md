# 🚀 FASE 6 - INSTALAÇÃO E USO RÁPIDO

## 📁 Estrutura dos Arquivos

Você recebeu 9 arquivos para a Fase 6:

```
fase6_eval_llm/
├── README.md                      # Documentação completa (LEIA PRIMEIRO!)
├── __init__.py                    # Módulo Python
├── eval_suite.py                  # Framework de avaliação
├── llm_judge.py                   # LLM-as-a-Judge
├── compare_models.py              # Comparação BERT vs GPT
├── explainability.py              # Explicabilidade (LIME)
├── run_evaluation.py              # Script de execução
├── requirements-evaluation.txt    # Dependências
└── .env.example                   # Template de configuração
```

---

## ⚡ INSTALAÇÃO RÁPIDA (3 PASSOS)

### 1️⃣ **Colocar Arquivos no Projeto**

```bash
# No diretório raiz do projeto SentiBR:

# Criar diretório de evaluation (se não existir)
mkdir -p src/evaluation

# Copiar módulos de evaluation
cp eval_suite.py src/evaluation/
cp llm_judge.py src/evaluation/
cp compare_models.py src/evaluation/
cp explainability.py src/evaluation/
cp __init__.py src/evaluation/

# Criar diretório scripts (se não existir)
mkdir -p scripts

# Copiar script de execução
cp run_evaluation.py scripts/
chmod +x scripts/run_evaluation.py

# Copiar configuração
cp .env.example .env
```

### 2️⃣ **Instalar Dependências**

```bash
# Instalar requirements específicos da Fase 6
pip install -r requirements-evaluation.txt

# Ou manualmente:
pip install openai>=1.3.0 lime>=0.2.0.1 tqdm>=4.65.0
```

### 3️⃣ **Configurar OpenAI API Key**

```bash
# Editar .env e adicionar sua chave
nano .env

# Ou export direto
export OPENAI_API_KEY='sk-your-key-here'
```

**✅ Pronto! Instalação completa.**

---

## 🎯 USO BÁSICO

### **Teste Rápido (sem API Key)**

```bash
# Apenas métricas básicas (não precisa de OpenAI)
python scripts/run_evaluation.py --metrics-only
```

### **Avaliação Completa (com API Key)**

```bash
# TODAS as fases (métricas + LLM + comparação + explainability)
python scripts/run_evaluation.py --full

# Com menos amostras para economizar (recomendado para testes)
python scripts/run_evaluation.py --full --samples 50
```

### **Fases Individuais**

```bash
# Apenas LLM-as-Judge
python scripts/run_evaluation.py --llm-only --samples 30

# Apenas comparação BERT vs GPT
python scripts/run_evaluation.py --comparison --samples 50

# Apenas explicabilidade
python scripts/run_evaluation.py --explainability
```

---

## 📊 RESULTADOS

Após executar, os resultados estarão em:

```
logs/evaluation_YYYYMMDD_HHMMSS/
├── metrics/              # Métricas + visualizações
├── llm_judge/           # Avaliações LLM
├── bert_vs_gpt/         # Comparação de modelos
└── explainability/      # Explicações LIME
```

---

## 💡 EXEMPLOS DE CÓDIGO

### **Exemplo 1: Avaliação Básica**

```python
from src.evaluation import ModelEvaluator
import pandas as pd

# Carregar dados
test_df = pd.read_csv('data/processed/test.csv')

# Avaliar
evaluator = ModelEvaluator(model_path='models/bert_finetuned')
results = evaluator.evaluate_dataset(
    df=test_df,
    save_dir='logs/my_evaluation'
)

print(f"Accuracy: {results['metrics']['overall']['accuracy']:.2%}")
```

### **Exemplo 2: LLM-as-Judge**

```python
from src.evaluation import LLMJudge

judge = LLMJudge()  # Usa OPENAI_API_KEY do ambiente

evaluation = judge.evaluate_prediction(
    review_text="Comida ótima mas demorou!",
    predicted_sentiment="Positivo",
    predicted_confidence=0.85
)

print(f"Verdadeiro: {evaluation['true_sentiment']}")
print(f"Correto: {evaluation['is_correct']}")
```

### **Exemplo 3: Comparação**

```python
from src.evaluation import ModelComparator, GPTSentimentAnalyzer

evaluator = ModelEvaluator(model_path='models/bert_finetuned')
gpt = GPTSentimentAnalyzer()
comparator = ModelComparator(evaluator, gpt)

results = comparator.compare_on_samples(
    reviews=["Excelente!", "Péssimo"],
    max_samples=5
)

print(comparator.generate_recommendation(results))
```

---

## 🔧 TROUBLESHOOTING RÁPIDO

### **❌ Erro: "OPENAI_API_KEY not found"**

```bash
# Verificar se está setada
echo $OPENAI_API_KEY

# Setar novamente
export OPENAI_API_KEY='sk-your-key'

# Ou adicionar ao .env
echo "OPENAI_API_KEY=sk-your-key" > .env
```

### **❌ Erro: "Model not found"**

```bash
# Treinar modelo primeiro
python src/training/train.py
```

### **❌ Erro: "No module named 'lime'"**

```bash
# Instalar dependências
pip install -r requirements-evaluation.txt
```

### **❌ Rate Limit do OpenAI**

```python
# Reduzir número de samples
python scripts/run_evaluation.py --llm-only --samples 10

# Ou aumentar delay no código
gpt_df = gpt_analyzer.predict_batch(reviews, delay=1.0)
```

---

## 📈 CUSTOS ESTIMADOS

### **OpenAI API (GPT-4o-mini)**

- **Preço**: ~$0.150 / 1M input tokens
- **Custo por review**: ~$0.000013 (13 tokens médios)
- **100 reviews**: ~$0.0013 (menos de 1 centavo!)
- **1000 reviews**: ~$0.013 (1 centavo!)

### **Recomendações de Uso**

| Samples | Custo Estimado | Tempo | Uso Recomendado |
|---------|----------------|-------|-----------------|
| 10 | $0.0001 | ~30s | Teste rápido |
| 50 | $0.0007 | ~2min | Validação |
| 100 | $0.0013 | ~5min | Análise padrão |
| 500 | $0.0065 | ~25min | Análise completa |

---

## ✅ CHECKLIST DE VALIDAÇÃO

Execute esta checklist para garantir que tudo está funcionando:

```bash
# 1. Verificar instalação
python -c "from src.evaluation import ModelEvaluator, LLMJudge; print('✅ Import OK')"

# 2. Verificar API Key
python -c "import os; print('✅ API Key OK' if os.getenv('OPENAI_API_KEY') else '❌ API Key Missing')"

# 3. Testar avaliação básica (sem API)
python scripts/run_evaluation.py --metrics-only

# 4. Testar LLM (com API) - apenas 5 samples
python scripts/run_evaluation.py --llm-only --samples 5

# 5. Ver resultados
ls -R logs/evaluation_*
```

Se todos os passos funcionarem: **✅ FASE 6 INSTALADA COM SUCESSO!**

---

## 📚 DOCUMENTAÇÃO COMPLETA

Para mais detalhes, consulte:

- **README.md**: Documentação completa e detalhada
- **Código**: Todos os arquivos têm docstrings e comentários
- **Exemplos**: Ver seção "COMO USAR" no README.md

---

## 🎯 PRÓXIMOS PASSOS

Após validar a Fase 6:

1. ✅ Testar avaliação básica
2. ✅ Testar LLM-as-judge
3. ✅ Testar comparação BERT vs GPT
4. ✅ Revisar resultados e métricas
5. ➡️ **FASE 7**: Docker + Docker Compose
6. ➡️ **FASE 8**: Testes (Unit + Integration + Load)

---

## 💬 SUPORTE

Se tiver dúvidas ou problemas:

1. Consulte README.md completo
2. Verifique os docstrings no código
3. Execute com --help: `python scripts/run_evaluation.py --help`

---

**✨ Boa sorte com a Fase 6!**

**Desenvolvido para o desafio técnico de IA Sênior** 🚀
