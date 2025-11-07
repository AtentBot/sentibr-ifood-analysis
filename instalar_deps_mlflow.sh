#!/bin/bash

# ============================================
# Instalação de Dependências do MLflow
# ============================================

echo "📦 Instalando dependências do MLflow..."
echo ""

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar MLflow e dependências
echo "[1/3] Instalando MLflow..."
pip install mlflow==2.9.2 --break-system-packages 2>/dev/null || pip install mlflow==2.9.2
echo "✅ MLflow instalado"
echo ""

echo "[2/3] Instalando dependências adicionais..."
pip install requests --break-system-packages 2>/dev/null || pip install requests
pip install protobuf --break-system-packages 2>/dev/null || pip install protobuf
pip install packaging --break-system-packages 2>/dev/null || pip install packaging
echo "✅ Dependências instaladas"
echo ""

echo "[3/3] Verificando instalação..."
python3 -c "import mlflow; print(f'MLflow versão: {mlflow.__version__}')"
echo ""

echo "===================================="
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo "===================================="
echo ""
echo "Agora execute:"
echo "  python3 testar_mlflow.py"
echo ""
