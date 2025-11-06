"""
SentiBR - Phase 6 Quick Test
Testa rapidamente todos os componentes antes da execução completa
"""

import sys
from pathlib import Path


def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def test_imports():
    """Testa se todos os imports necessários funcionam"""
    print_header("🔍 TESTANDO IMPORTS")
    
    packages = {
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'openai': 'OpenAI',
        'lime.lime_text': 'LIME',
        'sklearn': 'Scikit-learn',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'matplotlib': 'Matplotlib',
        'seaborn': 'Seaborn',
        'tqdm': 'TQDM'
    }
    
    failed = []
    
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            failed.append(name)
    
    if failed:
        print(f"\n⚠️  Pacotes faltando: {', '.join(failed)}")
        print("Execute: pip install -r requirements_phase6.txt")
        return False
    
    print("\n✅ Todos os imports funcionaram!")
    return True


def test_files():
    """Verifica se arquivos necessários existem"""
    print_header("📁 VERIFICANDO ARQUIVOS")
    
    required_files = [
        'phase6_eval_suite.py',
        'phase6_llm_judge.py',
        'phase6_bert_vs_gpt.py',
        'phase6_explainability.py',
        'run_phase6.py'
    ]
    
    missing = []
    
    for file in required_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            print(f"  ✅ {file} ({size:,} bytes)")
        else:
            print(f"  ❌ {file} - NÃO ENCONTRADO")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  Arquivos faltando: {', '.join(missing)}")
        return False
    
    print("\n✅ Todos os arquivos encontrados!")
    return True


def test_phase6_modules():
    """Testa se os módulos Phase 6 podem ser importados"""
    print_header("🐍 TESTANDO MÓDULOS PHASE 6")
    
    modules = [
        ('phase6_eval_suite', 'ModelEvaluator'),
        ('phase6_llm_judge', 'LLMJudge'),
        ('phase6_bert_vs_gpt', 'BERTvsGPTComparison'),
        ('phase6_explainability', 'SentimentExplainer')
    ]
    
    failed = []
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name}: {e}")
            failed.append(module_name)
    
    if failed:
        print(f"\n⚠️  Módulos com problema: {', '.join(failed)}")
        return False
    
    print("\n✅ Todos os módulos funcionais!")
    return True


def test_model_and_data():
    """Verifica se modelo e dados existem"""
    print_header("🤖 VERIFICANDO MODELO E DADOS")
    
    model_path = Path('models/bert_finetuned')
    test_data_path = Path('data/processed/test.csv')
    
    model_ok = False
    data_ok = False
    
    # Verifica modelo
    if model_path.exists():
        config_file = model_path / 'config.json'
        model_file = list(model_path.glob('*.bin')) or list(model_path.glob('*.safetensors'))
        
        if config_file.exists() and model_file:
            print(f"  ✅ Modelo BERT encontrado em {model_path}")
            model_ok = True
        else:
            print(f"  ⚠️  Diretório do modelo existe mas arquivos incompletos")
    else:
        print(f"  ❌ Modelo não encontrado em {model_path}")
        print(f"     Execute o treinamento (Fase 2) primeiro")
    
    # Verifica dados
    if test_data_path.exists():
        try:
            import pandas as pd
            df = pd.read_csv(test_data_path, nrows=5)
            required_cols = ['text', 'label']
            
            if all(col in df.columns for col in required_cols):
                print(f"  ✅ Test data encontrado ({test_data_path})")
                data_ok = True
            else:
                print(f"  ⚠️  Test data sem colunas necessárias: {required_cols}")
        except Exception as e:
            print(f"  ⚠️  Erro ao ler test data: {e}")
    else:
        print(f"  ❌ Test data não encontrado em {test_data_path}")
        print(f"     Execute a preparação de dados (Fase 1) primeiro")
    
    if model_ok and data_ok:
        print("\n✅ Modelo e dados prontos!")
        return True
    else:
        print("\n⚠️  Complete as fases anteriores antes de rodar Fase 6")
        return False


def test_openai_key():
    """Verifica OpenAI API key"""
    print_header("🔑 VERIFICANDO OPENAI API KEY")
    
    import os
    
    key = os.getenv('OPENAI_API_KEY')
    
    if key:
        key_preview = key[:10] + '...' + key[-4:] if len(key) > 14 else key[:10] + '...'
        print(f"  ✅ OPENAI_API_KEY encontrada ({key_preview})")
        
        # Tenta importar OpenAI
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            print(f"  ✅ OpenAI client inicializado")
            return True
        except Exception as e:
            print(f"  ⚠️  Erro ao inicializar OpenAI client: {e}")
            print(f"     Verifique se a key está correta")
            return False
    else:
        print(f"  ⚠️  OPENAI_API_KEY não encontrada")
        print(f"\n     Para usar LLM-as-Judge e comparação BERT vs GPT:")
        print(f"     export OPENAI_API_KEY='sua-key-aqui'")
        print(f"\n     Ou pule essas etapas com:")
        print(f"     python run_phase6.py --skip-llm-judge --skip-comparison")
        return False


def test_quick_prediction():
    """Testa uma predição rápida com BERT"""
    print_header("🔮 TESTE RÁPIDO DE PREDIÇÃO")
    
    try:
        import torch
        from transformers import BertTokenizer, BertForSequenceClassification
        
        model_path = 'models/bert_finetuned'
        
        if not Path(model_path).exists():
            print("  ⏭️  Pulando (modelo não encontrado)")
            return True
        
        print("  📦 Carregando modelo...")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        tokenizer = BertTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
        model = BertForSequenceClassification.from_pretrained(model_path)
        model.to(device)
        model.eval()
        
        print(f"  ✅ Modelo carregado no {device}")
        
        # Predição de teste
        test_text = "A comida estava deliciosa!"
        
        print(f"\n  🧪 Testando predição...")
        print(f"     Texto: '{test_text}'")
        
        with torch.no_grad():
            encodings = tokenizer(
                test_text,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors='pt'
            )
            
            input_ids = encodings['input_ids'].to(device)
            attention_mask = encodings['attention_mask'].to(device)
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
            pred = outputs.logits.argmax(dim=-1).cpu().numpy()[0]
        
        labels = {0: 'negativo', 1: 'neutro', 2: 'positivo'}
        
        print(f"\n  🎯 Resultado:")
        print(f"     Predição: {labels[pred]}")
        print(f"     Confiança: {probs[pred]:.2%}")
        print(f"     Probabilidades: neg={probs[0]:.2%}, neu={probs[1]:.2%}, pos={probs[2]:.2%}")
        
        print("\n  ✅ Predição funcionando!")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na predição: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║          🧪 SentiBR - Phase 6 Quick Test Suite 🧪           ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    results = {
        'Imports': test_imports(),
        'Arquivos': test_files(),
        'Módulos Phase 6': test_phase6_modules(),
        'Modelo e Dados': test_model_and_data(),
        'OpenAI Key': test_openai_key(),
        'Predição BERT': test_quick_prediction()
    }
    
    # Sumário
    print_header("📋 SUMÁRIO DOS TESTES")
    
    all_passed = True
    warnings = []
    failures = []
    
    for test_name, passed in results.items():
        if passed:
            print(f"  ✅ {test_name}")
        else:
            print(f"  ⚠️  {test_name}")
            if test_name in ['OpenAI Key']:
                warnings.append(test_name)
            else:
                failures.append(test_name)
                all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES CRÍTICOS PASSARAM!")
        print("\n🚀 Sistema pronto para Fase 6!")
        
        if warnings:
            print(f"\n⚠️  Avisos (componentes opcionais):")
            for warning in warnings:
                print(f"   • {warning}")
            print("\n   Você pode rodar Fase 6 pulando esses componentes:")
            print("   python run_phase6.py --skip-llm-judge --skip-comparison")
        
        print("\n📌 Próximos passos:")
        print("   1. Execute: python run_phase6.py")
        print("   2. Ou componentes individuais:")
        print("      • python phase6_eval_suite.py")
        print("      • python phase6_llm_judge.py")
        print("      • python phase6_bert_vs_gpt.py")
        print("      • python phase6_explainability.py")
        
        return 0
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print(f"\n   Problemas encontrados:")
        for failure in failures:
            print(f"   • {failure}")
        
        print("\n   Corrija os problemas acima antes de rodar Fase 6")
        print("   Consulte README_PHASE6.md para mais informações")
        
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
