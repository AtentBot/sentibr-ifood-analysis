#!/bin/bash

# ============================================
# Configuração Automática do Grafana
# ============================================

set -e

GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASS="sentibr_grafana_2024"

echo "📊 Configurando Grafana automaticamente..."
echo ""

# 1. Aguardar Grafana estar pronto
echo "[1/4] Aguardando Grafana inicializar..."
for i in {1..30}; do
    if curl -s "$GRAFANA_URL/api/health" > /dev/null 2>&1; then
        echo "✅ Grafana online!"
        break
    fi
    echo "   Tentativa $i/30..."
    sleep 2
done
echo ""

# 2. Adicionar Prometheus como Data Source
echo "[2/4] Adicionando Prometheus como Data Source..."
curl -X POST "$GRAFANA_URL/api/datasources" \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_USER:$GRAFANA_PASS" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }' 2>/dev/null && echo "✅ Prometheus adicionado!" || echo "⚠️  Prometheus já existe"
echo ""

# 3. Importar Dashboard
echo "[3/4] Importando dashboard..."
if [ -f "dashboard_sentibr.json" ]; then
    curl -X POST "$GRAFANA_URL/api/dashboards/db" \
      -H "Content-Type: application/json" \
      -u "$GRAFANA_USER:$GRAFANA_PASS" \
      -d @dashboard_sentibr.json 2>/dev/null && \
      echo "✅ Dashboard importado!" || \
      echo "⚠️  Dashboard já existe ou erro ao importar"
else
    echo "❌ dashboard_sentibr.json não encontrado!"
    echo "   Baixe de: dashboard_sentibr.json"
fi
echo ""

# 4. Criar Alertas Básicos
echo "[4/4] Configurando alertas..."
echo "⚠️  Alertas devem ser configurados manualmente no Grafana"
echo ""

echo "===================================="
echo "✅ Configuração Concluída!"
echo "===================================="
echo ""
echo "Acesse: $GRAFANA_URL"
echo "Usuário: $GRAFANA_USER"
echo "Senha: $GRAFANA_PASS"
echo ""
echo "Dashboard disponível em:"
echo "  → Dashboards → Browse → SentiBR - Monitoramento Geral"
echo ""
