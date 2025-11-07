# 🎓 Módulo de Treinamento - SentiBR

Este módulo contém todos os scripts necessários para treinar o modelo BERT para análise de sentimento.

## 📁 Estrutura

```
src/training/
├── __init__.py           # Módulo Python
├── dataset.py            # Dataset PyTorch customizado
├── train.py              # Script principal de treinamento
├── evaluate.py           # Script de avaliação detalhada
├── quick_test.py         # Teste rápido do pipeline
└── README.md             # Esta documentação
```

## 🚀 Quick Start

### 1. Preparar os Dados

Antes de treinar, você precisa ter os dados preparados e divididos:

```bash
# Opção A: Carregar dados reais
python src/data/load_data_v2.py
python src/data/split_dataset.py

# Opção B: Criar dados de teste rápidos
python src/data/quick_test_data.py
python src/data/split_dataset.py
```

### 2. Teste Rápido (Recomendado)

Antes de treinar o modelo completo, teste o pipeline:

```bash
python src/training/quick_test.py --samples 100 --epochs 1
```

Isso irá:
- ✅ Verificar se o ambiente está configurado corretamente
- ✅ Testar se o modelo carrega
- ✅ Executar 1 época de treinamento em 100 samples
- ✅ Validar que tudo funciona

**Tempo estimado: 2-5 minutos**

### 3. Treinamento Completo

Quando o teste passar, execute o treinamento completo:

```bash
python src/training/train.py
```

**Tempo estimado:**
- CPU: 4-8 horas (dependendo do dataset)
- GPU: 30-90 minutos

### 4. Avaliação Detalhada

Após o treinamento, avalie o modelo:

```bash
python src/training/evaluate.py
```

Isso irá:
- Calcular todas as métricas (accuracy, precision, recall, F1)
- Gerar confusion matrix
- Analisar os erros do modelo
- Salvar relatório completo

## 📊 Arquivos Gerados

Após o treinamento, você terá:

```
models/bert_finetuned/
├── config.json               # Configuração do modelo
├── pytorch_model.bin         # Pesos do modelo
├── tokenizer_config.json     # Configuração do tokenizer
├── vocab.txt                 # Vocabulário
├── metrics.json              # Métricas de validação
└── training_config.json      # Hiperparâmetros usados

mlruns/                       # Experimentos MLflow
└── 0/
    └── <run_id>/
        ├── metrics/          # Métricas por época
        ├── params/           # Hiperparâmetros
        └── artifacts/        # Artefatos salvos

logs/
├── confusion_matrix.png      # Matriz de confusão
└── evaluation_report.json    # Relatório completo
```

## ⚙️ Configuração

As configurações de treinamento estão em `src/config.py`:

```python
# Modelo
MODEL_NAME = "neuralmind/bert-base-portuguese-cased"
NUM_LABELS = 3  # positivo, neutro, negativo
MAX_LENGTH = 512

# Treinamento
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
NUM_EPOCHS = 3
WARMUP_STEPS = 500
WEIGHT_DECAY = 0.01

# Early Stopping
PATIENCE = 3  # Parar após 3 épocas sem melhora
```

Você pode ajustar essas configurações no arquivo `.env` ou diretamente no `config.py`.

## 🔧 Hiperparâmetros Recomendados

### Para datasets pequenos (< 10k samples):
```python
LEARNING_RATE = 3e-5
BATCH_SIZE = 16
NUM_EPOCHS = 5
```

### Para datasets médios (10k-100k samples):
```python
LEARNING_RATE = 2e-5
BATCH_SIZE = 32
NUM_EPOCHS = 3
```

### Para datasets grandes (> 100k samples):
```python
LEARNING_RATE = 2e-5
BATCH_SIZE = 64
NUM_EPOCHS = 2
```

## 🐛 Troubleshooting

### Erro: CUDA out of memory

**Solução 1: Reduzir batch size**
```bash
# No .env
BATCH_SIZE=8
```

**Solução 2: Reduzir max_length**
```bash
# No .env
MAX_LENGTH=256
```

**Solução 3: Usar gradient accumulation** (adicionar no código se necessário)

### Erro: Dataset não encontrado

```bash
# Execute primeiro:
python src/data/quick_test_data.py
python src/data/split_dataset.py
```

### Erro: MLflow tracking URI

```bash
# No .env
MLFLOW_TRACKING_URI=file:./mlruns
```

### Modelo não aprende (loss não diminui)

Verifique:
- [ ] Learning rate muito baixo? Tente 3e-5
- [ ] Learning rate muito alto? Tente 1e-5
- [ ] Dataset balanceado? Use class weights se necessário
- [ ] Labels corretos? Verifique no EDA

## 📈 Monitoramento com MLflow

Visualize os experimentos:

```bash
mlflow ui
```

Acesse: http://localhost:5000

Você verá:
- 📊 Gráficos de loss e accuracy por época
- 🔢 Todos os hiperparâmetros usados
- 📁 Modelos e artefatos salvos
- 🔄 Comparação entre diferentes runs

## 🎯 Métricas de Sucesso

Um bom modelo deve ter:

- ✅ **Accuracy > 0.80** (80%)
- ✅ **F1-Score > 0.75** por classe
- ✅ **Precision e Recall balanceados** (diferença < 0.1)
- ✅ **Confusion matrix** sem confusões extremas

Se as métricas estiverem abaixo:
1. Verifique a qualidade dos dados (EDA)
2. Tente diferentes hiperparâmetros
3. Aumente o tamanho do dataset
4. Considere data augmentation
5. Experimente diferentes modelos base

## 🚀 Próximos Passos

Após treinar o modelo com sucesso:

1. ✅ Avaliar detalhadamente (`evaluate.py`)
2. ✅ Criar API REST (Fase 3)
3. ✅ Integrar com frontend (Fase 4)
4. ✅ Configurar monitoring (Fase 5)

## 📚 Recursos Adicionais

- [Documentação do Transformers](https://huggingface.co/docs/transformers/)
- [Fine-tuning BERT](https://huggingface.co/docs/transformers/training)
- [MLflow Tracking](https://www.mlflow.org/docs/latest/tracking.html)
- [PyTorch Lightning](https://pytorch-lightning.readthedocs.io/) (alternativa avançada)

## 💡 Dicas Avançadas

### 1. Usar GPU na Colab

```python
# No Colab, sempre use GPU:
# Runtime > Change runtime type > GPU

# Verificar:
import torch
print(torch.cuda.is_available())  # Deve ser True
```

### 2. Salvar checkpoints intermediários

```python
# Adicionar no train.py:
if epoch % 2 == 0:  # A cada 2 épocas
    checkpoint_path = f"models/checkpoint_epoch_{epoch}"
    trainer.save_model(checkpoint_path)
```

### 3. Usar Learning Rate Finder

```python
# Experimentar diferentes LRs automaticamente
from torch.optim.lr_scheduler import ReduceLROnPlateau

scheduler = ReduceLROnPlateau(optimizer, mode='min', patience=1)
```

### 4. Data Augmentation

```python
# Adicionar augmentation no dataset.py
import nlpaug.augmenter.word as naw

aug = naw.SynonymAug(aug_src='wordnet')
augmented_text = aug.augment(text)
```

## 🤝 Contribuindo

Para adicionar novas features ao módulo de treinamento:

1. Adicione testes unitários
2. Documente no README
3. Atualize o `requirements.txt` se necessário
4. Teste com `quick_test.py`

## 📧 Suporte

Problemas? Abra uma issue no GitHub com:
- Logs completos do erro
- Configurações usadas (.env)
- Informações do sistema (GPU, RAM, etc)
