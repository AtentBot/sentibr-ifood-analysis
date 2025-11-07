# 🎨 INTEGRAÇÃO FRONTEND - Página de Avaliação

Guia completo para adicionar a página de avaliação ao frontend Streamlit.

## 📦 Arquivos Incluídos

1. **`4_🧪_Avaliação.py`** (450 linhas)
   - Página completa de avaliação
   - Interface interativa
   - Visualizações profissionais

2. **`README_AVALIACAO.md`** (400 linhas)
   - Documentação completa
   - Guia de uso
   - Troubleshooting

---

## 🚀 Integração em 3 Passos

### Passo 1: Copiar Arquivo

```bash
# Copiar página para frontend
cp 4_🧪_Avaliação.py seu-projeto/frontend/pages/

# Verificar
ls -lh seu-projeto/frontend/pages/4_🧪_Avaliação.py
```

### Passo 2: Instalar Dependências

```bash
# Já deve estar instalado se seguiu a Fase 6
pip install -r requirements-evaluation.txt

# Verificar
python -c "from src.evaluation import ModelEvaluator; print('OK')"
```

### Passo 3: Configurar (Opcional - para LLM)

```bash
# Para usar LLM Judge
export OPENAI_API_KEY='your-api-key-here'
```

**Pronto!** A página já aparecerá no menu do Streamlit.

---

## 🎯 Como Funciona

### Fluxo de Uso

```
1. Usuário acessa "🧪 Avaliação"
   ↓
2. Configura parâmetros:
   - Número de samples (10-1000)
   - Usar LLM Judge? (Sim/Não)
   - Samples para LLM (5-100)
   ↓
3. Clica em "Executar"
   ↓
4. Sistema executa:
   - Carrega test data
   - Faz predições BERT
   - Calcula métricas
   - Executa LLM Judge (se ativado)
   - Gera visualizações
   ↓
5. Exibe resultados:
   - Métricas BERT
   - Confusion Matrix
   - Resultados LLM
   - Comparação
   ↓
6. Permite download:
   - Relatórios JSON
   - Análises completas
```

### Arquitetura

```
Frontend (Streamlit)
    ↓
src/evaluation/
    ├── ModelEvaluator → Métricas BERT
    └── LLMJudge → Avaliação GPT
    ↓
src/api/inference.py
    └── SentimentPredictor → Predições
    ↓
models/bert_finetuned/
    └── Modelo treinado
```

---

## 📊 Interface Detalhada

### Seção 1: Configuração

```python
# Controles interativos
n_samples = st.slider(...)        # 10-1000
use_llm = st.checkbox(...)        # Sim/Não
llm_samples = st.slider(...)      # 5-100

# Custo estimado automático
estimated_cost = calcular_custo(llm_samples)
st.info(f"💰 Custo: ${estimated_cost}")
```

### Seção 2: Execução

```python
if st.button("Executar"):
    # Progress bar em tempo real
    progress = st.progress(0)
    
    # Avaliação BERT
    bert_result = run_bert_evaluation(...)
    
    # Avaliação LLM (opcional)
    if use_llm:
        llm_result = run_llm_evaluation(...)
```

### Seção 3: Resultados

```python
# Cards de métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Accuracy", f"{accuracy:.1%}")
col2.metric("Precision", f"{precision:.1%}")
...

# Confusion Matrix interativa (Plotly)
fig = go.Figure(data=go.Heatmap(...))
st.plotly_chart(fig)

# Tabelas de dados
st.dataframe(df_metrics)
```

### Seção 4: Download

```python
# Botões de download
st.download_button(
    label="Download BERT (JSON)",
    data=bert_json,
    file_name="bert_eval.json"
)
```

---

## 🎨 Customização

### Mudar Cores

```python
# Em 4_🧪_Avaliação.py, seção CSS
st.markdown("""
<style>
    .metric-value {
        color: #EA1D2C;  /* Sua cor */
    }
</style>
""")
```

### Adicionar Métricas

```python
# Após display_bert_results()
def display_custom_metric():
    st.metric("Sua Métrica", valor)

display_custom_metric()
```

### Mudar Thresholds

```python
# Validação customizada
if bert_result.accuracy >= 0.95:  # Seu threshold
    st.success("Excelente!")
```

---

## 🔧 Configurações Avançadas

### Mudar Caminho dos Dados

```python
# Em load_test_data()
test_paths = [
    Path("seu/caminho/test.csv"),
    ...
]
```

### Adicionar Mais Samples

```python
# No slider
n_samples = st.slider(
    ...,
    max_value=5000,  # Aumentar limite
    ...
)
```

### Customizar LLM Model

```python
# Em run_llm_evaluation()
judge = LLMJudge(
    model="gpt-4",  # Usar GPT-4 em vez de mini
    temperature=0.0  # Mais determinístico
)
```

---

## 📱 Responsividade

A página é **totalmente responsiva**:

- ✅ Desktop (1920x1080)
- ✅ Laptop (1366x768)
- ✅ Tablet (1024x768)
- ⚠️ Mobile (limitado - Streamlit não é ideal para mobile)

---

## 🎯 Features Implementadas

### ✅ Básicas
- [x] Configuração de parâmetros
- [x] Execução de avaliação BERT
- [x] Exibição de métricas
- [x] Confusion Matrix
- [x] Download de relatórios

### ✅ Avançadas
- [x] LLM Judge integration
- [x] Progress bars em tempo real
- [x] Estimativa de custos
- [x] Validação automática
- [x] Comparação BERT vs GPT
- [x] Análise de erros
- [x] Visualizações interativas

### ✅ UX
- [x] Cards visuais de métricas
- [x] Cores do iFood
- [x] Mensagens de validação
- [x] Loading states
- [x] Error handling
- [x] Tooltips informativos

---

## 🧪 Testing

### Teste Manual

```bash
# 1. Iniciar Streamlit
cd frontend
streamlit run app.py

# 2. Acessar http://localhost:8501

# 3. Clicar em "🧪 Avaliação"

# 4. Configurar:
#    - 10 samples
#    - Sem LLM

# 5. Clicar em "Executar"

# 6. Verificar:
#    - Métricas aparecem
#    - Confusion matrix renderiza
#    - Download funciona
```

### Teste com LLM

```bash
# 1. Configurar API key
export OPENAI_API_KEY='your-key'

# 2. Iniciar Streamlit
streamlit run app.py

# 3. Na página:
#    - 10 samples
#    - ✓ Usar LLM
#    - 5 samples LLM

# 4. Executar

# 5. Verificar:
#    - Custo ~$0.001
#    - Resultados LLM aparecem
#    - Comparação exibida
```

---

## 📊 Métricas de Performance

### Tempos Esperados

| Samples | BERT | LLM (se ativado) | Total |
|---------|------|------------------|-------|
| 10 | ~3s | ~30s | ~33s |
| 50 | ~10s | ~150s | ~160s |
| 100 | ~20s | ~300s | ~320s |
| 500 | ~90s | N/A | ~90s |

### Uso de Memória

- **BERT:** ~2GB RAM
- **LLM Judge:** ~500MB RAM
- **Visualizações:** ~100MB RAM

**Total:** ~2.5GB RAM recomendados

---

## 🐛 Troubleshooting Específico

### Problema: Página não aparece

**Causa:** Arquivo não está em `frontend/pages/`

**Solução:**
```bash
# Verificar estrutura
ls frontend/pages/

# Deve mostrar:
# 1_📝_Análise.py
# 2_📊_Métricas.py
# 3_🔍_Monitoramento.py
# 4_🧪_Avaliação.py  ← Este arquivo
```

### Problema: Import Error

**Causa:** Módulo de evaluation não instalado

**Solução:**
```bash
pip install -r requirements-evaluation.txt
```

### Problema: Test data não encontrado

**Causa:** Dados não preparados

**Solução:**
```bash
python src/data/load_data_v2.py
python src/data/split_dataset.py
```

### Problema: Plotly não renderiza

**Causa:** Versão incompatível

**Solução:**
```bash
pip install --upgrade plotly
pip install --upgrade streamlit
```

---

## 🎓 Conceitos de UI/UX

### Design Principles

1. **Progressive Disclosure**
   - Mostra opções básicas primeiro
   - LLM é opcional e expandível

2. **Feedback Imediato**
   - Progress bars em tempo real
   - Loading states
   - Success/error messages

3. **Visual Hierarchy**
   - Métricas principais em destaque
   - Detalhes em expandibles
   - Cores para guiar atenção

4. **Error Prevention**
   - Validação de inputs
   - Warnings preventivos
   - Confirmações para ações custosas

---

## 🚀 Próximas Melhorias

### Curto Prazo
- [ ] Histórico de avaliações
- [ ] Comparação entre runs
- [ ] Export para PDF
- [ ] Gráficos adicionais

### Médio Prazo
- [ ] Agendamento de avaliações
- [ ] Notificações por email
- [ ] Dashboard de trending
- [ ] A/B testing UI

### Longo Prazo
- [ ] Real-time evaluation
- [ ] Collaborative features
- [ ] Mobile app
- [ ] API REST para automação

---

## 📚 Recursos

### Documentação
- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Docs](https://plotly.com/python/)
- [evaluation/README.md](../evaluation/README.md)

### Exemplos
- Ver `main()` function em `4_🧪_Avaliação.py`
- Ver outras páginas em `frontend/pages/`

---

## ✅ Checklist de Integração

- [ ] Arquivo copiado para `frontend/pages/`
- [ ] Dependências instaladas
- [ ] OpenAI API key configurada (opcional)
- [ ] Test data disponível
- [ ] Streamlit iniciado
- [ ] Página aparece no menu
- [ ] Avaliação BERT funciona
- [ ] Avaliação LLM funciona (se configurado)
- [ ] Visualizações renderizam
- [ ] Download funciona
- [ ] Documentação lida

---

## 🎉 Conclusão

Agora você tem uma **interface visual completa** para executar avaliações!

**Benefícios:**
- ✅ Sem necessidade de terminal
- ✅ Interface user-friendly
- ✅ Visualizações profissionais
- ✅ Download automático
- ✅ Tracking de custos

**Usuários podem:**
1. Configurar visualmente
2. Executar com um clique
3. Ver resultados em tempo real
4. Baixar relatórios
5. Repetir facilmente

**Tudo isso sem digitar um único comando!** 🎨

---

**Desenvolvido com ❤️ para o desafio técnico de IA Sênior**

🧪 **Testing + 🎨 Frontend = 💪 User Experience!**
