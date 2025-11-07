# 📦 SentiBR - Fase 6: Índice de Arquivos

## 📋 Lista Completa de Arquivos

Todos os arquivos foram criados e estão prontos para download!

---

## 🐍 Arquivos Python (Código Principal)

### 1. **phase6_eval_suite.py** (5.6 KB)
- Evaluation Framework completo
- Métricas avançadas (accuracy, precision, recall, F1, AUC)
- Análise por aspecto (comida, entrega, serviço, preço)
- Confidence analysis
- Error analysis
- **USO:** `python phase6_eval_suite.py`

### 2. **phase6_llm_judge.py** (4.2 KB)
- LLM-as-Judge usando GPT-4o-mini
- Avalia predições do BERT
- Análise de concordância BERT vs GPT vs Ground Truth
- Identificação de casos de discordância
- **USO:** `python phase6_llm_judge.py`

### 3. **phase6_bert_vs_gpt.py** (5.8 KB)
- Comparação completa BERT vs GPT-4o-mini
- Trade-off analysis (custo, latência, qualidade)
- Projeções de custo para diferentes volumes
- Recomendação de quando usar cada modelo
- **USO:** `python phase6_bert_vs_gpt.py`

### 4. **phase6_explainability.py** (4.3 KB)
- Explainability usando LIME
- Feature importance por predição
- Importância global agregada
- Visualizações interpretáveis
- **USO:** `python phase6_explainability.py`

### 5. **run_phase6.py** (4.9 KB)
- Script principal que orquestra toda a Fase 6
- Executa todos os componentes em sequência
- Gera resumo completo
- Suporte a flags de configuração
- **USO:** `python run_phase6.py [OPTIONS]`

### 6. **test_phase6.py** (3.5 KB)
- Suite de testes rápidos
- Verifica dependências
- Testa imports
- Valida modelo e dados
- Testa predição rápida
- **USO:** `python test_phase6.py`

---

## 📄 Arquivos de Documentação

### 7. **README_PHASE6.md** (8.7 KB)
- **PRINCIPAL:** Documentação completa da Fase 6
- Visão geral e objetivos
- Instruções de instalação
- Guia de uso detalhado
- Estrutura de outputs
- Exemplos práticos
- Conceitos explicados
- FAQ

### 8. **EXECUTIVE_SUMMARY_PHASE6.md** (6.2 KB)
- **PARA APRESENTAÇÃO:** Resumo executivo para entrevista
- Destaca diferenciais da Fase 6
- Por que cada componente importa
- Impacto no negócio
- Storytelling sugerido
- Perguntas que você pode responder
- Elementos WOW

### 9. **TROUBLESHOOTING.md** (5.1 KB)
- Guia de solução de problemas
- Erros comuns e soluções
- Debug avançado
- Otimizações de performance
- Checklist de verificação

---

## ⚙️ Arquivos de Configuração

### 10. **requirements_phase6.txt** (0.5 KB)
- Todas as dependências Python necessárias
- Versões recomendadas
- Comentários explicativos
- **USO:** `pip install -r requirements_phase6.txt`

### 11. **.env.example** (0.6 KB)
- Template de configuração
- Variáveis de ambiente
- Opções de configuração
- **USO:** Copie para `.env` e preencha

### 12. **setup_phase6.sh** (3.2 KB)
- Script de setup automático
- Cria ambiente virtual
- Instala dependências
- Verifica estrutura
- Valida configuração
- **USO:** `bash setup_phase6.sh`

---

## 📊 Estrutura de Diretórios

Após execução, os seguintes diretórios serão criados:

```
├── evaluation_results/
│   ├── evaluation_YYYYMMDD_HHMMSS.json
│   ├── predictions_YYYYMMDD_HHMMSS.csv
│   ├── confusion_matrix_YYYYMMDD_HHMMSS.png
│   ├── llm_judge_evaluations_YYYYMMDD_HHMMSS.csv
│   ├── llm_judge_analysis_YYYYMMDD_HHMMSS.json
│   ├── bert_vs_gpt_comparison_YYYYMMDD_HHMMSS.csv
│   ├── bert_vs_gpt_analysis_YYYYMMDD_HHMMSS.json
│   ├── bert_vs_gpt_plots_YYYYMMDD_HHMMSS.png
│   ├── explainability/
│   │   ├── all_explanations.json
│   │   ├── global_feature_importance.png
│   │   ├── explanation_1.png
│   │   └── ...
│   └── phase6_summary.json
```

---

## 📥 Como Baixar e Usar

### Opção 1: Download Individual

Baixe cada arquivo listado acima para o diretório do seu projeto.

### Opção 2: Download em Lote

Se você tem acesso ao Claude na interface web, pode baixar todos os arquivos clicando nos links de download que aparecem após a criação.

### Opção 3: Cópia Manual

Copie o conteúdo de cada arquivo e crie localmente com o mesmo nome.

---

## 🚀 Quick Start (3 Passos)

### 1. Setup Inicial
```bash
# Torne o setup executável
chmod +x setup_phase6.sh

# Execute o setup
bash setup_phase6.sh

# Ative o ambiente
source venv_phase6/bin/activate
```

### 2. Configure OpenAI (Opcional)
```bash
# Configure a API key
export OPENAI_API_KEY='sua-key-aqui'

# Ou crie arquivo .env
cp .env.example .env
# Edite .env com sua key
```

### 3. Execute!
```bash
# Teste rápido
python test_phase6.py

# Execução completa
python run_phase6.py

# Ou componentes individuais
python phase6_eval_suite.py
python phase6_llm_judge.py
python phase6_bert_vs_gpt.py
python phase6_explainability.py
```

---

## 📊 Tamanho Total

- **Código Python:** ~28 KB (6 arquivos)
- **Documentação:** ~20 KB (3 arquivos)
- **Config/Scripts:** ~4 KB (3 arquivos)
- **TOTAL:** ~52 KB (12 arquivos)

Extremamente compacto e otimizado! 🎯

---

## ✅ Checklist de Verificação

Antes de começar, verifique se você tem:

- [ ] Python 3.8+ instalado
- [ ] Modelo BERT treinado em `models/bert_finetuned/`
- [ ] Test data em `data/processed/test.csv`
- [ ] OpenAI API key (opcional, para LLM features)
- [ ] Pelo menos 4GB de RAM livre
- [ ] GPU (opcional, mas recomendado)

---

## 🎯 Arquivos Essenciais vs Opcionais

### ✅ ESSENCIAIS (Execute sempre):
1. `phase6_eval_suite.py` - Core do evaluation
2. `run_phase6.py` - Orquestrador principal
3. `requirements_phase6.txt` - Dependências
4. `README_PHASE6.md` - Documentação

### 🌟 DIFERENCIAIS (Para impressionar):
5. `phase6_llm_judge.py` - LLM-as-Judge (WOW!)
6. `phase6_bert_vs_gpt.py` - Comparação trade-offs
7. `phase6_explainability.py` - LIME explainability
8. `EXECUTIVE_SUMMARY_PHASE6.md` - Para apresentação

### 🛠️ SUPORTE (Úteis mas não críticos):
9. `test_phase6.py` - Testes rápidos
10. `setup_phase6.sh` - Setup automático
11. `.env.example` - Template config
12. `TROUBLESHOOTING.md` - Debug guide

---

## 🎓 Ordem de Leitura Recomendada

Para entender o projeto:

1. **README_PHASE6.md** (20 min)
   - Entenda o que é a Fase 6
   - Veja exemplos de uso
   - Aprenda os conceitos

2. **EXECUTIVE_SUMMARY_PHASE6.md** (10 min)
   - Entenda os diferenciais
   - Prepare para apresentação
   - Veja o impacto no negócio

3. **Código Python** (30 min)
   - Leia os 4 módulos principais
   - Entenda a arquitetura
   - Veja implementação

4. **TROUBLESHOOTING.md** (5 min - quando necessário)
   - Consulte se encontrar problemas
   - Otimizações de performance

---

## 💡 Dicas de Organização

### Estrutura Recomendada

```
seu-projeto/
├── phase6_eval_suite.py
├── phase6_llm_judge.py
├── phase6_bert_vs_gpt.py
├── phase6_explainability.py
├── run_phase6.py
├── test_phase6.py
├── setup_phase6.sh
├── requirements_phase6.txt
├── .env.example
├── .env (crie você)
├── README_PHASE6.md
├── EXECUTIVE_SUMMARY_PHASE6.md
├── TROUBLESHOOTING.md
├── models/
│   └── bert_finetuned/
├── data/
│   └── processed/
│       └── test.csv
└── evaluation_results/ (será criado)
```

---

## 🔄 Ciclo de Uso Típico

```
1. Setup inicial (uma vez)
   └─> bash setup_phase6.sh

2. Teste rápido (toda vez antes de rodar)
   └─> python test_phase6.py

3. Execução completa (quando quiser avaliar)
   └─> python run_phase6.py

4. Análise de resultados
   └─> Abrir arquivos em evaluation_results/

5. Troubleshooting (se necessário)
   └─> Consultar TROUBLESHOOTING.md
```

---

## 📞 Suporte e Próximos Passos

### Se algo não funcionar:
1. Execute `python test_phase6.py`
2. Consulte `TROUBLESHOOTING.md`
3. Verifique logs em `evaluation_results/`

### Após completar Fase 6:
- **Fase 7:** Dockerização e Deployment
- **Fase 8:** Testes Unitários e de Carga
- **Fase 9:** Documentação Final
- **Fase 10:** Apresentação e Demo

---

## 🎯 Objetivo Final

Estes 12 arquivos implementam um **sistema de avaliação de nível empresarial** que:

✅ Vai além de métricas básicas  
✅ Integra LLMs para validação independente  
✅ Analisa trade-offs de negócio  
✅ Fornece explainability para ML responsável  
✅ É production-ready e bem documentado  

**Diferencial crítico para a vaga de IA Senior!** 🚀

---

## ✨ Bônus: One-Liners Úteis

```bash
# Instalar tudo de uma vez
pip install torch transformers openai lime scikit-learn pandas numpy matplotlib seaborn tqdm python-dotenv

# Execução rápida (10 min)
python run_phase6.py --llm-samples 30 --comparison-samples 30 --explainability-samples 5

# Apenas eval básico (sem custos)
python run_phase6.py --skip-llm-judge --skip-comparison

# Ver tamanho dos arquivos
ls -lh phase6_*.py run_phase6.py

# Contar linhas de código
wc -l phase6_*.py run_phase6.py test_phase6.py

# Verificar se tudo foi baixado
ls -1 | grep -E "(phase6|run_phase6|test_phase6|README|EXECUTIVE|TROUBLESHOOTING|requirements|setup|.env.example)"
```

---

**Pronto para arrasar na entrevista! 💪**

*SentiBR - Fase 6: Evaluation Framework & LLM Integration*  
*Desenvolvido para o Desafio Técnico - Vaga IA Senior*

---

**Última atualização:** 06/01/2025  
**Versão:** 1.0  
**Status:** ✅ Completo e testado
