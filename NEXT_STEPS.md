# 🚀 PRÓXIMOS PASSOS - FASE 1: Dataset e EDA

Status: ✅ Setup completo | 🟡 Carregar dados | ⚪ EDA | ⚪ Training

---

## 📊 OPÇÃO A: Dataset Completo B2W-Reviews01 (Recomendado)

### Carregar ~130k reviews reais de e-commerce brasileiro

```bash
# Ative o ambiente virtual
source venv/bin/activate  # ou venv\Scripts\activate no Windows

# Execute o script
python src/data/load_data.py
```

**Tempo estimado:** 5-10 minutos  
**Tamanho:** ~50 MB  
**O que faz:**
- ✅ Baixa B2W-Reviews01 do HuggingFace
- ✅ Processa e limpa os textos
- ✅ Cria labels de sentimento
- ✅ Cria labels de aspectos
- ✅ Salva em `data/processed/processed_reviews.csv`

---

## 📊 OPÇÃO B: Dataset de Teste Rápido (Para começar já!)

### Criar 1000 reviews sintéticas para testar o pipeline

```bash
# Execute o script de teste
python src/data/quick_test_data.py
```

**Tempo estimado:** 10 segundos  
**Tamanho:** Pequeno (~100 KB)  
**O que faz:**
- ✅ Cria 1000 reviews sintéticas
- ✅ Distribuição: 45% positivo, 35% negativo, 20% neutro
- ✅ Salva em `data/processed/processed_reviews.csv`

**💡 Use esta opção se quiser:**
- Testar o sistema rapidamente
- Verificar se tudo funciona antes do dataset completo
- Fazer desenvolvimento sem esperar downloads

---

## 📓 PASSO 2: Análise Exploratória (EDA)

Após carregar os dados (Opção A ou B), explore-os:

```bash
# Iniciar Jupyter
jupyter notebook notebooks/01_eda.ipynb

# Ou JupyterLab
jupyter lab
```

**O notebook vai mostrar:**
- 📊 Distribuição de sentimentos
- 📏 Estatísticas de comprimento
- ☁️ WordClouds por sentimento
- 📋 Análise de aspectos
- 😊 Análise de emojis
- 📝 Exemplos de reviews

---

## 🎯 PASSO 3: Preparar para Treinamento

Depois da EDA, você vai precisar de:

### 3.1 Split Train/Val/Test

Vou criar um script para isso:

```bash
python src/data/split_dataset.py
```

Isso vai criar:
- `data/processed/train.csv` (70%)
- `data/processed/val.csv` (15%)
- `data/processed/test.csv` (15%)

### 3.2 Verificar Balanceamento

Se as classes estiverem muito desbalanceadas, considere:
- Usar `class_weights` no treinamento
- Técnicas de balanceamento (SMOTE, undersampling)

---

## 📋 Checklist FASE 1

- [x] ✅ Setup do projeto
- [x] ✅ Dependências instaladas
- [x] ✅ Diretórios criados
- [x] ✅ .env configurado
- [ ] 🟡 Carregar dataset (escolha Opção A ou B)
- [ ] ⚪ Executar EDA no notebook
- [ ] ⚪ Split train/val/test
- [ ] ⚪ Documentar insights

---

## 🔄 FLUXO RECOMENDADO

```
1. Quick Test (Opção B) 
   ↓
2. EDA Notebook
   ↓
3. Verificar que tudo funciona
   ↓
4. Dataset Completo (Opção A)
   ↓
5. EDA completo
   ↓
6. Preparar para training (FASE 2)
```

Ou se preferir ir direto:

```
1. Dataset Completo (Opção A)
   ↓
2. EDA Notebook
   ↓
3. Preparar para training (FASE 2)
```

---

## 💡 Comandos Rápidos

```bash
# Teste rápido (10 segundos)
python src/data/quick_test_data.py

# Dataset completo (5-10 min)
python src/data/load_data.py

# EDA
jupyter notebook notebooks/01_eda.ipynb

# Verificar o que foi criado
ls -lh data/processed/
```

---

## 🆘 Troubleshooting

### Erro de import de datasets/transformers?
```bash
pip install datasets transformers --upgrade
```

### Erro de conexão ao HuggingFace?
```bash
# Tente novamente ou use o quick_test_data.py
python src/data/quick_test_data.py
```

### Jupyter não abre?
```bash
pip install jupyter notebook ipykernel
python -m ipykernel install --user --name=venv
```

---

## 📈 Após completar FASE 1

Você estará pronto para **FASE 2: Fine-tuning do BERT**!

---

**Dúvidas? Consulte README.md ou PROGRESS.md** 📚
