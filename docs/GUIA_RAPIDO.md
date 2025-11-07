# ⚡ SentiBR - Guia Rápido (5 Minutos)

## 🚀 Início Rápido

### **Passo 1: Acessar** (10 segundos)
```
http://localhost:8502
```

### **Passo 2: Testar com 1 Review** (1 minuto)
```
1. Clique: 🔍 Análise Individual
2. Digite: "Comida deliciosa, entrega rápida!"
3. Clique: 🚀 Analisar
4. Veja: Sentimento Positive (95%)
```

### **Passo 3: Upload de CSV** (2 minutos)
```
1. Clique: 📦 Análise em Lote
2. Faça upload de CSV com reviews
3. Clique: Analisar
4. Veja: Resultados em tabela
5. Baixe: CSV com sentimentos
```

### **Passo 4: Ver Dashboard** (1 minuto)
```
1. Clique: 📊 Dashboard
2. Veja: Gráficos e métricas
3. Analise: Distribuição de sentimentos
```

### **Passo 5: Avaliar Modelo** (1 minuto)
```
1. Clique: 🔎 Avaliação
2. Upload CSV com labels
3. Ver: Acurácia, F1-Score
4. Analisar: Matriz de confusão
```

---

## 📝 Exemplo de CSV para Teste

Crie arquivo `teste.csv`:

```csv
text,label
"Comida deliciosa, melhor restaurante!",positive
"Entrega demorou 3 horas, comida fria",negative
"Normal, nada excepcional",neutral
"Excelente atendimento!",positive
"Péssima experiência",negative
```

**Use este CSV para testar todas as funcionalidades!**

---

## 🎯 Principais Funcionalidades

| Página | O que faz | Tempo |
|--------|-----------|-------|
| 🔍 Análise Individual | Analisa 1 review | 2s |
| 📦 Análise em Lote | Analisa 100s de reviews | 30s-5min |
| 🔎 Avaliação | Testa acurácia do modelo | 1-2min |
| ⚔️ Comparação | BERT vs GPT | 2-10min |
| 📊 Dashboard | Visualiza métricas | Instantâneo |

---

## 💡 Dica Rápida

**Para análise rápida de 1 review**:
```
http://localhost:8502 → 🔍 Análise Individual → Digite → Analisar
```

**Para analisar arquivo CSV**:
```
http://localhost:8502 → 📦 Análise em Lote → Upload → Processar
```

---

## ✅ Checklist de Uso

- [ ] Acessei http://localhost:8502
- [ ] Testei análise individual
- [ ] Fiz upload de CSV
- [ ] Vi dashboard
- [ ] Avaliei modelo
- [ ] Baixei resultados

---

**Pronto! Você já sabe usar o SentiBR! 🎉**

**Guia completo**: [GUIA_USUARIO_FRONTEND.md](computer:///mnt/user-data/outputs/GUIA_USUARIO_FRONTEND.md)
