# RELATÓRIO DE ANÁLISE DO CÓDIGO LHASA_RIO.py

## 1. RESUMO EXECUTIVO

O código `LHASA_RIO.py` é um sistema de análise de riscos de deslizamentos desenvolvido pelo Instituto Pereira Passos (IPP) do Rio de Janeiro em parceria com a NASA. O sistema processa dados pluviométricos em tempo real e históricos para gerar alertas de risco de deslizamento em diferentes zonas da cidade do Rio de Janeiro.

**Versão:** 2.1  
**Instituição:** IPP - Instituto Pereira Passos | Rio de Janeiro | RJ  
**Projeto:** LHASA RIO | NASA | Nowcast  

---

## 2. PRINCIPAIS BIBLIOTECAS E DEPENDÊNCIAS

### 2.1 Bibliotecas Externas
- **arcpy**: Biblioteca principal do ArcGIS para processamento geoespacial
- **urllib3**: Cliente HTTP para requisições web
- **unidecode**: Conversão de caracteres Unicode para ASCII

### 2.2 Bibliotecas Padrão do Python
- **sys, os**: Interação com sistema operacional
- **shutil, copy, glob**: Manipulação de arquivos e diretórios
- **logging**: Sistema de logs
- **socket**: Comunicação de rede
- **json, csv**: Processamento de dados estruturados
- **datetime**: Manipulação de datas e horários

### 2.3 Módulos Locais
- **logger**: Módulo personalizado de logging (importado como `log`)

---

## 3. FUNCIONALIDADE DO CÓDIGO-FONTE

### 3.1 Estrutura Geral

O sistema está organizado em três componentes principais:

1. **Carregamento de Dados** (Data Loading)
2. **Análise de Riscos** (Risk Analysis)
3. **Geração de Saídas** (Output Generation)

### 3.2 Principais Funções

#### 3.2.1 Funções de Inicialização
- **`initialize()`**: Configura o ambiente ArcGIS, sistema de logs e variáveis globais

#### 3.2.2 Funções de Carregamento de Dados
- **`loadPluviometricZones()`**: Carrega dados das zonas pluviométricas do Rio de Janeiro
- **`loadPluviometricData()`**: Obtém dados atuais de chuva via API web
- **`loadNowData()`**: Processa dados de chuva em tempo real
- **`loadHistoricalData()`**: Processa dados históricos de chuva

#### 3.2.3 Funções de Busca e Localização
- **`findPluviometricZone()`**: Localiza zona pluviométrica por nome ou código
- **`findPluviometricData()`**: Localiza dados pluviométricos por estação
- **`findStationDefinition()`**: Localiza definição de estação meteorológica

#### 3.2.4 Funções de Análise
- **`doAnalysis()`**: Executa análise completa de risco de deslizamento
- **`nowcast()`**: Processamento para dados atuais
- **`historicalcast()`**: Processamento para dados históricos

### 3.3 Estruturas de Dados

#### 3.3.1 Templates de Dados
- **`TPL_PZ_ITEM`**: Template para dados de zona pluviométrica
- **`TPL_PH_ITEM`**: Template para dados históricos de pluviômetro

#### 3.3.2 Arrays Globais
- **`ARR_HD`**: Dados históricos
- **`ARR_PZ`**: Zonas pluviométricas
- **`ARR_PD`**: Dados pluviométricos
- **`ARR_ST`**: Definições de estações (33 estações do Rio de Janeiro)

### 3.4 Algoritmo de Análise de Risco

O sistema utiliza um algoritmo que considera:

1. **Dados de Susceptibilidade**: Classificação do terreno (Baixa=1, Média=2, Alta=3)
2. **Dados Pluviométricos**: Chuva em diferentes intervalos (15min, 1h, 4h, 24h, 96h)

#### Critérios de Classificação de Risco:

**Condições de Alerta Moderado/Alto:**
- H01 ≥ 50mm e < 70mm, OU
- H24 ≥ 140mm e < 185mm, OU
- H96 ≥ 185mm e < 255mm E H24 ≥ 55mm e < 100mm

**Condições de Alerta Crítico:**
- H01 ≥ 70mm, OU
- H24 ≥ 185mm, OU
- H96 ≥ 255mm E H24 ≥ 100mm

**Matriz de Classificação:**
| Susceptibilidade | Condição Moderada | Condição Crítica |
|------------------|-------------------|------------------|
| Baixa (1)        | SEM PERIGO        | SEM PERIGO       |
| Média (2)        | MODERADO          | MUITO ALTO       |
| Alta (3)         | ALTO              | CRÍTICO          |

### 3.5 Estações Pluviométricas

O sistema monitora 33 estações distribuídas pelo Rio de Janeiro:

1. VIDIGAL, 2. URCA, 3. ROCINHA, 4. TIJUCA, 5. SANTA TERESA,
6. COPACABANA, 7. GRAJAU, 8. ILHA DO GOVERNADOR, 9. PENHA,
10. MADUREIRA, 11. IRAJA, 12. BANGU, 13. PIEDADE, 15. SAUDE,
16. JARDIM BOTANICO, 17. BARRA/ITANHANGA, 18. JACAREPAGUA/CIDADE DE DEUS,
19. BARRA/RIO CENTRO, 20. GUARATIBA, 21. ESTRADA GRAJAU/JACAREPAGUA,
22. SANTA CRUZ, 23. GRANDE MEIER, 24. ANCHIETA, 25. GROTA FUNDA,
26. CAMPO GRANDE, 27. SEPETIBA, 28. ALTO DA BOA VISTA,
29. AV. BRASIL/MENDANHA, 30. RECREIO DOS BANDEIRANTES, 31. LARANJEIRAS,
32. SAO CRISTOVAO, 33. TIJUCA/MUDA

### 3.6 Fluxo de Processamento

#### Para Dados Atuais (`nowcast()`):
1. Carrega zonas pluviométricas
2. Obtém dados atuais via API
3. Associa dados de chuva às zonas
4. Executa análise de risco
5. Gera saídas em GDB e SDE

#### Para Dados Históricos (`historicalcast()`):
1. Valida parâmetros de período
2. Carrega dados históricos de arquivos
3. Processa e filtra dados por período
4. Associa às zonas pluviométricas
5. Executa análise de risco
6. Gera saídas

### 3.7 Configurações e Caminhos

- **Workspace Base**: `data/LHASA-DATA.gdb`
- **Dados SDE**: Conexão com servidor geoespacial
- **API de Chuva**: `http://websempre.rio.rj.gov.br/json/chuvas`
- **Logs**: Armazenados em `logs/LHASA_RIO.log`

### 3.8 Saídas do Sistema

1. **Shapefile**: `data/input/RJ_LHASA_NOWCAST.shp`
2. **Feature Classes**: Armazenadas em geodatabase
3. **Tabelas SDE**: Para integração com sistemas corporativos
4. **Logs**: Registro detalhado de processamento

---

## 4. ARQUITETURA E DESIGN

### 4.1 Padrões Utilizados
- **Modular**: Funções especializadas para cada etapa
- **Template Pattern**: Templates para estruturas de dados
- **Data Pipeline**: Fluxo sequencial de processamento

### 4.2 Integração com Sistemas Externos
- **ArcGIS**: Processamento geoespacial
- **APIs Web**: Coleta de dados meteorológicos
- **SDE**: Banco de dados geoespaciais corporativo

### 4.3 Tratamento de Erros
- Sistema de logging abrangente
- Validação de parâmetros de entrada
- Movimentação de arquivos com erro para pasta específica

---

## 5. CONSIDERAÇÕES TÉCNICAS

### 5.1 Dependências Críticas
- **ArcGIS License**: Necessária para execução do arcpy
- **Conectividade de Rede**: Para APIs e SDE
- **Estrutura de Diretórios**: Paths específicos devem existir

### 5.2 Limitações
- Processamento histórico limitado a mesmo ano/mês/dia
- Dependência de dados externos (APIs)
- Requer ambiente ArcGIS configurado

### 5.3 Performance
- Processamento em memória (in_memory workspace)
- Otimizações para grandes volumes de dados históricos
- Sistema de cache para zonas pluviométricas

---

## 6. MODO DE EXECUÇÃO

O sistema aceita dois modos de execução via linha de comando:

```bash
# Processamento de dados atuais (nowcast)
python LHASA_RIO.py -n

# Processamento histórico
python LHASA_RIO.py -h "DD/MM/AAAA" "DD/MM/AAAA" "HH:MM:SS" "HH:MM:SS"
```

**Exemplo histórico:**
```bash
python LHASA_RIO.py -h "01/01/2019" "01/01/2019" "08:00:00" "20:00:00"
```

---

Este sistema representa uma solução robusta para monitoramento de riscos de deslizamento, integrando dados meteorológicos em tempo real com análise geoespacial para proteção da população carioca.
