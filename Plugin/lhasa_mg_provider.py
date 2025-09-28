# -*- coding: utf-8 -*-

"""
Provider para registrar o algoritmo LHASA MG no QGIS
"""

from qgis.core import QgsProcessingProvider

class LhasaMgProvider(QgsProcessingProvider):
    """
    Provider para algoritmos LHASA MG
    """

    def loadAlgorithms(self, *args, **kwargs):
        """Carregar algoritmos disponíveis"""
        try:
            from .lhasa_mg_simple import LhasaMgAnalysis
            self.addAlgorithm(LhasaMgAnalysis())
        except ImportError as e:
            # Log do erro mas não falha o carregamento do provider
            import logging
            logging.error(f"Erro ao carregar algoritmo LHASA MG: {e}")
        except Exception as e:
            import logging
            logging.error(f"Erro inesperado ao carregar LHASA MG: {e}")

    def id(self, *args, **kwargs):
        """ID único do provider"""
        return 'lhasa_mg'

    def name(self, *args, **kwargs):
        """Nome do provider"""
        return 'LHASA MG'

    def icon(self):
        """Ícone do provider (opcional)"""
        return QgsProcessingProvider.icon(self)

    def longName(self):
        """Nome longo do provider"""
        return 'Análises de Risco de Deslizamento - Minas Gerais'
