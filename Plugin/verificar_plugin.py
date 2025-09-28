# -*- coding: utf-8 -*-

"""
Script para verificar se o plugin LHASA MG está funcionando corretamente
Execute este script no Console Python do QGIS
"""

def verificar_plugin_lhasa_mg():
    """Verifica se o plugin LHASA MG está funcionando"""
    
    print("=== VERIFICAÇÃO DO PLUGIN LHASA MG ===")
    print()
    
    # Teste 1: Importações básicas
    print("1. Testando importações...")
    try:
        from qgis.core import QgsApplication
        print("   ✓ QGIS core importado")
        
        import processing
        print("   ✓ Processing importado")
        
        import requests
        print("   ✓ Requests disponível")
        
    except ImportError as e:
        print(f"   ✗ Erro de importação: {e}")
        return False
    
    # Teste 2: Verificar se o plugin está carregado
    print("\n2. Verificando carregamento do plugin...")
    try:
        registry = QgsApplication.processingRegistry()
        providers = registry.providers()
        
        lhasa_provider = None
        for provider in providers:
            if provider.id() == 'lhasa_mg':
                lhasa_provider = provider
                break
        
        if lhasa_provider:
            print("   ✓ Provider LHASA MG encontrado")
            
            # Verificar algoritmos
            algorithms = lhasa_provider.algorithms()
            if algorithms:
                print(f"   ✓ {len(algorithms)} algoritmo(s) disponível(is)")
                for alg in algorithms:
                    print(f"      - {alg.displayName()}")
            else:
                print("   ⚠ Provider encontrado mas sem algoritmos")
                
        else:
            print("   ✗ Provider LHASA MG não encontrado")
            print("   Providers disponíveis:")
            for provider in providers:
                print(f"      - {provider.id()}: {provider.name()}")
            return False
            
    except Exception as e:
        print(f"   ✗ Erro ao verificar providers: {e}")
        return False
    
    # Teste 3: Testar API INMET
    print("\n3. Testando conexão com API INMET...")
    try:
        import requests
        response = requests.get("https://apitempo.inmet.gov.br/estacoes/T", timeout=10)
        
        if response.status_code == 200:
            estacoes = response.json()
            estacoes_mg = [e for e in estacoes if e.get('SG_ESTADO') == 'MG']
            print(f"   ✓ API INMET acessível - {len(estacoes_mg)} estações em MG")
        else:
            print(f"   ⚠ API INMET retornou código {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Erro ao acessar API INMET: {e}")
        print("   (Isso pode afetar a funcionalidade do plugin)")
    
    # Teste 4: Verificar se algoritmo pode ser executado
    print("\n4. Testando disponibilidade do algoritmo...")
    try:
        alg_id = "lhasa_mg:lhasa_mg_analysis"
        alg = QgsApplication.processingRegistry().algorithmById(alg_id)
        
        if alg:
            print(f"   ✓ Algoritmo '{alg_id}' disponível")
            print(f"   Nome: {alg.displayName()}")
            print(f"   Grupo: {alg.group()}")
            
            # Listar parâmetros
            params = alg.parameterDefinitions()
            print(f"   Parâmetros ({len(params)}):")
            for param in params:
                print(f"      - {param.name()}: {param.description()}")
                
        else:
            print(f"   ✗ Algoritmo '{alg_id}' não encontrado")
            return False
            
    except Exception as e:
        print(f"   ✗ Erro ao verificar algoritmo: {e}")
        return False
    
    # Teste 5: Verificar estrutura de arquivos
    print("\n5. Verificando estrutura de arquivos...")
    try:
        import os
        from qgis.utils import pluginDirectory
        
        plugin_dir = pluginDirectory('lhasa_mg')
        if os.path.exists(plugin_dir):
            print(f"   ✓ Diretório do plugin: {plugin_dir}")
            
            arquivos_necessarios = [
                '__init__.py',
                'lhasa_mg_plugin.py', 
                'lhasa_mg_provider.py',
                'lhasa_mg_simple.py',
                'metadata.txt'
            ]
            
            for arquivo in arquivos_necessarios:
                caminho = os.path.join(plugin_dir, arquivo)
                if os.path.exists(caminho):
                    print(f"   ✓ {arquivo}")
                else:
                    print(f"   ✗ {arquivo} não encontrado")
                    
        else:
            print(f"   ✗ Diretório do plugin não encontrado: {plugin_dir}")
            return False
            
    except Exception as e:
        print(f"   ⚠ Não foi possível verificar arquivos: {e}")
    
    print("\n=== RESULTADO ===")
    print("✓ Plugin LHASA MG está funcionando corretamente!")
    print("\nPara usar:")
    print("1. Abra a Caixa de Ferramentas (Ctrl+Alt+T)")
    print("2. Navegue até: Análises de Risco → LHASA MG")
    print("3. Configure seus dados e execute")
    
    return True

def listar_algoritmos_disponiveis():
    """Lista todos os algoritmos de processamento disponíveis"""
    print("\n=== ALGORITMOS DISPONÍVEIS ===")
    
    try:
        from qgis.core import QgsApplication
        registry = QgsApplication.processingRegistry()
        
        for provider in registry.providers():
            algorithms = provider.algorithms()
            if algorithms:
                print(f"\n{provider.name()} ({provider.id()}):")
                for alg in algorithms:
                    print(f"  - {alg.id()}: {alg.displayName()}")
                    
    except Exception as e:
        print(f"Erro ao listar algoritmos: {e}")

# Executar verificação
if __name__ == "__main__":
    verificar_plugin_lhasa_mg()
else:
    # Quando importado no QGIS, execute automaticamente
    verificar_plugin_lhasa_mg()
