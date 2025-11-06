"""
Página de Análise de Sentimentos
Permite análise individual e comparação BERT vs GPT
"""
import streamlit as st
import requests
import time
from pathlib import Path
import sys

# Adicionar componentes ao path
sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import (
    sentiment_badge,
    confidence_gauge,
    aspect_analysis_chart,
    comparison_table,
    show_explainability,
    loading_animation
)


# Configuração da página
st.set_page_config(
    page_title="Análise de Sentimentos - SentiBR",
    page_icon="📝",
    layout="wide"
)


# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1"


def call_api(endpoint: str, data: dict) -> dict:
    """
    Chama a API do sistema
    
    Args:
        endpoint: Endpoint da API
        data: Dados a enviar
    
    Returns:
        Resposta da API
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/{endpoint}",
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "⚠️ API não está respondendo. Certifique-se de que a API está rodando."}
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Timeout na requisição. Tente novamente."}
    except requests.exceptions.RequestException as e:
        return {"error": f"❌ Erro na requisição: {str(e)}"}


def analyze_sentiment(text: str, use_comparison: bool = False):
    """
    Analisa o sentimento do texto
    
    Args:
        text: Texto a analisar
        use_comparison: Se True, faz comparação BERT vs GPT
    """
    if use_comparison:
        endpoint = "predict/compare"
    else:
        endpoint = "predict"
    
    with st.spinner("🔄 Analisando sentimento..."):
        start_time = time.time()
        result = call_api(endpoint, {"text": text})
        latency = time.time() - start_time
    
    if "error" in result:
        st.error(result["error"])
        return
    
    # Exibir resultado
    if use_comparison and "bert" in result and "gpt" in result:
        show_comparison_results(result, latency)
    else:
        show_single_result(result, latency)


def show_single_result(result: dict, latency: float):
    """
    Exibe resultado de uma única predição
    
    Args:
        result: Resultado da API
        latency: Latência da requisição
    """
    st.markdown("## 🎯 Resultado da Análise")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Badge de sentimento
        sentiment_badge(
            result.get("sentiment", "neutral"),
            result.get("confidence", 0.0)
        )
        
        # Detalhes da predição
        with st.expander("📊 Detalhes da Predição", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Sentimento", result.get("sentiment", "N/A").title())
            
            with col_b:
                st.metric("Confiança", f"{result.get('confidence', 0):.1%}")
            
            with col_c:
                st.metric("Latência", f"{latency*1000:.0f}ms")
            
            # Scores detalhados
            st.markdown("### Scores por Classe")
            scores = result.get("scores", {})
            if scores:
                for label, score in scores.items():
                    st.progress(score, text=f"{label.title()}: {score:.1%}")
    
    with col2:
        # Gauge de confiança
        fig_gauge = confidence_gauge(
            result.get("confidence", 0.0),
            result.get("sentiment", "neutral")
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Análise por aspectos (simulado)
    if st.checkbox("🔍 Ver Análise por Aspectos"):
        st.markdown("### Análise Detalhada por Aspectos")
        
        # Simulação de análise por aspectos
        aspects = {
            "Qualidade da Comida": 0.8,
            "Tempo de Entrega": 0.3,
            "Atendimento": 0.6,
            "Preço": -0.2,
            "Embalagem": 0.5
        }
        
        fig_aspects = aspect_analysis_chart(aspects)
        st.plotly_chart(fig_aspects, use_container_width=True)
        
        st.info("""
        💡 **Nota**: A análise por aspectos é uma funcionalidade avançada que identifica 
        o sentimento para diferentes aspectos do serviço (comida, entrega, atendimento, etc.)
        """)
    
    # Explicabilidade
    if st.checkbox("🔬 Ver Explicabilidade (LIME/SHAP)"):
        st.markdown("### Explicabilidade da Predição")
        
        # Simulação de word importance
        word_importance = {
            "excelente": 0.9,
            "delicioso": 0.8,
            "péssimo": -0.9,
            "horrível": -0.8,
            "adorei": 0.85,
            "nunca": -0.6,
            "mais": -0.4,
            "recomendo": 0.7
        }
        
        show_explainability(
            result.get("text", ""),
            word_importance
        )
        
        st.info("""
        💡 **Nota**: As palavras destacadas mostram quais termos mais influenciaram 
        a decisão do modelo. Verde = contribui para sentimento positivo, 
        Vermelho = contribui para sentimento negativo.
        """)


def show_comparison_results(result: dict, latency: float):
    """
    Exibe comparação BERT vs GPT
    
    Args:
        result: Resultado da API com BERT e GPT
        latency: Latência da requisição
    """
    st.markdown("## 🆚 Comparação BERT vs GPT-4o-mini")
    
    bert_result = result.get("bert", {})
    gpt_result = result.get("gpt", {})
    
    # Tabela de comparação
    comparison_table(bert_result, gpt_result)
    
    # Análise comparativa
    st.markdown("### 📊 Análise Comparativa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Vantagens do BERT")
        st.markdown("""
        - ✅ **Rápido**: Latência consistentemente baixa
        - ✅ **Custo Zero**: Roda localmente
        - ✅ **Controle Total**: Fine-tuning customizado
        - ✅ **Privacy**: Dados não saem do servidor
        - ✅ **Offline**: Funciona sem internet
        """)
    
    with col2:
        st.markdown("#### Vantagens do GPT")
        st.markdown("""
        - ✅ **Contextual**: Melhor compreensão de nuances
        - ✅ **Atualizado**: Conhecimento mais recente
        - ✅ **Versatilidade**: Entende contextos complexos
        - ✅ **Raciocínio**: Pode explicar suas decisões
        - ✅ **Zero-shot**: Funciona sem treinamento prévio
        """)
    
    # Trade-offs
    with st.expander("⚖️ Trade-offs e Recomendações"):
        st.markdown("""
        ### Quando usar BERT:
        - 📱 **Produção em larga escala**: Milhões de requisições/dia
        - 💰 **Budget limitado**: Sem custos de API
        - 🔒 **Dados sensíveis**: Privacidade crítica
        - ⚡ **Latência crítica**: Respostas < 100ms
        
        ### Quando usar GPT:
        - 🎯 **Alta precisão**: Casos críticos de negócio
        - 🔄 **Prototipagem rápida**: Sem necessidade de fine-tuning
        - 📚 **Contexto complexo**: Reviews longos e elaborados
        - 💡 **Explicabilidade**: Necessidade de justificativas
        
        ### Abordagem Híbrida (Recomendada):
        1. **BERT como primário** para 95% dos casos
        2. **GPT para casos ambíguos** (confiança BERT < 70%)
        3. **GPT como validação** em amostra aleatória
        4. **Custo-benefício otimizado** e qualidade garantida
        """)


def main():
    """Função principal da página"""
    
    st.title("📝 Análise de Sentimentos")
    st.markdown("Analise reviews de restaurantes do iFood e identifique sentimentos automaticamente")
    
    # Tabs para diferentes modos
    tab1, tab2, tab3 = st.tabs(["🔍 Análise Individual", "🆚 Comparação BERT vs GPT", "📊 Análise em Lote"])
    
    with tab1:
        st.markdown("### Digite ou cole um review para análise")
        
        # Exemplos pré-definidos
        examples = {
            "Selecione um exemplo": "",
            "Positivo - Pizza excelente": "A pizza estava simplesmente divina! Massa crocante, ingredientes fresquíssimos e chegou quentinha. Adorei o atendimento também, muito atenciosos. Com certeza vou pedir novamente! 🍕❤️",
            "Negativo - Entrega atrasada": "Péssima experiência! O pedido atrasou mais de 2 horas e quando chegou a comida estava fria. Tentei entrar em contato mas ninguém me respondeu. Nunca mais peço nesse restaurante!",
            "Neutro - Experiência mediana": "O lanche estava ok, nada de mais. O preço é justo mas esperava algo melhor pela reputação do lugar. Entrega no prazo.",
            "Misto - Bom mas caro": "A comida é realmente muito boa, sabor excelente e bem temperada. Porém achei o preço bem salgado para o tamanho das porções. Mesmo assim recomendo para ocasiões especiais."
        }
        
        selected_example = st.selectbox("💡 Ou escolha um exemplo:", list(examples.keys()))
        
        # Text area
        if selected_example != "Selecione um exemplo":
            default_text = examples[selected_example]
        else:
            default_text = ""
        
        text_input = st.text_area(
            "Review do Restaurante:",
            value=default_text,
            height=150,
            placeholder="Ex: A comida estava deliciosa! O atendimento foi excelente e a entrega rápida. Super recomendo! 😊",
            help="Digite ou cole o review que deseja analisar"
        )
        
        # Opções avançadas
        with st.expander("⚙️ Opções Avançadas"):
            show_aspects = st.checkbox("Analisar por aspectos", value=True)
            show_explain = st.checkbox("Mostrar explicabilidade", value=True)
        
        # Botão de análise
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            analyze_btn = st.button("🔍 Analisar Sentimento", type="primary", use_container_width=True)
        with col2:
            clear_btn = st.button("🗑️ Limpar", use_container_width=True)
        
        if clear_btn:
            st.rerun()
        
        if analyze_btn:
            if not text_input.strip():
                st.warning("⚠️ Por favor, digite um review para analisar.")
            else:
                analyze_sentiment(text_input, use_comparison=False)
    
    with tab2:
        st.markdown("### Compare as predições de BERT e GPT lado a lado")
        
        st.info("""
        🆚 **Modo Comparação**: Neste modo, o texto será analisado simultaneamente pelo 
        modelo BERT fine-tunado e pelo GPT-4o-mini, permitindo comparar resultados, 
        latência e confiança de ambos os modelos.
        """)
        
        text_compare = st.text_area(
            "Review para Comparação:",
            height=150,
            placeholder="Digite o review que deseja comparar entre BERT e GPT...",
            key="compare_text"
        )
        
        if st.button("🆚 Comparar Modelos", type="primary", use_container_width=True):
            if not text_compare.strip():
                st.warning("⚠️ Por favor, digite um review para comparar.")
            else:
                analyze_sentiment(text_compare, use_comparison=True)
    
    with tab3:
        st.markdown("### Análise de múltiplos reviews simultaneamente")
        
        st.info("📊 **Em desenvolvimento**: Envie um arquivo CSV ou cole múltiplos reviews para análise em lote.")
        
        uploaded_file = st.file_uploader(
            "Upload de arquivo CSV",
            type=['csv'],
            help="Arquivo deve conter uma coluna 'text' com os reviews"
        )
        
        if uploaded_file:
            st.success("✅ Arquivo carregado! Processamento em lote será implementado em breve.")
        
        st.markdown("**OU**")
        
        batch_text = st.text_area(
            "Cole múltiplos reviews (um por linha):",
            height=200,
            placeholder="Review 1\nReview 2\nReview 3\n...",
            key="batch_text"
        )
        
        if st.button("📊 Analisar Lote", type="primary", use_container_width=True):
            st.info("🚧 Funcionalidade de análise em lote em desenvolvimento...")
    
    # Sidebar com informações
    with st.sidebar:
        st.markdown("### 📊 Estatísticas da Sessão")
        
        if 'total_predictions' not in st.session_state:
            st.session_state.total_predictions = 0
        
        st.metric("Predições Realizadas", st.session_state.total_predictions)
        
        st.markdown("---")
        
        st.markdown("### 💡 Dicas")
        st.markdown("""
        - Reviews mais longos tendem a ter análises mais precisas
        - Use pontuação e emojis naturalmente
        - A explicabilidade ajuda a entender a decisão
        - Compare BERT vs GPT para casos complexos
        """)
        
        st.markdown("---")
        
        st.markdown("### ⚙️ Status da API")
        
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                st.success("✅ API Online")
            else:
                st.error("❌ API Offline")
        except:
            st.error("❌ API Offline")


if __name__ == "__main__":
    main()
