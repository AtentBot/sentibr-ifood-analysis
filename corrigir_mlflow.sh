#!/bin/bash

# ============================================
# Script de Correção do MLflow
# ============================================

set -e

echo "🔧 Corrigindo MLflow SentiBR..."
echo ""

# 1. Parar serviços
echo "[1/8] Parando serviços..."
docker-compose down
echo "✅ Serviços parados"
echo ""

# 2. Remover containers antigos
echo "[2/8] Removendo containers antigos..."
docker rm -f sentibr-mlflow 2>/dev/null || true
docker rmi -f sentibr-mlflow:latest 2>/dev/null || true
echo "✅ Containers removidos"
echo ""

# 3. Criar estrutura de diretórios
echo "[3/8] Criando estrutura de diretórios..."
mkdir -p mlflow/artifacts
mkdir -p mlflow/mlruns
mkdir -p mlflow/backend
echo "✅ Diretórios criados"
echo ""

# 4. Definir permissões corretas
echo "[4/8] Ajustando permissões..."
chmod -R 777 mlflow/
echo "✅ Permissões ajustadas"
echo ""

# 5. Inicializar banco de dados SQLite
echo "[5/8] Inicializando banco de dados..."
touch mlflow/mlruns/mlflow.db
chmod 666 mlflow/mlruns/mlflow.db
echo "✅ Banco de dados inicializado"
echo ""

# 6. Backup do docker-compose antigo
echo "[6/8] Fazendo backup do docker-compose..."
if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml docker-compose.yml.backup
    echo "✅ Backup criado: docker-compose.yml.backup"
else
    echo "⚠️  docker-compose.yml não encontrado"
fi
echo ""

# 7. Copiar nova configuração
echo "[7/8] Aplicando nova configuração..."
if [ -f "docker-compose-mlflow-corrigido.yml" ]; then
    cp docker-compose-mlflow-corrigido.yml docker-compose.yml
    echo "✅ Nova configuração aplicada"
else
    echo "❌ Arquivo docker-compose-mlflow-corrigido.yml não encontrado!"
    echo "   Baixe o arquivo primeiro"
    exit 1
fi
echo ""

# 8. Iniciar MLflow
echo "[8/8] Iniciando MLflow..."
docker-compose up -d mlflow
echo "✅ MLflow iniciado"
echo ""

# Aguardar inicialização
echo "Aguardando MLflow inicializar (30s)..."
for i in {1..30}; do
    printf "."
    sleep 1
done
echo ""
echo ""

# Verificar saúde
echo "===================================="
echo "🔍 Verificando MLflow:"
echo "===================================="

if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ MLflow está ONLINE!"
    echo ""
    echo "===================================="
    echo "🎉 CORREÇÃO CONCLUÍDA!"
    echo "===================================="
    echo ""
    echo "Acesse: http://localhost:5000"
    echo ""
    echo "Teste criar um experimento!"
else
    echo "⚠️  MLflow ainda inicializando..."
    echo ""
    echo "Aguarde mais 30s e teste:"
    echo "  curl http://localhost:5000/health"
    echo ""
    echo "Ver logs:"
    echo "  docker logs -f sentibr-mlflow"
fi

echo ""
echo "===================================="
echo "📋 Comandos Úteis:"
echo "===================================="
echo ""
echo "Ver logs:"
echo "  docker logs -f sentibr-mlflow"
echo ""
echo "Reiniciar:"
echo "  docker-compose restart mlflow"
echo ""
echo "Verificar saúde:"
echo "  curl http://localhost:5000/health"
echo ""
echo "Acessar bash:"
echo "  docker exec -it sentibr-mlflow sh"
echo ""
