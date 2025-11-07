"""
SentiBR - Dashboard
Visualização de métricas e estatísticas
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard - Visão Geral")
st.markdown("Métricas e estatísticas do sistema em tempo real")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Reviews Analisadas", "150,234", "+5,432 hoje", delta_color="normal")

with col2:
    st.metric("Acurácia Modelo", "92.3%", "+2.1%", delta_color="normal")

with col3:
    st.metric("Latência Média", "87ms", "-15ms", delta_color="inverse")

with col4:
    st.metric("Uptime", "99.8%", "", delta_color="off")

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição de Sentimentos")
    
    # Dados de exemplo
    sentimentos_data = pd.DataFrame({
        'Sentimento': ['Positivo', 'Neutro', 'Negativo'],
        'Quantidade': [65432, 45678, 39124]
    })
    
    fig_pie = px.pie(
        sentimentos_data,
        values='Quantidade',
        names='Sentimento',
        color='Sentimento',
        color_discrete_map={
            'Positivo': '#28a745',
            'Neutro': '#ffc107',
            'Negativo': '#dc3545'
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Evolução Temporal")
    
    # Dados de exemplo - últimos 7 dias
    dates = [datetime.now() - timedelta(days=x) for x in range(6, -1, -1)]
    temporal_data = pd.DataFrame({
        'Data': dates,
        'Positivo': [8500, 9200, 8800, 9500, 10200, 9800, 10500],
        'Neutro': [6200, 6500, 6300, 6800, 7100, 6900, 7300],
        'Negativo': [5300, 5100, 5400, 4900, 4600, 5000, 4800]
    })
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=temporal_data['Data'], y=temporal_data['Positivo'], name='Positivo', line=dict(color='#28a745')))
    fig_line.add_trace(go.Scatter(x=temporal_data['Data'], y=temporal_data['Neutro'], name='Neutro', line=dict(color='#ffc107')))
    fig_line.add_trace(go.Scatter(x=temporal_data['Data'], y=temporal_data['Negativo'], name='Negativo', line=dict(color='#dc3545')))
    fig_line.update_layout(xaxis_title='Data', yaxis_title='Quantidade')
    
    st.plotly_chart(fig_line, use_container_width=True)

# Performance do Modelo
st.markdown("---")
st.subheader("Performance do Modelo")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### BERT")
    st.metric("F1-Score", "0.923")
    st.metric("Precision", "0.917")
    st.metric("Recall", "0.929")

with col2:
    st.markdown("### Latência")
    
    # Gráfico de latência
    latency_data = pd.DataFrame({
        'Percentil': ['P50', 'P75', 'P90', 'P95', 'P99'],
        'Tempo (ms)': [45, 72, 95, 123, 187]
    })
    
    fig_bar = px.bar(latency_data, x='Percentil', y='Tempo (ms)', color='Tempo (ms)')
    st.plotly_chart(fig_bar, use_container_width=True)

with col3:
    st.markdown("### Cache Redis")
    st.metric("Hit Rate", "87.3%")
    st.metric("Conexões", "42")
    st.metric("Memória Usada", "234 MB")

# Status dos Serviços
st.markdown("---")
st.subheader("Status dos Serviços")

services = pd.DataFrame({
    'Serviço': ['API', 'BERT Model', 'PostgreSQL', 'Redis', 'Prometheus', 'Grafana'],
    'Status': ['🟢 Online', '🟢 Online', '🟢 Online', '🟢 Online', '🟢 Online', '🟢 Online'],
    'Uptime': ['99.9%', '99.8%', '100%', '99.7%', '99.9%', '99.6%'],
    'Última Verificação': ['2s atrás', '5s atrás', '3s atrás', '2s atrás', '10s atrás', '8s atrás']
})

st.dataframe(services, use_container_width=True, hide_index=True)

# Alertas
with st.expander("⚠️ Alertas e Notificações"):
    st.info("✅ Sem alertas críticos no momento")
    st.markdown("""
    **Últimas notificações:**
    - ✅ Modelo BERT atualizado com sucesso (2h atrás)
    - ✅ Backup do banco de dados concluído (5h atrás)
    - ⚠️ Latência acima de 100ms detectada às 14:23 (resolvido)
    """)
