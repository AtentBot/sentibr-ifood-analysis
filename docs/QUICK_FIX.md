# 🔧 Quick Fix - Caminhos Absolutos

## Problema Identificado

Os arquivos originais usam caminhos absolutos `/home/claude/` que não existem no seu sistema.

## ✅ Solução Rápida

### 1. Usar start_api_fixed.py

```bash
# Ao invés de:
python start_api.py --reload

# Use:
python start_api_fixed.py --reload
```

### 2. Ajustar caminho do modelo

Edite `src/api/inference.py` linha 53:

**Antes:**
```python
model_path = Path("/home/claude/models/bert_finetuned")
```

**Depois (use o caminho do SEU modelo):**
```python
# Opção 1: Caminho relativo ao projeto
model_path = Path(__file__).parent.parent.parent / "models" / "bert_finetuned"

# Opção 2: Caminho absoluto do seu sistema
model_path = Path("/mnt/e/softplan/sentibr-ifood-analysis/models/bert_finetuned")

# Opção 3: Usar variável de ambiente (melhor)
import os
model_path = Path(os.getenv("MODEL_PATH", "models/bert_finetuned"))
```

### 3. Configurar .env (Recomendado)

Crie `.env` no diretório raiz:

```env
MODEL_PATH=/mnt/e/softplan/sentibr-ifood-analysis/models/bert_finetuned
```

E ajuste `src/api/inference.py` para usar:

```python
import os
model_path = Path(os.getenv("MODEL_PATH", "models/bert_finetuned"))
```

---

## 🚀 Solução Completa (3 passos)

### 1️⃣ Criar .env

```bash
cat > .env << 'ENVEOF'
# Model Configuration
MODEL_PATH=./models/bert_finetuned

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVEOF
```

### 2️⃣ Modificar src/api/inference.py

Abra o arquivo e modifique a linha 53:

```python
# Adicione no topo do arquivo
import os
from dotenv import load_dotenv

# No método _load_model(), linha ~53
def _load_model(self):
    """Load model and tokenizer from disk"""
    try:
        logger.info("Loading model and tokenizer...")
        start_time = time.time()
        
        # Determine device
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self._device}")
        
        # MODIFICAR AQUI - Model path
        # Carregar .env
        load_dotenv()
        
        # Tentar múltiplos caminhos
        model_path_env = os.getenv("MODEL_PATH")
        possible_paths = [
            Path(model_path_env) if model_path_env else None,
            Path(__file__).parent.parent.parent / "models" / "bert_finetuned",
            Path("models/bert_finetuned"),
            Path("../models/bert_finetuned"),
            Path("/mnt/e/softplan/sentibr-ifood-analysis/models/bert_finetuned"),
        ]
        
        model_path = None
        for path in possible_paths:
            if path and path.exists():
                model_path = path
                break
        
        if not model_path:
            raise FileNotFoundError(
                f"Model not found. Tried:\n" + 
                "\n".join([f"  - {p}" for p in possible_paths if p])
            )
        
        logger.info(f"Loading model from: {model_path}")
        # ... resto do código continua igual
```

### 3️⃣ Instalar python-dotenv

```bash
pip install python-dotenv
```

### 4️⃣ Iniciar a API

```bash
python start_api_fixed.py --reload
```

---

## 🔍 Debug

Se ainda tiver problemas, verifique:

```bash
# 1. Verificar se o modelo existe
ls -la models/bert_finetuned/

# 2. Verificar caminho absoluto
pwd
# Anote o caminho completo

# 3. Testar import
python -c "from pathlib import Path; print(Path('.').absolute())"

# 4. Verificar dependências
pip list | grep -E "fastapi|uvicorn|transformers|torch"
```

---

## 📝 Modificações Necessárias

### Arquivo: src/api/inference.py

**Linhas 52-58** - Modificar caminho do modelo

### Arquivo: src/api/middleware.py (opcional)

Se usar feedback, linha ~232 - Modificar caminho do feedback:

```python
# Antes
feedback_dir = Path("/home/claude/data/feedback")

# Depois
feedback_dir = Path(__file__).parent.parent.parent / "data" / "feedback"
# ou
feedback_dir = Path("data/feedback")
```

---

## ✅ Verificação Final

```bash
# 1. Verificar estrutura
ls -la

# Deve ter:
# - src/api/
# - models/bert_finetuned/
# - .env (opcional)
# - start_api_fixed.py

# 2. Testar
python start_api_fixed.py --skip-checks --reload
```

---

## 💡 Alternativa Rápida (sem modificar código)

Se não quiser modificar o código, crie um link simbólico:

```bash
# Linux/Mac
sudo mkdir -p /home/claude
sudo ln -s $(pwd)/models /home/claude/models
sudo ln -s $(pwd)/logs /home/claude/logs
sudo ln -s $(pwd)/data /home/claude/data

# Windows (WSL)
# Execute como administrador
mkdir -p /home/claude
ln -s /mnt/e/softplan/sentibr-ifood-analysis/models /home/claude/models
ln -s /mnt/e/softplan/sentibr-ifood-analysis/logs /home/claude/logs
ln -s /mnt/e/softplan/sentibr-ifood-analysis/data /home/claude/data
```

---

## 🆘 Ainda com Problemas?

Se nada funcionar, use o caminho absoluto direto:

1. Descubra seu caminho:
```bash
pwd
# Exemplo: /mnt/e/softplan/sentibr-ifood-analysis
```

2. Edite `src/api/inference.py` linha 53:
```python
model_path = Path("/mnt/e/softplan/sentibr-ifood-analysis/models/bert_finetuned")
```

3. Execute:
```bash
python start_api_fixed.py --reload
```

---

## ✅ Checklist

- [ ] Baixei start_api_fixed.py
- [ ] Instalei python-dotenv: `pip install python-dotenv`
- [ ] Criei .env com MODEL_PATH correto
- [ ] Modifiquei src/api/inference.py
- [ ] Testei: `python start_api_fixed.py --reload`
- [ ] API iniciou com sucesso! 🎉

---

**Depois que funcionar, você pode usar normalmente!**
