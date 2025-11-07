"""
Correção para o erro: "Erro na avaliação BERT: 'text'"

Este erro ocorre quando os dados não estão no formato esperado pelo modelo BERT.
"""

import streamlit as st
import pandas as pd
import requests
from typing import List, Dict
import json

# ============================================
# CORREÇÃO 1: Validação de Dados
# ============================================

def validate_data_format(data):
    """
    Valida se os dados estão no formato correto para avaliação BERT
    
    Formato esperado:
    - Lista de dicts com chave 'text' ou 'review'
    - DataFrame com coluna 'text' ou 'review'
    """
    
    # Se for DataFrame
    if isinstance(data, pd.DataFrame):
        # Verificar se tem coluna 'text'
        if 'text' not in data.columns:
            # Tentar encontrar coluna similar
            possible_columns = ['review', 'Review', 'texto', 'Texto', 'content', 'Content']
            
            for col in possible_columns:
                if col in data.columns:
                    # Renomear coluna
                    data = data.rename(columns={col: 'text'})
                    st.info(f"✅ Coluna '{col}' renomeada para 'text'")
                    return data
            
            # Se não encontrou, mostrar erro
            st.error(f"""
            ❌ **Erro de Formato de Dados**
            
            O DataFrame não possui a coluna 'text' esperada.
            
            **Colunas disponíveis**: {list(data.columns)}
            
            **Soluções**:
            1. Renomeie a coluna para 'text'
            2. Use uma das colunas: {possible_columns}
            """)
            return None
        
        return data
    
    # Se for lista de dicts
    elif isinstance(data, list):
        if len(data) == 0:
            st.error("❌ Lista de dados está vazia")
            return None
        
        # Verificar primeiro item
        first_item = data[0]
        
        if not isinstance(first_item, dict):
            st.error(f"❌ Esperado dict, recebido {type(first_item)}")
            return None
        
        if 'text' not in first_item:
            # Tentar encontrar chave similar
            possible_keys = ['review', 'Review', 'texto', 'Texto', 'content', 'Content']
            
            for key in possible_keys:
                if key in first_item:
                    # Renomear chave em todos os items
                    data = [{'text': item.get(key, '')} for item in data]
                    st.info(f"✅ Chave '{key}' renomeada para 'text'")
                    return data
            
            st.error(f"""
            ❌ **Erro de Formato de Dados**
            
            Os dicts não possuem a chave 'text' esperada.
            
            **Chaves disponíveis**: {list(first_item.keys())}
            """)
            return None
        
        return data
    
    else:
        st.error(f"❌ Formato de dados não suportado: {type(data)}")
        return None


# ============================================
# CORREÇÃO 2: Função de Avaliação BERT Robusta
# ============================================

def evaluate_bert_safe(samples: List[Dict], api_url: str = "http://localhost:8000/api/v1"):
    """
    Avalia samples usando BERT com tratamento de erros robusto
    """
    
    results = []
    errors = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, sample in enumerate(samples):
        try:
            # Extrair texto do sample
            if isinstance(sample, dict):
                text = sample.get('text') or sample.get('review') or sample.get('Review')
            else:
                text = str(sample)
            
            if not text or not isinstance(text, str):
                errors.append(f"Sample {idx}: Texto inválido")
                continue
            
            # Fazer predição
            status_text.text(f"Avaliando sample {idx+1}/{len(samples)}...")
            
            response = requests.post(
                f"{api_url}/predict",
                json={"text": text},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'text': text,
                    'sentiment': result.get('sentiment'),
                    'confidence': result.get('confidence'),
                    'aspects': result.get('aspects', [])
                })
            else:
                errors.append(f"Sample {idx}: HTTP {response.status_code}")
            
            # Atualizar progresso
            progress_bar.progress((idx + 1) / len(samples))
            
        except requests.exceptions.Timeout:
            errors.append(f"Sample {idx}: Timeout")
        except requests.exceptions.ConnectionError:
            errors.append(f"Sample {idx}: Erro de conexão")
        except Exception as e:
            errors.append(f"Sample {idx}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    
    return results, errors


# ============================================
# CORREÇÃO 3: Interface de Avaliação Corrigida
# ============================================

def show_evaluation_interface():
    """
    Interface de avaliação com tratamento de erros
    """
    
    st.title("🎯 Avaliação BERT - Versão Corrigida")
    
    # Upload de dados
    uploaded_file = st.file_uploader(
        "📤 Upload de dados para avaliar",
        type=['csv', 'json', 'xlsx']
    )
    
    if uploaded_file:
        # Carregar dados
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Carregados {len(df)} samples")
            
            # Mostrar preview
            with st.expander("👀 Preview dos Dados"):
                st.dataframe(df.head())
            
            # VALIDAR FORMATO
            df_validated = validate_data_format(df)
            
            if df_validated is None:
                st.stop()
            
            # Configuração
            st.markdown("---")
            st.subheader("⚙️ Configuração da Avaliação")
            
            num_samples = st.slider(
                "Número de samples para avaliar",
                min_value=1,
                max_value=len(df_validated),
                value=min(30, len(df_validated))
            )
            
            # Selecionar samples
            samples_to_evaluate = df_validated.head(num_samples).to_dict('records')
            
            # Botão de avaliação
            if st.button("🚀 Executar Avaliação BERT", use_container_width=True):
                
                with st.spinner("Executando avaliação..."):
                    
                    # Executar avaliação
                    results, errors = evaluate_bert_safe(samples_to_evaluate)
                    
                    # Mostrar resultados
                    if results:
                        st.success(f"✅ {len(results)} avaliações concluídas!")
                        
                        # Converter para DataFrame
                        results_df = pd.DataFrame(results)
                        
                        # Mostrar métricas
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            positive = len(results_df[results_df['sentiment'] == 'positive'])
                            st.metric("Positivos", positive)
                        
                        with col2:
                            negative = len(results_df[results_df['sentiment'] == 'negative'])
                            st.metric("Negativos", negative)
                        
                        with col3:
                            neutral = len(results_df[results_df['sentiment'] == 'neutral'])
                            st.metric("Neutros", neutral)
                        
                        # Mostrar resultados detalhados
                        with st.expander("📊 Resultados Detalhados"):
                            st.dataframe(results_df)
                        
                        # Download
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Resultados (CSV)",
                            data=csv,
                            file_name="evaluation_results.csv",
                            mime="text/csv"
                        )
                    
                    # Mostrar erros se houver
                    if errors:
                        st.warning(f"⚠️ {len(errors)} erro(s) encontrado(s)")
                        
                        with st.expander("❌ Ver Erros"):
                            for error in errors:
                                st.error(error)
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
            st.info("""
            **Formatos aceitos**:
            - CSV com coluna 'text' ou 'review'
            - JSON com chave 'text' ou 'review'
            - Excel com coluna 'text' ou 'review'
            """)


# ============================================
# CORREÇÃO 4: Exemplo de Uso Correto
# ============================================

def show_correct_usage_example():
    """
    Mostra exemplos de formato correto de dados
    """
    
    st.subheader("📚 Exemplos de Formato Correto")
    
    tab1, tab2, tab3 = st.tabs(["CSV", "JSON", "DataFrame"])
    
    with tab1:
        st.markdown("### Formato CSV")
        st.code("""
text,label
"A comida estava deliciosa!",positive
"Entrega muito demorada",negative
"Produto ok",neutral
        """)
    
    with tab2:
        st.markdown("### Formato JSON")
        st.code("""
[
  {"text": "A comida estava deliciosa!", "label": "positive"},
  {"text": "Entrega muito demorada", "label": "negative"},
  {"text": "Produto ok", "label": "neutral"}
]
        """, language="json")
    
    with tab3:
        st.markdown("### DataFrame (pandas)")
        st.code("""
import pandas as pd

df = pd.DataFrame({
    'text': [
        'A comida estava deliciosa!',
        'Entrega muito demorada',
        'Produto ok'
    ],
    'label': ['positive', 'negative', 'neutral']
})
        """, language="python")


# ============================================
# CORREÇÃO 5: Diagnostic Tool
# ============================================

def show_diagnostic_tool():
    """
    Ferramenta de diagnóstico para identificar problemas
    """
    
    st.subheader("🔍 Ferramenta de Diagnóstico")
    
    uploaded_file = st.file_uploader(
        "Upload seu arquivo para diagnóstico",
        type=['csv', 'json', 'xlsx']
    )
    
    if uploaded_file:
        try:
            # Tentar carregar
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            
            st.success("✅ Arquivo carregado com sucesso!")
            
            # Diagnóstico
            st.markdown("### 📊 Análise do Arquivo")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Número de Linhas", len(df))
                st.metric("Número de Colunas", len(df.columns))
            
            with col2:
                st.write("**Colunas Disponíveis:**")
                for col in df.columns:
                    st.write(f"- `{col}` ({df[col].dtype})")
            
            # Verificar coluna 'text'
            st.markdown("### ✅ Verificações")
            
            if 'text' in df.columns:
                st.success("✅ Coluna 'text' encontrada!")
            else:
                st.error("❌ Coluna 'text' NÃO encontrada")
                
                # Sugerir colunas
                text_like_columns = [col for col in df.columns if 'text' in col.lower() or 'review' in col.lower()]
                
                if text_like_columns:
                    st.info(f"💡 Colunas similares encontradas: {text_like_columns}")
                    st.info("Sugestão: Renomeie uma dessas colunas para 'text'")
            
            # Verificar valores nulos
            null_counts = df.isnull().sum()
            if null_counts.any():
                st.warning("⚠️ Valores nulos encontrados:")
                st.write(null_counts[null_counts > 0])
            else:
                st.success("✅ Nenhum valor nulo")
            
            # Preview
            st.markdown("### 👀 Preview dos Dados")
            st.dataframe(df.head(10))
            
        except Exception as e:
            st.error(f"❌ Erro ao analisar arquivo: {str(e)}")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    
    st.set_page_config(
        page_title="Correção - Avaliação BERT",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 Correção - Erro de Avaliação BERT")
    
    st.error("""
    ### ❌ Erro Detectado
    **"Erro na avaliação BERT: 'text'"**
    
    Este erro ocorre quando os dados não estão no formato esperado.
    """)
    
    st.info("""
    ### 💡 Solução
    Use as ferramentas abaixo para corrigir o problema.
    """)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "🔧 Avaliação Corrigida",
        "📚 Exemplos Corretos",
        "🔍 Diagnóstico"
    ])
    
    with tab1:
        show_evaluation_interface()
    
    with tab2:
        show_correct_usage_example()
    
    with tab3:
        show_diagnostic_tool()
