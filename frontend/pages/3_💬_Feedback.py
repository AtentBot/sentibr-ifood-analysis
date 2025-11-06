"""
Página de Feedback
Interface para validar predições e fornecer feedback para melhoria do modelo
"""
import streamlit as st
import requests
from datetime import datetime
import pandas as pd
from pathlib import Path
import sys

# Adicionar componentes ao path
sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import sentiment_badge, metric_card


# Configuração da página
st.set_page_config(
    page_title="Feedback - SentiBR",
    page_icon="💬",
    layout="wide"
)


# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1"


def submit_feedback(text: str, predicted: str, correct: str, confidence: float, comments: str = ""):
    """
    Envia feedback para a API
    
    Args:
        text: Texto analisado
        predicted: Sentimento predito
        correct: Sentimento correto
        confidence: Confiança da predição
        comments: Comentários adicionais
    
    Returns:
        Response da API
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback",
            json={
                "text": text,
                "predicted_sentiment": predicted,
                "correct_sentiment": correct,
                "confidence": confidence,
                "comments": comments,
                "timestamp": datetime.now().isoformat()
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_feedback_stats():
    """Retorna estatísticas de feedback (mockado)"""
    return {
        "total_feedbacks": 1247,
        "corrections": 89,
        "accuracy_improvement": 2.3,
        "avg_confidence": 0.89,
        "feedbacks_today": 23
    }


def generate_sample_predictions():
    """Gera predições de exemplo para validação"""
    samples = [
        {
            "id": 1,
            "text": "A comida estava excelente! Super recomendo este restaurante.",
            "predicted": "positive",
            "confidence": 0.95
        },
        {
            "id": 2,
            "text": "Entrega demorou muito, mas a comida estava boa.",
            "predicted": "neutral",
            "confidence": 0.72
        },
        {
            "id": 3,
            "text": "Péssimo atendimento, nunca mais volto.",
            "predicted": "negative",
            "confidence": 0.98
        },
        {
            "id": 4,
            "text": "Normal, nada de especial.",
            "predicted": "neutral",
            "confidence": 0.65
        },
        {
            "id": 5,
            "text": "Adorei! A pizza estava divina e chegou quentinha.",
            "predicted": "positive",
            "confidence": 0.91
        }
    ]
    return samples


def main():
    """Função principal da página"""
    
    st.title("💬 Sistema de Feedback")
    st.markdown("Ajude a melhorar o modelo validando predições e fornecendo feedback")
    
    # Estatísticas de feedback
    st.markdown("### 📊 Estatísticas de Feedback")
    
    stats = get_feedback_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        metric_card(
            title="Total Feedbacks",
            value=f"{stats['total_feedbacks']:,}",
            icon="📝",
            color="#EA1D2C"
        )
    
    with col2:
        metric_card(
            title="Correções",
            value=f"{stats['corrections']}",
            icon="✏️",
            color="#ffc107"
        )
    
    with col3:
        metric_card(
            title="Melhoria",
            value=f"+{stats['accuracy_improvement']:.1f}%",
            icon="📈",
            color="#28a745"
        )
    
    with col4:
        metric_card(
            title="Confiança Média",
            value=f"{stats['avg_confidence']:.1%}",
            icon="🎯",
            color="#17a2b8"
        )
    
    with col5:
        metric_card(
            title="Hoje",
            value=f"{stats['feedbacks_today']}",
            icon="📅",
            color="#6c757d"
        )
    
    st.markdown("---")
    
    # Tabs principais
    tab1, tab2, tab3 = st.tabs([
        "✍️ Novo Feedback",
        "🔍 Validar Predições",
        "📜 Histórico"
    ])
    
    with tab1:
        st.markdown("### ✍️ Fornecer Novo Feedback")
        
        st.info("""
        💡 **Como funciona:**
        1. Cole ou digite um review de restaurante
        2. O sistema fará a predição automaticamente
        3. Valide se a predição está correta
        4. Adicione comentários (opcional)
        5. Envie o feedback
        """)
        
        # Input do texto
        feedback_text = st.text_area(
            "Review para Análise e Feedback:",
            height=150,
            placeholder="Cole aqui o review que deseja validar...",
            help="Digite ou cole um review de restaurante"
        )
        
        if st.button("🔍 Analisar e Validar", type="primary", use_container_width=True):
            if feedback_text.strip():
                with st.spinner("Analisando..."):
                    # Simular predição
                    import time
                    time.sleep(1)
                    
                    # Mock prediction
                    predicted_sentiment = "positive"
                    confidence = 0.87
                    
                    st.session_state['current_feedback'] = {
                        'text': feedback_text,
                        'predicted': predicted_sentiment,
                        'confidence': confidence
                    }
                    
                    st.success("✅ Análise concluída! Valide o resultado abaixo.")
            else:
                st.warning("⚠️ Digite um review para analisar.")
        
        # Formulário de feedback
        if 'current_feedback' in st.session_state:
            st.markdown("---")
            st.markdown("### 🎯 Validação da Predição")
            
            current = st.session_state['current_feedback']
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Review Analisado:**")
                st.info(current['text'])
            
            with col2:
                st.markdown("**Predição do Modelo:**")
                sentiment_badge(
                    current['predicted'],
                    current['confidence'],
                    size="small"
                )
            
            st.markdown("---")
            
            # Validação
            col1, col2 = st.columns(2)
            
            with col1:
                is_correct = st.radio(
                    "A predição está correta?",
                    ["Sim", "Não"],
                    horizontal=True
                )
            
            with col2:
                if is_correct == "Não":
                    correct_sentiment = st.selectbox(
                        "Qual o sentimento correto?",
                        ["positive", "negative", "neutral"],
                        format_func=lambda x: {"positive": "😊 Positivo", "negative": "😞 Negativo", "neutral": "😐 Neutro"}[x]
                    )
                else:
                    correct_sentiment = current['predicted']
            
            # Comentários opcionais
            comments = st.text_area(
                "Comentários adicionais (opcional):",
                placeholder="Ex: O modelo não captou o sarcasmo no texto...",
                help="Adicione observações que possam ajudar a melhorar o modelo"
            )
            
            # Botão de envio
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("📤 Enviar Feedback", type="primary", use_container_width=True):
                    result = submit_feedback(
                        text=current['text'],
                        predicted=current['predicted'],
                        correct=correct_sentiment,
                        confidence=current['confidence'],
                        comments=comments
                    )
                    
                    if "error" not in result:
                        st.success("✅ Feedback enviado com sucesso! Obrigado por ajudar a melhorar o modelo.")
                        del st.session_state['current_feedback']
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ Erro ao enviar feedback: {result['error']}")
            
            with col2:
                if st.button("🗑️ Cancelar", use_container_width=True):
                    del st.session_state['current_feedback']
                    st.rerun()
    
    with tab2:
        st.markdown("### 🔍 Validar Predições em Lote")
        
        st.info("""
        💡 **Validação Rápida**: Aqui você pode validar múltiplas predições de uma vez, 
        ideal para revisão rápida de casos com baixa confiança ou suspeitos.
        """)
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            confidence_filter = st.slider(
                "Confiança máxima:",
                0.0, 1.0, 0.8,
                help="Mostrar apenas predições com confiança abaixo deste valor"
            )
        
        with col2:
            sentiment_filter = st.multiselect(
                "Filtrar por sentimento:",
                ["positive", "negative", "neutral"],
                default=["positive", "negative", "neutral"],
                format_func=lambda x: {"positive": "😊 Positivo", "negative": "😞 Negativo", "neutral": "😐 Neutro"}[x]
            )
        
        with col3:
            limit = st.number_input("Quantidade:", 1, 50, 10)
        
        if st.button("🔍 Buscar Predições para Validar", use_container_width=True):
            st.markdown("---")
            
            # Gerar amostras
            samples = generate_sample_predictions()
            
            # Filtrar por confiança
            filtered_samples = [s for s in samples if s['confidence'] <= confidence_filter and s['predicted'] in sentiment_filter]
            
            if not filtered_samples:
                st.warning("⚠️ Nenhuma predição encontrada com os filtros aplicados.")
            else:
                st.success(f"✅ Encontradas {len(filtered_samples)} predições para validar")
                
                for i, sample in enumerate(filtered_samples[:limit], 1):
                    with st.expander(f"📝 Predição #{sample['id']} - Confiança: {sample['confidence']:.1%}", expanded=i==1):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown("**Review:**")
                            st.info(sample['text'])
                        
                        with col2:
                            st.markdown("**Predição:**")
                            sentiment_badge(
                                sample['predicted'],
                                sample['confidence'],
                                size="small"
                            )
                        
                        # Validação rápida
                        col1, col2, col3 = st.columns([1, 1, 2])
                        
                        with col1:
                            if st.button("✅ Correto", key=f"correct_{sample['id']}", use_container_width=True):
                                st.success("Feedback registrado!")
                        
                        with col2:
                            if st.button("❌ Incorreto", key=f"incorrect_{sample['id']}", use_container_width=True):
                                st.error("Marque o sentimento correto acima")
                        
                        with col3:
                            correct = st.selectbox(
                                "Sentimento correto:",
                                ["positive", "negative", "neutral"],
                                key=f"correct_sent_{sample['id']}",
                                format_func=lambda x: {"positive": "😊 Positivo", "negative": "😞 Negativo", "neutral": "😐 Neutro"}[x]
                            )
    
    with tab3:
        st.markdown("### 📜 Histórico de Feedbacks")
        
        # Filtros de data
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            date_from = st.date_input("Data inicial:", datetime.now().date())
        
        with col2:
            date_to = st.date_input("Data final:", datetime.now().date())
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Filtrar", use_container_width=True):
                st.rerun()
        
        # Gerar dados mockados de histórico
        history_data = pd.DataFrame({
            'Data': pd.date_range(end=datetime.now(), periods=50, freq='H'),
            'Review': [f"Review exemplo {i}" for i in range(50)],
            'Predição': ['positive', 'negative', 'neutral'] * 17 + ['positive'],
            'Correto': ['positive', 'negative', 'neutral'] * 16 + ['negative', 'positive'],
            'Confiança': [0.5 + i*0.01 for i in range(50)],
            'Status': ['Correto' if i % 3 == 0 else 'Corrigido' for i in range(50)]
        })
        
        # Exibir tabela
        st.dataframe(
            history_data.head(20),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Data": st.column_config.DatetimeColumn("Data", format="DD/MM/YYYY HH:mm"),
                "Confiança": st.column_config.ProgressColumn("Confiança", min_value=0, max_value=1),
                "Status": st.column_config.TextColumn("Status")
            }
        )
        
        # Download do histórico
        st.download_button(
            label="📥 Download Histórico (CSV)",
            data=history_data.to_csv(index=False).encode('utf-8'),
            file_name=f"feedback_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Sidebar com informações
    with st.sidebar:
        st.markdown("### 💡 Por que dar feedback?")
        
        st.markdown("""
        O feedback ajuda a:
        
        1. **🎯 Melhorar Precisão**
           - Identificar erros do modelo
           - Capturar casos extremos
        
        2. **📚 Expandir Dataset**
           - Adicionar novos exemplos
           - Balancear classes
        
        3. **🔄 Continuous Learning**
           - Retreinar modelo periodicamente
           - Adaptar a novos padrões
        
        4. **🐛 Detectar Problemas**
           - Drift de dados
           - Edge cases
        """)
        
        st.markdown("---")
        
        st.markdown("### 🎖️ Top Contribuidores")
        
        contributors = [
            ("👤 Usuário A", 127),
            ("👤 Usuário B", 98),
            ("👤 Usuário C", 76),
            ("👤 Você", 23)
        ]
        
        for name, count in contributors:
            st.markdown(f"**{name}**: {count} feedbacks")
        
        st.markdown("---")
        
        st.markdown("### 📈 Impacto do Feedback")
        
        st.metric("Melhoria de Acurácia", "+2.3%")
        st.metric("Casos Corrigidos", "89")
        st.metric("Novos Padrões", "12")


if __name__ == "__main__":
    main()
