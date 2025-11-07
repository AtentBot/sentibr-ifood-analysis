#!/bin/bash

# ============================================
# Instalação COMPLETA da API do zero
# ============================================

set -e

echo "🚀 Instalação Completa da API SentiBR"
echo "===================================="
echo ""

# 1. Criar diretório api se não existir
echo "[1/8] Verificando estrutura..."
mkdir -p api
echo "✅ Diretório api/ criado"
echo ""

# 2. Copiar main.py
echo "[2/8] Instalando main.py..."
if [ -f "main.py" ]; then
    cp main.py api/main.py
    echo "✅ main.py instalado"
else
    echo "❌ main.py não encontrado!"
    echo "Baixe: main.py"
    exit 1
fi
echo ""

# 3. Copiar requirements.txt
echo "[3/8] Instalando requirements.txt..."
if [ -f "requirements.txt" ]; then
    cp requirements.txt api/requirements.txt
    echo "✅ requirements.txt instalado"
else
    echo "❌ requirements.txt não encontrado!"
    exit 1
fi
echo ""

# 4. Criar __init__.py
echo "[4/8] Criando __init__.py..."
touch api/__init__.py
echo "✅ __init__.py criado"
echo ""

# 5. Substituir Dockerfile
echo "[5/8] Instalando Dockerfile..."
if [ -f "Dockerfile.api.ATUALIZADO" ]; then
    mkdir -p docker
    cp docker/Dockerfile.api docker/Dockerfile.api.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    cp Dockerfile.api.ATUALIZADO docker/Dockerfile.api
    echo "✅ Dockerfile instalado"
else
    echo "❌ Dockerfile.api.ATUALIZADO não encontrado!"
    exit 1
fi
echo ""

# 6. Verificar estrutura
echo "[6/8] Verificando estrutura final..."
if [ -f "api/main.py" ] && [ -f "api/requirements.txt" ]; then
    echo "✅ Estrutura correta:"
    echo "   api/"
    echo "   ├── main.py"
    echo "   ├── requirements.txt"
    echo "   └── __init__.py"
else
    echo "❌ Estrutura incorreta!"
    exit 1
fi
echo ""

# 7. Limpar containers antigos
echo "[7/8] Limpando API antiga..."
docker-compose stop api 2>/dev/null || true
docker rm -f sentibr-api 2>/dev/null || true
docker rmi sentibr-api:latest 2>/dev/null || true
echo "✅ API antiga removida"
echo ""

# 8. Build
echo "[8/8] Building API (pode demorar 5-10min)..."
docker-compose build --no-cache api
echo "✅ Build concluído"
echo ""

# Iniciar
echo "Iniciando API..."
docker-compose up -d api
echo "✅ API iniciada"
echo ""

# Aguardar
echo "Aguardando API carregar modelo BERT (60s)..."
sleep 60
echo ""

# Status
echo "===================================="
echo "📋 Status da API:"
echo "===================================="
docker ps | grep sentibr-api
echo ""

# Logs
echo "===================================="
echo "📋 Logs (últimas 30 linhas):"
echo "===================================="
docker logs --tail 30 sentibr-api
echo ""

# Testar
echo "===================================="
echo "🧪 Testando API..."
echo "===================================="

if curl -f http://localhost:8000/api/v1/health 2>/dev/null; then
    echo ""
    echo "✅ API FUNCIONANDO!"
    echo ""
    echo "Endpoints disponíveis:"
    echo "  • Docs: http://localhost:8000/docs"
    echo "  • Health: http://localhost:8000/api/v1/health"
    echo "  • Predict: http://localhost:8000/api/v1/predict"
else
    echo ""
    echo "⚠️  API ainda inicializando"
    echo ""
    echo "Aguarde mais 30s e teste:"
    echo "  curl http://localhost:8000/api/v1/health"
    echo ""
    echo "Ver logs:"
    echo "  docker logs -f sentibr-api"
fi

echo ""
echo "===================================="
echo "✅ Instalação Concluída!"
echo "===================================="
