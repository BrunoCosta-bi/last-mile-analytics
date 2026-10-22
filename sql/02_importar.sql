-- 1. Execute sql/01_schema.sql.
-- 2. Substitua o caminho abaixo pelo caminho ABSOLUTO do arquivo processado.
-- 3. O serviço do SQL Server precisa ter permissão de leitura nesse caminho.
USE PortfolioLastMile;
GO
BULK INSERT dbo.fato_entregas
FROM 'C:\repos\01-last-mile-analytics\data\processed\fato_entregas.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    CODEPAGE = '65001',
    ROWTERMINATOR = '0x0a',
    TABLOCK
);
GO
SELECT COUNT(*) AS linhas, COUNT(DISTINCT id_entrega) AS ids_unicos
FROM dbo.fato_entregas;
GO
