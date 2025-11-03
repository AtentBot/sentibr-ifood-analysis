#!/bin/bash

# ============================================
# SentiBR - Quickstart Script
# ============================================

set -e  # Exit on error

echo "============================================"
echo "🚀 SentiBR - Inicialização Rápida"
echo "============================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. Verificar Python
print_status "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION encontrado"
else
    print_error "Python 3 não encontrado. Instale Python 3.10+ primeiro."
    exit 1
fi

# 2. Criar ambiente virtual
print_status "Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Ambiente virtual criado"
else
    print_warning "Ambiente virtual já existe"
fi

# 3. Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate
print_success "Ambiente virtual ativado"

# 4. Atualizar pip
print_status "Atualizando pip..."
pip install --upgrade pip --quiet
print_success "Pip atualizado"

# 5. Instalar dependências
print_status "Instalando dependências (isso pode demorar alguns minutos)..."
pip install -r requirements.txt --quiet
print_success "Dependências instaladas"

# 6. Configurar .env
if [ ! -f ".env" ]; then
    print_status "Criando arquivo .env..."
    cp .env.example .env
    print_warning "Arquivo .env criado. IMPORTANTE: Configure suas API keys!"
    echo ""
    echo "   Edite o arquivo .env e configure:"
    echo "   - OPENAI_API_KEY (para geração de dados sintéticos e LLM evaluation)"
    echo ""
else
    print_warning ".env já existe"
fi

# 7. Verificar setup
print_status "Verificando configuração..."
python scripts/check_setup.py

echo ""
echo "============================================"
echo "✅ Setup concluído com sucesso!"
echo "============================================"
echo ""
echo "📚 Próximos passos:"
echo ""
echo "1️⃣  Configure suas API keys no .env:"
echo "   nano .env"
echo ""
echo "2️⃣  Carregar dataset B2W-Reviews01:"
echo "   python src/data/load_data.py"
echo ""
echo "3️⃣  (Opcional) Gerar dados sintéticos iFood:"
echo "   python src/data/generate_synthetic_data.py"
echo ""
echo "4️⃣  Explorar dados no notebook:"
echo "   jupyter notebook notebooks/01_eda.ipynb"
echo ""
echo "5️⃣  Treinar modelo (após preparar dados):"
echo "   python src/training/train.py"
echo ""
echo "6️⃣  Iniciar API:"
echo "   uvicorn src.api.main:app --reload"
echo ""
echo "7️⃣  Iniciar Frontend:"
echo "   streamlit run frontend/app.py"
echo ""
echo "============================================"
echo "📖 Documentação: README.md"
echo "🐛 Issues: https://github.com/seu-usuario/sentibr-ifood-analysis/issues"
echo "============================================"
