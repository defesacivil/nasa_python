# -*- coding: utf-8 -*-
"""
Exemplo de Uso do Sistema de Logging LHASA MG
=============================================

Este script demonstra como usar o sistema de logging avançado
para rastrear a execução do algoritmo LHASA.

Autor: NASA LHASA Team
Versão: 1.0
Data: 2025
"""

import os
import sys
import time
from datetime import datetime

# Adicionar o diretório do plugin ao path
sys.path.append(os.path.dirname(__file__))

# Importar o sistema de logging
from logger import (
    lhasa_logger, log_event, log_error, log_warning, log_performance, 
    log_data_validation, log_api_call, log_geoprocessing, log_function_calls, 
    LogContext, get_session_summary, save_session_log
)


@log_function_calls
def exemplo_carregamento_dados():
    """
    Exemplo de função com logging de carregamento de dados
    """
    log_event("DATA_LOADING_START", "Iniciando carregamento de dados de exemplo")
    
    # Simular carregamento de dados
    time.sleep(1)  # Simular processamento
    
    # Simular dados carregados
    dados_simulados = {
        'estacoes': 25,
        'registros': 1500,
        'periodo': '2025-01-01 a 2025-01-02'
    }
    
    log_data_validation("DADOS_CARREGADOS", "PASS", 
        f"Carregados {dados_simulados['registros']} registros de {dados_simulados['estacoes']} estações", 
        dados_simulados)
    
    log_event("DATA_LOADING_SUCCESS", "Carregamento de dados concluído", dados_simulados)
    return dados_simulados


@log_function_calls
def exemplo_processamento_geografico():
    """
    Exemplo de função com logging de processamento geográfico
    """
    log_event("GEOPROCESSING_START", "Iniciando processamento geográfico")
    
    # Simular operações geográficas
    operacoes = [
        {'nome': 'Seleção de áreas de risco', 'features_entrada': 1000, 'features_saida': 150},
        {'nome': 'Interseção com zonas pluviométricas', 'features_entrada': 150, 'features_saida': 75},
        {'nome': 'Cálculo de níveis de perigo', 'features_entrada': 75, 'features_saida': 75},
        {'nome': 'Dissolução por nível de perigo', 'features_entrada': 75, 'features_saida': 5}
    ]
    
    for i, op in enumerate(operacoes):
        # Simular tempo de processamento
        tempo_processamento = 0.5 + (i * 0.2)
        time.sleep(tempo_processamento)
        
        log_geoprocessing(
            op['nome'], 
            op['features_entrada'], 
            op['features_saida'], 
            tempo_processamento, 
            success=True
        )
    
    log_event("GEOPROCESSING_SUCCESS", "Processamento geográfico concluído")
    return operacoes


@log_function_calls
def exemplo_chamada_api():
    """
    Exemplo de função com logging de chamadas de API
    """
    log_event("API_CALLS_START", "Iniciando chamadas de API")
    
    # Simular chamadas para API do INMET
    endpoints = [
        {'url': 'https://apitempo.inmet.gov.br/estacoes/T', 'method': 'GET'},
        {'url': 'https://apitempo.inmet.gov.br/token/estacao/2025-01-01/2025-01-02/A001/TOKEN', 'method': 'GET'},
        {'url': 'https://apitempo.inmet.gov.br/token/estacao/2025-01-01/2025-01-02/A002/TOKEN', 'method': 'GET'}
    ]
    
    for i, endpoint in enumerate(endpoints):
        # Simular tempo de resposta
        tempo_resposta = 0.3 + (i * 0.1)
        time.sleep(tempo_resposta)
        
        # Simular códigos de status
        status_codes = [200, 200, 204]  # Última chamada retorna "sem dados"
        
        log_api_call(
            "INMET", 
            endpoint['url'], 
            endpoint['method'], 
            status_codes[i], 
            tempo_resposta, 
            data_size=1024 * (i + 1)
        )
    
    log_event("API_CALLS_SUCCESS", "Chamadas de API concluídas")
    return len(endpoints)


def exemplo_analise_completa():
    """
    Exemplo de análise completa com logging detalhado
    """
    start_time = time.time()
    
    # Log de início do algoritmo
    lhasa_logger.log_algorithm_start("LHASA_EXEMPLO", {
        'tipo_analise': 'exemplo',
        'data_source': 'simulado',
        'regiao': 'Minas Gerais'
    })
    
    try:
        # Etapa 1: Carregamento de dados
        with LogContext("CARREGAMENTO_DADOS", "Carregando dados meteorológicos"):
            log_event("ETAPA_1", "Carregando dados meteorológicos", {
                'step': 1,
                'description': 'Carregamento de dados do INMET'
            })
            dados = exemplo_carregamento_dados()
        
        # Etapa 2: Chamadas de API
        with LogContext("CHAMADAS_API", "Realizando chamadas para API"):
            log_event("ETAPA_2", "Realizando chamadas para API", {
                'step': 2,
                'description': 'Busca de dados meteorológicos'
            })
            api_calls = exemplo_chamada_api()
        
        # Etapa 3: Processamento geográfico
        with LogContext("PROCESSAMENTO_GEOGRAFICO", "Processando dados geográficos"):
            log_event("ETAPA_3", "Processando dados geográficos", {
                'step': 3,
                'description': 'Análise de risco geográfica'
            })
            operacoes = exemplo_processamento_geografico()
        
        # Resumo final
        processing_time = time.time() - start_time
        
        log_performance("ANALISE_COMPLETA", processing_time, {
            'dados_carregados': dados['registros'],
            'chamadas_api': api_calls,
            'operacoes_geograficas': len(operacoes),
            'tempo_total': processing_time
        })
        
        # Log de sucesso
        lhasa_logger.log_algorithm_end("LHASA_EXEMPLO", True, {
            'processing_time_seconds': processing_time,
            'dados_processados': dados['registros'],
            'chamadas_api': api_calls,
            'operacoes_geograficas': len(operacoes)
        })
        
        log_event("ANALISE_SUCCESS", "Análise de exemplo concluída com sucesso", {
            'processing_time': round(processing_time, 2),
            'dados_processados': dados['registros']
        })
        
        return {
            'success': True,
            'dados': dados,
            'api_calls': api_calls,
            'operacoes': operacoes,
            'processing_time': processing_time
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Log de erro
        lhasa_logger.log_algorithm_end("LHASA_EXEMPLO", False, {
            'processing_time_seconds': processing_time,
            'error': str(e)
        })
        
        log_error("ANALISE_ERROR", "Erro na análise de exemplo", e, {
            'processing_time': round(processing_time, 2)
        })
        
        raise


def main():
    """
    Função principal de exemplo
    """
    print("=== EXEMPLO DE SISTEMA DE LOGGING LHASA MG ===")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Executar análise de exemplo
        resultado = exemplo_analise_completa()
        
        print("\n=== RESULTADO DA ANÁLISE ===")
        print(f"Sucesso: {resultado['success']}")
        print(f"Dados processados: {resultado['dados']['registros']}")
        print(f"Chamadas de API: {resultado['api_calls']}")
        print(f"Operações geográficas: {len(resultado['operacoes'])}")
        print(f"Tempo de processamento: {resultado['processing_time']:.2f}s")
        
    except Exception as e:
        print(f"\nErro na execução: {e}")
    
    finally:
        # Salvar log da sessão
        session_summary = get_session_summary()
        log_file = save_session_log()
        
        print("\n=== RESUMO DA SESSÃO ===")
        print(f"ID da Sessão: {session_summary['session_id']}")
        print(f"Duração Total: {session_summary['total_duration_seconds']:.2f}s")
        print(f"Total de Eventos: {session_summary['total_events']}")
        print(f"Erros: {session_summary['error_count']}")
        print(f"Avisos: {session_summary['warning_count']}")
        print(f"Log da Sessão: {log_file}")
        
        print("\n=== ARQUIVOS DE LOG GERADOS ===")
        print(f"1. Log principal: logs/LHASA_MG_{session_summary['session_id']}.log")
        print(f"2. Log de erros: logs/LHASA_ERRORS_{session_summary['session_id']}.log")
        print(f"3. Log da sessão: {log_file}")
        
        print("\n=== COMO USAR OS LOGS ===")
        print("1. Log principal: Contém todos os eventos da execução")
        print("2. Log de erros: Contém apenas erros críticos")
        print("3. Log da sessão: Arquivo JSON com resumo completo")
        print("\nOs logs permitem rastrear:")
        print("- Cada etapa do algoritmo")
        print("- Tempo de execução de cada operação")
        print("- Chamadas de API e seus resultados")
        print("- Processamento geográfico")
        print("- Erros e avisos")
        print("- Validação de dados")


if __name__ == "__main__":
    main()

