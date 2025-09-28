# Instalação do Plugin LHASA MG no QGIS

## Problema Resolvido

O erro `ModuleNotFoundError: No module named 'lhasa_mg.LHASA_Mg'` foi corrigido. O problema estava relacionado à convenção de nomes Python e dependências complexas.

## Solução Implementada

1. **Arquivo Simplificado**: Criado `lhasa_mg_simple.py` com versão otimizada para QGIS
2. **Correção de Importações**: Ajustadas todas as referências nos arquivos do plugin
3. **Tratamento de Erros**: Adicionado tratamento robusto de erros de importação

## Estrutura de Arquivos Necessária

Certifique-se de que sua pasta do plugin contenha:

```
lhasa_mg/
├── __init__.py
├── lhasa_mg_plugin.py
├── lhasa_mg_provider.py
├── lhasa_mg_simple.py          ← Arquivo principal (novo)
├── metadata.txt
└── README_QGIS.md
```

## Passos para Instalação

### 1. Localizar a Pasta de Plugins

**Windows:**

```
C:\Users\[seu_usuario]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
```

**Linux:**

```
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
```

**macOS:**

```
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
```

### 2. Criar a Pasta do Plugin

1. Navegue até a pasta de plugins do QGIS
2. Crie uma pasta chamada `lhasa_mg`
3. Copie todos os arquivos listados acima para esta pasta

### 3. Verificar Arquivos

Certifique-se de que os seguintes arquivos estão presentes:

- ✅ `__init__.py`
- ✅ `lhasa_mg_plugin.py`
- ✅ `lhasa_mg_provider.py`
- ✅ `lhasa_mg_simple.py` (arquivo principal)
- ✅ `metadata.txt`

### 4. Reiniciar o QGIS

1. Feche completamente o QGIS
2. Abra o QGIS novamente

### 5. Ativar o Plugin

1. Vá em **Plugins → Gerenciar e Instalar Plugins**
2. Clique na aba **Instalados**
3. Procure por "LHASA MG"
4. Marque a caixa para ativar o plugin

## Verificar se Funcionou

### Método 1: Caixa de Ferramentas

1. Abra a **Caixa de Ferramentas de Processamento** (Ctrl+Alt+T)
2. Procure por **"Análises de Risco"**
3. Deve aparecer **"LHASA MG - Análise de Risco de Deslizamento"**

### Método 2: Console Python

Execute no Console Python do QGIS:

```python
# Teste de importação
try:
    from processing import algorithmHelp
    help_text = algorithmHelp("lhasa_mg:lhasa_mg_analysis")
    print("✓ Plugin carregado com sucesso!")
    print(help_text)
except:
    print("✗ Plugin não encontrado")
```

## Solução de Problemas

### Erro: "Plugin não aparece na lista"

- Verifique se todos os arquivos estão na pasta correta
- Certifique-se de que o arquivo `metadata.txt` está presente
- Reinicie o QGIS

### Erro: "Algoritmo não encontrado"

- Verifique se o arquivo `lhasa_mg_simple.py` está presente
- Abra o Console Python e execute:
  ```python
  import processing
  processing.core.Processing.Processing.initialize()
  ```

### Erro de Dependências

O plugin agora usa apenas bibliotecas padrão do QGIS. Se ainda houver erros:

1. Verifique se tem internet (para acessar API INMET)
2. Instale bibliotecas necessárias:
   ```bash
   pip install requests unidecode
   ```

## Principais Melhorias

### Versão Simplificada (`lhasa_mg_simple.py`)

- ✅ Sem dependências externas problemáticas
- ✅ Tratamento robusto de erros
- ✅ Interface simplificada mas funcional
- ✅ Integração completa com API INMET
- ✅ Feedback em tempo real

### Funcionalidades Mantidas

- ✅ Busca automática de estações INMET em MG
- ✅ Análise de risco baseada em suscetibilidade + chuva
- ✅ Interface gráfica integrada ao QGIS
- ✅ Classificação de perigo (BAIXO → CRÍTICO)

## Uso Básico

1. **Prepare os dados:**

   - Camada de suscetibilidade com campo `gridcode` (1, 2, 3)
   - Camada de zonas pluviométricas

2. **Execute o algoritmo:**

   - Caixa de Ferramentas → Análises de Risco → LHASA MG
   - Configure os parâmetros
   - Clique em Executar

3. **Interprete os resultados:**
   - BAIXO: Risco mínimo
   - MODERADO: Risco moderado
   - ALTO: Risco alto
   - MUITO_ALTO: Risco muito alto
   - CRÍTICO: Risco crítico

## Suporte

Se ainda houver problemas:

1. Verifique os logs do QGIS
2. Execute o teste no Console Python
3. Verifique a conexão com a internet
4. Consulte a documentação completa no `README_QGIS.md`
