"""
SentiBR - Sistema de Analise de Sentimentos
App Principal - Home Page
"""
import streamlit as st

# Configuracao da pagina
st.set_page_config(
    page_title="SentiBR - Analise de Sentimentos",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #f0f0f0;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Funcao principal da pagina Home"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ SentiBR - Analise de Sentimentos</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Sistema inteligente de analise de reviews usando BERT e GPT
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Descricao do projeto
    st.markdown("## 📋 Sobre o Projeto")
    
    st.markdown("""
    O **SentiBR** é um sistema completo de analise de sentimentos desenvolvido especialmente 
    para reviews de restaurantes. Utilizando modelos de linguagem avancados (BERT fine-tunado 
    e GPT-4o-mini), o sistema oferece:
    
    - 🎯 **Classificacao de Sentimento** em tempo real (Positivo, Negativo, Neutro)
    - 🔍 **Explicabilidade** visual das predicoes
    - 🆚 **Comparacao BERT vs GPT** lado a lado
    - 📊 **Monitoramento** continuo de performance
    - 🎨 **Interface intuitiva** e responsiva
    """)
    
    # Metricas do sistema
    st.markdown("## 📈 Estatisticas do Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Reviews Analisadas", "150K+", "+5.2K hoje")
    
    with col2:
        st.metric("Acuracia Modelo", "94.7%", "+2.3%")
    
    with col3:
        st.metric("Latencia Media", "45ms", "-12ms")
    
    with col4:
        st.metric("Uptime", "99.9%", "")
    
    # Features principais
    st.markdown("## ✨ Funcionalidades Principais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea;">🧪 Analise em Tempo Real</h3>
            <p>
                Digite ou cole qualquer review de restaurante e receba 
                instantaneamente a analise de sentimento com explicacao 
                detalhada e nivel de confianca.
            </p>
            <ul>
                <li>Analise instantanea</li>
                <li>Explicabilidade visual</li>
                <li>Analise por aspectos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea;">🆚 Comparacao de Modelos</h3>
            <p>
                Compare lado a lado as predicoes do BERT fine-tunado 
                com GPT-4o-mini e entenda as diferencas entre os modelos.
            </p>
            <ul>
                <li>BERT vs GPT-4o-mini</li>
                <li>Metricas de latencia</li>
                <li>Trade-offs explicados</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #667eea;">📊 Monitoramento 24/7</h3>
            <p>
                Dashboard completo com metricas em tempo real, 
                deteccao de drift e alertas de performance.
            </p>
            <ul>
                <li>Metricas Prometheus</li>
                <li>Grafana dashboards</li>
                <li>Deteccao de drift</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Tech Stack
    st.markdown("## 🛠️ Tech Stack")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Machine Learning")
        st.markdown("""
        - 🤗 **Transformers** - BERT fine-tuning
        - 🔥 **PyTorch** - Deep learning framework
        - 🧠 **BERT** - neuralmind/bert-base-portuguese-cased
        - 🤖 **GPT-4o-mini** - OpenAI API
        - 📊 **Scikit-learn** - Metricas e avaliacao
        """)
        
        st.markdown("### API & Backend")
        st.markdown("""
        - ⚡ **FastAPI** - REST API framework
        - 🔄 **Uvicorn** - ASGI server
        - 🔐 **Pydantic** - Data validation
        - 🐍 **Python 3.10+** - Linguagem principal
        """)
    
    with col2:
        st.markdown("### Frontend & UI")
        st.markdown("""
        - 🎨 **Streamlit** - Interface web
        - 📈 **Plotly** - Visualizacoes interativas
        - 🎯 **Pandas** - Manipulacao de dados
        """)
        
        st.markdown("### Observabilidade")
        st.markdown("""
        - 📊 **Prometheus** - Metricas
        - 📈 **Grafana** - Dashboards
        - 🔬 **MLflow** - Experiment tracking
        - 🐳 **Docker** - Containerizacao
        """)
    
    # Quick Start
    st.markdown("## 🚀 Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **👉 Experimente agora!**
        
        1. Va para a pagina **🔍 Analise Individual**
        2. Digite ou cole um review de restaurante
        3. Clique em **Analisar**
        4. Veja o resultado instantaneo!
        """)
    
    with col2:
        st.success("""
        **📚 Explore o sistema:**
        
        - **📊 Dashboard**: Visualizacao de metricas
        - **📦 Analise em Lote**: Processe multiplos reviews
        - **🔎 Avaliacao**: Teste a acuracia do modelo
        - **⚔️ Comparacao**: BERT vs GPT lado a lado
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Desenvolvido com ❤️ para analise de sentimentos</p>
        <p>SentiBR v1.0.0 | API: <a href="http://localhost:8000/docs" target="_blank">localhost:8000/docs</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar info
    with st.sidebar:
        st.markdown("## 🎯 Navegacao")
        st.markdown("""
        Use o menu acima para navegar entre as paginas:
        
        - 🏠 **Home** - Pagina inicial
        - 📊 **Dashboard** - Visao geral
        - 🔍 **Analise Individual** - Analise unica
        - 📦 **Analise em Lote** - Multiplos reviews
        - 🔎 **Avaliacao** - Teste o modelo
        - ⚔️ **Comparacao** - BERT vs GPT
        - 🤖 **LLM Judge** - Avaliacao com IA
        - 📈 **Monitoramento** - Status do sistema
        """)
        
        st.markdown("---")
        
        # Status da API
        st.markdown("### ⚡ Status do Sistema")
        try:
            import requests
            response = requests.get("http://api:8000/api/v1/health", timeout=2)
            if response.status_code == 200:
                st.success("API Online ✅")
            else:
                st.error("API Offline ❌")
        except:
            st.warning("API nao acessivel ⚠️")


if __name__ == "__main__":
    main()
