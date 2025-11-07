#!/bin/bash

# ============================================
# Instalação Completa da API
# ============================================

set -e

echo "🔧 Instalando API..."
echo ""

# 1. Copiar requirements.txt para dentro de api/
echo "[1/6] Copiando requirements.txt para api/..."
if [ -f "requirements.txt" ]; then
    cp requirements.txt api/requirements.txt
    echo "✅ requirements.txt copiado"
elif [ -f "api/requirements.txt" ]; then
    echo "✅ requirements.txt já existe em api/"
else
    echo "❌ requirements.txt não encontrado!"
    echo "   Procure em: $(pwd)"
    exit 1
fi
echo ""

# 2. Substituir Dockerfile
echo "[2/6] Substituindo Dockerfile.api..."
if [ -f "Dockerfile.api.ATUALIZADO" ]; then
    cp docker/Dockerfile.api docker/Dockerfile.api.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    cp Dockerfile.api.ATUALIZADO docker/Dockerfile.api
    echo "✅ Dockerfile substituído"
else
    echo "❌ Dockerfile.api.ATUALIZADO não encontrado!"
    exit 1
fi
echo ""

# 3. Verificar
echo "[3/6] Verificando Dockerfile..."
if grep -q "FROM ubuntu:22.04" docker/Dockerfile.api; then
    echo "✅ Dockerfile correto (Ubuntu)"
else
    echo "❌ Dockerfile incorreto!"
    exit 1
fi
echo ""

# 4. Parar API antiga
echo "[4/6] Parando API antiga..."
docker-compose stop api 2>/dev/null || true
docker rm -f sentibr-api 2>/dev/null || true
echo "✅ API antiga removida"
echo ""

# 5. Remover imagem antiga
echo "[5/6] Removendo imagem antiga..."
docker rmi sentibr-api:latest 2>/dev/null || true
echo "✅ Imagem antiga removida"
echo ""

# 6. Build
echo "[6/6] Building API (pode demorar 5-10min)..."
docker-compose build --no-cache api
echo "✅ Build concluído"
echo ""

# 7. Iniciar
echo "Iniciando API..."
docker-compose up -d api
echo "✅ API iniciada"
echo ""

# 8. Aguardar
echo "Aguardando API inicializar (30s)..."
sleep 30
echo ""

# 9. Mostrar status
echo "===================================="
echo "📋 Status da API:"
echo "===================================="
docker ps | grep sentibr-api || echo "❌ Container não encontrado!"
echo ""

# 10. Mostrar logs
echo "===================================="
echo "📋 Últimos logs:"
echo "===================================="
docker logs --tail 50 sentibr-api
echo ""

# 11. Testar health
echo "===================================="
echo "🔍 Testando health check..."
echo "===================================="
sleep 5
if curl -f http://localhost:8000/api/v1/health 2>/dev/null; then
    echo ""
    echo "✅ API FUNCIONANDO!"
    echo ""
    echo "Acesse: http://localhost:8000/docs"
else
    echo ""
    echo "⚠️  API ainda inicializando ou com erro"
    echo ""
    echo "Ver logs completos:"
    echo "  docker logs -f sentibr-api"
fi
