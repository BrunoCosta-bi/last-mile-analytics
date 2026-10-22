USE PortfolioLastMile;
GO
-- 1) Priorizar transportadoras com mais entregas em atraso (volume e taxa).
SELECT transportadora,
       SUM(CONVERT(INT, entregue)) AS entregues,
       SUM(CASE WHEN entregue = 1 AND no_prazo = 0 THEN 1 ELSE 0 END) AS atrasadas,
       CAST(100.0 * SUM(CONVERT(INT, no_prazo)) /
            NULLIF(SUM(CONVERT(INT, entregue)), 0) AS DECIMAL(6,2)) AS on_time_pct
FROM dbo.fato_entregas
GROUP BY transportadora
ORDER BY atrasadas DESC;

-- 2) Pareto de motivos, somente entre entregas atrasadas.
WITH motivos AS (
    SELECT motivo_atraso, COUNT(*) AS qtd
    FROM dbo.fato_entregas
    WHERE entregue = 1 AND no_prazo = 0
    GROUP BY motivo_atraso
)
SELECT motivo_atraso, qtd,
       CAST(100.0 * SUM(qtd) OVER (ORDER BY qtd DESC, motivo_atraso) /
            NULLIF(SUM(qtd) OVER (), 0) AS DECIMAL(6,2)) AS percentual_acumulado
FROM motivos
ORDER BY qtd DESC, motivo_atraso;

-- 3) CD mais crítico a cada mês: ROW_NUMBER + CTE.
WITH centros AS (
    SELECT mes_referencia, cd,
           SUM(CONVERT(INT, entregue)) AS entregues,
           SUM(CONVERT(INT, no_prazo)) AS pontuais
    FROM dbo.fato_entregas
    GROUP BY mes_referencia, cd
), ranking AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY mes_referencia
        ORDER BY 1.0 * pontuais / NULLIF(entregues, 0), cd
    ) AS posicao
    FROM centros
    WHERE entregues > 0
)
SELECT mes_referencia, cd, entregues, pontuais,
       CAST(100.0 * pontuais / entregues AS DECIMAL(6,2)) AS on_time_pct
FROM ranking WHERE posicao = 1
ORDER BY mes_referencia;
