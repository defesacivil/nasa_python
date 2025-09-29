# -*- coding: utf-8 -*-
"""
Teste Simples do Sistema de Logging LHASA MG
============================================

Este script testa o sistema de logging sem caracteres especiais.
"""

import os
import sys
import time
from datetime import datetime

# Adicionar o diretório do plugin ao path
sys.path.append(os.path.dirname(__file__))

def test_logging_system():
    """
    Teste completo do sistema de logging
    """
    print("=== TESTE DO SISTEMA DE LOGGING LHASA MG ===")
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Importar o sistema de logging
        from logger import (
            lhasa_logger, log_event, log_error, log_warning, log_performance, 
            log_data_validation, log_api_call, log_geoprocessing, log_function_calls, 
            LogContext, get_session_summary, save_session_log
        )
        
        print("[OK] Sistema de logging importado com sucesso")
        
        # Teste 1: Logs básicos
        print("\n1. Testando logs básicos...")
        log_event("TEST_START", "Iniciando teste do sistema de logging")
        log_warning("TEST_WARNING", "Este é um aviso de teste")
        
        # Teste 2: Logs de performance
        print("2. Testando logs de performance...")
        start_time = time.time()
        time.sleep(0.1)  # Simular processamento
        duration = time.time() - start_time
        log_performance("TEST_OPERATION", duration, {
            'registros_processados': 100,
            'memoria_utilizada': '50MB'
        })
        
        # Teste 3: Logs de validação
        print("3. Testando logs de validação...")
        log_data_validation("TEST_VALIDATION", "PASS", "Dados validados com sucesso", {
            'dados_validados': 50,
            'erros_encontrados': 0
        })
        
        # Teste 4: Logs de API
        print("4. Testando logs de API...")
        log_api_call("TEST_API", "https://api.exemplo.com/test", "GET", 200, 0.5, 1024)
        
        # Teste 5: Logs de processamento geográfico
        print("5. Testando logs de processamento geográfico...")
        log_geoprocessing("TEST_GEOPROCESSING", 100, 50, 1.2, True)
        
        # Teste 6: Context manager
        print("6. Testando context manager...")
        with LogContext("TEST_CONTEXT", "Testando context manager"):
            time.sleep(0.05)
            log_event("CONTEXT_TEST", "Dentro do context manager")
        
        # Teste 7: Decorator para função
        print("7. Testando decorator...")
        
        @log_function_calls
        def funcao_teste():
            time.sleep(0.05)
            return "resultado_teste"
        
        resultado = funcao_teste()
        print(f"   Resultado da função: {resultado}")
        
        # Teste 8: Logs de algoritmo
        print("8. Testando logs de algoritmo...")
        lhasa_logger.log_algorithm_start("TEST_ALGORITHM", {
            'tipo': 'teste',
            'parametros': {'param1': 'valor1'}
        })
        
        time.sleep(0.1)
        
        lhasa_logger.log_algorithm_end("TEST_ALGORITHM", True, {
            'resultado': 'sucesso',
            'tempo_execucao': 0.1
        })
        
        # Teste 9: Simulação de erro
        print("9. Testando logs de erro...")
        try:
            raise ValueError("Erro simulado para teste")
        except Exception as e:
            log_error("TEST_ERROR", "Erro simulado para teste", e, {
                'contexto': 'teste_de_logging'
            })
        
        print("\n[OK] Todos os testes de logging concluídos com sucesso!")
        
        # Salvar log da sessão
        print("\n10. Salvando log da sessão...")
        session_summary = get_session_summary()
        log_file = save_session_log()
        
        print(f"[OK] Log da sessão salvo em: {log_file}")
        
        # Mostrar resumo
        print("\n=== RESUMO DA SESSÃO DE TESTE ===")
        print(f"ID da Sessão: {session_summary['session_id']}")
        print(f"Duração Total: {session_summary['total_duration_seconds']:.2f}s")
        print(f"Total de Eventos: {session_summary['total_events']}")
        print(f"Erros: {session_summary['error_count']}")
        print(f"Avisos: {session_summary['warning_count']}")
        
        # Verificar arquivos gerados
        print("\n=== ARQUIVOS DE LOG GERADOS ===")
        log_dir = "logs"
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.log') or f.endswith('.json')]
            for log_file in sorted(log_files):
                file_path = os.path.join(log_dir, log_file)
                file_size = os.path.getsize(file_path)
                print(f"  {log_file} ({file_size} bytes)")
        
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        return True
        
    except ImportError as e:
        print(f"[ERRO] Erro ao importar sistema de logging: {e}")
        print("Verifique se o arquivo logger.py está no diretório correto")
        return False
        
    except Exception as e:
        print(f"[ERRO] Erro durante o teste: {e}")
        return False


def test_logging_without_qgis():
    """
    Teste específico para ambiente sem QGIS
    """
    print("\n=== TESTE SEM DEPENDÊNCIAS DO QGIS ===")
    
    try:
        # Simular execução do LHASA sem QGIS
        from logger import lhasa_logger, log_event, log_error, log_performance
        
        # Simular carregamento de dados
        log_event("DATA_LOADING", "Simulando carregamento de dados do INMET")
        
        # Simular processamento
        start_time = time.time()
        time.sleep(0.2)
        duration = time.time() - start_time
        
        log_performance("DATA_PROCESSING", duration, {
            'registros_processados': 1000,
            'estacoes_carregadas': 25
        })
        
        # Simular erro de API
        log_error("API_ERROR", "Simulação de erro de API", 
                 Exception("Timeout na conexão"), {
                     'url': 'https://apitempo.inmet.gov.br/estacoes/T',
                     'timeout': 30
                 })
        
        print("[OK] Teste sem QGIS concluído com sucesso")
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro no teste sem QGIS: {e}")
        return False


if __name__ == "__main__":
    print("Iniciando testes do sistema de logging...")
    
    # Teste principal
    success1 = test_logging_system()
    
    # Teste sem QGIS
    success2 = test_logging_without_qgis()
    
    if success1 and success2:
        print("\n[SUCESSO] TODOS OS TESTES PASSARAM!")
        print("\nO sistema de logging está funcionando corretamente.")
        print("Você pode agora usar o sistema no algoritmo LHASA.")
    else:
        print("\n[FALHA] ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima e corrija os problemas.")
    
    print("\nPara usar o sistema de logging no LHASA:")
    print("1. Execute: python LHASA_MG.py -test")
    print("2. Execute: python exemplo_logging.py")
    print("3. Consulte: LOGGING_GUIDE.md")

