# Guia Rápido - Solução de Problemas Mapa LHASA MG

## Problema: Mapa não é gerado no QGIS

### Verificações Essenciais:

1. **Camadas de Entrada**
   - [ ] Camada de suscetibilidade carregada
   - [ ] Camada de zonas pluviométricas carregada
   - [ ] Camadas têm geometrias válidas

2. **Campos Necessários**
   - [ ] Campo 'gridcode' na camada de suscetibilidade
   - [ ] Campos 'Cod' e 'Est' na camada de zonas
   - [ ] Campos têm dados válidos

3. **Configuração do Projeto**
   - [ ] SRC configurado para SIRGAS 2000 / UTM Zona 23S
   - [ ] Camadas estão alinhadas visualmente
   - [ ] Projeto salvo corretamente

4. **API INMET**
   - [ ] Token da API configurado no código
   - [ ] Conexão com internet funcionando
   - [ ] Data da análise válida

5. **Execução do Algoritmo**
   - [ ] QGIS está executando
   - [ ] Plugin LHASA MG está ativado
   - [ ] Parâmetros configurados corretamente
   - [ ] Diretório de saída tem permissão de escrita

### Soluções Rápidas:

1. **Se as camadas não aparecem:**
   - Recarregue as camadas no QGIS
   - Verifique o formato dos arquivos
   - Use "Adicionar Camada Vetorial"

2. **Se os campos não existem:**
   - Verifique os nomes na tabela de atributos
   - Renomeie os campos se necessário
   - Ou modifique o código para usar os nomes corretos

3. **Se o SRC está incorreto:**
   - Vá em Projeto > Propriedades > SRC
   - Selecione SIRGAS 2000 / UTM Zona 23S (EPSG:31983)
   - Aplique a configuração

4. **Se a API não funciona:**
   - Configure o token real da API INMET
   - Teste a conexão manualmente
   - Use uma data anterior (ex: ontem)

5. **Se o algoritmo não executa:**
   - Execute dentro do QGIS (não via linha de comando)
   - Use a Caixa de Ferramentas de Processamento
   - Verifique os logs de erro

### Teste Passo a Passo:

1. Abra o QGIS
2. Carregue as camadas de entrada
3. Configure o SRC do projeto
4. Execute: Plugin/teste_qgis_lhasa.py no console Python
5. Vá em Processamento > Caixa de Ferramentas
6. Procure por "LHASA MG - Análise de Risco de Deslizamento"
7. Execute o algoritmo
8. Verifique o resultado no QGIS

### Logs de Debug:

- Arquivo principal: logs/LHASA_MG_*.log
- Arquivo de erros: logs/LHASA_ERRORS_*.log
- Arquivo da sessão: logs/LHASA_SESSION_*.json

### Contato:

Se os problemas persistirem, verifique os logs detalhados
e execute o script de teste no QGIS.
