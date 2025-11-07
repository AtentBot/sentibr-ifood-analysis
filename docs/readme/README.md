# 🐳 SentiBR - Docker Deployment

Infraestrutura completa em containers Docker para o projeto SentiBR.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Quick Start](#quick-start)
- [Serviços](#serviços)
- [Configuração](#configuração)
- [Scripts de Gerenciamento](#scripts-de-gerenciamento)
- [Monitoramento](#monitoramento)
- [Backup e Restore](#backup-e-restore)
- [Troubleshooting](#troubleshooting)
- [Produção](#produção)

## 🎯 Visão Geral

O SentiBR utiliza uma arquitetura de microserviços containerizada com Docker Compose, incluindo:

- **API Backend** (FastAPI)
- **Frontend** (Streamlit)
- **Banco de Dados** (PostgreSQL)
- **Cache** (Redis)
- **ML Tracking** (MLflow)
- **Monitoramento** (Prometheus + Grafana)
- **Reverse Proxy** (Nginx)

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                         Nginx                            │
│                    (Reverse Proxy)                       │
└──────┬──────────────────┬─────────────────┬─────────────┘
       │                  │                 │
   ┌───▼────┐      ┌──────▼───────┐   ┌────▼──────┐
   │Frontend│      │     API      │   │  Grafana  │
   │Streamlit│     │   FastAPI    │   │           │
   └────────┘      └──┬───────┬───┘   └─────┬─────┘
                      │       │             │
            ┌─────────┼───┬───┼─────────────┘
            │         │   │   │
        ┌───▼──┐  ┌───▼┐ │ ┌─▼────────┐
        │Redis │  │PG  │ │ │Prometheus│
        │Cache │  │SQL │ │ └──────────┘
        └──────┘  └────┘ │
                    ┌────▼─────┐
                    │  MLflow  │
                    └──────────┘
```

## 🔧 Pré-requisitos

### Software Necessário

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git**
- **Bash** (para scripts de gerenciamento)

### Recursos Mínimos Recomendados

- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disco**: 20 GB livres
- **SO**: Linux, macOS, ou Windows com WSL2

### Verificar Instalação

```bash
docker --version
docker-compose --version
```

## 🚀 Quick Start

### 1. Clone e Configure

```bash
# Clone o repositório
git clone https://github.com/your-repo/sentibr.git
cd sentibr

# Copie o arquivo de ambiente
cp .env.example .env

# IMPORTANTE: Configure suas variáveis
nano .env  # ou vim, code, etc.
```

### 2. Configure OpenAI API Key

Edite o arquivo `.env` e adicione sua chave:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Deploy

```bash
# Tornar scripts executáveis
chmod +x deploy.sh stop.sh backup.sh

# Iniciar todos os serviços
./deploy.sh
```

### 4. Acesse os Serviços

Após alguns minutos:

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/sentibr_grafana_2024)
- **Prometheus**: http://localhost:9090
- **MLflow**: http://localhost:5000

## 📦 Serviços

### 1. API (FastAPI)

```yaml
Container: sentibr-api
Porta: 8000
Recursos: 4 CPU, 8GB RAM
```

**Endpoints principais:**
- `GET /api/v1/health` - Health check
- `POST /api/v1/predict` - Predição individual
- `POST /api/v1/predict/batch` - Predição em lote
- `POST /api/v1/predict/compare` - Comparação BERT vs GPT
- `GET /api/v1/metrics` - Métricas Prometheus

### 2. Frontend (Streamlit)

```yaml
Container: sentibr-frontend
Porta: 8501
Recursos: 2 CPU, 4GB RAM
```

### 3. PostgreSQL

```yaml
Container: sentibr-postgres
Porta: 5432
Recursos: 1 CPU, 1GB RAM
Volume: postgres-data
```

**Schemas:**
- `predictions` - Armazena predições
- `feedback` - Armazena feedbacks
- `metrics` - Métricas agregadas

### 4. Redis

```yaml
Container: sentibr-redis
Porta: 6379
Recursos: 0.5 CPU, 512MB RAM
Volume: redis-data
```

### 5. MLflow

```yaml
Container: sentibr-mlflow
Porta: 5000
Recursos: 1 CPU, 2GB RAM
Volume: mlflow-data
```

### 6. Prometheus

```yaml
Container: sentibr-prometheus
Porta: 9090
Recursos: 1 CPU, 2GB RAM
Volume: prometheus-data
```

### 7. Grafana

```yaml
Container: sentibr-grafana
Porta: 3000
Recursos: 1 CPU, 1GB RAM
Volume: grafana-data
```

**Dashboards pré-configurados:**
- SentiBR Overview
- API Performance
- Model Metrics
- Infrastructure

### 8. Nginx

```yaml
Container: sentibr-nginx
Portas: 80, 443
Recursos: 0.5 CPU, 256MB RAM
```

## ⚙️ Configuração

### Variáveis de Ambiente

Principais variáveis no `.env`:

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
POSTGRES_PASSWORD=change-me
DATABASE_URL=postgresql://...

# Redis
REDIS_PASSWORD=change-me

# OpenAI
OPENAI_API_KEY=sk-your-key

# Model
MODEL_NAME=neuralmind/bert-base-portuguese-cased
BATCH_SIZE=16

# API
WORKERS=4
```

### Customizar Recursos

Edite `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '4'      # Ajuste aqui
          memory: 8G     # Ajuste aqui
```

### Configurar Grafana

1. Acesse http://localhost:3000
2. Login: `admin` / `sentibr_grafana_2024`
3. Dashboards estão em: Dashboards → Browse → SentiBR

### Configurar Alertas Prometheus

Edite `docker/prometheus/alerts.yml`:

```yaml
- alert: CustomAlert
  expr: your_metric > threshold
  for: 5m
  annotations:
    summary: "Your custom alert"
```

## 🛠️ Scripts de Gerenciamento

### deploy.sh

Script principal de deployment:

```bash
./deploy.sh

# Opções:
# 1) Full Stack (todos serviços)
# 2) Development (API + Frontend + DB + Redis)
# 3) Backend Only (API + DB + Redis + MLflow)
# 4) Monitoring Only (Prometheus + Grafana)
```

### stop.sh

Parar e limpar containers:

```bash
./stop.sh

# Opções:
# 1) Stop (manter dados)
# 2) Stop e remover containers
# 3) Stop e limpar tudo (CUIDADO!)
```

### backup.sh

Backup completo dos dados:

```bash
./backup.sh

# Cria backup de:
# - PostgreSQL database
# - MLflow artifacts
# - Grafana dashboards
# - Prometheus data
# - Model files
```

## 📊 Monitoramento

### Métricas Disponíveis

**API Metrics:**
- Request rate
- Latency (P50, P95, P99)
- Error rate
- Status codes

**Model Metrics:**
- Predictions per minute
- Confidence scores
- Sentiment distribution
- Inference time

**Infrastructure:**
- CPU usage
- Memory usage
- Disk usage
- Network I/O

### Dashboards Grafana

**SentiBR Overview:**
- Total predictions
- Average latency
- SLA compliance
- Sentiment distribution

**API Performance:**
- Request rate by endpoint
- Latency percentiles
- Error rates
- Cache hit rate

**Model Metrics:**
- Prediction confidence
- Aspect distribution
- Data drift detection
- Feedback analysis

### Alertas Configurados

- API Down (critical)
- High Error Rate (warning)
- High Latency (warning)
- SLA Violation (critical)
- Low Prediction Confidence (warning)
- Data Drift Detected (warning)

## 💾 Backup e Restore

### Fazer Backup

```bash
# Backup completo
./backup.sh

# Backup é salvo em: ./backups/sentibr_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Restaurar Backup

```bash
# 1. Extrair backup
cd backups
tar xzf sentibr_backup_YYYYMMDD_HHMMSS.tar.gz

# 2. Parar serviços
./stop.sh

# 3. Restaurar PostgreSQL
cat backups/sentibr_backup_*/postgres_backup.dump | \
  docker exec -i sentibr-postgres pg_restore -U sentibr_user -d sentibr

# 4. Restaurar volumes
docker run --rm -v sentibr-mlflow-data:/mlflow \
  -v $(pwd)/backups/sentibr_backup_*:/backup alpine \
  sh -c "cd / && tar xzf /backup/mlflow_data.tar.gz"

# 5. Reiniciar serviços
./deploy.sh
```

### Backup Automático

Configure um cron job:

```bash
# Editar crontab
crontab -e

# Adicionar backup diário às 2 AM
0 2 * * * cd /path/to/sentibr && ./backup.sh
```

## 🔍 Troubleshooting

### Serviço não inicia

```bash
# Ver logs
docker-compose logs -f [service-name]

# Verificar status
docker-compose ps

# Reiniciar serviço específico
docker-compose restart [service-name]
```

### API retorna erro 500

```bash
# Ver logs da API
docker-compose logs -f api

# Verificar conexão com banco
docker exec sentibr-api curl -f http://postgres:5432

# Verificar modelo
docker exec sentibr-api ls -la /app/models/
```

### Alto uso de memória

```bash
# Ver uso de recursos
docker stats

# Ajustar limites no docker-compose.yml
# ou aumentar swap do sistema
```

### Banco de dados corrompido

```bash
# Parar serviços
./stop.sh

# Restaurar último backup
# (ver seção Backup e Restore)

# Reiniciar
./deploy.sh
```

### Porta já em uso

```bash
# Verificar portas em uso
netstat -tlnp | grep :8000

# Matar processo
kill -9 <PID>

# Ou alterar portas no docker-compose.yml
```

## 🚀 Produção

### Checklist de Produção

- [ ] Alterar todas as senhas padrão
- [ ] Configurar SSL/TLS (Nginx)
- [ ] Habilitar autenticação (API endpoints)
- [ ] Configurar firewall
- [ ] Limitar rate limiting
- [ ] Configurar backup automático
- [ ] Configurar log rotation
- [ ] Configurar alertas (email/Slack)
- [ ] Testar disaster recovery
- [ ] Documentar runbooks
- [ ] Configurar CI/CD
- [ ] Testar escalabilidade

### SSL/TLS com Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... resto da configuração
}
```

### Scaling

Para escalar serviços:

```bash
# Escalar API para 3 instâncias
docker-compose up -d --scale api=3
```

### Cloud Deployment

Para deploy em cloud (AWS, GCP, Azure):

1. Use **Kubernetes** (k8s) com os manifestos em `k8s/`
2. Configure **Load Balancer** externo
3. Use **Managed Database** (RDS, Cloud SQL)
4. Configure **Object Storage** (S3, GCS) para modelos
5. Use **Secrets Manager** para credenciais

## 📚 Documentação Adicional

- [API Documentation](../docs/API.md)
- [Model Training](../docs/TRAINING.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [Contributing](../CONTRIBUTING.md)

## 🤝 Suporte

- **Issues**: https://github.com/your-repo/sentibr/issues
- **Discussions**: https://github.com/your-repo/sentibr/discussions
- **Email**: support@sentibr.com

## 📝 Licença

MIT License - Ver [LICENSE](../LICENSE) para detalhes.

---

Desenvolvido com ❤️ pela equipe SentiBR
