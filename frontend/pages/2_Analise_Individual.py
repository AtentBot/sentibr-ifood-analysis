"""
SentiBR - Análise Individual v2
Com detecção de baixa confiança
"""
import streamlit as st
import requests
import time

st.set_page_config(page_title="Análise Individual", page_icon="🔍", layout="wide")

st.title("🔍 Análise Individual de Sentimento")
st.markdown("Analise o sentimento de um review de restaurante")

# API endpoint
API_URL = "http://api:8000/api/v1/predict"

# CONFIGURAÇÃO DE THRESHOLD
CONFIDENCE_THRESHOLD = 0.65  # 65% - abaixo disso, mostrar aviso

# Input do review
st.subheader("Digite o Review")

review_text = st.text_area(
    "Review do Restaurante",
    height=150,
    placeholder="Exemplo: A comida estava deliciosa! Entrega rápida e atendimento excelente. Recomendo muito!",
    help="Digite ou cole o texto do review que deseja analisar"
)

# Botão de análise
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    analyze_button = st.button("🚀 Analisar Sentimento", type="primary", use_container_width=True)

# Processar análise
if analyze_button:
    if not review_text.strip():
        st.error("❌ Por favor, digite um review para análise!")
    else:
        with st.spinner("🔄 Analisando sentimento..."):
            try:
                # Fazer requisição à API
                start_time = time.time()
                
                response = requests.post(
                    API_URL,
                    json={"text": review_text},
                    timeout=10
                )
                
                elapsed_time = (time.time() - start_time) * 1000  # em ms
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Sentimento principal
                    sentiment = result.get('sentiment', 'unknown')
                    confidence = result.get('confidence', 0)
                    scores = result.get('scores', {})
                    
                    # ============================================================
                    # VERIFICAÇÃO DE CONFIANÇA CRÍTICA
                    # ============================================================
                    if confidence < CONFIDENCE_THRESHOLD:
                        st.error(f"""
                        ⚠️ **ATENÇÃO: BAIXA CONFIANÇA ({confidence*100:.1f}%)**
                        
                        O modelo está **INCERTO** sobre esta classificação!
                        
                        **Possíveis causas:**
                        - Review ambíguo ou misto
                        - Modelo não viu exemplos similares
                        - Sarcasmo ou ironia no texto
                        - Contexto complexo
                        
                        **Recomendações:**
                        1. ⚠️ **NÃO confie** nesta classificação
                        2. 👁️ Revisar manualmente
                        3. 🔄 Considere retreinar o modelo com mais exemplos
                        4. 🤖 Use GPT para comparação (página Comparação)
                        """)
                    
                    st.success("✅ Análise concluída!")
                    
                    # Resultados
                    st.markdown("---")
                    st.subheader("📊 Resultados da Análise")
                    
                    # Emoji baseado no sentimento
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
                    
                    emoji = sentiment_emoji.get(sentiment, '❓')
                    color = sentiment_color.get(sentiment, '#6c757d')
                    
                    # Adicionar borda vermelha se confiança baixa
                    border_style = "border: 3px solid #dc3545;" if confidence < CONFIDENCE_THRESHOLD else ""
                    
                    # Exibir resultado principal
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 2rem; background: {color}; border-radius: 10px; color: white; {border_style}">
                            <h1 style="font-size: 4rem; margin: 0;">{emoji}</h1>
                            <h2 style="margin: 1rem 0;">{sentiment.upper()}</h2>
                            <h3>Confiança: {confidence:.1f}%</h3>
                            {f'<p style="color: #fff; font-weight: bold;">⚠️ INCERTO</p>' if confidence < CONFIDENCE_THRESHOLD else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("### Probabilidades")
                        
                        for sent_type, score in scores.items():
                            percentage = score * 100
                            
                            # Destacar se score alto mas não foi escolhido
                            if sent_type != sentiment and score > 0.35:
                                st.warning(f"⚠️ **{sent_type.capitalize()}**: {percentage:.1f}% (competindo!)")
                            else:
                                st.markdown(f"**{sent_type.capitalize()}**: {percentage:.1f}%")
                            
                            st.progress(score)
                    
                    with col3:
                        st.markdown("### Métricas")
                        st.metric("Latência", f"{elapsed_time:.0f}ms")
                        st.metric("Comprimento", f"{len(review_text)} chars")
                        st.metric("Palavras", f"{len(review_text.split())} palavras")
                        
                        # Indicador de confiança
                        if confidence >= 0.85:
                            st.success("✅ Alta Confiança")
                        elif confidence >= CONFIDENCE_THRESHOLD:
                            st.info("ℹ️ Confiança Moderada")
                        else:
                            st.error("⚠️ Baixa Confiança")
                    
                    # Análise detalhada
                    st.markdown("---")
                    st.subheader("📝 Análise Detalhada")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Review Original")
                        st.info(review_text)
                        
                        # Análise de palavras-chave (simplificada)
                        palavras_negativas = ['péssima', 'ruim', 'horrível', 'demora', 'frio', 'vazou', 'mal', 'não', 'difícil']
                        palavras_positivas = ['ótimo', 'delicioso', 'excelente', 'recomendo', 'rápido', 'bom', 'melhor']
                        
                        text_lower = review_text.lower()
                        neg_count = sum(1 for palavra in palavras_negativas if palavra in text_lower)
                        pos_count = sum(1 for palavra in palavras_positivas if palavra in text_lower)
                        
                        if neg_count > pos_count + 2:
                            st.warning(f"""
                            ⚠️ **Alerta de Inconsistência**
                            
                            Detectadas **{neg_count} palavras negativas** vs **{pos_count} positivas**.
                            
                            Possível erro de classificação!
                            """)
                    
                    with col2:
                        st.markdown("#### Interpretação")
                        
                        if confidence < CONFIDENCE_THRESHOLD:
                            st.error(f"""
                            ⚠️ **CLASSIFICAÇÃO INCERTA**
                            
                            Confiança muito baixa ({confidence*100:.1f}%).
                            
                            **Ações recomendadas:**
                            1. Revisar manualmente
                            2. Comparar com GPT (aba Comparação)
                            3. Usar para retreinamento
                            4. Pedir segunda opinião de especialista
                            """)
                        elif sentiment == 'positive':
                            st.success("""
                            ✅ **Sentimento Positivo**
                            
                            O modelo identificou que este review expressa satisfação com o restaurante.
                            Aspectos positivos foram detectados no texto.
                            """)
                        elif sentiment == 'negative':
                            st.error("""
                            ❌ **Sentimento Negativo**
                            
                            O modelo identificou que este review expressa insatisfação com o restaurante.
                            Aspectos negativos foram detectados no texto.
                            """)
                        else:
                            st.warning("""
                            ⚠️ **Sentimento Neutro**
                            
                            O modelo identificou que este review é neutro ou misto.
                            Não há aspectos fortemente positivos ou negativos.
                            """)
                    
                    # Sugestões de melhoria
                    if confidence < CONFIDENCE_THRESHOLD:
                        st.markdown("---")
                        st.markdown("### 🔄 Sugestões de Melhoria")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.info("""
                            **📊 Comparar com GPT**
                            
                            Vá para a página **Comparação** 
                            para ver o que o GPT-4o-mini 
                            classifica.
                            """)
                        
                        with col2:
                            st.info("""
                            **🔄 Adicionar ao Dataset**
                            
                            Use este exemplo no 
                            **Retreinamento** para 
                            melhorar o modelo.
                            """)
                        
                        with col3:
                            st.info("""
                            **🤖 LLM Judge**
                            
                            Vá para **LLM Judge** para 
                            obter avaliação detalhada 
                            do GPT.
                            """)
                    
                    # Informações técnicas
                    with st.expander("🔧 Informações Técnicas"):
                        st.json(result)
                
                else:
                    st.error(f"❌ Erro na API: {response.status_code}")
                    st.code(response.text)
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout: A API demorou muito para responder")
                st.info("Verifique se o serviço está rodando: `docker ps | grep sentibr-api`")
                
            except requests.exceptions.ConnectionError:
                st.error("🔌 Erro de Conexão: Não foi possível conectar à API")
                st.info("Verifique se a API está rodando: `docker-compose ps api`")
                
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")

# Exemplos
st.markdown("---")
st.subheader("💡 Exemplos de Reviews")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 😊 Positivo")
    if st.button("Usar exemplo positivo", use_container_width=True):
        st.session_state.example = "A comida estava absolutamente deliciosa! Melhor hambúrguer que já comi. Entrega super rápida e tudo chegou quentinho. O atendimento foi excelente, muito educados. Com certeza vou pedir novamente!"

with col2:
    st.markdown("#### 😐 Neutro")
    if st.button("Usar exemplo neutro", use_container_width=True):
        st.session_state.example = "Pedi uma pizza. Chegou no prazo. Sabor normal, nada excepcional. Preço na média do mercado. Atendimento padrão."

with col3:
    st.markdown("#### 😞 Negativo")
    if st.button("Usar exemplo negativo", use_container_width=True):
        st.session_state.example = "Péssima experiência! A comida chegou fria e com mais de 2 horas de atraso. O hambúrguer estava completamente desmontado e a batata murcha. Atendimento horrível, não recomendo para ninguém!"

# Mostrar exemplo se selecionado
if 'example' in st.session_state:
    st.info(f"📝 Exemplo selecionado: {st.session_state.example}")

# Dicas
with st.expander("💡 Sobre Confiança do Modelo"):
    st.markdown(f"""
    ### Como Interpretar a Confiança
    
    **🟢 Alta Confiança (85-100%)**
    - Modelo muito seguro da classificação
    - Pode confiar no resultado
    - Padrão claro no texto
    
    **🟡 Média Confiança ({CONFIDENCE_THRESHOLD*100:.0f}-85%)**
    - Modelo moderadamente seguro
    - Revisar se crítico
    - Geralmente correto
    
    **🔴 Baixa Confiança (< {CONFIDENCE_THRESHOLD*100:.0f}%)**
    - ⚠️ **NÃO confiar!**
    - Modelo muito incerto
    - **Sempre revisar manualmente**
    - Usar GPT para comparação
    - Adicionar ao dataset de retreinamento
    
    ### Por Que Baixa Confiança?
    
    1. **Review ambíguo**: Mistura positivo e negativo
    2. **Sarcasmo/ironia**: Modelo não detecta
    3. **Contexto novo**: Modelo nunca viu similar
    4. **Palavras enganosas**: Contexto confuso
    5. **Review longo/complexo**: Difícil de processar
    
    ### O Que Fazer?
    
    - ⚠️ **< 50% confiança**: Sempre revisar
    - 🤖 **Comparar com GPT**: Página Comparação
    - 🔄 **Retreinar**: Adicionar ao dataset
    - 📊 **LLM Judge**: Obter avaliação detalhada
    """)
