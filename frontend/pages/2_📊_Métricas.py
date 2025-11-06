"""
Página de Métricas e Dashboard
Exibe estatísticas e métricas do sistema em tempo real
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from pathlib import Path
import sys

# Adicionar componentes ao path
sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import metric_card


# Configuração da página
st.set_page_config(
    page_title="Métricas - SentiBR",
    page_icon="📊",
    layout="wide"
)


# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1"


def generate_mock_data():
    """Gera dados mockados para demonstração"""
    
    # Dados de predições ao longo do tempo
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    predictions_data = pd.DataFrame({
        'date': dates,
        'positive': np.random.randint(100, 500, 30),
        'negative': np.random.randint(50, 200, 30),
        'neutral': np.random.randint(30, 150, 30)
    })
    
    # Dados de latência
    latency_data = pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=100, freq='H'),
        'latency_ms': np.random.normal(45, 15, 100),
        'p95': np.random.normal(80, 20, 100),
        'p99': np.random.normal(120, 30, 100)
    })
    
    # Distribuição de confiança
    confidence_data = pd.DataFrame({
        'confidence': np.random.beta(8, 2, 1000)
    })
    
    return predictions_data, latency_data, confidence_data


def plot_predictions_over_time(data: pd.DataFrame):
    """Plota predições ao longo do tempo"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['positive'],
        name='Positivo',
        mode='lines+markers',
        line=dict(color='#28a745', width=3),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['negative'],
        name='Negativo',
        mode='lines+markers',
        line=dict(color='#dc3545', width=3),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['neutral'],
        name='Neutro',
        mode='lines+markers',
        line=dict(color='#6c757d', width=3),
        fill='tonexty'
    ))
    
    fig.update_layout(
        title="Predições ao Longo do Tempo (Últimos 30 dias)",
        xaxis_title="Data",
        yaxis_title="Número de Predições",
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def plot_sentiment_distribution(data: pd.DataFrame):
    """Plota distribuição de sentimentos"""
    
    total_positive = data['positive'].sum()
    total_negative = data['negative'].sum()
    total_neutral = data['neutral'].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=['Positivo', 'Negativo', 'Neutro'],
        values=[total_positive, total_negative, total_neutral],
        hole=.4,
        marker_colors=['#28a745', '#dc3545', '#6c757d']
    )])
    
    fig.update_layout(
        title="Distribuição de Sentimentos",
        height=400,
        annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return fig


def plot_latency_metrics(data: pd.DataFrame):
    """Plota métricas de latência"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['timestamp'],
        y=data['latency_ms'],
        name='Latência Média',
        mode='lines',
        line=dict(color='#17a2b8', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=data['timestamp'],
        y=data['p95'],
        name='P95',
        mode='lines',
        line=dict(color='#ffc107', width=2, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=data['timestamp'],
        y=data['p99'],
        name='P99',
        mode='lines',
        line=dict(color='#dc3545', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title="Latência ao Longo do Tempo",
        xaxis_title="Timestamp",
        yaxis_title="Latência (ms)",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def plot_confidence_distribution(data: pd.DataFrame):
    """Plota distribuição de confiança"""
    
    fig = go.Figure(data=[go.Histogram(
        x=data['confidence'],
        nbinsx=50,
        marker_color='#EA1D2C',
        opacity=0.7
    )])
    
    fig.update_layout(
        title="Distribuição de Confiança das Predições",
        xaxis_title="Confiança",
        yaxis_title="Frequência",
        height=400,
        bargap=0.1
    )
    
    # Adicionar linha vertical na média
    mean_conf = data['confidence'].mean()
    fig.add_vline(
        x=mean_conf,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Média: {mean_conf:.2%}",
        annotation_position="top right"
    )
    
    return fig


def plot_hourly_heatmap():
    """Plota heatmap de predições por hora/dia"""
    
    # Gerar dados mockados
    days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    hours = [f"{h:02d}h" for h in range(24)]
    
    data = np.random.randint(10, 200, (7, 24))
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=hours,
        y=days,
        colorscale='RdYlGn',
        text=data,
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Predições")
    ))
    
    fig.update_layout(
        title="Heatmap de Predições por Hora e Dia da Semana",
        xaxis_title="Hora do Dia",
        yaxis_title="Dia da Semana",
        height=400
    )
    
    return fig


def main():
    """Função principal da página"""
    
    st.title("📊 Métricas e Dashboard")
    st.markdown("Acompanhe as métricas e performance do sistema em tempo real")
    
    # Atualização automática
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 📈 Dashboard em Tempo Real")
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=False)
    
    with col3:
        if st.button("♻️ Atualizar Dados"):
            st.rerun()
    
    if auto_refresh:
        st.info("🔄 Auto-refresh ativado - Atualização a cada 30 segundos")
        import time
        time.sleep(30)
        st.rerun()
    
    # Gerar dados mockados
    predictions_data, latency_data, confidence_data = generate_mock_data()
    
    # Métricas principais
    st.markdown("### 📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_predictions = predictions_data[['positive', 'negative', 'neutral']].sum().sum()
    avg_latency = latency_data['latency_ms'].mean()
    avg_confidence = confidence_data['confidence'].mean()
    positive_rate = predictions_data['positive'].sum() / total_predictions
    
    with col1:
        metric_card(
            title="Total de Predições",
            value=f"{int(total_predictions):,}",
            delta=f"+{np.random.randint(100, 500)} hoje",
            icon="📝",
            color="#EA1D2C"
        )
    
    with col2:
        metric_card(
            title="Latência Média",
            value=f"{avg_latency:.1f}ms",
            delta=f"-{np.random.randint(5, 15)}ms",
            icon="⚡",
            color="#17a2b8"
        )
    
    with col3:
        metric_card(
            title="Confiança Média",
            value=f"{avg_confidence:.1%}",
            delta=f"+{np.random.uniform(0.5, 2.0):.1f}%",
            icon="🎯",
            color="#28a745"
        )
    
    with col4:
        metric_card(
            title="Taxa Positiva",
            value=f"{positive_rate:.1%}",
            delta=f"+{np.random.uniform(1, 3):.1f}%",
            icon="😊",
            color="#ffc107"
        )
    
    st.markdown("---")
    
    # Gráficos principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Tendências", 
        "⏱️ Performance", 
        "🎯 Qualidade", 
        "🔥 Heatmaps"
    ])
    
    with tab1:
        st.markdown("### Tendências de Predições")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Gráfico de predições ao longo do tempo
            fig_predictions = plot_predictions_over_time(predictions_data)
            st.plotly_chart(fig_predictions, use_container_width=True)
        
        with col2:
            # Pizza de distribuição
            fig_distribution = plot_sentiment_distribution(predictions_data)
            st.plotly_chart(fig_distribution, use_container_width=True)
        
        # Estatísticas adicionais
        st.markdown("### 📊 Estatísticas Detalhadas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 😊 Sentimentos Positivos")
            st.metric("Total", f"{predictions_data['positive'].sum():,}")
            st.metric("Média Diária", f"{predictions_data['positive'].mean():.0f}")
            st.metric("Crescimento", f"+{np.random.uniform(5, 15):.1f}%")
        
        with col2:
            st.markdown("#### 😞 Sentimentos Negativos")
            st.metric("Total", f"{predictions_data['negative'].sum():,}")
            st.metric("Média Diária", f"{predictions_data['negative'].mean():.0f}")
            st.metric("Redução", f"-{np.random.uniform(2, 8):.1f}%")
        
        with col3:
            st.markdown("#### 😐 Sentimentos Neutros")
            st.metric("Total", f"{predictions_data['neutral'].sum():,}")
            st.metric("Média Diária", f"{predictions_data['neutral'].mean():.0f}")
            st.metric("Variação", f"+{np.random.uniform(1, 5):.1f}%")
    
    with tab2:
        st.markdown("### Performance e Latência")
        
        # Gráfico de latência
        fig_latency = plot_latency_metrics(latency_data)
        st.plotly_chart(fig_latency, use_container_width=True)
        
        # Métricas de performance
        st.markdown("### 📊 Métricas de Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Latência Média", f"{latency_data['latency_ms'].mean():.1f}ms")
        
        with col2:
            st.metric("P50", f"{np.percentile(latency_data['latency_ms'], 50):.1f}ms")
        
        with col3:
            st.metric("P95", f"{latency_data['p95'].mean():.1f}ms")
        
        with col4:
            st.metric("P99", f"{latency_data['p99'].mean():.1f}ms")
        
        # SLA Status
        st.markdown("### ⚡ SLA Status")
        
        sla_target = 100  # ms
        sla_compliance = (latency_data['latency_ms'] < sla_target).mean() * 100
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.progress(sla_compliance / 100, text=f"SLA Compliance: {sla_compliance:.1f}%")
        
        with col2:
            if sla_compliance >= 99:
                st.success("✅ Excelente")
            elif sla_compliance >= 95:
                st.warning("⚠️ Atenção")
            else:
                st.error("❌ Crítico")
    
    with tab3:
        st.markdown("### Qualidade das Predições")
        
        # Distribuição de confiança
        fig_confidence = plot_confidence_distribution(confidence_data)
        st.plotly_chart(fig_confidence, use_container_width=True)
        
        # Métricas de qualidade
        st.markdown("### 🎯 Métricas de Qualidade")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Confiança")
            st.metric("Média", f"{confidence_data['confidence'].mean():.1%}")
            st.metric("Mediana", f"{confidence_data['confidence'].median():.1%}")
            st.metric("Desvio Padrão", f"{confidence_data['confidence'].std():.1%}")
        
        with col2:
            st.markdown("#### Distribuição")
            high_conf = (confidence_data['confidence'] > 0.9).sum()
            med_conf = ((confidence_data['confidence'] > 0.7) & (confidence_data['confidence'] <= 0.9)).sum()
            low_conf = (confidence_data['confidence'] <= 0.7).sum()
            
            st.metric("Alta (>90%)", f"{high_conf:,}")
            st.metric("Média (70-90%)", f"{med_conf:,}")
            st.metric("Baixa (<70%)", f"{low_conf:,}")
        
        with col3:
            st.markdown("#### Modelo")
            st.metric("Acurácia", "94.7%")
            st.metric("F1-Score", "0.932")
            st.metric("AUC-ROC", "0.978")
    
    with tab4:
        st.markdown("### Padrões de Uso")
        
        # Heatmap
        fig_heatmap = plot_hourly_heatmap()
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Insights
        st.markdown("### 💡 Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **📊 Picos de Uso:**
            - Horário de almoço (12h-14h)
            - Fim do dia (18h-20h)
            - Finais de semana (Sáb-Dom)
            """)
        
        with col2:
            st.success("""
            **✅ Recomendações:**
            - Scale-up em horários de pico
            - Cache agressivo 12h-14h
            - Batch processing madrugada
            """)
    
    # Alertas e Notificações
    st.markdown("---")
    st.markdown("### 🔔 Alertas e Notificações")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ **Sistema Saudável**\nTodas as métricas dentro do esperado")
    
    with col2:
        st.warning("⚠️ **Atenção**\nLatência P99 acima de 100ms em 2% das requisições")
    
    with col3:
        st.info("ℹ️ **Informação**\nNovo modelo disponível para deploy")
    
    # Grafana embed (placeholder)
    st.markdown("---")
    st.markdown("### 📊 Grafana Dashboard")
    
    st.info("""
    🚧 **Grafana Integration**
    
    Para visualizar dashboards completos do Grafana, configure:
    1. Inicie o Grafana com `docker-compose up grafana`
    2. Acesse http://localhost:3000
    3. Dashboards disponíveis em: Dashboards → SentiBR
    
    Os dashboards incluem:
    - Model Performance
    - API Metrics
    - System Health
    - Business Metrics
    """)
    
    # Iframe do Grafana (se disponível)
    # st.components.v1.iframe("http://localhost:3000/d/sentibr", height=600)


if __name__ == "__main__":
    main()
