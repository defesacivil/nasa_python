# GUIA DE MAPAS COM GRÁFICOS DE BOLHAS
## LHASA MG - Visualização Avançada com Bolhas Proporcionais

---

## 🎯 CONCEITO DE MAPAS DE BOLHAS

Os **mapas de bolhas** são uma técnica de visualização que representa dados quantitativos através de **círculos (bolhas)** de tamanhos e cores variáveis plotados em coordenadas geográficas.

### **Vantagens dos Mapas de Bolhas:**
- ✅ **Múltiplas dimensões** de dados em uma visualização
- ✅ **Comparação visual** imediata entre estações
- ✅ **Identificação de padrões** geoespaciais
- ✅ **Análise de correlações** entre variáveis

---

## 🔵 COMO FUNCIONA O SISTEMA

### **Métricas Calculadas para Cada Estação:**

#### **1. Tamanho da Bolha = Importância Regional**
```python
importancia = 10  # Base
+ 20 (se altitude > 1000m)
+ 30 (se é capital - Belo Horizonte)
+ 15 (se é estação automática)
```

#### **2. Cor da Bolha = Índice de Risco**
```python
risco = 20  # Base
+ 40 (se em área de alto risco histórico)
+ 30 (se próximo < 50km de área crítica)
+ 25 (se tem palavras: serra, monte, pico)
```

#### **3. Métricas Complementares:**
- **Altitude**: Elevação da estação (0-1545m)
- **Densidade Populacional**: Estimativa baseada na cidade
- **Tipo de Estação**: Automática, Convencional, Pluviométrica

---

## 🚀 COMO GERAR MAPAS DE BOLHAS

### **OPÇÃO 1: Integrado com LHASA**
```bash
# Gera mapa básico + mapa de bolhas automaticamente
python LHASA_RIO.py -n
```

**Saída esperada:**
```
#11 | GERANDO MAPA GEORREFERENCIADO
      Mapa básico gerado: mapa_lhasa_mg_YYYYMMDD_HHMMSS.html
#12 | GERANDO MAPA DE BOLHAS
      Mapa de bolhas gerado: mapa_bolhas_mg_YYYYMMDD_HHMMSS.html
```

### **OPÇÃO 2: Apenas Mapa de Bolhas**
```bash
# Gera apenas o mapa de bolhas
python mapa_bolhas.py
```

---

## 📊 ARQUIVOS GERADOS

### **1. Mapa Interativo HTML**
- **Nome**: `mapa_bolhas_mg_YYYYMMDD_HHMMSS.html`
- **Tamanho**: ~140KB
- **Características**:
  - 🔵 **62 bolhas** representando estações de MG
  - 🎨 **4 cores** de risco (verde, amarelo, laranja, vermelho)
  - 📏 **Tamanhos variáveis** (10-50 pixels de raio)
  - 📋 **Popups informativos** com todas as métricas
  - 🗺️ **4 camadas de mapa** diferentes

### **2. Gráficos de Análise PNG**
- **Nome**: `grafico_bolhas_estacoes.png`
- **Tamanho**: ~400KB
- **Conteúdo**:
  - **Dispersão Altitude vs Risco** (com bolhas)
  - **Importância por Tipo** de estação
  - **Mapa de calor** de correlações
  - **Top 15 estações** por importância

---

## 🎨 INTERPRETAÇÃO VISUAL

### **Tamanho das Bolhas (Importância):**
- 🔵 **Pequena** (10-20px): Estações de baixa importância regional
- 🔵 **Média** (20-35px): Estações de importância moderada  
- 🔵 **Grande** (35-50px): Estações de alta importância regional

### **Cores das Bolhas (Risco):**
- 🟢 **Verde** (0-30): Risco Baixo de deslizamento
- 🟡 **Amarelo** (30-50): Risco Moderado
- 🟠 **Laranja** (50-70): Risco Alto
- 🔴 **Vermelho** (70-100): Risco Crítico

---

## 📈 ANÁLISE DOS RESULTADOS

### **Estatísticas Atuais (62 Estações MG):**

#### **🎯 Resumo Geral:**
- **Altitude média**: 758.1m
- **Risco médio**: 28.6/100
- **Importância média**: 29.7/100

#### **🔴 Estações de Alto Risco (≥70):**
1. **IBIRITE (ROLA MOCA)**: 100/100 - *1199m altitude*
2. **OURO BRANCO**: 100/100 - *1048m altitude*
3. **FLORESTAL**: 80/100 - *778m altitude*

#### **⭐ Estações Mais Importantes:**
1. **BELO HORIZONTE - CERCADINHO**: 75/100
2. **BELO HORIZONTE - PAMPULHA**: 55/100
3. **BELO HORIZONTE - SANTO AGOSTINHO**: 55/100
4. **ARAXÁ**: 45/100
5. **BARBACENA**: 45/100

#### **🏔️ Maiores Altitudes:**
1. **MONTE VERDE**: 1545m
2. **DIAMANTINA**: 1359m
3. **MARIA DA FÉ**: 1281m
4. **BELO HORIZONTE - CERCADINHO**: 1200m
5. **IBIRITE (ROLA MOCA)**: 1199m

#### **📊 Distribuição por Risco:**
- **Baixo** (0-30): 49 estações (79%)
- **Moderado** (30-50): 4 estações (6%)
- **Alto** (50-70): 6 estações (10%)
- **Crítico** (≥70): 3 estações (5%)

---

## 🔍 FUNCIONALIDADES INTERATIVAS

### **No Mapa HTML:**
1. **Zoom e Navegação**: Mouse/teclado
2. **Informações Detalhadas**: Clicar nas bolhas
3. **Tooltip Rápido**: Passar mouse sobre bolhas
4. **Controle de Camadas**: Canto superior direito
5. **Legenda Fixa**: Sempre visível

### **Popup das Estações Inclui:**
- Código e nome da estação
- Tipo e coordenadas
- Altitude e métricas calculadas
- Índices de risco, importância e densidade
- Explicação das cores e tamanhos

---

## 📱 VISUALIZAÇÃO RESPONSIVA

### **Dispositivos Suportados:**
- 💻 **Desktop**: Experiência completa
- 📱 **Tablet**: Interface adaptada
- 📱 **Smartphone**: Versão otimizada

### **Navegadores Compatíveis:**
- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅

---

## 🛠️ PERSONALIZAÇÃO AVANÇADA

### **Modificar Critérios de Importância:**
```python
# Editar função processar_dados_para_bolhas()
importancia = 10
if altitude > 1000:
    importancia += 20  # Ajustar peso da altitude
if 'BELO HORIZONTE' in nome.upper():
    importancia += 30  # Ajustar peso da capital
```

### **Alterar Cores de Risco:**
```python
# Editar função adicionar_bolhas_ao_mapa()
if dados['risco_index'] >= 70:
    cor = 'red'           # Personalizar cor crítica
elif dados['risco_index'] >= 50:
    cor = 'orange'        # Personalizar cor alta
```

### **Ajustar Tamanhos das Bolhas:**
```python
# Modificar escala de tamanhos (10 a 50 pixels)
tamanho_normalizado = 15 + (dados['tamanho_bolha'] - tamanho_min) / (tamanho_max - tamanho_min) * 60
```

---

## 📊 COMPARAÇÃO: MAPA BÁSICO vs BOLHAS

| Aspecto | Mapa Básico | Mapa de Bolhas |
|---------|-------------|----------------|
| **Visualização** | Marcadores fixos | Bolhas proporcionais |
| **Informação** | Localização | Múltiplas dimensões |
| **Análise** | Qualitativa | Quantitativa |
| **Comparação** | Difícil | Visual imediata |
| **Padrões** | Limitados | Correlações visíveis |
| **Uso** | Localização | Análise de dados |

---

## 🎯 CASOS DE USO ESPECÍFICOS

### **1. Identificação de Estações Críticas:**
- Procurar **bolhas vermelhas grandes**
- Focar em **regiões montanhosas**
- Analisar **proximidade com centros urbanos**

### **2. Planejamento de Monitoramento:**
- **Bolhas pequenas** = possível necessidade de mais estações
- **Áreas sem cobertura** = lacunas no monitoramento
- **Concentração de bolhas** = redundância possível

### **3. Análise de Correlações:**
- **Altitude vs Risco**: Verificar padrão visual
- **Importância vs Localização**: Distribuição regional
- **Densidade vs Tipo**: Adequação tecnológica

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### **Bolhas não aparecem:**
```bash
# Verificar se matplotlib está instalado
pip install matplotlib seaborn

# Verificar dados das estações
python -c "from mapa_bolhas import obter_estacoes_inmet; print(len(obter_estacoes_inmet()))"
```

### **Cores estranhas:**
- Verificar se índices estão no range 0-100
- Confirmar cálculo de risco nas funções

### **Tamanhos inadequados:**
- Ajustar normalização na função `adicionar_bolhas_ao_mapa()`
- Modificar multiplicador do raio (atualmente 500m)

---

## 📚 EXEMPLO PRÁTICO DE ANÁLISE

### **Cenário: Identificar Estações Prioritárias**

1. **Abrir mapa de bolhas**
2. **Procurar bolhas vermelhas grandes** = Alto risco + Alta importância
3. **Verificar distribuição geográfica**
4. **Analisar popup para detalhes**
5. **Comparar com gráfico de dispersão**

### **Interpretação dos Resultados:**
- **IBIRITE (ROLA MOCA)**: Bolha vermelha grande = Prioridade máxima
- **Região da Grande BH**: Concentração de bolhas importantes
- **Norte de MG**: Poucas estações = Possível lacuna

---

## 🌐 INTEGRAÇÃO COM OUTROS SISTEMAS

### **Exportar Dados:**
```python
# Acessar dados processados
from mapa_bolhas import obter_estacoes_inmet, processar_dados_para_bolhas
dados = processar_dados_para_bolhas(obter_estacoes_inmet())

# Converter para DataFrame
import pandas as pd
df = pd.DataFrame(dados)
df.to_csv('dados_bolhas_mg.csv', index=False)
```

### **API REST (exemplo):**
```python
# Servir dados via Flask
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/estacoes/bolhas')
def get_estacoes_bolhas():
    return jsonify(processar_dados_para_bolhas(obter_estacoes_inmet()))
```

---

## 📈 MÉTRICAS DE PERFORMANCE

### **Tempos de Processamento:**
- **Carregamento API INMET**: ~2-5 segundos
- **Processamento de métricas**: ~1 segundo
- **Geração do mapa**: ~2-3 segundos
- **Gráficos complementares**: ~3-5 segundos
- **Total**: ~8-15 segundos

### **Recursos Utilizados:**
- **Memória**: ~50-100MB durante processamento
- **Armazenamento**: ~140KB (HTML) + ~400KB (PNG)
- **CPU**: Baixo uso, picos durante matplotlib

---

## 🎉 PRÓXIMOS PASSOS

### **Melhorias Futuras:**
1. **Animação temporal** das bolhas
2. **Clustering** de estações próximas
3. **Filtros interativos** por tipo/risco
4. **Dados em tempo real** do INMET
5. **Integração com dados climáticos**

### **Expansão:**
- Outros estados brasileiros
- Diferentes tipos de sensores
- Dados históricos de eventos
- Machine learning para previsões

---

**Desenvolvido por:** Instituto Pereira Passos | NASA | Visualização Avançada  
**Versão:** 2.1 - Mapas de Bolhas para Minas Gerais  
**Última atualização:** Setembro 2025

