/* Modelo de carga por BULK INSERT no SQL Server 2019+.
   IMPORTANTE: use o caminho completo do CSV no computador do SERVIDOR SQL.
   A conta do serviço SQL Server precisa ter permissão de leitura nessa pasta.
   A carga direta pressupõe formato de data ISO e colunas na ordem do CSV.
   Em caso de divergência de drivers/formato, use sql/importar_sqlserver.py. */

-- Antes de recarregar dados DEMO (NÃO execute em uma base com dados reais):
-- TRUNCATE TABLE dbo.fato_entregas;

BULK INSERT dbo.fato_entregas
FROM 'C:\LastMile\data\lastmile_sintetico.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK,
    KEEPNULLS
);

SELECT COUNT(*) AS pedidos,
       SUM(CAST(entregue AS int)) AS concluidas,
       SUM(CAST(no_prazo AS int)) AS pontuais
FROM dbo.fato_entregas;
