# Detalhes Técnicos: Integração da API INMET com o QGIS

Este documento descreve os componentes e o fluxo de trabalho técnico necessários para integrar dados da API do INMET em análises de geoprocessamento dentro do QGIS, utilizando um script Python (PyQGIS).

---

## 1. A API do INMET

A API (Interface de Programação de Aplicações) do INMET é um serviço web que fornece dados meteorológicos via requisições HTTP.

### Endpoints Utilizados

Um "endpoint" é uma URL específica que fornece um tipo de dado. Nós usamos duas:

- **Listagem de Estações:** `https://apitempo.inmet.gov.br/estacoes/T`
  - **Função:** Retorna uma lista de **todas as estações automáticas** do Brasil com seus metadados (código, nome, latitude, longitude).
- **Dados Horários por Estação:** `https://apitempo.inmet.gov.br/token/estacao/{data_inicio}/{data_fim}/{codigo_estacao}/{token}`
  - **Função:** Retorna os **dados meteorológicos horários** para uma única estação dentro de um intervalo de datas.

### Formato dos Dados

- A API retorna os dados no formato **`JSON` (JavaScript Object Notation)**. É um formato de texto leve, estruturado e padronizado, ideal para ser processado por linguagens de programação.

### Estrutura dos Dados Relevantes

- **Endpoint de Estações:** Campos-chave são `CD_ESTACAO`, `VL_LATITUDE`, `VL_LONGITUDE`.
- **Endpoint de Dados:** O campo-chave para nossa análise é `CHUVA`, que representa o volume de chuva acumulado naquela hora específica.

### Considerações Técnicas

- **Latência de Dados:** Existe um atraso na consolidação dos dados. Requisições para datas muito recentes (ex: ontem) podem retornar um `Código HTTP 204 (No Content)`, indicando ausência de dados. O script deve ser robusto a essa condição.
- **Rate Limiting (Limite de Requisições):** Fazer um número excessivo de requisições em um curto período pode levar a um bloqueio temporário do acesso. Para scripts que iteram sobre muitas estações, é prudente incluir um pequeno intervalo entre as chamadas (ex: `time.sleep(0.1)`).
- **Tratamento de Erros:** A conexão pode falhar ou estações podem estar offline. O uso de blocos `try...except` é fundamental para capturar exceções de rede ou dados faltantes, permitindo que o script continue sua execução sem travar.

---

## 2. O Ambiente QGIS e PyQGIS

O QGIS oferece um ecossistema completo para automação via Python, conhecido como PyQGIS.

### Estrutura de Script (`QgsProcessingAlgorithm`)

- A abordagem moderna e recomendada para criar ferramentas no QGIS é criar uma classe que herda de `QgsProcessingAlgorithm`.
- **Vantagens Técnicas:**
  - Integração nativa com a **Caixa de Ferramentas de Processamento**.
  - Geração automática de uma **interface gráfica (GUI)** para os parâmetros de entrada e saída.
  - Gerenciamento padronizado de camadas temporárias e permanentes.
  - Possibilidade de encadear a ferramenta em modelos gráficos maiores.

### Manipulação de Camadas Vetoriais

- **Parâmetros de Entrada:** Utilizamos `self.parameterAsVectorLayer()` para obter a camada de entrada como um objeto `QgsVectorLayer`, que é a classe principal para manipular dados vetoriais no PyQGIS.
- **Modificação Segura:** O método `.clone()` é usado para criar uma cópia da camada em memória. Isso garante que a camada original do usuário não seja alterada. As edições são encapsuladas de forma segura e eficiente usando o gerenciador de contexto `with edit(layer):`.
- **Criação de Campos:** Novos campos são adicionados à tabela de atributos programaticamente com `provider.addAttributes([QgsField(...)])` e `layer.updateFields()`.

### Geoprocessamento via `processing` Framework

- Em vez de reinventar algoritmos, a prática recomendada é chamar as ferramentas nativas do QGIS, que são altamente otimizadas, através do `processing.run()`.
- Cada ferramenta é chamada pelo seu identificador único (ex: `native:voronoipolygons`, `native:intersection`) e recebe um dicionário Python com seus parâmetros.

### Gerenciamento de SRC (Sistema de Referência de Coordenadas)

- **Geográfico vs. Projetado:** Este é um conceito técnico crucial. A API do INMET fornece coordenadas **geográficas** (em graus), cujo SRC padrão no Brasil é o **SIRGAS 2000 (`EPSG:4674`)**.
- **Precisão de Análise:** Cálculos geométricos (área, distância, intersecção) são imprecisos quando feitos em graus. Por isso, o **SRC do Projeto QGIS** deve ser configurado para um sistema **projetado** (em metros), como o **SIRGAS 2000 / UTM (`EPSG:31983` para a Zona 23S)**.
- **Reprojeção "On-the-fly":** O QGIS gerencia a conversão entre os SRCs das camadas e do projeto em tempo real, garantindo o alinhamento visual e a precisão dos cálculos do `processing` framework.

---

## 3. O Script Python (A Ponte de Conexão)

O script Python orquestra todo o fluxo de trabalho, conectando a API ao ambiente QGIS.

### Fluxo Lógico dos Dados

[API INMET] -> (1. Requisição HTTP) -> [Dados JSON] -> (2. Parsing em Python) -> [Dicionário de Chuva]
|
V
[Camada de Estações QGIS] -> (3. Leitura com PyQGIS) -> [Loop] -> (4. Join com Dicionário) -> [Camada em Memória com Chuva]
|
V
[Camada c/ Chuva] + [Camada Suscetibilidade] -> (5. Geoprocessamento em Cadeia) -> [Resultado Final]

### Bibliotecas Essenciais

- **`requests`**: Biblioteca padrão de mercado para fazer requisições HTTP em Python de forma simples e robusta. Responsável pelo passo 1.
- **`qgis.core` e `qgis.processing`**: O núcleo da API do QGIS. Permitem a manipulação de camadas, feições e a execução de algoritmos de geoprocessamento. Responsáveis pelos passos 3, 4 e 5.
- **`datetime`**: Biblioteca nativa do Python para manipular datas e horas, essencial para formatar as datas corretamente para a API do INMET.
