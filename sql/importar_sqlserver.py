"""Carga alternativa para SQL Server usando ODBC (dependência opcional: pyodbc).

Exemplo: python sql/importar_sqlserver.py --csv data/lastmile_sintetico.csv \
   --server 'localhost\\MSSQLSERVER01' --database PortfolioLastMile
Execute antes sql/01_schema_views.sql. Apenas dados DEMO em banco próprio.
"""
import argparse
import csv

COLS = [
    "id_entrega", "data_coleta", "data_prevista", "data_entrega", "cd", "uf",
    "cidade", "transportadora", "status", "valor_pedido", "peso_kg", "tentativas",
    "motivo_atraso", "data_coleta_dia", "mes_referencia", "entregue", "no_prazo",
    "atraso_horas", "tempo_ciclo_horas"
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default="data/lastmile_sintetico.csv")
    p.add_argument("--server", required=True)
    p.add_argument("--database", default="PortfolioLastMile")
    p.add_argument("--driver", default="ODBC Driver 18 for SQL Server")
    p.add_argument("--replace", action="store_true", help="Limpa a tabela antes da carga — use APENAS em banco de demonstração.")
    a = p.parse_args()
    try:
        import pyodbc
    except ImportError as e:
        raise SystemExit("Instale: pip install pyodbc (e driver ODBC da Microsoft).") from e
    conn_str = f"DRIVER={{{a.driver}}};SERVER={a.server};DATABASE={a.database};Trusted_Connection=yes;TrustServerCertificate=yes;"
    with pyodbc.connect(conn_str, autocommit=False) as conn:
        cursor = conn.cursor()
        if a.replace:
            cursor.execute("DELETE FROM dbo.fato_entregas")
        marks = ",".join("?" for _ in COLS)
        sql = f"INSERT INTO dbo.fato_entregas ({','.join(COLS)}) VALUES ({marks})"
        with open(a.csv, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            chunk = []
            for r in reader:
                chunk.append(tuple(None if r[col] == "" else r[col] for col in COLS))
                if len(chunk) >= 500:
                    cursor.executemany(sql, chunk)
                    chunk.clear()
            if chunk:
                cursor.executemany(sql, chunk)
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM dbo.fato_entregas")
        print("Linhas no SQL Server:", cursor.fetchone()[0])

if __name__ == "__main__":
    main()
