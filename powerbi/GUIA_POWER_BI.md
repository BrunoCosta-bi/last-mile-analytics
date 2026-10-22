# Montagem do dashboard — Last Mile

> Não há `.pbix` ou `.pbip` gerado automaticamente aqui. Execute no Power BI Desktop e salve em **Arquivo > Salvar como > Projeto do Power BI (.pbip)** dentro desta pasta.

## 1. Fonte
- Recomendado: **Obter dados > SQL Server**. Banco `PortfolioLastMile`, tabela `dbo.fato_entregas`, modo Importar.
- Alternativa sem SQL Server: importe `../data/processed/fato_entregas.csv` (UTF-8) e ajuste os tipos: datas, inteiros e números decimais.
- Renomeie a tabela no painel de dados para `fato_entregas` se o nome importado for diferente.

## 2. Modelo
- Crie a tabela `DimCalendario` conforme `medidas.dax`.
- Relacione `DimCalendario[Date]` (1) → `fato_entregas[data_coleta_dia]` (*), filtro de direção única.
- Formate `On Time %`, `Taxa Conclusao %`, `Meta On Time` como porcentagem, duas casas.
- `Desvio Meta (p.p.)` é número decimal, não porcentagem.

## 3. Layout sugerido
**Página 1: Visão executiva**
- Cards: total de pedidos | entregas concluídas | On Time % | variação da meta em p.p.
- Gráfico de linhas: eixo `DimCalendario[MesAno]`, valores `On Time %`, linha de referência `Meta On Time`.
- Barras ordenadas: `transportadora` x `Entregas Atrasadas`.
- Matriz: `cd` x `On Time %`, `Entregas Concluidas`, `Lead Time Medio (h)`.
- Segmentações: mês, CD, UF e transportadora.

**Página 2: Diagnóstico da operação**
- Barras: `motivo_atraso` x `Entregas Atrasadas` (filtrar motivos "Nao aplicavel").
- Ranking de transportadoras por `On Time %`, com volume entregue ao lado.
- Tabela de entregas críticas: ID, CD, transportadora, previsão, entrega, atraso_horas.
- Destaque áreas com menor pontualidade e maior volume absoluto de atrasos.

## 4. Storytelling
Pergunta → **Qual transportadora está pressionando o SLA?**
Evidência → ranking por atraso absoluto + taxa + evolução mensal.
Decisão → priorizar tratativas onde impacto e volume sejam maiores.

**Atenção:** os dados são fictícios e não validam desempenho de transportadoras reais. Somente entregas concluídas entram no denominador do On Time.

## 5. Git
Salve como `.pbip` dentro de `powerbi/`, preservando o `.gitignore`. Adicione capturas reais do painel em `powerbi/screenshots/` após criar o relatório.
