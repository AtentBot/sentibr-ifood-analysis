"""
SentiBR - Análise em Lote
Análise de múltiplos reviews simultaneamente
"""
import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Análise em Lote", page_icon="📦", layout="wide")

st.title("📦 Análise em Lote de Sentimentos")
st.markdown("Processe múltiplos reviews de uma vez")

# API endpoint
API_URL = "http://api:8000/api/v1/predict/batch"

# Upload de arquivo
st.subheader("📤 Upload de Arquivo CSV")

st.info("""
**Formato esperado do CSV:**
- Coluna `text`: Reviews para análise
- Coluna `rating` (opcional): Nota do review (1-5)

Exemplo:
```csv
text,rating
"Comida deliciosa!",5
"Entrega demorou",2
```
""")

uploaded_file = st.file_uploader(
    "Escolha um arquivo CSV",
    type=['csv'],
    help="Arquivo CSV com reviews para análise"
)

# Processar arquivo
if uploaded_file is not None:
    try:
        # Ler CSV
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Arquivo carregado: {len(df)} reviews encontrados")
        
        # Mostrar preview
        with st.expander("👀 Preview dos dados"):
            st.dataframe(df.head(10))
        
        # Opções de processamento
        st.markdown("---")
        st.subheader("⚙️ Configurações")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Número de reviews para processar
            max_reviews = st.selectbox(
                "Quantidade de reviews",
                options=[10, 50, 100, 500, len(df)],
                index=0,
                help="Quantidade de reviews para processar"
            )
        
        with col2:
            # Coluna com o texto
            text_column = st.selectbox(
                "Coluna com o texto",
                options=df.columns.tolist(),
                index=df.columns.tolist().index('text') if 'text' in df.columns else 0,
                help="Selecione a coluna que contém o texto dos reviews"
            )
        
        # Botão de processamento
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            process_button = st.button(
                "🚀 Processar Reviews",
                type="primary",
                use_container_width=True
            )
        
        # Processar
        if process_button:
            # Limitar quantidade
            df_process = df.head(max_reviews)
            
            # Verificar coluna
            if text_column not in df_process.columns:
                st.error(f"❌ Coluna '{text_column}' não encontrada!")
            else:
                # Extrair textos
                reviews = df_process[text_column].tolist()
                
                with st.spinner(f"🔄 Processando {len(reviews)} reviews..."):
                    try:
                        # Fazer requisição
                        response = requests.post(
                            API_URL,
                            json={"reviews": reviews},
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            results_list = result.get('results', [])
                            
                            st.success(f"✅ {len(results_list)} reviews processados!")
                            
                            # Criar DataFrame de resultados
                            results_df = pd.DataFrame([
                                {
                                    'text': r['text'],
                                    'sentiment': r['sentiment'],
                                    'confidence': f"{r['confidence'] * 100:.1f}%",
                                    'positive_score': f"{r['scores']['positive'] * 100:.1f}%",
                                    'neutral_score': f"{r['scores']['neutral'] * 100:.1f}%",
                                    'negative_score': f"{r['scores']['negative'] * 100:.1f}%"
                                }
                                for r in results_list
                            ])
                            
                            # Estatísticas
                            st.markdown("---")
                            st.subheader("📊 Estatísticas")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            total = len(results_df)
                            positives = len(results_df[results_df['sentiment'] == 'positive'])
                            neutrals = len(results_df[results_df['sentiment'] == 'neutral'])
                            negatives = len(results_df[results_df['sentiment'] == 'negative'])
                            
                            with col1:
                                st.metric("Total", total)
                            
                            with col2:
                                st.metric("Positivos", positives, f"{positives/total*100:.1f}%")
                            
                            with col3:
                                st.metric("Neutros", neutrals, f"{neutrals/total*100:.1f}%")
                            
                            with col4:
                                st.metric("Negativos", negatives, f"{negatives/total*100:.1f}%")
                            
                            # Resultados
                            st.markdown("---")
                            st.subheader("📋 Resultados")
                            
                            # Adicionar cores baseadas no sentimento
                            def highlight_sentiment(row):
                                if row['sentiment'] == 'positive':
                                    return ['background-color: #d4edda'] * len(row)
                                elif row['sentiment'] == 'negative':
                                    return ['background-color: #f8d7da'] * len(row)
                                else:
                                    return ['background-color: #fff3cd'] * len(row)
                            
                            styled_df = results_df.style.apply(highlight_sentiment, axis=1)
                            
                            st.dataframe(styled_df, use_container_width=True, height=400)
                            
                            # Download
                            st.markdown("---")
                            st.subheader("📥 Download")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # CSV
                                csv = results_df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download CSV",
                                    data=csv,
                                    file_name="sentibr_resultados.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
                            
                            with col2:
                                # Excel
                                output = io.BytesIO()
                                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                    results_df.to_excel(writer, index=False, sheet_name='Resultados')
                                
                                st.download_button(
                                    label="📥 Download Excel",
                                    data=output.getvalue(),
                                    file_name="sentibr_resultados.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        
                        else:
                            st.error(f"❌ Erro na API: {response.status_code}")
                            st.code(response.text)
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Timeout: Processamento demorou muito")
                        st.info("Tente com menos reviews ou aumente o timeout")
                    
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Erro de Conexão: API não acessível")
                    
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Erro ao ler arquivo: {str(e)}")
        st.info("Verifique se o arquivo está no formato CSV correto")

else:
    # Sem arquivo - mostrar exemplo
    st.markdown("---")
    st.subheader("💡 Exemplo de CSV")
    
    example_df = pd.DataFrame({
        'text': [
            'Comida deliciosa, entrega rápida!',
            'Péssimo atendimento, nunca mais',
            'Normal, nada excepcional',
            'Melhor restaurante da cidade!',
            'Demorou muito, comida fria'
        ],
        'rating': [5, 1, 3, 5, 2]
    })
    
    st.dataframe(example_df)
    
    # Download do exemplo
    csv_example = example_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Exemplo CSV",
        data=csv_example,
        file_name="exemplo_reviews.csv",
        mime="text/csv"
    )

# Informações
st.markdown("---")

with st.expander("ℹ️ Informações Importantes"):
    st.markdown("""
    ### Formato do Arquivo
    
    - **Formato**: CSV (valores separados por vírgula)
    - **Encoding**: UTF-8
    - **Colunas obrigatórias**: `text`
    - **Colunas opcionais**: `rating`, `date`, etc.
    
    ### Limites
    
    - **Máximo recomendado**: 500 reviews por processamento
    - **Timeout**: 60 segundos
    - **Tamanho máximo**: 10MB
    
    ### Performance
    
    - **Tempo médio**: ~100-200ms por review
    - **Processamento**: Sequencial (um por vez)
    - **Cache**: Reviews idênticos são cacheados
    
    ### Dicas
    
    - Use arquivos menores para testes
    - Processe em lotes para volumes grandes
    - Verifique a qualidade dos textos antes
    """)
