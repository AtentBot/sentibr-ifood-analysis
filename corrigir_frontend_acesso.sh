#!/bin/bash

# ============================================
# Correção Frontend - Acesso Externo
# ============================================

set -e

echo "🔧 Corrigindo acesso ao Frontend..."
echo ""

# 1. Parar frontend
echo "[1/5] Parando frontend..."
docker-compose stop frontend
echo "✅ Frontend parado"
echo ""

# 2. Ver porta mapeada atual
echo "[2/5] Verificando porta mapeada..."
docker-compose ps frontend | grep frontend
echo ""

# 3. Atualizar docker-compose.yml
echo "[3/5] Atualizando docker-compose.yml..."

# Backup
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)

# Atualizar seção frontend
cat > /tmp/frontend_fix.yml << 'EOF'
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
    image: sentibr-frontend:latest
    container_name: sentibr-frontend
    restart: unless-stopped
    environment:
      API_HOST: http://api
      API_PORT: 8000
      STREAMLIT_SERVER_PORT: 8501
      STREAMLIT_SERVER_ADDRESS: 0.0.0.0
      STREAMLIT_SERVER_HEADLESS: true
    ports:
      - "8502:8501"
    networks:
      - sentibr-network
    depends_on:
      - api
EOF

echo "✅ Configuração atualizada"
echo ""

# 4. Verificar Dockerfile
echo "[4/5] Verificando Dockerfile.frontend..."
if grep -q "server.address=0.0.0.0" docker/Dockerfile.frontend; then
    echo "✅ Dockerfile correto"
else
    echo "⚠️  Atualizando Dockerfile..."
    cat > docker/Dockerfile.frontend << 'EOF'
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    python3.10 \
    python3-pip \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /root/.streamlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["python3", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
EOF
    echo "✅ Dockerfile atualizado"
fi
echo ""

# 5. Rebuild e restart
echo "[5/5] Rebuild do frontend..."
docker-compose build --no-cache frontend
echo "✅ Build concluído"
echo ""

echo "Iniciando frontend..."
docker-compose up -d frontend
echo "✅ Frontend iniciado"
echo ""

# Aguardar
echo "Aguardando frontend inicializar (30s)..."
sleep 30
echo ""

# Testar
echo "===================================="
echo "🧪 Testando acesso..."
echo "===================================="

if curl -f http://localhost:8502 > /dev/null 2>&1; then
    echo "✅ FRONTEND ACESSÍVEL!"
    echo ""
    echo "Acesse: http://localhost:8502"
else
    echo "⚠️  Ainda não acessível"
    echo ""
    echo "Ver logs:"
    echo "  docker logs sentibr-frontend"
    echo ""
    echo "Testar manualmente:"
    echo "  curl http://localhost:8502"
fi
echo ""
