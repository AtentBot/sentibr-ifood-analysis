# 🚀 Guia de Início Rápido - Treinamento do BERT

Este guia te levará do zero ao modelo treinado em poucos passos.

## ⏱️ Tempo Estimado

- **Setup inicial**: 10-15 minutos
- **Teste rápido**: 5 minutos
- **Treinamento completo**: 30-90 minutos (com GPU) ou 4-8 horas (CPU)

## 📋 Pré-requisitos

- Python 3.10 ou superior
- 8GB+ de RAM
- 5GB+ de espaço em disco
- (Opcional mas recomendado) GPU com CUDA

## 🎯 Passo a Passo

### Passo 1: Setup do Ambiente

Execute o script de setup automático:

```bash
python scripts/setup_training.py
```

Este script irá:
- ✅ Verificar versão do Python
- ✅ Instalar todas as dependências
- ✅ Criar diretórios necessários
- ✅ Criar dados de teste
- ✅ (Opcional) Executar teste rápido

**Tempo: ~10 minutos**

### Passo 2: Preparar os Dados

#### Opção A: Dados de Teste Rápidos (Recomendado para começar)

```bash
# Criar dataset sintético pequeno (1000 reviews)
python src/data/quick_test_data.py

# Dividir em train/val/test
python src/data/split_dataset.py
```

**Tempo: ~1 minuto**

#### Opção B: Dataset Real B2W-Reviews01

```bash
# Baixar e processar dataset real (~130k reviews)
python src/data/load_data_v2.py

# Dividir em train/val/test
python src/data/split_dataset.py
```

**Tempo: ~5-10 minutos** (depende da conexão)

#### Opção C: Dataset Sintético iFood

```bash
# Requer OPENAI_API_KEY no .env
python src/data/generate_synthetic_data.py

# Dividir em train/val/test
python src/data/split_dataset.py
```

**Tempo: ~10-20 minutos** (depende da quantidade)

### Passo 3: Explorar os Dados (Opcional mas Recomendado)

```bash
jupyter notebook notebooks/01_eda.ipynb
```

Isso te ajudará a entender:
- Distribuição de sentimentos
- Qualidade dos textos
- Balanceamento das classes
- Características do dataset

**Tempo: ~15-30 minutos**

### Passo 4: Teste Rápido do Pipeline

Antes de treinar o modelo completo, teste se tudo funciona:

```bash
python src/training/quick_test.py --samples 100 --epochs 1
```

Você deve ver:
```
✅ Train Loss: ~1.0
✅ Train Acc: ~0.5-0.7
✅ Val Acc: ~0.5-0.7
✅ TESTE CONCLUÍDO COM SUCESSO!
```

**Tempo: ~2-5 minutos**

### Passo 5: Configurar Hiperparâmetros (Opcional)

Edite o arquivo `.env` para ajustar:

```bash
# Modelo
MODEL_NAME=neuralmind/bert-base-portuguese-cased
MAX_LENGTH=512
NUM_LABELS=3

# Treinamento
LEARNING_RATE=2e-5
BATCH_SIZE=16
NUM_EPOCHS=3
WARMUP_STEPS=500

# MLflow
MLFLOW_TRACKING_URI=file:./mlruns
```

### Passo 6: Treinar o Modelo 🚀

```bash
python src/training/train.py
```

O que vai acontecer:
1. ✅ Carregar dados
2. ✅ Inicializar BERT
3. ✅ Treinar por N épocas
4. ✅ Validar após cada época
5. ✅ Salvar melhor modelo
6. ✅ Registrar no MLflow

**Output esperado:**
```
🚀 INICIANDO TREINAMENTO
================================================
📊 Época 1/3
  Train Loss: 0.6543, Train Acc: 0.7234
  Val Loss: 0.5432, Val Acc: 0.7891
  ✅ Melhor modelo até agora!

📊 Época 2/3
  Train Loss: 0.4321, Train Acc: 0.8123
  Val Loss: 0.4567, Val Acc: 0.8234
  ✅ Melhor modelo até agora!

📊 Época 3/3
  Train Loss: 0.3456, Train Acc: 0.8567
  Val Loss: 0.4601, Val Acc: 0.8198
  ⚠️  Patience: 1/3

✅ TREINAMENTO CONCLUÍDO
Melhor Val Loss: 0.4567
Melhor Val Acc: 0.8234
💾 Modelo salvo em: models/bert_finetuned/
```

**Tempo:**
- Dataset pequeno (1k): ~5-10 minutos (GPU) / 30-60 minutos (CPU)
- Dataset médio (10k): ~15-30 minutos (GPU) / 2-4 horas (CPU)
- Dataset grande (100k+): ~60-90 minutos (GPU) / 6-12 horas (CPU)

### Passo 7: Avaliar o Modelo

```bash
python src/training/evaluate.py
```

Você verá:
- ✅ Métricas detalhadas (Accuracy, Precision, Recall, F1)
- ✅ Confusion Matrix
- ✅ Análise de erros
- ✅ Classification Report

**Output esperado:**
```
📊 MÉTRICAS DE AVALIAÇÃO
================================================
Accuracy:  0.8234
Precision: 0.8123
Recall:    0.8198
F1-Score:  0.8156

📊 Métricas por Classe:
  Negativo:
    Precision: 0.7856
    Recall:    0.8123
    F1-Score:  0.7987

  Neutro:
    Precision: 0.7234
    Recall:    0.6987
    F1-Score:  0.7108

  Positivo:
    Precision: 0.8789
    Recall:    0.8912
    F1-Score:  0.8850
```

**Tempo: ~2-5 minutos**

### Passo 8: Visualizar Experimentos (Opcional)

```bash
mlflow ui
```

Acesse: http://localhost:5000

Você verá:
- 📊 Gráficos de loss e accuracy
- 🔢 Todos os hiperparâmetros
- 📁 Modelos salvos
- 🔄 Comparação entre runs

## 🎉 Pronto!

Seu modelo está treinado e salvo em `models/bert_finetuned/`!

## 💡 Próximos Passos

1. **Teste o modelo interativamente:**
   ```bash
   python -c "from transformers import pipeline; nlp = pipeline('sentiment-analysis', model='models/bert_finetuned'); print(nlp('Adorei o produto!'))"
   ```

2. **Crie a API REST:**
   ```bash
   # Vá para a Fase 3
   python src/api/main.py
   ```

3. **Inicie o Frontend:**
   ```bash
   # Vá para a Fase 4
   streamlit run frontend/app.py
   ```

## 🐛 Problemas Comuns

### Erro: CUDA out of memory

**Solução:** Reduza o batch size no `.env`:
```bash
BATCH_SIZE=8  # ou até 4
```

### Erro: Dataset não encontrado

**Solução:** Execute os scripts de dados:
```bash
python src/data/quick_test_data.py
python src/data/split_dataset.py
```

### Modelo não aprende (loss não diminui)

**Verifique:**
- [ ] Learning rate (tente 3e-5 ou 1e-5)
- [ ] Dataset balanceado
- [ ] Labels corretos (0, 1, 2)
- [ ] Batch size adequado

### Erro: ModuleNotFoundError

**Solução:** Reinstale dependências:
```bash
pip install -r requirements.txt
```

## 📊 Benchmarks

### Dataset de Teste (1k reviews)
- **Tempo de treinamento:** 5-10 min (GPU) / 30-60 min (CPU)
- **Accuracy esperada:** 80-85%
- **F1-Score esperado:** 0.75-0.80

### Dataset Real (130k reviews)
- **Tempo de treinamento:** 60-90 min (GPU) / 6-8 horas (CPU)
- **Accuracy esperada:** 85-90%
- **F1-Score esperado:** 0.82-0.88

## 🎓 Dicas Avançadas

### 1. Usar GPU no Google Colab

Se não tem GPU local:

1. Abra [Google Colab](https://colab.research.google.com)
2. Runtime → Change runtime type → GPU
3. Clone o repositório:
   ```python
   !git clone https://github.com/seu-usuario/sentibr-ifood-analysis
   %cd sentibr-ifood-analysis
   ```
4. Execute os scripts normalmente

### 2. Ajustar para seu dataset

Se usar seu próprio dataset, ajuste em `src/config.py`:
- `text_column`: nome da coluna com o texto
- `label_column`: nome da coluna com o label
- `num_labels`: número de classes

### 3. Salvar checkpoints intermediários

Edite `src/training/train.py` e adicione:
```python
if epoch % 2 == 0:
    checkpoint_path = f"models/checkpoint_epoch_{epoch}"
    self.save_model(checkpoint_path)
```

### 4. Hyperparameter Tuning

Para encontrar os melhores hiperparâmetros automaticamente:
```bash
# TODO: Adicionar script de tuning com Optuna
python src/training/hyperparameter_tuning.py
```

## 📚 Recursos Adicionais

- [Documentação do Transformers](https://huggingface.co/docs/transformers/)
- [Fine-tuning BERT Tutorial](https://huggingface.co/docs/transformers/training)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [MLflow Tracking](https://www.mlflow.org/docs/latest/tracking.html)

## ❓ Ainda com Dúvidas?

1. Leia o [README principal](../README.md)
2. Consulte o [README do módulo de treinamento](src/training/README.md)
3. Veja os [notebooks de exemplo](notebooks/)
4. Abra uma issue no GitHub

---

**Última atualização:** Novembro 2024
**Versão:** 1.0.0
