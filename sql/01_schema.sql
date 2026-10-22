-- SQL Server 2019+ | executar no SSMS
IF DB_ID(N'PortfolioLastMile') IS NULL
    CREATE DATABASE PortfolioLastMile;
GO
USE PortfolioLastMile;
GO
IF OBJECT_ID('dbo.fato_entregas', 'U') IS NOT NULL DROP TABLE dbo.fato_entregas;
GO
CREATE TABLE dbo.fato_entregas (
    id_entrega VARCHAR(20) NOT NULL PRIMARY KEY,
    data_coleta DATETIME2(0) NOT NULL,
    data_prevista DATETIME2(0) NOT NULL,
    data_entrega DATETIME2(0) NULL,
    cd VARCHAR(10) NOT NULL,
    uf CHAR(2) NOT NULL,
    cidade NVARCHAR(80) NOT NULL,
    transportadora NVARCHAR(80) NOT NULL,
    status VARCHAR(20) NOT NULL,
    valor_pedido DECIMAL(14,2) NOT NULL,
    peso_kg DECIMAL(12,2) NOT NULL,
    tentativas SMALLINT NOT NULL,
    motivo_atraso NVARCHAR(80) NOT NULL,
    data_coleta_dia DATE NOT NULL,
    mes_referencia DATE NOT NULL,
    entregue BIT NOT NULL,
    no_prazo BIT NOT NULL,
    atraso_horas DECIMAL(12,2) NOT NULL,
    tempo_ciclo_horas DECIMAL(12,2) NOT NULL
);
GO
CREATE INDEX IX_Entregas_Coleta ON dbo.fato_entregas(data_coleta_dia, cd)
    INCLUDE (entregue, no_prazo);
CREATE INDEX IX_Entregas_Transportadora ON dbo.fato_entregas(transportadora, mes_referencia);
GO
