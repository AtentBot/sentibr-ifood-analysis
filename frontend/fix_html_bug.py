#!/usr/bin/env python3
"""
Script Automático de Correção do Bug HTML
Adiciona unsafe_allow_html=True em todos os st.markdown() necessários
"""
import re
import sys
from pathlib import Path
import shutil


def fix_streamlit_html(file_path: str) -> bool:
    """
    Corrige st.markdown() adicionando unsafe_allow_html=True
    
    Args:
        file_path: Caminho para o arquivo app.py
    
    Returns:
        True se corrigiu, False se erro
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    # Fazer backup
    backup_path = file_path.with_suffix('.py.backup')
    shutil.copy(file_path, backup_path)
    print(f"✅ Backup criado: {backup_path}")
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar st.markdown() com HTML mas sem unsafe_allow_html
    # Procura por st.markdown com """ ou ''' e HTML tags, mas sem unsafe_allow_html
    pattern = r'(st\.markdown\s*\(\s*f?["\']"")([\s\S]*?)(["\']"")\s*\)'
    
    fixes_made = 0
    
    def replacer(match):
        nonlocal fixes_made
        
        prefix = match.group(1)
        content_block = match.group(2)
        suffix = match.group(3)
        
        # Verificar se tem HTML tags
        has_html = bool(re.search(r'<[a-zA-Z]', content_block))
        
        # Verificar se já tem unsafe_allow_html
        full_match = match.group(0)
        has_unsafe = 'unsafe_allow_html' in full_match
        
        if has_html and not has_unsafe:
            fixes_made += 1
            # Adicionar unsafe_allow_html=True
            return f'{prefix}{content_block}{suffix}, unsafe_allow_html=True)'
        else:
            return match.group(0)
    
    # Aplicar correções
    new_content = re.sub(pattern, replacer, content)
    
    if fixes_made > 0:
        # Salvar arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n✅ Correções aplicadas: {fixes_made}")
        print(f"✅ Arquivo atualizado: {file_path}")
        print(f"\n📝 Para desfazer: cp {backup_path} {file_path}")
        return True
    else:
        print("\n⚠️ Nenhuma correção necessária ou padrão não encontrado")
        print("💡 Verifique se o arquivo tem st.markdown() com HTML")
        # Remover backup desnecessário
        backup_path.unlink()
        return False


def find_streamlit_app():
    """Tenta encontrar app.py do Streamlit"""
    possible_paths = [
        "app.py",
        "frontend/app.py",
        "src/app.py",
        "../frontend/app.py",
        "../../frontend/app.py",
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    return None


def main():
    print("=" * 60)
    print("🔧 CORREÇÃO AUTOMÁTICA - HTML NO STREAMLIT")
    print("=" * 60)
    print()
    
    # Tentar encontrar arquivo
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = find_streamlit_app()
        
        if file_path is None:
            print("❌ app.py não encontrado automaticamente")
            print()
            print("💡 USO:")
            print(f"   python {sys.argv[0]} /caminho/para/app.py")
            print()
            print("   OU coloque este script no mesmo diretório do app.py")
            sys.exit(1)
    
    print(f"📁 Arquivo alvo: {file_path}")
    print()
    
    # Aplicar correções
    success = fix_streamlit_html(file_path)
    
    if success:
        print()
        print("=" * 60)
        print("✅ CORREÇÃO CONCLUÍDA!")
        print("=" * 60)
        print()
        print("🚀 Próximos passos:")
        print("   1. Reinicie o Streamlit:")
        print("      streamlit run app.py --server.port 8502")
        print()
        print("   2. Abra no navegador:")
        print("      http://localhost:8502")
        print()
        print("   3. Verifique se os cards estão renderizando!")
        print()
    else:
        print()
        print("❌ Não foi possível aplicar correções")
        print()
        print("💡 Correção manual:")
        print("   Adicione 'unsafe_allow_html=True' nos st.markdown()")
        print("   Exemplo:")
        print("   st.markdown('<div>...</div>', unsafe_allow_html=True)")
        print()


if __name__ == "__main__":
    main()
