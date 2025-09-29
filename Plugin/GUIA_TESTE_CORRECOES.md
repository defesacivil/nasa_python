# Guia de Teste - Correções LHASA MG

## Correções Aplicadas

### 1. Tratamento de Erros Melhorado
- Adicionado try/catch em todas as operações de processamento
- Mensagens de erro mais específicas
- Retorno de None em caso de erro para evitar falhas

### 2. Logging Detalhado
- Logging do tipo de camadas de entrada
- Mensagens de sucesso para cada etapa
- Feedback detalhado durante a execução

### 3. Validação de Camadas
- Verificação se camadas são válidas
- Verificação se camadas têm features
- Mensagens de erro específicas para cada problema

### 4. Correções de Código
- Corrigida indentação na função associateRainDataQgis
- Adicionado updateExtents() após processamento
- Melhor tratamento de exceções

## Como Testar

### 1. Preparar Dados
- Carregar camada de suscetibilidade no QGIS
- Carregar camada de zonas pluviométricas no QGIS
- Verificar se as camadas têm os campos necessários

### 2. Executar Algoritmo
- Abrir Caixa de Ferramentas de Processamento
- Procurar por "LHASA MG - Análise de Risco de Deslizamento"
- Configurar parâmetros
- Executar

### 3. Verificar Logs
- Observar mensagens de feedback no console
- Verificar se há mensagens de erro específicas
- Confirmar se cada etapa é executada com sucesso

### 4. Validar Resultado
- Verificar se o mapa final é gerado
- Confirmar se as cores estão aplicadas
- Validar se os níveis de perigo estão corretos

## Problemas Esperados

### Se ainda houver erro "valor inválido":
1. Verificar se as camadas têm geometrias válidas
2. Verificar se os campos necessários existem
3. Verificar se o SRC está configurado corretamente
4. Verificar se há dados suficientes nas camadas

### Se o algoritmo falhar em uma etapa específica:
1. Verificar a mensagem de erro específica
2. Verificar se a camada de entrada tem os dados necessários
3. Verificar se a expressão de cálculo está correta
4. Verificar se há permissão para salvar o arquivo de saída

## Logs de Debug

As correções adicionam logs detalhados que ajudam a identificar:
- Tipo de camadas sendo processadas
- Sucesso/falha de cada etapa
- Erros específicos com contexto
- Número de features processadas

## Contato

Se os problemas persistirem após as correções:
1. Verificar os logs detalhados
2. Testar com dados de exemplo simples
3. Verificar configuração do QGIS
4. Consultar documentação do QGIS
