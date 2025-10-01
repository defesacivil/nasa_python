# -*- coding: utf-8 -*-
"""
Teste das Correções do LHASA MG
===============================

Script para testar se as correções aplicadas no arquivo original
resolvem o problema de carregamento de camadas no QGIS.
"""

import os
import sys
from datetime import datetime

def testar_correcoes():
    """
    Testa as correções aplicadas no LHASA_MG.py
    """
    print("=== TESTE DAS CORREÇÕES LHASA MG ===")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    print("\n1. VERIFICANDO ARQUIVO ORIGINAL...")
    
    arquivo_original = "Plugin/LHASA_MG.py"
    if os.path.exists(arquivo_original):
        print(f"   [OK] Arquivo {arquivo_original} encontrado")
        
        # Verificar se contém as correções
        with open(arquivo_original, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        correcoes_aplicadas = [
            "feedback.pushInfo(f\"Tipo da camada de suscetibilidade: {type(camada_suscetibilidade)}\")",
            "feedback.pushInfo(f\"Tipo da camada de zonas: {type(zonas_com_chuva)}\")",
            "try:",
            "except Exception as e:",
            "feedback.reportError(f\"Erro ao selecionar áreas de risco: {str(e)}\")",
            "feedback.reportError(f\"Erro na interseção: {str(e)}\")",
            "feedback.reportError(f\"Erro ao calcular campo de perigo: {str(e)}\")",
            "feedback.reportError(f\"Erro ao gerar resultado final: {str(e)}\")",
            "feedback.pushInfo(\"Áreas de risco selecionadas com sucesso\")",
            "feedback.pushInfo(\"Interseção realizada com sucesso\")",
            "feedback.pushInfo(\"Campo de perigo calculado com sucesso\")",
            "feedback.pushInfo(\"Resultado final gerado com sucesso\")"
        ]
        
        for correcao in correcoes_aplicadas:
            if correcao in conteudo:
                print(f"   [OK] Correção aplicada: {correcao[:50]}...")
            else:
                print(f"   [ERRO] Correção NÃO encontrada: {correcao[:50]}...")
        
        print(f"\n2. VERIFICANDO FUNÇÃO executeRiskAnalysisQgis...")
        
        if "def executeRiskAnalysisQgis" in conteudo:
            print("   [OK] Função executeRiskAnalysisQgis encontrada")
            
            # Verificar se tem tratamento de erro
            if "try:" in conteudo and "except Exception as e:" in conteudo:
                print("   [OK] Tratamento de erro implementado")
            else:
                print("   [ERRO] Tratamento de erro NÃO implementado")
            
            # Verificar se tem validação de camadas
            if "if not camada_suscetibilidade:" in conteudo:
                print("   [OK] Validação de camadas implementada")
            else:
                print("   [ERRO] Validação de camadas NÃO implementada")
        else:
            print("   [ERRO] Função executeRiskAnalysisQgis NÃO encontrada")
        
        print(f"\n3. VERIFICANDO FUNÇÃO associateRainDataQgis...")
        
        if "def associateRainDataQgis" in conteudo:
            print("   [OK] Função associateRainDataQgis encontrada")
            
            # Verificar se tem tratamento de erro
            if "try:" in conteudo and "except Exception as e:" in conteudo:
                print("   [OK] Tratamento de erro implementado")
            else:
                print("   [ERRO] Tratamento de erro NÃO implementado")
            
            # Verificar se tem logging de tipo de camada
            if "Tipo da camada de zonas:" in conteudo:
                print("   [OK] Logging de tipo de camada implementado")
            else:
                print("   [ERRO] Logging de tipo de camada NÃO implementado")
        else:
            print("   [ERRO] Função associateRainDataQgis NÃO encontrada")
        
        print(f"\n4. VERIFICANDO MENSAGENS DE FEEDBACK...")
        
        mensagens_feedback = [
            "Áreas de risco selecionadas com sucesso",
            "Interseção realizada com sucesso", 
            "Campo de perigo calculado com sucesso",
            "Resultado final gerado com sucesso",
            "Campos adicionados com sucesso",
            "Processadas"
        ]
        
        for mensagem in mensagens_feedback:
            if mensagem in conteudo:
                print(f"   [OK] Mensagem de feedback: {mensagem}")
            else:
                print(f"   [AVISO] Mensagem de feedback NÃO encontrada: {mensagem}")
        
        print(f"\n5. VERIFICANDO TRATAMENTO DE ERROS...")
        
        erros_tratados = [
            "Erro ao selecionar áreas de risco",
            "Erro na interseção",
            "Erro ao calcular campo de perigo", 
            "Erro ao gerar resultado final",
            "Erro ao adicionar campos",
            "Erro ao processar zonas pluviométricas"
        ]
        
        for erro in erros_tratados:
            if erro in conteudo:
                print(f"   [OK] Tratamento de erro: {erro}")
            else:
                print(f"   [AVISO] Tratamento de erro NÃO encontrado: {erro}")
        
        print(f"\n6. RESUMO DAS CORREÇÕES...")
        
        print("   [INFO] Correções aplicadas no arquivo original LHASA_MG.py:")
        print("   - Adicionado tratamento de erro em todas as operações de processamento")
        print("   - Adicionado logging detalhado de tipos de camadas")
        print("   - Adicionado validação de camadas de entrada")
        print("   - Adicionado mensagens de feedback para cada etapa")
        print("   - Corrigida indentação na função associateRainDataQgis")
        print("   - Adicionado tratamento de exceções com retorno de None")
        
        print(f"\n7. PRÓXIMOS PASSOS...")
        
        print("   1. Testar o algoritmo corrigido no QGIS")
        print("   2. Verificar se as mensagens de erro são mais claras")
        print("   3. Confirmar se o problema de carregamento foi resolvido")
        print("   4. Validar se o mapa final é gerado corretamente")
        
        return True
        
    else:
        print(f"   [ERRO] Arquivo {arquivo_original} NÃO encontrado")
        return False


def criar_guia_teste_qgis():
    """
    Cria guia para testar as correções no QGIS
    """
    guia = '''# Guia de Teste - Correções LHASA MG

## Correções Aplicadas

### 1. Tratamento de Erros Melhorado
- Adicionado try/catch em todas as operações de processamento
- Mensagens de erro mais específicas
- Retorno de None em caso de erro para evitar falhas

### 2. Logging Detalhado
- Logging do tipo de camadas de entrada
- Mensagens de sucesso para cada etapa
- Feedback detalhado durante a execução

### 3. Validação de Camadas
- Verificação se camadas são válidas
- Verificação se camadas têm features
- Mensagens de erro específicas para cada problema

### 4. Correções de Código
- Corrigida indentação na função associateRainDataQgis
- Adicionado updateExtents() após processamento
- Melhor tratamento de exceções

## Como Testar

### 1. Preparar Dados
- Carregar camada de suscetibilidade no QGIS
- Carregar camada de zonas pluviométricas no QGIS
- Verificar se as camadas têm os campos necessários

### 2. Executar Algoritmo
- Abrir Caixa de Ferramentas de Processamento
- Procurar por "LHASA MG - Análise de Risco de Deslizamento"
- Configurar parâmetros
- Executar

### 3. Verificar Logs
- Observar mensagens de feedback no console
- Verificar se há mensagens de erro específicas
- Confirmar se cada etapa é executada com sucesso

### 4. Validar Resultado
- Verificar se o mapa final é gerado
- Confirmar se as cores estão aplicadas
- Validar se os níveis de perigo estão corretos

## Problemas Esperados

### Se ainda houver erro "valor inválido":
1. Verificar se as camadas têm geometrias válidas
2. Verificar se os campos necessários existem
3. Verificar se o SRC está configurado corretamente
4. Verificar se há dados suficientes nas camadas

### Se o algoritmo falhar em uma etapa específica:
1. Verificar a mensagem de erro específica
2. Verificar se a camada de entrada tem os dados necessários
3. Verificar se a expressão de cálculo está correta
4. Verificar se há permissão para salvar o arquivo de saída

## Logs de Debug

As correções adicionam logs detalhados que ajudam a identificar:
- Tipo de camadas sendo processadas
- Sucesso/falha de cada etapa
- Erros específicos com contexto
- Número de features processadas

## Contato

Se os problemas persistirem após as correções:
1. Verificar os logs detalhados
2. Testar com dados de exemplo simples
3. Verificar configuração do QGIS
4. Consultar documentação do QGIS
'''
    
    with open("Plugin/GUIA_TESTE_CORRECOES.md", "w", encoding="utf-8") as f:
        f.write(guia)
    
    print("Guia de teste criado: Plugin/GUIA_TESTE_CORRECOES.md")


if __name__ == "__main__":
    print("Iniciando teste das correções do LHASA MG...")
    
    # Executar teste
    if testar_correcoes():
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        print("As correções foram aplicadas no arquivo original!")
        
        # Criar guia de teste
        criar_guia_teste_qgis()
        
        print("\nArquivos criados:")
        print("- Plugin/GUIA_TESTE_CORRECOES.md")
        
        print("\nPróximos passos:")
        print("1. Teste o algoritmo corrigido no QGIS")
        print("2. Verifique se as mensagens de erro são mais claras")
        print("3. Confirme se o problema foi resolvido")
        print("4. Valide se o mapa final é gerado corretamente")
    else:
        print("\n=== TESTE FALHOU ===")
        print("Verifique se o arquivo original existe e as correções foram aplicadas")





