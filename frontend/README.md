# 🍔 SentiBR Frontend - Interface Streamlit

Interface web interativa para análise de sentimentos de reviews do iFood.

## 📋 Visão Geral

O frontend do SentiBR é uma aplicação Streamlit multi-página que oferece:

- 🏠 **Home**: Visão geral do projeto e estatísticas
- 📝 **Análise**: Interface para análise de sentimentos individual
- 📊 **Métricas**: Dashboard com métricas em tempo real
- 💬 **Feedback**: Sistema de validação e melhoria contínua
- 🔍 **Monitor**: Detecção de drift e monitoramento de saúde

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- API do SentiBR rodando em `http://localhost:8000`

### Instalação

```bash
# Instalar dependências
cd frontend
pip install -r requirements.txt

# Iniciar aplicação
streamlit run app.py
```

A aplicação estará disponível em: `http://localhost:8501`

## 📁 Estrutura de Arquivos

```
frontend/
├── app.py                          # Página principal (Home)
├── requirements.txt                # Dependências Python
│
├── .streamlit/
│   └── config.toml                # Configuração e tema
│
├── assets/
│   └── ifood_logo.jpeg           # Logo do iFood
│
├── components/
│   └── ui_components.py          # Componentes reutilizáveis
│
└── pages/
    ├── 1_📝_Análise.py           # Análise de sentimentos
    ├── 2_📊_Métricas.py          # Dashboard de métricas
    ├── 3_💬_Feedback.py          # Sistema de feedback
    └── 4_🔍_Monitor.py           # Monitoramento e drift
```

## 🎨 Features

### 1. Home (app.py)
- Visão geral do projeto
- Estatísticas gerais
- Arquitetura do sistema
- Tech stack
- Quick start guide

### 2. Análise de Sentimentos
- **Análise Individual**: Digite ou cole um review
- **Comparação BERT vs GPT**: Compare modelos lado a lado
- **Análise em Lote**: Processe múltiplos reviews
- **Explicabilidade**: Visualize palavras importantes
- **Análise por Aspectos**: Sentimento por categoria

### 3. Dashboard de Métricas
- **Tendências**: Predições ao longo do tempo
- **Performance**: Latência e SLA
- **Qualidade**: Distribuição de confiança
- **Heatmaps**: Padrões de uso por hora/dia

### 4. Sistema de Feedback
- **Validação**: Confirme ou corrija predições
- **Validação em Lote**: Revise múltiplas predições
- **Histórico**: Acompanhe feedbacks enviados
- **Estatísticas**: Impacto do feedback no modelo

### 5. Monitoramento
- **Data Drift**: Detecção de mudanças na distribuição
- **Model Performance**: Métricas ao longo do tempo
- **Alertas**: Sistema de notificações
- **System Metrics**: CPU, memória, etc.

## 🛠️ Componentes Reutilizáveis

O arquivo `components/ui_components.py` contém componentes customizados:

### `sentiment_badge(sentiment, confidence, size)`
Badge colorido de sentimento com ícone e confiança.

```python
from components.ui_components import sentiment_badge

sentiment_badge("positive", 0.95, size="medium")
```

### `metric_card(title, value, delta, icon, color)`
Card de métrica estilizado.

```python
from components.ui_components import metric_card

metric_card(
    title="Total de Predições",
    value="150K+",
    delta="+5.2K hoje",
    icon="📝",
    color="#EA1D2C"
)
```

### `confidence_gauge(confidence, sentiment)`
Gauge visual de confiança.

```python
from components.ui_components import confidence_gauge

fig = confidence_gauge(0.95, "positive")
st.plotly_chart(fig)
```

### `comparison_table(bert_result, gpt_result)`
Tabela comparativa BERT vs GPT.

```python
from components.ui_components import comparison_table

comparison_table(bert_result, gpt_result)
```

### `show_explainability(text, word_importance)`
Visualização de explicabilidade (LIME/SHAP style).

```python
from components.ui_components import show_explainability

word_importance = {
    "excelente": 0.9,
    "péssimo": -0.9,
    "bom": 0.6
}

show_explainability(review_text, word_importance)
```

## 🎨 Tema e Estilo

O frontend usa o tema customizado do iFood:

- **Primary Color**: `#EA1D2C` (Vermelho iFood)
- **Background**: `#FFFFFF`
- **Secondary Background**: `#F5F5F5`
- **Text**: `#262626`

Configurado em: `.streamlit/config.toml`

## 🔗 Integração com API

O frontend se comunica com a API REST via:

```python
API_BASE_URL = "http://localhost:8000/api/v1"

# Endpoints principais
GET  /health              # Health check
POST /predict             # Predição individual
POST /predict/compare     # Comparação BERT vs GPT
POST /predict/batch       # Predição em lote
POST /feedback            # Enviar feedback
GET  /metrics             # Métricas Prometheus
```

## 🚀 Deploy

### Local
```bash
streamlit run frontend/app.py --server.port 8501
```

### Docker
```bash
docker build -t sentibr-frontend -f docker/Dockerfile.frontend .
docker run -p 8501:8501 sentibr-frontend
```

### Produção
Para deploy em produção, considere:

- **Streamlit Cloud**: Deploy direto do GitHub
- **Docker + Kubernetes**: Para maior controle
- **AWS/GCP/Azure**: Serviços gerenciados

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# API Configuration
API_HOST=http://localhost
API_PORT=8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Config.toml Customizado

Edite `.streamlit/config.toml` para personalizar:

```toml
[theme]
primaryColor = "#EA1D2C"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"

[server]
port = 8501
headless = true
```

## 📊 Grafana Integration

Para visualizar dashboards Grafana embarcados:

1. Inicie o Grafana:
```bash
docker-compose up grafana
```

2. Acesse: `http://localhost:3000`

3. Configure dashboards

4. (Opcional) Embuta no Streamlit:
```python
st.components.v1.iframe("http://localhost:3000/d/sentibr", height=600)
```

## 🐛 Troubleshooting

### API não está respondendo
```
⚠️ API não está respondendo. Certifique-se de que a API está rodando.
```

**Solução**: Inicie a API primeiro:
```bash
uvicorn src.api.main:app --reload
```

### Porta 8501 já está em uso
```bash
# Use outra porta
streamlit run app.py --server.port 8502
```

### Logo não aparece
```
# Verifique o caminho do logo
ls frontend/assets/ifood_logo.jpeg
```

## 📝 Desenvolvimento

### Adicionar Nova Página

1. Crie arquivo em `pages/`:
```python
# pages/5_📋_Nova_Página.py
import streamlit as st

st.set_page_config(page_title="Nova Página", page_icon="📋")

st.title("📋 Nova Página")
# Seu código aqui
```

2. O número no início define a ordem no menu.

### Adicionar Novo Componente

1. Edite `components/ui_components.py`:
```python
def novo_componente(parametros):
    """Descrição do componente"""
    # Implementação
    pass
```

2. Importe onde necessário:
```python
from components.ui_components import novo_componente
```

## 🎯 Best Practices

1. **Performance**:
   - Use `@st.cache_data` para dados estáticos
   - Use `@st.cache_resource` para modelos
   - Evite requisições desnecessárias à API

2. **UX**:
   - Forneça feedback visual (spinners, progress bars)
   - Trate erros graciosamente
   - Use placeholders informativos

3. **Código**:
   - Mantenha componentes reutilizáveis
   - Documente funções
   - Siga PEP 8

## 📚 Recursos

- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [iFood Brand Guidelines](https://www.ifood.com.br/)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Add nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📄 Licença

Este projeto faz parte do desafio técnico para vaga de IA Sênior.

## 👥 Autor

Desenvolvido para o desafio técnico iFood.

---

**💡 Dica**: Para melhor experiência, use a aplicação em tela cheia e com resolução mínima de 1366x768.
