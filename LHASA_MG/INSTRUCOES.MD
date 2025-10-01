# Análise de Risco Hidrológico com Dados INMET

> EXECUCAO DENTRO DO NOTEBOOK PYTHON NO SOFTWARE ARCGIS PRO\
VIDE CREDENCIAIS DE ACESSO PARA EXECUCAO DO PROJETO

## 1. Objetivo
Este projeto utiliza dados de chuva em tempo real da API do INMET e dados geoespaciais de suscetibilidade a deslizamentos para gerar um mapa de análise de perigo (Nowcast). O processo é executado dentro de um Notebook no ambiente ArcGIS Pro.

## 2. Estrutura de Pastas Esperada
Para que o script funcione corretamente, a organização das suas pastas e arquivos deve seguir a estrutura abaixo. O script foi projetado para ser executado a partir da pasta principal do projeto, onde o arquivo .aprx está localizado.

## 2. Estrutura de Pastas Esperada

Para que o script funcione corretamente, a organização das suas pastas e arquivos deve seguir a estrutura abaixo. O script foi projetado para ser executado a partir da pasta principal do projeto.

```
📁 Meu_Projeto_Arc/
 │
 ├── 📄 Meu_Projeto_Hidrologico.aprx
 ├── 📄 Seu_Notebook.ipynb
 ├── 📄 estacoes_mg_completo.csv
 ├── 🗃️ Meu_Projeto_Hidrologico.gdb
 ├── 🗃️ Meu_Projeto_Hidrologico.tbx
 │
 ├── 📁 data/
 │   │
 │   └── 🗃️ MG-HIDRO-DATA.gdb
 │
 └── 📁 logs/
     │
     └── 📄 LHASA_MG.log (será criado na 1ª execução)
```

## 3. Pré-requisitos
Software: ArcGIS Pro instalado.

Dados de Entrada:

Um arquivo estacoes_mg_completo.csv com as colunas DC_NOME e CD_ESTACAO.

Dentro do geodatabase MG-HIDRO-DATA.gdb, você deve ter:

Uma camada de polígonos ou pontos (Camada_Estacoes_MG) representando suas estações. Esta camada precisa ter campos que correspondam à definição em LYR_PZ_FLDS (ex: Codigo, Nome_Estacao, Endereco). O nome da estação (Nome_Estacao) deve ser idêntico ao DC_NOME do CSV para o mapeamento funcionar.

Uma camada raster ou de polígonos (Camada_Suscetibilidade_MG) com um campo gridcode (ou similar) indicando os níveis de suscetibilidade.

Acesso à API: Um token de acesso válido para a API do INMET.

## 4. Configuração do Código
Antes de executar, você precisa fazer os seguintes ajustes no seu notebook:

Token da API (Bloco 2): Na variável INMET_TOKEN, substitua "SEU_TOKEN_REAL_AQUI" pelo seu token.

Caminhos das Camadas (Bloco 2): Verifique e corrija os caminhos nas variáveis LYR_IN_PZ e LYR_IN_SZ para que apontem corretamente para suas camadas de estações e suscetibilidade.

Campos da Camada de Estações (Bloco 2): Verifique se os nomes dos campos na lista LYR_PZ_FLDS correspondem exatamente aos nomes dos campos na sua camada Camada_Estacoes_MG.

## 5. Como Executar
O código no notebook está dividido em 6 blocos sequenciais. Para executar a análise completa:

Abra seu projeto .aprx no ArcGIS Pro.

Abra o notebook associado ao projeto.

Execute cada célula de código em ordem, do Bloco 1 ao Bloco 6.

## 6. Entendendo o Funcionamento do Código (Bloco a Bloco)
Bloco 1: Importações

Carrega todas as bibliotecas Python necessárias para o funcionamento do script (arcpy, pandas, logging, etc.).

Bloco 2: Configurações Globais e Constantes

Define todas as variáveis fixas: URLs da API, seu token, caminhos para as pastas e geodatabases, e nomes das camadas e campos que serão usados. É o principal local para ajustes.

Bloco 3: Leitura do CSV e Criação do Mapa de Estações

Lê o arquivo estacoes_mg_completo.csv.

Cria um dicionário em memória chamado MAP_ESTACAO_PARA_CODIGO_INMET. Este dicionário é a "ponte" entre o nome da estação na sua camada do mapa e o código oficial da estação usado pela API do INMET.

Bloco 4: Estruturas de Dados e Templates

Prepara as listas (ARR_PZ, ARR_PD) e dicionários modelo que serão usados para armazenar temporariamente os dados coletados do mapa e da API antes de serem processados.

Bloco 5: Definição das Funções

Contém a "inteligência" do script, dividida em funções:

initialize(): Prepara o ambiente do ArcPy.

loadPluviometricZones(): Lê sua camada de mapa (LYR_IN_PZ) para obter a geometria e o nome de cada estação.

loadPluviometricData(): Itera sobre as estações lidas, consulta a API do INMET para cada uma e busca os dados de chuva mais recentes.

loadNowData(): Organiza a junção dos dados geográficos com os dados de chuva.

doAnalysis(): Executa as ferramentas de geoprocessamento do ArcGIS (Intersect, Calculate Field, Dissolve) para realizar a análise de risco.

nowcast(): É a função principal que "orquestra" a chamada das outras funções na ordem correta.

Bloco 6: Execução do Processo

É o gatilho final. Chama a função initialize() e depois a nowcast() para iniciar e executar todo o fluxo de trabalho descrito acima. Inclui tratamento de erros para capturar falhas.

## 7. Saída (Output)
Ao final da execução, o script irá gerar uma nova camada de polígonos dentro do seu geodatabase (MG-HIDRO-DATA.gdb). O nome da camada conterá a data e hora da execução (ex: MG_LHASA_N_20251001_1043). Esta camada mostrará as áreas com os respectivos níveis de perigo calculados ("BAIXO", "MODERADO", "ALTO", etc.). Se a opção OUTPUT_TO_SDE estiver ativa, os dados também serão gravados no SDE configurado.