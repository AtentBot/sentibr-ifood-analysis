#!/bin/bash

# ============================================
# Script de Instalação da Correção BERT
# Automatiza a instalação do arquivo corrigido
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  SentiBR - Instalação da Correção BERT${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Verificar se arquivo corrigido existe
if [ ! -f "4_🔎_Avaliação_CORRIGIDO.py" ]; then
    echo -e "${RED}❌ Erro: Arquivo 4_🔎_Avaliação_CORRIGIDO.py não encontrado!${NC}"
    echo -e "${YELLOW}Baixe o arquivo primeiro e execute este script no mesmo diretório.${NC}"
    exit 1
fi

# Verificar se diretório frontend/pages existe
if [ ! -d "frontend/pages" ]; then
    echo -e "${RED}❌ Erro: Diretório frontend/pages não encontrado!${NC}"
    echo -e "${YELLOW}Execute este script no diretório raiz do projeto.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Pré-instalação:${NC}"
echo ""

# 1. Backup
echo -e "${BLUE}[1/4]${NC} Fazendo backup do arquivo original..."

if [ -f "frontend/pages/4_🔎_Avaliação.py" ]; then
    BACKUP_NAME="4_🔎_Avaliação_backup_$(date +%Y%m%d_%H%M%S).py"
    cp "frontend/pages/4_🔎_Avaliação.py" "frontend/pages/$BACKUP_NAME"
    echo -e "${GREEN}✅ Backup criado: $BACKUP_NAME${NC}"
else
    echo -e "${YELLOW}⚠️  Arquivo original não encontrado (primeira instalação)${NC}"
fi

echo ""

# 2. Copiar arquivo corrigido
echo -e "${BLUE}[2/4]${NC} Instalando arquivo corrigido..."
cp "4_🔎_Avaliação_CORRIGIDO.py" "frontend/pages/4_🔎_Avaliação.py"
echo -e "${GREEN}✅ Arquivo instalado com sucesso!${NC}"
echo ""

# 3. Verificar instalação
echo -e "${BLUE}[3/4]${NC} Verificando instalação..."

if grep -q "VERSÃO CORRIGIDA" "frontend/pages/4_🔎_Avaliação.py"; then
    echo -e "${GREEN}✅ Instalação verificada (versão corrigida detectada)${NC}"
else
    echo -e "${RED}❌ Erro na verificação!${NC}"
    exit 1
fi

if grep -q "fix_data_format" "frontend/pages/4_🔎_Avaliação.py"; then
    echo -e "${GREEN}✅ Função de correção encontrada${NC}"
else
    echo -e "${RED}❌ Função de correção não encontrada!${NC}"
    exit 1
fi

echo ""

# 4. Verificar se Streamlit está rodando
echo -e "${BLUE}[4/4]${NC} Verificando Streamlit..."

if pgrep -f "streamlit run" > /dev/null; then
    echo -e "${YELLOW}⚠️  Streamlit está rodando${NC}"
    echo -e "${YELLOW}   Você precisa reiniciar o Streamlit para aplicar as mudanças.${NC}"
    echo ""
    read -p "Deseja que eu tente reiniciar? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${BLUE}Parando Streamlit...${NC}"
        pkill -f "streamlit run"
        sleep 2
        echo -e "${GREEN}✅ Streamlit parado${NC}"
        echo -e "${BLUE}Iniciando Streamlit...${NC}"
        cd frontend && nohup streamlit run app.py > /dev/null 2>&1 &
        sleep 3
        echo -e "${GREEN}✅ Streamlit reiniciado${NC}"
    fi
else
    echo -e "${YELLOW}ℹ️  Streamlit não está rodando${NC}"
    read -p "Deseja iniciar o Streamlit agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${BLUE}Iniciando Streamlit...${NC}"
        cd frontend && nohup streamlit run app.py > /dev/null 2>&1 &
        sleep 3
        echo -e "${GREEN}✅ Streamlit iniciado${NC}"
    fi
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ Instalação concluída com sucesso!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo ""
echo "1. Acesse: ${BLUE}http://localhost:8501${NC}"
echo "2. Vá em: ${BLUE}🔎 Avaliação${NC}"
echo "3. Faça upload de um CSV"
echo "4. Execute a avaliação"
echo ""
echo -e "${GREEN}✅ O erro 'text' não deve mais aparecer!${NC}"
echo ""
echo -e "${YELLOW}📚 Arquivos úteis:${NC}"
echo "- ${BLUE}exemplo_teste.csv${NC} - CSV para teste"
echo "- ${BLUE}INSTALACAO_CORRECAO.md${NC} - Documentação"
echo "- ${BLUE}RESUMO_COMPLETO.md${NC} - Resumo geral"
echo ""
echo -e "${GREEN}Boa sorte! 🚀${NC}"
