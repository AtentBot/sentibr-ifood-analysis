#!/usr/bin/env python3
"""
Script de verificação do ambiente SentiBR
Verifica se todas as dependências e configurações estão corretas
"""

import sys
import subprocess
from pathlib import Path
import importlib.util


def check_python_version():
    """Verifica versão do Python"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 10:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} (requer 3.10+)")
        return False


def check_package(package_name, import_name=None):
    """Verifica se um pacote está instalado"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def check_dependencies():
    """Verifica dependências principais"""
    print("\n📦 Verificando dependências...")
    
    dependencies = {
        'torch': 'torch',
        'transformers': 'transformers',
        'fastapi': 'fastapi',
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scikit-learn': 'sklearn',
        'mlflow': 'mlflow',
        'openai': 'openai',
    }
    
    all_ok = True
    for package, import_name in dependencies.items():
        if check_package(package, import_name):
            print(f"   ✅ {package}")
        else:
            print(f"   ❌ {package} (não instalado)")
            all_ok = False
    
    return all_ok


def check_directories():
    """Verifica estrutura de diretórios"""
    print("\n📁 Verificando estrutura de diretórios...")
    
    required_dirs = [
        "data/raw",
        "data/processed",
        "models/bert_finetuned",
        "src/training",
        "src/api",
        "src/monitoring",
        "src/evaluation",
        "src/data",
        "frontend",
        "notebooks",
        "tests",
        "logs"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ (não existe)")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Verifica arquivo .env"""
    print("\n🔧 Verificando configurações...")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_example_path.exists():
        print("   ❌ .env.example não encontrado")
        return False
    else:
        print("   ✅ .env.example encontrado")
    
    if not env_path.exists():
        print("   ⚠️  .env não encontrado (copie de .env.example)")
        return False
    else:
        print("   ✅ .env encontrado")
        
        # Verificar variáveis importantes
        with open(env_path) as f:
            content = f.read()
            
        required_vars = [
            "OPENAI_API_KEY",
            "MODEL_NAME",
            "MLFLOW_TRACKING_URI"
        ]
        
        missing = []
        for var in required_vars:
            if var not in content or f"{var}=your_" in content or f"{var}=" in content and content.split(f"{var}=")[1].split("\n")[0].strip() == "":
                missing.append(var)
        
        if missing:
            print(f"   ⚠️  Variáveis não configuradas: {', '.join(missing)}")
            return False
        
    return True


def check_git():
    """Verifica Git"""
    print("\n🔀 Verificando Git...")
    
    git_path = Path(".git")
    if git_path.exists():
        print("   ✅ Repositório Git inicializado")
        
        # Verificar remote
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                print("   ✅ Remote configurado")
            else:
                print("   ⚠️  Remote não configurado")
        except:
            pass
        
        return True
    else:
        print("   ❌ Git não inicializado (execute: git init)")
        return False


def check_cuda():
    """Verifica CUDA (GPU)"""
    print("\n🖥️  Verificando GPU...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"   ✅ CUDA disponível: {torch.cuda.get_device_name(0)}")
            print(f"   ℹ️  Memória: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return True
        else:
            print("   ⚠️  CUDA não disponível (CPU only)")
            return False
    except:
        print("   ❌ Não foi possível verificar CUDA")
        return False


def print_summary(checks):
    """Imprime resumo final"""
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    total = len(checks)
    passed = sum(checks.values())
    
    print(f"\n✅ Passou: {passed}/{total}")
    print(f"❌ Falhou: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 Tudo certo! Ambiente pronto para uso.")
        print("\n💡 Próximos passos:")
        print("   1. Configure a OPENAI_API_KEY no .env (se usar GPT)")
        print("   2. Execute: python src/data/load_data.py")
        print("   3. Explore o notebook: notebooks/01_eda.ipynb")
        return True
    else:
        print("\n⚠️  Alguns problemas encontrados. Corrija-os antes de continuar.")
        
        failed = [name for name, result in checks.items() if not result]
        print("\n❌ Falhou em:")
        for item in failed:
            print(f"   - {item}")
        
        print("\n💡 Sugestões:")
        print("   - Execute: pip install -r requirements.txt")
        print("   - Copie .env.example para .env e configure")
        print("   - Execute: mkdir -p data/{raw,processed} models logs")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 SENTIBR - Verificação de Ambiente")
    print("=" * 60)
    
    checks = {
        "Python 3.10+": check_python_version(),
        "Dependências": check_dependencies(),
        "Estrutura de diretórios": check_directories(),
        "Configurações (.env)": check_env_file(),
        "Git": check_git(),
    }
    
    # CUDA é opcional
    check_cuda()
    
    success = print_summary(checks)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
