# -*- coding: utf-8 -*-

"""
Plugin principal LHASA MG para QGIS
"""

from qgis.core import QgsApplication
from .lhasa_mg_provider import LhasaMgProvider

class LhasaMgPlugin:
    """Plugin principal para LHASA MG"""

    def __init__(self, iface):
        self.iface = iface
        self.provider = None

    def initProcessing(self):
        """Inicializar o provider de processamento"""
        self.provider = LhasaMgProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """Inicializar a interface gráfica"""
        self.initProcessing()

    def unload(self):
        """Descarregar o plugin"""
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
