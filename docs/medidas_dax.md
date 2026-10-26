# Medidas DAX e interpretações

As medidas abaixo documentam regras utilizadas pelo modelo semântico PBIP. Elas também servem de referência para explicar as regras em entrevistas.

```dax
Entregas Atrasadas =
CALCULATE(
    COUNTROWS(fato_entregas),
    fato_entregas[entregue] = TRUE(),
    fato_entregas[no_prazo] = FALSE()
)

Data de Corte = DATE(2026, 10, 26)

Pendentes Vencidos =
VAR FimDia = [Data de Corte] + 1
RETURN
    COUNTROWS(
        FILTER(
            fato_entregas,
            fato_entregas[entregue] = FALSE()
                && fato_entregas[data_prevista] < FimDia
        )
    )

Taxa de Atraso Concluídas % =
DIVIDE([Entregas Atrasadas], [Entregas Concluídas])

On Time Mês Anterior % =
CALCULATE(
    [On Time %],
    DATEADD(dim_calendario[Date], -1, MONTH)
)

Delta On Time (p.p.) =
VAR Atual = [On Time %]
VAR Anterior = [On Time Mês Anterior %]
RETURN
    IF(ISBLANK(Anterior), BLANK(), (Atual - Anterior) * 100)
```

**Interpretação:** `Entregas Atrasadas` considera somente concluídas; `Pendentes Vencidos` representa backlog vencido. Não some as duas medidas como se tivessem o mesmo denominador e período sem explicar a análise. O cálculo de mês anterior pressupõe segmentação por `dim_calendario`, relacionada à data de coleta. Com `data_entrega_dia`, use `USERELATIONSHIP` numa medida de entregas por data efetiva.

A data de corte fixa impede que o mesmo CSV produza resultados diferentes conforme o dia da abertura. Em um cenário produtivo, a data de corte deveria vir de uma referência controlada, como um snapshot de ingestão ou parâmetro do negócio.

**Ressalva:** uma entrega concluída após a data de corte pode existir no CSV sintético de demonstração somente se a lógica do gerador permitir; neste pacote, os horários foram limitados para não ultrapassar a data de corte. A regra usada para medir atrasos deve ser aprovada com o negócio (data/hora real, justificativas e possíveis exceções contratuais).
