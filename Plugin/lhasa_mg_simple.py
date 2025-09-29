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
    QgsFields,
    QgsFeature,
    QgsVectorLayer,
    QgsFeatureSink,
    QgsProcessingUtils,
    QgsWkbTypes,
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

        # Verificação: Se não conseguiu processar nenhuma estação, para o algoritmo
        if not chuva_por_estacao:
            feedback.pushInfo("AVISO: Não foi possível processar nenhuma estação. Verifique se há estações na camada de entrada.")
            return {}  # Retorna dicionário vazio para parar a execução
        
        # Contar estações com dados válidos (mesmo que 0.0)
        total_chuva = sum(chuva_por_estacao.values())
        estacoes_com_chuva = sum(1 for v in chuva_por_estacao.values() if v > 0.0)
        feedback.pushInfo(f"Processadas {len(chuva_por_estacao)} estações. {estacoes_com_chuva} com chuva > 0. Total acumulado: {total_chuva:.2f} mm")

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

                url_dados = f"https://apitempo.inmet.gov.br/token/estacao/{data_analise}/{data_analise}/{codigo_estacao}/Q2MyWEhWUmxwalRSN0Z6ZXVOdmhBTTZYZHo3MEhlMTA=Cc2XHVRlpjTR7FzeuNvhAM6Xdz70He10"
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
                        feedback.pushInfo(f"  - Estação {codigo_estacao}: {chuva_acumulada_24h:.2f} mm")
                    else:
                        feedback.pushInfo(f"  - Estação {codigo_estacao}: Resposta vazia (0.0 mm)")
                        chuva_por_estacao[codigo_estacao] = 0.0
                elif response.status_code == 204:
                    # Código 204: No Content - dados válidos mas sem conteúdo (chuva = 0)
                    feedback.pushInfo(f"  - Estação {codigo_estacao}: Sem dados disponíveis (0.0 mm)")
                    chuva_por_estacao[codigo_estacao] = 0.0
                elif response.status_code == 404:
                    # Código 404: Estação não encontrada
                    feedback.pushWarning(f"  - Estação {codigo_estacao}: Estação não encontrada na API")
                elif response.status_code == 401:
                    # Código 401: Token inválido
                    feedback.pushWarning(f"  - Estação {codigo_estacao}: Token de API inválido")
                else:
                    # Outros códigos de erro
                    feedback.pushWarning(f"  - Estação {codigo_estacao}: Erro HTTP {response.status_code}")
            except Exception as e:
                # CORREÇÃO DO BUG: Usando pushWarning que é um método válido
                feedback.pushWarning(f"  - Ocorreu um erro ao processar a estação {codigo_estacao}: {str(e)}")

            estacoes_processadas += 1
            feedback.setProgress(int((estacoes_processadas / total_estacoes) * 100))

        return chuva_por_estacao

    def adicionarDadosChuva(self, camada_estacoes, chuva_dados, campo_codigo, feedback):
        """
        Cria uma nova camada em memória com os dados de chuva adicionados.
        Esta abordagem é mais estável do que clonar e editar uma camada baseada em CSV.
        """
        # Pega os campos (colunas) da camada de entrada original
        campos_originais = camada_estacoes.fields()
        
        # Cria uma nova lista de campos, adicionando o nosso novo campo de chuva
        novos_campos = QgsFields()
        for campo in campos_originais:
            novos_campos.append(campo)
        novos_campos.append(QgsField("CHUVA_24H", QVariant.Double))

        # Cria uma nova camada em memória
        camada_memoria = QgsVectorLayer(
            f"{QgsWkbTypes.displayString(camada_estacoes.wkbType())}?crs={camada_estacoes.crs().authid()}",
            "estacoes_com_chuva",
            "memory"
        )
        provider = camada_memoria.dataProvider()
        provider.addAttributes(novos_campos.toList())
        camada_memoria.updateFields()

        # Itera sobre a camada original para criar as novas feições
        novas_features = []
        for feature_original in camada_estacoes.getFeatures():
            if feedback.isCanceled():
                break
            
            # Cria uma nova feição
            nova_feature = QgsFeature()
            nova_feature.setGeometry(feature_original.geometry())
            nova_feature.setFields(novos_campos)
            
            # Copia os atributos da feição original para a nova
            for i in range(len(campos_originais)):
                nova_feature.setAttribute(i, feature_original.attribute(i))
            
            # Obtém e adiciona o dado de chuva
            codigo = str(feature_original[campo_codigo]).upper().strip()
            chuva = chuva_dados.get(codigo, 0.0)
            nova_feature.setAttribute("CHUVA_24H", chuva)
            
            # Adiciona a nova feição à lista
            novas_features.append(nova_feature)

        # Adiciona todas as feições de uma vez à camada
        provider.addFeatures(novas_features)
        camada_memoria.updateExtents()
        
        feedback.pushInfo(f"Criada nova camada em memória com dados de chuva para {len(chuva_dados)} estações")
        return camada_memoria

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
