# 🚀 Quick Start - API REST

Guia rápido para começar a usar a API de análise de sentimento em **3 minutos**.

---

## ⚡ Start em 3 Passos

### 1️⃣ Iniciar a API

```bash
# Opção mais simples
python start_api.py --reload
```

Ou:

```bash
# Usando uvicorn diretamente
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Pronto!** A API está rodando em http://localhost:8000

---

### 2️⃣ Testar no Navegador

Abra: http://localhost:8000/docs

Você verá a interface Swagger com todos os endpoints disponíveis.

---

### 3️⃣ Fazer Primeira Predição

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Produto excelente!", "return_probabilities": true}'
```

**Resposta:**
```json
{
  "sentiment": "positive",
  "score": 0.95,
  "probabilities": {
    "positive": 0.95,
    "negative": 0.03,
    "neutral": 0.02
  },
  "processing_time_ms": 45.2,
  "model_version": "bert-sentiment-v1.0"
}
```

✅ **Funciona!** Você já está fazendo predições.

---

## 📱 Exemplos Práticos

### Python - Requests

```python
import requests

# Predição única
response = requests.post(
    "http://localhost:8000/api/v1/predict",
    json={"text": "Adorei o produto!"}
)

result = response.json()
print(f"{result['sentiment']}: {result['score']:.2%}")
# Output: positive: 95.00%
```

### Python - Cliente Oficial

```python
from examples.api_client import SentimentAPIClient

client = SentimentAPIClient("http://localhost:8000")

# Uma linha
sentiment = client.predict_sentiment("Produto excelente!")
print(sentiment)  # Output: positive

# Com confiança
sentiment, score = client.predict_with_confidence("Péssimo!")
print(f"{sentiment}: {score:.2%}")  # Output: negative: 92.00%
```

### JavaScript / Node.js

```javascript
// Predição única
fetch('http://localhost:8000/api/v1/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    text: 'Produto excelente!',
    return_probabilities: true
  })
})
.then(res => res.json())
.then(data => {
  console.log(`${data.sentiment}: ${(data.score * 100).toFixed(2)}%`);
});
```

---

## 🎯 Endpoints Essenciais

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Predição Única
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Seu texto aqui"}'
```

### 3. Predição em Lote (mais rápido!)
```bash
curl -X POST http://localhost:8000/api/v1/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Texto 1",
      "Texto 2",
      "Texto 3"
    ]
  }'
```

### 4. Métricas
```bash
curl http://localhost:8000/api/v1/metrics
```

---

## 🔍 Explorar API

### Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
  - Interface visual
  - Testar endpoints
  - Ver exemplos

- **ReDoc**: http://localhost:8000/redoc
  - Documentação detalhada
  - Mais legível
  - Para referência

### Testar Todos Endpoints
```bash
python test_api.py
```

---

## 💡 Dicas Úteis

### ✅ Predições Múltiplas?
Use `/predict/batch` - **3x mais rápido**

```python
# ❌ Lento
for text in texts:
    predict(text)

# ✅ Rápido
predict_batch(texts)
```

### ✅ Desenvolvimento?
Use `--reload` para hot reload

```bash
python start_api.py --reload
```

### ✅ Produção?
Use múltiplos workers

```bash
python start_api.py --workers 4
```

### ✅ Problemas?
1. Check logs: `logs/api.log`
2. Verifique health: `curl http://localhost:8000/health`
3. Veja métricas: `curl http://localhost:8000/api/v1/metrics`

---

## 📊 Performance

| Operação | Latência | Throughput |
|----------|----------|------------|
| Single (CPU) | ~45ms | ~20 req/s |
| Single (GPU) | ~20ms | ~50 req/s |
| Batch 10 (CPU) | ~80ms | ~120 texts/s |
| Batch 10 (GPU) | ~35ms | ~280 texts/s |

---

## 🎓 Próximos Passos

1. ✅ **Explorar** a documentação: http://localhost:8000/docs
2. ✅ **Ler** o guia completo: `docs/API.md`
3. ✅ **Ver** exemplos: `examples/api_client.py`
4. ✅ **Testar** todos endpoints: `python test_api.py`

---

## 🆘 Problemas Comuns

### Porta já em uso
```bash
# Use outra porta
python start_api.py --port 8001
```

### Modelo não encontrado
```bash
# Treine o modelo primeiro
python src/training/train.py
```

### Dependências faltando
```bash
# Instale tudo
pip install -r requirements.txt
```

---

## 📚 Mais Informações

- **API Completa**: [docs/API.md](API.md)
- **Fase 3 README**: [docs/FASE_3_README.md](FASE_3_README.md)
- **Resumo Executivo**: [docs/FASE_3_SUMMARY.md](FASE_3_SUMMARY.md)

---

## ✅ Checklist Rápido

- [ ] API iniciada
- [ ] Health check OK
- [ ] Primeira predição funcionando
- [ ] Documentação explorada
- [ ] Cliente Python testado

**Tudo funcionando?** 🎉

**Próximo**: Fase 4 - Frontend (Streamlit)
