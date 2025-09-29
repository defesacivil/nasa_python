# -*- coding: utf-8 -*-

"""
Este é um script de processamento do QGIS para adaptar a lógica do LHASA-RIO
utilizando dados das APIs do INMET.
"""

# Importações necessárias para o QGIS e para requisições web
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsField,
                       QgsFeature,
                       QgsVectorLayer,
                       QgsProject)
from qgis.utils import iface
import processing
import requests
from datetime import datetime, timedelta
import json

class AnaliseRiscoInmet(QgsProcessingAlgorithm):
    """
    Este algoritmo realiza uma análise de risco de deslizamento cruzando dados
    de suscetibilidade com dados de chuva obtidos da API do INMET.
    """
    # Constantes para as entradas e saídas
    INPUT_SUSCETIBILIDADE = 'INPUT_SUSCETIBILIDADE'
    INPUT_ESTACOES_INMET = 'INPUT_ESTACOES_INMET'
    INPUT_CAMPO_CODIGO_ESTACAO = 'INPUT_CAMPO_CODIGO_ESTACAO'
    INPUT_DATA_ANALISE = 'INPUT_DATA_ANALISE'
    OUTPUT_RISCO = 'OUTPUT_RISCO'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return AnaliseRiscoInmet()

    def name(self):
        return 'analise_risco_inmet'

    def displayName(self):
        return self.tr('Análise de Risco de Deslizamento (INMET)')

    def group(self):
        return self.tr('Análises Meteorológicas')

    def groupId(self):
        return 'analisesmeteorologicas'

    def shortHelpString(self):
        return self.tr("Este script cruza uma camada de suscetibilidade com dados de chuva do INMET para gerar um mapa de risco.")

    def initAlgorithm(self, config=None):
        # Camada de entrada com o mapa de suscetibilidade
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_SUSCETIBILIDADE,
                self.tr('Camada de Suscetibilidade'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        # Camada de PONTOS com a localização das estações do INMET
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_ESTACOES_INMET,
                self.tr('Camada de Pontos das Estações INMET'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        # Campo na camada de estações que contém o código (ex: "A521")
        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_CAMPO_CODIGO_ESTACAO,
                self.tr('Nome do Campo com o Código da Estação (ex: CD_ESTACAO)')
            )
        )
        # Data para a análise
        ontem = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_DATA_ANALISE,
                self.tr('Data da Análise (AAAA-MM-DD)'),
                defaultValue=ontem
            )
        )
        # Camada de saída
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_RISCO,
                self.tr('Camada de Saída com Análise de Risco')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Obter parâmetros da interface
        camada_suscetibilidade = self.parameterAsSource(parameters, self.INPUT_SUSCETIBILIDADE, context)
        camada_estacoes = self.parameterAsVectorLayer(parameters, self.INPUT_ESTACOES_INMET, context)
        campo_codigo = self.parameterAsString(parameters, self.INPUT_CAMPO_CODIGO_ESTACAO, context)
        data_analise = self.parameterAsString(parameters, self.INPUT_DATA_ANALISE, context)
        output_path = self.parameterAsFileOutput(parameters, self.OUTPUT_RISCO, context)

        feedback.pushInfo("--- INICIANDO ANÁLISE DE RISCO ---")
        
        # --- ETAPA 1: Obter dados de chuva da API do INMET ---
        feedback.pushInfo(f"Buscando dados de chuva para a data: {data_analise}")

        # Dicionário para armazenar a chuva por estação
        chuva_por_estacao = {}
        
        # Iterar sobre cada estação na camada de pontos
        for estacao in camada_estacoes.getFeatures():
            codigo_estacao = estacao[campo_codigo]
            url_dados = f"https://apitempo.inmet.gov.br/token/estacao/{data_analise}/{data_analise}/{codigo_estacao}/YOUR_TOKEN_HERE"
            
            try:
                response = requests.get(url_dados)
                if response.status_code == 200:
                    dados = response.json()
                    chuva_acumulada_24h = 0.0
                    for registro in dados:
                        # O campo 'CHUVA' no INMET é o acumulado na hora. Somamos para ter o total de 24h.
                        chuva_hora = registro.get('CHUVA')
                        if chuva_hora is not None:
                            try:
                                chuva_acumulada_24h += float(chuva_hora)
                            except (ValueError, TypeError):
                                continue # Ignora valores nulos ou inválidos
                    
                    chuva_por_estacao[codigo_estacao] = chuva_acumulada_24h
                    feedback.pushInfo(f"  - Estação {codigo_estacao}: {chuva_acumulada_24h:.2f} mm")
                else:
                    feedback.pushWarning(f"  - Falha ao buscar dados para a estação {codigo_estacao} (Código: {response.status_code})")
            except Exception as e:
                feedback.pushWarning(f"  - Erro de conexão para a estação {codigo_estacao}: {str(e)}")

        # --- ETAPA 2: Adicionar dados de chuva à camada de estações ---
        feedback.pushInfo("Adicionando dados de chuva à camada de estações...")
        
        # Criar uma cópia em memória da camada de estações para não alterar a original
        estacoes_com_chuva = camada_estacoes.clone()
        provider = estacoes_com_chuva.dataProvider()
        provider.addAttributes([QgsField("CHUVA_24H", QgsField.Type.Double)])
        estacoes_com_chuva.updateFields()

        # Atualizar cada feição com o valor da chuva
        with edit(estacoes_com_chuva):
            for feature in estacoes_com_chuva.getFeatures():
                codigo = feature[campo_codigo]
                chuva = chuva_por_estacao.get(codigo, 0.0) # Usa 0.0 se não encontrou dados
                feature['CHUVA_24H'] = chuva
                estacoes_com_chuva.updateFeature(feature)

        # --- ETAPA 3: Geoprocessamento (Tradução da lógica 'arcpy') ---
        feedback.pushInfo("Iniciando etapas de geoprocessamento...")

        # 3.1 - Criar uma área de influência (buffer/Voronoi) ao redor das estações para ter "zonas pluviométricas"
        # Usaremos Polígonos de Voronoi para definir a área de influência de cada estação.
        zonas_pluviometricas = processing.run("native:voronoipolygons", {
            'INPUT': estacoes_com_chuva,
            'BUFFER': 0, # Sem buffer adicional
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 3.2 - Selecionar apenas áreas de risco ALTO e MÉDIO da camada de suscetibilidade
        # No script original: "gridcode IN (2,3)". Adapte o nome do campo e os valores se necessário.
        feedback.pushInfo("Selecionando áreas de risco (suscetibilidade média e alta)...")
        areas_de_risco_selecionadas = processing.run("native:extractbyexpression", {
            'INPUT': camada_suscetibilidade,
            'EXPRESSION': '"gridcode" IN (2, 3)', # <-- ATENÇÃO: Altere "gridcode" para o nome do seu campo!
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']

        # 3.3 - Interseção entre as zonas de chuva e as áreas de risco
        feedback.pushInfo("Cruzando zonas de chuva com áreas de risco...")
        intersecao = processing.run("native:intersection", {
            'INPUT': zonas_pluviometricas,
            'OVERLAY': areas_de_risco_selecionadas,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']

        # 3.4 - Calcular o campo de PERIGO
        feedback.pushInfo("Calculando o nível de perigo...")
        
        # A lógica do script original é complexa e usa H01, H24, H96.
        # Simplificamos aqui para usar apenas a chuva de 24h, pois é o que a API do INMET fornece facilmente.
        # A lógica completa precisaria de um tratamento de dados mais avançado.
        expressao_perigo = """
        CASE
            WHEN "CHUVA_24H" >= 150 AND "gridcode" = 3 THEN 'CRÍTICO'
            WHEN "CHUVA_24H" >= 150 AND "gridcode" = 2 THEN 'MUITO ALTO'
            WHEN "CHUVA_24H" >= 70 AND "gridcode" = 3 THEN 'ALTO'
            WHEN "CHUVA_24H" >= 70 AND "gridcode" = 2 THEN 'MODERADO'
            ELSE 'BAIXO'
        END
        """
        
        camada_com_perigo = processing.run("native:fieldcalculator", {
            'INPUT': intersecao,
            'FIELD_NAME': 'PERIGO',
            'FIELD_TYPE': 0, # String
            'FIELD_LENGTH': 20,
            'FORMULA': expressao_perigo,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 3.5 - Dissolver (agregar) feições com o mesmo nível de perigo
        feedback.pushInfo("Agregando resultados...")
        processing.run("native:dissolve", {
            'INPUT': camada_com_perigo,
            'FIELD': ['PERIGO'], # Agrupar por perigo
            'OUTPUT': output_path
        }, context=context, feedback=feedback)
        
        feedback.pushInfo("--- ANÁLISE FINALIZADA COM SUCESSO ---")
        return {self.OUTPUT_RISCO: output_path}