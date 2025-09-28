# -*- coding: utf-8 -*-

"""
Versão simplificada do algoritmo LHASA MG para QGIS
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterVectorDestination,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsField,
    QgsFeature,
    QgsVectorLayer,
    edit
)
import processing

class LhasaMgAnalysis(QgsProcessingAlgorithm):
    """
    Algoritmo QGIS simplificado para análise de risco de deslizamento em Minas Gerais
    """
    
    INPUT_SUSCETIBILIDADE = 'INPUT_SUSCETIBILIDADE'
    INPUT_ZONAS_PLUVIOMETRICAS = 'INPUT_ZONAS_PLUVIOMETRICAS'
    INPUT_DATA_ANALISE = 'INPUT_DATA_ANALISE'
    OUTPUT_RESULTADO = 'OUTPUT_RESULTADO'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LhasaMgAnalysis()

    def name(self):
        return 'lhasa_mg_analysis'

    def displayName(self):
        return self.tr('LHASA MG - Análise de Risco de Deslizamento')

    def group(self):
        return self.tr('Análises de Risco')

    def groupId(self):
        return 'analises_risco'

    def shortHelpString(self):
        return self.tr("""
        Análise de risco de deslizamento para Minas Gerais usando dados do INMET.
        
        Parâmetros:
        - Camada de Suscetibilidade: Polígonos com campo 'gridcode' (1=baixa, 2=média, 3=alta)
        - Zonas Pluviométricas: Polígonos com campos 'Cod' e 'Est'
        - Data da Análise: Formato YYYY-MM-DD
        """)

    def initAlgorithm(self, config=None):
        # --- Parâmetros de Entrada ---
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT_SUSCETIBILIDADE',
                self.tr('Camada de Suscetibilidade'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT_ESTACOES_INMET',
                self.tr('Camada de Pontos das Estações INMET'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                'INPUT_CAMPO_CODIGO_ESTACAO',
                self.tr('Nome do Campo com o Código da Estação'),
                defaultValue='CD_ESTACAO'
            )
        )
        
        # Data padrão D-2 para maior chance de dados disponíveis
        data_padrao = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        self.addParameter(
            QgsProcessingParameterString(
                'INPUT_DATA_ANALISE',
                self.tr('Data da Análise (AAAA-MM-DD)'),
                defaultValue=data_padrao
            )
        )
        
        # --- NOVOS PARÂMETROS DE LIMIAR DE CHUVA (mm) ---
        self.addParameter(
            QgsProcessingParameterNumber(
                'LIMIAR_MODERADO',
                self.tr('Limiar de Chuva para Risco MODERADO (mm)'),
                QgsProcessingParameterNumber.Double,
                defaultValue=50.0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'LIMIAR_ALTO',
                self.tr('Limiar de Chuva para Risco ALTO (mm)'),
                QgsProcessingParameterNumber.Double,
                defaultValue=100.0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                'LIMIAR_CRITICO',
                self.tr('Limiar de Chuva para Risco CRÍTICO (mm)'),
                QgsProcessingParameterNumber.Double,
                defaultValue=150.0
            )
        )
        
        # --- Parâmetro de Saída ---
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                'OUTPUT_RESULTADO',
                self.tr('Camada de Saída com Análise de Risco')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Obter parâmetros
        camada_suscetibilidade = self.parameterAsSource(parameters, 'INPUT_SUSCETIBILIDADE', context)
        camada_estacoes = self.parameterAsVectorLayer(parameters, 'INPUT_ESTACOES_INMET', context)
        campo_codigo = self.parameterAsString(parameters, 'INPUT_CAMPO_CODIGO_ESTACAO', context)
        data_analise = self.parameterAsString(parameters, 'INPUT_DATA_ANALISE', context)
        output_path = self.parameterAsFileOutput(parameters, 'OUTPUT_RESULTADO', context)

        feedback.pushInfo("=== INICIANDO ANÁLISE LHASA MG ===")
        feedback.pushInfo(f"Data da análise: {data_analise}")

        # ETAPA 1: Buscar dados de chuva
        feedback.pushInfo("Buscando dados do INMET...")
        chuva_por_estacao = self.buscarDadosInmet(camada_estacoes, campo_codigo, data_analise, feedback)
        feedback.pushInfo(f"Dados encontrados para {len(chuva_por_estacao)} estações.")

        # Verificação CRÍTICA: Se não encontrou dados, para o algoritmo
        if not chuva_por_estacao:
            feedback.pushInfo("AVISO: Nenhum dado de chuva foi encontrado para a data selecionada. O algoritmo será interrompido.")
            return {}  # Retorna dicionário vazio para parar a execução

        # ETAPA 2: Adicionar dados de chuva à camada de pontos
        feedback.pushInfo("Adicionando dados de chuva à camada de pontos...")
        estacoes_com_chuva = self.adicionarDadosChuva(camada_estacoes, chuva_por_estacao, campo_codigo, feedback)

        # ETAPA 3: Criar Zonas Pluviométricas
        feedback.pushInfo("Criando Zonas Pluviométricas (áreas de influência)...")
        zonas_pluviometricas = processing.run("native:voronoipolygons", {
            'INPUT': estacoes_com_chuva,
            'BUFFER': 0,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']

        # ETAPA 4: Geoprocessamento da Análise de Risco
        feedback.pushInfo("Iniciando geoprocessamento da análise de risco...")
        resultado_final = self.executarAnaliseRisco(zonas_pluviometricas, camada_suscetibilidade, parameters, output_path, context, feedback)

        feedback.pushInfo("--- ANÁLISE FINALIZADA COM SUCESSO ---")
        return { 'OUTPUT_RESULTADO': resultado_final }
    
    def buscarDadosInmet(self, camada_estacoes, campo_codigo, data_analise, feedback):
        chuva_por_estacao = {}
        total_estacoes = camada_estacoes.featureCount()
        estacoes_processadas = 0

        if total_estacoes == 0:
            feedback.pushWarning("A camada de estações de entrada está vazia.")
            return chuva_por_estacao

        for estacao in camada_estacoes.getFeatures():
            if feedback.isCanceled():
                break

            try:
                codigo_estacao = str(estacao[campo_codigo]).upper().strip()
                if not codigo_estacao:
                    continue

                url_dados = f"https://apitempo.inmet.gov.br/estacao/{data_analise}/{data_analise}/{codigo_estacao}"
                feedback.pushInfo(f"--- Tentando URL: {url_dados}")
                response = requests.get(url_dados, timeout=20)
                feedback.pushInfo(f"  - Resposta para {codigo_estacao}: Código {response.status_code}")

                if response.status_code == 200:
                    dados = response.json()
                    if dados:
                        chuva_acumulada_24h = 0.0
                        for registro in dados:
                            chuva_hora = registro.get('CHUVA')
                            if chuva_hora is not None:
                                try:
                                    chuva_acumulada_24h += float(chuva_hora)
                                except (ValueError, TypeError):
                                    continue
                        chuva_por_estacao[codigo_estacao] = chuva_acumulada_24h
            except Exception as e:
                # CORREÇÃO DO BUG: Usando pushWarning que é um método válido
                feedback.pushWarning(f"  - Ocorreu um erro ao processar a estação {codigo_estacao}: {str(e)}")

            estacoes_processadas += 1
            feedback.setProgress(int((estacoes_processadas / total_estacoes) * 100))

        return chuva_por_estacao

    def adicionarDadosChuva(self, camada_estacoes, chuva_por_estacao, campo_codigo, feedback):
        """
        Adiciona dados de chuva à camada de pontos das estações.
        Retorna uma nova camada com os dados de chuva incorporados.
        """
        # Criar uma cópia em memória da camada de estações
        estacoes_com_chuva = camada_estacoes.clone()
        provider = estacoes_com_chuva.dataProvider()
        
        # Adicionar novos campos para os dados de chuva
        provider.addAttributes([
            QgsField("CHUVA_24H", QVariant.Double)
        ])
        estacoes_com_chuva.updateFields()
        
        # Atualizar cada feição com o valor da chuva
        with edit(estacoes_com_chuva):
            for feature in estacoes_com_chuva.getFeatures():
                codigo = feature[campo_codigo]
                chuva = chuva_por_estacao.get(codigo, 0.0)  # Usa 0.0 se não encontrou dados
                feature['CHUVA_24H'] = chuva
                estacoes_com_chuva.updateFeature(feature)
        
        feedback.pushInfo(f"Adicionados dados de chuva para {len(chuva_por_estacao)} estações")
        return estacoes_com_chuva

    def executarAnaliseRisco(self, zonas_pluviometricas, camada_suscetibilidade, parameters, output_path, context, feedback):
        """Calcula o risco de deslizamento usando limiares ajustáveis"""
        
        # Obter os valores dos limiares da interface do usuário
        limiar_moderado = self.parameterAsDouble(parameters, 'LIMIAR_MODERADO', context)
        limiar_alto = self.parameterAsDouble(parameters, 'LIMIAR_ALTO', context)
        limiar_critico = self.parameterAsDouble(parameters, 'LIMIAR_CRITICO', context)
        
        feedback.pushInfo(f"Limiares configurados: Moderado={limiar_moderado}mm, Alto={limiar_alto}mm, Crítico={limiar_critico}mm")
        
        # 1. Selecionar áreas de suscetibilidade média e alta
        feedback.pushInfo("Selecionando áreas de suscetibilidade média e alta...")
        areas_risco = processing.run("native:extractbyexpression", {
            'INPUT': camada_suscetibilidade,
            'EXPRESSION': '"gridcode" IN (2, 3)',
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 2. Cruzar zonas de chuva com áreas de risco
        feedback.pushInfo("Cruzando zonas de chuva com áreas de risco...")
        intersecao = processing.run("native:intersection", {
            'INPUT': zonas_pluviometricas,
            'OVERLAY': areas_risco,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 3. Calcular perigo com limiares dinâmicos
        feedback.pushInfo("Calculando o nível de perigo com base nos limiares definidos...")
        expressao_perigo = f'''
        CASE
            WHEN "CHUVA_24H" >= {limiar_critico} AND "gridcode" = 3 THEN 'CRITICO'
            WHEN "CHUVA_24H" >= {limiar_critico} AND "gridcode" = 2 THEN 'MUITO_ALTO'
            WHEN "CHUVA_24H" >= {limiar_alto} AND "gridcode" = 3 THEN 'ALTO'
            WHEN "CHUVA_24H" >= {limiar_alto} AND "gridcode" = 2 THEN 'MODERADO'
            WHEN "CHUVA_24H" >= {limiar_moderado} AND "gridcode" = 3 THEN 'MODERADO'
            ELSE 'BAIXO'
        END
        '''
        
        camada_com_perigo = processing.run("native:fieldcalculator", {
            'INPUT': intersecao,
            'FIELD_NAME': 'PERIGO',
            'FIELD_TYPE': 2,  # String
            'FIELD_LENGTH': 20,
            'FORMULA': expressao_perigo,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 4. Agregar resultados por nível de perigo
        feedback.pushInfo("Agregando resultados...")
        resultado = processing.run("native:dissolve", {
            'INPUT': camada_com_perigo,
            'FIELD': ['PERIGO'],
            'OUTPUT': output_path
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 5. Gerar relatório de áreas
        self.gerarRelatorioAreas(output_path, feedback)
        
        return resultado
    
    def gerarRelatorioAreas(self, output_path, feedback):
        """Gera relatório de áreas por nível de risco"""
        
        feedback.pushInfo("\n--- RELATÓRIO DE ÁREAS POR NÍVEL DE RISCO ---")
        
        # Carregar a camada de resultado
        camada_resultado = QgsVectorLayer(output_path, 'Resultado Final', 'ogr')
        
        if not camada_resultado.isValid():
            feedback.pushWarning("Não foi possível carregar a camada de resultado para o relatório")
            return
        
        # Adicionar campo de área em km²
        provider = camada_resultado.dataProvider()
        provider.addAttributes([QgsField("AREA_KM2", QVariant.Double, len=10, prec=4)])
        camada_resultado.updateFields()
        
        # Calcular área para cada feição
        with edit(camada_resultado):
            for feature in camada_resultado.getFeatures():
                geom = feature.geometry()
                area_km2 = geom.area() / 1000000  # Converter m² para km²
                feature['AREA_KM2'] = area_km2
                camada_resultado.updateFeature(feature)
        
        # Gerar relatório
        total_area = 0
        for feature in camada_resultado.getFeatures():
            nivel_perigo = feature['PERIGO']
            area_km2 = feature['AREA_KM2']
            if nivel_perigo and area_km2:
                feedback.pushInfo(f"Nível: {nivel_perigo:<12} | Área: {area_km2:.4f} km²")
                total_area += area_km2
        
        feedback.pushInfo("-" * 50)
        feedback.pushInfo(f"Área Total de Risco Mapeada: {total_area:.4f} km²")
        feedback.pushInfo("--- FIM DO RELATÓRIO ---\n")
