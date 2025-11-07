# ⚠️ LEIA-ME PRIMEIRO - Correção de Caminhos

## 🔴 Problema Identificado

Você encontrou um erro de **PermissionError** porque os arquivos originais usam caminhos absolutos `/home/claude/` que não existem no seu sistema.

---

## ✅ SOLUÇÃO RÁPIDA (2 minutos)

### 📥 1. Baixe o Arquivo Corrigido

**[start_api_fixed.py](computer:///mnt/user-data/outputs/fase3_api_rest/start_api_fixed.py)** ⬅️ BAIXE ESTE

Este arquivo já corrige o problema de caminhos.

### 🔧 2. Modifique src/api/inference.py

Abra `src/api/inference.py` e na **linha 53**, substitua:

```python
# ❌ ANTES (linha 53)
model_path = Path("/home/claude/models/bert_finetuned")
```

Por:

```python
# ✅ DEPOIS (linha 53)
# Tentar múltiplos caminhos
possible_paths = [
    Path(__file__).parent.parent.parent / "models" / "bert_finetuned",
    Path("models/bert_finetuned"),
    Path("../models/bert_finetuned"),
]

model_path = None
for path in possible_paths:
    if path.exists():
        model_path = path
        break

if not model_path:
    raise FileNotFoundError(
        f"Model not found. Please ensure the model is trained."
    )
```

### 🚀 3. Executar

```bash
python start_api_fixed.py --reload
```

**Pronto!** A API deve iniciar normalmente. ✅

---

## 📚 DOCUMENTAÇÃO COMPLETA

Para instruções detalhadas, consulte:

**[QUICK_FIX.md](computer:///mnt/user-data/outputs/fase3_api_rest/QUICK_FIX.md)** ⬅️ Guia Completo de Correção

---

## 🎯 ALTERNATIVA: Link Simbólico (WSL)

Se você está no WSL e não quer modificar código:

```bash
# Criar diretórios
sudo mkdir -p /home/claude

# Criar links simbólicos
sudo ln -s /mnt/e/softplan/sentibr-ifood-analysis/models /home/claude/models
sudo ln -s /mnt/e/softplan/sentibr-ifood-analysis/logs /home/claude/logs
sudo ln -s /mnt/e/softplan/sentibr-ifood-analysis/data /home/claude/data

# Agora pode usar o start_api.py original
python start_api.py --reload
```

---

## 📦 TODOS OS DOWNLOADS

### ⚡ Arquivos de Correção

1. **[start_api_fixed.py](computer:///mnt/user-data/outputs/fase3_api_rest/start_api_fixed.py)** - Script corrigido
2. **[QUICK_FIX.md](computer:///mnt/user-data/outputs/fase3_api_rest/QUICK_FIX.md)** - Guia completo

### 📖 Documentação

3. **[README.md](computer:///mnt/user-data/outputs/fase3_api_rest/README.md)** - Overview
4. **[INSTALL.md](computer:///mnt/user-data/outputs/fase3_api_rest/INSTALL.md)** - Instalação
5. **[INDEX.md](computer:///mnt/user-data/outputs/fase3_api_rest/INDEX.md)** - Índice completo
6. **[DOWNLOADS.md](computer:///mnt/user-data/outputs/fase3_api_rest/DOWNLOADS.md)** - Lista de downloads

### 💻 Código Fonte (src/api/)

7. **[src/api/__init__.py](computer:///mnt/user-data/outputs/fase3_api_rest/src/api/__init__.py)**
8. **[src/api/main.py](computer:///mnt/user-data/outputs/fase3_api_rest/src/api/main.py)** - FastAPI app
9. **[src/api/models.py](computer:///mnt/user-data/outputs/fase3_api_rest/src/api/models.py)** - Pydantic models
10. **[src/api/inference.py](computer:///mnt/user-data/outputs/fase3_api_rest/src/api/inference.py)** - ⚠️ MODIFICAR linha 53
11. **[src/api/middleware.py](computer:///mnt/user-data/outputs/fase3_api_rest/src/api/middleware.py)**

### 📚 Documentação Técnica (docs/)

12. **[docs/QUICK_START.md](computer:///mnt/user-data/outputs/fase3_api_rest/docs/QUICK_START.md)**
13. **[docs/API.md](computer:///mnt/user-data/outputs/fase3_api_rest/docs/API.md)**
14. **[docs/FASE_3_README.md](computer:///mnt/user-data/outputs/fase3_api_rest/docs/FASE_3_README.md)**
15. **[docs/FASE_3_SUMMARY.md](computer:///mnt/user-data/outputs/fase3_api_rest/docs/FASE_3_SUMMARY.md)**

### 🔧 Scripts e Exemplos

16. **[test_api.py](computer:///mnt/user-data/outputs/fase3_api_rest/test_api.py)** - Testes
17. **[examples/api_client.py](computer:///mnt/user-data/outputs/fase3_api_rest/examples/api_client.py)** - Cliente Python
18. **[requirements.txt](computer:///mnt/user-data/outputs/fase3_api_rest/requirements.txt)** - Dependências
19. **[.env.example](computer:///mnt/user-data/outputs/fase3_api_rest/.env.example)** - Configuração

---

## ✅ CHECKLIST RÁPIDO

1. [ ] Baixei **start_api_fixed.py**
2. [ ] Modifiquei **src/api/inference.py** linha 53
3. [ ] Executei: `python start_api_fixed.py --reload`
4. [ ] API iniciou sem erros ✅
5. [ ] Acessei http://localhost:8000/docs ✅

---

## 🆘 AINDA COM PROBLEMAS?

### Debug Básico

```bash
# 1. Verificar onde você está
pwd
# Deve estar em: /mnt/e/softplan/sentibr-ifood-analysis

# 2. Verificar se modelo existe
ls -la models/bert_finetuned/

# 3. Verificar Python
python --version
# Deve ser 3.8+

# 4. Verificar dependências
pip list | grep -E "fastapi|uvicorn|torch|transformers"
```

### Solução Definitiva (Hard-coded)

Se nada funcionar, edite `src/api/inference.py` linha 53 com SEU caminho:

```python
model_path = Path("/mnt/e/softplan/sentibr-ifood-analysis/models/bert_finetuned")
```

---

## 💡 DICA PRO

Para evitar problemas futuros, use variáveis de ambiente:

1. Crie `.env`:
```bash
MODEL_PATH=./models/bert_finetuned
```

2. Instale:
```bash
pip install python-dotenv
```

3. No código:
```python
import os
from dotenv import load_dotenv

load_dotenv()
model_path = Path(os.getenv("MODEL_PATH", "models/bert_finetuned"))
```

---

## 📞 RESUMO

| Problema | Solução |
|----------|---------|
| PermissionError /home/claude | Use **start_api_fixed.py** |
| Model not found | Modifique **src/api/inference.py** linha 53 |
| Caminhos errados | Use caminhos relativos ou .env |

---

## 🎉 DEPOIS QUE FUNCIONAR

A API estará disponível em:
- **Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1/predict

Teste com:
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Produto excelente!"}'
```

---

**Total de arquivos disponíveis**: 20 arquivos
**Status**: Pronto para usar após correções ✅
**Dificuldade**: Fácil 🟢
**Tempo estimado**: 5 minutos ⚡

---

**Desenvolvido para o Desafio Técnico - Cientista de Dados Sr**
**Versão**: 1.0.1 (com correções)
**Data**: Novembro 2024
