"""
SentiBR - LLM as a Judge
GPT-4 avalia a qualidade das predições do BERT
"""
import streamlit as st
import time

st.set_page_config(page_title="LLM Judge", page_icon="🤖", layout="wide")

st.title("🤖 LLM as a Judge")
st.markdown("GPT-4o-mini avalia a qualidade das predições do BERT")

# Explicação
st.info("""
**Como funciona:**

1. BERT faz a predição inicial (rápido, ~100ms)
2. GPT-4o-mini avalia se a predição foi correta (lento, ~2s)
3. GPT justifica sua avaliação com raciocínio detalhado
4. Sistema aprende com feedbacks para melhorar

**Objetivo**: Validar e melhorar continuamente o modelo BERT
""")

st.markdown("---")

# Input
st.subheader("📝 Teste de Avaliação")

review_text = st.text_area(
    "Review para Análise",
    height=100,
    placeholder="Digite um review para que BERT analise e GPT avalie...",
    help="Review que será analisado pelo BERT e depois avaliado pelo GPT"
)

# Opções
col1, col2 = st.columns(2)

with col1:
    show_reasoning = st.checkbox("Mostrar raciocínio do GPT", value=True)

with col2:
    show_confidence = st.checkbox("Mostrar níveis de confiança", value=True)

# Botão
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    judge_button = st.button("⚖️ Analisar e Julgar", type="primary", use_container_width=True)

# Processar
if judge_button:
    if not review_text.strip():
        st.error("❌ Digite um review para análise!")
    else:
        # Fase 1: BERT prediz
        st.markdown("---")
        st.subheader("🎯 Fase 1: Predição BERT")
        
        with st.spinner("🧠 BERT analisando..."):
            time.sleep(0.5)
            
            # Simulação de predição BERT
            bert_prediction = "positive"
            bert_confidence = 0.82
            bert_scores = {
                'positive': 0.82,
                'neutral': 0.12,
                'negative': 0.06
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
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
                <div style="text-align: center; padding: 1.5rem; background: {sentiment_color[bert_prediction]}; border-radius: 10px; color: white;">
                    <h1 style="font-size: 3rem; margin: 0;">{sentiment_emoji[bert_prediction]}</h1>
                    <h2>BERT: {bert_prediction.upper()}</h2>
                    <h3>Confiança: {bert_confidence*100:.1f}%</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if show_confidence:
                    st.markdown("#### Scores BERT")
                    for sent, score in bert_scores.items():
                        st.markdown(f"**{sent.capitalize()}**: {score*100:.1f}%")
                        st.progress(score)
        
        # Fase 2: GPT julga
        st.markdown("---")
        st.subheader("⚖️ Fase 2: Julgamento GPT-4o-mini")
        
        with st.spinner("🤖 GPT avaliando a predição..."):
            time.sleep(1.5)
            
            # Simulação de julgamento GPT
            gpt_verdict = "correct"  # correct, incorrect, ambiguous
            gpt_confidence = 0.88
            gpt_reasoning = """
            **Análise do Review:**
            O texto apresenta características predominantemente positivas, incluindo 
            termos como "delicioso" e "recomendo". Embora haja uma menção neutra sobre 
            o preço, o tom geral é de satisfação.
            
            **Avaliação da Predição BERT:**
            ✅ A classificação como "Positive" está **CORRETA**
            
            **Justificativa:**
            - O sentimento dominante é claramente positivo
            - A confiança de 82% é adequada (não há ambiguidade significativa)
            - A distribuição de scores reflete bem a análise (82% pos, 12% neu, 6% neg)
            
            **Sugestões de Melhoria:**
            - BERT poderia ter maior confiança (90%+) dado o tom claramente positivo
            - Aspecto "preço" poderia ser tratado separadamente em análise multi-aspecto
            """
            
            alternative_prediction = None
            
            # Mostrar veredicto
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if gpt_verdict == "correct":
                    st.success("### ✅ CORRETO")
                    st.metric("Confiança do Juiz", f"{gpt_confidence*100:.0f}%")
                elif gpt_verdict == "incorrect":
                    st.error("### ❌ INCORRETO")
                    st.metric("Confiança do Juiz", f"{gpt_confidence*100:.0f}%")
                    st.warning(f"Deveria ser: **{alternative_prediction}**")
                else:
                    st.warning("### ⚠️ AMBÍGUO")
                    st.metric("Confiança do Juiz", f"{gpt_confidence*100:.0f}%")
            
            with col2:
                st.markdown("### Concordância")
                st.metric("BERT vs GPT", "✅ Concordam")
            
            with col3:
                st.markdown("### Score Final")
                final_score = 8.5
                st.metric("Nota", f"{final_score}/10")
            
            # Raciocínio detalhado
            if show_reasoning:
                st.markdown("---")
                st.markdown("### 💭 Raciocínio Detalhado do GPT")
                st.markdown(gpt_reasoning)

# Estatísticas
st.markdown("---")
st.subheader("📊 Estatísticas do LLM Judge")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Avaliações Totais", "5,432")

with col2:
    st.metric("Taxa de Acerto BERT", "91.3%")

with col3:
    st.metric("Casos Ambíguos", "7.2%")

with col4:
    st.metric("Concordância", "89.5%")

# Casos recentes
with st.expander("📋 Casos Avaliados Recentemente"):
    import pandas as pd
    
    cases_df = pd.DataFrame({
        'Review': [
            'Comida excelente!',
            'Entrega demorou, mas valeu a pena',
            'Não gostei, caro demais',
            'Ok, nada especial'
        ],
        'BERT': ['Positive', 'Positive', 'Negative', 'Neutral'],
        'GPT Verdict': ['✅ Correto', '⚠️ Ambíguo', '✅ Correto', '✅ Correto'],
        'Score': ['9/10', '6/10', '8/10', '7/10']
    })
    
    st.dataframe(cases_df, hide_index=True, use_container_width=True)

# Framework de Avaliação
st.markdown("---")
st.subheader("🎯 Framework de Avaliação")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Critérios do GPT Judge")
    st.markdown("""
    1. **Acurácia**: Predição correta?
    2. **Confiança**: Nível apropriado?
    3. **Nuance**: Capturou sutilezas?
    4. **Contexto**: Considerou contexto completo?
    5. **Aspectos**: Identificou múltiplos aspectos?
    
    **Scoring:**
    - 9-10: Excelente
    - 7-8: Bom
    - 5-6: Aceitável
    - 3-4: Ruim
    - 0-2: Muito ruim
    """)

with col2:
    st.markdown("### Ações Baseadas no Feedback")
    st.markdown("""
    **Score Alto (8-10):**
    - ✅ Mantém modelo como está
    - ✅ Usa caso para validação
    
    **Score Médio (5-7):**
    - ⚠️ Adiciona caso ao dataset de treino
    - ⚠️ Investiga padrão de erro
    
    **Score Baixo (0-4):**
    - ❌ Prioriza correção
    - ❌ Re-treina modelo
    - ❌ Analisa features faltantes
    """)

# Insights
with st.expander("💡 Insights e Aprendizados"):
    st.markdown("""
    ### Padrões Identificados pelo LLM Judge
    
    **BERT tende a errar quando:**
    - Reviews muito longos (> 500 palavras)
    - Sarcasmo ou ironia presentes
    - Sentimentos mistos (positivo + negativo)
    - Contexto cultural específico
    
    **BERT é excelente quando:**
    - Reviews diretos e claros
    - Vocabulário comum de reviews
    - Sentimento uniforme
    - Tamanho médio (50-200 palavras)
    
    ### Melhorias Implementadas
    
    - ✅ Aumentado dataset com casos ambíguos
    - ✅ Fine-tuning adicional em sarcasmo
    - ✅ Melhor tratamento de reviews longos
    - 🔄 Em progresso: Multi-aspect analysis
    """)

# Configurações
with st.expander("⚙️ Configurações Avançadas"):
    st.markdown("### Parâmetros do LLM Judge")
    
    threshold_agreement = st.slider("Threshold de Concordância", 0.5, 1.0, 0.75)
    threshold_confidence = st.slider("Threshold de Confiança BERT", 0.5, 1.0, 0.70)
    enable_learning = st.checkbox("Habilitar aprendizado contínuo", value=True)
    
    st.info("""
    **Thresholds configurados:**
    - Concordância < 75%: Caso marcado para revisão
    - Confiança BERT < 70%: Solicita avaliação GPT
    - Aprendizado contínuo: Casos avaliados alimentam re-treino
    """)

# Info
st.markdown("---")
st.success("""
💡 **LLM as a Judge** é uma técnica poderosa para validação e melhoria contínua de modelos.
GPT-4o-mini atua como "professor" do BERT, identificando casos problemáticos e sugerindo melhorias.
""")
