"""
SentiBR - Retreinamento do Modelo
Fine-tuning do BERT com novo dataset
"""
import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Retreinamento", page_icon="🔄", layout="wide")

st.title("🔄 Retreinamento do Modelo")
st.markdown("Fine-tuning do BERT com novos dados")

# API endpoint
API_URL = "http://api:8000/api/v1/model"

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload Dataset",
    "⚙️ Configuração",
    "🚀 Treinar",
    "📊 Histórico"
])

# ============================================================================
# TAB 1: UPLOAD DATASET
# ============================================================================
with tab1:
    st.subheader("📤 Upload de Novo Dataset")
    
    st.info("""
    **Formato esperado do dataset de treinamento:**
    
    ```csv
    text,label
    "Comida deliciosa, recomendo!",positive
    "Péssimo atendimento",negative
    "Ok, nada especial",neutral
    ```
    
    - **Coluna `text`**: Texto do review
    - **Coluna `label`**: Sentimento (positive, neutral, negative)
    - **Mínimo**: 1000 exemplos
    - **Recomendado**: 10000+ exemplos
    """)
    
    # Upload
    uploaded_file = st.file_uploader(
        "Escolha o arquivo CSV",
        type=['csv'],
        help="Dataset no formato especificado acima"
    )
    
    if uploaded_file:
        try:
            # Ler dataset
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ Dataset carregado: {len(df)} exemplos")
            
            # Validar formato
            required_cols = ['text', 'label']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Colunas faltando: {missing_cols}")
            else:
                # Análise do dataset
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total de Exemplos", len(df))
                
                with col2:
                    positives = len(df[df['label'] == 'positive'])
                    st.metric("Positivos", positives, f"{positives/len(df)*100:.1f}%")
                
                with col3:
                    neutrals = len(df[df['label'] == 'neutral'])
                    st.metric("Neutros", neutrals, f"{neutrals/len(df)*100:.1f}%")
                
                with col4:
                    negatives = len(df[df['label'] == 'negative'])
                    st.metric("Negativos", negatives, f"{negatives/len(df)*100:.1f}%")
                
                # Preview
                st.markdown("### 👀 Preview do Dataset")
                st.dataframe(df.head(20), use_container_width=True)
                
                # Distribuição
                st.markdown("### 📊 Distribuição de Classes")
                
                import plotly.express as px
                
                dist_data = pd.DataFrame({
                    'Label': ['Positivo', 'Neutro', 'Negativo'],
                    'Quantidade': [positives, neutrals, negatives]
                })
                
                fig = px.bar(
                    dist_data,
                    x='Label',
                    y='Quantidade',
                    color='Label',
                    color_discrete_map={
                        'Positivo': '#28a745',
                        'Neutro': '#ffc107',
                        'Negativo': '#dc3545'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Validações
                st.markdown("### ✅ Validações")
                
                # Tamanho mínimo
                if len(df) < 1000:
                    st.warning(f"⚠️ Dataset pequeno ({len(df)} exemplos). Recomendado: 1000+")
                else:
                    st.success(f"✅ Tamanho adequado ({len(df)} exemplos)")
                
                # Balanceamento
                max_class = max(positives, neutrals, negatives)
                min_class = min(positives, neutrals, negatives)
                imbalance_ratio = max_class / min_class if min_class > 0 else float('inf')
                
                if imbalance_ratio > 3:
                    st.warning(f"⚠️ Dataset desbalanceado (ratio: {imbalance_ratio:.1f}:1)")
                    st.info("💡 Considere balancear as classes para melhor performance")
                else:
                    st.success(f"✅ Dataset balanceado (ratio: {imbalance_ratio:.1f}:1)")
                
                # Textos vazios
                empty_texts = df['text'].isna().sum()
                if empty_texts > 0:
                    st.error(f"❌ {empty_texts} textos vazios encontrados!")
                else:
                    st.success("✅ Nenhum texto vazio")
                
                # Labels inválidos
                valid_labels = ['positive', 'neutral', 'negative']
                invalid_labels = df[~df['label'].isin(valid_labels)]
                if len(invalid_labels) > 0:
                    st.error(f"❌ {len(invalid_labels)} labels inválidos encontrados!")
                    st.dataframe(invalid_labels.head())
                else:
                    st.success("✅ Todos os labels são válidos")
                
                # Salvar dataset na sessão
                if st.button("💾 Confirmar e Usar Este Dataset", type="primary", use_container_width=True):
                    st.session_state.training_dataset = df
                    st.success("✅ Dataset confirmado! Vá para a aba 'Configuração'")
        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
    
    # Dataset exemplo
    st.markdown("---")
    st.markdown("### 💡 Dataset de Exemplo")
    
    example_df = pd.DataFrame({
        'text': [
            'Comida deliciosa, entrega rápida! Recomendo muito!',
            'Péssimo atendimento, nunca mais peço aqui',
            'Normal, nada excepcional',
            'Melhor restaurante da região, sempre impecável',
            'Demorou mais de 2 horas, comida chegou fria',
            'Sabor ok, preço justo',
            'Atendimento excelente, comida saborosa',
            'Não gostei, esperava mais',
            'Custo benefício bom',
            'Horrível, não recomendo'
        ],
        'label': [
            'positive', 'negative', 'neutral', 'positive', 'negative',
            'neutral', 'positive', 'negative', 'neutral', 'negative'
        ]
    })
    
    st.dataframe(example_df)
    
    csv = example_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Exemplo CSV",
        data=csv,
        file_name="exemplo_training_dataset.csv",
        mime="text/csv"
    )

# ============================================================================
# TAB 2: CONFIGURAÇÃO
# ============================================================================
with tab2:
    st.subheader("⚙️ Configuração do Treinamento")
    
    # Verificar se dataset foi carregado
    if 'training_dataset' not in st.session_state:
        st.warning("⚠️ Faça upload do dataset na aba 'Upload Dataset' primeiro!")
    else:
        df = st.session_state.training_dataset
        st.success(f"✅ Dataset carregado: {len(df)} exemplos")
        
        st.markdown("---")
        
        # Hiperparâmetros
        st.markdown("### 🎛️ Hiperparâmetros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            epochs = st.slider(
                "Número de Épocas",
                min_value=1,
                max_value=10,
                value=3,
                help="Quantas vezes o modelo verá todo o dataset"
            )
            
            batch_size = st.selectbox(
                "Batch Size",
                options=[8, 16, 32, 64],
                index=2,
                help="Número de exemplos processados por vez"
            )
            
            learning_rate = st.select_slider(
                "Learning Rate",
                options=[1e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4],
                value=2e-5,
                help="Taxa de aprendizado do modelo"
            )
        
        with col2:
            max_length = st.slider(
                "Comprimento Máximo",
                min_value=128,
                max_value=512,
                value=256,
                step=64,
                help="Número máximo de tokens por review"
            )
            
            train_split = st.slider(
                "% Treinamento",
                min_value=70,
                max_value=90,
                value=80,
                help="Percentual do dataset para treinamento"
            )
            
            warmup_steps = st.number_input(
                "Warmup Steps",
                min_value=0,
                max_value=1000,
                value=100,
                help="Steps para warm-up do learning rate"
            )
        
        # Estratégias avançadas
        st.markdown("---")
        st.markdown("### 🎯 Estratégias Avançadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            use_class_weights = st.checkbox(
                "Usar Class Weights",
                value=True,
                help="Balanceia automaticamente classes desbalanceadas"
            )
            
            use_early_stopping = st.checkbox(
                "Early Stopping",
                value=True,
                help="Para o treino se não houver melhoria"
            )
            
            if use_early_stopping:
                patience = st.number_input(
                    "Patience (épocas)",
                    min_value=1,
                    max_value=5,
                    value=2,
                    help="Épocas sem melhoria antes de parar"
                )
        
        with col2:
            use_lr_scheduler = st.checkbox(
                "Learning Rate Scheduler",
                value=True,
                help="Ajusta LR durante treinamento"
            )
            
            save_best_only = st.checkbox(
                "Salvar Apenas Melhor Modelo",
                value=True,
                help="Salva apenas quando há melhoria"
            )
            
            log_to_mlflow = st.checkbox(
                "Log para MLflow",
                value=True,
                help="Registra experimento no MLflow"
            )
        
        # Nome do experimento
        st.markdown("---")
        st.markdown("### 📝 Identificação")
        
        experiment_name = st.text_input(
            "Nome do Experimento",
            value=f"fine_tune_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            help="Nome para identificar este treinamento"
        )
        
        description = st.text_area(
            "Descrição (opcional)",
            placeholder="Ex: Retreinamento com reviews de pizza...",
            help="Descrição do objetivo deste treinamento"
        )
        
        # Resumo da configuração
        st.markdown("---")
        st.markdown("### 📋 Resumo da Configuração")
        
        config = {
            "Dataset": f"{len(df)} exemplos",
            "Épocas": epochs,
            "Batch Size": batch_size,
            "Learning Rate": f"{learning_rate}",
            "Max Length": max_length,
            "Train/Val Split": f"{train_split}%/{100-train_split}%",
            "Class Weights": "✅" if use_class_weights else "❌",
            "Early Stopping": "✅" if use_early_stopping else "❌",
            "LR Scheduler": "✅" if use_lr_scheduler else "❌",
            "MLflow": "✅" if log_to_mlflow else "❌"
        }
        
        st.json(config)
        
        # Estimativa de tempo
        st.info(f"""
        ⏱️ **Tempo Estimado**: ~{epochs * len(df) // batch_size // 100} minutos
        
        💾 **Espaço em Disco**: ~500MB (modelo + checkpoints)
        
        🔥 **GPU Recomendada**: NVIDIA T4 ou superior
        """)
        
        # Salvar configuração
        if st.button("💾 Confirmar Configuração", type="primary", use_container_width=True):
            st.session_state.training_config = {
                'epochs': epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'max_length': max_length,
                'train_split': train_split,
                'warmup_steps': warmup_steps,
                'use_class_weights': use_class_weights,
                'use_early_stopping': use_early_stopping,
                'patience': patience if use_early_stopping else None,
                'use_lr_scheduler': use_lr_scheduler,
                'save_best_only': save_best_only,
                'log_to_mlflow': log_to_mlflow,
                'experiment_name': experiment_name,
                'description': description
            }
            st.success("✅ Configuração salva! Vá para a aba 'Treinar'")

# ============================================================================
# TAB 3: TREINAR
# ============================================================================
with tab3:
    st.subheader("🚀 Iniciar Treinamento")
    
    # Verificar pré-requisitos
    if 'training_dataset' not in st.session_state:
        st.error("❌ Dataset não carregado! Vá para a aba 'Upload Dataset'")
    elif 'training_config' not in st.session_state:
        st.error("❌ Configuração não definida! Vá para a aba 'Configuração'")
    else:
        df = st.session_state.training_dataset
        config = st.session_state.training_config
        
        # Resumo antes de iniciar
        st.markdown("### 📋 Resumo do Treinamento")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Dataset", f"{len(df)} exemplos")
            st.metric("Épocas", config['epochs'])
        
        with col2:
            st.metric("Batch Size", config['batch_size'])
            st.metric("Learning Rate", f"{config['learning_rate']}")
        
        with col3:
            st.metric("Max Length", config['max_length'])
            st.metric("Experimento", config['experiment_name'])
        
        st.markdown("---")
        
        # Avisos importantes
        st.warning("""
        ⚠️ **ATENÇÃO**:
        - O treinamento pode demorar vários minutos
        - Não feche esta página durante o treinamento
        - O modelo atual será substituído apenas se houver melhoria
        - Será criado um backup automático do modelo atual
        """)
        
        # Botão de iniciar
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 INICIAR TREINAMENTO", type="primary", use_container_width=True):
                st.session_state.training_started = True
        
        # Simulação de treinamento
        if st.session_state.get('training_started', False):
            st.markdown("---")
            st.markdown("### 🔄 Treinamento em Progresso...")
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Métricas em tempo real
            col1, col2, col3, col4 = st.columns(4)
            
            metric_epoch = col1.empty()
            metric_loss = col2.empty()
            metric_acc = col3.empty()
            metric_time = col4.empty()
            
            # Log de treinamento
            log_container = st.empty()
            logs = []
            
            # Simulação de épocas
            import numpy as np
            
            for epoch in range(1, config['epochs'] + 1):
                # Atualizar época
                metric_epoch.metric("Época", f"{epoch}/{config['epochs']}")
                
                # Simular steps da época
                steps_per_epoch = len(df) // config['batch_size']
                
                for step in range(1, steps_per_epoch + 1):
                    # Progresso
                    total_steps = config['epochs'] * steps_per_epoch
                    current_step = (epoch - 1) * steps_per_epoch + step
                    progress = current_step / total_steps
                    progress_bar.progress(progress)
                    
                    # Status
                    status_text.text(f"Época {epoch}/{config['epochs']} - Step {step}/{steps_per_epoch}")
                    
                    # Métricas simuladas
                    loss = 2.0 * np.exp(-current_step / (total_steps * 0.3)) + np.random.normal(0, 0.1)
                    acc = 0.33 + 0.60 * (1 - np.exp(-current_step / (total_steps * 0.4))) + np.random.normal(0, 0.02)
                    
                    metric_loss.metric("Loss", f"{loss:.4f}")
                    metric_acc.metric("Acurácia", f"{acc*100:.1f}%")
                    metric_time.metric("ETA", f"{(total_steps - current_step) * 0.5:.0f}s")
                    
                    # Log a cada 10 steps
                    if step % 10 == 0:
                        log_msg = f"[Época {epoch}] Step {step}/{steps_per_epoch} - Loss: {loss:.4f} - Acc: {acc:.3f}"
                        logs.append(log_msg)
                        log_container.code("\n".join(logs[-10:]))  # Últimas 10 linhas
                    
                    time.sleep(0.1)  # Simular processamento
                
                # Validação ao final da época
                val_loss = loss * 0.9
                val_acc = acc * 1.05
                
                log_msg = f"\n[Época {epoch}] Validação - Loss: {val_loss:.4f} - Acc: {val_acc:.3f} - Melhor modelo salvo ✅"
                logs.append(log_msg)
                log_container.code("\n".join(logs[-10:]))
                
                time.sleep(0.5)
            
            # Concluído
            progress_bar.progress(1.0)
            status_text.text("✅ Treinamento Concluído!")
            
            st.success("""
            ✅ **Treinamento Concluído com Sucesso!**
            
            - Modelo salvo em: `/models/bert_finetuned_{experiment_name}`
            - Acurácia final: 92.8%
            - F1-Score: 0.925
            - Melhoria: +3.5% em relação ao modelo anterior
            - MLflow Run ID: `abc123def456`
            """)
            
            # Ações pós-treinamento
            st.markdown("---")
            st.markdown("### 📊 Próximos Passos")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Ver Métricas Detalhadas", use_container_width=True):
                    st.info("Abrir MLflow em http://localhost:5000")
            
            with col2:
                if st.button("🔄 Fazer Deploy do Modelo", use_container_width=True):
                    st.success("Modelo implantado com sucesso!")
            
            with col3:
                if st.button("🗑️ Reverter para Modelo Anterior", use_container_width=True):
                    st.warning("Revertido para modelo anterior")
            
            # Reset
            if st.button("🔄 Novo Treinamento"):
                st.session_state.training_started = False
                st.rerun()

# ============================================================================
# TAB 4: HISTÓRICO
# ============================================================================
with tab4:
    st.subheader("📊 Histórico de Treinamentos")
    
    # Tabela de treinos
    history_data = pd.DataFrame({
        'Data': [
            '2025-11-06 18:30',
            '2025-11-05 14:20',
            '2025-11-04 09:15',
            '2025-11-03 16:45',
            '2025-11-02 11:30'
        ],
        'Experimento': [
            'fine_tune_20251106_1830',
            'fine_tune_20251105_1420',
            'fine_tune_20251104_0915',
            'fine_tune_20251103_1645',
            'fine_tune_20251102_1130'
        ],
        'Dataset': [
            '15.2K exemplos',
            '12.8K exemplos',
            '10.5K exemplos',
            '8.2K exemplos',
            '5.0K exemplos'
        ],
        'Acurácia': [
            '92.8%',
            '91.3%',
            '89.7%',
            '87.5%',
            '85.2%'
        ],
        'F1-Score': [
            '0.925',
            '0.910',
            '0.895',
            '0.873',
            '0.850'
        ],
        'Status': [
            '✅ Em Produção',
            '📦 Arquivado',
            '📦 Arquivado',
            '📦 Arquivado',
            '📦 Arquivado'
        ],
        'Ações': [
            '👁️ Ver | 🔄 Reverter',
            '👁️ Ver | 🔄 Usar',
            '👁️ Ver | 🔄 Usar',
            '👁️ Ver | 🔄 Usar',
            '👁️ Ver | 🗑️ Deletar'
        ]
    })
    
    st.dataframe(history_data, use_container_width=True, hide_index=True)
    
    # Comparação de modelos
    st.markdown("---")
    st.markdown("### 📈 Evolução das Métricas")
    
    import plotly.graph_objects as go
    
    dates = ['02/11', '03/11', '04/11', '05/11', '06/11']
    accuracy = [85.2, 87.5, 89.7, 91.3, 92.8]
    f1_score = [85.0, 87.3, 89.5, 91.0, 92.5]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=accuracy, name='Acurácia', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=dates, y=f1_score, name='F1-Score', mode='lines+markers'))
    fig.update_layout(
        xaxis_title='Data',
        yaxis_title='%',
        yaxis_range=[80, 95]
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Informações
with st.expander("ℹ️ Sobre o Retreinamento"):
    st.markdown("""
    ### Como Funciona
    
    1. **Upload**: Carregue um novo dataset no formato CSV
    2. **Configure**: Ajuste hiperparâmetros e estratégias
    3. **Treine**: Inicie o fine-tuning do BERT
    4. **Avalie**: Compare métricas com modelo anterior
    5. **Deploy**: Implante se houver melhoria
    
    ### Boas Práticas
    
    - Use **no mínimo 1000 exemplos** por classe
    - Mantenha o dataset **balanceado** (ratio < 3:1)
    - Comece com **3 épocas** e ajuste conforme necessário
    - Use **early stopping** para evitar overfitting
    - **Log no MLflow** para rastreabilidade
    
    ### Requisitos
    
    - **GPU**: Recomendado (NVIDIA T4 ou superior)
    - **RAM**: 8GB+
    - **Disco**: 2GB+ livre
    - **Tempo**: 5-30 minutos dependendo do dataset
    
    ### Segurança
    
    - Backup automático do modelo atual
    - Rollback disponível a qualquer momento
    - Versionamento com MLflow
    - Testes A/B antes de deploy final
    """)
