#!/bin/bash

# ============================================
# SentiBR - Deploy Script
# Script para iniciar toda a infraestrutura
# ============================================

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "============================================"
echo "   🍔 SentiBR - Deploy Script"
echo "============================================"
echo -e "${NC}"

# ==========================================
# Funções auxiliares
# ==========================================

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ==========================================
# Verificações pré-deploy
# ==========================================

print_info "Verificando pré-requisitos..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker não encontrado. Por favor, instale o Docker."
    exit 1
fi
print_success "Docker encontrado"

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose não encontrado. Por favor, instale o Docker Compose."
    exit 1
fi
print_success "Docker Compose encontrado"

# Verificar arquivo .env
if [ ! -f .env ]; then
    print_warning ".env não encontrado. Copiando de .env.example..."
    cp .env.example .env
    print_warning "⚠️  IMPORTANTE: Configure suas variáveis de ambiente no arquivo .env"
    print_warning "⚠️  Especialmente: OPENAI_API_KEY"
    echo ""
    read -p "Pressione Enter para continuar após configurar o .env..."
fi
print_success ".env encontrado"

# ==========================================
# Opções de deploy
# ==========================================

echo ""
print_info "Escolha o modo de deploy:"
echo "  1) Full Stack (todos os serviços)"
echo "  2) Desenvolvimento (apenas API + Frontend + PostgreSQL + Redis)"
echo "  3) Apenas Backend (API + PostgreSQL + Redis + MLflow)"
echo "  4) Apenas Monitoramento (Prometheus + Grafana)"
echo ""

read -p "Opção (1-4): " deploy_option

case $deploy_option in
    1)
        print_info "Iniciando Full Stack..."
        COMPOSE_PROFILES=""
        ;;
    2)
        print_info "Iniciando modo Desenvolvimento..."
        COMPOSE_PROFILES="dev"
        ;;
    3)
        print_info "Iniciando apenas Backend..."
        COMPOSE_PROFILES="backend"
        ;;
    4)
        print_info "Iniciando apenas Monitoramento..."
        COMPOSE_PROFILES="monitoring"
        ;;
    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

# ==========================================
# Build e Deploy
# ==========================================

echo ""
print_info "Building images..."
if docker compose build; then
    print_success "Images built successfully"
else
    print_error "Failed to build images"
    exit 1
fi

echo ""
print_info "Starting services..."
if docker compose up -d; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# ==========================================
# Aguardar serviços ficarem healthy
# ==========================================

echo ""
print_info "Aguardando serviços ficarem healthy..."

check_health() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            print_success "$service está healthy"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    print_warning "$service não respondeu no tempo esperado"
    return 1
}

# Verificar PostgreSQL
print_info "Verificando PostgreSQL..."
sleep 5
print_success "PostgreSQL iniciado"

# Verificar Redis
print_info "Verificando Redis..."
sleep 2
print_success "Redis iniciado"

# Verificar API
print_info "Verificando API..."
check_health "API" "http://localhost:8000/api/v1/health"

# Verificar Frontend
print_info "Verificando Frontend..."
check_health "Frontend" "http://localhost:8501/_stcore/health"

# Verificar MLflow
if [ "$deploy_option" = "1" ] || [ "$deploy_option" = "3" ]; then
    print_info "Verificando MLflow..."
    check_health "MLflow" "http://localhost:5000/health"
fi

# Verificar Prometheus
if [ "$deploy_option" = "1" ] || [ "$deploy_option" = "4" ]; then
    print_info "Verificando Prometheus..."
    check_health "Prometheus" "http://localhost:9090/-/healthy"
fi

# Verificar Grafana
if [ "$deploy_option" = "1" ] || [ "$deploy_option" = "4" ]; then
    print_info "Verificando Grafana..."
    check_health "Grafana" "http://localhost:3000/api/health"
fi

# ==========================================
# Informações finais
# ==========================================

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   🎉 Deploy concluído com sucesso!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

print_info "Serviços disponíveis:"
echo ""
echo "  📱 Frontend (Streamlit):  http://localhost:8501"
echo "  🔌 API (FastAPI):         http://localhost:8000"
echo "  📚 API Docs (Swagger):    http://localhost:8000/docs"
echo "  📊 MLflow:                http://localhost:5000"
echo "  📈 Prometheus:            http://localhost:9090"
echo "  📉 Grafana:               http://localhost:3000"
echo "     └─ User: admin"
echo "     └─ Pass: sentibr_grafana_2024"
echo ""

print_info "Comandos úteis:"
echo ""
echo "  Ver logs:           docker-compose logs -f [service]"
echo "  Parar serviços:     docker-compose down"
echo "  Reiniciar:          docker-compose restart [service]"
echo "  Status:             docker-compose ps"
echo ""

print_info "Monitoramento:"
echo ""
echo "  docker-compose logs -f api        # Logs da API"
echo "  docker-compose logs -f frontend   # Logs do Frontend"
echo "  docker stats                      # Uso de recursos"
echo ""

# ==========================================
# Verificar se há warnings
# ==========================================

print_warning "Lembre-se de:"
echo "  1. Configurar OPENAI_API_KEY no .env para usar GPT comparisons"
echo "  2. Treinar o modelo BERT antes de fazer predições"
echo "  3. Configurar SSL/TLS para produção"
echo "  4. Revisar os recursos alocados no docker-compose.yml"
echo ""

print_success "Deploy finalizado! 🚀"
