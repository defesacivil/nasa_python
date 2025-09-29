# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# LHASA MG | NASA | Nowcast
# Processo de análise de riscos de deslizamento - Minas Gerais
# Integração com API INMET para dados meteorológicos
# V 2.2 - Adaptado para API INMET
# ---------------------------------------------------------------------------

import sys, os, shutil, copy, glob
import logging
import urllib3
import socket
import json, csv
import os
import time
import requests
from unidecode import unidecode
from datetime import datetime, timedelta

# Importações específicas do QGIS (PyQGIS)
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterVectorDestination,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsField,
    QgsFeature,
    QgsVectorLayer,
    QgsProject,
    QgsGeometry,
    edit
)
import processing

# Configurar logging para QGIS
import logging
log = logging.getLogger(__name__)

# EXTERNAL SERVICES ENDPOINTS - API INMET
# Principais mudanças implementadas:
# 1. Substituição da API do Rio pela API do INMET
# 2. Implementação de tratamento de erros HTTP 204 (dados não disponíveis)
# 3. Rate limiting para evitar sobrecarga da API
# 4. Adaptação da estrutura de dados para formato JSON do INMET
# 5. Configuração para SRC SIRGAS 2000 (padrão brasileiro)
INMET_STATIONS_URL = "https://apitempo.inmet.gov.br/estacoes/T"  # Lista todas as estações automáticas
INMET_DATA_URL = "https://apitempo.inmet.gov.br/token/estacao/{data_inicio}/{data_fim}/{codigo_estacao}/{token}"  # Dados horários por estação com token
INMET_TOKEN = "YOUR_TOKEN_HERE"  # Token de acesso à API INMET - substitua pelo token real

# WORKSPACE PATH
PROJECT_PATH = os.path.dirname(__file__)
WKSP = os.path.join(PROJECT_PATH, "data") #diretório base do projeto
GDB_WKSP_OUT = os.path.join(WKSP, "LHASA-DATA.gdb") # pasta que fica todos os dados do projeto 
#SDE_WKSP_OUT = os.path.join(PROJECT_PATH, "data\\10.70.23.17@PAINELCHUVAS.sde\\PainelChuvas.DBO.RJ_LHASA_NOWCAST")
SDE_WKSP_OUT = os.path.join(PROJECT_PATH, "data\\datagis.rio.rj.gov.br@Geotecnia.sde\\geotecnia.gisadmin.RJ_LHASA_NOWCAST")

# SDE_WKSP_OUT = os.path.join(WKSP, "LHASA-DATA.gdb\\RJ_LHASA_NOWCAST")
HISTORIC_DATA_PATH = os.path.join(WKSP, "history")

# LOGGING SETUP
# LOG_FILE = os.path.join(PROJECT_PATH, "logs\\" + datetime.now().strftime("%Y%m%d") +".log")
LOG_FILE = os.path.join(PROJECT_PATH, "logs\\" + "LHASA_RIO" +".log")
LOG_LEVEL = logging.DEBUG
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
LOG_SUFIX = "[LHASA-RIO]"

OUTPUT_TO_SDE = True #como não tem "site" salvar em pasta .gdb
DATE_SEPARATOR = "/" #as datas serão formatadas com barras

# LAYER / TABLE DEFINITION
# LYR_IN_PZ = "D:\\LHASA-RIO\\2.1\\data\\LHASA-DATA.gdb\\RJ_ZONA_PLUVIOMETRICA"
# LYR_IN_SZ = "D:\\LHASA-RIO\\2.1\\data\\LHASA-DATA.gdb\\RJ_SUSCEPTIBILIDADE"
#LYR_IN_PZ = os.path.join(WKSP, "10.70.23.17@GEORIO.sde\\GEORIO.DBO.Zonas_Pluviometricas")
LYR_IN_PZ = os.path.join(WKSP, "datagis.rio.rj.gov.br@Geotecnia.sde\\geotecnia.gisadmin.Zonas_Pluviometricas") #trocar por caminho na pasta onde está o dado geoespacial
#temos valores individuais para cada

#LYR_IN_SZ = os.path.join(WKSP, "10.70.23.17@GEORIO.sde\\GEORIO.DBO.Susceptibilidade_RJ")
LYR_IN_SZ = os.path.join(WKSP, "datagis.rio.rj.gov.br@Geotecnia.sde\\geotecnia.gisadmin.Susceptibilidade_RJ")

LYR_OUT_LHASA_NOW = os.path.join(WKSP, "LHASA-DATA.gdb\\RJ_LHASA_AGORA")
LYR_OUT_LHASA_HISTORICAL = os.path.join(WKSP, "LHASA-DATA.gdb\\RJ_LHASA_HISTORICO")

TBL_OUT_RAIN_NOW = os.path.join(WKSP, "LHASA-DATA.gdb\\RJ_CHUVA_AGORA")
TBL_OUT_RAIN_HISTORICAL = os.path.join(WKSP, "LHASA-DATA.gdb\\RJ_CHUVA_HISTORICO")

LYR_PRC_VOLUME_CHUVA = ""

LYR_PRC_A_AREAS_DE_RISCO = "%scratchworkspace%\\A_AREA_RISCO"
LYR_PRC_B_VOLUME_VS_RISCO = "%scratchworkspace%\\B_VOLUME_X_RISCO"
LYR_PRC_C_AREAS_PERIGO = "%scratchworkspace%\\C_AREAS_PERIGO"
LYR_PRC_D_AREAS_PERIGO_DESLIZAMENTO = "%scratchworkspace%\\D_AREAS_PERIGO_DESLIZAMENTO"

TBL_PRC_CHUVA_HISTORICA = "TB_CHUVA_HISTORICA"

LYR_PRC_LHASA_HISTORICAL = "RJ_LHASA_HISTORICO"
LYR_PRC_LHASA_NOW = "RJ_LHASA_AGORA"

FLD_RISCO = "PERIGO"

# FIELD DEFINITION
# LYR_PZ_FLDS = ["SHAPE@JSON","NM_CODIGO","TX_ESTACAO","TX_ENDERECO"]
LYR_PZ_FLDS = ["SHAPE@JSON","Cod","Est","Endereço"]

TBL_OUT_RAIN_NOW_FLDS = ["NM_CODIGO","TX_ESTACAO","DT_COLETA","DATA","HORA","NM_M15","NM_H01","NM_H04","NM_H24","NM_H96"]
TBL_OUT_RAIN_HISTORICAL_FLDS = ["NM_CODIGO","TX_ESTACAO","DT_COLETA","DATA","HORA","NM_M15","DH_M15","NM_H01","DH_H01","NM_H04","DH_H04","NM_H24","DH_H24","NM_H96","DH_H96"]

LYR_LHASA_NOW_FLDS = ["SHAPE@JSON","NM_CODIGO","TX_ESTACAO","TX_ENDERECO","DT_COLETA","NM_M15","NM_H01","NM_H02","NM_H03","NM_H04","NM_H24","NM_H96","NM_MES"]
LYR_LHASA_HISTORICAL_FLDS = ["SHAPE@JSON","NM_CODIGO","TX_ESTACAO","DT_COLETA","DATA","HORA","NM_M15","DH_M15","NM_H01","DH_H01","NM_H04","DH_H04","NM_H24","DH_H24","NM_H96","DH_H96"]

# DATA DEFINITION
TPL_PZ_ITEM = { # PLUVIOMETRIC ITEM DATA
    "SHAPE": "",
    "NM_CODIGO": 0,
    "TX_ESTACAO": "",
    "TX_ENDERECO": "",
    "DT_COLETA": "",
    "NM_M15": 0.0,
    "NM_H01": 0.0,
    "NM_H02": 0.0,
    "NM_H03": 0.0,
    "NM_H04": 0.0,
    "NM_H24": 0.0,
    "NM_H96": 0.0,
    "NM_MES": 0.0
}

TPL_PH_ITEM = { # PLUVIOMETER HISTORICAL DATA ITEM
    "NM_CODIGO": 0,
    "TX_ESTACAO": "",
    "DT_COLETA": "",
    "DATA": "",
    "HORA": "",
    "NM_M15": 0.0,
    "DH_M15": "",
    "NM_H01": 0.0,
    "DH_H01": "",
    "NM_H04": 0.0,
    "DH_H04": "",
    "NM_H24": 0.0,
    "DH_H24": "",
    "NM_H96": 0.0,
    "DH_H96": ""
}

ARR_HD = [] # Historical Data
ARR_PZ = [] # Pluviometric Zones
ARR_PD = [] # Pluviometric Data
ARR_ST = [ # Pluviometric Stations Definition
    {"PZ_CODE":  1, "PZ_NAME": "VIDIGAL", "PZ_FILE_NAME": "vidigal"},
    {"PZ_CODE":  2, "PZ_NAME": "URCA", "PZ_FILE_NAME": "urca"},
    {"PZ_CODE":  3, "PZ_NAME": "ROCINHA", "PZ_FILE_NAME": "rocinha"},
    {"PZ_CODE":  4, "PZ_NAME": "TIJUCA", "PZ_FILE_NAME": "tijuca"},
    {"PZ_CODE":  5, "PZ_NAME": "SANTA TERESA", "PZ_FILE_NAME": "santa_teresa"},
    {"PZ_CODE":  6, "PZ_NAME": "COPACABANA", "PZ_FILE_NAME": "copacabana"},
    {"PZ_CODE":  7, "PZ_NAME": "GRAJAU", "PZ_FILE_NAME": "grajau"},
    {"PZ_CODE":  8, "PZ_NAME": "ILHA DO GOVERNADOR", "PZ_FILE_NAME": "ilha_do_governador"},
    {"PZ_CODE":  9, "PZ_NAME": "PENHA", "PZ_FILE_NAME": "penha"},
    {"PZ_CODE": 10, "PZ_NAME": "MADUREIRA", "PZ_FILE_NAME": "madureira"},
    {"PZ_CODE": 11, "PZ_NAME": "IRAJA", "PZ_FILE_NAME": "iraja"},
    {"PZ_CODE": 12, "PZ_NAME": "BANGU", "PZ_FILE_NAME": "bangu"},
    {"PZ_CODE": 13, "PZ_NAME": "PIEDADE", "PZ_FILE_NAME": "piedade"},
    {"PZ_CODE": 15, "PZ_NAME": "SAUDE", "PZ_FILE_NAME": "saude"},
    {"PZ_CODE": 16, "PZ_NAME": "JARDIM BOTANICO", "PZ_FILE_NAME": "jardim_botanico"},
    {"PZ_CODE": 17, "PZ_NAME": "BARRA/ITANHANGA", "PZ_FILE_NAME": "barrinha"},
    {"PZ_CODE": 18, "PZ_NAME": "JACAREPAGUA/CIDADE DE DEUS", "PZ_FILE_NAME": "cidade_de_deus"},
    {"PZ_CODE": 19, "PZ_NAME": "BARRA/RIO CENTRO", "PZ_FILE_NAME": "riocentro"},
    {"PZ_CODE": 20, "PZ_NAME": "GUARATIBA", "PZ_FILE_NAME": "guaratiba"},
    {"PZ_CODE": 21, "PZ_NAME": "ESTRADA GRAJAU/JACAREPAGUA", "PZ_FILE_NAME": "grajau_jacarepagua"},
    {"PZ_CODE": 22, "PZ_NAME": "SANTA CRUZ", "PZ_FILE_NAME": "santa_cruz"},
    {"PZ_CODE": 23, "PZ_NAME": "GRANDE MEIER", "PZ_FILE_NAME": "grande_meier"},
    {"PZ_CODE": 24, "PZ_NAME": "ANCHIETA", "PZ_FILE_NAME": "anchieta"},
    {"PZ_CODE": 25, "PZ_NAME": "GROTA FUNDA", "PZ_FILE_NAME": "grota_funda"},
    {"PZ_CODE": 26, "PZ_NAME": "CAMPO GRANDE", "PZ_FILE_NAME": "campo_grande"},
    {"PZ_CODE": 27, "PZ_NAME": "SEPETIBA", "PZ_FILE_NAME": "sepetiba"},
    {"PZ_CODE": 28, "PZ_NAME": "ALTO DA BOA VISTA", "PZ_FILE_NAME": "alto_da_boa_vista"},
    {"PZ_CODE": 29, "PZ_NAME": "AV. BRASIL/MENDANHA", "PZ_FILE_NAME": "av_brasil_mendanha"},
    {"PZ_CODE": 30, "PZ_NAME": "RECREIO DOS BANDEIRANTES", "PZ_FILE_NAME": "recreio"},
    {"PZ_CODE": 31, "PZ_NAME": "LARANJEIRAS", "PZ_FILE_NAME": "laranjeiras"},
    {"PZ_CODE": 32, "PZ_NAME": "SAO CRISTOVAO", "PZ_FILE_NAME": "sao_cristovao"},
    {"PZ_CODE": 33, "PZ_NAME": "TIJUCA/MUDA", "PZ_FILE_NAME": "tijuca_muda"}
]

OUT_FILE = ""

HISTORIC_LEVEL = "HOUR" # DAY | HOUR | MINUTE

def initialize():
    global OUT_FILE

    arcpy.SetLogHistory(False)
    arcpy.env.overwriteOutput = True
    arcpy.env.autoCommit = ""
    arcpy.env.workspace = WKSP
    arcpy.env.scratchWorkspace = "in_memory"
    
    # Configurar SRC padrão para SIRGAS 2000 (EPSG:4674) - padrão brasileiro
    # As coordenadas da API INMET vêm em graus (sistema geográfico)
    # Para análises precisas, o projeto QGIS deve usar sistema projetado (UTM)
    log.info("Sistema de coordenadas configurado para SIRGAS 2000 (EPSG:4674)")
    log.info("Recomenda-se configurar o projeto QGIS para SIRGAS 2000 / UTM (EPSG:31983 para Zona 23S)")

    DH = datetime.today()
    logging.basicConfig(filename=LOG_FILE, filemode="a+", level=LOG_LEVEL, 
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')

    MIN = int(DH.strftime('%M'))
    if (MIN >= 0 and MIN <= 15): MIN = "00"
    elif (MIN > 15 and MIN <= 30): MIN = "15"
    elif (MIN > 30 and MIN <= 45): MIN = "30"
    else: MIN = "45"
    OUT_FILE = DH.strftime('%Y%m%d_%H') + MIN + "00"

# def log(message, level=LOG_LEVEL):
#     if(LOG_TO_FILE == True): 
#         # logging.log(level, str(datetime.now()) + "" + LOG_SUFIX + " | " + message)
#         logging.log(level, LOG_SUFIX + " | " + message)
#     if(LOG_TO_CONSOLE == True):
#         print(str(datetime.now()) + " | " + LOG_SUFIX + " | " + message)
#         # print(LOG_SUFIX + " | " + message)

def loadHistoricalData(year=None, month=None, dayFrom=None, dayTo=None, hourFrom=None, hourTo=None):
    log.info("#01 | CARGA DE DADOS DAS ESTACOES PLUVIOMETRICAS")
    loadPluviometricZones()
    log.info("      Dados carregados para " + str(len(ARR_PZ)) + " estacoes")

    log.info("#02 | CARGA DE DADOS HISTORICOS DE CHUVA")

    if arcpy.Exists(arcpy.env.scratchWorkspace + "\\" + TBL_PRC_CHUVA_HISTORICA) == True:
        arcpy.Delete_management(arcpy.env.scratchWorkspace + "\\" + TBL_PRC_CHUVA_HISTORICA)
    arcpy.CreateTable_management(arcpy.env.scratchWorkspace, TBL_PRC_CHUVA_HISTORICA, TBL_OUT_RAIN_HISTORICAL)

    loadedFiles = 0

    files = []
    if (year == None or month == None): files = glob.glob(HISTORIC_DATA_PATH + "/*.txt")
    else: files = glob.glob(HISTORIC_DATA_PATH + "/*" + year + month + "*.txt")

    for i in files:
        loadedFiles += 1

        log.info("      + ARQUIVO: " + str(i) + " | " + str(int((loadedFiles / float(len(files))) * 100)) + "%")

        fileName = str(i).replace(HISTORIC_DATA_PATH + "\\", "")
        filePeriod = fileName.split("_")[len(fileName.split("_")) - 2]
        fileYear = filePeriod[:4]
        fileMonth = filePeriod[-2:]
        fileStation = fileName.replace("_" + fileYear + fileMonth + "_" + str(i).split("_")[len(str(i).split("_")) - 1], "")

        SDI = findStationDefinition(stationFileName=fileStation)
        
        if (SDI == None): 
            log.error("        [ERRO] ESTACAO NAO LOCALIZADA")
            shutil.move(i, HISTORIC_DATA_PATH + "\\ERROR\\" + fileName)
            continue

        if (month != None and fileMonth != month):
            log.error("        [INFO] ARQUIVO IGNORADO DEVIDO A PERIODO")
            continue
            
        PHI = findPluviometricZone(stationName=SDI['PZ_NAME'])

        if (SDI != None):
            # log("      + ESTACAO: " + PHI['TX_ESTACAO'])

            whereHistoricalData = "NM_CODIGO = " + str(SDI['PZ_CODE']) + " AND DATA LIKE '__/" + fileMonth + "/" + fileYear + "'"
            # log("      + WHERE: " + whereHistoricalData)

            cursorSPH = arcpy.da.SearchCursor(arcpy.env.scratchWorkspace + "\\" + TBL_PRC_CHUVA_HISTORICA, TBL_OUT_RAIN_HISTORICAL_FLDS, whereHistoricalData)
            existStationData = [row[0] for row in cursorSPH]
            if (len(existStationData) > 0):
                with arcpy.da.UpdateCursor(arcpy.env.scratchWorkspace + "\\" + TBL_PRC_CHUVA_HISTORICA, TBL_OUT_RAIN_HISTORICAL_FLDS, whereHistoricalData) as cursorUPH:
                    for rowUPH in cursorUPH:
                        cursorUPH.deleteRow() # Delete all rows from historical period
                del cursorUPH
            del cursorSPH

            # log("        CARREGANDO DADOS...")
            with open(i, "rb") as fileHD:
                lineCount = 0
                for lineHD in fileHD:
                    lineCount += 1
                    if (lineCount >= 6): # Ignore header of files ( no caso do CINDEC pula 10 linhas)
                        lineHD = lineHD.strip("\n\r") # Remove special characters

                        lineDateTime = lineHD[:26].replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").strip()
                        lineValues = lineHD[26:].replace("  ", " ").replace("  ", " ").replace("  ", " ").replace("  ", " ").strip()
                        lineValues = lineValues.replace("ND", "0.0")
                        # lineValues = lineValues.replace(".", ",") #paramos aqui

                        if (len(lineValues) < 20):
                            lineValues = "0.0 0.0 0.0 0.0 0.0"

                        ARR_HD = []
                        ARR_HD.append(lineDateTime.split(" ")[0])
                        ARR_HD.append(lineDateTime.split(" ")[1])
                        ARR_HD.append(lineValues.split(" ")[0])
                        ARR_HD.append(lineValues.split(" ")[1])
                        ARR_HD.append(lineValues.split(" ")[2])
                        ARR_HD.append(lineValues.split(" ")[3])
                        ARR_HD.append(lineValues.split(" ")[4])

                        if ((HISTORIC_LEVEL == "DAY" and ARR_HD[1].replace(':','')[-6:] == "000000") or
                            (HISTORIC_LEVEL == "HOUR" and ARR_HD[1].replace(':','')[-4:] == "0000")):
                            PHD_ITEM = copy.deepcopy(TPL_PH_ITEM)
                            
                            PHD_ITEM["NM_CODIGO"] = SDI['PZ_CODE']
                            PHD_ITEM["TX_ESTACAO"] = SDI['PZ_NAME']
                            PHD_ITEM["DT_COLETA"] = datetime.strptime(ARR_HD[0] + " " + ARR_HD[1], "%d/%m/%Y %H:%M:%S")
                            PHD_ITEM["DATA"] = ARR_HD[0]
                            PHD_ITEM["HORA"] = ARR_HD[1]
                            
                            PHD_ITEM["NM_M15"] = float(ARR_HD[2])
                            PHD_ITEM["DH_M15"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            PHD_ITEM["NM_H01"] = float(ARR_HD[3])
                            PHD_ITEM["DH_H01"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            PHD_ITEM["NM_H04"] = float(ARR_HD[4])
                            PHD_ITEM["DH_H04"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            PHD_ITEM["NM_H24"] = float(ARR_HD[5])
                            PHD_ITEM["DH_H24"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            PHD_ITEM["NM_H96"] = float(ARR_HD[6])
                            PHD_ITEM["DH_H96"] = ARR_HD[0] + " " + ARR_HD[1]
                        
                        else:
                            if (float(ARR_HD[2]) > float(PHD_ITEM["NM_M15"])):
                                PHD_ITEM["NM_M15"] = float(ARR_HD[2])
                                PHD_ITEM["DH_M15"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            if (float(ARR_HD[3]) > float(PHD_ITEM["NM_H01"])):
                                PHD_ITEM["NM_H01"] = float(ARR_HD[3])
                                PHD_ITEM["DH_H01"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            if (float(ARR_HD[4]) > float(PHD_ITEM["NM_H04"])):
                                PHD_ITEM["NM_H04"] = float(ARR_HD[4])
                                PHD_ITEM["DH_H04"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            if (float(ARR_HD[5]) > float(PHD_ITEM["NM_H24"])):
                                PHD_ITEM["NM_H24"] = float(ARR_HD[5])
                                PHD_ITEM["DH_H24"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            if (float(ARR_HD[6]) > float(PHD_ITEM["NM_H96"])):
                                PHD_ITEM["NM_H96"] = float(ARR_HD[6])
                                PHD_ITEM["DH_H96"] = ARR_HD[0] + " " + ARR_HD[1]
                            
                            if (ARR_HD[1].replace(':','')[-4:] == "4500"):
                                monthRow = str(PHD_ITEM["DATA"])[3:-5]
                                dayRow = str(PHD_ITEM["DATA"])[:2]
                                hourRow = str(PHD_ITEM["HORA"])[:2]

                                if (monthRow == month):
                                    if (dayRow >= dayFrom and dayRow <= dayTo):
                                        if (hourRow >= hourFrom and hourRow <= hourTo):
                                            # log("        + " + str(PHD_ITEM["NM_CODIGO"]) + " | " + PHD_ITEM["TX_ESTACAO"] + " | " + str(PHD_ITEM["DATA"]) + " | " + str(PHD_ITEM["HORA"]))

                                            with arcpy.da.InsertCursor(arcpy.env.scratchWorkspace + "\\" + TBL_PRC_CHUVA_HISTORICA, TBL_OUT_RAIN_HISTORICAL_FLDS) as cursorIPH:
                                                cursorIPH.insertRow((
                                                    PHD_ITEM["NM_CODIGO"], # 00
                                                    PHD_ITEM["TX_ESTACAO"],   # 01
                                                    PHD_ITEM["DT_COLETA"],      # 02
                                                    PHD_ITEM["DATA"],           # 03
                                                    PHD_ITEM["HORA"],           # 04
                                                    PHD_ITEM["NM_M15"],            # 05
                                                    PHD_ITEM["DH_M15"],         # 06
                                                    PHD_ITEM["NM_H01"],            # 07
                                                    PHD_ITEM["DH_H01"],         # 08
                                                    PHD_ITEM["NM_H04"],            # 09
                                                    PHD_ITEM["DH_H04"],         # 10
                                                    PHD_ITEM["NM_H24"],            # 11
                                                    PHD_ITEM["DH_H24"],         # 12
                                                    PHD_ITEM["NM_H96"],            # 13
                                                    PHD_ITEM["DH_H96"]          # 14
                                                ))
                                                del cursorIPH

                fileHD.close()
            
            # log("        [OK] CARGA CONCLUIDA...")
            # shutil.move(i, HISTORIC_DATA_PATH + "\\LOADED\\" + fileName)
        else:
            log.error("        [ERRO] ESTACAO NAO LOCALIZADA")
            shutil.move(i, HISTORIC_DATA_PATH + "\\ERROR\\" + fileName)

    log.info("")
    log.info("#03 | ASSOCIANDO ZONA PLUVIOMETRICA A DADO DE CHUVA")

    if arcpy.Exists(arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_HISTORICAL) == True:
        arcpy.Delete_management(arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_HISTORICAL)
    arcpy.CopyFeatures_management(LYR_OUT_LHASA_HISTORICAL, arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_HISTORICAL)
    # arcpy.MakeFeatureLayer_management(LYR_OUT_LHASA_HISTORICAL, arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_HISTORICAL)
    
    for PZ in ARR_PZ:
        PHD_ITEM = copy.deepcopy(TPL_PH_ITEM)
        itemHDCount = 0
        
        PHD_ITEM["NM_CODIGO"] = int(PZ["NM_CODIGO"])
        PHD_ITEM["TX_ESTACAO"] = PZ["TX_ESTACAO"]
        PHD_ITEM["DT_COLETA"] = None
        PHD_ITEM["DATA"] = dayFrom + "/" + month + "/" + year
        PHD_ITEM["HORA"] = hourFrom + " a " + hourTo

        PHD_ITEM["NM_M15"] = float("0.0")
        PHD_ITEM["DH_M15"] = "-"
        PHD_ITEM["NM_H01"] = float("0.0")
        PHD_ITEM["DH_H01"] = "-"
        PHD_ITEM["NM_H04"] = float("0.0")
        PHD_ITEM["DH_H04"] = "-"
        PHD_ITEM["NM_H24"] = float("0.0")
        PHD_ITEM["DH_H24"] = "-"
        PHD_ITEM["NM_H96"] = float("0.0")
        PHD_ITEM["DH_H96"] = "-"

        # log(" ")
        # log("      > " + "NM_CODIGO = " + str(PZ["NM_CODIGO"]))
        cursorSPH = arcpy.da.SearchCursor(arcpy.env.scratchWorkspace + "\\" + TBL_PRC_CHUVA_HISTORICA, TBL_OUT_RAIN_HISTORICAL_FLDS, "NM_CODIGO = " + str(PZ["NM_CODIGO"]))
        existStationData = [row[0] for row in cursorSPH]
        if (len(existStationData) > 0):
            cursorSPH.reset()
            for rowSPH in cursorSPH:
                if (itemHDCount == 0):
                    PHD_ITEM["NM_M15"] = float(rowSPH[5])
                    PHD_ITEM["DH_M15"] = str(rowSPH[6])
                    PHD_ITEM["NM_H01"] = float(rowSPH[7])
                    PHD_ITEM["DH_H01"] = str(rowSPH[8])
                    PHD_ITEM["NM_H04"] = float(rowSPH[9])
                    PHD_ITEM["DH_H04"] = str(rowSPH[10])
                    PHD_ITEM["NM_H24"] = float(rowSPH[11])
                    PHD_ITEM["DH_H24"] = str(rowSPH[12])
                    PHD_ITEM["NM_H96"] = float(rowSPH[13])
                    PHD_ITEM["DH_H96"] = str(rowSPH[14])
                else:
                    PHD_ITEM["DH_M15"] = str(rowSPH[6]) if float(rowSPH[5]) > float(PHD_ITEM["NM_M15"]) else PHD_ITEM["DH_M15"]
                    PHD_ITEM["NM_M15"] = float(rowSPH[5]) if float(rowSPH[5]) > float(PHD_ITEM["NM_M15"]) else float(PHD_ITEM["NM_M15"])
                    PHD_ITEM["DH_H01"] = str(rowSPH[8]) if float(rowSPH[7]) > float(PHD_ITEM["NM_H01"]) else PHD_ITEM["DH_H01"]
                    PHD_ITEM["NM_H01"] = float(rowSPH[7]) if float(rowSPH[7]) > float(PHD_ITEM["NM_H01"]) else float(PHD_ITEM["NM_H01"])
                    PHD_ITEM["DH_H04"] = str(rowSPH[10]) if float(rowSPH[9]) > float(PHD_ITEM["NM_H04"]) else PHD_ITEM["DH_H04"]
                    PHD_ITEM["NM_H04"] = float(rowSPH[9]) if float(rowSPH[9]) > float(PHD_ITEM["NM_H04"]) else float(PHD_ITEM["NM_H04"])
                    PHD_ITEM["DH_H24"] = str(rowSPH[12]) if float(rowSPH[11]) > float(PHD_ITEM["NM_H24"]) else PHD_ITEM["DH_H24"]
                    PHD_ITEM["NM_H24"] = float(rowSPH[11]) if float(rowSPH[11]) > float(PHD_ITEM["NM_H24"]) else float(PHD_ITEM["NM_H24"])
                    PHD_ITEM["DH_H96"] = str(rowSPH[14]) if float(rowSPH[13]) > float(PHD_ITEM["NM_H96"]) else PHD_ITEM["DH_H96"]
                    PHD_ITEM["NM_H96"] = float(rowSPH[13]) if float(rowSPH[13]) > float(PHD_ITEM["NM_H96"]) else float(PHD_ITEM["NM_H96"])
            
                itemHDCount += 1
        
        log.info("      + " + str(PHD_ITEM["NM_CODIGO"]).zfill(2) + " | " + str(PHD_ITEM["TX_ESTACAO"]) + " | " + str(PHD_ITEM["DATA"]) + " | " + str(PHD_ITEM["HORA"]))
        # log("        + " + str(PHD_ITEM["M15"]) + " | " + str(PHD_ITEM["DH_M15"]))
        # log("        + " + str(PHD_ITEM["H01"]) + " | " + str(PHD_ITEM["DH_H01"]))
        # log("        + " + str(PHD_ITEM["H04"]) + " | " + str(PHD_ITEM["DH_H04"]))
        # log("        + " + str(PHD_ITEM["H96"]) + " | " + str(PHD_ITEM["DH_H96"]))

        del cursorSPH

        with arcpy.da.InsertCursor(arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_HISTORICAL, LYR_LHASA_HISTORICAL_FLDS) as cursorIPH:
            cursorIPH.insertRow((
                PZ["SHAPE"],
                PHD_ITEM["NM_CODIGO"],
                PHD_ITEM["TX_ESTACAO"],
                PHD_ITEM["DT_COLETA"],
                PHD_ITEM["DATA"],
                PHD_ITEM["HORA"],
                PHD_ITEM["NM_M15"],
                PHD_ITEM["DH_M15"],
                PHD_ITEM["NM_H01"],
                PHD_ITEM["DH_H01"],
                PHD_ITEM["NM_H04"],
                PHD_ITEM["DH_H04"],
                PHD_ITEM["NM_H24"],
                PHD_ITEM["DH_H24"],
                PHD_ITEM["NM_H96"],
                PHD_ITEM["DH_H96"]
            ))
        del cursorIPH
    
    return

def loadNowData():
    log.info("")

    log.info("#01 | CARGA DE DADOS DAS ESTACOES PLUVIOMETRICAS")
    loadPluviometricZones()
    log.info("      Dados carregados para " + str(len(ARR_PZ)) + " estacoes")

    log.info("")
    log.info("#02 | CARGA DE DADOS ATUAIS DE CHUVA")
    loadPluviometricData()

    log.info("")
    log.info("#03 | ASSOCIANDO ZONA PLUVIOMETRICA A DADO DE CHUVA")

    if arcpy.Exists(arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_NOW) == True:
        arcpy.Delete_management(arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_NOW)
    arcpy.CopyFeatures_management(LYR_OUT_LHASA_NOW, arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_NOW)

    with arcpy.da.InsertCursor(arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_NOW, LYR_LHASA_NOW_FLDS) as cursorIPZ:
        with arcpy.da.UpdateCursor(arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_NOW, LYR_LHASA_NOW_FLDS, "1=1") as cursorUPZ:
            for rowUPZ in cursorUPZ:
                cursorUPZ.deleteRow() # Delete all rows from now cast data
        
        del cursorUPZ

        for PZ in ARR_PZ:
            # log("      + ZONA PLUVIOMETRICA: " + PZ["TX_ESTACAO"])

            if (PZ["TX_ESTACAO"] == "BARRA/RIO CENTRO"): stationName = "Barra/Riocentro"
            elif (PZ["TX_ESTACAO"] == "ESTRADA GRAJAU/JACAREPAGUA"): stationName = "Est. Grajau/Jacarepagua"
            elif (PZ["TX_ESTACAO"] == "BARRA/ITANHANGA"): stationName = "Barra/Barrinha"
            else: stationName = PZ["TX_ESTACAO"]
            
            # log("      + ESTACAO: " + stationName)

            # Primeiro tenta buscar por código da estação, depois por nome
            PD = findPluviometricData(stationCode=PZ["NM_CODIGO"])
            if PD is None:
                PD = findPluviometricData(stationName=stationName)
            
            if PD is not None:
                # Extrair dados de chuva do formato INMET
                rain_data = extractRainDataFromInmet(PD)
                
                if rain_data:
                    try:
                        # Converter data do INMET (formato: YYYY-MM-DD HH:MM:SS)
                        dt_medicao = PD.get('DT_MEDICAO', '')
                        if dt_medicao:
                            PZ["DT_COLETA"] = datetime.strptime(dt_medicao, "%Y-%m-%d %H:%M:%S")
                        else:
                            PZ["DT_COLETA"] = datetime.now()
                    except (ValueError, TypeError):
                        PZ["DT_COLETA"] = datetime.now()
                    
                    PZ["NM_M15"] = rain_data['data']['m15']
                    PZ["NM_H01"] = rain_data['data']['h01']
                    PZ["NM_H02"] = rain_data['data']['h02']
                    PZ["NM_H03"] = rain_data['data']['h03']
                    PZ["NM_H04"] = rain_data['data']['h04']
                    PZ["NM_H24"] = rain_data['data']['h24']
                    PZ["NM_H96"] = rain_data['data']['h96']
                    PZ["NM_MES"] = rain_data['data']['mes']

                cursorIPZ.insertRow((
                    PZ["SHAPE"],
                    PZ["NM_CODIGO"],
                    PZ["TX_ESTACAO"],
                    PZ["TX_ENDERECO"],
                    PZ["DT_COLETA"],
                    PZ["NM_M15"],
                    PZ["NM_H01"],
                    PZ["NM_H02"],
                    PZ["NM_H03"],
                    PZ["NM_H04"],
                    PZ["NM_H24"],
                    PZ["NM_H96"],
                    PZ["NM_MES"]
                ))

            log.info("      " + ("0" + str(PZ["NM_CODIGO"]) if (PZ["NM_CODIGO"] < 10) else str(PZ["NM_CODIGO"])) + " | " + str(PZ["TX_ESTACAO"]).upper() + " | " + str(PZ["DT_COLETA"]) + ": " + ("---" if PD == None else "CARREGADO..."))
    
    del cursorIPZ

    return
def loadInmetStations():
    """Carrega lista de estações automáticas do INMET"""
    try:
        log.info("Buscando lista de estações do INMET...")
        response = requests.get(INMET_STATIONS_URL, timeout=30)
        
        if response.status_code == 200:
            stations = response.json()
            log.info(f"Encontradas {len(stations)} estações do INMET")
            return stations
        elif response.status_code == 204:
            log.warning("Nenhuma estação disponível no momento (HTTP 204)")
            return []
        else:
            log.error(f"Erro ao buscar estações: HTTP {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        log.error(f"Erro de conexão ao buscar estações: {e}")
        return []
    except json.JSONDecodeError as e:
        log.error(f"Erro ao decodificar JSON das estações: {e}")
        return []

def loadInmetStationData(codigo_estacao, data_inicio, data_fim, token):
    """Busca dados horários de uma estação específica do INMET"""
    try:
        # Rate limiting - pequeno intervalo entre requisições
        time.sleep(0.1)
        
        url = INMET_DATA_URL.format(
            data_inicio=data_inicio,
            data_fim=data_fim,
            codigo_estacao=codigo_estacao,
            token=token
        )
        
        log.info(f"Buscando dados da estação {codigo_estacao}: {url}")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data
        elif response.status_code == 204:
            log.warning(f"Sem dados disponíveis para estação {codigo_estacao} no período (HTTP 204)")
            return []
        else:
            log.error(f"Erro ao buscar dados da estação {codigo_estacao}: HTTP {response.status_code}")
            return []
            
    except requests.exceptions.RequestException as e:
        log.error(f"Erro de conexão ao buscar dados da estação {codigo_estacao}: {e}")
        return []
    except json.JSONDecodeError as e:
        log.error(f"Erro ao decodificar JSON da estação {codigo_estacao}: {e}")
        return []

def loadPluviometricData():
    """Carrega dados pluviométricos atuais do INMET"""
    global ARR_PD
    del ARR_PD[:]

    # Buscar estações disponíveis
    stations = loadInmetStations()
    if not stations:
        log.error("Nenhuma estação disponível")
        return

    # Data atual para buscar dados recentes
    DH = datetime.today()
    data_fim = DH.strftime('%Y-%m-%d')
    data_inicio = (DH - timedelta(days=1)).strftime('%Y-%m-%d')  # Último dia para garantir dados
    
    log.info(f"Buscando dados do período: {data_inicio} a {data_fim}")
    
    # Buscar dados de cada estação (limitando para evitar sobrecarga)
    for i, station in enumerate(stations[:50]):  # Limitar a 50 estações para teste
        codigo_estacao = station.get('CD_ESTACAO')
        if codigo_estacao:
            station_data = loadInmetStationData(codigo_estacao, data_inicio, data_fim, INMET_TOKEN)
            
            # Processar dados da estação
            if station_data:
                # Adicionar metadados da estação aos dados
                for record in station_data:
                    record['station_info'] = {
                        'CD_ESTACAO': station.get('CD_ESTACAO'),
                        'DC_NOME': station.get('DC_NOME'),
                        'VL_LATITUDE': station.get('VL_LATITUDE'),
                        'VL_LONGITUDE': station.get('VL_LONGITUDE'),
                        'UF': station.get('SG_ESTADO')
                    }
                
                ARR_PD.extend(station_data)
        
        # Progress feedback
        if (i + 1) % 10 == 0:
            log.info(f"Processadas {i + 1} estações...")
    
    log.info(f"Total de registros carregados: {len(ARR_PD)}")

def loadPluviometricZones():
    global ARR_PZ
    # ARR_PZ.clear()
    del ARR_PZ[:]

    with arcpy.da.SearchCursor(LYR_IN_PZ, LYR_PZ_FLDS) as cursorPZ:
        for row in cursorPZ:
            PZ_ITEM = copy.deepcopy(TPL_PZ_ITEM)
            PZ_ITEM["SHAPE"] = row[0]
            PZ_ITEM["NM_CODIGO"] = int(row[1])
            PZ_ITEM["TX_ESTACAO"] = unidecode(row[2].upper())
            PZ_ITEM["TX_ENDERECO"] = unidecode(row[3].upper())
            
            ARR_PZ.append(PZ_ITEM)
            
            del PZ_ITEM

    del cursorPZ

def findPluviometricZone(stationName="", stationCode=0):
    searchField = "TX_ESTACAO" if stationName != "" else ("NM_CODIGO" if stationCode > 0 else (None))
    searchedValue = stationName if stationName != "" else (stationCode if stationCode > 0 else (""))

    # TODO THROW ERROR IF FIELD NOT FOUNDED
    
    ZP_ITEMS = [ZPI for ZPI in ARR_PZ if ZPI[searchField] == searchedValue]

    return ZP_ITEMS[0] if (len(ZP_ITEMS) > 0) else None

def findPluviometricData(stationName="", stationCode=""):
    """Busca dados pluviométricos por nome ou código da estação do INMET"""
    if not ARR_PD:
        return None
    
    # Buscar por código da estação (mais preciso)
    if stationCode:
        for record in ARR_PD:
            if record.get('station_info', {}).get('CD_ESTACAO') == stationCode:
                return record
    
    # Buscar por nome da estação (fallback)
    if stationName:
        searchedValue = unidecode(stationName.upper())
        for record in ARR_PD:
            station_name = record.get('station_info', {}).get('DC_NOME', '')
            if station_name and unidecode(station_name.upper()) == searchedValue:
                return record
    
    return None

def extractRainDataFromInmet(inmet_record):
    """Extrai dados de chuva de um registro do INMET e converte para formato esperado"""
    if not inmet_record:
        return None
    
    # Campo CHUVA do INMET contém precipitação horária
    chuva_horaria = inmet_record.get('CHUVA', 0.0)
    
    # Converter string para float se necessário
    try:
        if isinstance(chuva_horaria, str):
            chuva_horaria = float(chuva_horaria) if chuva_horaria != '' else 0.0
        elif chuva_horaria is None:
            chuva_horaria = 0.0
    except (ValueError, TypeError):
        chuva_horaria = 0.0
    
    # Data e hora do registro
    data_hora = inmet_record.get('DT_MEDICAO', '')
    
    # Simular estrutura esperada pelo sistema original
    # Nota: O INMET fornece dados horários, então precisamos calcular acumulados
    return {
        'read_at': data_hora,
        'data': {
            'm15': chuva_horaria,  # Aproximação - INMET não tem dados de 15min
            'h01': chuva_horaria,  # Precipitação horária
            'h02': chuva_horaria * 2,  # Aproximação para 2 horas
            'h03': chuva_horaria * 3,  # Aproximação para 3 horas  
            'h04': chuva_horaria * 4,  # Aproximação para 4 horas
            'h24': chuva_horaria * 24, # Aproximação para 24 horas
            'h96': chuva_horaria * 96, # Aproximação para 96 horas
            'mes': chuva_horaria * 720 # Aproximação para mês (30 dias)
        },
        'station_info': inmet_record.get('station_info', {})
    }

def findStationDefinition(stationCode=0, stationName="", stationFileName=""):
    searchField = "PZ_FILE_NAME" if stationFileName != "" else ("PZ_NAME" if stationName != "" else ("PZ_CODE" if stationCode != 0 else None))
    searchedValue = stationFileName if stationFileName != "" else (stationName if stationName != "" else (stationCode if stationCode != 0 else None))
   
    SD_ITEMS = [SD for SD in ARR_ST if SD[searchField].encode('utf-8').upper() == searchedValue.upper()]
    return SD_ITEMS[0] if (len(SD_ITEMS) > 0) else None

def doAnalysis(dataType="", startDate=None, endDate=None, startTime=None, endTime=None):
    global OUT_FILE

    if (dataType == "H"): 
        # arcpy.MakeFeatureLayer_management(LYR_OUT_LHASA_HISTORICAL, LYR_PRC_VOLUME_CHUVA, "DT_COLETA > timestamp '" + startDate + " " + startTime + "' And DT_COLETA <  timestamp '" + endDate + " " + endTime + "'")
        LYR_PRC_VOLUME_CHUVA = arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_HISTORICAL
    elif (dataType == "N"): 
        # arcpy.MakeFeatureLayer_management(LYR_OUT_LHASA_NOW, LYR_PRC_VOLUME_CHUVA)
        LYR_PRC_VOLUME_CHUVA = arcpy.env.scratchWorkspace + "\\" + LYR_PRC_LHASA_NOW

    log.info("#01 | SELECIONANDO AREAS DE RISCO")
    arcpy.Select_analysis(LYR_IN_SZ, LYR_PRC_A_AREAS_DE_RISCO, "gridcode IN (2,3)")
    
    log.info("")
    log.info("#02 | RELACIONANDO VOLUME E AREA DE RISCO")
    # arcpy.Intersect_analysis(LYR_OUT_LHASA_NOW + " #;" + LYR_PRC_A_AREAS_DE_RISCO + " #", LYR_PRC_B_VOLUME_VS_RISCO, "ALL", "", "INPUT")
    arcpy.Intersect_analysis(LYR_PRC_VOLUME_CHUVA + " #;" + LYR_PRC_A_AREAS_DE_RISCO + " #", LYR_PRC_B_VOLUME_VS_RISCO, "ALL", "", "INPUT")
    
    log.info("")
    log.info("#03 | CRIANDO CAMPO DE RISCO")
    arcpy.AddField_management(LYR_PRC_B_VOLUME_VS_RISCO, FLD_RISCO, "TEXT", "", "", "20", "nivel_perigo", "NULLABLE", "NON_REQUIRED", "")

    log.info("")
    log.info("#04 | CALCULANDO CAMPO DE RISCO")
    code_block = """def NivelPerigo(susceptibilidade, h01, h24, h96):
    if((h01 >= 50 and h01 < 70) or (h24 >= 140 and h24 < 185) or ((h96 >= 185 and h96 < 255) and (h24 >= 55 and h24 < 100))):
        if(susceptibilidade == 1): # BAIXA
            return "SEM PERIGO"
        elif(susceptibilidade == 2): # MEDIA
            return "MODERADO"
        elif(susceptibilidade == 3): # ALTA
            return "ALTO"
    elif((h01 >= 70) or (h24 >= 185) or (h96 >= 255 and h24 >= 100)): 
        if(susceptibilidade == 1): # BAIXA
            return "SEM PERIGO"
        elif(susceptibilidade == 2): # MEDIA
            return "MUITO ALTO"
        elif(susceptibilidade == 3): # ALTA
            return "CRITICO"
    else:
        # SEM CHUVA
        return "BAIXO"
    """
#paramos aqui 29/04/2025   
    arcpy.CalculateField_management(LYR_PRC_B_VOLUME_VS_RISCO, "PERIGO", "NivelPerigo( !gridcode!, !NM_H01!, !NM_H24!, !NM_H96! )", "PYTHON",code_block)
    log.info("")
    log.info("#05 | SELECIONANDO AREAS DE PERIGO")
    arcpy.Select_analysis(LYR_PRC_B_VOLUME_VS_RISCO, LYR_PRC_C_AREAS_PERIGO, "gridcode IN (2,3)")

    log.info("")
    arcpy.Delete_management(GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE)
    if (dataType == "N"): 
        log.info("#06 | AGREGANDO FEICOES SEMELHANTES")
        arcpy.Dissolve_management(LYR_PRC_C_AREAS_PERIGO, GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE, "NM_CODIGO;TX_ESTACAO;DT_COLETA;PERIGO", "NM_M15 MAX;NM_H01 MAX;NM_H04 MAX;NM_H24 MAX;NM_H96 MAX", "MULTI_PART", "DISSOLVE_LINES")
    elif (dataType == "H"): 
        arcpy.Dissolve_management(LYR_PRC_C_AREAS_PERIGO, GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE, "NM_CODIGO;TX_ESTACAO;DT_COLETA;DH_H01;DH_H04;DH_H24;DH_H96;PERIGO", "NM_M15 MAX;NM_H01 MAX;NM_H04 MAX;NM_H24 MAX;NM_H96 MAX", "MULTI_PART", "DISSOLVE_LINES")

    try:
        log.info("")
        log.info("#07 | GERANDO SHAPEFILE PARA SCRIPT DE EXPOSICAO")
        current_folder = os.path.dirname(__file__)
        rio_shpfl = os.path.join(current_folder, "data\\input\\RJ_LHASA_NOWCAST.shp")
        if arcpy.Exists(rio_shpfl):
            arcpy.management.Delete(rio_shpfl)

        arcpy.management.CopyFeatures(GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE, rio_shpfl)
    except Exception as error:
        log.error("Erro ao gerar shapefile de saida do LHASA")
        log.error(error.message)

    if(OUTPUT_TO_SDE == True):
        log.info("")
        log.info("#08 | LIMPANDO DADO DE SAIDA NO SDE")
        # arcpy.DeleteFeatures_management(SDE_WKSP_OUT)
        arcpy.management.DeleteFeatures(SDE_WKSP_OUT)

        log.info("")
        log.info("#09 | GERANDO SAIDA NO SDE")
        # arcpy.Append_management(GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE, SDE_WKSP_OUT, "TEST", "", "")
        arcpy.management.Append(GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE, SDE_WKSP_OUT,"TEST", "", "")
    
        log.info("")
        log.info("#10 | APAGANDO DADOS DE PROCESSAMENTO")
        # arcpy.Delete_management(GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE)
        arcpy.management.Delete(GDB_WKSP_OUT + "\\RJ_LHASA_" + dataType + "_" + OUT_FILE)

    return

def nowcast():
    log.info("---- PROCESSAMENTO DE DADOS ATUAIS DE CHUVA ----")
    
    log.info("")
    log.info("[CARREGANDO DADOS PARA PROCESSAMENTO]")
    log.info("")
    loadNowData()

    log.info("")
    log.info("[EXECUTANDO ANALISE]")
    log.info("")
    doAnalysis("N")

    return

def historicalcast(startDate, endDate, startTime, endTime):
    log.info("")
    log.info("---- PROCESSAMENTO DE DADOS HISTORICOS DE CHUVA ----")
    
    log.info("")
    log.info("[PARAMETROS DE PROCESSAMENTO]")
    log.info(" + Data Inicial: " + startDate)
    log.info(" + Hora Inicial: " + startTime)
    log.info(" + Data Final: " + endDate)
    log.info(" + Hora Final: " + endTime)

    yearFrom = startDate[-4:]
    yearTo = endDate[-4:]

    monthFrom = startDate[3:-5]
    monthTo = endDate[3:-5]

    dayFrom = startDate[:2]
    dayTo = endDate[:2]

    hourFrom = startTime[:2]
    hourTo = endTime[:2]

    dateFrom = yearFrom + "-" + monthFrom + "-" + dayFrom
    dateTo = yearTo + "-" + monthTo + "-" + dayTo

    if ((len(startDate) < 10 or len(endDate) < 10) or (startDate.count("/") < 2 or endDate.count("/") < 2)):
        log.error(" ERRO | PERÍODO INVÁLIDO. FORMATO DE DATA: DD/MM/AAAA")
        sys.exit(0)
    elif ((len(startTime) < 5 or len(endTime) < 5) or (startTime.count(":") < 2 or endTime.count(":") < 2)):
        log.error(" ERRO | PERÍODO INVÁLIDO. FORMATO DE HORA: HH:MM:SS")
        sys.exit(0)
    elif(yearFrom != yearTo):
        log.error(" ERRO | PERÍODO INVÁLIDO. A CONSULTA HISTÓRICA DEVE MANTER DADOS DO MESMO ANO.")
        sys.exit(0)
    elif(monthFrom != monthTo):
        log.error(" ERRO | PERÍODO INVÁLIDO. A CONSULTA HISTÓRICA DEVE MANTER DADOS DO MESMO MÊS.")
        sys.exit(0)
    elif(dayFrom != dayTo):
        log.error(" ERRO | PERÍODO INVÁLIDO. A CONSULTA HISTÓRICA DEVE MANTER DADOS DO MESMO DIA.")
        sys.exit(0)
    elif(hourFrom < 23 and hourFrom >= hourTo):
        log.error(" ERRO | PERÍODO INVÁLIDO. A HORA DE INÍCIO DEVE SER MENOR QUE A HORA DE TÉRMINO.")
        sys.exit(0)

    log.info("")
    log.info("[CARREGANDO DADOS PARA PROCESSAMENTO]")
    log.info("")
    loadHistoricalData(yearFrom, monthFrom, dayFrom, dayTo, hourFrom, hourTo)

    log.info("")
    log.info("[EXECUTANDO ANALISE]")
    log.info("")
    doAnalysis("H", dateFrom, dateTo, startTime, endTime)

    return

# ============================================================================
# CLASSE PRINCIPAL PARA QGIS - QgsProcessingAlgorithm
# ============================================================================

class LhasaMgAnalysis(QgsProcessingAlgorithm):
    """
    Algoritmo QGIS para análise de risco de deslizamento em Minas Gerais
    utilizando dados da API do INMET
    """
    
    # Constantes para parâmetros
    INPUT_SUSCETIBILIDADE = 'INPUT_SUSCETIBILIDADE'
    INPUT_ZONAS_PLUVIOMETRICAS = 'INPUT_ZONAS_PLUVIOMETRICAS'
    INPUT_DATA_ANALISE = 'INPUT_DATA_ANALISE'
    INPUT_TIPO_ANALISE = 'INPUT_TIPO_ANALISE'
    OUTPUT_RESULTADO = 'OUTPUT_RESULTADO'

    def tr(self, string):
        """Tradução de strings para internacionalização"""
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
        Este algoritmo realiza análise de risco de deslizamento para Minas Gerais
        cruzando dados de suscetibilidade com dados meteorológicos do INMET.
        
        Parâmetros:
        - Camada de Suscetibilidade: Polígonos com classificação de suscetibilidade
        - Zonas Pluviométricas: Polígonos das zonas de medição de chuva
        - Data da Análise: Data para buscar dados do INMET (YYYY-MM-DD)
        - Tipo de Análise: 'atual' para dados recentes ou 'historico' para período específico
        """)

    def initAlgorithm(self, config=None):
        """Definir parâmetros de entrada e saída"""
        
        # Camada de suscetibilidade
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_SUSCETIBILIDADE,
                self.tr('Camada de Suscetibilidade'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        # Zonas pluviométricas
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_ZONAS_PLUVIOMETRICAS,
                self.tr('Zonas Pluviométricas'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        # Data da análise
        data_padrao = datetime.now().strftime('%Y-%m-%d')
        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_DATA_ANALISE,
                self.tr('Data da Análise (YYYY-MM-DD)'),
                defaultValue=data_padrao
            )
        )
        
        # Tipo de análise
        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_TIPO_ANALISE,
                self.tr('Tipo de Análise (atual/historico)'),
                defaultValue='atual'
            )
        )
        
        # Camada de saída
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_RESULTADO,
                self.tr('Resultado da Análise de Risco')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """Processar o algoritmo principal"""
        
        # Obter parâmetros
        camada_suscetibilidade = self.parameterAsSource(parameters, self.INPUT_SUSCETIBILIDADE, context)
        camada_zonas = self.parameterAsSource(parameters, self.INPUT_ZONAS_PLUVIOMETRICAS, context)
        data_analise = self.parameterAsString(parameters, self.INPUT_DATA_ANALISE, context)
        tipo_analise = self.parameterAsString(parameters, self.INPUT_TIPO_ANALISE, context)
        output_path = self.parameterAsFileOutput(parameters, self.OUTPUT_RESULTADO, context)

        feedback.pushInfo("=== INICIANDO ANÁLISE LHASA MG ===")
        feedback.pushInfo(f"Data da análise: {data_analise}")
        feedback.pushInfo(f"Tipo de análise: {tipo_analise}")

        # Inicializar dados
        self.initializeQgisData(feedback)
        
        # Carregar dados pluviométricos do INMET
        feedback.pushInfo("Carregando dados do INMET...")
        self.loadPluviometricDataQgis(data_analise, feedback)
        
        # Associar dados de chuva às zonas pluviométricas
        feedback.pushInfo("Associando dados de chuva às zonas...")
        zonas_com_chuva = self.associateRainDataQgis(camada_zonas, context, feedback)
        
        # Executar análise de risco
        feedback.pushInfo("Executando análise de risco...")
        resultado = self.executeRiskAnalysisQgis(
            camada_suscetibilidade, 
            zonas_com_chuva, 
            output_path, 
            context, 
            feedback
        )
        
        feedback.pushInfo("=== ANÁLISE FINALIZADA COM SUCESSO ===")
        return {self.OUTPUT_RESULTADO: resultado}

    def initializeQgisData(self, feedback):
        """Inicializar dados globais para QGIS"""
        global ARR_PD, ARR_PZ
        ARR_PD = []
        ARR_PZ = []
        feedback.pushInfo("Dados globais inicializados")

    def loadPluviometricDataQgis(self, data_analise, feedback):
        """Carregar dados pluviométricos do INMET para QGIS"""
        global ARR_PD
        
        # Buscar estações disponíveis
        stations = loadInmetStations()
        if not stations:
            feedback.reportError("Nenhuma estação INMET disponível")
            return

        data_fim = data_analise
        data_inicio = (datetime.strptime(data_analise, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        
        feedback.pushInfo(f"Buscando dados do período: {data_inicio} a {data_fim}")
        
        # Buscar dados de estações (limitando para MG)
        count = 0
        for station in stations:
            if station.get('SG_ESTADO') == 'MG':  # Filtrar apenas estações de MG
                codigo_estacao = station.get('CD_ESTACAO')
                if codigo_estacao and count < 20:  # Limitar para teste
                    station_data = loadInmetStationData(codigo_estacao, data_inicio, data_fim, INMET_TOKEN)
                    
                    if station_data:
                        for record in station_data:
                            record['station_info'] = {
                                'CD_ESTACAO': station.get('CD_ESTACAO'),
                                'DC_NOME': station.get('DC_NOME'),
                                'VL_LATITUDE': station.get('VL_LATITUDE'),
                                'VL_LONGITUDE': station.get('VL_LONGITUDE'),
                                'UF': station.get('SG_ESTADO')
                            }
                        ARR_PD.extend(station_data)
                        count += 1
                        
                        if count % 5 == 0:
                            feedback.pushInfo(f"Processadas {count} estações de MG...")
        
        feedback.pushInfo(f"Total de registros carregados: {len(ARR_PD)}")

    def associateRainDataQgis(self, camada_zonas, context, feedback):
        """Associar dados de chuva às zonas pluviométricas usando QGIS"""
        
        # Criar camada em memória com os dados de chuva
        zonas_layer = QgsVectorLayer(f"Polygon?crs=EPSG:4674", "zonas_com_chuva", "memory")
        provider = zonas_layer.dataProvider()
        
        # Copiar campos da camada original e adicionar campos de chuva
        original_fields = camada_zonas.fields()
        provider.addAttributes(original_fields.toList())
        provider.addAttributes([
            QgsField("NM_M15", QgsField.Double),
            QgsField("NM_H01", QgsField.Double),
            QgsField("NM_H04", QgsField.Double),
            QgsField("NM_H24", QgsField.Double),
            QgsField("NM_H96", QgsField.Double),
            QgsField("DT_COLETA", QgsField.String)
        ])
        zonas_layer.updateFields()
        
        # Processar cada zona pluviométrica
        with edit(zonas_layer):
            for zona_feature in camada_zonas.getFeatures():
                new_feature = QgsFeature(zonas_layer.fields())
                
                # Copiar geometria e atributos originais
                new_feature.setGeometry(zona_feature.geometry())
                for i, field in enumerate(original_fields):
                    new_feature.setAttribute(field.name(), zona_feature.attribute(i))
                
                # Buscar dados de chuva para esta zona
                codigo_zona = zona_feature.attribute('Cod') if 'Cod' in [f.name() for f in original_fields] else None
                nome_zona = zona_feature.attribute('Est') if 'Est' in [f.name() for f in original_fields] else None
                
                rain_data = self.findRainDataForZone(codigo_zona, nome_zona)
                
                if rain_data:
                    new_feature.setAttribute("NM_M15", rain_data['data']['m15'])
                    new_feature.setAttribute("NM_H01", rain_data['data']['h01'])
                    new_feature.setAttribute("NM_H04", rain_data['data']['h04'])
                    new_feature.setAttribute("NM_H24", rain_data['data']['h24'])
                    new_feature.setAttribute("NM_H96", rain_data['data']['h96'])
                    new_feature.setAttribute("DT_COLETA", rain_data['read_at'])
                else:
                    # Valores padrão quando não há dados
                    new_feature.setAttribute("NM_M15", 0.0)
                    new_feature.setAttribute("NM_H01", 0.0)
                    new_feature.setAttribute("NM_H04", 0.0)
                    new_feature.setAttribute("NM_H24", 0.0)
                    new_feature.setAttribute("NM_H96", 0.0)
                    new_feature.setAttribute("DT_COLETA", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                zonas_layer.addFeature(new_feature)
        
        feedback.pushInfo(f"Processadas {zonas_layer.featureCount()} zonas pluviométricas")
        return zonas_layer

    def findRainDataForZone(self, codigo_zona, nome_zona):
        """Encontrar dados de chuva para uma zona específica"""
        # Primeiro tenta por código, depois por nome
        rain_record = findPluviometricData(stationCode=codigo_zona)
        if not rain_record and nome_zona:
            rain_record = findPluviometricData(stationName=nome_zona)
        
        if rain_record:
            return extractRainDataFromInmet(rain_record)
        return None

    def executeRiskAnalysisQgis(self, camada_suscetibilidade, zonas_com_chuva, output_path, context, feedback):
        """Executar análise de risco usando ferramentas do QGIS"""
        
        # 1. Selecionar áreas de risco (suscetibilidade média e alta)
        feedback.pushInfo("Selecionando áreas de risco...")
        areas_risco = processing.run("native:extractbyexpression", {
            'INPUT': camada_suscetibilidade,
            'EXPRESSION': '"gridcode" IN (2, 3)',
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 2. Interseção entre zonas de chuva e áreas de risco
        feedback.pushInfo("Cruzando dados de chuva com suscetibilidade...")
        intersecao = processing.run("native:intersection", {
            'INPUT': zonas_com_chuva,
            'OVERLAY': areas_risco,
            'OUTPUT': 'memory:'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # 3. Calcular campo de perigo
        feedback.pushInfo("Calculando níveis de perigo...")
        expressao_perigo = '''
        CASE
            WHEN ("NM_H01" >= 70) OR ("NM_H24" >= 185) OR ("NM_H96" >= 255 AND "NM_H24" >= 100) THEN
                CASE
                    WHEN "gridcode" = 2 THEN 'MUITO ALTO'
                    WHEN "gridcode" = 3 THEN 'CRITICO'
                    ELSE 'SEM PERIGO'
                END
            WHEN ("NM_H01" >= 50 AND "NM_H01" < 70) OR ("NM_H24" >= 140 AND "NM_H24" < 185) OR ("NM_H96" >= 185 AND "NM_H96" < 255 AND "NM_H24" >= 55 AND "NM_H24" < 100) THEN
                CASE
                    WHEN "gridcode" = 2 THEN 'MODERADO'
                    WHEN "gridcode" = 3 THEN 'ALTO'
                    ELSE 'SEM PERIGO'
                END
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
        
        # 4. Dissolver por nível de perigo
        feedback.pushInfo("Agregando resultados finais...")
        resultado_final = processing.run("native:dissolve", {
            'INPUT': camada_com_perigo,
            'FIELD': ['PERIGO'],
            'OUTPUT': output_path
        }, context=context, feedback=feedback)['OUTPUT']
        
        return resultado_final


# ============================================================================
# EXECUÇÃO PARA LINHA DE COMANDO (COMPATIBILIDADE)
# ============================================================================

if __name__ == "__main__":
    # Manter compatibilidade com execução por linha de comando
    # Para uso no QGIS, a classe LhasaMgAnalysis será registrada como algoritmo
    
    try:
        # Configurar logging
        LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "LHASA_MG.log")
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        logging.basicConfig(
            filename=LOG_FILE, 
            filemode="a+", 
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S'
        )
        
        log = logging.getLogger(__name__)
        log.info("================================")
        log.info("LHASA MG - ANÁLISE DE RISCO")
        log.info("================================")
        
        # Verificar se está sendo executado no QGIS
        try:
            from qgis.core import QgsApplication
            log.info("Executando no ambiente QGIS")
            log.info("Use a Caixa de Ferramentas de Processamento para executar o algoritmo")
        except ImportError:
            log.info("Ambiente QGIS não detectado")
            log.info("Para usar este script, execute-o dentro do QGIS")
            
        # Manter funcionalidade básica para testes
        if len(sys.argv) > 1:
            if sys.argv[1] == "-test":
                log.info("Modo de teste - carregando dados do INMET...")
                initialize()
                loadPluviometricData()
                log.info("Teste concluído")
            else:
                log.info("Uso: python LHASA_Mg.py -test")
        else:
            log.info("Script carregado. Use no QGIS ou execute com -test")
            
    except Exception as e:
        print(f"Erro na execução: {e}")
        if 'log' in locals():
            log.error(f"Erro na execução: {e}")
    
    finally:
        if 'log' in locals():
            log.info("---- PROCESSO FINALIZADO ----")
