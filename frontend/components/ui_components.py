"""
Componentes de UI reutilizáveis - VERSÃO CORRIGIDA
Todos os st.markdown() com HTML agora têm unsafe_allow_html=True
"""
import streamlit as st
from typing import Optional


def metric_card(
    title: str,
    value: str,
    delta: str = "",
    icon: str = "📊",
    color: str = "#EA1D2C"
):
    """
    Renderiza um card de métrica customizado - CORRIGIDO
    
    Args:
        title: Título da métrica
        value: Valor principal
        delta: Variação (opcional)
        icon: Emoji do ícone
        color: Cor do card
    """
    # Determinar cor de fundo baseada na cor principal
    bg_colors = {
        "#EA1D2C": "linear-gradient(135deg, #FFE5E5 0%, #FFF5F5 100%)",
        "#28a745": "linear-gradient(135deg, #E5F5E5 0%, #F5FFF5 100%)",
        "#17a2b8": "linear-gradient(135deg, #E5F5FF 0%, #F5FAFF 100%)",
        "#6c757d": "linear-gradient(135deg, #F0F0F0 0%, #F8F8F8 100%)",
        "#ffc107": "linear-gradient(135deg, #FFF5E5 0%, #FFFEF5 100%)",
    }
    
    bg_gradient = bg_colors.get(color, bg_colors["#EA1D2C"])
    
    st.markdown(
        f"""
        <div style="
            background: {bg_gradient};
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid {color};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            height: 100%;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 2rem; margin-right: 0.5rem;">{icon}</span>
                <span style="
                    font-size: 0.75rem;
                    color: #666;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">{title}</span>
            </div>
            <div style="
                font-size: 2rem;
                font-weight: bold;
                color: {color};
                margin-top: 0.5rem;
            ">{value}</div>
            {f'<div style="font-size: 0.75rem; color: #999; margin-top: 0.25rem;">»{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True  # ← CORREÇÃO APLICADA!
    )


def sentiment_badge(sentiment: str, confidence: float):
    """
    Renderiza um badge de sentimento - CORRIGIDO
    
    Args:
        sentiment: positive, negative, ou neutral
        confidence: Confiança da predição (0-1)
    """
    colors = {
        "positive": "#28a745",
        "negative": "#dc3545",
        "neutral": "#6c757d"
    }
    
    labels = {
        "positive": "😊 Positivo",
        "negative": "😞 Negativo",
        "neutral": "😐 Neutro"
    }
    
    color = colors.get(sentiment, "#6c757d")
    label = labels.get(sentiment, sentiment)
    
    st.markdown(
        f"""
        <div style="
            display: inline-block;
            background-color: {color};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1rem;
        ">
            {label}
            <span style="
                background-color: rgba(255,255,255,0.2);
                padding: 0.25rem 0.5rem;
                border-radius: 10px;
                margin-left: 0.5rem;
                font-size: 0.9rem;
            ">{confidence:.1%}</span>
        </div>
        """,
        unsafe_allow_html=True  # ← CORREÇÃO APLICADA!
    )


def confidence_bar(confidence: float, label: str = "Confiança"):
    """
    Renderiza uma barra de confiança - CORRIGIDO
    
    Args:
        confidence: Valor de confiança (0-1)
        label: Label da barra
    """
    # Determinar cor baseada na confiança
    if confidence >= 0.8:
        color = "#28a745"
        status = "Alta"
    elif confidence >= 0.6:
        color = "#ffc107"
        status = "Média"
    else:
        color = "#dc3545"
        status = "Baixa"
    
    percentage = confidence * 100
    
    st.markdown(
        f"""
        <div style="margin: 1rem 0;">
            <div style="
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
            ">
                <span style="font-weight: 600; color: #333;">{label}</span>
                <span style="color: {color}; font-weight: bold;">{percentage:.1f}% ({status})</span>
            </div>
            <div style="
                background-color: #f0f0f0;
                border-radius: 10px;
                height: 20px;
                overflow: hidden;
            ">
                <div style="
                    background: linear-gradient(90deg, {color} 0%, {color}dd 100%);
                    height: 100%;
                    width: {percentage}%;
                    transition: width 0.3s ease;
                    border-radius: 10px;
                "></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True  # ← CORREÇÃO APLICADA!
    )


def alert_box(message: str, alert_type: str = "info"):
    """
    Renderiza um box de alerta customizado - CORRIGIDO
    
    Args:
        message: Mensagem do alerta
        alert_type: Tipo (info, success, warning, error)
    """
    configs = {
        "info": {"color": "#17a2b8", "icon": "ℹ️", "bg": "#d1ecf1"},
        "success": {"color": "#28a745", "icon": "✅", "bg": "#d4edda"},
        "warning": {"color": "#ffc107", "icon": "⚠️", "bg": "#fff3cd"},
        "error": {"color": "#dc3545", "icon": "❌", "bg": "#f8d7da"}
    }
    
    config = configs.get(alert_type, configs["info"])
    
    st.markdown(
        f"""
        <div style="
            background-color: {config['bg']};
            border-left: 4px solid {config['color']};
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.5rem; margin-right: 0.75rem;">{config['icon']}</span>
                <span style="color: #333;">{message}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True  # ← CORREÇÃO APLICADA!
    )


def info_tooltip(text: str, tooltip: str):
    """
    Renderiza texto com tooltip - CORRIGIDO
    
    Args:
        text: Texto principal
        tooltip: Texto do tooltip
    """
    st.markdown(
        f"""
        <div style="position: relative; display: inline-block;">
            <span style="
                border-bottom: 1px dotted #666;
                cursor: help;
            " title="{tooltip}">{text}</span>
        </div>
        """,
        unsafe_allow_html=True  # ← CORREÇÃO APLICADA!
    )


def progress_ring(percentage: float, label: str, size: int = 120):
    """
    Renderiza um anel de progresso circular - CORRIGIDO
    
    Args:
        percentage: Porcentagem (0-100)
        label: Label do anel
        size: Tamanho do anel em pixels
    """
    # Calcular cor baseada na porcentagem
    if percentage >= 80:
        color = "#28a745"
    elif percentage >= 60:
        color = "#ffc107"
    else:
        color = "#dc3545"
    
    # Calcular circunferência
    radius = (size / 2) - 10
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100 * circumference)
    
    st.markdown(
        f"""
        <div style="text-align: center; margin: 1rem 0;">
            <svg width="{size}" height="{size}">
                <circle
                    cx="{size/2}"
                    cy="{size/2}"
                    r="{radius}"
                    fill="none"
                    stroke="#f0f0f0"
                    stroke-width="10"
                />
                <circle
                    cx="{size/2}"
                    cy="{size/2}"
                    r="{radius}"
                    fill="none"
                    stroke="{color}"
                    stroke-width="10"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    transform="rotate(-90 {size/2} {size/2})"
                    style="transition: stroke-dashoffset 0.5s ease;"
                />
                <text
                    x="50%"
                    y="50%"
                    text-anchor="middle"
                    dy="0.3em"
                    font-size="24"
                    font-weight="bold"
                    fill="{color}"
                >{percentage:.0f}%</text>
            </svg>
            <div style="
                font-weight: 600;
                color: #333;
                margin-top: 0.5rem;
            ">{label}</div>
        </div>
        """,
        unsafe_allow_html=True  # ← CORREÇÃO APLICADA!
    )


def confidence_gauge(confidence: float, title: str = "Confiança", height: int = 200):
    """
    Renderiza um medidor de confiança estilo gauge/velocímetro
    
    Args:
        confidence: Valor de confiança (0-1)
        title: Título do medidor
        height: Altura do componente em pixels
    """
    # Converter para porcentagem
    percentage = confidence * 100
    
    # Determinar cor e status baseado na confiança
    if confidence >= 0.8:
        color = "#28a745"
        status = "Alta"
        emoji = "🎯"
    elif confidence >= 0.6:
        color = "#ffc107"
        status = "Média"
        emoji = "📊"
    else:
        color = "#dc3545"
        status = "Baixa"
        emoji = "⚠️"
    
    # Calcular ângulo do ponteiro (180 graus de range)
    angle = 180 * confidence
    
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 1rem;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 1rem 0;
        ">
            <h3 style="
                color: #333;
                margin-bottom: 1rem;
                font-size: 1.2rem;
            ">{emoji} {title}</h3>
            
            <div style="position: relative; height: {height}px;">
                <!-- Gauge Background -->
                <svg width="100%" height="{height}" viewBox="0 0 300 180" style="position: absolute; left: 50%; transform: translateX(-50%);">
                    <!-- Arco de fundo -->
                    <path d="M 30 150 A 120 120 0 0 1 270 150"
                          stroke="#e0e0e0" stroke-width="25" fill="none"/>
                    
                    <!-- Arco colorido (progresso) -->
                    <path d="M 30 150 A 120 120 0 0 1 270 150"
                          stroke="{color}" stroke-width="25" fill="none"
                          stroke-dasharray="{377 * confidence} 377"
                          style="transition: stroke-dasharray 0.5s ease;"/>
                    
                    <!-- Marcadores -->
                    <text x="30" y="170" text-anchor="middle" fill="#999" font-size="12">0%</text>
                    <text x="150" y="40" text-anchor="middle" fill="#999" font-size="12">50%</text>
                    <text x="270" y="170" text-anchor="middle" fill="#999" font-size="12">100%</text>
                    
                    <!-- Ponteiro -->
                    <g transform="translate(150, 150)">
                        <line x1="0" y1="0" x2="0" y2="-90"
                              stroke="{color}" stroke-width="4"
                              transform="rotate({angle - 90})"
                              style="transition: transform 0.5s ease;"/>
                        <circle cx="0" cy="0" r="8" fill="{color}"/>
                    </g>
                    
                    <!-- Valor central -->
                    <text x="150" y="130" text-anchor="middle" 
                          font-size="36" font-weight="bold" fill="{color}">
                        {percentage:.1f}%
                    </text>
                    
                    <!-- Status -->
                    <text x="150" y="155" text-anchor="middle" 
                          font-size="14" fill="#666">
                        {status}
                    </text>
                </svg>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def comparison_card(title: str, model1_data: dict, model2_data: dict):
    """
    Renderiza um card de comparação entre dois modelos - CORRIGIDO
    
    Args:
        title: Título da comparação
        model1_data: Dados do modelo 1 {'name': str, 'value': str, 'color': str}
        model2_data: Dados do modelo 2 {'name': str, 'value': str, 'color': str}
    """
    st.markdown(
        f"""
        <div style="
            background: white;
            border: 2px solid #f0f0f0;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        ">
            <h3 style="
                color: #333;
                margin-bottom: 1rem;
                border-bottom: 2px solid #EA1D2C;
                padding-bottom: 0.5rem;
            ">{title}</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="
                    text-align: center;
                    padding: 1rem;
                    background: linear-gradient(135deg, {model1_data['color']}20 0%, {model1_data['color']}10 100%);
                    border-radius: 8px;
                    border: 2px solid {model1_data['color']};
                ">
                    <div style="
                        font-size: 0.9rem;
                        color: #666;
                        margin-bottom: 0.5rem;
                        font-weight: 600;
                    ">{model1_data['name']}</div>
                    <div style="
                        font-size: 1.8rem;
                        font-weight: bold;
                        color: {model1_data['color']};
                    ">{model1_data['value']}</div>
                </div>
                
                <div style="
                    text-align: center;
                    padding: 1rem;
                    background: linear-gradient(135deg, {model2_data['color']}20 0%, {model2_data['color']}10 100%);
                    border-radius: 8px;
                    border: 2px solid {model2_data['color']};
                ">
                    <div style="
                        font-size: 0.9rem;
                        color: #666;
                        margin-bottom: 0.5rem;
                        font-weight: 600;
                    ">{model2_data['name']}</div>
                    <div style="
                        font-size: 1.8rem;
                        font-weight: bold;
                        color: {model2_data['color']};
                    ">{model2_data['value']}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True  # ← CORREÇÃO APLICADA!
    )


# ============================================
# Exemplo de uso
# ============================================

if __name__ == "__main__":
    st.set_page_config(page_title="UI Components Demo", layout="wide")
    
    st.title("🎨 Componentes UI - Demonstração")
    st.markdown("---")
    
    # Metric Cards
    st.markdown("### 📊 Metric Cards")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("Reviews", "150K+", "+5.2K", "📊", "#EA1D2C")
    
    with col2:
        metric_card("Acurácia", "94.7%", "+2.3%", "🎯", "#28a745")
    
    with col3:
        metric_card("Latência", "45ms", "-12ms", "⚡", "#17a2b8")
    
    with col4:
        metric_card("Uptime", "99.9%", "", "✅", "#6c757d")
    
    st.markdown("---")
    
    # Sentiment Badge
    st.markdown("### 😊 Sentiment Badges")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_badge("positive", 0.95)
    
    with col2:
        sentiment_badge("negative", 0.87)
    
    with col3:
        sentiment_badge("neutral", 0.72)
    
    st.markdown("---")
    
    # Confidence Bar
    st.markdown("### 📊 Confidence Bars")
    confidence_bar(0.95, "Confiança Alta")
    confidence_bar(0.72, "Confiança Média")
    confidence_bar(0.45, "Confiança Baixa")
    
    st.markdown("---")
    
    # Alert Boxes
    st.markdown("### 📢 Alert Boxes")
    alert_box("Esta é uma informação importante", "info")
    alert_box("Operação realizada com sucesso!", "success")
    alert_box("Atenção: verificar configuração", "warning")
    alert_box("Erro ao processar requisição", "error")
    
    st.markdown("---")
    
    # Progress Rings
    st.markdown("### ⭕ Progress Rings")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        progress_ring(95, "Modelo A", 120)
    
    with col2:
        progress_ring(72, "Modelo B", 120)
    
    with col3:
        progress_ring(45, "Modelo C", 120)
    
    st.markdown("---")
    
    # Confidence Gauge
    st.markdown("### 🎯 Confidence Gauge")
    col1, col2 = st.columns(2)
    
    with col1:
        confidence_gauge(0.92, "Modelo BERT", 200)
    
    with col2:
        confidence_gauge(0.67, "Modelo GPT", 200)
    
    st.markdown("---")
    
    # Comparison Card
    st.markdown("### 🆚 Comparison Card")
    comparison_card(
        "Acurácia dos Modelos",
        {"name": "BERT", "value": "94.7%", "color": "#EA1D2C"},
        {"name": "GPT-4o-mini", "value": "96.2%", "color": "#28a745"}
    )
    
    st.success("✅ Todos os componentes agora renderizam HTML corretamente!")
