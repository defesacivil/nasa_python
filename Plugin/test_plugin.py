# -*- coding: utf-8 -*-

"""
Teste simples para verificar se o plugin pode ser importado
"""

def test_imports():
    """Testa se todas as importações funcionam"""
    try:
        print("Testando importação do algoritmo...")
        from lhasa_mg_algorithm import LhasaMgAnalysis
        print("✓ LhasaMgAnalysis importado com sucesso")
        
        print("Testando importação do provider...")
        from lhasa_mg_provider import LhasaMgProvider
        print("✓ LhasaMgProvider importado com sucesso")
        
        print("Testando importação do plugin...")
        from lhasa_mg_plugin import LhasaMgPlugin
        print("✓ LhasaMgPlugin importado com sucesso")
        
        print("✓ Todos os módulos importados com sucesso!")
        return True
        
    except ImportError as e:
        print(f"✗ Erro de importação: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
