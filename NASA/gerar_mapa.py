# -*- coding: utf-8 -*-
"""
Gerador de Mapas Georreferenciados - LHASA RIO
Sistema de visualização das estações meteorológicas e áreas de risco
"""

import folium
import pandas as pd
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from folium.plugins import HeatMap, MarkerCluster
import urllib3

# Configurações do mapa
MG_COORDS = [-18.5122, -44.5550]  # Coordenadas do centro de Minas Gerais (Belo Horizonte)
INMET_STATIONS_URL = "https://apitempo.inmet.gov.br/estacoes/T"

def obter_estacoes_inmet():
    """Obtém lista de estações meteorológicas do INMET para MG"""
    try:
        http = urllib3.PoolManager()
        response = http.request("GET", INMET_STATIONS_URL)
        stations_data = json.loads(response.data)
        
        # Filtrar apenas estações de Minas Gerais operantes
        mg_stations = [station for station in stations_data 
                      if station['SG_ESTADO'] == 'MG' and station['CD_SITUACAO'] == 'Operante']
        
        return mg_stations
    except Exception as e:
        print(f"Erro ao obter estações INMET: {e}")
        return []

def criar_mapa_base():
    """Cria o mapa base de Minas Gerais"""
    mapa = folium.Map(
        location=MG_COORDS,
        zoom_start=7,  # Zoom menor para cobrir todo o estado
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Adicionar diferentes camadas de mapa
    folium.TileLayer('Stamen Terrain', name='Terreno').add_to(mapa)
    folium.TileLayer('Stamen Toner', name='Preto e Branco').add_to(mapa)
    folium.TileLayer('CartoDB positron', name='CartoDB').add_to(mapa)
    
    return mapa

def adicionar_estacoes_meteorologicas(mapa, estacoes):
    """Adiciona marcadores das estações meteorológicas no mapa"""
    
    # Criar cluster de marcadores para melhor visualização
    marker_cluster = MarkerCluster(name="Estações INMET").add_to(mapa)
    
    cores_estacao = {
        'Automatica': 'blue',
        'Convencional': 'green',
        'Pluviometrica': 'orange'
    }
    
    for estacao in estacoes:
        try:
            lat = float(estacao['VL_LATITUDE'])
            lon = float(estacao['VL_LONGITUDE'])
            nome = estacao['DC_NOME']
            codigo = estacao['CD_ESTACAO']
            tipo = estacao.get('TP_ESTACAO', 'Automatica')
            altitude = estacao.get('VL_ALTITUDE', 'N/A')
            
            # Cor baseada no tipo de estação
            cor = cores_estacao.get(tipo, 'red')
            
            # Popup com informações da estação
            popup_html = f"""
            <div style="width: 250px;">
                <h4><b>{nome}</b></h4>
                <hr>
                <p><b>Código:</b> {codigo}</p>
                <p><b>Tipo:</b> {tipo}</p>
                <p><b>Altitude:</b> {altitude}m</p>
                <p><b>Coordenadas:</b> {lat:.4f}, {lon:.4f}</p>
                <p><b>Status:</b> {estacao['CD_SITUACAO']}</p>
            </div>
            """
            
            # Adicionar marcador
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{codigo}: {nome}",
                icon=folium.Icon(color=cor, icon='cloud', prefix='fa')
            ).add_to(marker_cluster)
            
        except (ValueError, KeyError) as e:
            print(f"Erro ao processar estação {estacao.get('CD_ESTACAO', 'N/A')}: {e}")
            continue

def adicionar_areas_risco(mapa):
    """Adiciona áreas de risco conhecidas de Minas Gerais"""
    
    # Áreas de risco baseadas em regiões importantes de MG
    areas_risco = [
        {"nome": "BELO HORIZONTE", "coords": [-19.9167, -43.9345], "risco": "ALTO"},
        {"nome": "NOVA LIMA", "coords": [-19.9858, -43.8465], "risco": "ALTO"},
        {"nome": "OURO PRETO", "coords": [-20.3856, -43.5033], "risco": "ALTO"},
        {"nome": "MARIANA", "coords": [-20.3778, -43.4175], "risco": "ALTO"},
        {"nome": "SABARÁ", "coords": [-19.8833, -43.8014], "risco": "MÉDIO"},
        {"nome": "ITABIRA", "coords": [-19.6194, -43.2269], "risco": "MÉDIO"},
        {"nome": "CONSELHEIRO LAFAIETE", "coords": [-20.6597, -43.7858], "risco": "MÉDIO"},
        {"nome": "BARBACENA", "coords": [-21.2258, -43.7736], "risco": "MÉDIO"},
        {"nome": "JUIZ DE FORA", "coords": [-21.7642, -43.3467], "risco": "MÉDIO"},
        {"nome": "UBERLÂNDIA", "coords": [-18.9186, -48.2772], "risco": "BAIXO"},
        {"nome": "CONTAGEM", "coords": [-19.9317, -44.0536], "risco": "MÉDIO"},
        {"nome": "BETIM", "coords": [-19.9678, -44.1978], "risco": "BAIXO"},
        {"nome": "MONTES CLAROS", "coords": [-16.7289, -43.8611], "risco": "BAIXO"},
        {"nome": "RIBEIRÃO DAS NEVES", "coords": [-19.7667, -44.0867], "risco": "BAIXO"},
        {"nome": "UBERABA", "coords": [-19.7475, -47.9319], "risco": "BAIXO"},
        {"nome": "GOVERNADOR VALADARES", "coords": [-18.8508, -41.9494], "risco": "MÉDIO"},
        {"nome": "IPATINGA", "coords": [-19.4681, -42.5364], "risco": "MÉDIO"},
        {"nome": "TEÓFILO OTONI", "coords": [-17.8631, -41.5056], "risco": "BAIXO"},
    ]
    
    cores_risco = {
        "BAIXO": "green",
        "MÉDIO": "orange", 
        "ALTO": "red",
        "CRÍTICO": "darkred"
    }
    
    # Adicionar círculos para áreas de risco
    for area in areas_risco:
        cor = cores_risco.get(area["risco"], "blue")
        raio = {"BAIXO": 1000, "MÉDIO": 1500, "ALTO": 2000, "CRÍTICO": 2500}[area["risco"]]
        
        folium.Circle(
            location=area["coords"],
            radius=raio,
            popup=f"<b>{area['nome']}</b><br>Risco: {area['risco']}",
            tooltip=f"{area['nome']} - Risco {area['risco']}",
            color=cor,
            fillColor=cor,
            fillOpacity=0.3,
            weight=2
        ).add_to(mapa)

def adicionar_mapa_calor(mapa, estacoes):
    """Adiciona mapa de calor baseado na densidade de estações"""
    
    # Preparar dados para o mapa de calor
    heat_data = []
    for estacao in estacoes:
        try:
            lat = float(estacao['VL_LATITUDE'])
            lon = float(estacao['VL_LONGITUDE'])
            # Usar altitude como peso (estações em maior altitude têm mais "calor")
            peso = float(estacao.get('VL_ALTITUDE', '100')) / 100
            heat_data.append([lat, lon, peso])
        except (ValueError, KeyError):
            continue
    
    if heat_data:
        HeatMap(
            heat_data,
            name="Densidade de Estações",
            radius=20,
            blur=15,
            max_zoom=1,
        ).add_to(mapa)

def adicionar_legenda(mapa):
    """Adiciona legenda ao mapa"""
    
    legenda_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: 200px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>LHASA MG - Legenda</h4>
    <p><i class="fa fa-cloud" style="color:blue"></i> Estação Automática</p>
    <p><i class="fa fa-cloud" style="color:green"></i> Estação Convencional</p>
    <p><i class="fa fa-cloud" style="color:orange"></i> Estação Pluviométrica</p>
    <hr>
    <p><span style="color:green">●</span> Risco Baixo</p>
    <p><span style="color:orange">●</span> Risco Médio</p>
    <p><span style="color:red">●</span> Risco Alto</p>
    <p><span style="color:darkred">●</span> Risco Crítico</p>
    </div>
    '''
    
    mapa.get_root().html.add_child(folium.Element(legenda_html))

def gerar_estatisticas(estacoes):
    """Gera gráficos estatísticos das estações"""
    
    if not estacoes:
        print("Nenhuma estação encontrada para gerar estatísticas")
        return
    
    # Criar DataFrame
    df = pd.DataFrame(estacoes)
    
    # Configurar estilo dos gráficos
    plt.style.use('seaborn-v0_8')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('LHASA MG - Estatísticas das Estações INMET', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Distribuição por tipo de estação
    tipo_counts = df['TP_ESTACAO'].value_counts()
    ax1.pie(tipo_counts.values, labels=tipo_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Distribuição por Tipo de Estação')
    
    # Gráfico 2: Distribuição por situação
    situacao_counts = df['CD_SITUACAO'].value_counts()
    ax2.bar(situacao_counts.index, situacao_counts.values, color=['green', 'red', 'orange'])
    ax2.set_title('Status das Estações')
    ax2.set_xlabel('Situação')
    ax2.set_ylabel('Quantidade')
    
    # Gráfico 3: Distribuição de altitudes
    altitudes = pd.to_numeric(df['VL_ALTITUDE'], errors='coerce').dropna()
    ax3.hist(altitudes, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
    ax3.set_title('Distribuição de Altitudes')
    ax3.set_xlabel('Altitude (m)')
    ax3.set_ylabel('Frequência')
    
    # Gráfico 4: Top 10 estações por altitude
    df_alt = df.copy()
    df_alt['VL_ALTITUDE'] = pd.to_numeric(df_alt['VL_ALTITUDE'], errors='coerce')
    top_alt = df_alt.nlargest(10, 'VL_ALTITUDE')[['DC_NOME', 'VL_ALTITUDE']]
    ax4.barh(range(len(top_alt)), top_alt['VL_ALTITUDE'], color='lightcoral')
    ax4.set_yticks(range(len(top_alt)))
    ax4.set_yticklabels([nome[:20] + '...' if len(nome) > 20 else nome for nome in top_alt['DC_NOME']])
    ax4.set_title('Top 10 Estações por Altitude')
    ax4.set_xlabel('Altitude (m)')
    
    plt.tight_layout()
    plt.savefig('estatisticas_estacoes.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfico de estatísticas salvo como 'estatisticas_estacoes.png'")

def gerar_mapa_completo():
    """Função principal para gerar o mapa completo"""
    
    print("🗺️  Gerando mapa georreferenciado LHASA MG...")
    
    # Obter estações do INMET
    print("📡 Carregando estações meteorológicas do INMET...")
    estacoes = obter_estacoes_inmet()
    
    if not estacoes:
        print("❌ Não foi possível carregar as estações do INMET")
        return
    
    print(f"✅ {len(estacoes)} estações carregadas de Minas Gerais")
    
    # Criar mapa base
    print("🗺️  Criando mapa base...")
    mapa = criar_mapa_base()
    
    # Adicionar estações meteorológicas
    print("📍 Adicionando marcadores das estações...")
    adicionar_estacoes_meteorologicas(mapa, estacoes)
    
    # Adicionar áreas de risco
    print("⚠️  Adicionando áreas de risco...")
    adicionar_areas_risco(mapa)
    
    # Adicionar mapa de calor
    print("🔥 Adicionando mapa de calor...")
    adicionar_mapa_calor(mapa, estacoes)
    
    # Adicionar legenda
    print("📋 Adicionando legenda...")
    adicionar_legenda(mapa)
    
    # Adicionar controle de camadas
    folium.LayerControl().add_to(mapa)
    
    # Salvar mapa
    nome_arquivo = f"mapa_lhasa_mg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    mapa.save(nome_arquivo)
    print(f"✅ Mapa salvo como '{nome_arquivo}'")
    
    # Gerar estatísticas
    print("📊 Gerando estatísticas...")
    gerar_estatisticas(estacoes)
    
    print("\n🎉 Mapa georreferenciado gerado com sucesso!")
    print(f"📁 Arquivos gerados:")
    print(f"   - {nome_arquivo} (mapa interativo)")
    print(f"   - estatisticas_estacoes.png (gráficos)")
    
    return nome_arquivo

if __name__ == "__main__":
    gerar_mapa_completo()
