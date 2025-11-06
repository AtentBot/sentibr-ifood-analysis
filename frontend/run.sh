#!/bin/bash

# ============================================
# SentiBR Frontend - Script de Demonstração
# ============================================

echo "============================================"
echo "🍔 SentiBR - Frontend Streamlit"
echo "============================================"
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${BLUE}[1/4]${NC} Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION encontrado"
else
    echo -e "${RED}✗${NC} Python 3 não encontrado"
    exit 1
fi

# Verificar/Instalar dependências
echo ""
echo -e "${BLUE}[2/4]${NC} Verificando dependências..."
if pip3 show streamlit &> /dev/null; then
    echo -e "${GREEN}✓${NC} Streamlit já instalado"
else
    echo "Instalando dependências..."
    pip3 install -r frontend/requirements.txt
fi

# Verificar API
echo ""
echo -e "${BLUE}[3/4]${NC} Verificando API..."
API_URL="http://localhost:8000/api/v1/health"

if curl -s --fail $API_URL > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API está online em http://localhost:8000"
else
    echo -e "${RED}⚠${NC} API não está respondendo em http://localhost:8000"
    echo ""
    echo "Para iniciar a API, execute em outro terminal:"
    echo "  cd .. && uvicorn src.api.main:app --reload"
    echo ""
    echo "O frontend pode ser iniciado sem a API, mas as funcionalidades"
    echo "de predição não estarão disponíveis."
    echo ""
fi

# Iniciar Streamlit
echo ""
echo -e "${BLUE}[4/4]${NC} Iniciando Frontend..."
echo ""
echo "============================================"
echo "🎨 Frontend Streamlit será iniciado"
echo "============================================"
echo ""
echo "📍 URL: http://localhost:8501"
echo ""
echo "📚 Páginas disponíveis:"
echo "   🏠 Home - Visão geral do projeto"
echo "   📝 Análise - Interface de predição"
echo "   📊 Métricas - Dashboard em tempo real"
echo "   💬 Feedback - Sistema de validação"
echo "   🔍 Monitor - Detecção de drift"
echo ""
echo "⌨️  Pressione Ctrl+C para parar"
echo ""
echo "============================================"
echo ""

# Iniciar Streamlit
cd frontend && streamlit run app.py
