# 🚀 SentiBR - Guia Rápido de Instalação

## 📦 Você baixou o projeto SentiBR!

### Passo 1: Extrair o projeto

```bash
# Se baixou o .tar.gz
tar -xzf sentibr-ifood-analysis.tar.gz
cd sentibr-ifood-analysis

# Ou se baixou a pasta diretamente
cd sentibr-ifood-analysis
```

### Passo 2: Executar o Quickstart

```bash
# Linux/Mac
chmod +x scripts/quickstart.sh
./scripts/quickstart.sh

# Ou manualmente:
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Passo 3: Configurar .env

```bash
# Copiar template
cp .env.example .env

# Editar com suas keys
nano .env  # ou vim, code, etc
```

**Importante:** Configure pelo menos:
- `OPENAI_API_KEY` (se for usar GPT)
- `MODEL_NAME` (já está configurado)

### Passo 4: Verificar Setup

```bash
python scripts/check_setup.py
```

### Passo 5: Carregar Dataset

```bash
# Ative o ambiente virtual primeiro!
source venv/bin/activate  # Windows: venv\Scripts\activate

# Carregar B2W-Reviews01
python src/data/load_data.py
```

### Passo 6: Explorar os Dados

```bash
# Iniciar Jupyter
jupyter notebook notebooks/01_eda.ipynb

# Ou JupyterLab
jupyter lab
```

---

## 📚 Estrutura do Projeto

```
sentibr-ifood-analysis/
├── 📁 data/                    → Dados
├── 📁 models/                  → Modelos treinados
├── 📁 src/                     → Código fonte
│   ├── data/                   → Scripts de dados
│   ├── training/               → Training pipeline
│   ├── api/                    → FastAPI
│   └── ...
├── 📁 frontend/                → Streamlit
├── 📁 notebooks/               → Jupyter notebooks
├── 📁 scripts/                 → Scripts úteis
│   ├── quickstart.sh           ← COMECE AQUI!
│   └── check_setup.py          ← Verifica ambiente
├── README.md                   → Documentação completa
├── PROGRESS.md                 → Status do projeto
├── requirements.txt            → Dependências
└── .env.example                → Template de config
```

---

## 🎯 Próximos Passos

1. **HOJE:** Setup + carregar dados + EDA
2. **AMANHÃ:** Começar fine-tuning do BERT
3. **SEMANA:** API + Frontend + Monitoramento

---

## 📖 Documentação Completa

Leia o **README.md** para documentação detalhada!

---

## 🆘 Problemas?

1. `python scripts/check_setup.py` - Verifica problemas
2. Leia README.md - Seção de troubleshooting
3. Verifique se Python 3.10+ está instalado

---

## 🎉 Boa sorte!

Você tem um projeto de ML/MLOps profissional pronto!

**Desenvolvido com ❤️ para o desafio técnico**
