#!/bin/bash

# ============================================
# SentiBR - Stop & Cleanup Script
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

echo -e "${BLUE}"
echo "============================================"
echo "   🛑 SentiBR - Stop & Cleanup"
echo "============================================"
echo -e "${NC}"

# ==========================================
# Opções
# ==========================================

echo "Escolha uma opção:"
echo "  1) Stop (manter dados)"
echo "  2) Stop e remover containers"
echo "  3) Stop e limpar tudo (CUIDADO: remove volumes!)"
echo ""

read -p "Opção (1-3): " option

case $option in
    1)
        print_info "Parando containers..."
        docker-compose stop
        print_success "Containers parados. Use 'docker-compose start' para reiniciar."
        ;;
    
    2)
        print_info "Parando e removendo containers..."
        docker-compose down
        print_success "Containers removidos. Volumes preservados."
        ;;
    
    3)
        print_warning "ATENÇÃO: Esta ação removerá TODOS os dados!"
        print_warning "Isso inclui: banco de dados, MLflow, Prometheus, Grafana"
        echo ""
        read -p "Tem certeza? Digite 'CONFIRMAR' para continuar: " confirm
        
        if [ "$confirm" = "CONFIRMAR" ]; then
            print_info "Removendo tudo..."
            docker-compose down -v --remove-orphans
            print_success "Tudo removido!"
        else
            print_info "Operação cancelada."
        fi
        ;;
    
    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

echo ""
print_info "Comandos úteis:"
echo "  docker-compose ps          # Ver status"
echo "  docker-compose start       # Reiniciar"
echo "  docker system prune        # Limpar recursos não utilizados"
echo ""
