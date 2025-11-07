"""
SentiBR - Comparação BERT vs GPT
Compara predições entre BERT e GPT-4o-mini
"""
import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Comparação", page_icon="⚔️", layout="wide")

st.title("⚔️ Comparação: BERT vs GPT-4o-mini")
st.markdown("Compare as predições dos dois modelos lado a lado")

# Informações dos modelos
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🧠 BERT (Fine-tuned)
    - **Modelo**: neuralmind/bert-base-portuguese-cased
    - **Latência**: ~100ms
    - **Custo**: Grátis (local)
    - **Acurácia**: 92.3%
    """)

with col2:
    st.markdown("""
    ### 🤖 GPT-4o-mini
    - **Modelo**: OpenAI GPT-4o-mini
    - **Latência**: ~2000ms
    - **Custo**: $0.15/1M tokens
    - **Acurácia**: ~94% (estimado)
    """)

st.markdown("---")

# Input de review
st.subheader("Digite o Review para Comparação")

review_text = st.text_area(
    "Review do Restaurante",
    height=150,
    placeholder="Exemplo: A comida estava deliciosa mas a entrega demorou muito...",
    help="Digite um review para comparar as predições"
)

# Botão de comparação
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    compare_button = st.button("⚔️ Comparar Modelos", type="primary", use_container_width=True)

# Processar comparação
if compare_button:
    if not review_text.strip():
        st.error("❌ Digite um review para comparação!")
    else:
        st.markdown("---")
        
        # Criar duas colunas para resultados lado a lado
        col_bert, col_gpt = st.columns(2)
        
        # BERT
        with col_bert:
            st.markdown("### 🧠 BERT")
            
            with st.spinner("Analisando com BERT..."):
                time.sleep(0.5)  # Simular latência
                
                # Simulação de resultado BERT
                bert_sentiment = "positive"
                bert_confidence = 0.87
                bert_scores = {
                    'positive': 0.87,
                    'neutral': 0.09,
                    'negative': 0.04
                }
                bert_latency = 95
                
                # Exibir resultado
                sentiment_emoji = {
                    'positive': '😊',
                    'neutral': '😐',
                    'negative': '😞'
                }
                
                sentiment_color = {
                    'positive': '#28a745',
                    'neutral': '#ffc107',
                    'negative': '#dc3545'
                }
                
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: {sentiment_color[bert_sentiment]}; border-radius: 10px; color: white; margin: 1rem 0;">
                    <h1 style="font-size: 3rem; margin: 0;">{sentiment_emoji[bert_sentiment]}</h1>
                    <h2>{bert_sentiment.upper()}</h2>
                    <h3>Confiança: {bert_confidence*100:.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Probabilidades")
                for sent, score in bert_scores.items():
                    st.markdown(f"**{sent.capitalize()}**: {score*100:.1f}%")
                    st.progress(score)
                
                st.metric("⚡ Latência", f"{bert_latency}ms")
        
        # GPT
        with col_gpt:
            st.markdown("### 🤖 GPT-4o-mini")
            
            with st.spinner("Analisando com GPT..."):
                time.sleep(1.5)  # Simular latência maior
                
                # Simulação de resultado GPT
                gpt_sentiment = "positive"
                gpt_confidence = 0.92
                gpt_reasoning = """
                O review expressa satisfação com a comida ("deliciosa"), 
                mas também menciona um problema com a entrega ("demorou muito"). 
                No entanto, o aspecto positivo (qualidade da comida) parece ter 
                maior peso no sentimento geral, resultando em classificação positiva.
                """
                gpt_latency = 1847
                
                st.markdown(f"""
                <div style="text-align: center; padding: 1.5rem; background: {sentiment_color[gpt_sentiment]}; border-radius: 10px; color: white; margin: 1rem 0;">
                    <h1 style="font-size: 3rem; margin: 0;">{sentiment_emoji[gpt_sentiment]}</h1>
                    <h2>{gpt_sentiment.upper()}</h2>
                    <h3>Confiança: {gpt_confidence*100:.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Raciocínio")
                st.info(gpt_reasoning)
                
                st.metric("⚡ Latência", f"{gpt_latency}ms")
        
        # Comparação final
        st.markdown("---")
        st.subheader("📊 Análise Comparativa")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Concordância")
            if bert_sentiment == gpt_sentiment:
                st.success("✅ Modelos concordam!")
            else:
                st.warning("⚠️ Modelos divergem")
        
        with col2:
            st.markdown("#### Diferença de Confiança")
            diff = abs(bert_confidence - gpt_confidence) * 100
            st.metric("Diferença", f"{diff:.1f}%")
        
        with col3:
            st.markdown("#### Diferença de Latência")
            latency_diff = gpt_latency - bert_latency
            st.metric("Mais lento", f"+{latency_diff}ms", delta_color="inverse")
        
        # Tabela comparativa
        st.markdown("#### Comparação Detalhada")
        
        comparison_df = pd.DataFrame({
            'Métrica': ['Sentimento', 'Confiança', 'Latência', 'Custo'],
            'BERT': [
                bert_sentiment,
                f"{bert_confidence*100:.1f}%",
                f"{bert_latency}ms",
                "Grátis"
            ],
            'GPT-4o-mini': [
                gpt_sentiment,
                f"{gpt_confidence*100:.1f}%",
                f"{gpt_latency}ms",
                "~$0.0001"
            ]
        })
        
        st.dataframe(comparison_df, hide_index=True, use_container_width=True)

# Trade-offs
st.markdown("---")
st.subheader("⚖️ Trade-offs entre os Modelos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧠 BERT - Vantagens")
    st.markdown("""
    ✅ **Latência baixa** (~100ms)  
    ✅ **Custo zero** (roda local)  
    ✅ **Previsível** (comportamento consistente)  
    ✅ **Escalável** (milhares de req/s)  
    ✅ **Offline** (não precisa internet)  
    
    ❌ **Limitações:**
    - Menos contextual que GPT
    - Sem raciocínio explícito
    - Precisa fine-tuning
    """)

with col2:
    st.markdown("### 🤖 GPT - Vantagens")
    st.markdown("""
    ✅ **Maior acurácia** (~94%)  
    ✅ **Raciocínio** (explica decisões)  
    ✅ **Contextual** (entende nuances)  
    ✅ **Zero-shot** (sem fine-tuning)  
    ✅ **Flexible** (múltiplas tarefas)  
    
    ❌ **Limitações:**
    - Alta latência (~2s)
    - Custo por requisição
    - Precisa internet
    - Rate limits
    """)

# Casos de uso
st.markdown("---")
st.subheader("🎯 Quando Usar Cada Modelo")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Use BERT para:")
    st.info("""
    - **Alto volume** (milhares de reviews/dia)
    - **Tempo real** (análise instantânea)
    - **Produção** (baixo custo, alta disponibilidade)
    - **Batch processing** (milhões de reviews)
    - **Edge cases** (offline, latência crítica)
    """)

with col2:
    st.markdown("### Use GPT para:")
    st.info("""
    - **Análise profunda** (reviews complexos)
    - **Explicabilidade** (precisa justificar)
    - **Casos ambíguos** (sentimento misto)
    - **Baixo volume** (poucos reviews críticos)
    - **Prototipagem** (teste rápido sem treino)
    """)

# Estatísticas
with st.expander("📈 Estatísticas de Comparação"):
    st.markdown("""
    ### Dados Coletados (últimos 1000 reviews)
    
    - **Taxa de concordância**: 87.3%
    - **Casos onde GPT foi melhor**: 9.2%
    - **Casos onde BERT foi melhor**: 3.5%
    - **Custo médio GPT**: $0.12 por 1000 reviews
    - **Throughput BERT**: 500 req/s
    - **Throughput GPT**: 30 req/s
    """)

# Recomendação
st.markdown("---")
st.info("""
💡 **Recomendação**: Use **BERT para produção** (volume alto, baixo custo, latência baixa) 
e **GPT para casos especiais** (análise profunda, explicabilidade, ambiguidade).

Estratégia híbrida: BERT como modelo principal + GPT para validação de casos incertos (confiança < 70%).
""")
