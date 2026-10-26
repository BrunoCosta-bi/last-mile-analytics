/* Last-Mile Analytics — SQL Server 2019+
   Dados exclusivamente sintéticos. Execute dentro de PortfolioLastMile.
   Os scripts são idempotentes para desenvolvimento: views são substituídas;
   a tabela fato não é destruída caso já exista. */
IF OBJECT_ID(N'dbo.fato_entregas', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.fato_entregas (
        id_entrega            varchar(20)   NOT NULL PRIMARY KEY,
        data_coleta           datetime2(0)  NOT NULL,
        data_prevista         datetime2(0)  NOT NULL,
        data_entrega          datetime2(0)  NULL,
        cd                    varchar(10)   NOT NULL,
        uf                    char(2)       NOT NULL,
        cidade                nvarchar(100) NOT NULL,
        transportadora        nvarchar(100) NOT NULL,
        status                nvarchar(40)  NOT NULL,
        valor_pedido          decimal(12,2) NOT NULL,
        peso_kg               decimal(10,2) NOT NULL,
        tentativas            int           NOT NULL,
        motivo_atraso         nvarchar(80)  NULL,
        data_coleta_dia       date          NOT NULL,
        mes_referencia        date          NOT NULL,
        entregue              bit           NOT NULL,
        no_prazo              bit           NOT NULL,
        atraso_horas          decimal(10,2) NULL,
        tempo_ciclo_horas     decimal(10,2) NULL,
        CONSTRAINT CK_fato_flags CHECK (no_prazo = 0 OR entregue = 1),
        CONSTRAINT CK_fato_data CHECK (data_prevista >= data_coleta),
        CONSTRAINT CK_fato_tentativas CHECK (tentativas >= 0)
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.fato_entregas') AND name='IX_fato_coleta_cd')
    CREATE INDEX IX_fato_coleta_cd ON dbo.fato_entregas(data_coleta_dia, cd) INCLUDE (entregue, no_prazo);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('dbo.fato_entregas') AND name='IX_fato_transportadora_mes')
    CREATE INDEX IX_fato_transportadora_mes ON dbo.fato_entregas(transportadora, mes_referencia) INCLUDE (entregue, no_prazo);
GO
CREATE OR ALTER VIEW dbo.vw_kpi_diario AS
SELECT data_coleta_dia,
       cd,
       COUNT_BIG(*) AS total_pedidos,
       SUM(CASE WHEN entregue=1 THEN 1 ELSE 0 END) AS entregas_concluidas,
       SUM(CASE WHEN entregue=1 AND no_prazo=1 THEN 1 ELSE 0 END) AS pontuais,
       CAST(SUM(CASE WHEN entregue=1 AND no_prazo=1 THEN 1.0 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN entregue=1 THEN 1.0 ELSE 0 END),0) AS decimal(10,6)) AS on_time_pct
FROM dbo.fato_entregas
GROUP BY data_coleta_dia, cd;
GO
CREATE OR ALTER VIEW dbo.vw_evolucao_transportadora AS
WITH agregado AS (
    SELECT mes_referencia,
           transportadora,
           SUM(CASE WHEN entregue=1 THEN 1 ELSE 0 END) AS entregues,
           SUM(CASE WHEN entregue=1 AND no_prazo=1 THEN 1 ELSE 0 END) AS pontuais
    FROM dbo.fato_entregas
    GROUP BY mes_referencia, transportadora
), porcentagens AS (
    SELECT *, CAST(pontuais * 1.0 / NULLIF(entregues,0) AS decimal(10,6)) AS on_time_pct
    FROM agregado
), anterior AS (
    SELECT *, LAG(on_time_pct) OVER (PARTITION BY transportadora ORDER BY mes_referencia) AS on_time_mes_anterior_pct
    FROM porcentagens
)
SELECT mes_referencia, transportadora, entregues, pontuais, on_time_pct,
       on_time_mes_anterior_pct,
       CAST((on_time_pct - on_time_mes_anterior_pct) * 100.0 AS decimal(10,2)) AS delta_pontos_percentuais
FROM anterior;
GO
/* Checagem rápida após carga:
SELECT COUNT(*) pedidos, SUM(CAST(entregue AS int)) concluidas,
       SUM(CAST(no_prazo AS int)) no_prazo
FROM dbo.fato_entregas;
-- Esperado com seed padrão: 11965 / 10886 / 9705.
*/
