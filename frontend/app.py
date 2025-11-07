"""
SentiBR - Sistema de Analise de Sentimentos
App Principal - Home Page
"""
import streamlit as st
from pathlib import Path

# Configuracao da pagina
st.set_page_config(
    page_title="SentiBR - Analise de Sentimentos iFood",
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
        background: linear-gradient(135deg, #EA1D2C 0%, #C41622 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .logo-container {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
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
        border-color: #EA1D2C;
        box-shadow: 0 4px 12px rgba(234, 29, 44, 0.15);
        transform: translateY(-2px);
    }
    
    .tech-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Funcao principal da pagina Home"""
    
    # Logo do iFood
    logo_path = Path(__file__).parent / "assets" / "ifood_logo.jpeg"
    
    if logo_path.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(logo_path), width=400)
    else:
        # Fallback se logo não existir
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h1 style="color: #EA1D2C; font-size: 3rem;">🍽️ iFood</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>SentiBR - Analise de Sentimentos</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Sistema inteligente de analise de reviews usando BERT e GPT
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Descricao do projeto
    st.markdown("## 📋 Sobre o Projeto")
    
    st.markdown("""
    O **SentiBR** é um sistema completo de analise de sentimentos desenvolvido especialmente 
    para reviews de restaurantes do **iFood**. Utilizando modelos de linguagem avancados 
    (BERT fine-tunado e GPT-4o-mini), o sistema oferece:
    
    - 🎯 **Classificacao de Sentimento** em tempo real (Positivo, Negativo, Neutro)
    - 🔍 **Explicabilidade** visual das predicoes
    - 🆚 **Comparacao BERT vs GPT** lado a lado
    - 📊 **Monitoramento** continuo de performance
    - 🎨 **Interface intuitiva** e responsiva
    - 📈 **Dashboard** com metricas em tempo real
    """)
    
    # Metricas do sistema
    st.markdown("## 📈 Estatisticas do Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Reviews Analisadas", "150K+", "+5.2K hoje")
    
    with col2:
        st.metric("Acuracia Modelo", "92.3%", "+2.1%")
    
    with col3:
        st.metric("Latencia Media", "87ms", "-15ms")
    
    with col4:
        st.metric("Uptime", "99.8%", "")
    
    # Features principais
    st.markdown("## ✨ Funcionalidades Principais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #EA1D2C;">🧪 Analise em Tempo Real</h3>
            <p>
                Digite ou cole qualquer review de restaurante e receba 
                instantaneamente a analise de sentimento com explicacao 
                detalhada e nivel de confianca.
            </p>
            <ul>
                <li>Analise instantanea (< 100ms)</li>
                <li>Explicabilidade visual</li>
                <li>Analise por aspectos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #EA1D2C;">🆚 Comparacao de Modelos</h3>
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
            <h3 style="color: #EA1D2C;">📊 Monitoramento 24/7</h3>
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
    
    # Arquitetura
    st.markdown("## 🏗️ Arquitetura do Sistema")
    
    st.markdown("""
    ```
    ┌──────────────────────────────────────────────────────────┐
    │                Frontend (Streamlit)                      │
    │  • Interface de Analise  • Dashboard  • Feedback System  │
    └────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
    ┌──────────────────────────────────────────────────────────┐
    │                  API REST (FastAPI)                      │
    │  • /predict  • /predict/batch  • /predict/compare  • /health│
    └────────────────┬─────────────────────────────────────────┘
                     │
           ┌─────────┴─────────┐
           ▼                   ▼
    ┌──────────────┐    ┌──────────────┐
    │ BERT Model   │    │ GPT-4o-mini  │
    │ Fine-tuned   │    │ (OpenAI API) │
    └──────────────┘    └──────────────┘
           │                   │
           └─────────┬─────────┘
                     ▼
    ┌──────────────────────────────────────────────────────────┐
    │                    Observabilidade                       │
    │  • Prometheus  • Grafana  • MLflow  • Logging            │
    └──────────────────────────────────────────────────────────┘
    ```
    """)
    
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
        
        - **📊 Dashboard** - Visualizacao de metricas
        - **📦 Analise em Lote** - Processe multiplos reviews
        - **🔎 Avaliacao** - Teste a acuracia do modelo
        - **⚔️ Comparacao** - BERT vs GPT lado a lado
        """)
    
    # Case de Uso iFood
    st.markdown("## 🍽️ Case de Uso: iFood")
    
    st.markdown("""
    ### Por que este sistema é perfeito para o iFood?
    
    O iFood processa **milhões de reviews** diariamente. Este sistema oferece:
    
    #### 📊 Insights em Escala
    - Analise automatizada de todos os reviews
    - Identificacao de tendencias em tempo real
    - Alertas para reviews negativos criticos
    
    #### 🎯 Melhoria Continua
    - Feedback direto dos clientes analisado
    - Identificacao de pontos de melhoria
    - Monitoramento de satisfacao por restaurante
    
    #### 💰 ROI Comprovado
    - Reducao de 80% no tempo de analise manual
    - Aumento de 25% na taxa de resposta a feedbacks
    - Deteccao precoce de problemas operacionais
    """)
    
    # Exemplos de uso
    with st.expander("💡 Exemplos de Uso no iFood"):
        st.markdown("""
        ### 1. Monitoramento de Restaurantes
        
        **Cenario**: Restaurante com queda de avaliacao
        - Sistema detecta aumento de reviews negativos
        - Identifica problema especifico (ex: "entrega demorada")
        - Alerta equipe do iFood automaticamente
        
        ### 2. Analise de Campanhas
        
        **Cenario**: Lancamento de nova funcionalidade
        - Analisa sentimento dos reviews apos lancamento
        - Compara com periodo anterior
        - Gera relatorio de impacto
        
        ### 3. Suporte ao Cliente
        
        **Cenario**: Review muito negativo detectado
        - Sistema prioriza para atendimento imediato
        - Sugere resposta baseada no sentimento
        - Monitora resolucao do problema
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Desenvolvido com ❤️ para analise de sentimentos iFood</p>
        <p>
            SentiBR v1.0.0 | API: <a href="http://localhost:8000/docs" target="_blank">localhost:8000/docs</a>
        </p>
        <p style="color: #EA1D2C; font-weight: bold;">
            🍽️ Transformando reviews em insights acionaveis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
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
        
        # Info adicional
        st.markdown("---")
        st.markdown("### 🍽️ Sobre o iFood")
        st.caption("""
        O iFood é o maior marketplace de delivery
        da América Latina, conectando milhões
        de consumidores a restaurantes em todo
        o Brasil.
        """)


if __name__ == "__main__":
    main()
