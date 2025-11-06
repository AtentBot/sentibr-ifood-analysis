"""
SentiBR - Phase 6 Runner
Executa todas as avaliações da Fase 6: Eval + LLM + Explainability
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import argparse


def print_banner():
    """Imprime banner da Fase 6"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🚀 SentiBR - FASE 6: EVALUATION 🚀             ║
    ║                                                              ║
    ║     Advanced Evaluation Framework & LLM Integration          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_phase_6(config: dict):
    """
    Executa Fase 6 completa
    
    Args:
        config: Configurações da fase
    """
    print_banner()
    
    start_time = datetime.now()
    results = {}
    
    # ========================================
    # 6.1: EVALUATION FRAMEWORK BÁSICO
    # ========================================
    if config.get('run_eval_framework', True):
        print("\n" + "="*70)
        print("📊 ETAPA 6.1: EVALUATION FRAMEWORK BÁSICO")
        print("="*70)
        
        try:
            from phase6_eval_suite import run_full_evaluation
            
            eval_results = run_full_evaluation(
                model_path=config['model_path'],
                test_data_path=config['test_data_path']
            )
            
            results['eval_framework'] = {
                'status': 'success',
                'accuracy': eval_results['metrics']['accuracy'],
                'f1_weighted': eval_results['metrics']['f1_weighted']
            }
            
            print("\n✅ Evaluation Framework concluído!")
            
        except Exception as e:
            print(f"\n❌ Erro no Evaluation Framework: {e}")
            results['eval_framework'] = {'status': 'error', 'error': str(e)}
    
    # ========================================
    # 6.2: LLM-AS-JUDGE
    # ========================================
    if config.get('run_llm_judge', True):
        print("\n" + "="*70)
        print("🤖 ETAPA 6.2: LLM-AS-JUDGE (GPT-4o-mini)")
        print("="*70)
        
        # Verifica API key
        openai_key = config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        
        if not openai_key:
            print("\n⚠️  OPENAI_API_KEY não encontrada!")
            print("Pulando LLM-as-Judge. Configure a key para habilitar:")
            print("export OPENAI_API_KEY='sua-key-aqui'")
            results['llm_judge'] = {'status': 'skipped', 'reason': 'no_api_key'}
        else:
            try:
                from phase6_llm_judge import run_llm_judge_evaluation
                
                # Busca arquivo de predições mais recente
                eval_dir = Path('evaluation_results')
                predictions_files = list(eval_dir.glob('predictions_*.csv'))
                
                if not predictions_files:
                    print("\n⚠️  Nenhum arquivo de predições encontrado!")
                    print("Execute primeiro o Evaluation Framework (6.1)")
                    results['llm_judge'] = {'status': 'skipped', 'reason': 'no_predictions'}
                else:
                    latest_predictions = max(predictions_files, key=lambda p: p.stat().st_mtime)
                    print(f"\n📂 Usando predições: {latest_predictions}")
                    
                    eval_df, analysis = run_llm_judge_evaluation(
                        predictions_csv=str(latest_predictions),
                        api_key=openai_key,
                        n_samples=config.get('llm_judge_samples', 100)
                    )
                    
                    results['llm_judge'] = {
                        'status': 'success',
                        'n_samples': analysis['n_samples'],
                        'gpt_accuracy': analysis['gpt_accuracy'],
                        'bert_accuracy': analysis['bert_accuracy'],
                        'agreement': analysis['bert_gpt_agreement'],
                        'cost_usd': analysis['total_cost_usd']
                    }
                    
                    print("\n✅ LLM-as-Judge concluído!")
                
            except Exception as e:
                print(f"\n❌ Erro no LLM-as-Judge: {e}")
                results['llm_judge'] = {'status': 'error', 'error': str(e)}
    
    # ========================================
    # 6.3: BERT vs GPT COMPARISON
    # ========================================
    if config.get('run_bert_vs_gpt', True):
        print("\n" + "="*70)
        print("⚖️  ETAPA 6.3: BERT vs GPT COMPARISON")
        print("="*70)
        
        openai_key = config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        
        if not openai_key:
            print("\n⚠️  OPENAI_API_KEY não encontrada!")
            print("Pulando comparação BERT vs GPT.")
            results['bert_vs_gpt'] = {'status': 'skipped', 'reason': 'no_api_key'}
        else:
            try:
                from phase6_bert_vs_gpt import run_bert_vs_gpt_comparison
                
                comp_df, analysis = run_bert_vs_gpt_comparison(
                    bert_model_path=config['model_path'],
                    test_data_path=config['test_data_path'],
                    openai_api_key=openai_key,
                    n_samples=config.get('comparison_samples', 100)
                )
                
                results['bert_vs_gpt'] = {
                    'status': 'success',
                    'bert_accuracy': analysis['bert_metrics']['accuracy'],
                    'gpt_accuracy': analysis['gpt_metrics']['accuracy'],
                    'bert_latency_ms': analysis['bert_metrics']['avg_latency_ms'],
                    'gpt_latency_ms': analysis['gpt_metrics']['avg_latency_ms'],
                    'gpt_cost_per_1k': analysis['gpt_metrics']['cost_per_request'] * 1000,
                    'recommendation': analysis['trade_off_analysis']['recommendation']
                }
                
                print("\n✅ Comparação BERT vs GPT concluída!")
                
            except Exception as e:
                print(f"\n❌ Erro na comparação BERT vs GPT: {e}")
                results['bert_vs_gpt'] = {'status': 'error', 'error': str(e)}
    
    # ========================================
    # 6.4: EXPLAINABILITY
    # ========================================
    if config.get('run_explainability', True):
        print("\n" + "="*70)
        print("🔍 ETAPA 6.4: EXPLAINABILITY (LIME)")
        print("="*70)
        
        try:
            from phase6_explainability import run_explainability_analysis
            
            explanations, global_stats = run_explainability_analysis(
                model_path=config['model_path'],
                test_data_path=config['test_data_path'],
                n_samples=config.get('explainability_samples', 20)
            )
            
            results['explainability'] = {
                'status': 'success',
                'n_explanations': len(explanations),
                'output_dir': 'evaluation_results/explainability'
            }
            
            print("\n✅ Explainability analysis concluída!")
            
        except Exception as e:
            print(f"\n❌ Erro na explainability: {e}")
            results['explainability'] = {'status': 'error', 'error': str(e)}
    
    # ========================================
    # SUMÁRIO FINAL
    # ========================================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*70)
    print("🎉 FASE 6 CONCLUÍDA!")
    print("="*70)
    
    print(f"\n⏱️  Tempo total: {duration:.1f}s ({duration/60:.1f} minutos)")
    
    print("\n📊 RESUMO DOS RESULTADOS:")
    for component, result in results.items():
        status_emoji = {
            'success': '✅',
            'error': '❌',
            'skipped': '⏭️'
        }.get(result['status'], '❓')
        
        print(f"\n  {status_emoji} {component.upper().replace('_', ' ')}:")
        
        if result['status'] == 'success':
            for key, value in result.items():
                if key != 'status':
                    if isinstance(value, float):
                        if 'accuracy' in key or 'agreement' in key:
                            print(f"    • {key}: {value:.2%}")
                        elif 'cost' in key:
                            print(f"    • {key}: ${value:.4f}")
                        elif 'latency' in key:
                            print(f"    • {key}: {value:.0f}ms")
                        else:
                            print(f"    • {key}: {value}")
                    else:
                        print(f"    • {key}: {value}")
        elif result['status'] == 'error':
            print(f"    Erro: {result.get('error', 'Unknown error')}")
        else:
            print(f"    Razão: {result.get('reason', 'Unknown')}")
    
    # Salva resumo
    summary_path = Path('evaluation_results/phase6_summary.json')
    summary_path.parent.mkdir(exist_ok=True)
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': duration,
        'config': {k: str(v) if isinstance(v, Path) else v 
                  for k, v in config.items() if k != 'openai_api_key'},
        'results': results
    }
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resumo salvo em: {summary_path}")
    
    print("\n" + "="*70)
    print("📁 ARQUIVOS GERADOS:")
    print("="*70)
    
    eval_dir = Path('evaluation_results')
    if eval_dir.exists():
        all_files = sorted(eval_dir.rglob('*'), key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Mostra os 10 arquivos mais recentes
        print("\n🆕 Arquivos mais recentes:")
        for file_path in all_files[:10]:
            if file_path.is_file():
                size = file_path.stat().st_size
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                print(f"  • {file_path.relative_to(eval_dir.parent)} ({size_str})")
    
    print("\n" + "="*70)
    
    return results


def parse_args():
    """Parse argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='SentiBR Phase 6: Evaluation Framework & LLM Integration'
    )
    
    parser.add_argument(
        '--model-path',
        type=str,
        default='models/bert_finetuned',
        help='Caminho para o modelo BERT treinado'
    )
    
    parser.add_argument(
        '--test-data',
        type=str,
        default='data/processed/test.csv',
        help='Caminho para o test dataset'
    )
    
    parser.add_argument(
        '--openai-key',
        type=str,
        help='OpenAI API key (ou use variável de ambiente OPENAI_API_KEY)'
    )
    
    parser.add_argument(
        '--skip-eval',
        action='store_true',
        help='Pula Evaluation Framework básico'
    )
    
    parser.add_argument(
        '--skip-llm-judge',
        action='store_true',
        help='Pula LLM-as-Judge'
    )
    
    parser.add_argument(
        '--skip-comparison',
        action='store_true',
        help='Pula comparação BERT vs GPT'
    )
    
    parser.add_argument(
        '--skip-explainability',
        action='store_true',
        help='Pula análise de explainability'
    )
    
    parser.add_argument(
        '--llm-samples',
        type=int,
        default=100,
        help='Número de samples para LLM-as-Judge (default: 100)'
    )
    
    parser.add_argument(
        '--comparison-samples',
        type=int,
        default=100,
        help='Número de samples para comparação BERT vs GPT (default: 100)'
    )
    
    parser.add_argument(
        '--explainability-samples',
        type=int,
        default=20,
        help='Número de samples para explainability (default: 20)'
    )
    
    return parser.parse_args()


def main():
    """Função principal"""
    args = parse_args()
    
    # Verifica dependências
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'torch',
        'transformers',
        'openai',
        'lime',
        'scikit-learn',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("\nInstale com:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)
    
    print("✅ Todas as dependências encontradas!")
    
    # Monta configuração
    config = {
        'model_path': args.model_path,
        'test_data_path': args.test_data,
        'openai_api_key': args.openai_key,
        'run_eval_framework': not args.skip_eval,
        'run_llm_judge': not args.skip_llm_judge,
        'run_bert_vs_gpt': not args.skip_comparison,
        'run_explainability': not args.skip_explainability,
        'llm_judge_samples': args.llm_samples,
        'comparison_samples': args.comparison_samples,
        'explainability_samples': args.explainability_samples
    }
    
    # Verifica arquivos
    if not Path(config['model_path']).exists():
        print(f"\n❌ Modelo não encontrado: {config['model_path']}")
        sys.exit(1)
    
    if not Path(config['test_data_path']).exists():
        print(f"\n❌ Test data não encontrado: {config['test_data_path']}")
        sys.exit(1)
    
    # Executa Fase 6
    try:
        results = run_phase_6(config)
        
        # Código de saída baseado em sucesso
        all_success = all(
            r['status'] in ['success', 'skipped'] 
            for r in results.values()
        )
        
        sys.exit(0 if all_success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
