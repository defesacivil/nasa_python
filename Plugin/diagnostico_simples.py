# -*- coding: utf-8 -*-
"""
Diagnóstico Simples - Problemas de Mapa no QGIS
===============================================

Este script identifica problemas comuns na geração de mapas
do algoritmo LHASA MG no QGIS.
"""

import os
import sys
from datetime import datetime

def diagnosticar_problemas():
    """
    Diagnostica problemas comuns na geração de mapas no QGIS
    """
    print("=== DIAGNOSTICO DE PROBLEMAS - MAPA LHASA MG NO QGIS ===")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    problemas_identificados = []
    solucoes = []
    
    print("\n1. VERIFICANDO ESTRUTURA DO ALGORITMO...")
    
    # Verificar se o arquivo principal existe
    arquivo_principal = "Plugin/LHASA_MG.py"
    conteudo = ""
    if os.path.exists(arquivo_principal):
        print(f"   [OK] Arquivo {arquivo_principal} encontrado")
        
        # Verificar se contém a classe principal
        with open(arquivo_principal, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        if "class LhasaMgAnalysis" in conteudo:
            print("   [OK] Classe LhasaMgAnalysis encontrada")
        else:
            print("   [ERRO] Classe LhasaMgAnalysis NAO encontrada")
            problemas_identificados.append("Classe principal ausente")
            solucoes.append("Implementar classe LhasaMgAnalysis")
        
        # Verificar métodos essenciais
        metodos_essenciais = [
            'initAlgorithm', 'processAlgorithm', 'executeRiskAnalysisQgis',
            'associateRainDataQgis', 'loadPluviometricDataQgis'
        ]
        
        for metodo in metodos_essenciais:
            if f"def {metodo}" in conteudo:
                print(f"   [OK] Metodo {metodo} encontrado")
            else:
                print(f"   [ERRO] Metodo {metodo} NAO encontrado")
                problemas_identificados.append(f"Metodo {metodo} ausente")
                solucoes.append(f"Implementar metodo {metodo}")
    else:
        print(f"   [ERRO] Arquivo {arquivo_principal} NAO encontrado")
        problemas_identificados.append("Arquivo principal ausente")
        solucoes.append("Criar arquivo LHASA_MG.py")
    
    print("\n2. VERIFICANDO DEPENDENCIAS...")
    
    # Verificar dependências Python
    dependencias = ['requests', 'json', 'datetime', 'os', 'sys']
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"   [OK] Modulo {dep} disponivel")
        except ImportError:
            print(f"   [ERRO] Modulo {dep} NAO disponivel")
            problemas_identificados.append(f"Modulo {dep} ausente")
            solucoes.append(f"Instalar modulo {dep}")
    
    # Verificar dependências QGIS (sem importar)
    print("   [INFO] Dependencias QGIS devem ser verificadas dentro do QGIS")
    print("   [INFO] Modulos necessarios: qgis.core, qgis.PyQt, processing")
    
    print("\n3. VERIFICANDO CONFIGURACAO DA API...")
    
    # Verificar token da API INMET
    if "INMET_TOKEN = \"YOUR_TOKEN_HERE\"" in conteudo:
        print("   [ERRO] Token da API INMET nao configurado")
        problemas_identificados.append("Token da API INMET nao configurado")
        solucoes.append("Configurar token real da API INMET")
    else:
        print("   [OK] Token da API INMET configurado")
    
    # Verificar URLs da API
    if "https://apitempo.inmet.gov.br" in conteudo:
        print("   [OK] URLs da API INMET encontradas")
    else:
        print("   [ERRO] URLs da API INMET nao encontradas")
        problemas_identificados.append("URLs da API INMET ausentes")
        solucoes.append("Adicionar URLs da API INMET")
    
    print("\n4. VERIFICANDO SISTEMA DE LOGGING...")
    
    arquivo_logger = "logger.py"
    if os.path.exists(arquivo_logger):
        print(f"   [OK] Arquivo {arquivo_logger} encontrado")
        
        # Verificar se está sendo importado
        if "from logger import" in conteudo:
            print("   [OK] Sistema de logging sendo importado")
        else:
            print("   [AVISO] Sistema de logging nao sendo importado")
    else:
        print(f"   [ERRO] Arquivo {arquivo_logger} NAO encontrado")
        problemas_identificados.append("Sistema de logging ausente")
        solucoes.append("Criar arquivo logger.py")
    
    print("\n5. VERIFICANDO ESTRUTURA DE DIRETORIOS...")
    
    diretorios_necessarios = ["logs"]
    
    for diretorio in diretorios_necessarios:
        if os.path.exists(diretorio):
            print(f"   [OK] Diretorio {diretorio} existe")
        else:
            print(f"   [AVISO] Diretorio {diretorio} nao existe (sera criado automaticamente)")
    
    print("\n6. PROBLEMAS COMUNS IDENTIFICADOS...")
    
    problemas_comuns = [
        "Camadas de entrada nao carregadas no QGIS",
        "Campos com nomes diferentes dos esperados",
        "SRC do projeto nao configurado corretamente", 
        "Token da API INMET nao configurado",
        "Camadas de entrada vazias ou sem geometria",
        "Erro na expressao de calculo do campo PERIGO",
        "Problemas de permissao para salvar arquivo de saida",
        "QGIS nao esta executando ou plugin nao carregado",
        "Camadas de entrada nao tem os campos esperados",
        "Geometrias das camadas estao corrompidas"
    ]
    
    for i, problema in enumerate(problemas_comuns, 1):
        print(f"   {i}. {problema}")
    
    print("\n7. SOLUCOES RECOMENDADAS...")
    
    solucoes_recomendadas = [
        "1. Carregar as camadas de entrada no QGIS antes de executar",
        "2. Verificar se os nomes dos campos correspondem aos esperados",
        "3. Configurar o SRC do projeto para SIRGAS 2000 / UTM Zona 23S",
        "4. Configurar o token correto da API INMET no codigo",
        "5. Verificar se as camadas tem geometrias validas",
        "6. Testar a expressao de calculo do campo PERIGO",
        "7. Verificar permissoes de escrita no diretorio de saida",
        "8. Executar o algoritmo dentro do QGIS (nao via linha de comando)",
        "9. Verificar se o plugin esta carregado corretamente",
        "10. Usar dados de exemplo simples para teste"
    ]
    
    for solucao in solucoes_recomendadas:
        print(f"   {solucao}")
    
    print("\n8. CHECKLIST DE VERIFICACAO...")
    
    checklist = [
        "Camada de suscetibilidade carregada no QGIS",
        "Camada de zonas pluviometricas carregada no QGIS", 
        "Campo 'gridcode' existe na camada de suscetibilidade",
        "Campos 'Cod' e 'Est' existem na camada de zonas",
        "SRC do projeto configurado corretamente",
        "Token da API INMET configurado",
        "Camadas tem geometrias validas",
        "Permissoes de escrita no diretorio de saida",
        "QGIS esta executando",
        "Plugin LHASA MG esta ativado"
    ]
    
    print("   Verifique cada item:")
    for i, item in enumerate(checklist, 1):
        print(f"   {i}. [ ] {item}")
    
    print("\n9. COMO EXECUTAR O TESTE...")
    
    print("   1. Abra o QGIS")
    print("   2. Carregue as camadas de entrada")
    print("   3. Configure o SRC do projeto")
    print("   4. Vá em Processamento > Caixa de Ferramentas")
    print("   5. Procure por 'LHASA MG - Análise de Risco de Deslizamento'")
    print("   6. Execute o algoritmo com os parâmetros corretos")
    print("   7. Verifique os logs gerados em logs/")
    
    print("\n10. RESUMO DO DIAGNOSTICO...")
    
    if problemas_identificados:
        print(f"   [ERRO] {len(problemas_identificados)} problema(s) identificado(s):")
        for i, problema in enumerate(problemas_identificados, 1):
            print(f"      {i}. {problema}")
        
        print(f"\n   [SOLUCAO] Solucoes sugeridas:")
        for i, solucao in enumerate(solucoes, 1):
            print(f"      {i}. {solucao}")
    else:
        print("   [OK] Nenhum problema estrutural identificado")
        print("   [INFO] O problema pode estar nos dados de entrada ou configuracao do QGIS")
    
    return problemas_identificados, solucoes


def criar_script_teste_qgis():
    """
    Cria um script de teste para executar no QGIS
    """
    script = '''# -*- coding: utf-8 -*-
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
    print("\\nCamadas disponíveis:")
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
    print("\\nTestando ferramentas de processamento...")
    
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
    print("\\nTestando algoritmo LHASA...")
    
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
    
    print("\\n=== TESTE CONCLUÍDO ===")
    return True

# Executar teste
testar_lhasa_qgis()
'''
    
    with open("Plugin/teste_qgis_lhasa.py", "w", encoding="utf-8") as f:
        f.write(script)
    
    print("Script de teste criado: Plugin/teste_qgis_lhasa.py")


def criar_guia_rapido():
    """
    Cria um guia rápido de solução
    """
    guia = '''# Guia Rápido - Solução de Problemas Mapa LHASA MG

## Problema: Mapa não é gerado no QGIS

### Verificações Essenciais:

1. **Camadas de Entrada**
   - [ ] Camada de suscetibilidade carregada
   - [ ] Camada de zonas pluviométricas carregada
   - [ ] Camadas têm geometrias válidas

2. **Campos Necessários**
   - [ ] Campo 'gridcode' na camada de suscetibilidade
   - [ ] Campos 'Cod' e 'Est' na camada de zonas
   - [ ] Campos têm dados válidos

3. **Configuração do Projeto**
   - [ ] SRC configurado para SIRGAS 2000 / UTM Zona 23S
   - [ ] Camadas estão alinhadas visualmente
   - [ ] Projeto salvo corretamente

4. **API INMET**
   - [ ] Token da API configurado no código
   - [ ] Conexão com internet funcionando
   - [ ] Data da análise válida

5. **Execução do Algoritmo**
   - [ ] QGIS está executando
   - [ ] Plugin LHASA MG está ativado
   - [ ] Parâmetros configurados corretamente
   - [ ] Diretório de saída tem permissão de escrita

### Soluções Rápidas:

1. **Se as camadas não aparecem:**
   - Recarregue as camadas no QGIS
   - Verifique o formato dos arquivos
   - Use "Adicionar Camada Vetorial"

2. **Se os campos não existem:**
   - Verifique os nomes na tabela de atributos
   - Renomeie os campos se necessário
   - Ou modifique o código para usar os nomes corretos

3. **Se o SRC está incorreto:**
   - Vá em Projeto > Propriedades > SRC
   - Selecione SIRGAS 2000 / UTM Zona 23S (EPSG:31983)
   - Aplique a configuração

4. **Se a API não funciona:**
   - Configure o token real da API INMET
   - Teste a conexão manualmente
   - Use uma data anterior (ex: ontem)

5. **Se o algoritmo não executa:**
   - Execute dentro do QGIS (não via linha de comando)
   - Use a Caixa de Ferramentas de Processamento
   - Verifique os logs de erro

### Teste Passo a Passo:

1. Abra o QGIS
2. Carregue as camadas de entrada
3. Configure o SRC do projeto
4. Execute: Plugin/teste_qgis_lhasa.py no console Python
5. Vá em Processamento > Caixa de Ferramentas
6. Procure por "LHASA MG - Análise de Risco de Deslizamento"
7. Execute o algoritmo
8. Verifique o resultado no QGIS

### Logs de Debug:

- Arquivo principal: logs/LHASA_MG_*.log
- Arquivo de erros: logs/LHASA_ERRORS_*.log
- Arquivo da sessão: logs/LHASA_SESSION_*.json

### Contato:

Se os problemas persistirem, verifique os logs detalhados
e execute o script de teste no QGIS.
'''
    
    with open("Plugin/GUIA_RAPIDO.md", "w", encoding="utf-8") as f:
        f.write(guia)
    
    print("Guia rápido criado: Plugin/GUIA_RAPIDO.md")


if __name__ == "__main__":
    print("Iniciando diagnóstico de problemas do mapa QGIS...")
    
    # Executar diagnóstico
    problemas, solucoes = diagnosticar_problemas()
    
    # Criar scripts de ajuda
    criar_script_teste_qgis()
    criar_guia_rapido()
    
    print("\n=== DIAGNOSTICO CONCLUIDO ===")
    print("Arquivos criados:")
    print("- Plugin/teste_qgis_lhasa.py")
    print("- Plugin/GUIA_RAPIDO.md")
    print("\nProximos passos:")
    print("1. Execute o script de teste no QGIS")
    print("2. Consulte o guia rapido de solucao")
    print("3. Verifique os logs gerados durante a execucao")

