# GUIA DE GERAÇÃO DE MAPAS GEORREFERENCIADOS
## LHASA RIO - Sistema de Visualização Geoespacial

---

## 🎯 OBJETIVO

Gerar mapas interativos georreferenciados com:
- **26 estações meteorológicas** do INMET no Rio de Janeiro
- **Áreas de risco** de deslizamento 
- **Mapa de calor** da densidade de estações
- **Gráficos estatísticos** das estações

---

## 📋 PRÉ-REQUISITOS

### 1. Dependências Necessárias
```bash
# Instalar bibliotecas de mapeamento
pip install folium pandas matplotlib seaborn
```

### 2. Arquivos Necessários
- `gerar_mapa.py` - Script gerador de mapas
- `LHASA_RIO.py` - Código principal (opcional)

---

## 🚀 COMO GERAR O MAPA

### **OPÇÃO 1: Execução Independente**

```bash
# Gerar apenas o mapa
python gerar_mapa.py
```

**Saída esperada:**
```
🗺️ Gerando mapa georreferenciado LHASA RIO...
📡 Carregando estações meteorológicas do INMET...
✅ 26 estações carregadas do Rio de Janeiro
🗺️ Criando mapa base...
📍 Adicionando marcadores das estações...
⚠️ Adicionando áreas de risco...
🔥 Adicionando mapa de calor...
📋 Adicionando legenda...
✅ Mapa salvo como 'mapa_lhasa_rio_YYYYMMDD_HHMMSS.html'
📊 Gerando estatísticas...
✅ Gráfico de estatísticas salvo como 'estatisticas_estacoes.png'
```

### **OPÇÃO 2: Integrado com LHASA RIO**

```bash
# Executar análise completa + mapa
python LHASA_RIO.py -n
```

O mapa será gerado automaticamente como **etapa #11** do processamento.

---

## 📊 ARQUIVOS GERADOS

### 1. **Mapa Interativo HTML**
- **Nome**: `mapa_lhasa_rio_YYYYMMDD_HHMMSS.html`
- **Tamanho**: ~75KB
- **Funcionalidades**:
  - ✅ Zoom e navegação
  - ✅ Múltiplas camadas de mapa
  - ✅ Popups informativos
  - ✅ Controle de camadas
  - ✅ Legenda integrada

### 2. **Gráficos Estatísticos PNG**
- **Nome**: `estatisticas_estacoes.png`
- **Tamanho**: ~320KB
- **Conteúdo**:
  - 📊 Distribuição por tipo de estação
  - 📊 Status das estações
  - 📊 Distribuição de altitudes
  - 📊 Top 10 estações por altitude

---

## 🗺️ FUNCIONALIDADES DO MAPA

### **Camadas Disponíveis:**
1. **OpenStreetMap** (padrão)
2. **Terreno** (Stamen Terrain)
3. **Preto e Branco** (Stamen Toner)
4. **CartoDB** (CartoDB Positron)
5. **Mapa de Calor** (densidade de estações)

### **Marcadores das Estações:**
- 🔵 **Azul**: Estação Automática
- 🟢 **Verde**: Estação Convencional  
- 🟠 **Laranja**: Estação Pluviométrica

### **Áreas de Risco:**
- 🟢 **Verde**: Risco Baixo (raio 1km)
- 🟠 **Laranja**: Risco Médio (raio 1.5km)
- 🔴 **Vermelho**: Risco Alto (raio 2km)
- 🔴 **Vermelho Escuro**: Risco Crítico (raio 2.5km)

---

## 📍 ESTAÇÕES MONITORADAS

### **26 Estações INMET no Rio de Janeiro:**

| Código | Nome da Estação | Coordenadas |
|--------|-----------------|-------------|
| A628 | ANGRA DOS REIS | -22.976, -44.303 |
| A606 | ARRAIAL DO CABO | -22.975, -42.021 |
| A604 | CAMBUCI | -21.587, -41.958 |
| A607 | CAMPOS DOS GOYTACAZES | -21.715, -41.344 |
| A620 | CAMPOS - SAO TOME | -22.042, -41.052 |
| A629 | CARMO | -21.939, -42.601 |
| A603 | DUQUE DE CAXIAS | -22.590, -43.282 |
| A608 | MACAE | -22.376, -41.812 |
| A627 | NITEROI | -22.867, -43.102 |
| A624 | NOVA FRIBURGO | -22.335, -42.677 |
| A619 | PARATY | -23.224, -44.727 |
| A610 | PICO DO COUTO | -22.465, -43.291 |
| A637 | PATY DO ALFERES | -22.429, -43.425 |
| A609 | RESENDE | -22.464, -44.448 |
| A626 | RIO CLARO | -22.751, -44.128 |
| A652 | RIO DE JANEIRO - COPACABANA | -22.971, -43.182 |
| A636 | RIO DE JANEIRO - JACAREPAGUA | -22.956, -43.364 |
| A621 | RIO DE JANEIRO - VILA MILITAR | -22.836, -43.278 |
| A602 | RIO DE JANEIRO - MARAMBAIA | -23.049, -43.604 |
| A630 | SANTA MARIA MADALENA | -21.958, -42.012 |
| A667 | SAQUAREMA | -22.871, -42.609 |
| A601 | SEROPEDICA | -22.758, -43.685 |
| A659 | SILVA JARDIM | -22.646, -42.416 |
| A618 | TERESOPOLIS | -22.449, -42.987 |
| A625 | TRES RIOS | -22.098, -43.208 |
| A611 | VALENCA | -22.358, -43.696 |

---

## 🎨 ÁREAS DE RISCO MAPEADAS

### **17 Zonas Pluviométricas com Classificação de Risco:**

| Zona | Coordenadas | Nível de Risco |
|------|-------------|----------------|
| VIDIGAL | -22.994, -43.233 | 🔴 ALTO |
| ROCINHA | -22.989, -43.248 | 🔴 ALTO |
| SANTA TERESA | -22.913, -43.189 | 🔴 ALTO |
| LARANJEIRAS | -22.934, -43.188 | 🔴 ALTO |
| TIJUCA | -22.925, -43.231 | 🟠 MÉDIO |
| GRAJAU | -22.920, -43.265 | 🟠 MÉDIO |
| PENHA | -22.836, -43.278 | 🟠 MÉDIO |
| JARDIM BOTANICO | -22.966, -43.223 | 🟠 MÉDIO |
| JACAREPAGUA | -22.956, -43.364 | 🟠 MÉDIO |
| COPACABANA | -22.971, -43.182 | 🟢 BAIXO |
| MADUREIRA | -22.876, -43.336 | 🟢 BAIXO |
| BANGU | -22.880, -43.468 | 🟢 BAIXO |
| BARRA DA TIJUCA | -23.013, -43.318 | 🟢 BAIXO |
| GUARATIBA | -23.075, -43.593 | 🟢 BAIXO |
| SANTA CRUZ | -22.907, -43.679 | 🟢 BAIXO |
| CAMPO GRANDE | -22.899, -43.562 | 🟢 BAIXO |
| RECREIO | -23.026, -43.465 | 🟢 BAIXO |

---

## 🔧 COMO VISUALIZAR O MAPA

### **1. Abrir o Arquivo HTML**
```bash
# Abrir no navegador padrão (macOS)
open mapa_lhasa_rio_*.html

# Abrir no navegador padrão (Linux)
xdg-open mapa_lhasa_rio_*.html

# Abrir no navegador padrão (Windows)
start mapa_lhasa_rio_*.html
```

### **2. Navegação no Mapa**
- **Zoom**: Roda do mouse ou botões +/-
- **Navegação**: Arrastar com o mouse
- **Informações**: Clicar nos marcadores
- **Camadas**: Usar controle no canto superior direito
- **Legenda**: Canto superior direito (fixa)

### **3. Visualizar Gráficos**
```bash
# Abrir gráficos estatísticos
open estatisticas_estacoes.png
```

---

## 📱 COMPATIBILIDADE

### **Navegadores Suportados:**
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Opera

### **Dispositivos:**
- ✅ Desktop/Laptop
- ✅ Tablet
- ✅ Smartphone (responsivo)

---

## 🛠️ PERSONALIZAÇÃO

### **Modificar Áreas de Risco:**
Edite a função `adicionar_areas_risco()` em `gerar_mapa.py`:

```python
areas_risco = [
    {"nome": "NOVA_AREA", "coords": [-22.xxx, -43.xxx], "risco": "ALTO"},
    # Adicionar mais áreas...
]
```

### **Alterar Cores:**
Modifique os dicionários de cores:

```python
cores_risco = {
    "BAIXO": "green",
    "MÉDIO": "orange", 
    "ALTO": "red",
    "CRÍTICO": "darkred"
}
```

### **Adicionar Camadas:**
```python
folium.TileLayer('Nova_Camada', name='Nome').add_to(mapa)
```

---

## 🔍 SOLUÇÃO DE PROBLEMAS

### **Erro: "ModuleNotFoundError: folium"**
```bash
pip install folium pandas matplotlib seaborn
```

### **Mapa não carrega estações**
- Verificar conexão com internet
- API do INMET pode estar indisponível temporariamente

### **Arquivo HTML muito grande**
- Normal para mapas com muitos marcadores
- Arquivo otimizado (~75KB é aceitável)

### **Gráficos não aparecem**
- Verificar se matplotlib está instalado
- Arquivo PNG deve estar no mesmo diretório

---

## 📊 EXEMPLO DE SAÍDA

### **Estrutura de Arquivos Gerados:**
```
NASA/
├── mapa_lhasa_rio_20250923_144457.html    # Mapa interativo
├── estatisticas_estacoes.png              # Gráficos estatísticos
├── gerar_mapa.py                          # Script gerador
└── LHASA_RIO.py                          # Código principal
```

### **Informações no Popup das Estações:**
```
NITERÓI
─────────────────
Código: A627
Tipo: Automatica
Altitude: 6m
Coordenadas: -22.8675, -43.1019
Status: Operante
```

---

## 🌐 INTEGRAÇÃO WEB

### **Incorporar em Website:**
```html
<iframe src="mapa_lhasa_rio_YYYYMMDD_HHMMSS.html" 
        width="100%" height="600px" 
        frameborder="0">
</iframe>
```

### **Servir via HTTP:**
```bash
# Servidor Python simples
python -m http.server 8000
# Acessar: http://localhost:8000/mapa_lhasa_rio_*.html
```

---

## 📚 DOCUMENTAÇÃO TÉCNICA

### **APIs Utilizadas:**
- **INMET**: `https://apitempo.inmet.gov.br/estacoes/T`
- **Tiles**: OpenStreetMap, Stamen, CartoDB

### **Bibliotecas:**
- **Folium 0.20.0**: Mapas interativos
- **Pandas**: Manipulação de dados
- **Matplotlib/Seaborn**: Gráficos estatísticos

### **Formato de Coordenadas:**
- **Sistema**: WGS84 (EPSG:4326)
- **Formato**: Decimal (ex: -22.9068, -43.1729)

---

**Desenvolvido por:** Instituto Pereira Passos | NASA | Rio de Janeiro  
**Versão:** 2.1 com visualização geoespacial  
**Última atualização:** Setembro 2025
