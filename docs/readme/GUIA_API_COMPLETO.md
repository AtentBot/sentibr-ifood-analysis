# 🚀 API SentiBR - Instalação Completa do ZERO

## 📥 BAIXE ESTES 4 ARQUIVOS:

1. **[main.py](computer:///mnt/user-data/outputs/main.py)** ⭐ - Código da API
2. **[requirements.txt](computer:///mnt/user-data/outputs/requirements.txt)** ⭐ - Dependências
3. **[Dockerfile.api.ATUALIZADO](computer:///mnt/user-data/outputs/Dockerfile.api.ATUALIZADO)** ⭐ - Dockerfile
4. **[instalar_api_completa.sh](computer:///mnt/user-data/outputs/instalar_api_completa.sh)** ⭐ - Script de instalação

---

## ⚡ INSTALAÇÃO AUTOMÁTICA (1 comando):

```bash
chmod +x instalar_api_completa.sh
./instalar_api_completa.sh
```

**Pronto! Faz tudo sozinho!** ✅

---

## 🔧 INSTALAÇÃO MANUAL (6 passos):

### 1. Criar estrutura:
```bash
mkdir -p api
```

### 2. Copiar arquivos:
```bash
cp main.py api/main.py
cp requirements.txt api/requirements.txt
cp Dockerfile.api.ATUALIZADO docker/Dockerfile.api
```

### 3. Criar __init__.py:
```bash
touch api/__init__.py
```

### 4. Verificar estrutura:
```bash
tree api/
# Deve mostrar:
# api/
# ├── main.py
# ├── requirements.txt
# └── __init__.py
```

### 5. Build:
```bash
docker-compose build --no-cache api
```

### 6. Iniciar:
```bash
docker-compose up -d api
docker logs -f sentibr-api
```

---

## ✅ ESTRUTURA FINAL:

```
projeto/
├── api/
│   ├── main.py              ← NOVO
│   ├── requirements.txt     ← NOVO
│   └── __init__.py          ← NOVO
├── docker/
│   └── Dockerfile.api       ← ATUALIZADO
└── docker-compose.yml
```

---

## 📋 O QUE A API FAZ:

### **Endpoints Disponíveis:**

1. **GET /** - Raiz
2. **GET /api/v1/health** - Health check
3. **POST /api/v1/predict** - Predição única
4. **POST /api/v1/predict/batch** - Predição em lote
5. **GET /api/v1/model/info** - Info do modelo

### **Exemplo de Uso:**

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Predição
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Comida deliciosa, entrega rápida!"}'

# Resposta:
{
  "text": "Comida deliciosa, entrega rápida!",
  "sentiment": "positive",
  "confidence": 0.95,
  "scores": {
    "negative": 0.02,
    "neutral": 0.03,
    "positive": 0.95
  }
}
```

---

## 🎯 VERIFICAR SE FUNCIONOU:

### 1. Ver logs:
```bash
docker logs sentibr-api
```

**Deve mostrar:**
```
🔄 Carregando modelo BERT...
✅ Modelo BERT carregado com sucesso!
INFO:     Started server process [1]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Testar health:
```bash
curl http://localhost:8000/api/v1/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-06T...",
  "version": "1.0.0"
}
```

### 3. Acessar docs:
```
http://localhost:8000/docs
```

---

## 🔥 CARACTERÍSTICAS DA API:

- ✅ **FastAPI** - Framework moderno e rápido
- ✅ **BERT** - Modelo neuralmind/bert-base-portuguese-cased
- ✅ **3 classes** - negative, neutral, positive
- ✅ **Batch prediction** - Múltiplos reviews de uma vez
- ✅ **Health check** - Monitoramento
- ✅ **OpenAPI docs** - Documentação automática
- ✅ **CORS habilitado** - Frontend pode conectar
- ✅ **Async/Await** - Performance
- ✅ **Error handling** - Tratamento robusto

---

## 📊 PERFORMANCE:

- **Startup**: ~60s (primeira vez, carrega BERT)
- **Predição**: ~100-200ms por review
- **Batch**: ~1-2s para 10 reviews
- **Memory**: ~2GB RAM (modelo BERT)

---

## 🆘 TROUBLESHOOTING:

### Erro: "Could not import module 'main'"
```bash
# Verificar se main.py existe
ls -la api/main.py

# Se não existir, copiar novamente
cp main.py api/main.py
```

### Erro: "Model not loaded"
```bash
# Aguardar mais tempo (modelo demora para carregar)
sleep 60

# Ver logs
docker logs sentibr-api
```

### Erro: "Permission denied"
```bash
# Verificar Dockerfile
cat docker/Dockerfile.api | head -1

# Deve mostrar: FROM ubuntu:22.04
# Se mostrar python:3.10-slim, substituir Dockerfile
```

---

## 🎉 SUCESSO!

Quando tudo funcionar:

```bash
$ curl http://localhost:8000/api/v1/health
{"status":"healthy"...}

$ curl http://localhost:8000
{"message":"SentiBR API - Análise de Sentimentos"...}
```

**Acesse**: http://localhost:8000/docs 📚

---

**Use o script automático! Instala tudo em 1 comando! 🚀**
