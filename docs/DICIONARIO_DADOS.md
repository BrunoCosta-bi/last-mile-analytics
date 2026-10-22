# Dicionário — Entregas

O grão da tabela `fato_entregas` é **uma linha por ID de entrega válido**.

| Coluna | Tipo | Regra |
|---|---|---|
| id_entrega | Texto | Chave única de entrega |
| data_coleta | Data/hora | Coleta operacional |
| data_prevista | Data/hora | Data/hora prometida |
| data_entrega | Data/hora ou nulo | Só preenchida quando entregue |
| data_coleta_dia | Data | Chave de relação com calendário |
| mes_referencia | Data | Primeiro dia do mês da coleta |
| cd, uf, cidade | Texto | Geografia e centro operacional fictícios |
| transportadora | Texto | Operador sintético |
| status | Texto | ENTREGUE, EM_TRANSITO, CANCELADO |
| entregue | Inteiro 0/1 | 1 se o registro foi concluído |
| no_prazo | Inteiro 0/1 | 1 se entregue e `data_entrega <= data_prevista` |
| valor_pedido | Decimal | Valor sintético do pedido |
| peso_kg | Decimal | Peso do pedido |
| tentativas | Inteiro | Quantidade de tentativas |
| motivo_atraso | Texto | Motivo atribuído de forma sintética |
| atraso_horas | Decimal | Máximo de `data_entrega - data_prevista` e zero, apenas concluídas |
| tempo_ciclo_horas | Decimal | Tempo de coleta até entrega, apenas concluídas |

Campos derivados de duração estão preenchidos com zero para registros não concluídos; **sempre filtrar `entregue=1` em médias**, ou usar as medidas DAX documentadas.
