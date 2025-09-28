# -*- coding: utf-8 -*-

"""
Plugin LHASA MG para QGIS
Análise de Risco de Deslizamento para Minas Gerais
"""

def classFactory(iface):
    """Função para criar a instância do plugin"""
    try:
        from .lhasa_mg_plugin import LhasaMgPlugin
        return LhasaMgPlugin(iface)
    except ImportError as e:
        import traceback
        traceback.print_exc()
        raise ImportError(f"Erro ao importar plugin LHASA MG: {e}")
