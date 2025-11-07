# 🎯 FASE 6 - EVAL E LLM INTEGRATION

Sistema completo de avaliação e integração com LLMs para o SentiBR.

## 📋 O Que Foi Criado

### ✅ **Evaluation Suite**
- Framework completo de avaliação de modelos
- Métricas clássicas (Accuracy, Precision, Recall, F1)
- Confusion Matrix e visualizações
- Análise detalhada de erros
- Relatórios em JSON e texto

### ✅ **LLM-as-Judge**
- Avaliação qualitativa com GPT-4o-mini
- Comparação BERT vs GPT
- Identificação de casos edge
- Análise por aspectos (comida, entrega, serviço, preço)
- Explicações detalhadas

### ✅ **Integração OpenAI**
- Cliente OpenAI configurado
- Rate limiting e error handling
- Tracking de custos e tokens
- Suporte a batch processing

---

## 🏗️ Estrutura de Arquivos

```
src/evaluation/
├── __init__.py              # Módulo Python
├── eval_suite.py            # Framework de avaliação
├── llm_judge.py             # LLM-as-Judge
└── README.md                # Esta documentação

logs/evaluation/             # Resultados de avaliação
logs/llm_judge/              # Resultados do LLM Judge
```

---

## 🚀 Quick Start

### 1️⃣ **Configurar OpenAI API Key**

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Ou crie um arquivo `.env`:

```bash
OPENAI_API_KEY=your-api-key-here
```

### 2️⃣ **Instalar Dependências**

```bash
pip install openai pandas matplotlib seaborn tqdm
```

### 3️⃣ **Executar Avaliação Básica**

```python
from src.evaluation import ModelEvaluator
import numpy as np

# Criar dados de teste
y_true = np.array([0, 1, 2, 0, 1, 2])
y_pred = np.array([0, 1, 2, 1, 1, 2])

# Criar avaliador
evaluator = ModelEvaluator(
    model_name="BERT Fine-tuned",
    label_names=['negativo', 'neutro', 'positivo']
)

# Avaliar
result = evaluator.evaluate(y_true, y_pred)

# Mostrar resultados
print(result.summary())

# Salvar
result.to_json("evaluation_results.json")
```

### 4️⃣ **Usar LLM-as-Judge**

```python
from src.evaluation import LLMJudge

# Criar judge
judge = LLMJudge(model="gpt-4o-mini")

# Julgar uma predição
result = judge.judge_single(
    text="A comida estava deliciosa!",
    bert_pred="positivo"
)

# Ver resultado
print(result.explanation)
print(f"Acordo com BERT: {result.agreement_with_bert}")
print(f"Confiança: {result.confidence}")
```

---

## 📊 Exemplo Completo

### Avaliação + LLM Judge

```python
import pandas as pd
from src.evaluation import ModelEvaluator, LLMJudge

# 1. Carregar dados de teste
test_data = pd.read_csv("data/processed/test.csv")

# 2. Fazer predições com BERT
from src.api.inference import SentimentPredictor
predictor = SentimentPredictor()

predictions = []
for text in test_data['text']:
    pred = predictor.predict(text)
    predictions.append(pred['sentiment'])

# 3. Avaliar com métricas clássicas
evaluator = ModelEvaluator(model_name="BERT Fine-tuned")
result = evaluator.evaluate(
    y_true=test_data['label'].values,
    y_pred=predictions,
    texts=test_data['text'].tolist()
)

print(result.summary())
evaluator.plot_confusion_matrix(test_data['label'].values, predictions)

# 4. Avaliar com LLM Judge (sample de 100)
judge = LLMJudge()
llm_results, metrics = judge.judge_batch(
    texts=test_data['text'].tolist()[:100],
    bert_preds=predictions[:100],
    max_samples=100
)

judge.print_summary(metrics)

# 5. Salvar tudo
result.to_json("logs/evaluation/bert_evaluation.json")
```

---

## 📈 Métricas Calculadas

### **Evaluation Suite**

1. **Overall Metrics**
   - Accuracy
   - Precision (macro e weighted)
   - Recall (macro e weighted)
   - F1-Score (macro e weighted)

2. **Per-Class Metrics**
   - Precision por classe
   - Recall por classe
   - F1-Score por classe
   - Support (número de samples)

3. **Error Analysis**
   - Total de erros
   - Taxa de erro
   - Distribuição de erros por tipo
   - Exemplos de erros

4. **Visualizações**
   - Confusion Matrix
   - Comparação entre modelos
   - Distribuição de predições

### **LLM Judge**

1. **Agreement Rates**
   - Taxa de acordo com BERT
   - Taxa de acordo com GPT
   - Análise de discordâncias

2. **Edge Cases**
   - Identificação de casos difíceis
   - Taxa de edge cases
   - Análise de ambiguidade

3. **Aspect Analysis**
   - Sentimento por aspecto (comida, entrega, etc)
   - Distribuição de aspectos mencionados
   - Correlação entre aspectos

4. **Confidence**
   - Confiança média do LLM
   - Distribuição de confiança
   - Correlação com dificuldade

---

## 🎯 Casos de Uso

### 1. **Avaliar Modelo Novo**

```python
evaluator = ModelEvaluator(model_name="BERTimbau v2")
result = evaluator.evaluate(y_true, y_pred, texts)
evaluator.plot_confusion_matrix(y_true, y_pred)
report = evaluator.generate_report(result)
```

### 2. **Comparar Modelos**

```python
# Avaliar BERT
bert_result = evaluator_bert.evaluate(y_true, y_pred_bert)

# Avaliar GPT
gpt_result = evaluator_gpt.evaluate(y_true, y_pred_gpt)

# Comparar
evaluator.plot_metrics_comparison([bert_result, gpt_result])
```

### 3. **Encontrar Casos Difíceis**

```python
judge = LLMJudge()
results, metrics = judge.judge_batch(texts, bert_preds)

# Filtrar edge cases
edge_cases = [r for r in results if r.is_edge_case]
print(f"Encontrados {len(edge_cases)} casos difíceis")

for case in edge_cases[:5]:
    print(f"Text: {case.text}")
    print(f"Explanation: {case.explanation}\n")
```

### 4. **Análise de Aspectos**

```python
results, _ = judge.judge_batch(texts, bert_preds)

# Agregar por aspecto
aspect_sentiments = {
    'food': [],
    'delivery': [],
    'service': [],
    'price': []
}

for result in results:
    for aspect, sentiment in result.aspects.items():
        if sentiment != 'não mencionado':
            aspect_sentiments[aspect].append(sentiment)

# Mostrar distribuição
for aspect, sentiments in aspect_sentiments.items():
    print(f"\n{aspect.upper()}:")
    print(f"  Positivo: {sentiments.count('positivo')}")
    print(f"  Neutro:   {sentiments.count('neutro')}")
    print(f"  Negativo: {sentiments.count('negativo')}")
```

---

## 💰 Custos do LLM Judge

### **GPT-4o-mini Pricing (Nov 2024)**

- **Input**: $0.15 / 1M tokens
- **Output**: $0.60 / 1M tokens

### **Estimativas**

Para 100 reviews de ~100 palavras cada:

- **Tokens por review**: ~300-500 tokens
- **Total de tokens**: 30-50k tokens
- **Custo estimado**: **$0.02 - $0.04**

Para 1000 reviews:

- **Custo estimado**: **$0.20 - $0.40**

### **Dicas para Reduzir Custos**

1. **Sample estrategicamente**: Não precisa avaliar todos os casos
2. **Use cache**: Reutilize avaliações quando possível
3. **Batch processing**: Processe em lotes para economia
4. **Filtre por confiança**: Avalie apenas casos com baixa confiança do BERT

---

## 🔧 Configuração Avançada

### **Customizar LLM Judge**

```python
judge = LLMJudge(
    model="gpt-4o-mini",           # Modelo a usar
    temperature=0.1,               # Criatividade (0-1)
    max_tokens=1000,               # Máx tokens na resposta
    output_dir=Path("custom/dir")  # Dir para salvar
)
```

### **Customizar Prompts**

```python
# Editar prompts em llm_judge.py
LLMJudge.SYSTEM_PROMPT = "Seu prompt customizado..."
LLMJudge.USER_PROMPT_TEMPLATE = "Template customizado..."
```

### **Adicionar Métricas Customizadas**

```python
# Em eval_suite.py
def custom_metric(y_true, y_pred):
    # Sua lógica aqui
    return score

# Adicionar ao evaluator
evaluator.custom_metrics['my_metric'] = custom_metric
```

---

## 📊 Outputs Gerados

### **Evaluation Suite**

```
logs/evaluation/
├── bert_evaluation.json              # Resultados em JSON
├── evaluation_report.txt             # Relatório em texto
├── confusion_matrix_BERT.png         # Matriz de confusão
└── metrics_comparison.png            # Comparação entre modelos
```

### **LLM Judge**

```
logs/llm_judge/
├── judgments_20241106_143022.json    # Julgamentos individuais
└── metrics_20241106_143022.json      # Métricas agregadas
```

---

## 🎓 Conceitos Avançados

### **LLM-as-Judge**

O conceito de usar LLMs para avaliar outputs de outros modelos é poderoso porque:

1. **Avaliação Qualitativa**: Vai além de métricas numéricas
2. **Nuances**: Captura sutilezas que métricas não capturam
3. **Explicabilidade**: Fornece razões para as avaliações
4. **Flexibilidade**: Pode avaliar múltiplos aspectos
5. **Escalabilidade**: Mais barato que avaliação humana

### **Quando Usar LLM Judge**

✅ **Use quando:**
- Precisa entender WHY o modelo errou
- Quer avaliar qualidade qualitativa
- Tem budget para API calls
- Precisa identificar edge cases
- Quer análise de múltiplos aspectos

❌ **Não use quando:**
- Precisa apenas de métricas quantitativas
- Budget é muito limitado
- Precisa de avaliação instantânea
- Dataset é muito grande (>10k samples)

### **BERT vs GPT Trade-offs**

| Aspecto | BERT Fine-tuned | GPT-4o-mini |
|---------|----------------|-------------|
| **Latência** | < 100ms | ~1-2s |
| **Custo** | $0 (após treino) | $0.20-0.40 / 1k reviews |
| **Precisão** | 92-95% | 94-97% |
| **Contexto** | Limitado (512 tokens) | Extenso (128k tokens) |
| **Explicabilidade** | Baixa | Alta |
| **Customização** | Alta (fine-tuning) | Média (prompts) |
| **Produção** | Ideal para alto volume | Ideal para casos críticos |

### **Estratégia Híbrida (Recomendada)**

```python
# 1. BERT para todos os casos
bert_pred = bert_model.predict(text)

# 2. Se confiança baixa, usar GPT
if bert_pred['confidence'] < 0.70:
    gpt_pred = gpt_model.predict(text)
    final_pred = gpt_pred
else:
    final_pred = bert_pred

# 3. LLM Judge em sample aleatório para monitoramento
if random.random() < 0.01:  # 1% de sample
    judge.judge_single(text, final_pred)
```

---

## 🧪 Testing

### **Testar Evaluation Suite**

```bash
python -m pytest tests/unit/test_eval_suite.py -v
```

### **Testar LLM Judge**

```bash
# Requer OPENAI_API_KEY
export OPENAI_API_KEY='your-key'
python src/evaluation/llm_judge.py
```

---

## 📚 Referências

### **Papers**

- [Constitutional AI](https://arxiv.org/abs/2212.08073) - Anthropic
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)
- [BERT for Sentiment Analysis](https://arxiv.org/abs/1810.04805)

### **Recursos**

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Scikit-learn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [MLflow Evaluation](https://mlflow.org/docs/latest/models.html#model-evaluation)

### **Exemplos de Prompts**

- [Awesome Prompts](https://github.com/f/awesome-chatgpt-prompts)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## 🎯 Próximos Passos

Após completar a Fase 6:

1. **FASE 7**: Docker + Deploy Completo
2. **FASE 8**: Testes (Unit + Integration + Load)
3. **FASE 9**: Documentação Final

### **Melhorias Futuras**

- [ ] Suporte a outros LLMs (Claude, Gemini)
- [ ] Active Learning com LLM Judge
- [ ] Dashboard interativo de avaliação
- [ ] A/B testing framework
- [ ] Continuous evaluation pipeline

---

## 🎉 Resumo

✅ **Evaluation Suite** completo com métricas clássicas  
✅ **LLM-as-Judge** com GPT-4o-mini  
✅ **Análise de aspectos** (comida, entrega, etc)  
✅ **Comparação BERT vs GPT** side-by-side  
✅ **Identificação de edge cases**  
✅ **Explicações detalhadas**  
✅ **Visualizações** e relatórios  
✅ **Tracking de custos** e tokens  

**FASE 6 - 100% COMPLETA!** 🚀

---

**Desenvolvido com ❤️ para o desafio técnico de IA Sênior**

🎯 Evaluation + 🤖 LLM Integration = 💪 Production-Ready AI!
