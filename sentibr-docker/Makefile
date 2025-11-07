# ============================================
# SentiBR - Makefile
# Comandos úteis para gerenciamento
# ============================================

.PHONY: help build up down restart logs ps clean backup test migrate

# Cores
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# Variáveis
COMPOSE := docker-compose
COMPOSE_DEV := docker-compose -f docker-compose.yml -f docker-compose.dev.yml

##@ Gerenciamento

help: ## Mostra esta mensagem de ajuda
	@awk 'BEGIN {FS = ":.*##"; printf "\n${GREEN}Usage:${NC}\n  make ${YELLOW}<target>${NC}\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  ${GREEN}%-15s${NC} %s\n", $$1, $$2 } /^##@/ { printf "\n${YELLOW}%s${NC}\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

build: ## Build de todas as imagens
	@echo "$(GREEN)Building images...$(NC)"
	$(COMPOSE) build

up: ## Inicia todos os serviços
	@echo "$(GREEN)Starting services...$(NC)"
	$(COMPOSE) up -d
	@echo "$(GREEN)Services started! Check status with 'make ps'$(NC)"

down: ## Para todos os serviços
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(COMPOSE) down

restart: ## Reinicia todos os serviços
	@echo "$(YELLOW)Restarting services...$(NC)"
	$(COMPOSE) restart

stop: ## Para serviços sem remover
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(COMPOSE) stop

start: ## Inicia serviços parados
	@echo "$(GREEN)Starting services...$(NC)"
	$(COMPOSE) start

##@ Desenvolvimento

dev: ## Inicia em modo desenvolvimento (com hot reload)
	@echo "$(GREEN)Starting in development mode...$(NC)"
	$(COMPOSE_DEV) up -d

dev-build: ## Build para desenvolvimento
	@echo "$(GREEN)Building for development...$(NC)"
	$(COMPOSE_DEV) build

dev-logs: ## Logs em modo desenvolvimento
	$(COMPOSE_DEV) logs -f

##@ Monitoramento

ps: ## Lista status dos containers
	$(COMPOSE) ps

logs: ## Mostra logs de todos os serviços
	$(COMPOSE) logs -f

logs-api: ## Logs da API
	$(COMPOSE) logs -f api

logs-frontend: ## Logs do Frontend
	$(COMPOSE) logs -f frontend

logs-db: ## Logs do PostgreSQL
	$(COMPOSE) logs -f postgres

stats: ## Mostra estatísticas de recursos
	docker stats

##@ Database

db-shell: ## Acessa shell do PostgreSQL
	docker exec -it sentibr-postgres psql -U sentibr_user -d sentibr

db-backup: ## Backup do banco de dados
	@echo "$(GREEN)Creating database backup...$(NC)"
	./backup.sh

db-migrate: ## Executa migrações
	docker exec sentibr-api alembic upgrade head

db-reset: ## CUIDADO: Reseta o banco de dados
	@echo "$(YELLOW)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(COMPOSE) exec postgres psql -U sentibr_user -d sentibr -c "DROP SCHEMA predictions CASCADE; DROP SCHEMA feedback CASCADE; DROP SCHEMA metrics CASCADE;"; \
		$(COMPOSE) exec postgres psql -U sentibr_user -d sentibr -f /docker-entrypoint-initdb.d/init-db.sql; \
		echo "\n$(GREEN)Database reset complete$(NC)"; \
	fi

##@ Cache

redis-cli: ## Acessa Redis CLI
	docker exec -it sentibr-redis redis-cli -a sentibr_redis_2024

redis-flush: ## Limpa todo o cache
	docker exec sentibr-redis redis-cli -a sentibr_redis_2024 FLUSHALL

cache-stats: ## Estatísticas do cache
	docker exec sentibr-redis redis-cli -a sentibr_redis_2024 INFO stats

##@ Testing

test: ## Executa testes
	docker exec sentibr-api pytest tests/ -v

test-unit: ## Testes unitários
	docker exec sentibr-api pytest tests/unit/ -v

test-integration: ## Testes de integração
	docker exec sentibr-api pytest tests/integration/ -v

test-coverage: ## Testes com coverage
	docker exec sentibr-api pytest tests/ --cov=src --cov-report=html

load-test: ## Load testing
	docker exec sentibr-api locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 1m

##@ Limpeza

clean: ## Remove containers, volumes e imagens
	@echo "$(YELLOW)Cleaning up...$(NC)"
	$(COMPOSE) down -v --remove-orphans
	docker system prune -f

clean-volumes: ## Remove apenas volumes
	@echo "$(YELLOW)Removing volumes...$(NC)"
	$(COMPOSE) down -v

clean-images: ## Remove imagens do projeto
	@echo "$(YELLOW)Removing images...$(NC)"
	docker rmi $$(docker images | grep sentibr | aq '{print $$3}')

clean-logs: ## Limpa arquivos de log
	@echo "$(YELLOW)Cleaning logs...$(NC)"
	rm -rf ../logs/*.log

##@ Serviços Individuais

api-restart: ## Reinicia apenas a API
	$(COMPOSE) restart api

frontend-restart: ## Reinicia apenas o Frontend
	$(COMPOSE) restart frontend

api-shell: ## Acessa shell da API
	docker exec -it sentibr-api /bin/bash

frontend-shell: ## Acessa shell do Frontend
	docker exec -it sentibr-frontend /bin/bash

##@ Monitoring

grafana: ## Abre Grafana no browser
	@echo "Opening Grafana at http://localhost:3000"
	@open http://localhost:3000 || xdg-open http://localhost:3000

prometheus: ## Abre Prometheus no browser
	@echo "Opening Prometheus at http://localhost:9090"
	@open http://localhost:9090 || xdg-open http://localhost:9090

mlflow: ## Abre MLflow no browser
	@echo "Opening MLflow at http://localhost:5000"
	@open http://localhost:5000 || xdg-open http://localhost:5000

##@ Úteis

health: ## Verifica health de todos os serviços
	@echo "$(GREEN)Checking service health...$(NC)"
	@echo "\nAPI:"
	@curl -f http://localhost:8000/api/v1/health || echo "$(YELLOW)API not ready$(NC)"
	@echo "\nFrontend:"
	@curl -f http://localhost:8501/_stcore/health || echo "$(YELLOW)Frontend not ready$(NC)"
	@echo "\nPrometheus:"
	@curl -f http://localhost:9090/-/healthy || echo "$(YELLOW)Prometheus not ready$(NC)"
	@echo "\nGrafana:"
	@curl -f http://localhost:3000/api/health || echo "$(YELLOW)Grafana not ready$(NC)"

urls: ## Lista todas as URLs dos serviços
	@echo "$(GREEN)===================================$(NC)"
	@echo "$(GREEN)  SentiBR - Service URLs$(NC)"
	@echo "$(GREEN)===================================$(NC)"
	@echo "Frontend:    http://localhost:8501"
	@echo "API:         http://localhost:8000"
	@echo "API Docs:    http://localhost:8000/docs"
	@echo "MLflow:      http://localhost:5000"
	@echo "Prometheus:  http://localhost:9090"
	@echo "Grafana:     http://localhost:3000"
	@echo "  └─ User: admin"
	@echo "  └─ Pass: sentibr_grafana_2024"
	@echo "$(GREEN)===================================$(NC)"

env-check: ## Verifica variáveis de ambiente
	@echo "$(GREEN)Checking environment...$(NC)"
	@test -f .env && echo "$(GREEN)✓ .env file exists$(NC)" || echo "$(YELLOW)✗ .env file missing$(NC)"
	@grep -q "OPENAI_API_KEY" .env && echo "$(GREEN)✓ OPENAI_API_KEY configured$(NC)" || echo "$(YELLOW)✗ OPENAI_API_KEY not configured$(NC)"

watch: ## Watch logs de todos os serviços
	$(COMPOSE) logs -f --tail=100

##@ Backup & Restore

backup-all: ## Backup completo
	./backup.sh

backup-db: ## Apenas backup do banco
	@echo "$(GREEN)Backing up database...$(NC)"
	docker exec sentibr-postgres pg_dump -U sentibr_user -d sentibr -F c > backup_$(shell date +%Y%m%d_%H%M%S).dump

##@ Default

.DEFAULT_GOAL := help
