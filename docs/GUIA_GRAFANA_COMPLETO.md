# 📊 Grafana - Configuração Completa

## 🔐 **Acesso:**
```
URL: http://localhost:3000
Usuário: admin
Senha: sentibr_grafana_2024
```

---

## ⚙️ **PASSO 1: Adicionar Data Source (Prometheus)**

### **1. Acessar Configuração:**
```
1. Login no Grafana
2. Menu lateral esquerdo → ⚙️ (Configuration)
3. Clicar: "Data sources"
4. Clicar: "Add data source"
```

### **2. Selecionar Prometheus:**
```
1. Procurar: "Prometheus"
2. Clicar em: "Prometheus"
```

### **3. Configurar:**
```
Name: Prometheus
URL: http://prometheus:9090
Access: Server (default)
```

### **4. Salvar:**
```
1. Scroll para baixo
2. Clicar: "Save & Test"
3. Deve aparecer: ✅ "Data source is working"
```

---

## 📊 **PASSO 2: Importar Dashboard**

### **Método 1: Upload de Arquivo (Recomendado)**

#### **1. Baixar Dashboard:**
- **[dashboard_sentibr.json](computer:///mnt/user-data/outputs/dashboard_sentibr.json)** ⭐

#### **2. Importar:**
```
1. Menu lateral → + (Create)
2. Clicar: "Import"
3. Clicar: "Upload JSON file"
4. Selecionar: dashboard_sentibr.json
5. Selecionar Prometheus como Data Source
6. Clicar: "Import"
```

---

### **Método 2: Criar Manualmente (se preferir)**

#### **1. Criar Novo Dashboard:**
```
1. Menu lateral → + (Create)
2. Clicar: "Dashboard"
3. Clicar: "Add new panel"
```

#### **2. Adicionar Painel de Requests:**
```
Title: API - Requests por Segundo
Query: rate(http_requests_total[1m])
Visualization: Graph
```

#### **3. Adicionar mais painéis:**
Repita para:
- Latência
- Total de Predições
- Distribuição de Sentimentos
- Uso de CPU/Memória

---

## 📈 **Dashboards Disponíveis**

### **Dashboard: SentiBR - Monitoramento Geral**

**Painéis incluídos:**

1. **API - Requests por Segundo**
   - Monitoramento de tráfego
   - Por endpoint e método

2. **API - Latência Média (ms)**
   - Tempo de resposta
   - Alerta se > 500ms

3. **Total de Predições**
   - Contador de análises realizadas

4. **Acurácia do Modelo (%)**
   - Performance em tempo real

5. **Uso de Memória**
   - RAM utilizada pela API

6. **Uso de CPU**
   - Processamento

7. **Distribuição de Sentimentos**
   - Pizza: Positive/Neutral/Negative

8. **Tempo de Inferência BERT**
   - Quanto tempo leva cada predição

9. **Erros HTTP**
   - Status 5xx nos últimos 5min

10. **Cache Redis - Hit Rate**
    - Eficiência do cache

11. **Conexões PostgreSQL**
    - Banco de dados

12. **Status dos Serviços**
    - Todos os containers UP/DOWN

---

## 🎨 **Personalização**

### **Cores:**
```
✅ Verde: Healthy, Success
🟡 Amarelo: Warning
🔴 Vermelho: Error, Critical
```

### **Alertas:**
```
1. Edit Panel
2. Alert tab
3. Criar condição:
   - Se latência > 500ms → Alerta
   - Se erros > 10/min → Alerta
   - Se CPU > 80% → Alerta
```

### **Refresh:**
```
Dashboard settings → General
Auto-refresh: 5s, 10s, 30s, 1m
```

---

## 📊 **Métricas Disponíveis**

### **API Metrics:**
```
http_requests_total - Total de requests
http_request_duration_seconds - Latência
predictions_total - Total de predições
predictions_by_sentiment - Por sentimento
bert_inference_duration_seconds - Tempo BERT
```

### **Sistema:**
```
process_resident_memory_bytes - Memória
process_cpu_seconds_total - CPU
up - Status do serviço
```

### **Redis:**
```
redis_cache_hits - Cache hits
redis_cache_misses - Cache misses
```

### **PostgreSQL:**
```
pg_stat_activity_count - Conexões ativas
```

---

## 🔧 **Troubleshooting**

### **Erro: "Data source is not working"**
```bash
# Verificar se Prometheus está rodando
docker ps | grep prometheus

# Ver logs
docker logs sentibr-prometheus

# Testar conectividade
docker exec sentibr-grafana ping prometheus
```

### **Erro: "No data"**
```
1. Verificar se API está gerando métricas:
   http://localhost:8000/metrics

2. Verificar se Prometheus está coletando:
   http://localhost:9090/targets
   
3. Deve mostrar: sentibr-api (1/1 up)
```

### **Dashboard não aparece:**
```
1. Verificar JSON válido
2. Re-importar dashboard
3. Verificar Data Source selecionado
```

---

## 📚 **Recursos Extras**

### **Dashboards Adicionais:**

Você pode criar dashboards para:
- **MLflow**: Experimentos e métricas
- **Nginx**: Logs e requests
- **Frontend**: Usuários ativos

### **Exportar Dashboard:**
```
1. Abrir dashboard
2. ⚙️ (Settings)
3. JSON Model
4. Copiar JSON
5. Salvar em arquivo
```

### **Compartilhar Dashboard:**
```
1. Share icon (📤)
2. Export
3. Save to file
4. Enviar para equipe
```

---

## 🎯 **Checklist de Configuração**

- [ ] Login no Grafana (admin/sentibr_grafana_2024)
- [ ] Adicionar Prometheus como Data Source
- [ ] Testar Data Source (✅ working)
- [ ] Importar dashboard_sentibr.json
- [ ] Verificar painéis carregando dados
- [ ] Configurar auto-refresh (5s)
- [ ] Testar alertas (opcional)
- [ ] Exportar dashboard configurado (backup)

---

## 🎉 **Resultado Final**

Após configuração, você terá:

✅ **Dashboard completo** com 12 painéis  
✅ **Métricas em tempo real** (atualiza a cada 5s)  
✅ **Visão geral** do sistema  
✅ **Alertas** configuráveis  
✅ **Histórico** de métricas  

---

## 📞 **Comandos Úteis**

### **Reiniciar Grafana:**
```bash
docker-compose restart grafana
```

### **Ver configuração:**
```bash
docker exec sentibr-grafana cat /etc/grafana/grafana.ini
```

### **Reset completo:**
```bash
docker-compose down
docker volume rm sentibr-ifood-analysis_grafana-data
docker-compose up -d grafana
```

---

**Siga os passos e terá dashboards prontos! 📊🚀**
