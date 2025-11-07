# 🧪 Página de Avaliação - Frontend

Interface interativa para executar avaliações completas do modelo **sem usar terminal**!

## 🎯 Features

### ✅ Avaliação BERT
- Métricas clássicas em tempo real
- Confusion Matrix interativa
- Análise de erros detalhada
- Validação automática (threshold 90%)

### ✅ LLM Judge (Opcional)
- Avaliação qualitativa com GPT-4o-mini
- Identificação de edge cases
- Análise de acordo com BERT
- Tracking de custos em tempo real

### ✅ Comparação BERT vs GPT
- Trade-offs side-by-side
- Recomendações de uso
- Estratégia híbrida otimizada

### ✅ Download de Relatórios
- Relatórios em JSON
- Resultados salvos automaticamente

---

## 🚀 Como Usar

### 1. Acessar a Página

```bash
# Iniciar Streamlit
cd frontend
streamlit run app.py
```

Depois, clique em **"🧪 Avaliação"** no menu lateral.

### 2. Configurar Avaliação

**Parâmetros:**
- **Número de samples:** 10-1000 (padrão: 100)
- **Usar LLM Judge:** Sim/Não (requer OpenAI API key)
- **Samples para LLM:** 5-100 (padrão: 50)

**Custo estimado** é exibido automaticamente.

### 3. Executar

Clique em **"🚀 Executar Avaliação Completa"** e aguarde!

### 4. Ver Resultados

A página exibirá:

**Métricas BERT:**
- Accuracy, Precision, Recall, F1-Score
- Confusion Matrix interativa
- Métricas por classe
- Análise de erros

**LLM Judge (se ativado):**
- Taxa de acordo com BERT
- Taxa de edge cases
- Confiança média
- Custo real em USD

**Comparação:**
- Vantagens de cada modelo
- Trade-offs detalhados
- Recomendação de estratégia

### 5. Download

Baixe os relatórios em JSON para análise posterior.

---

## 📋 Pré-requisitos

### Obrigatório
- Modelo BERT treinado em `models/bert_finetuned/`
- Dados de teste em `data/processed/test.csv`
- Módulo de evaluation instalado

### Opcional (para LLM Judge)
- OpenAI API key configurada
- `export OPENAI_API_KEY='your-key'`

---

## 🔧 Setup

### 1. Instalar Dependências

```bash
pip install -r requirements-evaluation.txt
```

### 2. Copiar Página

```bash
# Copiar página para frontend
cp pages/4_🧪_Avaliação.py frontend/pages/
```

### 3. Configurar OpenAI (Opcional)

```bash
# Para usar LLM Judge
export OPENAI_API_KEY='your-api-key'
```

### 4. Verificar Test Data

```bash
# Verificar se test data existe
ls -lh data/processed/test.csv

# Se não existe, criar:
python src/data/load_data_v2.py
python src/data/split_dataset.py
```

---

## 💡 Exemplos de Uso

### Caso 1: Avaliação Rápida (BERT apenas)

1. Acessar página "🧪 Avaliação"
2. Configurar: **100 samples**, **Sem LLM**
3. Clicar em "Executar"
4. Ver resultados em ~30 segundos
5. Download do relatório

**Resultado:** Métricas completas sem custos!

### Caso 2: Validação Completa (com LLM)

1. Acessar página "🧪 Avaliação"
2. Configurar: **500 samples BERT**, **50 samples LLM**
3. Verificar custo estimado (~$0.005)
4. Clicar em "Executar"
5. Ver resultados em ~3 minutos
6. Analisar acordo BERT vs LLM
7. Download de ambos os relatórios

**Resultado:** Validação completa com LLM por centavos!

### Caso 3: Monitoramento Contínuo

**Schedule regular:**
- Segunda, Quarta, Sexta: Avaliar 200 samples
- Verificar se Accuracy > 90%
- Se não, retreinar modelo

---

## 📊 Interpretando Resultados

### ✅ Modelo Aprovado
```
Accuracy: ≥ 90%
F1-Score: ≥ 88%
LLM Agreement: ≥ 85%
```
**Ação:** Deploy em produção ✅

### ⚠️ Modelo OK
```
Accuracy: 85-90%
F1-Score: 83-88%
LLM Agreement: 75-85%
```
**Ação:** Considere melhorias antes de deploy

### ❌ Modelo Precisa Melhoria
```
Accuracy: < 85%
F1-Score: < 83%
LLM Agreement: < 75%
```
**Ação:** Retreine o modelo com mais dados

---

## 💰 Custos do LLM Judge

| Samples | Tokens | Custo USD | Uso |
|---------|--------|-----------|-----|
| 10 | ~3k | $0.001 | Smoke test |
| 50 | ~15k | $0.005 | Quick validation |
| 100 | ~30k | $0.015 | Standard eval |

**Dica:** Use 50-100 samples para validação regular.

---

## 🎨 Interface

### Tela Principal

```
┌─────────────────────────────────────────────┐
│  🧪 Avaliação do Modelo                     │
├─────────────────────────────────────────────┤
│                                             │
│  ⚙️ Configuração da Avaliação              │
│                                             │
│  [Número de samples]  [100]                 │
│  [✓] Usar LLM Judge                        │
│  [Samples LLM]       [50]                  │
│                                             │
│  💰 Custo estimado: $0.005                 │
│                                             │
│  [🚀 Executar Avaliação Completa]          │
│                                             │
└─────────────────────────────────────────────┘
```

### Resultados

```
┌─────────────────────────────────────────────┐
│  📊 Métricas do BERT                        │
├─────────────────────────────────────────────┤
│                                             │
│  92.3%      91.8%      92.0%      91.9%     │
│  Accuracy   Precision  Recall    F1-Score   │
│                                             │
│  ⏱️ Tempo: 28.5s                            │
│                                             │
│  [Confusion Matrix interativa]             │
│  [Métricas por classe]                     │
│  [Análise de erros]                        │
│                                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  🤖 LLM Judge (GPT-4o-mini)                 │
├─────────────────────────────────────────────┤
│                                             │
│  87.5%      12.0%      0.89       $0.005    │
│  Acordo     Edge Cases  Confiança  Custo    │
│                                             │
│  ⏱️ Tempo: 156.2s | 🎯 50 samples          │
│                                             │
│  [Distribuição de sentimentos]             │
│                                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  🆚 Comparação BERT vs LLM Judge            │
├─────────────────────────────────────────────┤
│                                             │
│  [Vantagens de cada] [Trade-offs]          │
│  [Recomendação: Estratégia Híbrida]        │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Problema 1: "Módulo de avaliação não encontrado"

**Solução:**
```bash
pip install -r requirements-evaluation.txt
```

### Problema 2: "OpenAI API Key não configurada"

**Solução:**
```bash
export OPENAI_API_KEY='your-key'
# Reiniciar Streamlit
```

### Problema 3: "Dados de teste não encontrados"

**Solução:**
```bash
python src/data/load_data_v2.py
python src/data/split_dataset.py
```

### Problema 4: Página não aparece no menu

**Solução:**
```bash
# Verificar arquivo
ls frontend/pages/4_🧪_Avaliação.py

# Se não existe, copiar
cp pages/4_🧪_Avaliação.py frontend/pages/

# Reiniciar Streamlit
```

---

## 🎯 Best Practices

### Frequência de Avaliação

**Desenvolvimento:**
- Após cada treinamento
- Antes de cada deploy

**Produção:**
- Semanal: 200-500 samples
- Mensal: 1000+ samples

### Otimização de Custos

1. **BERT Primeiro:** Sempre execute BERT (grátis)
2. **LLM Estratégico:** Use 50-100 samples, não todos
3. **Sample Inteligente:** Foque em casos de baixa confiança
4. **Cache Resultados:** Salve relatórios para análise posterior

### Validação de Produção

Antes de deploy, certifique-se:
- ✅ Accuracy ≥ 90%
- ✅ F1-Score ≥ 88%
- ✅ Todas as classes com F1 ≥ 0.85
- ✅ LLM Agreement ≥ 85% (se testado)
- ✅ Sem erros graves em edge cases

---

## 📈 Próximos Passos

Após validação bem-sucedida:

1. **Deploy:** Colocar modelo em produção
2. **Monitor:** Configurar monitoring contínuo
3. **Feedback Loop:** Coletar feedback de usuários
4. **Retreino:** Agendar retreino periódico

---

## 🎓 Conceitos

### Por que Avaliar?

**Antes do Deploy:**
- Garantir qualidade mínima
- Identificar pontos fracos
- Comparar versões

**Durante Produção:**
- Detectar degradação
- Identificar drift
- Validar melhorias

### BERT vs LLM Judge

**Use BERT quando:**
- Precisa de velocidade
- Quer zero custos
- Tem volume alto

**Use LLM quando:**
- Precisa explicação
- Quer validação qualitativa
- Budget permite

**Use Ambos quando:**
- Validação crítica
- Identificar edge cases
- Treinar novo modelo

---

## 🎉 Conclusão

Com esta página, você pode:

✅ **Avaliar modelos** sem terminal  
✅ **Visualizar resultados** em tempo real  
✅ **Comparar BERT vs GPT** interativamente  
✅ **Download relatórios** automaticamente  
✅ **Monitorar custos** em tempo real  

**Interface 100% visual e user-friendly!** 🚀

---

**Desenvolvido com ❤️ para o desafio técnico de IA Sênior**

🧪 **Testing + 🎨 UI = 💪 Professional ML!**
