"""
SentiBR - Avaliação BERT (VERSÃO CORRIGIDA)
Página para executar avaliações completas do modelo BERT
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Avaliação - SentiBR",
    page_icon="🔎",
    layout="wide"
)

# URL da API
API_URL = "http://localhost:8000/api/v1"

# ============================================
# CORREÇÃO DO ERRO 'text'
# ============================================

def fix_data_format(data):
    """
    CORREÇÃO: Garante que os dados estejam no formato correto
    com a chave 'text' que o modelo BERT espera
    """
    if isinstance(data, pd.DataFrame):
        # Se for DataFrame, renomear colunas comuns
        rename_map = {
            'review': 'text',
            'Review': 'text',
            'reviews': 'text',
            'texto': 'text',
            'Texto': 'text',
            'content': 'text',
            'Content': 'text',
            'comment': 'text',
            'Comment': 'text'
        }
        
        for old_col, new_col in rename_map.items():
            if old_col in data.columns and 'text' not in data.columns:
                data = data.rename(columns={old_col: new_col})
                st.success(f"✅ Coluna '{old_col}' renomeada para 'text'")
                break
        
        if 'text' not in data.columns:
            st.error(f"❌ Nenhuma coluna de texto encontrada. Colunas: {list(data.columns)}")
            return None
        
        return data
    
    elif isinstance(data, list):
        # Se for lista de dicts
        if len(data) == 0:
            return data
        
        fixed_data = []
        for item in data:
            if isinstance(item, dict):
                if 'text' not in item:
                    # Tentar encontrar chave alternativa
                    for key in ['review', 'Review', 'texto', 'content', 'comment']:
                        if key in item:
                            item['text'] = item[key]
                            break
                    
                    # Se ainda não tem 'text', pegar primeiro valor
                    if 'text' not in item and item:
                        first_key = list(item.keys())[0]
                        item['text'] = item[first_key]
                
                fixed_data.append(item)
            else:
                # Se não for dict, converter
                fixed_data.append({'text': str(item)})
        
        return fixed_data
    
    elif isinstance(data, dict):
        # Se for dict único
        if 'text' not in data:
            for key in ['review', 'Review', 'texto', 'content', 'comment']:
                if key in data:
                    data['text'] = data[key]
                    break
        
        return data
    
    return data


def validate_data(data):
    """Valida se os dados estão no formato correto"""
    if data is None:
        return False
    
    if isinstance(data, pd.DataFrame):
        return 'text' in data.columns and len(data) > 0
    
    elif isinstance(data, list):
        return len(data) > 0 and all('text' in item for item in data if isinstance(item, dict))
    
    elif isinstance(data, dict):
        return 'text' in data
    
    return False


# ============================================
# Funções de Avaliação
# ============================================

def evaluate_samples_bert(samples, progress_callback=None):
    """
    Avalia samples usando BERT com tratamento robusto de erros
    """
    results = []
    errors = []
    
    for idx, sample in enumerate(samples):
        try:
            # Extrair texto
            if isinstance(sample, dict):
                text = sample.get('text', '')
            else:
                text = str(sample)
            
            if not text:
                errors.append(f"Sample {idx}: Texto vazio")
                continue
            
            # Fazer predição
            response = requests.post(
                f"{API_URL}/predict",
                json={"text": text},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'index': idx,
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'sentiment': result.get('sentiment'),
                    'confidence': result.get('confidence'),
                    'inference_time': result.get('inference_time_ms', 0)
                })
            else:
                errors.append(f"Sample {idx}: HTTP {response.status_code}")
            
            # Callback de progresso
            if progress_callback:
                progress_callback(idx + 1, len(samples))
        
        except requests.exceptions.Timeout:
            errors.append(f"Sample {idx}: Timeout")
        except requests.exceptions.ConnectionError:
            errors.append(f"Sample {idx}: Erro de conexão com API")
        except Exception as e:
            errors.append(f"Sample {idx}: {str(e)}")
    
    return results, errors


def evaluate_samples_gpt(samples, progress_callback=None):
    """Avalia samples usando GPT"""
    results = []
    errors = []
    
    for idx, sample in enumerate(samples):
        try:
            text = sample.get('text', '') if isinstance(sample, dict) else str(sample)
            
            if not text:
                errors.append(f"Sample {idx}: Texto vazio")
                continue
            
            response = requests.post(
                f"{API_URL}/predict/gpt",
                json={"text": text},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'index': idx,
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'sentiment': result.get('sentiment'),
                    'confidence': result.get('confidence'),
                    'reasoning': result.get('reasoning', '')
                })
            else:
                errors.append(f"Sample {idx}: HTTP {response.status_code}")
            
            if progress_callback:
                progress_callback(idx + 1, len(samples))
        
        except Exception as e:
            errors.append(f"Sample {idx}: {str(e)}")
    
    return results, errors


# ============================================
# Interface Principal
# ============================================

st.title("🔎 Avaliação do Modelo BERT")
st.markdown("*Execute avaliações completas e compare com GPT*")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload de Dados", "⚙️ Configuração", "📊 Resultados"])

# ============================================
# TAB 1: Upload de Dados
# ============================================

with tab1:
    st.subheader("📤 Upload de Dados para Avaliação")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Faça upload do arquivo com os dados",
        type=['csv', 'json', 'xlsx'],
        help="Formatos aceitos: CSV, JSON, Excel"
    )
    
    if uploaded_file:
        try:
            # Carregar dados
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Arquivo carregado: {len(df)} linhas")
            
            # Mostrar preview
            with st.expander("👀 Preview dos Dados"):
                st.dataframe(df.head(10))
                st.info(f"**Colunas**: {', '.join(df.columns)}")
            
            # ✅ APLICAR CORREÇÃO
            st.info("🔄 Validando formato dos dados...")
            df_fixed = fix_data_format(df)
            
            if df_fixed is not None and validate_data(df_fixed):
                st.success("✅ Dados validados e prontos para avaliação!")
                
                # Salvar no session_state
                st.session_state['evaluation_data'] = df_fixed
                st.session_state['data_loaded'] = True
            else:
                st.error("❌ Erro: Dados em formato inválido após correção")
                st.session_state['data_loaded'] = False
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
            st.session_state['data_loaded'] = False
    else:
        st.info("""
        ### 📚 Formato Esperado
        
        Seu arquivo deve ter uma coluna com os textos para análise.
        
        **Nomes aceitos para a coluna**:
        - `text` (recomendado)
        - `review`
        - `content`
        - `comment`
        
        **Exemplo de CSV**:
        ```
        text,label
        "A comida estava deliciosa!",positive
        "Entrega muito demorada",negative
        ```
        """)

# ============================================
# TAB 2: Configuração
# ============================================

with tab2:
    st.subheader("⚙️ Configuração da Avaliação")
    
    if not st.session_state.get('data_loaded', False):
        st.warning("⚠️ Faça upload dos dados primeiro na aba 'Upload de Dados'")
    else:
        data = st.session_state['evaluation_data']
        total_samples = len(data) if isinstance(data, pd.DataFrame) else len(data)
        
        st.info(f"📊 Total de samples disponíveis: **{total_samples}**")
        
        # Número de samples
        num_samples = st.slider(
            "Número de samples para avaliar",
            min_value=1,
            max_value=min(total_samples, 100),
            value=min(30, total_samples),
            help="Máximo de 100 samples por avaliação"
        )
        
        # Usar LLM Judge
        use_llm_judge = st.checkbox(
            "🤖 Usar LLM Judge (GPT-4o-mini)",
            value=True,
            help="Compara resultados BERT com GPT"
        )
        
        st.markdown("---")
        
        # Botão de executar
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🚀 Executar Avaliação Completa", use_container_width=True):
                st.session_state['run_evaluation'] = True
                st.session_state['num_samples'] = num_samples
                st.session_state['use_llm_judge'] = use_llm_judge

# ============================================
# TAB 3: Resultados
# ============================================

with tab3:
    st.subheader("📊 Resultados da Avaliação")
    
    if st.session_state.get('run_evaluation', False):
        
        data = st.session_state['evaluation_data']
        num_samples = st.session_state['num_samples']
        use_llm = st.session_state['use_llm_judge']
        
        # Preparar samples
        if isinstance(data, pd.DataFrame):
            samples = data.head(num_samples).to_dict('records')
        else:
            samples = data[:num_samples]
        
        # ✅ GARANTIR FORMATO CORRETO
        samples = fix_data_format(samples)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Avaliação BERT
        status_text.text("🤖 Avaliando com BERT...")
        
        def update_progress_bert(current, total):
            progress = current / total * 0.5  # 50% do progresso
            progress_bar.progress(progress)
            status_text.text(f"🤖 BERT: {current}/{total} samples")
        
        bert_results, bert_errors = evaluate_samples_bert(
            samples,
            progress_callback=update_progress_bert
        )
        
        # Avaliação GPT (se habilitado)
        gpt_results = []
        gpt_errors = []
        
        if use_llm and bert_results:
            status_text.text("🧠 Avaliando com GPT...")
            
            def update_progress_gpt(current, total):
                progress = 0.5 + (current / total * 0.5)  # 50-100%
                progress_bar.progress(progress)
                status_text.text(f"🧠 GPT: {current}/{total} samples")
            
            gpt_results, gpt_errors = evaluate_samples_gpt(
                samples,
                progress_callback=update_progress_gpt
            )
        
        progress_bar.progress(1.0)
        status_text.text("✅ Avaliação concluída!")
        
        st.markdown("---")
        
        # Mostrar resultados BERT
        if bert_results:
            st.success(f"✅ BERT: {len(bert_results)} avaliações concluídas")
            
            df_bert = pd.DataFrame(bert_results)
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                positive = len(df_bert[df_bert['sentiment'] == 'positive'])
                st.metric("Positivos", positive)
            
            with col2:
                negative = len(df_bert[df_bert['sentiment'] == 'negative'])
                st.metric("Negativos", negative)
            
            with col3:
                neutral = len(df_bert[df_bert['sentiment'] == 'neutral'])
                st.metric("Neutros", neutral)
            
            with col4:
                avg_conf = df_bert['confidence'].mean()
                st.metric("Confiança Média", f"{avg_conf:.2%}")
            
            # Gráfico
            fig = px.pie(
                df_bert,
                names='sentiment',
                title='Distribuição de Sentimentos (BERT)',
                color='sentiment',
                color_discrete_map={
                    'positive': '#00CC96',
                    'negative': '#EF553B',
                    'neutral': '#FFA15A'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de resultados
            with st.expander("📋 Ver Resultados Detalhados"):
                st.dataframe(df_bert, use_container_width=True)
            
            # Download
            csv_bert = df_bert.to_csv(index=False)
            st.download_button(
                label="📥 Download Resultados BERT (CSV)",
                data=csv_bert,
                file_name=f"bert_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Mostrar erros BERT
        if bert_errors:
            with st.expander(f"⚠️ Erros BERT ({len(bert_errors)})"):
                for error in bert_errors:
                    st.error(error)
        
        # Mostrar resultados GPT
        if gpt_results:
            st.markdown("---")
            st.success(f"✅ GPT: {len(gpt_results)} avaliações concluídas")
            
            df_gpt = pd.DataFrame(gpt_results)
            
            # Comparação
            if len(bert_results) == len(gpt_results):
                agreement = sum(
                    b['sentiment'] == g['sentiment']
                    for b, g in zip(bert_results, gpt_results)
                )
                agreement_pct = (agreement / len(bert_results)) * 100
                
                st.info(f"🤝 Concordância BERT vs GPT: **{agreement_pct:.1f}%**")
            
            # Download GPT
            csv_gpt = df_gpt.to_csv(index=False)
            st.download_button(
                label="📥 Download Resultados GPT (CSV)",
                data=csv_gpt,
                file_name=f"gpt_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Limpar flag
        st.session_state['run_evaluation'] = False
    
    else:
        st.info("Configure e execute a avaliação na aba 'Configuração'")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>SentiBR Evaluation System v2.0 (Versão Corrigida) | Erro 'text' resolvido ✅</p>
</div>
""", unsafe_allow_html=True)
