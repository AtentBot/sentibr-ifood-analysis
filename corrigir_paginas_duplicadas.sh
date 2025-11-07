#!/bin/bash

# ============================================
# Correção Automática - Páginas Duplicadas
# ============================================

set -e

echo "🔧 Corrigindo páginas duplicadas do Streamlit..."
echo ""

# 1. Verificar estrutura
echo "[1/5] Verificando estrutura do frontend..."
if [ ! -d "frontend" ]; then
    echo "❌ Diretório frontend/ não encontrado!"
    echo "Execute este script na raiz do projeto"
    exit 1
fi

if [ ! -d "frontend/pages" ]; then
    echo "📁 Criando diretório pages/"
    mkdir -p frontend/pages
fi
echo "✅ Estrutura OK"
echo ""

# 2. Verificar arquivos duplicados
echo "[2/5] Procurando arquivos duplicados..."
cd frontend/pages

# Listar todos os arquivos .py
echo "Arquivos encontrados:"
ls -1 *.py 2>/dev/null || echo "  (nenhum arquivo .py encontrado)"
echo ""

# Contar arquivos
FILE_COUNT=$(ls -1 *.py 2>/dev/null | wc -l)
echo "Total: $FILE_COUNT arquivos"
echo ""

# 3. Remover duplicados óbvios
echo "[3/5] Removendo duplicados..."

# Procurar variações de nomes (case-insensitive duplicates)
declare -A seen
for file in *.py 2>/dev/null; do
    # Normalizar nome (lowercase, sem acentos)
    normalized=$(echo "$file" | tr '[:upper:]' '[:lower:]' | sed 's/ç/c/g; s/ã/a/g; s/á/a/g; s/é/e/g; s/í/i/g; s/ó/o/g; s/ú/u/g')
    
    if [[ -n "${seen[$normalized]}" ]]; then
        echo "⚠️  Duplicado encontrado: $file (similar a ${seen[$normalized]})"
        echo "   Removendo: $file"
        rm "$file"
    else
        seen[$normalized]="$file"
    fi
done

echo "✅ Duplicados removidos"
echo ""

# 4. Renomear arquivos para padrão correto
echo "[4/5] Renomeando arquivos..."

# Função para renomear
rename_if_exists() {
    local old_pattern="$1"
    local new_name="$2"
    
    # Procurar arquivo com pattern (case-insensitive)
    for file in $(ls -1 | grep -i "$old_pattern" 2>/dev/null | head -1); do
        if [ -f "$file" ] && [ "$file" != "$new_name" ]; then
            echo "  $file → $new_name"
            mv "$file" "$new_name"
            return 0
        fi
    done
    return 1
}

# Renomear cada página
rename_if_exists "dashboard" "1_📊_Dashboard.py" || echo "  Dashboard: não encontrado"
rename_if_exists "analise.*individual\|individual" "2_🔍_Analise_Individual.py" || echo "  Análise Individual: não encontrado"
rename_if_exists "analise.*lote\|lote\|batch" "3_📦_Analise_Lote.py" || echo "  Análise Lote: não encontrado"
rename_if_exists "avaliacao\|evaluation" "4_🔎_Avaliacao.py" || echo "  Avaliação: não encontrado"
rename_if_exists "comparacao\|comparison" "5_⚔️_Comparacao.py" || echo "  Comparação: não encontrado"
rename_if_exists "llm.*judge\|judge" "6_🤖_LLM_Judge.py" || echo "  LLM Judge: não encontrado"
rename_if_exists "monitoramento\|monitoring" "7_📈_Monitoramento.py" || echo "  Monitoramento: não encontrado"

echo "✅ Arquivos renomeados"
echo ""

# 5. Verificar resultado
echo "[5/5] Verificando resultado..."
cd ../..

echo ""
echo "===================================="
echo "📁 Estrutura Final:"
echo "===================================="
echo "frontend/"
echo "├── app.py"
tree -L 2 frontend/ 2>/dev/null || (
    echo "├── requirements.txt"
    echo "└── pages/"
    cd frontend/pages && ls -1 *.py 2>/dev/null | sed 's/^/    ├── /' || echo "    (vazio)"
)
echo ""

# Contar páginas finais
FINAL_COUNT=$(ls -1 frontend/pages/*.py 2>/dev/null | wc -l)
echo "Total de páginas: $FINAL_COUNT"
echo ""

if [ $FINAL_COUNT -eq 7 ]; then
    echo "✅ Estrutura correta! (7 páginas)"
else
    echo "⚠️  Esperado 7 páginas, encontrado $FINAL_COUNT"
    echo ""
    echo "Páginas que devem existir:"
    echo "  1. 1_📊_Dashboard.py"
    echo "  2. 2_🔍_Analise_Individual.py"
    echo "  3. 3_📦_Analise_Lote.py"
    echo "  4. 4_🔎_Avaliacao.py"
    echo "  5. 5_⚔️_Comparacao.py"
    echo "  6. 6_🤖_LLM_Judge.py"
    echo "  7. 7_📈_Monitoramento.py"
fi

echo ""
echo "===================================="
echo "✅ Correção Concluída!"
echo "===================================="
echo ""
echo "Próximos passos:"
echo "1. Rebuild do frontend:"
echo "   docker-compose build --no-cache frontend"
echo ""
echo "2. Iniciar:"
echo "   docker-compose up -d frontend"
echo ""
echo "3. Ver logs:"
echo "   docker logs -f sentibr-frontend"
echo ""
