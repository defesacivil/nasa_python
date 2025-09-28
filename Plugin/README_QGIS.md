# LHASA MG - Plugin QGIS

## Descrição

Este plugin implementa a análise de risco de deslizamento LHASA para Minas Gerais no ambiente QGIS, utilizando dados meteorológicos da API do INMET.

## Instalação

### Opção 1: Instalação Manual

1. Copie todos os arquivos para a pasta de plugins do QGIS:

   - Windows: `C:\Users\[usuario]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\lhasa_mg\`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/lhasa_mg/`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/lhasa_mg/`

2. Reinicie o QGIS

3. Ative o plugin em: **Plugins → Gerenciar e Instalar Plugins → Instalados**

### Opção 2: Execução Direta

Você também pode executar o script diretamente no Console Python do QGIS:

```python
exec(open('caminho/para/LHASA_Mg.py').read())
```

## Como Usar

### 1. Preparar os Dados

Você precisará de duas camadas vetoriais:

- **Camada de Suscetibilidade**: Polígonos com campo `gridcode` contendo valores:

  - 1 = Baixa suscetibilidade
  - 2 = Média suscetibilidade
  - 3 = Alta suscetibilidade

- **Zonas Pluviométricas**: Polígonos representando áreas de influência das estações meteorológicas com campos:
  - `Cod`: Código da estação
  - `Est`: Nome da estação

### 2. Executar a Análise

1. Abra a **Caixa de Ferramentas de Processamento** (Ctrl+Alt+T)

2. Navegue até: **Análises de Risco → LHASA MG - Análise de Risco de Deslizamento**

3. Configure os parâmetros:

   - **Camada de Suscetibilidade**: Selecione sua camada de suscetibilidade
   - **Zonas Pluviométricas**: Selecione sua camada de zonas pluviométricas
   - **Data da Análise**: Data no formato YYYY-MM-DD (padrão: hoje)
   - **Tipo de Análise**: 'atual' ou 'historico'
   - **Resultado**: Caminho para salvar o resultado

4. Clique em **Executar**

### 3. Interpretar os Resultados

A camada de saída conterá polígonos classificados por nível de perigo:

- **BAIXO**: Risco mínimo
- **MODERADO**: Risco moderado (suscetibilidade média + chuva moderada)
- **ALTO**: Risco alto (suscetibilidade alta + chuva moderada)
- **MUITO ALTO**: Risco muito alto (suscetibilidade média + chuva intensa)
- **CRÍTICO**: Risco crítico (suscetibilidade alta + chuva intensa)

## Configuração da API INMET

O plugin utiliza automaticamente a API pública do INMET:

- **Estações**: `https://apitempo.inmet.gov.br/estacoes/T`
- **Dados**: `https://apitempo.inmet.gov.br/estacao/{data_inicio}/{data_fim}/{codigo_estacao}`

### Limitações da API

- Dados recentes podem não estar disponíveis (HTTP 204)
- Rate limiting: máximo de requisições por minuto
- Dados horários apenas (não há dados de 15 minutos)

## Principais Diferenças do ArcGIS

| Aspecto              | ArcGIS (Original)                   | QGIS (Adaptado)                                |
| -------------------- | ----------------------------------- | ---------------------------------------------- |
| **Ambiente**         | Script de linha de comando          | Algoritmo com interface gráfica                |
| **Cursores**         | `arcpy.da.SearchCursor`             | `layer.getFeatures()`                          |
| **Geoprocessamento** | `arcpy.Select_analysis()`           | `processing.run("native:extractbyexpression")` |
| **Cálculo de Campo** | `arcpy.CalculateField_management()` | `processing.run("native:fieldcalculator")`     |
| **Workspace**        | `arcpy.env.workspace`               | Parâmetros de entrada/saída                    |
| **Memória**          | `in_memory`                         | `'memory:'`                                    |

## Dependências

- QGIS 3.16+
- Python 3.6+
- Bibliotecas: `requests`, `unidecode`

## Solução de Problemas

### Erro: "Nenhuma estação INMET disponível"

- Verifique sua conexão com a internet
- A API do INMET pode estar temporariamente indisponível

### Erro: "Sem dados disponíveis para estação X"

- Dados muito recentes podem não estar processados
- Tente uma data anterior (2-3 dias atrás)

### Performance lenta

- O plugin limita automaticamente a 20 estações de MG
- Para análises completas, ajuste o limite no código

## Logs

Os logs são salvos em: `logs/LHASA_MG.log` na pasta do plugin.

## Suporte

Para suporte técnico ou relatório de bugs, consulte a documentação do projeto ou entre em contato com a equipe de desenvolvimento.

==================================================================================================================

# Relatório Técnico: Algoritmo de Análise de Risco de Deslizamento para QGIS

## 1. Objetivo

Este documento descreve o funcionamento do algoritmo "LHASA MG - Análise de Risco de Deslizamento", uma ferramenta de geoprocessamento para o QGIS. O objetivo da ferramenta é automatizar a criação de um mapa de risco de deslizamento para uma área de estudo, utilizando dados de suscetibilidade do terreno e dados de precipitação obtidos em tempo real da API do Instituto Nacional de Meteorologia (INMET).

---

## 2. Lógica do Algoritmo

O processo é executado em uma sequência de quatro fases principais, orquestradas por um script Python (`PyQGIS`).

### Fase 1: Coleta de Dados de Chuva (API INMET)

1.  **Leitura dos Parâmetros:** O algoritmo recebe as camadas de entrada e a data da análise definidas pelo usuário.
2.  **Busca de Dados:** O script itera sobre cada feição (ponto) da **Camada de Estações INMET**.
3.  **Requisição à API:** Para cada estação, o script utiliza seu código (ex: `A521`) para montar uma URL e fazer uma requisição HTTP à API do INMET, solicitando todos os dados horários de chuva para a data especificada.
4.  **Processamento dos Dados:** A resposta da API (em formato JSON) é processada. O script soma os valores do campo `CHUVA` de cada hora para calcular a precipitação total acumulada em 24 horas para aquela estação.
5.  **Armazenamento em Memória:** Os totais de chuva de cada estação são armazenados em um dicionário Python (ex: `{'A521': 55.2, 'A522': 43.8, ...}`).

### Fase 2: Preparação dos Dados Espaciais

1.  **Adição dos Dados de Chuva:** O script cria uma cópia em memória da **Camada de Estações INMET** e adiciona uma nova coluna (ex: `CHUVA_24H`). Ele então preenche essa coluna com os valores de chuva correspondentes a cada estação, que foram armazenados no dicionário.
2.  **Criação das Zonas Pluviométricas:** Para transformar os dados de pontos de chuva em áreas, o algoritmo utiliza a ferramenta **Polígonos de Voronoi**. Isso cria um polígono de influência ao redor de cada estação, resultando em uma camada de "Zonas Pluviométricas", onde cada polígono herda o valor de chuva da sua estação correspondente.

### Fase 3: Análise de Risco (Geoprocessamento)

1.  **Seleção de Áreas de Risco:** O algoritmo primeiro filtra a **Camada de Suscetibilidade**, selecionando apenas os polígonos que representam risco médio e alto (geralmente `gridcode = 2` e `gridcode = 3`).
2.  **Interseção:** A ferramenta realiza uma **Interseção** espacial entre a camada de Zonas Pluviométricas (criada na Fase 2) e a camada de áreas de risco (filtrada no passo anterior). O resultado é uma nova camada onde cada polígono possui tanto a informação de chuva (`CHUVA_24H`) quanto a informação de suscetibilidade (`gridcode`).

### Fase 4: Classificação e Agregação

1.  **Cálculo do Nível de Perigo:** Usando a **Calculadora de Campo**, o script aplica um conjunto de regras (lógica `CASE WHEN ... END`) na camada resultante da interseção. Ele cria um novo campo de texto chamado `PERIGO` e o preenche com classificações como 'BAIXO', 'MODERADO', 'ALTO' ou 'CRÍTICO', com base nos limiares de chuva e nos níveis de suscetibilidade.
2.  **Agregação do Resultado:** Como etapa final, a ferramenta utiliza a função **Dissolver (Dissolve)** para unir todos os polígonos adjacentes que possuem a mesma classificação de `PERIGO`. Isso simplifica o mapa final, criando áreas de risco coesas e fáceis de interpretar.

---

## 3. Parâmetros de Entrada (Inputs)

A ferramenta requer que o usuário forneça os seguintes dados de entrada através da sua interface gráfica:

- **`Camada de Suscetibilidade`**

  - **Tipo:** Camada Vetorial de Polígonos.
  - **Descrição:** Mapa da área de estudo dividido em polígonos, onde cada um representa um nível de suscetibilidade a deslizamentos.
  - **Requisito Técnico:** Deve conter um campo numérico (ex: `gridcode`) que classifica o risco (ex: 1 para Baixo, 2 para Médio, 3 para Alto).

- **`Camada de Pontos das Estações INMET`**

  - **Tipo:** Camada Vetorial de Pontos.
  - **Descrição:** Localização geográfica de cada estação meteorológica do INMET.
  - **Requisito Técnico:** Deve conter um campo de texto com o código oficial da estação (ex: `CD_ESTACAO`).

- **`Nome do Campo com o Código da Estação`**

  - **Tipo:** Texto (String).
  - **Descrição:** O nome exato da coluna na camada de pontos que contém o código da estação.
  - **Exemplo:** `CD_ESTACAO`.

- **`Data da Análise`**
  - **Tipo:** Texto (String).
  - **Descrição:** A data para a qual os dados de chuva devem ser baixados.
  - **Formato:** `AAAA-MM-DD` (ex: `2025-09-26`).

---

## 4. Resultado Esperado (Output)

O resultado final do algoritmo é uma única camada vetorial de polígonos, que pode ser salva como um arquivo temporário ou permanente.

- **Descrição:** A camada representa as áreas de risco consolidadas para a data analisada. Cada polígono na camada terá um atributo principal, `PERIGO`, contendo sua classificação de risco.

- **Visualização no Mapa:** O resultado esperado é um mapa temático simplificado que destaca as áreas de preocupação. Para uma visualização eficaz, o usuário deve estilizar a camada de saída da seguinte forma:
  1.  Abra as **Propriedades da Camada > Simbologia**.
  2.  Escolha o renderizador **"Categorizado"**.
  3.  Selecione a coluna **`PERIGO`** como o "Valor".
  4.  Clique em **"Classificar"**.
  5.  Associe cores e legendas intuitivas a cada categoria de risco:
      - **`BAIXO`**: Cor Verde Claro
      - **`MODERADO`**: Cor Amarela
      - **`ALTO`**: Cor Laranja
      - **`MUITO ALTO`**: Cor Vermelha
      - **`CRÍTICO`**: Cor Vinho ou Roxo

O mapa final exibirá de forma clara e objetiva as zonas que requerem maior atenção com base na combinação da chuva ocorrida e da vulnerabilidade do terreno.
