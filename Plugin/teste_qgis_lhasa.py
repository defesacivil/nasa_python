# -*- coding: utf-8 -*-
"""
Script de Teste para QGIS - LHASA MG
====================================

Execute este script no console Python do QGIS para testar
a geração de mapas do algoritmo LHASA MG.

COMO USAR:
1. Abra o QGIS
2. Carregue as camadas de entrada
3. Abra o console Python (Plugins > Console Python)
4. Cole e execute este script
"""

from qgis.core import QgsProject, QgsVectorLayer, QgsField, QgsFeature
from qgis.PyQt.QtCore import QVariant
import processing

def testar_lhasa_qgis():
    """
    Testa o algoritmo LHASA MG no QGIS
    """
    print("=== TESTE LHASA MG NO QGIS ===")
    
    # 1. Verificar camadas carregadas
    project = QgsProject.instance()
    layers = project.mapLayers()
    
    print(f"Camadas carregadas: {len(layers)}")
    
    if len(layers) == 0:
        print("ERRO: Nenhuma camada carregada no QGIS")
        print("SOLUCAO: Carregue as camadas de suscetibilidade e zonas pluviometricas")
        return False
    
    # 2. Listar camadas
    print("\nCamadas disponíveis:")
    for layer_id, layer in layers.items():
        print(f"  - {layer.name()}")
        print(f"    Tipo: {layer.geometryType()}")
        print(f"    Features: {layer.featureCount()}")
        print(f"    Campos: {[field.name() for field in layer.fields()]}")
        print()
    
    # 3. Verificar campos necessários
    print("Verificando campos necessários...")
    
    suscetibilidade_ok = False
    zonas_ok = False
    
    for layer_id, layer in layers.items():
        if layer.geometryType() == 1:  # Polygon
            fields = [field.name() for field in layer.fields()]
            
            if 'gridcode' in fields:
                print(f"OK: Camada {layer.name()} tem campo 'gridcode'")
                suscetibilidade_ok = True
            
            if 'Cod' in fields and 'Est' in fields:
                print(f"OK: Camada {layer.name()} tem campos 'Cod' e 'Est'")
                zonas_ok = True
    
    if not suscetibilidade_ok:
        print("ERRO: Nenhuma camada tem campo 'gridcode'")
        print("SOLUCAO: Verifique o nome do campo na camada de suscetibilidade")
    
    if not zonas_ok:
        print("ERRO: Nenhuma camada tem campos 'Cod' e 'Est'")
        print("SOLUCAO: Verifique os nomes dos campos na camada de zonas")
    
    # 4. Testar ferramentas de processamento
    print("\nTestando ferramentas de processamento...")
    
    ferramentas = [
        'native:extractbyexpression',
        'native:intersection',
        'native:fieldcalculator',
        'native:dissolve'
    ]
    
    for ferramenta in ferramentas:
        try:
            info = processing.algorithmHelp(ferramenta)
            if info:
                print(f"OK: {ferramenta} disponível")
            else:
                print(f"ERRO: {ferramenta} NÃO disponível")
        except Exception as e:
            print(f"ERRO: {ferramenta} - {e}")
    
    # 5. Testar algoritmo LHASA
    print("\nTestando algoritmo LHASA...")
    
    try:
        # Importar o algoritmo
        from LHASA_MG import LhasaMgAnalysis
        
        algoritmo = LhasaMgAnalysis()
        print("OK: Algoritmo LHASA importado com sucesso")
        
        # Verificar parâmetros
        parametros = [
            'INPUT_SUSCETIBILIDADE',
            'INPUT_ZONAS_PLUVIOMETRICAS',
            'INPUT_DATA_ANALISE',
            'INPUT_TIPO_ANALISE',
            'OUTPUT_RESULTADO'
        ]
        
        for param in parametros:
            if hasattr(algoritmo, param):
                print(f"OK: Parâmetro {param} encontrado")
            else:
                print(f"ERRO: Parâmetro {param} NÃO encontrado")
        
    except ImportError as e:
        print(f"ERRO: Não foi possível importar algoritmo LHASA: {e}")
        print("SOLUCAO: Verifique se o arquivo LHASA_MG.py está no diretório correto")
    except Exception as e:
        print(f"ERRO: Erro ao testar algoritmo: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")
    return True

# Executar teste
testar_lhasa_qgis()
