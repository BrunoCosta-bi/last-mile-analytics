USE PortfolioLastMile;
GO
CREATE OR ALTER VIEW dbo.vw_kpi_diario AS
SELECT data_coleta_dia, cd,
       COUNT(*) AS total_pedidos,
       SUM(CONVERT(INT, entregue)) AS entregas_concluidas,
       SUM(CONVERT(INT, no_prazo)) AS pontuais,
       CAST(100.0 * SUM(CONVERT(INT, no_prazo)) /
            NULLIF(SUM(CONVERT(INT, entregue)), 0) AS DECIMAL(6,2)) AS on_time_pct
FROM dbo.fato_entregas
GROUP BY data_coleta_dia, cd;
GO
-- Exemplo de Window Function: comparação mensal por transportadora.
CREATE OR ALTER VIEW dbo.vw_evolucao_transportadora AS
WITH mensal AS (
    SELECT mes_referencia, transportadora,
           SUM(CONVERT(INT, entregue)) AS entregues,
           SUM(CONVERT(INT, no_prazo)) AS pontuais
    FROM dbo.fato_entregas
    GROUP BY mes_referencia, transportadora
), taxa AS (
    SELECT mes_referencia, transportadora, entregues, pontuais,
           CAST(100.0 * pontuais / NULLIF(entregues, 0) AS DECIMAL(6,2)) AS on_time_pct
    FROM mensal
)
SELECT *,
       LAG(on_time_pct) OVER (PARTITION BY transportadora ORDER BY mes_referencia)
           AS on_time_mes_anterior_pct,
       on_time_pct - LAG(on_time_pct) OVER
           (PARTITION BY transportadora ORDER BY mes_referencia) AS delta_pontos_percentuais
FROM taxa;
GO
