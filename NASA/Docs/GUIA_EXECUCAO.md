# GUIA DE EXECUÇÃO - LHASA RIO
## Sistema de Análise de Riscos de Deslizamento | NASA | IPP-RJ

---

## 📋 PRÉ-REQUISITOS

### 1. Sistema Operacional
- ✅ **Windows, macOS ou Linux**
- ✅ **Python 3.11+** instalado

### 2. Dependências Necessárias
```bash
# Instalar dependências básicas
pip install urllib3 unidecode
```

### 3. Estrutura de Diretórios
```
NASA/
├── LHASA_RIO.py          # Código principal
├── logger.py             # Sistema de logs
├── arcpy_mock.py         # Mock do ArcGIS (desenvolvimento)
├── requirements.txt      # Dependências
├── logs/                 # Diretório de logs (criado automaticamente)
└── data/                 # Diretório de dados (opcional)
```

---

## 🚀 COMO EXECUTAR O CÓDIGO

### **OPÇÃO 1: Execução Simples (Recomendada)**

```bash
# Navegar até o diretório do projeto
cd /caminho/para/NASA

# Executar o sistema no modo nowcast (dados atuais)
python LHASA_RIO.py -n
```

### **OPÇÃO 2: Execução com Saída Detalhada no Terminal**

```bash
python -c "
import sys
sys.path.append('.')
from LHASA_RIO import *

print('=== INICIANDO SISTEMA LHASA RIO ===')
print('Carregando configurações...')

initialize()
print('✅ Inicialização concluída')

print('\\n=== EXECUTANDO NOWCAST ===')
nowcast()
print('✅ Processamento concluído')
"
```

### **OPÇÃO 3: Execução com Dados Históricos**

```bash
# Formato: python LHASA_RIO.py -h "DD/MM/AAAA" "DD/MM/AAAA" "HH:MM:SS" "HH:MM:SS"
python LHASA_RIO.py -h "01/01/2024" "01/01/2024" "08:00:00" "20:00:00"
```

---

## 📊 MODOS DE EXECUÇÃO

### **Modo Nowcast (`-n`)**
- **Função**: Análise de dados meteorológicos atuais
- **Uso**: Monitoramento em tempo real
- **Comando**: `python LHASA_RIO.py -n`

### **Modo Histórico (`-h`)**
- **Função**: Análise de dados históricos específicos
- **Uso**: Análise retrospectiva de eventos
- **Comando**: `python LHASA_RIO.py -h "DD/MM/AAAA" "DD/MM/AAAA" "HH:MM:SS" "HH:MM:SS"`

**Exemplo:**
```bash
python LHASA_RIO.py -h "15/03/2024" "15/03/2024" "06:00:00" "18:00:00"
```

---

## 🔧 PASSO A PASSO DETALHADO

### **PASSO 1: Preparação do Ambiente**

```bash
# 1.1 - Verificar versão do Python
python --version
# Deve ser Python 3.11 ou superior

# 1.2 - Navegar para o diretório
cd /Users/matheusestrela/Documents/NASA

# 1.3 - Verificar arquivos necessários
ls -la
# Deve conter: LHASA_RIO.py, logger.py, arcpy_mock.py
```

### **PASSO 2: Instalação de Dependências**

```bash
# 2.1 - Instalar bibliotecas necessárias
pip install urllib3 unidecode

# 2.2 - Verificar instalação
python -c "import urllib3, unidecode; print('✅ Dependências instaladas')"
```

### **PASSO 3: Primeira Execução**

```bash
# 3.1 - Executar teste básico
python LHASA_RIO.py -n

# 3.2 - Verificar se executou sem erros
echo "Status da execução: $?"
# Deve retornar: Status da execução: 0
```

### **PASSO 4: Verificação dos Logs**

```bash
# 4.1 - Verificar se o diretório de logs foi criado
ls -la logs/

# 4.2 - Ver os logs mais recentes
tail -20 logs/LHASA_RIO.log

# 4.3 - Monitorar logs em tempo real (opcional)
tail -f logs/LHASA_RIO.log
```

---

## 📈 SAÍDA ESPERADA

### **Execução Bem-sucedida:**

```
ArcGIS não encontrado. Usando mock para desenvolvimento.
[14:36:40] [INFO] ---- PROCESSAMENTO DE DADOS ATUAIS DE CHUVA ----
[14:36:40] [INFO] [CARREGANDO DADOS PARA PROCESSAMENTO]
[14:36:40] [INFO] #01 | CARGA DE DADOS DAS ESTACOES PLUVIOMETRICAS
[14:36:40] [INFO] Carregando estações do INMET para o Rio de Janeiro...
[14:36:46] [INFO] Encontradas 26 estações operantes no RJ
[14:36:46] [INFO] Buscando dados para A628: ANGRA DOS REIS
[14:36:46] [INFO] Buscando dados para A606: ARRAIAL DO CABO
...
[14:36:50] [INFO] #10 | APAGANDO DADOS DE PROCESSAMENTO
✅ Processamento concluído
```

### **Indicadores de Sucesso:**
- ✅ `ArcGIS não encontrado. Usando mock para desenvolvimento.`
- ✅ `Encontradas 26 estações operantes no RJ`
- ✅ `#01 | CARGA DE DADOS DAS ESTACOES PLUVIOMETRICAS`
- ✅ `#10 | APAGANDO DADOS DE PROCESSAMENTO`
- ✅ Exit code: 0

---

## 🔍 MONITORAMENTO E LOGS

### **Localização dos Logs:**
```bash
# Arquivo principal de logs
logs/LHASA_RIO.log
```

### **Comandos Úteis para Monitoramento:**

```bash
# Ver últimas 50 linhas do log
tail -50 logs/LHASA_RIO.log

# Monitorar logs em tempo real
tail -f logs/LHASA_RIO.log

# Buscar por erros específicos
grep "ERROR" logs/LHASA_RIO.log

# Buscar por estações processadas
grep "Buscando dados" logs/LHASA_RIO.log

# Ver estatísticas de execução
grep "Total de.*estações" logs/LHASA_RIO.log
```

---

## ⚡ EXECUÇÃO RÁPIDA (COPY & PASTE)

### **Para Usuários Avançados:**

```bash
# Execução completa em uma linha
cd /Users/matheusestrela/Documents/NASA && python LHASA_RIO.py -n && echo "✅ Execução concluída com sucesso!"
```

### **Script de Execução Automática:**

```bash
#!/bin/bash
echo "🚀 Iniciando LHASA RIO..."
cd /Users/matheusestrela/Documents/NASA

echo "📦 Verificando dependências..."
python -c "import urllib3, unidecode" || { echo "❌ Dependências não encontradas. Execute: pip install urllib3 unidecode"; exit 1; }

echo "⚡ Executando análise..."
python LHASA_RIO.py -n

echo "📊 Verificando logs..."
tail -10 logs/LHASA_RIO.log

echo "✅ Processo finalizado!"
```

---

## 🛠️ SOLUÇÃO DE PROBLEMAS

### **Erro: "ModuleNotFoundError"**
```bash
# Solução: Instalar dependências
pip install urllib3 unidecode
```

### **Erro: "Permission denied"**
```bash
# Solução: Verificar permissões
chmod +x LHASA_RIO.py
```

### **Erro: "No such file or directory"**
```bash
# Solução: Verificar diretório atual
pwd
ls -la LHASA_RIO.py
```

### **Sem saída no terminal**
```bash
# Solução: Usar execução detalhada (Opção 2)
# Ou verificar logs: tail -f logs/LHASA_RIO.log
```

---

## 📚 INFORMAÇÕES ADICIONAIS

### **Estações Monitoradas (26 no Rio de Janeiro):**
- ANGRA DOS REIS (A628)
- ARRAIAL DO CABO (A606)
- CAMPOS DOS GOYTACAZES (A607)
- DUQUE DE CAXIAS - XEREM (A603)
- NITERÓI (A627)
- RIO DE JANEIRO - COPACABANA (A652)
- RIO DE JANEIRO - JACAREPAGUÁ (A636)
- TERESÓPOLIS (A618)
- E mais 18 estações...

### **Etapas de Processamento:**
1. Carga de estações pluviométricas
2. Carga de dados atuais de chuva (INMET)
3. Associação zona pluviométrica vs dados
4. Seleção de áreas de risco
5. Relacionamento volume vs área de risco
6. Criação de campo de risco
7. Cálculo de campo de risco
8. Seleção de áreas de perigo
9. Agregação de feições semelhantes
10. Geração de saídas (Shapefile/SDE)

### **APIs Utilizadas:**
- **INMET**: `https://apitempo.inmet.gov.br/estacoes/T`
- **Fallback**: API original do Rio de Janeiro

---

## 📞 SUPORTE

Para dúvidas ou problemas:
1. Verificar logs em `logs/LHASA_RIO.log`
2. Consultar este guia de execução
3. Verificar relatórios técnicos (`RELATORIO_*.md`)

---

**Desenvolvido por:** Instituto Pereira Passos | NASA | Rio de Janeiro  
**Versão:** 2.1 com integração INMET  
**Última atualização:** Setembro 2025
