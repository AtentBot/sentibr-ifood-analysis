# 🚀 Quick Start - Fase 6: EVAL E LLM INTEGRATION

Guia rápido para começar a usar o sistema de avaliação e LLM integration do SentiBR.

## ⚡ Setup em 5 Minutos

### 1. Instalar Dependências

```bash
# Instalar dependências da Fase 6
pip install -r requirements-evaluation.txt
```

### 2. Configurar OpenAI API

```bash
# Copiar exemplo de configuração
cp .env.example .env

# Editar e adicionar sua API key
nano .env

# Ou exportar diretamente
export OPENAI_API_KEY='your-api-key-here'
```

### 3. Executar Avaliação Básica

```bash
# Avaliação BERT apenas (sem LLM)
python scripts/run_evaluation.py --samples 100

# Com LLM Judge (100 samples)
python scripts/run_evaluation.py --samples 1000 --use-llm --llm-samples 100
```

### 4. Ver Resultados

```bash
# Resultados salvos em:
ls -lh logs/evaluation/

# Visualizar relatório
cat logs/evaluation/final_report_*.txt
```

---

## 📊 Exemplos de Uso

### Exemplo 1: Avaliação Rápida BERT

```python
from src.evaluation import ModelEvaluator
import numpy as np

# Dados de exemplo
y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
y_pred = np.array([0, 1, 2, 1, 1, 1, 0, 2, 2])

# Avaliar
evaluator = ModelEvaluator(model_name="BERT Fine-tuned")
result = evaluator.evaluate(y_true, y_pred)

# Ver resultado
print(result.summary())
```

**Saída:**
```
╔══════════════════════════════════════════════════════════════╗
║              EVALUATION SUMMARY - BERT Fine-tuned              
╚══════════════════════════════════════════════════════════════╝

📊 Overall Metrics:
   • Accuracy:  0.6667
   • Precision: 0.6667
   • Recall:    0.6667
   • F1-Score:  0.6667
...
```

### Exemplo 2: LLM Judge em Um Sample

```python
from src.evaluation import LLMJudge

# Criar judge
judge = LLMJudge(model="gpt-4o-mini")

# Julgar uma predição
result = judge.judge_single(
    text="A pizza estava divina! Chegou quentinha e super rápido.",
    bert_pred="positivo"
)

# Ver resultado
print(f"LLM Judgment: {result.llm_judgment}")
print(f"Confidence: {result.confidence}")
print(f"Agrees with BERT: {result.agreement_with_bert}")
print(f"\nExplanation: {result.explanation}")
```

**Saída:**
```
LLM Judgment: positivo
Confidence: 0.95
Agrees with BERT: True

Explanation: O review expressa clara satisfação com a pizza...
```

### Exemplo 3: Batch Evaluation

```python
import pandas as pd
from src.evaluation import ModelEvaluator, LLMJudge

# Carregar dados
test_df = pd.read_csv("data/processed/test.csv").head(100)

# 1. Avaliar com BERT
evaluator = ModelEvaluator(model_name="BERT")
# ... fazer predições ...
bert_result = evaluator.evaluate(y_true, y_pred)

# 2. Avaliar com LLM
judge = LLMJudge()
llm_results, metrics = judge.judge_batch(
    texts=test_df['text'].tolist(),
    bert_preds=predictions_list,
    max_samples=50  # Avaliar apenas 50 para economizar
)

# 3. Ver métricas
judge.print_summary(metrics)
```

### Exemplo 4: Comparação Visual

```python
# Gerar confusion matrix
evaluator.plot_confusion_matrix(y_true, y_pred)

# Comparar múltiplos modelos
bert_result = evaluator_bert.evaluate(y_true, y_pred_bert)
gpt_result = evaluator_gpt.evaluate(y_true, y_pred_gpt)

evaluator.plot_metrics_comparison([bert_result, gpt_result])
```

---

## 🎯 Casos de Uso Comuns

### Caso 1: Avaliar Novo Modelo

Você treinou um novo modelo e quer avaliar:

```bash
# Fazer predições e salvar
python scripts/run_predictions.py --model models/new_model --output predictions.csv

# Avaliar
python scripts/run_evaluation.py --predictions predictions.csv
```

### Caso 2: Encontrar Casos Difíceis

Identificar onde o modelo erra mais:

```python
from src.evaluation import LLMJudge

judge = LLMJudge()
results, _ = judge.judge_batch(texts, bert_preds, max_samples=100)

# Filtrar edge cases
edge_cases = [r for r in results if r.is_edge_case]

print(f"Encontrados {len(edge_cases)} casos difíceis:")
for case in edge_cases[:5]:
    print(f"\nText: {case.text}")
    print(f"BERT: {case.bert_prediction}")
    print(f"LLM: {case.llm_judgment}")
    print(f"Why: {case.explanation[:100]}...")
```

### Caso 3: Validar Antes de Deploy

Antes de fazer deploy em produção:

```bash
# Avaliação completa no test set
python scripts/run_evaluation.py \
    --test-file data/processed/test.csv \
    --use-llm \
    --llm-samples 200

# Verificar se métricas atendem threshold
# Accuracy > 0.90 ✅
# F1-Score > 0.88 ✅
# LLM Agreement > 0.85 ✅
```

---

## 💰 Controle de Custos

### Estimativas de Custo (GPT-4o-mini)

| Samples | Tokens | Custo USD |
|---------|--------|-----------|
| 10 | ~3k | $0.001 |
| 50 | ~15k | $0.005 |
| 100 | ~30k | $0.015 |
| 500 | ~150k | $0.075 |
| 1000 | ~300k | $0.150 |

### Dicas para Economizar

1. **Use sampling inteligente**
   ```python
   # Avaliar apenas casos com baixa confiança
   low_confidence = [i for i, conf in enumerate(confidences) if conf < 0.7]
   judge.judge_batch(texts[low_confidence], preds[low_confidence])
   ```

2. **Cache resultados**
   ```python
   # LLM Judge salva automaticamente em JSON
   # Reutilize se precisar reprocessar
   ```

3. **Use batch processing**
   ```python
   # Mais eficiente que múltiplas chamadas individuais
   judge.judge_batch(texts, preds, max_samples=100)
   ```

---

## 🐛 Troubleshooting

### Problema: "OPENAI_API_KEY not found"

**Solução:**
```bash
export OPENAI_API_KEY='your-key'
# ou
echo "OPENAI_API_KEY=your-key" >> .env
```

### Problema: "Model not found"

**Solução:**
```bash
# Verificar se modelo existe
ls -lh models/bert_finetuned/

# Se não existe, treinar primeiro
python src/training/train.py
```

### Problema: "Rate limit exceeded"

**Solução:**
```python
# Adicionar sleep entre chamadas
import time
for text in texts:
    result = judge.judge_single(text, pred)
    time.sleep(1)  # Esperar 1s entre chamadas
```

### Problema: "Out of memory"

**Solução:**
```bash
# Reduzir número de samples
python scripts/run_evaluation.py --samples 500

# Ou processar em batches menores
```

---

## 📚 Próximos Passos

### Fase 7: Docker + Deploy
- Containerizar aplicação completa
- Docker Compose com todos os serviços
- Deploy em nuvem (GCP/AWS/Azure)

### Fase 8: Testes
- Unit tests com pytest
- Integration tests
- Load tests com Locust

### Fase 9: Documentação
- README épico
- Documentação de API
- Guias de uso

---

## 🎓 Recursos Adicionais

### Documentação
- [README da Evaluation](src/evaluation/README.md)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Scikit-learn Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)

### Exemplos
- [eval_suite.py](src/evaluation/eval_suite.py) - Ver função `main()`
- [llm_judge.py](src/evaluation/llm_judge.py) - Ver função `main()`

### Papers
- [Constitutional AI](https://arxiv.org/abs/2212.08073)
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)

---

## ✅ Checklist de Validação

Antes de considerar a Fase 6 completa, verifique:

- [ ] Evaluation Suite funcionando
- [ ] Métricas calculadas corretamente
- [ ] Confusion matrix gerada
- [ ] LLM Judge configurado
- [ ] OpenAI API funcionando
- [ ] Batch processing testado
- [ ] Custos sob controle
- [ ] Resultados salvos em JSON
- [ ] Relatórios gerados
- [ ] Documentação lida

---

## 🎉 Conclusão

Parabéns! Você tem agora um sistema completo de avaliação com:

✅ **Métricas clássicas** (Accuracy, F1, etc)  
✅ **LLM-as-Judge** para validação qualitativa  
✅ **Comparação BERT vs GPT**  
✅ **Análise de edge cases**  
✅ **Visualizações** profissionais  
✅ **Tracking de custos**  

**A Fase 6 está completa!** 🚀

Agora você pode:
- Avaliar qualquer modelo novo
- Validar predições antes de deploy
- Identificar casos difíceis
- Comparar diferentes abordagens
- Monitorar qualidade ao longo do tempo

**Próximo passo:** [Fase 7 - Docker + Deploy](../docker/README.md)

---

**Desenvolvido com ❤️ para o desafio técnico de IA Sênior**
