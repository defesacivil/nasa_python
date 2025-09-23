# -*- coding: utf-8 -*-
"""
Gerador de Mapas com Gráfico de Bolhas - LHASA MG
Visualização avançada com bolhas proporcionais aos dados meteorológicos
"""

import folium
import pandas as pd
import json
import numpy as np
from datetime import datetime
import urllib3
from folium.plugins import HeatMap, MarkerCluster
import matplotlib.pyplot as plt
import seaborn as sns
from math import sqrt

# Configurações do mapa
MG_COORDS = [-18.5122, -44.5550]  # Centro de Minas Gerais
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

def processar_dados_para_bolhas(estacoes):
    """Processa dados das estações para criar métricas para as bolhas"""
    dados_processados = []
    
    for estacao in estacoes:
        try:
            # Dados básicos da estação
            codigo = estacao['CD_ESTACAO']
            nome = estacao['DC_NOME']
            lat = float(estacao['VL_LATITUDE'])
            lon = float(estacao['VL_LONGITUDE'])
            altitude = float(estacao.get('VL_ALTITUDE', '0'))
            tipo = estacao.get('TP_ESTACAO', 'Automatica')
            
            # Calcular métricas para as bolhas
            # Métrica 1: Altitude (normalizada)
            altitude_normalizada = min(altitude / 10, 100)  # Máximo 100 para visualização
            
            # Métrica 2: Importância regional (baseada na altitude e tipo)
            importancia = 10
            if altitude > 1000:
                importancia += 20  # Estações em altitude têm mais importância
            if 'BELO HORIZONTE' in nome.upper():
                importancia += 30  # Capital tem mais importância
            if tipo == 'Automatica':
                importancia += 15  # Estações automáticas são mais modernas
                
            # Métrica 3: Índice de risco (baseado na localização)
            risco_index = calcular_indice_risco(nome, lat, lon)
            
            # Métrica 4: Densidade populacional estimada (baseada na cidade)
            densidade_pop = estimar_densidade_populacional(nome)
            
            dados_processados.append({
                'codigo': codigo,
                'nome': nome,
                'lat': lat,
                'lon': lon,
                'altitude': altitude,
                'altitude_normalizada': altitude_normalizada,
                'tipo': tipo,
                'importancia': importancia,
                'risco_index': risco_index,
                'densidade_pop': densidade_pop,
                'tamanho_bolha': importancia,  # Métrica principal para tamanho da bolha
                'cor_bolha': risco_index,      # Métrica para cor da bolha
            })
            
        except (ValueError, KeyError) as e:
            print(f"Erro ao processar estação {estacao.get('CD_ESTACAO', 'N/A')}: {e}")
            continue
    
    return dados_processados

def calcular_indice_risco(nome, lat, lon):
    """Calcula índice de risco baseado na localização"""
    # Áreas de alto risco em MG (baseado em histórico de deslizamentos)
    areas_alto_risco = [
        ('BELO HORIZONTE', -19.9167, -43.9345),
        ('NOVA LIMA', -19.9858, -43.8465),
        ('OURO PRETO', -20.3856, -43.5033),
        ('MARIANA', -20.3778, -43.4175),
        ('SABARÁ', -19.8833, -43.8014),
    ]
    
    risco = 20  # Risco base
    
    # Verificar proximidade com áreas de alto risco
    for area_nome, area_lat, area_lon in areas_alto_risco:
        if area_nome in nome.upper():
            risco += 40
            break
        
        # Calcular distância aproximada
        dist = sqrt((lat - area_lat)**2 + (lon - area_lon)**2)
        if dist < 0.5:  # Dentro de ~50km
            risco += 30
        elif dist < 1.0:  # Dentro de ~100km
            risco += 15
    
    # Fator altitude (maior altitude = maior risco de deslizamento)
    if 'ALTITUDE' in nome.upper() or any(palavra in nome.upper() for palavra in ['SERRA', 'MONTE', 'PICO']):
        risco += 25
    
    return min(risco, 100)  # Máximo 100

def estimar_densidade_populacional(nome):
    """Estima densidade populacional baseada no nome da cidade"""
    cidades_grandes = {
        'BELO HORIZONTE': 90,
        'CONTAGEM': 70,
        'UBERLÂNDIA': 60,
        'JUIZ DE FORA': 55,
        'BETIM': 50,
        'MONTES CLAROS': 45,
        'RIBEIRÃO DAS NEVES': 40,
        'UBERABA': 35,
        'GOVERNADOR VALADARES': 30,
        'IPATINGA': 30,
    }
    
    for cidade, densidade in cidades_grandes.items():
        if cidade in nome.upper():
            return densidade
    
    return 15  # Densidade base para cidades menores

def criar_mapa_bolhas():
    """Cria mapa base para visualização com bolhas"""
    mapa = folium.Map(
        location=MG_COORDS,
        zoom_start=7,
        tiles='OpenStreetMap',
        control_scale=True
    )
    
    # Adicionar camadas diferentes
    folium.TileLayer('CartoDB positron', name='Claro').add_to(mapa)
    folium.TileLayer('Stamen Terrain', name='Terreno').add_to(mapa)
    folium.TileLayer('Stamen Toner', name='Escuro').add_to(mapa)
    
    return mapa

def adicionar_bolhas_ao_mapa(mapa, dados_estacoes):
    """Adiciona bolhas proporcionais ao mapa"""
    
    # Normalizar tamanhos das bolhas (10 a 50 pixels)
    tamanhos = [d['tamanho_bolha'] for d in dados_estacoes]
    tamanho_min, tamanho_max = min(tamanhos), max(tamanhos)
    
    # Normalizar cores (0 a 100 para risco)
    riscos = [d['risco_index'] for d in dados_estacoes]
    
    for dados in dados_estacoes:
        # Calcular tamanho da bolha (10 a 50 pixels)
        tamanho_normalizado = 10 + (dados['tamanho_bolha'] - tamanho_min) / (tamanho_max - tamanho_min) * 40
        
        # Calcular cor baseada no risco
        if dados['risco_index'] >= 70:
            cor = 'red'
            cor_fill = '#ff4444'
        elif dados['risco_index'] >= 50:
            cor = 'orange'
            cor_fill = '#ff8800'
        elif dados['risco_index'] >= 30:
            cor = 'yellow'
            cor_fill = '#ffdd00'
        else:
            cor = 'green'
            cor_fill = '#44ff44'
        
        # Criar popup com informações detalhadas
        popup_html = f"""
        <div style="width: 300px; font-family: Arial;">
            <h4><b>{dados['nome']}</b></h4>
            <hr>
            <table style="width:100%; font-size:12px;">
                <tr><td><b>Código:</b></td><td>{dados['codigo']}</td></tr>
                <tr><td><b>Tipo:</b></td><td>{dados['tipo']}</td></tr>
                <tr><td><b>Altitude:</b></td><td>{dados['altitude']:.0f}m</td></tr>
                <tr><td><b>Coordenadas:</b></td><td>{dados['lat']:.3f}, {dados['lon']:.3f}</td></tr>
                <tr><td><b>Índice de Risco:</b></td><td>{dados['risco_index']:.0f}/100</td></tr>
                <tr><td><b>Importância:</b></td><td>{dados['importancia']:.0f}/100</td></tr>
                <tr><td><b>Densidade Pop.:</b></td><td>{dados['densidade_pop']:.0f}/100</td></tr>
            </table>
            <hr>
            <p style="font-size:11px; color:#666;">
                <b>Tamanho da bolha:</b> Importância regional<br>
                <b>Cor da bolha:</b> Índice de risco de deslizamento
            </p>
        </div>
        """
        
        # Adicionar círculo (bolha) ao mapa
        folium.Circle(
            location=[dados['lat'], dados['lon']],
            radius=tamanho_normalizado * 500,  # Converter para metros
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{dados['codigo']}: {dados['nome']} (Risco: {dados['risco_index']:.0f})",
            color=cor,
            fillColor=cor_fill,
            fillOpacity=0.6,
            weight=2,
            opacity=0.8
        ).add_to(mapa)

def adicionar_legenda_bolhas(mapa):
    """Adiciona legenda específica para o mapa de bolhas"""
    
    legenda_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 280px; height: 320px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:12px; padding: 15px; border-radius: 5px;">
    
    <h4 style="margin-top:0; color:#333;"><b>LHASA MG - Mapa de Bolhas</b></h4>
    
    <div style="margin-bottom: 15px;">
        <h5 style="margin-bottom: 5px; color:#555;">Tamanho das Bolhas:</h5>
        <p style="margin: 2px 0;"><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#ccc; margin-right:5px;"></span> Pequena: Baixa importância</p>
        <p style="margin: 2px 0;"><span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#ccc; margin-right:5px;"></span> Média: Importância moderada</p>
        <p style="margin: 2px 0;"><span style="display:inline-block; width:16px; height:16px; border-radius:50%; background:#ccc; margin-right:5px;"></span> Grande: Alta importância</p>
    </div>
    
    <div style="margin-bottom: 15px;">
        <h5 style="margin-bottom: 5px; color:#555;">Cores (Índice de Risco):</h5>
        <p style="margin: 2px 0;"><span style="color:green;">●</span> Verde: Risco Baixo (0-30)</p>
        <p style="margin: 2px 0;"><span style="color:#ffdd00;">●</span> Amarelo: Risco Moderado (30-50)</p>
        <p style="margin: 2px 0;"><span style="color:orange;">●</span> Laranja: Risco Alto (50-70)</p>
        <p style="margin: 2px 0;"><span style="color:red;">●</span> Vermelho: Risco Crítico (70-100)</p>
    </div>
    
    <div style="border-top: 1px solid #ccc; padding-top: 10px;">
        <p style="font-size:10px; color:#666; margin:0;">
            <b>Importância:</b> Altitude + Tipo + Localização<br>
            <b>Risco:</b> Proximidade áreas de deslizamento
        </p>
    </div>
    
    </div>
    '''
    
    mapa.get_root().html.add_child(folium.Element(legenda_html))

def gerar_grafico_dispersao_bolhas(dados_estacoes):
    """Gera gráfico de dispersão complementar"""
    
    df = pd.DataFrame(dados_estacoes)
    
    # Configurar o gráfico
    plt.style.use('seaborn-v0_8')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('LHASA MG - Análise de Bolhas das Estações Meteorológicas', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Dispersão Altitude vs Risco (com bolhas)
    scatter1 = ax1.scatter(df['altitude'], df['risco_index'], 
                          s=df['importancia']*3, c=df['densidade_pop'], 
                          alpha=0.6, cmap='viridis', edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Altitude (m)')
    ax1.set_ylabel('Índice de Risco')
    ax1.set_title('Altitude vs Risco (tamanho = importância, cor = densidade pop.)')
    plt.colorbar(scatter1, ax=ax1, label='Densidade Populacional')
    
    # Gráfico 2: Distribuição de Importância por Tipo
    tipos = df['tipo'].unique()
    cores = ['skyblue', 'lightcoral', 'lightgreen']
    for i, tipo in enumerate(tipos):
        dados_tipo = df[df['tipo'] == tipo]
        ax2.scatter(dados_tipo.index, dados_tipo['importancia'], 
                   s=dados_tipo['risco_index']*2, c=cores[i % len(cores)], 
                   alpha=0.7, label=tipo, edgecolors='black', linewidth=0.5)
    ax2.set_xlabel('Índice da Estação')
    ax2.set_ylabel('Importância')
    ax2.set_title('Importância por Tipo (tamanho = risco)')
    ax2.legend()
    
    # Gráfico 3: Mapa de calor da correlação
    correlation_data = df[['altitude', 'importancia', 'risco_index', 'densidade_pop']].corr()
    sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0, ax=ax3)
    ax3.set_title('Correlação entre Métricas')
    
    # Gráfico 4: Top 15 estações por importância
    top_estacoes = df.nlargest(15, 'importancia')
    bars = ax4.barh(range(len(top_estacoes)), top_estacoes['importancia'], 
                    color=plt.cm.RdYlGn_r(top_estacoes['risco_index']/100))
    ax4.set_yticks(range(len(top_estacoes)))
    ax4.set_yticklabels([nome[:25] + '...' if len(nome) > 25 else nome 
                        for nome in top_estacoes['nome']], fontsize=9)
    ax4.set_xlabel('Importância')
    ax4.set_title('Top 15 Estações por Importância (cor = risco)')
    
    # Adicionar colorbar para o gráfico 4
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn_r, norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax4)
    cbar.set_label('Índice de Risco')
    
    plt.tight_layout()
    plt.savefig('grafico_bolhas_estacoes.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfico de bolhas salvo como 'grafico_bolhas_estacoes.png'")

def gerar_relatorio_estatistico(dados_estacoes):
    """Gera relatório estatístico das bolhas"""
    
    df = pd.DataFrame(dados_estacoes)
    
    print("\n📊 RELATÓRIO ESTATÍSTICO DAS BOLHAS")
    print("=" * 50)
    
    print(f"\n🎯 RESUMO GERAL:")
    print(f"   • Total de estações: {len(df)}")
    print(f"   • Altitude média: {df['altitude'].mean():.1f}m")
    print(f"   • Risco médio: {df['risco_index'].mean():.1f}/100")
    print(f"   • Importância média: {df['importancia'].mean():.1f}/100")
    
    print(f"\n🔴 ESTAÇÕES DE ALTO RISCO (≥70):")
    alto_risco = df[df['risco_index'] >= 70].sort_values('risco_index', ascending=False)
    for _, estacao in alto_risco.head(5).iterrows():
        print(f"   • {estacao['nome']}: {estacao['risco_index']:.0f}/100")
    
    print(f"\n⭐ ESTAÇÕES MAIS IMPORTANTES:")
    mais_importantes = df.nlargest(5, 'importancia')
    for _, estacao in mais_importantes.iterrows():
        print(f"   • {estacao['nome']}: {estacao['importancia']:.0f}/100")
    
    print(f"\n🏔️ ESTAÇÕES EM MAIOR ALTITUDE:")
    maior_altitude = df.nlargest(5, 'altitude')
    for _, estacao in maior_altitude.iterrows():
        print(f"   • {estacao['nome']}: {estacao['altitude']:.0f}m")
    
    print(f"\n📈 DISTRIBUIÇÃO POR RISCO:")
    print(f"   • Baixo (0-30): {len(df[df['risco_index'] < 30])} estações")
    print(f"   • Moderado (30-50): {len(df[(df['risco_index'] >= 30) & (df['risco_index'] < 50)])} estações")
    print(f"   • Alto (50-70): {len(df[(df['risco_index'] >= 50) & (df['risco_index'] < 70)])} estações")
    print(f"   • Crítico (≥70): {len(df[df['risco_index'] >= 70])} estações")

def gerar_mapa_bolhas_completo():
    """Função principal para gerar mapa com bolhas"""
    
    print("🔵 Gerando mapa de bolhas LHASA MG...")
    
    # Obter dados das estações
    print("📡 Carregando estações meteorológicas...")
    estacoes = obter_estacoes_inmet()
    
    if not estacoes:
        print("❌ Não foi possível carregar as estações")
        return
    
    print(f"✅ {len(estacoes)} estações carregadas")
    
    # Processar dados para bolhas
    print("⚙️ Processando dados para visualização em bolhas...")
    dados_bolhas = processar_dados_para_bolhas(estacoes)
    
    print(f"✅ {len(dados_bolhas)} estações processadas com métricas")
    
    # Criar mapa
    print("🗺️ Criando mapa base...")
    mapa = criar_mapa_bolhas()
    
    # Adicionar bolhas
    print("🔵 Adicionando bolhas proporcionais...")
    adicionar_bolhas_ao_mapa(mapa, dados_bolhas)
    
    # Adicionar legenda
    print("📋 Adicionando legenda...")
    adicionar_legenda_bolhas(mapa)
    
    # Adicionar controle de camadas
    folium.LayerControl().add_to(mapa)
    
    # Salvar mapa
    nome_arquivo = f"mapa_bolhas_mg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    mapa.save(nome_arquivo)
    print(f"✅ Mapa de bolhas salvo como '{nome_arquivo}'")
    
    # Gerar gráficos complementares
    print("📊 Gerando gráficos de análise...")
    gerar_grafico_dispersao_bolhas(dados_bolhas)
    
    # Gerar relatório
    gerar_relatorio_estatistico(dados_bolhas)
    
    print(f"\n🎉 Mapa de bolhas gerado com sucesso!")
    print(f"📁 Arquivos gerados:")
    print(f"   - {nome_arquivo} (mapa interativo de bolhas)")
    print(f"   - grafico_bolhas_estacoes.png (análises gráficas)")
    
    return nome_arquivo

if __name__ == "__main__":
    gerar_mapa_bolhas_completo()

