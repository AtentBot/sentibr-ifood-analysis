# 🔧 SentiBR - Troubleshooting Guide

Guia completo de resolução de problemas comuns.

## 📋 Índice

1. [Problemas de Inicialização](#problemas-de-inicialização)
2. [Erros de API](#erros-de-api)
3. [Problemas de Banco de Dados](#problemas-de-banco-de-dados)
4. [Problemas de Cache](#problemas-de-cache)
5. [Problemas de Performance](#problemas-de-performance)
6. [Problemas de Rede](#problemas-de-rede)
7. [Problemas de Memória](#problemas-de-memória)
8. [Logs e Debugging](#logs-e-debugging)

---

## 🚀 Problemas de Inicialização

### Serviço não inicia

**Sintomas:**
```bash
$ docker-compose up -d
ERROR: for sentibr-api  Cannot start service api: ...
```

**Diagnóstico:**
```bash
# Ver logs do serviço
docker-compose logs api

# Verificar status
docker-compose ps

# Ver detalhes do container
docker inspect sentibr-api
```

**Soluções:**

1. **Porta já em uso:**
```bash
# Verificar portas em uso
sudo netstat -tlnp | grep :8000

# Matar processo
sudo kill -9 <PID>

# Ou alterar porta no docker-compose.yml
```

2. **Falta de recursos:**
```bash
# Verificar recursos
docker system df
docker system prune -a  # Limpar recursos não utilizados

# Aumentar limites no Docker Desktop (macOS/Windows)
```

3. **Arquivo .env faltando:**
```bash
cp .env.example .env
# Editar e configurar variáveis
```

### Container reinicia constantemente

**Sintomas:**
```bash
$ docker-compose ps
sentibr-api    Restarting    ...
```

**Diagnóstico:**
```bash
# Ver últimos logs
docker-compose logs --tail=100 api

# Ver motivo da falha
docker inspect sentibr-api | grep -A 10 State
```

**Soluções:**

1. **Erro de código:**
   - Verificar sintaxe Python
   - Verificar imports
   - Verificar dependências no requirements.txt

2. **Falha no healthcheck:**
```bash
# Testar healthcheck manualmente
docker exec sentibr-api curl -f http://localhost:8000/api/v1/health
```

3. **Dependência não disponível:**
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Verificar conexão
docker exec sentibr-api pg_isready -h postgres -U sentibr_user
```

---

## 🔌 Erros de API

### HTTP 500 - Internal Server Error

**Diagnóstico:**
```bash
# Ver logs detalhados
docker-compose logs -f api | grep ERROR

# Verificar stack trace
docker exec sentibr-api cat /app/logs/sentibr.log
```

**Soluções comuns:**

1. **Modelo não encontrado:**
```bash
# Verificar se modelo existe
docker exec sentibr-api ls -la /app/models/

# Treinar modelo se necessário
docker exec sentibr-api python src/training/train.py
```

2. **Erro de conexão com banco:**
```bash
# Testar conexão
docker exec sentibr-api python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://sentibr_user:sentibr_password_2024@postgres:5432/sentibr')
print('OK' if engine.connect() else 'FAIL')
"
```

3. **OpenAI API Key inválida:**
```bash
# Verificar .env
grep OPENAI_API_KEY .env

# Testar key
docker exec sentibr-api python -c "
import openai
openai.api_key = 'your-key'
print(openai.Model.list())
"
```

### HTTP 503 - Service Unavailable

**Sintomas:**
- API não responde
- Timeouts

**Diagnóstico:**
```bash
# Verificar saúde dos workers
docker exec sentibr-api ps aux | grep uvicorn

# Verificar CPU/memória
docker stats sentibr-api
```

**Soluções:**

1. **Workers travados:**
```bash
# Reiniciar API
docker-compose restart api

# Ou aumentar número de workers no .env
WORKERS=8
```

2. **Recursos insuficientes:**
```bash
# Ajustar limites no docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
```

### Latência alta

**Diagnóstico:**
```bash
# Ver métricas
curl http://localhost:8000/api/v1/metrics | grep latency

# Benchmark
ab -n 100 -c 10 http://localhost:8000/api/v1/health
```

**Soluções:**

1. **Cache não funcionando:**
```bash
# Verificar Redis
docker exec sentibr-redis redis-cli -a sentibr_redis_2024 INFO stats

# Limpar cache
docker exec sentibr-redis redis-cli -a sentibr_redis_2024 FLUSHALL
```

2. **Banco de dados lento:**
```bash
# Ver queries lentas
docker exec sentibr-postgres psql -U sentibr_user -d sentibr -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
"

# Adicionar índices se necessário
```

---

## 🗄️ Problemas de Banco de Dados

### Não consegue conectar

**Diagnóstico:**
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Testar conexão
docker exec sentibr-postgres pg_isready -U sentibr_user -d sentibr

# Ver logs
docker-compose logs postgres
```

**Soluções:**

1. **Porta bloqueada:**
```bash
# Verificar firewall
sudo ufw status

# Verificar se porta está aberta
nc -zv localhost 5432
```

2. **Credenciais erradas:**
```bash
# Verificar .env
grep POSTGRES .env

# Resetar senha
docker exec sentibr-postgres psql -U postgres -c "
ALTER USER sentibr_user WITH PASSWORD 'new_password';
"
```

### Banco corrompido

**Sintomas:**
```bash
ERROR:  invalid page header in block X of relation base/...
```

**Soluções:**

1. **Restaurar backup:**
```bash
# Parar serviços
./stop.sh

# Restaurar
cat backups/postgres_backup.dump | \
  docker exec -i sentibr-postgres pg_restore \
  -U sentibr_user -d sentibr --clean

# Reiniciar
./deploy.sh
```

2. **Reconstruir banco:**
```bash
# CUIDADO: Perde todos os dados
docker-compose down -v
docker volume rm sentibr_postgres-data
docker-compose up -d postgres
```

### Muitas conexões

**Sintomas:**
```bash
ERROR:  sorry, too many clients already
```

**Soluções:**

1. **Aumentar max_connections:**
```bash
# Editar postgresql.conf
docker exec sentibr-postgres bash -c "
echo 'max_connections = 200' >> /var/lib/postgresql/data/postgresql.conf
"

# Reiniciar
docker-compose restart postgres
```

2. **Usar connection pooling:**
```python
# No código da API
from sqlalchemy.pool import QueuePool
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## 💾 Problemas de Cache

### Redis não responde

**Diagnóstico:**
```bash
# Verificar status
docker-compose ps redis

# Testar PING
docker exec sentibr-redis redis-cli -a sentibr_redis_2024 ping

# Ver logs
docker-compose logs redis
```

**Soluções:**

1. **Reiniciar Redis:**
```bash
docker-compose restart redis
```

2. **Limpar dados corrompidos:**
```bash
docker exec sentibr-redis redis-cli -a sentibr_redis_2024 FLUSHALL
```

### Memória cheia

**Sintomas:**
```bash
ERROR: Out of memory
```

**Soluções:**

1. **Aumentar maxmemory:**
```bash
# No docker-compose.yml
services:
  redis:
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

2. **Limpar keys antigas:**
```bash
# Encontrar keys grandes
docker exec sentibr-redis redis-cli -a sentibr_redis_2024 --bigkeys

# Deletar pattern específico
docker exec sentibr-redis redis-cli -a sentibr_redis_2024 --scan --pattern "old:*" | \
  xargs docker exec sentibr-redis redis-cli -a sentibr_redis_2024 DEL
```

---

## ⚡ Problemas de Performance

### Alto uso de CPU

**Diagnóstico:**
```bash
# Ver uso por container
docker stats

# Profiling da API
docker exec sentibr-api python -m cProfile -o profile.stats src/api/main.py
```

**Soluções:**

1. **Otimizar código:**
   - Usar cache agressivamente
   - Batch predictions
   - Async operations

2. **Escalar horizontalmente:**
```bash
docker-compose up -d --scale api=3
```

### Alto uso de memória

**Diagnóstico:**
```bash
# Ver uso detalhado
docker stats --no-stream

# Memory leak detection
docker exec sentibr-api python -m memory_profiler src/api/main.py
```

**Soluções:**

1. **Limitar batch size:**
```python
# No código
MAX_BATCH_SIZE = 16  # Reduzir se necessário
```

2. **Usar garbage collection:**
```python
import gc
gc.collect()
```

---

## 🌐 Problemas de Rede

### Containers não se comunicam

**Diagnóstico:**
```bash
# Ver networks
docker network ls
docker network inspect sentibr-network

# Testar conectividade
docker exec sentibr-api ping postgres
```

**Soluções:**

1. **Recriar network:**
```bash
docker-compose down
docker network prune
docker-compose up -d
```

### Slow network

**Diagnóstico:**
```bash
# Testar latência entre containers
docker exec sentibr-api time curl -o /dev/null -s http://postgres:5432
```

**Soluções:**

1. **Usar host network (Linux only):**
```yaml
services:
  api:
    network_mode: "host"
```

---

## 📝 Logs e Debugging

### Ver logs em tempo real

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f api

# Com timestamp
docker-compose logs -f --timestamps api

# Últimas N linhas
docker-compose logs --tail=100 api
```

### Buscar erros nos logs

```bash
# Grep por ERROR
docker-compose logs api | grep ERROR

# Filtrar por timestamp
docker-compose logs --since 2024-01-01T00:00:00 api

# Salvar logs
docker-compose logs > logs.txt
```

### Debug mode

1. **Habilitar debug logging:**
```bash
# No .env
LOG_LEVEL=DEBUG
```

2. **Usar debugger:**
```python
# No código
import pdb; pdb.set_trace()
```

3. **Attach ao container:**
```bash
docker exec -it sentibr-api bash
cd /app
python -m pdb src/api/main.py
```

---

## 🆘 Quando tudo falha

### Reset completo

```bash
# CUIDADO: Remove TUDO
./stop.sh  # Opção 3
docker system prune -a --volumes
./deploy.sh
```

### Buscar ajuda

1. **Logs completos:**
```bash
docker-compose logs > full-logs.txt
```

2. **System info:**
```bash
docker version > system-info.txt
docker-compose version >> system-info.txt
docker info >> system-info.txt
```

3. **Abrir issue:**
   - https://github.com/your-repo/sentibr/issues
   - Incluir logs e system info
   - Descrever passos para reproduzir

---

## 📚 Recursos Adicionais

- [Docker Docs](https://docs.docker.com/)
- [PostgreSQL Troubleshooting](https://www.postgresql.org/docs/current/maintenance.html)
- [Redis Troubleshooting](https://redis.io/docs/management/debugging/)
- [FastAPI Debugging](https://fastapi.tiangolo.com/tutorial/debugging/)
