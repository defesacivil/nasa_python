# -*- coding: utf-8 -*-
"""
Sistema de Logging Avançado para LHASA MG
==========================================

Este módulo fornece um sistema de logging abrangente para rastrear
toda a execução do algoritmo LHASA, incluindo:

- Logs de eventos principais
- Logs de erro com tratamento de exceções
- Logs de performance e timing
- Logs de dados e validações
- Logs de API e conexões externas
- Logs de processamento geográfico

Autor: NASA LHASA Team
Versão: 1.0
Data: 2025
"""

import os
import sys
import time
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import json


class LhasaLogger:
    """
    Sistema de logging avançado para LHASA MG
    """
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Inicializar o sistema de logging
        
        Args:
            log_dir: Diretório para salvar os logs
            log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.start_time = time.time()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar diretório de logs se não existir
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurar logger principal
        self.logger = logging.getLogger('LHASA_MG')
        self.logger.setLevel(self.log_level)
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers()
        
        # Logs de sessão
        self.session_logs = []
        self.error_count = 0
        self.warning_count = 0
        
    def _setup_handlers(self):
        """Configurar handlers de logging"""
        
        # Handler para arquivo principal
        main_log_file = os.path.join(self.log_dir, f"LHASA_MG_{self.session_id}.log")
        file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formato dos logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Handler para erros críticos
        error_log_file = os.path.join(self.log_dir, f"LHASA_ERRORS_{self.session_id}.log")
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
    def log_event(self, event_type: str, message: str, data: Optional[Dict] = None):
        """
        Log de evento principal
        
        Args:
            event_type: Tipo do evento (INIT, API_CALL, PROCESSING, etc.)
            message: Mensagem descritiva
            data: Dados adicionais (opcional)
        """
        timestamp = datetime.now()
        log_entry = {
            'timestamp': timestamp.isoformat(),
            'event_type': event_type,
            'message': message,
            'data': data or {},
            'session_id': self.session_id
        }
        
        self.session_logs.append(log_entry)
        
        # Log no sistema padrão
        self.logger.info(f"[{event_type}] {message}")
        
        if data:
            self.logger.debug(f"Dados do evento: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    def log_error(self, error_type: str, message: str, exception: Optional[Exception] = None, 
                  context: Optional[Dict] = None):
        """
        Log de erro com contexto
        
        Args:
            error_type: Tipo do erro (API_ERROR, PROCESSING_ERROR, etc.)
            message: Mensagem descritiva
            exception: Exceção capturada (opcional)
            context: Contexto adicional (opcional)
        """
        self.error_count += 1
        
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': message,
            'exception': str(exception) if exception else None,
            'traceback': traceback.format_exc() if exception else None,
            'context': context or {},
            'session_id': self.session_id
        }
        
        self.session_logs.append(error_entry)
        
        # Log de erro
        self.logger.error(f"[{error_type}] {message}")
        
        if exception:
            self.logger.error(f"Exceção: {exception}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
        
        if context:
            self.logger.debug(f"Contexto do erro: {json.dumps(context, indent=2, ensure_ascii=False)}")
    
    def log_warning(self, warning_type: str, message: str, data: Optional[Dict] = None):
        """
        Log de aviso
        
        Args:
            warning_type: Tipo do aviso
            message: Mensagem descritiva
            data: Dados adicionais (opcional)
        """
        self.warning_count += 1
        
        warning_entry = {
            'timestamp': datetime.now().isoformat(),
            'warning_type': warning_type,
            'message': message,
            'data': data or {},
            'session_id': self.session_id
        }
        
        self.session_logs.append(warning_entry)
        self.logger.warning(f"[{warning_type}] {message}")
        
        if data:
            self.logger.debug(f"Dados do aviso: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict] = None):
        """
        Log de performance
        
        Args:
            operation: Nome da operação
            duration: Duração em segundos
            details: Detalhes adicionais (opcional)
        """
        performance_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'duration_seconds': duration,
            'details': details or {},
            'session_id': self.session_id
        }
        
        self.session_logs.append(performance_entry)
        self.logger.info(f"[PERFORMANCE] {operation}: {duration:.3f}s")
        
        if details:
            self.logger.debug(f"Detalhes de performance: {json.dumps(details, indent=2, ensure_ascii=False)}")
    
    def log_data_validation(self, validation_type: str, status: str, message: str, 
                           data_summary: Optional[Dict] = None):
        """
        Log de validação de dados
        
        Args:
            validation_type: Tipo de validação
            status: Status da validação (PASS, FAIL, WARNING)
            message: Mensagem descritiva
            data_summary: Resumo dos dados validados
        """
        validation_entry = {
            'timestamp': datetime.now().isoformat(),
            'validation_type': validation_type,
            'status': status,
            'message': message,
            'data_summary': data_summary or {},
            'session_id': self.session_id
        }
        
        self.session_logs.append(validation_entry)
        
        if status == "PASS":
            self.logger.info(f"[VALIDATION] {validation_type}: {message}")
        elif status == "WARNING":
            self.logger.warning(f"[VALIDATION] {validation_type}: {message}")
        else:
            self.logger.error(f"[VALIDATION] {validation_type}: {message}")
        
        if data_summary:
            self.logger.debug(f"Resumo dos dados: {json.dumps(data_summary, indent=2, ensure_ascii=False)}")
    
    def log_api_call(self, api_name: str, endpoint: str, method: str, status_code: int, 
                    response_time: float, data_size: Optional[int] = None):
        """
        Log de chamada de API
        
        Args:
            api_name: Nome da API
            endpoint: Endpoint chamado
            method: Método HTTP
            status_code: Código de status da resposta
            response_time: Tempo de resposta em segundos
            data_size: Tamanho dos dados em bytes (opcional)
        """
        api_entry = {
            'timestamp': datetime.now().isoformat(),
            'api_name': api_name,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_seconds': response_time,
            'data_size_bytes': data_size,
            'session_id': self.session_id
        }
        
        self.session_logs.append(api_entry)
        
        status_level = "INFO" if 200 <= status_code < 300 else "WARNING" if 400 <= status_code < 500 else "ERROR"
        getattr(self.logger, status_level.lower())(
            f"[API] {api_name} {method} {endpoint} - Status: {status_code} - Tempo: {response_time:.3f}s"
        )
        
        if data_size:
            self.logger.debug(f"Tamanho dos dados: {data_size} bytes")
    
    def log_geoprocessing(self, operation: str, input_features: int, output_features: int, 
                          processing_time: float, success: bool = True):
        """
        Log de processamento geográfico
        
        Args:
            operation: Nome da operação geográfica
            input_features: Número de features de entrada
            output_features: Número de features de saída
            processing_time: Tempo de processamento em segundos
            success: Se a operação foi bem-sucedida
        """
        geoprocessing_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'input_features': input_features,
            'output_features': output_features,
            'processing_time_seconds': processing_time,
            'success': success,
            'session_id': self.session_id
        }
        
        self.session_logs.append(geoprocessing_entry)
        
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"[GEOPROCESSING] {operation} - {status} - "
                        f"Input: {input_features}, Output: {output_features}, "
                        f"Time: {processing_time:.3f}s")
    
    def get_session_summary(self) -> Dict:
        """
        Obter resumo da sessão de logging
        
        Returns:
            Dicionário com resumo da sessão
        """
        total_time = time.time() - self.start_time
        
        return {
            'session_id': self.session_id,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'total_duration_seconds': total_time,
            'total_events': len(self.session_logs),
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'log_files': [
                f"LHASA_MG_{self.session_id}.log",
                f"LHASA_ERRORS_{self.session_id}.log"
            ]
        }
    
    def save_session_log(self, filename: Optional[str] = None):
        """
        Salvar log da sessão em arquivo JSON
        
        Args:
            filename: Nome do arquivo (opcional)
        """
        if not filename:
            filename = f"LHASA_SESSION_{self.session_id}.json"
        
        filepath = os.path.join(self.log_dir, filename)
        
        session_data = {
            'summary': self.get_session_summary(),
            'events': self.session_logs
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Log da sessão salvo em: {filepath}")
        return filepath
    
    def log_algorithm_start(self, algorithm_name: str, parameters: Dict):
        """
        Log de início do algoritmo
        
        Args:
            algorithm_name: Nome do algoritmo
            parameters: Parâmetros de entrada
        """
        self.log_event("ALGORITHM_START", f"Iniciando {algorithm_name}", {
            'algorithm': algorithm_name,
            'parameters': parameters,
            'python_version': sys.version,
            'platform': sys.platform
        })
    
    def log_algorithm_end(self, algorithm_name: str, success: bool, results: Optional[Dict] = None):
        """
        Log de fim do algoritmo
        
        Args:
            algorithm_name: Nome do algoritmo
            success: Se o algoritmo foi executado com sucesso
            results: Resultados do algoritmo (opcional)
        """
        status = "SUCCESS" if success else "FAILED"
        self.log_event("ALGORITHM_END", f"Finalizando {algorithm_name} - {status}", {
            'algorithm': algorithm_name,
            'success': success,
            'results': results or {}
        })
    
    def log_step(self, step_number: int, step_name: str, description: str, 
                 data_count: Optional[int] = None, processing_time: Optional[float] = None):
        """
        Log de etapa do algoritmo
        
        Args:
            step_number: Número da etapa
            step_name: Nome da etapa
            description: Descrição da etapa
            data_count: Quantidade de dados processados (opcional)
            processing_time: Tempo de processamento (opcional)
        """
        step_data = {
            'step_number': step_number,
            'step_name': step_name,
            'description': description
        }
        
        if data_count is not None:
            step_data['data_count'] = data_count
        
        if processing_time is not None:
            step_data['processing_time'] = processing_time
        
        self.log_event("ALGORITHM_STEP", f"Etapa {step_number}: {step_name}", step_data)


# Instância global do logger
lhasa_logger = LhasaLogger()


# Funções de conveniência para uso direto
def log_event(event_type: str, message: str, data: Optional[Dict] = None):
    """Log de evento"""
    lhasa_logger.log_event(event_type, message, data)


def log_error(error_type: str, message: str, exception: Optional[Exception] = None, 
              context: Optional[Dict] = None):
    """Log de erro"""
    lhasa_logger.log_error(error_type, message, exception, context)


def log_warning(warning_type: str, message: str, data: Optional[Dict] = None):
    """Log de aviso"""
    lhasa_logger.log_warning(warning_type, message, data)


def log_performance(operation: str, duration: float, details: Optional[Dict] = None):
    """Log de performance"""
    lhasa_logger.log_performance(operation, duration, details)


def log_data_validation(validation_type: str, status: str, message: str, 
                       data_summary: Optional[Dict] = None):
    """Log de validação de dados"""
    lhasa_logger.log_data_validation(validation_type, status, message, data_summary)


def log_api_call(api_name: str, endpoint: str, method: str, status_code: int, 
                response_time: float, data_size: Optional[int] = None):
    """Log de chamada de API"""
    lhasa_logger.log_api_call(api_name, endpoint, method, status_code, response_time, data_size)


def log_geoprocessing(operation: str, input_features: int, output_features: int, 
                     processing_time: float, success: bool = True):
    """Log de processamento geográfico"""
    lhasa_logger.log_geoprocessing(operation, input_features, output_features, processing_time, success)


def get_session_summary() -> Dict:
    """Obter resumo da sessão"""
    return lhasa_logger.get_session_summary()


def save_session_log(filename: Optional[str] = None) -> str:
    """Salvar log da sessão"""
    return lhasa_logger.save_session_log(filename)


# Decorator para logging automático de funções
def log_function_calls(func):
    """
    Decorator para logging automático de chamadas de função
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        function_name = func.__name__
        
        lhasa_logger.log_event("FUNCTION_START", f"Iniciando função {function_name}", {
            'function': function_name,
            'args_count': len(args),
            'kwargs_count': len(kwargs)
        })
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            lhasa_logger.log_event("FUNCTION_END", f"Função {function_name} concluída com sucesso", {
                'function': function_name,
                'duration': duration,
                'success': True
            })
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            lhasa_logger.log_error("FUNCTION_ERROR", f"Erro na função {function_name}", e, {
                'function': function_name,
                'duration': duration,
                'args': str(args)[:200],  # Limitar tamanho
                'kwargs': str(kwargs)[:200]
            })
            
            raise
    
    return wrapper


# Context manager para logging de blocos de código
class LogContext:
    """
    Context manager para logging de blocos de código
    """
    
    def __init__(self, context_name: str, description: str = ""):
        self.context_name = context_name
        self.description = description
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        lhasa_logger.log_event("CONTEXT_START", f"Iniciando contexto: {self.context_name}", {
            'context': self.context_name,
            'description': self.description
        })
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            lhasa_logger.log_event("CONTEXT_END", f"Contexto {self.context_name} concluído com sucesso", {
                'context': self.context_name,
                'duration': duration,
                'success': True
            })
        else:
            lhasa_logger.log_error("CONTEXT_ERROR", f"Erro no contexto {self.context_name}", exc_val, {
                'context': self.context_name,
                'duration': duration,
                'exception_type': str(exc_type)
            })


# Exemplo de uso
if __name__ == "__main__":
    # Teste do sistema de logging
    logger = LhasaLogger()
    
    # Log de início
    logger.log_algorithm_start("LHASA_MG", {"data_source": "INMET", "region": "MG"})
    
    # Log de etapas
    logger.log_step(1, "CARREGAR_ESTACOES", "Carregando estações do INMET")
    logger.log_step(2, "BUSCAR_DADOS", "Buscando dados meteorológicos")
    logger.log_step(3, "PROCESSAR_DADOS", "Processando dados de chuva")
    
    # Log de API
    logger.log_api_call("INMET", "/estacoes/T", "GET", 200, 1.5, 1024)
    
    # Log de validação
    logger.log_data_validation("ESTACOES", "PASS", "33 estações carregadas com sucesso", {
        'total_stations': 33,
        'active_stations': 30,
        'error_stations': 3
    })
    
    # Log de performance
    logger.log_performance("PROCESSAR_DADOS", 2.5, {
        'records_processed': 1000,
        'memory_usage_mb': 150
    })
    
    # Log de fim
    logger.log_algorithm_end("LHASA_MG", True, {
        'output_features': 150,
        'processing_time': 5.2
    })
    
    # Salvar log da sessão
    log_file = logger.save_session_log()
    print(f"Log salvo em: {log_file}")
    
    # Mostrar resumo
    summary = logger.get_session_summary()
    print(f"Resumo da sessão: {summary}")



