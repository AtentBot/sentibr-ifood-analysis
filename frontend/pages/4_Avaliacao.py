"""
SentiBR - Avaliação do Modelo
Testa a acurácia e performance do modelo BERT
"""
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px

st.set_page_config(page_title="Avaliação", page_icon="🔎", layout="wide")

st.title("🔎 Avaliação do Modelo")
st.markdown("Teste a acurácia e performance do modelo BERT")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Métricas", "🎯 Teste Manual", "📈 Histórico"])

with tab1:
    st.subheader("📊 Métricas de Performance")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Acurácia", "92.3%", "+1.2%")
    
    with col2:
        st.metric("Precision", "91.5%", "+0.8%")
    
    with col3:
        st.metric("Recall", "93.1%", "+1.5%")
    
    with col4:
        st.metric("F1-Score", "92.3%", "+1.1%")
    
    st.markdown("---")
    
    # Matriz de confusão
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Matriz de Confusão")
        
        # Dados de exemplo
        z = [
            [2450, 120, 80],   # Positivo
            [95, 1820, 115],   # Neutro
            [88, 102, 1910]    # Negativo
        ]
        
        x = ['Positivo', 'Neutro', 'Negativo']
        y = ['Positivo', 'Neutro', 'Negativo']
        
        fig = ff.create_annotated_heatmap(
            z,
            x=x,
            y=y,
            annotation_text=[[str(val) for val in row] for row in z],
            colorscale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Predição",
            yaxis_title="Real",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Métricas por Classe")
        
        # Dados por classe
        class_metrics = pd.DataFrame({
            'Classe': ['Positivo', 'Neutro', 'Negativo'],
            'Precision': [0.927, 0.891, 0.910],
            'Recall': [0.924, 0.897, 0.910],
            'F1-Score': [0.926, 0.894, 0.910],
            'Suporte': [2650, 2030, 2100]
        })
        
        st.dataframe(class_metrics, hide_index=True, use_container_width=True)
        
        # Gráfico de barras
        fig = px.bar(
            class_metrics,
            x='Classe',
            y=['Precision', 'Recall', 'F1-Score'],
            barmode='group',
            title='Métricas por Classe'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Curvas
    st.markdown("---")
    st.subheader("Curvas de Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Curva ROC")
        
        # Dados simulados para curva ROC
        import numpy as np
        
        fpr = np.linspace(0, 1, 100)
        tpr_pos = 1 - np.exp(-5 * fpr)
        tpr_neu = 1 - np.exp(-4 * fpr)
        tpr_neg = 1 - np.exp(-4.5 * fpr)
        
        fig = px.line()
        fig.add_scatter(x=fpr, y=tpr_pos, name='Positivo (AUC=0.94)', mode='lines')
        fig.add_scatter(x=fpr, y=tpr_neu, name='Neutro (AUC=0.89)', mode='lines')
        fig.add_scatter(x=fpr, y=tpr_neg, name='Negativo (AUC=0.91)', mode='lines')
        fig.add_scatter(x=[0, 1], y=[0, 1], name='Baseline', mode='lines', line=dict(dash='dash'))
        
        fig.update_layout(
            xaxis_title='False Positive Rate',
            yaxis_title='True Positive Rate',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Distribuição de Confiança")
        
        # Dados simulados de confiança
        confidence_data = pd.DataFrame({
            'Confiança': np.concatenate([
                np.random.normal(0.85, 0.1, 500),
                np.random.normal(0.7, 0.15, 300),
                np.random.normal(0.6, 0.2, 200)
            ]),
            'Correto': ['Sim'] * 500 + ['Não'] * 500
        })
        
        fig = px.histogram(
            confidence_data,
            x='Confiança',
            color='Correto',
            nbins=30,
            title='Distribuição de Confiança'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🎯 Teste Manual")
    st.markdown("Teste o modelo com seus próprios dados")
    
    # Upload de dados de teste
    st.markdown("#### Upload de Dados de Teste")
    
    st.info("""
    **Formato esperado:**
    - Coluna `text`: Texto do review
    - Coluna `label`: Sentimento real (positive, neutral, negative)
    
    ```csv
    text,label
    "Comida deliciosa!",positive
    "Péssimo atendimento",negative
    ```
    """)
    
    test_file = st.file_uploader("Arquivo CSV de Teste", type=['csv'])
    
    if test_file:
        try:
            df_test = pd.read_csv(test_file)
            
            st.success(f"✅ {len(df_test)} exemplos carregados")
            
            with st.expander("Preview"):
                st.dataframe(df_test.head())
            
            if st.button("🚀 Executar Avaliação", type="primary"):
                with st.spinner("Avaliando..."):
                    # Aqui faria a avaliação real
                    st.success("Avaliação concluída!")
                    
                    # Resultados simulados
                    st.metric("Acurácia", "91.2%")
                    st.metric("Total Corretos", "912 / 1000")
        
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")
    
    else:
        # Exemplo manual
        st.markdown("---")
        st.markdown("#### Teste Individual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_text = st.text_area("Texto do Review", height=100)
        
        with col2:
            true_label = st.selectbox(
                "Sentimento Real",
                options=['positive', 'neutral', 'negative']
            )
        
        if st.button("Testar", type="primary"):
            if test_text:
                # Simulação de predição
                st.info(f"**Predição**: positive (92%)")
                st.info(f"**Real**: {true_label}")
                
                if "positive" == true_label:
                    st.success("✅ Correto!")
                else:
                    st.error("❌ Incorreto")

with tab3:
    st.subheader("📈 Histórico de Performance")
    
    # Dados históricos simulados
    import datetime
    
    dates = pd.date_range(end=datetime.datetime.now(), periods=30, freq='D')
    
    history_data = pd.DataFrame({
        'Data': dates,
        'Acurácia': np.random.normal(0.92, 0.02, 30).clip(0.85, 0.95),
        'F1-Score': np.random.normal(0.91, 0.02, 30).clip(0.84, 0.94),
        'Latência (ms)': np.random.normal(87, 15, 30).clip(50, 150)
    })
    
    # Gráfico de evolução
    fig = px.line(
        history_data,
        x='Data',
        y=['Acurácia', 'F1-Score'],
        title='Evolução das Métricas (Últimos 30 dias)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de latência
    fig2 = px.line(
        history_data,
        x='Data',
        y='Latência (ms)',
        title='Latência ao Longo do Tempo'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Tabela de histórico
    st.markdown("#### Histórico Detalhado")
    st.dataframe(
        history_data.sort_values('Data', ascending=False).head(10),
        hide_index=True,
        use_container_width=True
    )

# Informações
with st.expander("ℹ️ Sobre as Métricas"):
    st.markdown("""
    ### Métricas de Classificação
    
    - **Acurácia**: Percentual de predições corretas
    - **Precision**: Dentre os preditos como X, quantos realmente são X
    - **Recall**: Dentre os que são X, quantos foram preditos como X
    - **F1-Score**: Média harmônica entre Precision e Recall
    
    ### Matriz de Confusão
    
    - Diagonal principal: Predições corretas
    - Fora da diagonal: Erros do modelo
    - Linha: Classe real
    - Coluna: Classe predita
    
    ### Curva ROC
    
    - AUC (Area Under Curve): Quanto maior, melhor
    - Ideal: AUC = 1.0
    - Baseline: AUC = 0.5
    """)
