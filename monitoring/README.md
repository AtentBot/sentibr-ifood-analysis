# 🔍 FASE 5 - OBSERVABILIDADE E MONITORING

Sistema completo de observabilidade production-ready para o SentiBR.

## 📋 O Que Foi Criado

### ✅ **Prometheus Setup**
- Configuração completa do Prometheus
- Coleta de métricas a cada 15s
- 5 jobs de scraping configurados
- 15+ alertas configurados

### ✅ **Métricas Customizadas**
- **API Metrics**: Requests, latência, erros
- **Model Metrics**: Predições, confiança, inference time
- **Drift Metrics**: Drift score, KS statistics
- **Feedback Metrics**: Submissões, correções
- **Business Metrics**: Reviews processadas, distribuição de sentimentos
- **System Metrics**: Uptime, info do sistema

### ✅ **Grafana Dashboards**
- **Model Performance**: 8 painéis com métricas do modelo
- **API Health**: 8 painéis com saúde da API
- **Business Metrics**: 8 painéis com métricas de negócio

### ✅ **Drift Detection**
- Detector de drift com testes estatísticos
- Kolmogorov-Smirnov test para features numéricas
- Chi-Square test para features categóricas
- Thresholds configuráveis (warning 15%, critical 25%)
- Relatórios detalhados

### ✅ **Logging Estruturado**
- Logs em formato JSON
- Context management para requests
- 4 loggers especializados (API, Model, Monitoring, System)
- Funções helper para tipos comuns de log
- Rotation e retention automáticos

### ✅ **Docker Compose**
- Stack completa: Prometheus + Grafana + Node Exporter + Alertmanager
- Networks isoladas
- Volumes persistentes
- Restart policies configuradas

---

## 🏗️ Estrutura de Arquivos

```
monitoring/
├── prometheus/
│   ├── prometheus.yml       # Config Prometheus (5 jobs)
│   └── alerts.yml          # Regras de alerta (15+ alertas)
│
├── grafana/
│   ├── dashboards/
│   │   ├── model_performance.json
│   │   ├── api_health.json
│   │   └── business_metrics.json
│   │
│   └── provisioning/
│       ├── datasources/
│       │   └── prometheus.yml
│       └── dashboards/
│           └── dashboards.yml
│
└── alertmanager/
    └── config.yml           # Config de alertas

src/monitoring/
├── __init__.py
├── metrics.py              # Sistema de métricas Prometheus
├── drift_detector.py       # Detector de drift
└── logger.py               # Logging estruturado

docker-compose.monitoring.yml  # Stack de monitoring
requirements-monitoring.txt    # Dependências
```

---

## 🚀 Como Usar

### 1️⃣ **Instalar Dependências**

```bash
pip install -r requirements-monitoring.txt
```

### 2️⃣ **Iniciar Stack de Monitoring**

```bash
# Subir Prometheus + Grafana + Node Exporter
docker-compose -f docker-compose.monitoring.yml up -d

# Verificar status
docker-compose -f docker-compose.monitoring.yml ps
```

### 3️⃣ **Acessar Interfaces**

- **Grafana**: http://localhost:3000
  - User: `admin`
  - Password: `admin`
  
- **Prometheus**: http://localhost:9090

- **Alertmanager**: http://localhost:9093

### 4️⃣ **Instrumentar sua API**

```python
from src.monitoring.metrics import (
    track_prediction_metrics,
    track_request_metrics,
    init_metrics
)

# Inicializar métricas
init_metrics(version="1.0.0", model_version="bert-v1")

# Registrar predição
track_prediction_metrics(
    sentiment="positive",
    confidence=0.95,
    inference_time=0.042,  # segundos
    model_type="bert"
)

# Registrar requisição HTTP
track_request_metrics(
    method="POST",
    endpoint="/api/v1/predict",
    status_code=200
)
```

### 5️⃣ **Detectar Drift**

```python
from src.monitoring.drift_detector import DriftDetector
import pandas as pd

# Criar detector
detector = DriftDetector(
    baseline_path="data/baseline.json",
    warning_threshold=0.15,
    critical_threshold=0.25
)

# Salvar baseline (primeira vez)
baseline_data = pd.DataFrame({...})  # Seus dados
detector.save_baseline(baseline_data, "data/baseline.json")

# Detectar drift
current_data = pd.DataFrame({...})  # Dados atuais
results = detector.detect_drift(current_data)

# Ver relatório
print(detector.get_drift_report(results))
```

### 6️⃣ **Logging Estruturado**

```python
from src.monitoring.logger import (
    api_logger,
    log_prediction,
    log_request,
    RequestContext
)

# Log simples
api_logger.info("API started", port=8000)

# Log com contexto
with RequestContext(request_id="req-123", user_id="user-456"):
    api_logger.info("Processing request")
    
    log_prediction(
        text="A comida estava excelente!",
        sentiment="positive",
        confidence=0.95,
        inference_time_ms=42.5
    )

# Log de erro
try:
    # seu código
    pass
except Exception:
    api_logger.exception("Error processing request")
```

---

## 📊 Métricas Disponíveis

### **API Metrics**

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `http_requests_total` | Counter | Total de requisições HTTP |
| `http_request_duration_seconds` | Histogram | Latência das requisições |
| `http_requests_in_progress` | Gauge | Requisições em andamento |
| `http_errors_total` | Counter | Total de erros HTTP |

### **Model Metrics**

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `model_predictions_total` | Counter | Total de predições |
| `model_inference_duration_seconds` | Histogram | Tempo de inferência |
| `model_prediction_confidence_avg` | Gauge | Confiança média |
| `model_confidence_summary` | Summary | Summary de confiança |

### **Drift Metrics**

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `model_data_drift_score` | Gauge | Score de drift (0-1) |
| `model_feature_distribution_ks_statistic` | Gauge | KS statistic por feature |
| `model_last_drift_check_timestamp` | Gauge | Timestamp do último check |

### **Business Metrics**

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `business_reviews_processed_today` | Gauge | Reviews processadas hoje |
| `business_sentiment_distribution` | Counter | Distribuição de sentimentos |
| `feedback_submissions_total` | Counter | Total de feedbacks |
| `feedback_correction_rate` | Gauge | Taxa de correções |

---

## 🔔 Alertas Configurados

### **API Health**

- ❌ **APIDown**: API offline por >1min
- ⚠️ **HighErrorRate**: Taxa de erro >5% por 2min
- ⚠️ **HighLatencyP99**: P99 >200ms por 5min
- ❌ **CriticalLatencyP99**: P99 >500ms por 2min

### **Model Performance**

- ⚠️ **LowAverageConfidence**: Confiança média <70% por 5min
- ⚠️ **HighLowConfidencePredictions**: >30% predições com baixa confiança

### **Data Drift**

- ⚠️ **DataDriftWarning**: Drift >15% por 10min
- ❌ **DataDriftCritical**: Drift >25% por 5min
- ⚠️ **FeatureDistributionShift**: KS >0.3 por 15min

### **Resources**

- ⚠️ **HighCPUUsage**: CPU >80% por 5min
- ⚠️ **HighMemoryUsage**: Memória >85% por 5min
- ❌ **DiskSpaceLow**: Disco <10% por 5min

### **Business**

- ℹ️ **LowFeedbackRate**: Taxa de feedback <1% por 30min
- ℹ️ **HighNegativeSentimentRate**: >50% sentimentos negativos por 30min

---

## 📈 Dashboards Grafana

### **1. Model Performance**

**Métricas:**
- Total de predições (24h)
- Confiança média
- Drift score
- P95 inference time

**Gráficos:**
- Predições por sentimento
- Distribuição de confiança
- Percentis de inferência
- Drift score ao longo do tempo

### **2. API Health**

**Métricas:**
- Request rate
- Error rate
- P95 latency
- Active requests

**Gráficos:**
- Request rate por método
- Response time percentiles
- Status code distribution
- Error rate over time

### **3. Business Metrics**

**Métricas:**
- Reviews processadas hoje
- Taxa positiva
- Taxa de feedback
- Acurácia (via feedback)

**Gráficos:**
- Distribuição de sentimentos (pizza)
- Trends de sentimentos
- Submissões de feedback
- Taxa de correção

---

## 🔍 Queries PromQL Úteis

### **Request Rate**
```promql
sum(rate(http_requests_total[5m])) * 60
```

### **Error Rate**
```promql
(sum(rate(http_requests_total{status=~"5.."}[5m])) 
 / 
 sum(rate(http_requests_total[5m]))) * 100
```

### **P95 Latency**
```promql
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m]))
```

### **Predictions per Minute**
```promql
sum(rate(model_predictions_total[5m])) * 60
```

### **Average Confidence**
```promql
avg(model_prediction_confidence_avg)
```

### **Drift Score**
```promql
model_data_drift_score
```

---

## 🐛 Troubleshooting

### **Problema: Prometheus não está coletando métricas**

**Solução:**
1. Verificar se API está expondo `/metrics`:
   ```bash
   curl http://localhost:8000/api/v1/metrics
   ```

2. Verificar targets no Prometheus:
   - Acesse: http://localhost:9090/targets
   - Verifique se todos estão "UP"

3. Ver logs do Prometheus:
   ```bash
   docker logs sentibr-prometheus
   ```

### **Problema: Dashboards não aparecem no Grafana**

**Solução:**
1. Verificar provisioning:
   ```bash
   docker exec sentibr-grafana ls -la /etc/grafana/provisioning/dashboards
   ```

2. Verificar datasource:
   - Acesse: http://localhost:3000/datasources
   - Deve ter "Prometheus" configurado

3. Reimportar dashboards manualmente:
   - Configuration → Data Sources → Add Prometheus
   - Dashboards → Import → Copie JSON

### **Problema: Alertas não estão funcionando**

**Solução:**
1. Verificar regras no Prometheus:
   - Acesse: http://localhost:9090/alerts
   - Verifique estado dos alertas

2. Verificar Alertmanager:
   - Acesse: http://localhost:9093
   - Ver alertas ativos

3. Testar manualmente:
   ```bash
   # Forçar alta latência
   # Forçar drift alto
   # Ver se alerta dispara
   ```

---

## 🎯 Próximos Passos

Após configurar monitoring, você pode:

1. **FASE 6**: LLM Integration (GPT-4o-mini)
2. **FASE 7**: Docker + Deploy completo
3. **FASE 8**: Testes (Unit + Integration + Load)

---

## 📚 Referências

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Client Python](https://github.com/prometheus/client_python)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)

---

## 🎉 Resumo

✅ **Prometheus configurado** com 5 jobs de scraping  
✅ **15+ alertas** configurados  
✅ **3 dashboards Grafana** completos  
✅ **Sistema de métricas** Python completo  
✅ **Drift detector** com testes estatísticos  
✅ **Logging estruturado** em JSON  
✅ **Docker Compose** para subir tudo  

**FASE 5 - 100% COMPLETA!** 🚀

---

**Desenvolvido com ❤️ para o desafio técnico de IA Sênior**

🔍 Observabilidade + 📊 Métricas + 🔔 Alertas = 💪 Production-Ready!
