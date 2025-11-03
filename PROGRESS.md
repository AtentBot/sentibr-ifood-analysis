# 📊 SentiBR - Progress Tracker

Status do projeto atualizado em: **03 de Novembro de 2025**

---

## 🎯 Status Geral do Projeto

| Fase | Status | Progresso |
|------|--------|-----------|
| **FASE 0: Setup Inicial** | ✅ Completo | 100% |
| **FASE 1: Dataset e EDA** | 🟡 Em Progresso | 60% |
| **FASE 2: Fine-tuning BERT** | ⚪ Não Iniciado | 0% |
| **FASE 3: API REST** | ⚪ Não Iniciado | 0% |
| **FASE 4: Frontend** | ⚪ Não Iniciado | 0% |
| **FASE 5: Observabilidade** | ⚪ Não Iniciado | 0% |
| **FASE 6: EVAL e LLM** | ⚪ Não Iniciado | 0% |
| **FASE 7: Docker** | ⚪ Não Iniciado | 0% |
| **FASE 8: Testes** | ⚪ Não Iniciado | 0% |
| **FASE 9: Documentação** | 🟡 Em Progresso | 40% |
| **FASE 10: Demo** | ⚪ Não Iniciado | 0% |

**Legenda:**
- ✅ Completo
- 🟡 Em Progresso
- ⚪ Não Iniciado
- 🔴 Bloqueado

---

## ✅ FASE 0: SETUP INICIAL (100%)

### 0.1 Estrutura do Repositório ✅
- [x] Criar repositório GitHub
- [x] Configurar .gitignore
- [x] Criar estrutura de pastas completa
- [x] Inicializar git e fazer primeiro commit
- [x] Criar branch develop

### 0.2 Ambiente de Desenvolvimento ✅
- [x] Criar ambiente virtual Python 3.10+
- [x] Criar requirements.txt inicial
- [x] Criar requirements-dev.txt
- [x] Configurar .env.example
- [x] Criar .env local

### 0.3 Documentação Inicial ✅
- [x] Criar README.md completo
- [x] Adicionar LICENSE (MIT)
- [x] Criar CHANGELOG.md
- [x] Criar scripts de inicialização

---

## 🟡 FASE 1: DATASET E EDA (60%)

### 1.1 Coleta de Dados 🟡
- [x] Script para carregar B2W-Reviews01 do HuggingFace
- [x] Script para gerar dados sintéticos com GPT-4
- [ ] **TODO:** Executar script de coleta
- [ ] **TODO:** Gerar ~2000 reviews sintéticas iFood
- [ ] **TODO:** Combinar datasets

### 1.2 Preparação dos Dados 🟡
- [x] Script de preparação (load_data.py)
- [x] Análise de qualidade
- [x] Definir schema de dados
- [x] Criar labels de sentimento
- [x] Criar labels de aspectos (heurística)
- [ ] **TODO:** Executar pipeline completo
- [ ] **TODO:** Salvar dados processados

### 1.3 EDA ✅
- [x] Notebook de EDA criado
- [ ] **TODO:** Executar análises
- [ ] **TODO:** Gerar visualizações
- [ ] **TODO:** Documentar insights

---

## ⚪ FASE 2: MODELO - FINE-TUNING BERT (0%)

### 2.1 Data Pipeline ⚪
- [ ] Criar data_pipeline.py
- [ ] Implementar DatasetProcessor
- [ ] Text cleaning
- [ ] Tokenização BERT
- [ ] Split train/val/test
- [ ] DataLoaders PyTorch

### 2.2 Configuração do Modelo ⚪
- [ ] Escolher modelo base (neuralmind/bert-base-portuguese-cased)
- [ ] Configurar arquitetura
- [ ] Definir número de classes

### 2.3 Training Pipeline ⚪
- [ ] Criar train.py
- [ ] Training loop
- [ ] Optimizer (AdamW)
- [ ] Learning rate scheduler
- [ ] Early stopping
- [ ] Checkpoint saving
- [ ] Integração MLflow

### 2.4 Evaluation ⚪
- [ ] Criar evaluate.py
- [ ] Implementar métricas
- [ ] Confusion Matrix
- [ ] Classification Report
- [ ] Análise de erros

### 2.5 Hyperparameter Tuning ⚪
- [ ] Configurar Optuna
- [ ] Definir search space
- [ ] Executar tuning

### 2.6 Model Artifacts ⚪
- [ ] Salvar modelo fine-tuned
- [ ] Salvar tokenizer
- [ ] Criar model_info.json

---

## ⚪ FASE 3-10: PRÓXIMAS FASES

*(Detalhes serão adicionados conforme avançamos)*

---

## 🎯 Próximas Actions (Prioridade Alta)

1. **AGORA:**
   - [ ] Configurar OPENAI_API_KEY no .env
   - [ ] Executar: `python src/data/load_data.py`
   - [ ] Revisar dados no notebook EDA

2. **HOJE:**
   - [ ] Gerar dados sintéticos iFood (500 reviews)
   - [ ] Combinar com B2W dataset
   - [ ] Finalizar EDA

3. **AMANHÃ:**
   - [ ] Começar FASE 2: Training Pipeline
   - [ ] Implementar DatasetProcessor
   - [ ] Primeira rodada de fine-tuning

---

## 📈 Métricas de Progresso

| Métrica | Valor Atual | Target |
|---------|-------------|--------|
| Arquivos criados | 15 | ~50 |
| Linhas de código | ~2,200 | ~5,000 |
| Testes | 0 | 50+ |
| Cobertura | 0% | 70%+ |
| Documentação | 40% | 100% |

---

## 🚧 Blockers & Issues

Nenhum blocker no momento.

---

## 💡 Ideias & Melhorias Futuras

- [ ] Integração com Weights & Biases
- [ ] Deploy em Cloud (AWS/GCP)
- [ ] Kubernetes deployment
- [ ] CI/CD com GitHub Actions
- [ ] Multi-language support
- [ ] Real-time streaming

---

## 📝 Notas

- **Decisão:** Usar neuralmind/bert-base-portuguese-cased como base model
- **Decisão:** Começar com B2W dataset + dados sintéticos iFood
- **Decisão:** FastAPI para API, Streamlit para Frontend
- **Decisão:** Docker Compose para orquestração local

---

**Última atualização:** 03/11/2025 por SentiBR Team
