# Guia do Sistema de Logging LHASA MG

## Visão Geral

O sistema de logging avançado do LHASA MG foi projetado para fornecer rastreamento completo da execução do algoritmo, permitindo:

- **Monitoramento em tempo real** de cada etapa do processo
- **Identificação rápida de problemas** com logs de erro detalhados
- **Análise de performance** com métricas de tempo
- **Validação de dados** com logs de qualidade
- **Rastreamento de APIs** com logs de chamadas externas
- **Processamento geográfico** com logs de operações espaciais

## Estrutura dos Logs

### 1. Logs Principais

#### `LHASA_MG_YYYYMMDD_HHMMSS.log`
- **Conteúdo**: Todos os eventos da execução
- **Formato**: Texto legível com timestamps
- **Uso**: Análise geral da execução

#### `LHASA_ERRORS_YYYYMMDD_HHMMSS.log`
- **Conteúdo**: Apenas erros críticos
- **Formato**: Texto com stack traces
- **Uso**: Identificação rápida de problemas

#### `LHASA_SESSION_YYYYMMDD_HHMMSS.json`
- **Conteúdo**: Resumo completo da sessão
- **Formato**: JSON estruturado
- **Uso**: Análise programática e relatórios

### 2. Tipos de Logs

#### Logs de Eventos
```python
log_event("EVENT_TYPE", "Descrição do evento", {
    'parametro1': 'valor1',
    'parametro2': 'valor2'
})
```

#### Logs de Erro
```python
log_error("ERROR_TYPE", "Descrição do erro", exception, {
    'contexto': 'informações_adicionais'
})
```

#### Logs de Performance
```python
log_performance("OPERATION_NAME", duration_seconds, {
    'registros_processados': 1000,
    'memoria_utilizada': '150MB'
})
```

#### Logs de Validação
```python
log_data_validation("VALIDATION_TYPE", "PASS/FAIL/WARNING", "Mensagem", {
    'dados_validados': 500,
    'erros_encontrados': 0
})
```

#### Logs de API
```python
log_api_call("API_NAME", "endpoint", "GET", 200, 1.5, 1024)
```

#### Logs de Processamento Geográfico
```python
log_geoprocessing("OPERATION_NAME", input_features, output_features, processing_time, success)
```

## Exemplos de Uso

### 1. Execução Básica

```python
from logger import log_event, log_error, log_performance

# Log de início
log_event("ALGORITHM_START", "Iniciando análise LHASA")

# Log de performance
start_time = time.time()
# ... processamento ...
duration = time.time() - start_time
log_performance("DATA_PROCESSING", duration)

# Log de erro (se necessário)
try:
    # ... código ...
except Exception as e:
    log_error("PROCESSING_ERROR", "Erro no processamento", e)
```

### 2. Context Manager

```python
from logger import LogContext

with LogContext("DATA_LOADING", "Carregando dados do INMET"):
    # Todo código aqui será automaticamente logado
    load_data()
```

### 3. Decorator para Funções

```python
from logger import log_function_calls

@log_function_calls
def minha_funcao():
    # A função será automaticamente logada
    return resultado
```

## Interpretação dos Logs

### 1. Logs de Eventos Principais

```
[INITIALIZATION] - Inicialização do ambiente
[API_CALL_START] - Início de chamada de API
[STATION_DATA_START] - Início de carregamento de dados de estação
[PLUVIOMETRIC_DATA_START] - Início de carregamento de dados pluviométricos
[GEOPROCESSING_START] - Início de processamento geográfico
[ANALYSIS_START] - Início da análise de risco
```

### 2. Logs de Erro Comuns

```
[API_CONNECTION_ERROR] - Problemas de conexão com API
[STATION_DATA_ERROR] - Erro ao carregar dados de estação
[VALIDATION_ERROR] - Erro na validação de dados
[GEOPROCESSING_ERROR] - Erro no processamento geográfico
```

### 3. Logs de Performance

```
[PERFORMANCE] - Tempo de execução de operações
[API_CALL] - Tempo de resposta de APIs
[GEOPROCESSING] - Tempo de processamento geográfico
```

## Análise de Problemas

### 1. Identificar Gargalos de Performance

Procure por logs de performance com tempo alto:
```
[PERFORMANCE] LOAD_PLUVIOMETRIC_DATA: 15.234s
```

### 2. Identificar Problemas de API

Procure por códigos de status HTTP diferentes de 200:
```
[API] INMET GET /estacoes/T - Status: 500 - Tempo: 30.000s
```

### 3. Identificar Problemas de Dados

Procure por logs de validação com status "FAIL":
```
[VALIDATION] STATION_DATA: FAIL - Dados inválidos para estação A001
```

## Monitoramento em Tempo Real

### 1. Console Output

Durante a execução, você verá:
```
2025/01/23 14:30:15 | INFO     | initialize                | [INITIALIZATION] Iniciando configuração do ambiente LHASA
2025/01/23 14:30:16 | INFO     | loadInmetStations         | [API_CALL_START] Iniciando busca de estações do INMET
2025/01/23 14:30:17 | INFO     | loadInmetStations         | [API] INMET GET https://apitempo.inmet.gov.br/estacoes/T - Status: 200 - Tempo: 1.234s
```

### 2. Arquivos de Log

Os logs são salvos automaticamente em:
- `logs/LHASA_MG_YYYYMMDD_HHMMSS.log`
- `logs/LHASA_ERRORS_YYYYMMDD_HHMMSS.log`
- `logs/LHASA_SESSION_YYYYMMDD_HHMMSS.json`

## Configuração Avançada

### 1. Níveis de Log

```python
from logger import LhasaLogger

# Configurar nível de log
logger = LhasaLogger(log_level="DEBUG")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 2. Diretório Personalizado

```python
logger = LhasaLogger(log_dir="meus_logs")
```

### 3. Logs Específicos

```python
# Log apenas de erros
logger.logger.setLevel(logging.ERROR)

# Log de debug detalhado
logger.logger.setLevel(logging.DEBUG)
```

## Exemplo Completo

Execute o script de exemplo para ver o sistema em ação:

```bash
python exemplo_logging.py
```

Este script demonstra:
- Carregamento de dados com logging
- Chamadas de API simuladas
- Processamento geográfico
- Análise completa com resumo

## Troubleshooting

### 1. Logs não aparecem

- Verifique se o diretório `logs/` existe
- Verifique permissões de escrita
- Verifique se o logger foi inicializado

### 2. Logs muito verbosos

- Ajuste o nível de log para `WARNING` ou `ERROR`
- Use filtros específicos para eventos importantes

### 3. Performance impactada

- O sistema de logging é otimizado para baixo impacto
- Em caso de problemas, desabilite logs de debug
- Use logs assíncronos para operações críticas

## Integração com QGIS

O sistema de logging está totalmente integrado com o QGIS:

1. **Logs aparecem no console do QGIS**
2. **Feedback para o usuário em tempo real**
3. **Logs salvos automaticamente**
4. **Resumo da sessão ao final**

## Manutenção dos Logs

### 1. Limpeza Automática

Configure limpeza automática de logs antigos:

```python
# Exemplo de limpeza (implementar conforme necessário)
import glob
import os
from datetime import datetime, timedelta

def limpar_logs_antigos(dias=30):
    cutoff_date = datetime.now() - timedelta(days=dias)
    for log_file in glob.glob("logs/*.log"):
        if os.path.getmtime(log_file) < cutoff_date.timestamp():
            os.remove(log_file)
```

### 2. Rotação de Logs

Para execuções longas, considere rotação de logs:

```python
# Implementar rotação baseada em tamanho ou tempo
```

## Conclusão

O sistema de logging do LHASA MG fornece visibilidade completa da execução do algoritmo, facilitando:

- **Debugging** de problemas
- **Otimização** de performance
- **Monitoramento** de qualidade
- **Auditoria** de execuções
- **Relatórios** detalhados

Use este sistema para entender completamente o que está acontecendo durante a execução do algoritmo LHASA.
