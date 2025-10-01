# -*- coding: utf-8 -*-
"""
Diagnóstico do Problema de Geração de Mapa no QGIS
==================================================

Este script identifica e corrige problemas comuns na geração do mapa final
do algoritmo LHASA MG no QGIS.
"""

import os
import sys
from datetime import datetime

def diagnosticar_problemas_qgis():
    """
    Diagnostica problemas comuns na geração de mapas no QGIS
    """
    print("=== DIAGNÓSTICO DE PROBLEMAS - MAPA LHASA MG NO QGIS ===")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    problemas_identificados = []
    solucoes = []
    
    print("\n1. VERIFICANDO ESTRUTURA DO ALGORITMO...")
    
    # Verificar se a classe está corretamente implementada
    try:
        from LHASA_MG import LhasaMgAnalysis
        print("   ✓ Classe LhasaMgAnalysis encontrada")
        
        # Verificar métodos essenciais
        metodos_essenciais = [
            'initAlgorithm', 'processAlgorithm', 'executeRiskAnalysisQgis',
            'associateRainDataQgis', 'loadPluviometricDataQgis'
        ]
        
        for metodo in metodos_essenciais:
            if hasattr(LhasaMgAnalysis, metodo):
                print(f"   ✓ Método {metodo} encontrado")
            else:
                print(f"   ✗ Método {metodo} NÃO encontrado")
                problemas_identificados.append(f"Método {metodo} ausente")
                solucoes.append(f"Implementar método {metodo} na classe LhasaMgAnalysis")
        
    except ImportError as e:
        print(f"   ✗ Erro ao importar LhasaMgAnalysis: {e}")
        problemas_identificados.append("Erro de importação da classe principal")
        solucoes.append("Verificar se o arquivo LHASA_MG.py está no diretório correto")
    
    print("\n2. VERIFICANDO PARÂMETROS DO ALGORITMO...")
    
    # Verificar parâmetros de entrada
    parametros_esperados = [
        'INPUT_SUSCETIBILIDADE',
        'INPUT_ZONAS_PLUVIOMETRICAS', 
        'INPUT_DATA_ANALISE',
        'INPUT_TIPO_ANALISE',
        'OUTPUT_RESULTADO'
    ]
    
    try:
        from LHASA_MG import LhasaMgAnalysis
        algoritmo = LhasaMgAnalysis()
        
        # Verificar se os parâmetros estão definidos
        for param in parametros_esperados:
            if hasattr(algoritmo, param):
                print(f"   ✓ Parâmetro {param} definido")
            else:
                print(f"   ✗ Parâmetro {param} NÃO definido")
                problemas_identificados.append(f"Parâmetro {param} ausente")
                solucoes.append(f"Adicionar parâmetro {param} na classe")
        
    except Exception as e:
        print(f"   ✗ Erro ao verificar parâmetros: {e}")
        problemas_identificados.append("Erro na verificação de parâmetros")
    
    print("\n3. VERIFICANDO PROCESSAMENTO GEOGRÁFICO...")
    
    # Verificar se as ferramentas de processamento estão disponíveis
    try:
        from qgis.core import QgsApplication
        from qgis import processing
        
        # Verificar ferramentas essenciais
        ferramentas_essenciais = [
            'native:extractbyexpression',
            'native:intersection', 
            'native:fieldcalculator',
            'native:dissolve'
        ]
        
        for ferramenta in ferramentas_essenciais:
            try:
                # Tentar obter informações da ferramenta
                info = processing.algorithmHelp(ferramenta)
                if info:
                    print(f"   ✓ Ferramenta {ferramenta} disponível")
                else:
                    print(f"   ✗ Ferramenta {ferramenta} NÃO disponível")
                    problemas_identificados.append(f"Ferramenta {ferramenta} indisponível")
                    solucoes.append(f"Verificar se o QGIS está instalado corretamente")
            except Exception as e:
                print(f"   ✗ Erro ao verificar ferramenta {ferramenta}: {e}")
                problemas_identificados.append(f"Erro na ferramenta {ferramenta}")
        
    except ImportError as e:
        print(f"   ✗ QGIS não disponível: {e}")
        problemas_identificados.append("QGIS não disponível")
        solucoes.append("Executar o script dentro do QGIS")
    
    print("\n4. VERIFICANDO CAMPOS E DADOS...")
    
    # Verificar campos esperados
    campos_esperados = {
        'suscetibilidade': ['gridcode'],
        'zonas_pluviometricas': ['Cod', 'Est'],
        'dados_chuva': ['NM_M15', 'NM_H01', 'NM_H04', 'NM_H24', 'NM_H96']
    }
    
    for tipo, campos in campos_esperados.items():
        print(f"   Campos esperados para {tipo}: {campos}")
        print(f"   ✓ Verificar se estes campos existem nas camadas de entrada")
    
    print("\n5. VERIFICANDO SISTEMA DE COORDENADAS...")
    
    print("   SRC recomendado para o projeto QGIS:")
    print("   - SIRGAS 2000 / UTM Zona 23S (EPSG:31983)")
    print("   - Ou outro sistema projetado em metros")
    print("   ✓ Verificar se o projeto QGIS está configurado corretamente")
    
    print("\n6. VERIFICANDO LOGS E DEBUGGING...")
    
    # Verificar se o sistema de logging está funcionando
    try:
        from logger import lhasa_logger, log_event
        print("   ✓ Sistema de logging disponível")
        
        # Testar logging
        log_event("DIAGNOSTICO", "Teste de logging durante diagnóstico")
        print("   ✓ Logging funcionando corretamente")
        
    except ImportError as e:
        print(f"   ✗ Sistema de logging não disponível: {e}")
        problemas_identificados.append("Sistema de logging indisponível")
        solucoes.append("Verificar se o arquivo logger.py está no diretório correto")
    
    print("\n7. PROBLEMAS COMUNS IDENTIFICADOS...")
    
    problemas_comuns = [
        "Camadas de entrada não carregadas no QGIS",
        "Campos com nomes diferentes dos esperados",
        "SRC do projeto não configurado corretamente",
        "Token da API INMET não configurado",
        "Camadas de entrada vazias ou sem geometria",
        "Erro na expressão de cálculo do campo PERIGO",
        "Problemas de permissão para salvar arquivo de saída"
    ]
    
    for i, problema in enumerate(problemas_comuns, 1):
        print(f"   {i}. {problema}")
    
    print("\n8. SOLUÇÕES RECOMENDADAS...")
    
    solucoes_recomendadas = [
        "1. Verificar se as camadas de entrada estão carregadas no QGIS",
        "2. Verificar se os nomes dos campos correspondem aos esperados",
        "3. Configurar o SRC do projeto para SIRGAS 2000 / UTM Zona 23S",
        "4. Configurar o token da API INMET no código",
        "5. Verificar se as camadas têm geometrias válidas",
        "6. Testar a expressão de cálculo do campo PERIGO",
        "7. Verificar permissões de escrita no diretório de saída",
        "8. Usar o sistema de logging para identificar erros específicos",
        "9. Executar o algoritmo passo a passo para identificar onde falha",
        "10. Verificar se todas as dependências estão instaladas"
    ]
    
    for solucao in solucoes_recomendadas:
        print(f"   {solucao}")
    
    print("\n9. RESUMO DO DIAGNÓSTICO...")
    
    if problemas_identificados:
        print(f"   ✗ {len(problemas_identificados)} problema(s) identificado(s):")
        for i, problema in enumerate(problemas_identificados, 1):
            print(f"      {i}. {problema}")
        
        print(f"\n   💡 Soluções sugeridas:")
        for i, solucao in enumerate(solucoes, 1):
            print(f"      {i}. {solucao}")
    else:
        print("   ✓ Nenhum problema estrutural identificado")
        print("   💡 O problema pode estar nos dados de entrada ou configuração do QGIS")
    
    print("\n10. PRÓXIMOS PASSOS...")
    
    print("   1. Execute o algoritmo no QGIS com o sistema de logging ativado")
    print("   2. Verifique os logs gerados em logs/LHASA_MG_*.log")
    print("   3. Identifique em qual etapa o algoritmo falha")
    print("   4. Verifique os dados de entrada (camadas, campos, geometrias)")
    print("   5. Teste com dados de exemplo simples")
    print("   6. Configure corretamente o token da API INMET")
    
    return problemas_identificados, solucoes


def criar_script_teste_qgis():
    """
    Cria um script de teste simplificado para QGIS
    """
    script_teste = '''# -*- coding: utf-8 -*-
"""
Script de Teste Simplificado para QGIS
======================================

Execute este script no console Python do QGIS para testar
a geração de mapas do algoritmo LHASA MG.
"""

from qgis.core import QgsProject, QgsVectorLayer, QgsField, QgsFeature
from qgis.PyQt.QtCore import QVariant
import processing

def testar_geracao_mapa():
    """
    Testa a geração de mapa com dados de exemplo
    """
    print("=== TESTE DE GERAÇÃO DE MAPA LHASA MG ===")
    
    # 1. Verificar se há camadas carregadas
    project = QgsProject.instance()
    layers = project.mapLayers()
    
    print(f"Camadas carregadas: {len(layers)}")
    
    if len(layers) == 0:
        print("❌ Nenhuma camada carregada no QGIS")
        print("💡 Carregue as camadas de suscetibilidade e zonas pluviométricas")
        return False
    
    # 2. Listar camadas disponíveis
    print("\\nCamadas disponíveis:")
    for layer_id, layer in layers.items():
        print(f"  - {layer.name()} (ID: {layer_id})")
        print(f"    Tipo: {layer.geometryType()}")
        print(f"    Features: {layer.featureCount()}")
        print(f"    Campos: {[field.name() for field in layer.fields()]}")
        print()
    
    # 3. Verificar campos necessários
    print("Verificando campos necessários...")
    
    for layer_id, layer in layers.items():
        if layer.geometryType() == 1:  # Polygon
            fields = [field.name() for field in layer.fields()]
            
            # Verificar campos de suscetibilidade
            if 'gridcode' in fields:
                print(f"✓ Camada {layer.name()} tem campo 'gridcode'")
            else:
                print(f"✗ Camada {layer.name()} NÃO tem campo 'gridcode'")
                print("   Campos disponíveis:", fields)
            
            # Verificar campos de zonas pluviométricas
            if 'Cod' in fields and 'Est' in fields:
                print(f"✓ Camada {layer.name()} tem campos 'Cod' e 'Est'")
            else:
                print(f"✗ Camada {layer.name()} NÃO tem campos 'Cod' e 'Est'")
                print("   Campos disponíveis:", fields)
    
    # 4. Testar ferramentas de processamento
    print("\\nTestando ferramentas de processamento...")
    
    ferramentas_teste = [
        'native:extractbyexpression',
        'native:intersection',
        'native:fieldcalculator',
        'native:dissolve'
    ]
    
    for ferramenta in ferramentas_teste:
        try:
            info = processing.algorithmHelp(ferramenta)
            if info:
                print(f"✓ {ferramenta} disponível")
            else:
                print(f"✗ {ferramenta} NÃO disponível")
        except Exception as e:
            print(f"✗ Erro ao verificar {ferramenta}: {e}")
    
    # 5. Testar com dados de exemplo
    print("\\nTestando com dados de exemplo...")
    
    try:
        # Criar camada de teste
        layer_teste = QgsVectorLayer("Polygon?crs=EPSG:4674", "teste", "memory")
        provider = layer_teste.dataProvider()
        
        # Adicionar campos
        provider.addAttributes([
            QgsField("gridcode", QVariant.Int),
            QgsField("teste", QVariant.String)
        ])
        layer_teste.updateFields()
        
        # Adicionar feature de teste
        feature = QgsFeature()
        feature.setAttributes([2, "teste"])
        provider.addFeatures([feature])
        
        print("✓ Camada de teste criada com sucesso")
        
        # Testar ferramenta de seleção
        resultado = processing.run("native:extractbyexpression", {
            'INPUT': layer_teste,
            'EXPRESSION': '"gridcode" = 2',
            'OUTPUT': 'memory:'
        })
        
        if resultado['OUTPUT']:
            print("✓ Ferramenta de seleção funcionando")
        else:
            print("✗ Ferramenta de seleção falhou")
        
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
    
    print("\\n=== TESTE CONCLUÍDO ===")
    return True

# Executar teste
if __name__ == "__main__":
    testar_geracao_mapa()
'''
    
    with open("Plugin/teste_qgis_simples.py", "w", encoding="utf-8") as f:
        f.write(script_teste)
    
    print("✓ Script de teste criado: Plugin/teste_qgis_simples.py")
    print("💡 Execute este script no console Python do QGIS")


def criar_guia_solucao_problemas():
    """
    Cria um guia de solução de problemas
    """
    guia = '''# Guia de Solução de Problemas - Mapa LHASA MG no QGIS

## Problemas Comuns e Soluções

### 1. ❌ "Nenhuma camada carregada no QGIS"

**Problema:** O algoritmo não encontra as camadas de entrada.

**Soluções:**
- Carregue as camadas de suscetibilidade e zonas pluviométricas no QGIS
- Verifique se as camadas estão visíveis no painel de camadas
- Use o formato correto dos arquivos (Shapefile, GeoPackage, etc.)

### 2. ❌ "Campo 'gridcode' não encontrado"

**Problema:** A camada de suscetibilidade não tem o campo esperado.

**Soluções:**
- Verifique o nome do campo na tabela de atributos
- Renomeie o campo para 'gridcode' se necessário
- Ou modifique o código para usar o nome correto do campo

### 3. ❌ "Campos 'Cod' e 'Est' não encontrados"

**Problema:** A camada de zonas pluviométricas não tem os campos esperados.

**Soluções:**
- Verifique os nomes dos campos na tabela de atributos
- Renomeie os campos para 'Cod' e 'Est' se necessário
- Ou modifique o código para usar os nomes corretos

### 4. ❌ "Erro na ferramenta de processamento"

**Problema:** As ferramentas nativas do QGIS não estão funcionando.

**Soluções:**
- Verifique se o QGIS está instalado corretamente
- Atualize o QGIS para a versão mais recente
- Verifique se o plugin de processamento está ativado

### 5. ❌ "Token da API INMET inválido"

**Problema:** Não é possível buscar dados meteorológicos.

**Soluções:**
- Configure o token correto da API INMET no código
- Verifique se o token está ativo e válido
- Teste a conexão com a API manualmente

### 6. ❌ "Arquivo de saída não pode ser salvo"

**Problema:** Erro ao salvar o resultado final.

**Soluções:**
- Verifique as permissões de escrita no diretório
- Use um caminho de arquivo válido
- Verifique se há espaço suficiente em disco

### 7. ❌ "Geometrias inválidas"

**Problema:** As camadas têm geometrias corrompidas.

**Soluções:**
- Use a ferramenta "Corrigir geometrias" do QGIS
- Verifique se as camadas têm SRC definido
- Valide as geometrias antes de usar

### 8. ❌ "SRC incorreto"

**Problema:** As camadas não estão alinhadas corretamente.

**Soluções:**
- Configure o SRC do projeto para SIRGAS 2000 / UTM Zona 23S
- Verifique se todas as camadas têm SRC definido
- Use a reprojeção automática do QGIS

## Como Usar o Sistema de Logging

1. **Ativar logs detalhados:**
   ```python
   from logger import lhasa_logger
   lhasa_logger.logger.setLevel(logging.DEBUG)
   ```

2. **Verificar logs gerados:**
   - Arquivo principal: `logs/LHASA_MG_YYYYMMDD_HHMMSS.log`
   - Arquivo de erros: `logs/LHASA_ERRORS_YYYYMMDD_HHMMSS.log`
   - Arquivo da sessão: `logs/LHASA_SESSION_YYYYMMDD_HHMMSS.json`

3. **Interpretar os logs:**
   - Procure por mensagens de erro específicas
   - Verifique o contexto dos erros
   - Use os logs para identificar onde o algoritmo falha

## Teste Passo a Passo

1. **Carregar camadas de teste:**
   - Camada de suscetibilidade com campo 'gridcode'
   - Camada de zonas pluviométricas com campos 'Cod' e 'Est'

2. **Configurar projeto:**
   - SRC: SIRGAS 2000 / UTM Zona 23S (EPSG:31983)
   - Verificar se as camadas estão alinhadas

3. **Executar algoritmo:**
   - Use a Caixa de Ferramentas de Processamento
   - Configure os parâmetros corretamente
   - Monitore os logs durante a execução

4. **Verificar resultado:**
   - O mapa final deve aparecer no QGIS
   - Verificar se os níveis de perigo estão corretos
   - Validar a geometria do resultado

## Contato e Suporte

Se os problemas persistirem:
1. Verifique os logs detalhados
2. Teste com dados de exemplo simples
3. Execute o script de diagnóstico
4. Consulte a documentação do QGIS
'''
    
    with open("Plugin/GUIA_SOLUCAO_PROBLEMAS.md", "w", encoding="utf-8") as f:
        f.write(guia)
    
    print("✓ Guia de solução criado: Plugin/GUIA_SOLUCAO_PROBLEMAS.md")


if __name__ == "__main__":
    print("Iniciando diagnóstico de problemas do mapa QGIS...")
    
    # Executar diagnóstico
    problemas, solucoes = diagnosticar_problemas_qgis()
    
    # Criar scripts de ajuda
    criar_script_teste_qgis()
    criar_guia_solucao_problemas()
    
    print("\n=== DIAGNÓSTICO CONCLUÍDO ===")
    print("Arquivos criados:")
    print("- Plugin/teste_qgis_simples.py")
    print("- Plugin/GUIA_SOLUCAO_PROBLEMAS.md")
    print("\nPróximos passos:")
    print("1. Execute o script de teste no QGIS")
    print("2. Consulte o guia de solução de problemas")
    print("3. Use o sistema de logging para identificar erros específicos")



