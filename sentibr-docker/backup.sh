#!/bin/bash

# ============================================
# SentiBR - Backup Script
# Backup de dados críticos
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
# Configurações
# ==========================================

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="sentibr_backup_${TIMESTAMP}"

echo -e "${BLUE}"
echo "============================================"
echo "   💾 SentiBR - Backup Script"
echo "============================================"
echo -e "${NC}"

# Criar diretório de backup
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

print_info "Backup será salvo em: $BACKUP_DIR/$BACKUP_NAME"
echo ""

# ==========================================
# Backup PostgreSQL
# ==========================================

print_info "Fazendo backup do PostgreSQL..."

# Obter credenciais do .env
source .env

# Fazer backup
docker exec sentibr-postgres pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -F c \
    -f /tmp/postgres_backup.dump

# Copiar backup para host
docker cp sentibr-postgres:/tmp/postgres_backup.dump \
    "$BACKUP_DIR/$BACKUP_NAME/postgres_backup.dump"

print_success "PostgreSQL backup concluído"

# ==========================================
# Backup MLflow
# ==========================================

print_info "Fazendo backup do MLflow..."

# Backup de artifacts e metadata
docker run --rm \
    --volumes-from sentibr-mlflow \
    -v "$PWD/$BACKUP_DIR/$BACKUP_NAME:/backup" \
    alpine \
    tar czf /backup/mlflow_data.tar.gz /mlflow

print_success "MLflow backup concluído"

# ==========================================
# Backup Grafana
# ==========================================

print_info "Fazendo backup do Grafana..."

# Backup de dashboards e configurações
docker run --rm \
    --volumes-from sentibr-grafana \
    -v "$PWD/$BACKUP_DIR/$BACKUP_NAME:/backup" \
    alpine \
    tar czf /backup/grafana_data.tar.gz /var/lib/grafana

print_success "Grafana backup concluído"

# ==========================================
# Backup Prometheus
# ==========================================

print_info "Fazendo backup do Prometheus..."

docker run --rm \
    --volumes-from sentibr-prometheus \
    -v "$PWD/$BACKUP_DIR/$BACKUP_NAME:/backup" \
    alpine \
    tar czf /backup/prometheus_data.tar.gz /prometheus

print_success "Prometheus backup concluído"

# ==========================================
# Backup Modelos
# ==========================================

print_info "Fazendo backup dos modelos..."

if [ -d "../models" ]; then
    tar czf "$BACKUP_DIR/$BACKUP_NAME/models.tar.gz" -C .. models
    print_success "Modelos backup concluído"
else
    print_warning "Diretório de modelos não encontrado"
fi

# ==========================================
# Criar arquivo de metadados
# ==========================================

print_info "Criando arquivo de metadados..."

cat > "$BACKUP_DIR/$BACKUP_NAME/backup_info.txt" << EOF
============================================
SentiBR Backup Information
============================================

Date: $(date)
Timestamp: $TIMESTAMP
Backup Name: $BACKUP_NAME

Contents:
- PostgreSQL database dump
- MLflow artifacts and metadata
- Grafana dashboards and settings
- Prometheus data
- Model files

PostgreSQL Info:
- Database: $POSTGRES_DB
- User: $POSTGRES_USER

To restore:
1. Stop all services: ./stop.sh
2. Restore PostgreSQL: cat postgres_backup.dump | docker exec -i sentibr-postgres pg_restore -U $POSTGRES_USER -d $POSTGRES_DB
3. Extract volumes: tar xzf mlflow_data.tar.gz -C /
4. Start services: ./deploy.sh

============================================
EOF

print_success "Metadados criados"

# ==========================================
# Compactar tudo
# ==========================================

print_info "Compactando backup completo..."

cd "$BACKUP_DIR"
tar czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"
cd ..

# ==========================================
# Finalização
# ==========================================

BACKUP_SIZE=$(du -h "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" | cut -f1)

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   ✓ Backup concluído com sucesso!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
print_info "Arquivo: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
print_info "Tamanho: $BACKUP_SIZE"
echo ""

# ==========================================
# Limpeza de backups antigos (opcional)
# ==========================================

print_warning "Limpeza de backups antigos:"
echo "  Para manter apenas os últimos N backups:"
echo "  ls -t $BACKUP_DIR/sentibr_backup_*.tar.gz | tail -n +6 | xargs rm -f"
echo ""

print_success "Backup finalizado! 💾"
