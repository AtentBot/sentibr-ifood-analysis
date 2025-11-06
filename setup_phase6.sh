#!/bin/bash

# SentiBR - Phase 6 Setup Script
# Configura ambiente e verifica dependências

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║       🚀 SentiBR - Fase 6: Setup & Verification 🚀          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para printar com cor
print_status() {
    echo -e "${2}${1}${NC}"
}

# 1. Verifica Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Verificando Python..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v python3 &> /dev/null; then
    print_status "❌ Python 3 não encontrado!" "$RED"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "✅ Python $PYTHON_VERSION encontrado" "$GREEN"

# 2. Cria/ativa ambiente virtual
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Configurando ambiente virtual..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "venv_phase6" ]; then
    print_status "📦 Criando ambiente virtual..." "$BLUE"
    python3 -m venv venv_phase6
    print_status "✅ Ambiente virtual criado" "$GREEN"
else
    print_status "✅ Ambiente virtual já existe" "$GREEN"
fi

# Ativa ambiente
source venv_phase6/bin/activate

# 3. Atualiza pip
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Atualizando pip..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pip install --upgrade pip setuptools wheel > /dev/null 2>&1
print_status "✅ pip atualizado" "$GREEN"

# 4. Instala dependências
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Instalando dependências..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "requirements_phase6.txt" ]; then
    print_status "📦 Instalando pacotes do requirements_phase6.txt..." "$BLUE"
    pip install -r requirements_phase6.txt
    print_status "✅ Dependências instaladas" "$GREEN"
else
    print_status "⚠️  requirements_phase6.txt não encontrado" "$YELLOW"
    print_status "   Instalando pacotes essenciais manualmente..." "$YELLOW"
    
    pip install torch transformers openai lime scikit-learn pandas numpy matplotlib seaborn tqdm python-dotenv
fi

# 5. Verifica instalação
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Verificando instalação..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Lista de pacotes essenciais
packages=("torch" "transformers" "openai" "lime" "sklearn" "pandas" "numpy" "matplotlib" "seaborn" "tqdm")

all_installed=true
for package in "${packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        print_status "  ✅ $package" "$GREEN"
    else
        print_status "  ❌ $package não instalado" "$RED"
        all_installed=false
    fi
done

if [ "$all_installed" = false ]; then
    print_status "\n⚠️  Alguns pacotes faltando. Execute:" "$YELLOW"
    print_status "pip install -r requirements_phase6.txt" "$YELLOW"
    exit 1
fi

# 6. Verifica estrutura de diretórios
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Verificando estrutura de diretórios..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cria diretórios necessários
mkdir -p evaluation_results
mkdir -p evaluation_results/explainability
mkdir -p data/processed
mkdir -p models

print_status "✅ Diretórios criados/verificados" "$GREEN"

# 7. Verifica arquivos necessários
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Verificando arquivos necessários..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

files_ok=true

if [ -f "phase6_eval_suite.py" ]; then
    print_status "  ✅ phase6_eval_suite.py" "$GREEN"
else
    print_status "  ❌ phase6_eval_suite.py não encontrado" "$RED"
    files_ok=false
fi

if [ -f "phase6_llm_judge.py" ]; then
    print_status "  ✅ phase6_llm_judge.py" "$GREEN"
else
    print_status "  ❌ phase6_llm_judge.py não encontrado" "$RED"
    files_ok=false
fi

if [ -f "phase6_bert_vs_gpt.py" ]; then
    print_status "  ✅ phase6_bert_vs_gpt.py" "$GREEN"
else
    print_status "  ❌ phase6_bert_vs_gpt.py não encontrado" "$RED"
    files_ok=false
fi

if [ -f "phase6_explainability.py" ]; then
    print_status "  ✅ phase6_explainability.py" "$GREEN"
else
    print_status "  ❌ phase6_explainability.py não encontrado" "$RED"
    files_ok=false
fi

if [ -f "run_phase6.py" ]; then
    print_status "  ✅ run_phase6.py" "$GREEN"
else
    print_status "  ❌ run_phase6.py não encontrado" "$RED"
    files_ok=false
fi

if [ "$files_ok" = false ]; then
    print_status "\n⚠️  Alguns arquivos Python faltando" "$YELLOW"
    print_status "   Baixe todos os arquivos da Fase 6" "$YELLOW"
fi

# 8. Verifica modelo BERT
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  Verificando modelo BERT..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "models/bert_finetuned" ]; then
    print_status "✅ Modelo BERT encontrado em models/bert_finetuned" "$GREEN"
else
    print_status "⚠️  Modelo BERT não encontrado" "$YELLOW"
    print_status "   Execute o treinamento primeiro (Fase 2)" "$YELLOW"
fi

# 9. Verifica test data
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  Verificando test data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "data/processed/test.csv" ]; then
    num_lines=$(wc -l < data/processed/test.csv)
    print_status "✅ Test data encontrado ($num_lines linhas)" "$GREEN"
else
    print_status "⚠️  Test data não encontrado" "$YELLOW"
    print_status "   Execute a preparação de dados primeiro (Fase 1)" "$YELLOW"
fi

# 10. Verifica OpenAI API Key
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔟 Verificando OpenAI API Key..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -n "$OPENAI_API_KEY" ]; then
    key_preview="${OPENAI_API_KEY:0:10}..."
    print_status "✅ OPENAI_API_KEY configurada ($key_preview)" "$GREEN"
elif [ -f ".env" ] && grep -q "OPENAI_API_KEY" .env; then
    print_status "✅ OPENAI_API_KEY encontrada no .env" "$GREEN"
else
    print_status "⚠️  OPENAI_API_KEY não encontrada" "$YELLOW"
    print_status "\n   Para usar LLM-as-Judge e comparação BERT vs GPT:" "$YELLOW"
    print_status "   export OPENAI_API_KEY='sua-key-aqui'" "$YELLOW"
    print_status "\n   Ou crie arquivo .env com:" "$YELLOW"
    print_status "   OPENAI_API_KEY=sua-key-aqui" "$YELLOW"
fi

# Sumário final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 SUMÁRIO DO SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$all_installed" = true ] && [ "$files_ok" = true ]; then
    print_status "\n✅ Setup concluído com sucesso!" "$GREEN"
    print_status "\n🚀 Próximos passos:" "$BLUE"
    print_status "\n   1. Ative o ambiente virtual:" "$NC"
    print_status "      source venv_phase6/bin/activate" "$NC"
    print_status "\n   2. Configure OpenAI API Key (se necessário):" "$NC"
    print_status "      export OPENAI_API_KEY='sua-key-aqui'" "$NC"
    print_status "\n   3. Execute a Fase 6:" "$NC"
    print_status "      python run_phase6.py" "$NC"
    print_status "\n   Ou execute componentes individuais:" "$NC"
    print_status "      python phase6_eval_suite.py" "$NC"
    print_status "      python phase6_llm_judge.py" "$NC"
    print_status "      python phase6_bert_vs_gpt.py" "$NC"
    print_status "      python phase6_explainability.py" "$NC"
else
    print_status "\n⚠️  Setup completado com avisos" "$YELLOW"
    print_status "   Verifique os itens marcados com ❌ ou ⚠️ acima" "$YELLOW"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Documentação completa em: README_PHASE6.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
