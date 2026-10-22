"""Carga parametrizada para SQL Server: executar o DDL antes, com Windows Auth."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATABASE = 'PortfolioLastMile'
TABLES = [
    ('data/processed/fato_entregas.csv', 'fato_entregas',
     ['data_coleta', 'data_prevista', 'data_entrega', 'data_coleta_dia', 'mes_referencia'])
]


def normalize(v):
    if pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
    if isinstance(v, np.generic):
        return v.item()
    return v


def load_table(connection, source: Path, target: str, date_cols: list[str], replace: bool) -> int:
    frame = pd.read_csv(source)
    for col in date_cols:
        frame[col] = pd.to_datetime(frame[col], errors='coerce')
    columns = list(frame.columns)
    placeholders = ', '.join('?' for _ in columns)
    sql = f'INSERT INTO dbo.{target} (' + ', '.join(f'[{c}]' for c in columns) + f') VALUES ({placeholders})'
    cur = connection.cursor()
    current = cur.execute(f'SELECT COUNT(*) FROM dbo.{target}').fetchval()
    if current and not replace:
        raise RuntimeError(f'{target} ja contem {current} registros; use --replace para sobrescrever.')
    if current and replace:
        cur.execute(f'DELETE FROM dbo.{target}')
    cur.fast_executemany = True
    values = [tuple(normalize(v) for v in row) for row in frame.itertuples(index=False, name=None)]
    cur.executemany(sql, values)
    return len(values)


def main() -> None:
    try:
        import pyodbc
    except ImportError as e:
        raise SystemExit('Instale o driver Python: pip install -r requirements-sqlserver.txt') from e
    ap = argparse.ArgumentParser()
    ap.add_argument('--server', required=True, help=r'Exemplo: SERVIDOR\INSTANCIA')
    ap.add_argument('--driver', default='ODBC Driver 18 for SQL Server')
    ap.add_argument('--replace', action='store_true', help='Exclui dados existentes antes da carga')
    args = ap.parse_args()
    connection_string = (f'DRIVER={{{args.driver}}};SERVER={args.server};DATABASE={DATABASE};'
                         'Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes;')
    cn = pyodbc.connect(connection_string, autocommit=False)
    try:
        for relative_path, name, dates in TABLES:
            count = load_table(cn, ROOT / relative_path, name, dates, args.replace)
            print(f'{name}: {count:,} registros carregados')
        cn.commit()
        print('Transacao SQL confirmada.')
    except Exception:
        cn.rollback()
        raise
    finally:
        cn.close()


if __name__ == '__main__':
    main()
