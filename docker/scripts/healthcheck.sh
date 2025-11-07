#!/bin/bash

# ============================================
# SentiBR - Health Check Script
# Verifica saúde de todos os serviços
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

# ==========================================
# Funções de verificação
# ==========================================

check_service() {
    local name=$1
    local url=$2
    local max_attempts=${3:-30}
    local attempt=0
    
    print_info "Verificando $name..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            print_success "$name está saudável"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    print_error "$name não está respondendo"
    return 1
}

check_container() {
    local container=$1
    
    if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-health")
        
        if [ "$health" = "healthy" ] || [ "$health" = "no-health" ]; then
            print_success "$container está rodando"
            return 0
        else
            print_warning "$container está rodando mas não healthy (status: $health)"
            return 1
        fi
    else
        print_error "$container não está rodando"
        return 1
    fi
}

# ==========================================
# Banner
# ==========================================

echo -e "${BLUE}"
echo "============================================"
echo "   🏥 SentiBR - Health Check"
echo "============================================"
echo -e "${NC}"

# ==========================================
# Verificar Docker
# ==========================================

print_info "Verificando Docker..."

if ! docker info > /dev/null 2>&1; then
    print_error "Docker não está rodando"
    exit 1
fi

print_success "Docker está rodando"

# ==========================================
# Verificar Containers
# ==========================================

echo ""
print_info "Verificando Containers..."
echo ""

CONTAINERS=(
    "sentibr-postgres"
    "sentibr-redis"
    "sentibr-mlflow"
    "sentibr-api"
    "sentibr-frontend"
    "sentibr-prometheus"
    "sentibr-grafana"
    "sentibr-nginx"
)

CONTAINER_FAILURES=0

for container in "${CONTAINERS[@]}"; do
    if ! check_container "$container"; then
        CONTAINER_FAILURES=$((CONTAINER_FAILURES + 1))
    fi
done

# ==========================================
# Verificar Endpoints
# ==========================================

echo ""
print_info "Verificando Endpoints..."
echo ""

ENDPOINTS=(
    "API:http://localhost:8000/api/v1/health"
    "Frontend:http://localhost:8501/_stcore/health"
    "MLflow:http://localhost:5000/health"
    "Prometheus:http://localhost:9090/-/healthy"
    "Grafana:http://localhost:3000/api/health"
    "Nginx:http://localhost/health"
)

ENDPOINT_FAILURES=0

for endpoint in "${ENDPOINTS[@]}"; do
    IFS=':' read -r name url <<< "$endpoint"
    if ! check_service "$name" "$url" 10; then
        ENDPOINT_FAILURES=$((ENDPOINT_FAILURES + 1))
    fi
done

# ==========================================
# Verificar Banco de Dados
# ==========================================

echo ""
print_info "Verificando PostgreSQL..."

if docker exec sentibr-postgres pg_isready -U sentibr_user -d sentibr > /dev/null 2>&1; then
    print_success "PostgreSQL está aceitando conexões"
    
    # Verificar tabelas
    TABLE_COUNT=$(docker exec sentibr-postgres psql -U sentibr_user -d sentibr -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema IN ('predictions', 'feedback', 'metrics')" 2>/dev/null || echo "0")
    
    if [ "$TABLE_COUNT" -gt 0 ]; then
        print_success "Schema do banco está OK ($TABLE_COUNT tabelas)"
    else
        print_warning "Schema do banco pode estar incompleto"
    fi
else
    print_error "PostgreSQL não está aceitando conexões"
    ENDPOINT_FAILURES=$((ENDPOINT_FAILURES + 1))
fi

# ==========================================
# Verificar Redis
# ==========================================

echo ""
print_info "Verificando Redis..."

if docker exec sentibr-redis redis-cli -a sentibr_redis_2024 ping 2>/dev/null | grep -q "PONG"; then
    print_success "Redis está respondendo"
else
    print_error "Redis não está respondendo"
    ENDPOINT_FAILURES=$((ENDPOINT_FAILURES + 1))
fi

# ==========================================
# Estatísticas de Recursos
# ==========================================

echo ""
print_info "Estatísticas de Recursos..."
echo ""

docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | head -n 9

# ==========================================
# Resumo
# ==========================================

echo ""
echo -e "${BLUE}============================================${NC}"

TOTAL_FAILURES=$((CONTAINER_FAILURES + ENDPOINT_FAILURES))

if [ $TOTAL_FAILURES -eq 0 ]; then
    echo -e "${GREEN}   ✓ Todos os serviços estão saudáveis!${NC}"
    echo -e "${BLUE}============================================${NC}"
    exit 0
else
    echo -e "${RED}   ✗ $TOTAL_FAILURES problemas detectados${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
    print_warning "Execute 'docker-compose logs [service]' para investigar"
    exit 1
fi
