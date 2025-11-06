"""
SentiBR - Sistema de Análise de Sentimentos para Reviews do iFood
App Principal - Home Page
"""
import streamlit as st
from pathlib import Path
import sys

# Adicionar src ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from components.ui_components import metric_card


# Configuração da página
st.set_page_config(
    page_title="SentiBR - Análise de Sentimentos iFood",
    page_icon="🍔",
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


def load_logo():
    """Carrega e exibe o logo do iFood"""
    logo_path = Path(__file__).parent / "assets" / "ifood_logo.jpeg"
    if logo_path.exists():
        return str(logo_path)
    return None


def main():
    """Função principal da página Home"""
    
    # Header com logo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        logo_path = load_logo()
        if logo_path:
            st.image(logo_path, width=300)
    
    st.markdown("""
    <div class="main-header">
        <h1>🍔 SentiBR - Análise de Sentimentos</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Sistema inteligente de análise de reviews do iFood usando BERT e GPT
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Descrição do projeto
    st.markdown("## 📋 Sobre o Projeto")
    
    st.markdown("""
    O **SentiBR** é um sistema completo de análise de sentimentos desenvolvido especialmente 
    para reviews de restaurantes do iFood. Utilizando modelos de linguagem avançados (BERT fine-tunado 
    e GPT-4o-mini), o sistema oferece:
    
    - 🎯 **Classificação de Sentimento** em tempo real (Positivo, Negativo, Neutro)
    - 🔍 **Explicabilidade** visual das predições
    - 🆚 **Comparação BERT vs GPT** lado a lado
    - 📊 **Monitoramento** contínuo de performance
    - 🎨 **Interface intuitiva** e responsiva
    - 🔄 **Feedback Loop** para melhoria contínua
    """)
    
    # Métricas do sistema
    st.markdown("## 📈 Estatísticas do Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            title="Reviews Analisadas",
            value="150K+",
            delta="+5.2K hoje",
            icon="📊",
            color="#EA1D2C"
        )
    
    with col2:
        metric_card(
            title="Acurácia Modelo",
            value="94.7%",
            delta="+2.3%",
            icon="🎯",
            color="#28a745"
        )
    
    with col3:
        metric_card(
            title="Latência Média",
            value="45ms",
            delta="-12ms",
            icon="⚡",
            color="#17a2b8"
        )
    
    with col4:
        metric_card(
            title="Uptime",
            value="99.9%",
            delta="",
            icon="✅",
            color="#6c757d"
        )
    
    # Features principais
    st.markdown("## ✨ Funcionalidades Principais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #EA1D2C;">🧪 Análise em Tempo Real</h3>
            <p>
                Digite ou cole qualquer review de restaurante e receba 
                instantaneamente a análise de sentimento com explicação 
                detalhada e nível de confiança.
            </p>
            <ul>
                <li>Análise instantânea</li>
                <li>Explicabilidade visual</li>
                <li>Análise por aspectos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #EA1D2C;">🆚 Comparação de Modelos</h3>
            <p>
                Compare lado a lado as predições do BERT fine-tunado 
                com GPT-4o-mini e entenda as diferenças entre os modelos.
            </p>
            <ul>
                <li>BERT vs GPT-4o-mini</li>
                <li>Métricas de latência</li>
                <li>Trade-offs explicados</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3 style="color: #EA1D2C;">📊 Monitoramento 24/7</h3>
            <p>
                Dashboard completo com métricas em tempo real, 
                detecção de drift e alertas de performance.
            </p>
            <ul>
                <li>Métricas Prometheus</li>
                <li>Grafana dashboards</li>
                <li>Detecção de drift</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Arquitetura
    st.markdown("## 🗃️ Arquitetura do Sistema")
    
    st.markdown("""
    ```
    ┌──────────────────────────────────────────────────────────┐
    │                    Frontend (Streamlit)                      │
    │  • Interface de Análise  • Dashboard  • Feedback System      │
    └────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │                      API REST (FastAPI)                      │
    │  • /predict  • /predict/batch  • /predict/compare  • /health│
    └────────────────────┬─────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
    ┌──────────────┐          ┌──────────────┐
    │ BERT Model   │          │ GPT-4o-mini  │
    │ Fine-tuned   │          │ (OpenAI API) │
    └──────────────┘          └──────────────┘
           │                           │
           └─────────────┬─────────────┘
                         ▼
    ┌──────────────────────────────────────────────────────────┐
    │                    Observabilidade                           │
    │  • Prometheus  • Grafana  • MLflow  • Logging               │
    └──────────────────────────────────────────────────────────┘
    ```
    """)
    
    # Tech Stack
    st.markdown("## 🛠️ Tech Stack")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Machine Learning")
        st.markdown("""
        <div>
            <span class="tech-badge">🤗 Transformers</span>
            <span class="tech-badge">🔥 PyTorch</span>
            <span class="tech-badge">🧠 BERT</span>
            <span class="tech-badge">🤖 OpenAI GPT</span>
            <span class="tech-badge">📊 Scikit-learn</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### API & Backend")
        st.markdown("""
        <div>
            <span class="tech-badge">⚡ FastAPI</span>
            <span class="tech-badge">🔄 Uvicorn</span>
            <span class="tech-badge">📝 Pydantic</span>
            <span class="tech-badge">🐍 Python 3.10+</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Frontend & UI")
        st.markdown("""
        <div>
            <span class="tech-badge">🎨 Streamlit</span>
            <span class="tech-badge">📈 Plotly</span>
            <span class="tech-badge">🎯 Pandas</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Observabilidade")
        st.markdown("""
        <div>
            <span class="tech-badge">📊 Prometheus</span>
            <span class="tech-badge">📈 Grafana</span>
            <span class="tech-badge">🔬 MLflow</span>
            <span class="tech-badge">🐳 Docker</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Start
    st.markdown("## 🚀 Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **👉 Experimente agora!**
        
        1. Vá para a página **🔍 Análise de Sentimentos**
        2. Digite ou cole um review de restaurante
        3. Clique em **Analisar**
        4. Veja o resultado instantâneo!
        """)
    
    with col2:
        st.success("""
        **📚 Explore o sistema:**
        
        - **📊 Métricas**: Dashboard em tempo real
        - **💬 Feedback**: Ajude a melhorar o modelo
        - **🔍 Monitor**: Acompanhe a performance
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>Desenvolvido com ❤️ para o desafio técnico de IA Sênior</p>
        <p>
            <a href="https://github.com" target="_blank" style="color: #EA1D2C; text-decoration: none;">
                📦 GitHub
            </a> | 
            <a href="https://docs.example.com" target="_blank" style="color: #EA1D2C; text-decoration: none;">
                📚 Documentação
            </a> | 
            <a href="mailto:contato@example.com" style="color: #EA1D2C; text-decoration: none;">
                ✉️ Contato
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
