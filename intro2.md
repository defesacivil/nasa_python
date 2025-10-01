## 1 Integracao com o Mapa do Qgis

O objetivo e trabalhar as informacoes que eu ja disponho da api INMET passar para o mapa, com os niveis 
DV 1 - Verde: #8ddd55
DV 2 - Amarelo: #fff897
DV 3 - Vermelho: #f9494a
uso das informações que a própria API do INMET já oferece, para depois passar isso para o seu mapa de forma mais inteligente.
O processo envolve a interpolação dos valores de chuva acumulada, a reclassificação do resultado em 3 níveis de perigo (DV1, DV2, DV3) e a aplicação de uma estilização de cores pré-definida.

## 2 Fluxo

Entrada de Parâmetros: O usuário define a data final, o número de dias para acúmulo e os limiares de chuva para os níveis de perigo.

Coleta de Dados (API): A função buscarDadosInmet permanece, coletando a chuva acumulada para cada estação.

Criação da Camada de Pontos: A função adicionarDadosChuva cria a camada vetorial em memória com os pontos das estações e o atributo CHUVA_ACUMULADA.

Interpolação Espacial (IDW): Os valores da camada de pontos são interpolados para gerar um raster contínuo de precipitação. Esta etapa substitui a criação dos Polígonos de Voronoi.

Reclassificação do Perigo: O raster contínuo é reclassificado em 3 valores inteiros (1, 2, 3) que correspondem aos níveis de perigo DV1, DV2 e DV3.

Estilização e Saída: O raster reclassificado é estilizado com as cores especificadas e retornado como a camada de saída do algoritmo.



## 3 a execucao do Algoritmo

Ao finalizar a execucao do algoritmo , deve me retonar um mapa com os principais pontos de precipirtacao de chuva, DE ACORDO COM OS DADOS DA API    , usando como referencia para o mapa aplicado