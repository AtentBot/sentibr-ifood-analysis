# 📱 SentiBR - Guia do Usuário

## 🌐 Acesso

**URL**: http://localhost:8502

---

## 📄 Páginas Disponíveis

### 1. 🏠 **Página Inicial (Home)**

**O que faz**: Visão geral do sistema

**Como usar**:
1. Acesse http://localhost:8502
2. Veja o resumo das funcionalidades
3. Clique em qualquer seção no menu lateral

**Informações exibidas**:
- ✅ Descrição do projeto
- ✅ Tecnologias usadas (BERT, GPT-4)
- ✅ Estatísticas rápidas
- ✅ Links rápidos

---

### 2. 📊 **Dashboard**

**O que faz**: Visualização de métricas e estatísticas

**Como usar**:
1. Vá em: **📊 Dashboard** (menu lateral)
2. Veja gráficos e métricas
3. Filtre por período/sentimento

**Visualizações**:
- 📈 Distribuição de sentimentos (pizza/barras)
- 📉 Evolução temporal
- 🎯 Acurácia do modelo
- 📊 Top palavras por sentimento
- 🔥 Heatmap de aspectos

---

### 3. 🔍 **Análise Individual**

**O que faz**: Analisa um review por vez

**Passo a passo**:

#### **Opção 1: Digitar Review**
```
1. Vá em: 🔍 Análise Individual
2. Escreva o review na caixa de texto
   Exemplo: "Comida deliciosa, entrega rápida!"
3. Clique: "🚀 Analisar"
4. Veja o resultado:
   • Sentimento: Positive ✅
   • Confiança: 95%
   • Scores: Neg(2%) | Neu(3%) | Pos(95%)
```

#### **Opção 2: Upload de Arquivo**
```
1. Clique: "📤 Upload de Arquivo"
2. Selecione arquivo .txt ou .csv
3. Clique: "Analisar"
4. Veja resultados
```

**Resultados exibidos**:
- 😊 Emoji do sentimento
- 📊 Gráfico de probabilidades
- 💡 Explicação (palavras importantes)
- 🏷️ Aspectos identificados (comida, entrega, preço)

---

### 4. 📦 **Análise em Lote**

**O que faz**: Analisa múltiplos reviews de uma vez

**Passo a passo**:

#### **1. Upload do Arquivo**
```
1. Vá em: 📦 Análise em Lote
2. Clique: "📤 Escolher arquivo CSV"
3. Selecione seu CSV
   (deve ter coluna 'text' ou 'review')
4. Clique: "Upload"
```

#### **2. Configurar Análise**
```
1. Escolha número de amostras:
   • 10, 50, 100, 500, TODAS
2. Selecione opções:
   ☑️ Análise BERT
   ☑️ Análise GPT (opcional)
   ☑️ Comparação BERT vs GPT
3. Clique: "🚀 Iniciar Análise"
```

#### **3. Ver Resultados**
```
1. Aguarde processamento (barra de progresso)
2. Veja tabela com resultados:
   • Review | BERT | GPT | Confiança
3. Baixe resultados:
   • 📥 Download CSV
   • 📊 Download Relatório PDF
```

**Formato do CSV de entrada**:
```csv
text,rating
"Comida deliciosa, muito bom!",5
"Entrega demorou, comida fria",2
"Normal, nada especial",3
```

---

### 5. 🔎 **Avaliação do Modelo**

**O que faz**: Avalia performance do modelo BERT

**Passo a passo**:

#### **1. Upload de Dados de Teste**
```
1. Vá em: 🔎 Avaliação
2. Clique: "📤 Upload de Dados"
3. Selecione CSV com labels reais
4. CSV deve ter:
   • Coluna 'text': reviews
   • Coluna 'label': sentimento real
```

#### **2. Executar Avaliação**
```
1. Tab: "⚙️ Configuração"
2. Escolha número de samples
3. Clique: "🚀 Executar Avaliação"
4. Aguarde processamento
```

#### **3. Ver Métricas**
```
1. Tab: "📊 Resultados"
2. Veja métricas:
   • Acurácia: 92.3%
   • Precision: 91.5%
   • Recall: 90.8%
   • F1-Score: 91.1%
3. Matriz de confusão
4. Relatório de classificação
```

**Formato do CSV com labels**:
```csv
text,label
"Comida deliciosa!",positive
"Horrível, nunca mais",negative
"Normal",neutral
```

---

### 6. ⚔️ **Comparação BERT vs GPT**

**O que faz**: Compara predições BERT vs GPT-4

**Passo a passo**:

#### **1. Upload de Dados**
```
1. Vá em: ⚔️ Comparação
2. Upload CSV com reviews
3. Clique: "Processar"
```

#### **2. Ver Comparação**
```
1. Veja tabela lado a lado:
   • Review | BERT | GPT | Concordam?
2. Filtrar:
   • ✅ Apenas concordantes
   • ❌ Apenas discordantes
3. Estatísticas:
   • Taxa de concordância: 85%
   • Tempo médio BERT: 100ms
   • Tempo médio GPT: 2s
```

#### **3. Análise Detalhada**
```
1. Clique em qualquer review
2. Veja comparação detalhada:
   • Scores BERT
   • Scores GPT
   • Justificativa GPT
   • Por que divergiram?
```

---

### 7. 🤖 **LLM as a Judge**

**O que faz**: GPT-4 avalia qualidade das predições BERT

**Passo a passo**:

#### **1. Configurar Avaliação**
```
1. Vá em: 🤖 LLM Judge
2. Upload CSV com:
   • text: reviews
   • bert_prediction: predição BERT
   • true_label: label real (opcional)
3. Configure critérios:
   ☑️ Acurácia
   ☑️ Nuance
   ☑️ Contexto
   ☑️ Aspectos
```

#### **2. Executar Julgamento**
```
1. Clique: "⚖️ Julgar Predições"
2. Aguarde GPT-4 analisar
3. Veja resultados:
   • Review
   • BERT disse: Positive
   • GPT avalia: ✅ Correto / ❌ Errado
   • Justificativa
   • Score: 8/10
```

#### **3. Relatório Final**
```
1. Métricas agregadas:
   • Concordância: 88%
   • Casos ambíguos: 12%
   • Score médio: 7.5/10
2. Download relatório JSON
```

---

### 8. 📈 **Monitoramento**

**O que faz**: Monitora saúde do sistema

**Como usar**:
```
1. Vá em: 📈 Monitoramento
2. Veja status:
   • API: ✅ Online
   • BERT: ✅ Carregado
   • Redis: ✅ Conectado
   • PostgreSQL: ✅ Healthy
3. Métricas em tempo real:
   • Requests/segundo
   • Tempo de resposta
   • Uso de memória
   • Cache hit rate
```

**Alertas**:
- 🟢 Verde: Tudo OK
- 🟡 Amarelo: Atenção
- 🔴 Vermelho: Problema

---

## 🎯 Casos de Uso Práticos

### **Caso 1: Cliente quer analisar reviews de restaurante**

```
1. Exportar reviews do iFood (CSV)
2. Ir em: 📦 Análise em Lote
3. Upload do CSV
4. Executar análise BERT
5. Ver dashboard com insights:
   • 60% positivos
   • 30% neutros
   • 10% negativos
6. Baixar relatório
```

---

### **Caso 2: Testar acurácia do modelo**

```
1. Pegar dataset com labels (ex: 1000 reviews)
2. Ir em: 🔎 Avaliação
3. Upload do dataset
4. Executar avaliação
5. Ver métricas:
   • Acurácia: 92%
   • F1: 91%
6. Analisar matriz de confusão
7. Identificar onde modelo erra mais
```

---

### **Caso 3: Comparar BERT vs GPT**

```
1. Selecionar 50 reviews difíceis
2. Ir em: ⚔️ Comparação
3. Upload dos reviews
4. Ver onde BERT e GPT discordam
5. Analisar casos ambíguos:
   • "Comida ok, mas preço alto"
   • BERT: Neutral
   • GPT: Negative
6. Decidir qual faz mais sentido
```

---

### **Caso 4: Análise rápida de um review**

```
1. Cliente reclama no WhatsApp:
   "Entrega demorou 2h, comida fria!"
2. Ir em: 🔍 Análise Individual
3. Colar o texto
4. Ver resultado:
   • Sentimento: Negative (97%)
   • Aspecto: Entrega (-0.9)
5. Responder cliente com empatia
```

---

## 💡 Dicas de Uso

### **✅ Boas Práticas**

1. **CSVs bem formatados**:
   - Use coluna 'text' para reviews
   - Use 'label' para análise com ground truth
   - Codifique em UTF-8

2. **Análise em lote**:
   - Comece com amostra pequena (50-100)
   - Teste antes de processar milhares

3. **GPT-4**:
   - Use com moderação (custa dinheiro)
   - Configure OPENAI_API_KEY corretamente

4. **Monitoramento**:
   - Verifique saúde antes de análises grandes
   - Cache ajuda na performance

### **❌ Evitar**

1. ❌ Upload de arquivos muito grandes (>10MB) de uma vez
2. ❌ Análise GPT para todos os reviews (custa caro)
3. ❌ Reviews muito curtos (<3 palavras)
4. ❌ Texto em outras línguas que não português

---

## 🆘 Troubleshooting

### **Erro: "API não responde"**
```bash
# Verificar se API está rodando
docker ps | grep sentibr-api

# Ver logs
docker logs sentibr-api

# Reiniciar
docker-compose restart api
```

### **Erro: "Modelo não carregado"**
```
• Aguarde 60s (modelo demora para carregar)
• Verifique logs da API
• Reinicie container se necessário
```

### **Erro: "GPT não funciona"**
```
• Verifique OPENAI_API_KEY
• Adicione no docker-compose.yml:
  environment:
    OPENAI_API_KEY: sk-...
• Reinicie: docker-compose up -d
```

---

## 📞 Suporte

**Problemas?**
1. Veja logs: `docker logs sentibr-frontend`
2. Veja logs API: `docker logs sentibr-api`
3. Reinicie: `docker-compose restart`

---

## 🎉 Pronto para Usar!

**Acesse**: http://localhost:8502

**Comece por**:
1. 📊 Dashboard - Ver visão geral
2. 🔍 Análise Individual - Testar com 1 review
3. 📦 Análise em Lote - Processar vários

**Boa análise! 🚀**
