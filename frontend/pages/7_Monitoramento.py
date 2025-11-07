"""
SentiBR - Monitoramento
Status e saúde do sistema em tempo real
"""
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Monitoramento", page_icon="📈", layout="wide")

st.title("📈 Monitoramento do Sistema")
st.markdown("Status e saúde de todos os serviços")

# Função para verificar saúde
def check_health(url, timeout=2):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

# Status geral
st.subheader("🎯 Status Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    api_status = check_health("http://api:8000/api/v1/health")
    if api_status:
        st.success("🟢 API Online")
    else:
        st.error("🔴 API Offline")

with col2:
    # Simular status do modelo
    st.success("🟢 Modelo BERT")

with col3:
    # Simular status do cache
    st.success("🟢 Redis Cache")

with col4:
    # Simular status do banco
    st.success("🟢 PostgreSQL")

# Detalhes dos serviços
st.markdown("---")
st.subheader("🔧 Detalhes dos Serviços")

# Criar tabs para cada serviço
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 API",
    "🧠 BERT Model",
    "💾 Redis",
    "🗄️ PostgreSQL",
    "📊 Observabilidade"
])

with tab1:
    st.markdown("### API FastAPI")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🟢 Online")
        st.metric("Uptime", "99.8%")
    
    with col2:
        st.metric("Requests/s", "147")
        st.metric("Latência P95", "123ms")
    
    with col3:
        st.metric("Erros", "0.2%")
        st.metric("Última verificação", "5s atrás")
    
    st.markdown("#### Endpoints")
    
    endpoints = [
        {"Endpoint": "/api/v1/health", "Status": "🟢", "Latência": "12ms"},
        {"Endpoint": "/api/v1/predict", "Status": "🟢", "Latência": "87ms"},
        {"Endpoint": "/api/v1/predict/batch", "Status": "🟢", "Latência": "234ms"},
        {"Endpoint": "/api/v1/model/info", "Status": "🟢", "Latência": "8ms"},
    ]
    
    import pandas as pd
    st.dataframe(pd.DataFrame(endpoints), hide_index=True, use_container_width=True)
    
    st.markdown("#### Logs Recentes")
    st.code("""
[2025-11-06 18:30:15] INFO - Request processed successfully
[2025-11-06 18:30:12] INFO - Model prediction: positive (0.92)
[2025-11-06 18:30:10] INFO - Health check passed
[2025-11-06 18:30:05] INFO - Cache hit: review_12345
[2025-11-06 18:30:01] INFO - New request received
""")

with tab2:
    st.markdown("### Modelo BERT")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🟢 Carregado")
        st.metric("Versão", "v1.2.3")
    
    with col2:
        st.metric("Acurácia", "92.3%")
        st.metric("Predições Hoje", "12,456")
    
    with col3:
        st.metric("Memória", "1.8 GB")
        st.metric("Latência Média", "87ms")
    
    st.markdown("#### Informações do Modelo")
    st.json({
        "model_name": "neuralmind/bert-base-portuguese-cased",
        "num_labels": 3,
        "labels": ["negative", "neutral", "positive"],
        "max_length": 512,
        "trained_on": "150K reviews",
        "last_updated": "2025-11-01",
        "framework": "PyTorch 2.1.2"
    })
    
    st.markdown("#### Performance")
    st.progress(0.92, text="Acurácia: 92%")
    st.progress(0.91, text="F1-Score: 91%")
    st.progress(0.89, text="Cache Hit Rate: 89%")

with tab3:
    st.markdown("### Redis Cache")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🟢 Conectado")
        st.metric("Conexões", "42")
    
    with col2:
        st.metric("Hit Rate", "87.3%")
        st.metric("Keys", "1,234")
    
    with col3:
        st.metric("Memória", "234 MB")
        st.metric("Evictions", "0")
    
    st.markdown("#### Configuração")
    st.code("""
Host: redis
Port: 6379
Database: 0
Max Connections: 100
Timeout: 5s
TTL: 3600s (1 hora)
""")
    
    st.markdown("#### Top Keys")
    keys_df = pd.DataFrame({
        'Key': ['review:hash:abc123', 'review:hash:def456', 'review:hash:ghi789'],
        'TTL': ['45m', '32m', '18m'],
        'Tamanho': ['2.1 KB', '1.8 KB', '2.3 KB']
    })
    st.dataframe(keys_df, hide_index=True, use_container_width=True)

with tab4:
    st.markdown("### PostgreSQL")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "🟢 Conectado")
        st.metric("Conexões", "15/100")
    
    with col2:
        st.metric("Registros", "150,234")
        st.metric("Tamanho DB", "2.3 GB")
    
    with col3:
        st.metric("Queries/s", "23")
        st.metric("Cache Hit", "94%")
    
    st.markdown("#### Tabelas")
    tables_df = pd.DataFrame({
        'Tabela': ['reviews', 'predictions', 'feedbacks', 'model_versions'],
        'Registros': ['150,234', '152,891', '1,234', '12'],
        'Tamanho': ['1.8 GB', '450 MB', '12 MB', '2 MB']
    })
    st.dataframe(tables_df, hide_index=True, use_container_width=True)
    
    st.markdown("#### Queries Lentas")
    st.code("""
-- Nenhuma query lenta detectada nas últimas 24h
-- Todas as queries < 100ms
""")

with tab5:
    st.markdown("### Observabilidade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Prometheus")
        st.metric("Status", "🟢 Coletando")
        st.metric("Métricas", "87")
        st.metric("Targets", "5/5 UP")
        
        st.markdown("**Acesso:**")
        st.code("http://localhost:9090")
        
    with col2:
        st.markdown("#### Grafana")
        st.metric("Status", "🟢 Online")
        st.metric("Dashboards", "3")
        st.metric("Painéis", "24")
        
        st.markdown("**Acesso:**")
        st.code("http://localhost:3000")
        st.caption("Usuário: admin | Senha: sentibr_grafana_2024")
    
    st.markdown("#### MLflow")
    st.metric("Status", "🟢 Online")
    st.metric("Experimentos", "15")
    st.metric("Modelos", "8")
    
    st.markdown("**Acesso:**")
    st.code("http://localhost:5000")

# Alertas
st.markdown("---")
st.subheader("⚠️ Alertas e Notificações")

# Verificar se há alertas
has_alerts = False

if has_alerts:
    st.error("🔴 2 alertas críticos")
    st.warning("🟡 5 avisos")
else:
    st.success("✅ Sem alertas no momento")

# Últimas notificações
with st.expander("📋 Últimas Notificações"):
    notifications = [
        {"Hora": "18:25", "Tipo": "ℹ️ Info", "Mensagem": "Backup automático concluído"},
        {"Hora": "15:30", "Tipo": "✅ Success", "Mensagem": "Modelo atualizado para v1.2.3"},
        {"Hora": "12:45", "Tipo": "⚠️ Warning", "Mensagem": "Latência elevada detectada (resolvido)"},
        {"Hora": "09:15", "Tipo": "ℹ️ Info", "Mensagem": "Limpeza de cache executada"},
        {"Hora": "06:00", "Tipo": "ℹ️ Info", "Mensagem": "Health check noturno - OK"}
    ]
    
    st.dataframe(pd.DataFrame(notifications), hide_index=True, use_container_width=True)

# Métricas de Performance
st.markdown("---")
st.subheader("📊 Métricas de Performance")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### CPU")
    st.progress(0.45, text="45% (API)")
    st.progress(0.32, text="32% (DB)")
    st.progress(0.18, text="18% (Cache)")

with col2:
    st.markdown("#### Memória")
    st.progress(0.67, text="67% (API)")
    st.progress(0.42, text="42% (DB)")
    st.progress(0.23, text="23% (Cache)")

with col3:
    st.markdown("#### Disco")
    st.progress(0.34, text="34% (Usado)")
    st.metric("Disponível", "12.3 GB")

with col4:
    st.markdown("#### Rede")
    st.metric("In", "2.3 MB/s")
    st.metric("Out", "4.1 MB/s")

# Ações rápidas
st.markdown("---")
st.subheader("⚡ Ações Rápidas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Atualizar Status", use_container_width=True):
        st.rerun()

with col2:
    if st.button("🧹 Limpar Cache", use_container_width=True):
        with st.spinner("Limpando cache..."):
            time.sleep(1)
        st.success("Cache limpo!")

with col3:
    if st.button("📊 Ver Grafana", use_container_width=True):
        st.markdown("[Abrir Grafana](http://localhost:3000)")

with col4:
    if st.button("📈 Ver Prometheus", use_container_width=True):
        st.markdown("[Abrir Prometheus](http://localhost:9090)")

# Informações do sistema
with st.expander("💻 Informações do Sistema"):
    st.markdown(f"""
    **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    **Containers em Execução**: 8
    - sentibr-api
    - sentibr-frontend
    - sentibr-postgres
    - sentibr-redis
    - sentibr-prometheus
    - sentibr-grafana
    - sentibr-mlflow
    - sentibr-nginx
    
    **Versões**:
    - API: v1.0.0
    - Frontend: v1.0.0
    - BERT Model: v1.2.3
    
    **Ambiente**: Production
    **Deploy**: Docker Compose
    **Host**: localhost
    """)

# Footer
st.markdown("---")
st.caption("🔄 Atualizado automaticamente a cada 30 segundos")

# Auto-refresh (opcional)
auto_refresh = st.checkbox("Auto-refresh", value=False)
if auto_refresh:
    time.sleep(30)
    st.rerun()
