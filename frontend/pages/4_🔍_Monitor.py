"""
Página de Monitoramento
Detecção de drift, health checks e alertas do sistema
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
    page_title="Monitoramento - SentiBR",
    page_icon="🔍",
    layout="wide"
)


# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1"


def check_system_health():
    """Verifica saúde do sistema"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "latency": response.elapsed.total_seconds()}
        else:
            return {"status": "degraded", "latency": None}
    except:
        return {"status": "down", "latency": None}


def generate_drift_data():
    """Gera dados de drift simulados"""
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    # Simular drift gradual
    baseline_mean = 100
    baseline_std = 15
    
    drift_factor = np.linspace(0, 0.3, 90)  # Drift crescente
    
    data = pd.DataFrame({
        'date': dates,
        'text_length_mean': baseline_mean + drift_factor * 30 + np.random.normal(0, 5, 90),
        'text_length_std': baseline_std + drift_factor * 10 + np.random.normal(0, 2, 90),
        'drift_score': drift_factor + np.random.normal(0, 0.05, 90),
        'confidence_mean': 0.90 - drift_factor * 0.15 + np.random.normal(0, 0.02, 90)
    })
    
    return data


def plot_drift_detection(data: pd.DataFrame):
    """Plota detecção de drift"""
    
    fig = go.Figure()
    
    # Drift score
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['drift_score'],
        name='Drift Score',
        mode='lines+markers',
        line=dict(color='#EA1D2C', width=2),
        fill='tozeroy'
    ))
    
    # Threshold lines
    fig.add_hline(
        y=0.15,
        line_dash="dash",
        line_color="orange",
        annotation_text="Warning Threshold",
        annotation_position="right"
    )
    
    fig.add_hline(
        y=0.25,
        line_dash="dash",
        line_color="red",
        annotation_text="Critical Threshold",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Detecção de Data Drift ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Drift Score",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def plot_feature_distribution(current_data, baseline_data, feature_name):
    """Compara distribuição atual vs baseline"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=baseline_data,
        name='Baseline',
        opacity=0.7,
        marker_color='#28a745',
        nbinsx=30
    ))
    
    fig.add_trace(go.Histogram(
        x=current_data,
        name='Atual',
        opacity=0.7,
        marker_color='#EA1D2C',
        nbinsx=30
    ))
    
    fig.update_layout(
        title=f"Distribuição: {feature_name}",
        xaxis_title=feature_name,
        yaxis_title="Frequência",
        height=350,
        barmode='overlay'
    )
    
    return fig


def plot_model_performance_over_time(data: pd.DataFrame):
    """Plota performance do modelo ao longo do tempo"""
    
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    performance_data = pd.DataFrame({
        'date': dates,
        'accuracy': 0.95 - np.random.normal(0, 0.01, 30),
        'f1_score': 0.93 - np.random.normal(0, 0.015, 30),
        'precision': 0.94 - np.random.normal(0, 0.012, 30),
        'recall': 0.92 - np.random.normal(0, 0.013, 30)
    })
    
    fig = go.Figure()
    
    metrics = ['accuracy', 'f1_score', 'precision', 'recall']
    colors = ['#28a745', '#17a2b8', '#ffc107', '#EA1D2C']
    
    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Scatter(
            x=performance_data['date'],
            y=performance_data[metric],
            name=metric.replace('_', ' ').title(),
            mode='lines+markers',
            line=dict(color=color, width=2)
        ))
    
    fig.update_layout(
        title="Métricas de Performance ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Score",
        height=400,
        hovermode='x unified',
        yaxis=dict(range=[0.85, 1.0])
    )
    
    return fig


def main():
    """Função principal da página"""
    
    st.title("🔍 Monitoramento e Observabilidade")
    st.markdown("Acompanhe a saúde do sistema, detecte drift e monitore alertas")
    
    # Auto-refresh
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 🔄 Status do Sistema")
    
    with col2:
        if st.button("♻️ Atualizar", use_container_width=True):
            st.rerun()
    
    # Health Check
    health = check_system_health()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if health['status'] == 'healthy':
            st.success("✅ **Sistema Online**")
        elif health['status'] == 'degraded':
            st.warning("⚠️ **Performance Degradada**")
        else:
            st.error("❌ **Sistema Offline**")
    
    with col2:
        if health['latency']:
            st.metric("Latência API", f"{health['latency']*1000:.0f}ms")
        else:
            st.metric("Latência API", "N/A")
    
    with col3:
        st.metric("Uptime", "99.97%")
    
    with col4:
        st.metric("Última Falha", "23h atrás")
    
    st.markdown("---")
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Data Drift",
        "🎯 Model Performance",
        "🔔 Alertas",
        "📈 System Metrics"
    ])
    
    with tab1:
        st.markdown("### 📊 Detecção de Data Drift")
        
        st.info("""
        💡 **Data Drift**: Mudanças na distribuição dos dados de entrada ao longo do tempo. 
        O monitoramento contínuo ajuda a detectar quando o modelo precisa ser retreinado.
        """)
        
        # Gerar dados de drift
        drift_data = generate_drift_data()
        
        # Gráfico principal de drift
        fig_drift = plot_drift_detection(drift_data)
        st.plotly_chart(fig_drift, use_container_width=True)
        
        # Métricas de drift
        st.markdown("### 📊 Métricas de Drift")
        
        col1, col2, col3, col4 = st.columns(4)
        
        current_drift = drift_data['drift_score'].iloc[-1]
        drift_trend = drift_data['drift_score'].iloc[-7:].mean()
        
        with col1:
            if current_drift < 0.15:
                color = "#28a745"
                status = "Normal"
            elif current_drift < 0.25:
                color = "#ffc107"
                status = "Atenção"
            else:
                color = "#dc3545"
                status = "Crítico"
            
            metric_card(
                title="Drift Atual",
                value=f"{current_drift:.2%}",
                delta=status,
                icon="📊",
                color=color
            )
        
        with col2:
            metric_card(
                title="Tendência (7d)",
                value=f"{drift_trend:.2%}",
                delta=f"+{(current_drift - drift_trend):.2%}",
                icon="📈",
                color="#17a2b8"
            )
        
        with col3:
            metric_card(
                title="Máximo (90d)",
                value=f"{drift_data['drift_score'].max():.2%}",
                icon="⚠️",
                color="#EA1D2C"
            )
        
        with col4:
            days_since_retrain = 45
            metric_card(
                title="Último Retreino",
                value=f"{days_since_retrain}d",
                icon="🔄",
                color="#6c757d"
            )
        
        # Recomendações
        st.markdown("### 💡 Recomendações")
        
        if current_drift >= 0.25:
            st.error("""
            🚨 **AÇÃO NECESSÁRIA**: Drift crítico detectado!
            - Retreinar o modelo imediatamente
            - Revisar dados recentes
            - Validar performance atual
            """)
        elif current_drift >= 0.15:
            st.warning("""
            ⚠️ **ATENÇÃO**: Drift elevado detectado
            - Agendar retreino em breve
            - Monitorar de perto
            - Coletar mais feedbacks
            """)
        else:
            st.success("""
            ✅ **STATUS OK**: Drift dentro do esperado
            - Continuar monitoramento
            - Próximo retreino programado
            """)
        
        # Análise por features
        st.markdown("### 🔬 Análise por Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição de tamanho de texto
            baseline_lengths = np.random.normal(100, 15, 1000)
            current_lengths = np.random.normal(120, 18, 1000)
            
            fig1 = plot_feature_distribution(
                current_lengths,
                baseline_lengths,
                "Tamanho do Texto (caracteres)"
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Teste KS
            from scipy import stats
            ks_stat, ks_pval = stats.ks_2samp(baseline_lengths, current_lengths)
            
            if ks_pval < 0.05:
                st.warning(f"⚠️ Diferença significativa detectada (KS p-value: {ks_pval:.4f})")
            else:
                st.success(f"✅ Distribuição similar (KS p-value: {ks_pval:.4f})")
        
        with col2:
            # Distribuição de confiança
            baseline_conf = np.random.beta(9, 2, 1000)
            current_conf = np.random.beta(7, 3, 1000)
            
            fig2 = plot_feature_distribution(
                current_conf,
                baseline_conf,
                "Confiança das Predições"
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Teste KS
            ks_stat, ks_pval = stats.ks_2samp(baseline_conf, current_conf)
            
            if ks_pval < 0.05:
                st.warning(f"⚠️ Diferença significativa detectada (KS p-value: {ks_pval:.4f})")
            else:
                st.success(f"✅ Distribuição similar (KS p-value: {ks_pval:.4f})")
    
    with tab2:
        st.markdown("### 🎯 Performance do Modelo")
        
        # Gráfico de performance
        fig_perf = plot_model_performance_over_time(drift_data)
        st.plotly_chart(fig_perf, use_container_width=True)
        
        # Métricas atuais
        st.markdown("### 📊 Métricas Atuais vs Baseline")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_card(
                title="Accuracy",
                value="94.7%",
                delta="-0.3%",
                icon="🎯",
                color="#28a745"
            )
        
        with col2:
            metric_card(
                title="F1-Score",
                value="0.932",
                delta="-0.008",
                icon="📊",
                color="#17a2b8"
            )
        
        with col3:
            metric_card(
                title="Precision",
                value="0.941",
                delta="-0.005",
                icon="🔍",
                color="#ffc107"
            )
        
        with col4:
            metric_card(
                title="Recall",
                value="0.923",
                delta="-0.011",
                icon="📈",
                color="#EA1D2C"
            )
        
        # Matriz de confusão
        st.markdown("### 📊 Matriz de Confusão (Últimos 7 dias)")
        
        confusion_matrix = np.array([
            [450, 23, 12],
            [18, 380, 15],
            [10, 20, 290]
        ])
        
        labels = ['Positivo', 'Negativo', 'Neutro']
        
        fig_cm = go.Figure(data=go.Heatmap(
            z=confusion_matrix,
            x=labels,
            y=labels,
            text=confusion_matrix,
            texttemplate='%{text}',
            textfont={"size": 16},
            colorscale='RdYlGn',
            reversescale=False
        ))
        
        fig_cm.update_layout(
            title="Matriz de Confusão",
            xaxis_title="Predito",
            yaxis_title="Real",
            height=400
        )
        
        st.plotly_chart(fig_cm, use_container_width=True)
        
        # Análise de erros
        st.markdown("### 🔍 Análise de Erros Comuns")
        
        errors = pd.DataFrame({
            'Tipo': [
                'Positivo → Negativo',
                'Negativo → Positivo',
                'Neutro → Positivo',
                'Neutro → Negativo',
                'Positivo → Neutro'
            ],
            'Quantidade': [23, 18, 20, 10, 12],
            'Taxa': [4.7, 4.4, 6.3, 3.2, 2.5]
        })
        
        st.dataframe(
            errors,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Taxa": st.column_config.ProgressColumn(
                    "Taxa de Erro (%)",
                    min_value=0,
                    max_value=10,
                    format="%.1f%%"
                )
            }
        )
    
    with tab3:
        st.markdown("### 🔔 Sistema de Alertas")
        
        # Alertas ativos
        st.markdown("#### 🚨 Alertas Ativos")
        
        active_alerts = [
            {
                "severity": "warning",
                "title": "Drift Elevado Detectado",
                "description": "O drift score ultrapassou 15% nas últimas 24h",
                "timestamp": "2024-11-05 08:30",
                "action": "Revisar dados e considerar retreino"
            },
            {
                "severity": "info",
                "title": "Latência P99 Elevada",
                "description": "P99 acima de 100ms em 3% das requisições",
                "timestamp": "2024-11-05 07:15",
                "action": "Investigar gargalos de performance"
            }
        ]
        
        for alert in active_alerts:
            if alert["severity"] == "critical":
                alert_type = "error"
                icon = "🚨"
            elif alert["severity"] == "warning":
                alert_type = "warning"
                icon = "⚠️"
            else:
                alert_type = "info"
                icon = "ℹ️"
            
            with st.container():
                eval(f"st.{alert_type}")(f"""
                {icon} **{alert['title']}**
                
                {alert['description']}
                
                **Ação recomendada**: {alert['action']}
                
                ⏰ {alert['timestamp']}
                """)
        
        st.markdown("---")
        
        # Histórico de alertas
        st.markdown("#### 📜 Histórico de Alertas (Últimos 7 dias)")
        
        alert_history = pd.DataFrame({
            'Data': pd.date_range(end=datetime.now(), periods=20, freq='12H'),
            'Tipo': ['Warning', 'Info', 'Critical', 'Warning', 'Info'] * 4,
            'Alerta': [
                'Drift elevado', 'Latência alta', 'API down', 
                'Memória alta', 'Disco cheio'
            ] * 4,
            'Status': ['Resolvido', 'Ativo', 'Resolvido', 'Resolvido', 'Ativo'] * 4
        })
        
        st.dataframe(
            alert_history.head(10),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Data": st.column_config.DatetimeColumn(
                    "Data",
                    format="DD/MM/YYYY HH:mm"
                )
            }
        )
        
        # Configurações de alertas
        st.markdown("---")
        st.markdown("#### ⚙️ Configurações de Alertas")
        
        with st.expander("Configurar Thresholds"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.slider("Drift Warning", 0.0, 1.0, 0.15, 0.01)
                st.slider("Drift Critical", 0.0, 1.0, 0.25, 0.01)
                st.slider("Latência Warning (ms)", 0, 500, 100, 10)
            
            with col2:
                st.slider("Accuracy Min", 0.0, 1.0, 0.90, 0.01)
                st.slider("Confidence Min", 0.0, 1.0, 0.70, 0.01)
                st.slider("Error Rate Max (%)", 0, 20, 10, 1)
    
    with tab4:
        st.markdown("### 📈 System Metrics")
        
        st.info("""
        📊 **Prometheus & Grafana Integration**
        
        Para métricas detalhadas do sistema, acesse:
        - Prometheus: http://localhost:9090
        - Grafana: http://localhost:3000
        """)
        
        # Métricas de sistema
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_card(
                title="CPU Usage",
                value="45%",
                delta="+5%",
                icon="💻",
                color="#17a2b8"
            )
        
        with col2:
            metric_card(
                title="Memory",
                value="3.2GB",
                delta="+0.3GB",
                icon="🧠",
                color="#28a745"
            )
        
        with col3:
            metric_card(
                title="Disk I/O",
                value="120MB/s",
                delta="-10MB/s",
                icon="💾",
                color="#ffc107"
            )
        
        with col4:
            metric_card(
                title="Network",
                value="45Mbps",
                delta="+5Mbps",
                icon="🌐",
                color="#EA1D2C"
            )
        
        # Link para Grafana
        st.markdown("### 📊 Dashboards Grafana")
        
        dashboards = [
            ("Model Performance", "http://localhost:3000/d/model-perf"),
            ("API Metrics", "http://localhost:3000/d/api-metrics"),
            ("System Health", "http://localhost:3000/d/system-health"),
            ("Business Metrics", "http://localhost:3000/d/business")
        ]
        
        cols = st.columns(4)
        for i, (name, url) in enumerate(dashboards):
            with cols[i]:
                st.markdown(f"[📊 {name}]({url})")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Quick Status")
        
        # Status resumido
        status_items = [
            ("✅ API", "Online"),
            ("✅ Modelo", "Healthy"),
            ("⚠️ Drift", "Atenção"),
            ("✅ Performance", "Normal"),
            ("✅ Alertas", "2 Ativos")
        ]
        
        for item, status in status_items:
            st.markdown(f"**{item}**: {status}")
        
        st.markdown("---")
        
        st.markdown("### 📊 Última Verificação")
        st.markdown(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        
        if st.button("🔄 Verificar Agora", use_container_width=True):
            st.rerun()


if __name__ == "__main__":
    main()
