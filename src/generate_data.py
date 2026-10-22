"""Gera uma base 100% fictícia de entregas, incluindo problemas controlados."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def generate(n: int = 12000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cds = np.array(['RJ01', 'SP01', 'MG01', 'PR01'])
    cidades = {'RJ01': ('RJ', 'Rio de Janeiro'), 'SP01': ('SP', 'Sao Paulo'),
               'MG01': ('MG', 'Belo Horizonte'), 'PR01': ('PR', 'Curitiba')}
    carriers = np.array(['TransRota', 'Expresso Sul', 'ViaLog', 'MoveCargo'])
    cd = rng.choice(cds, size=n, p=[.42, .28, .20, .10])
    transportadora = rng.choice(carriers, size=n, p=[.36, .27, .23, .14])
    inicio = pd.Timestamp('2026-01-01')
    data_coleta = (inicio + pd.to_timedelta(rng.integers(0, 273, n), unit='D')
                   + pd.to_timedelta(rng.integers(6, 20, n), unit='h'))
    prazo_h = rng.choice([24, 36, 48, 72], n, p=[.18, .30, .32, .20])
    data_prevista = data_coleta + pd.to_timedelta(prazo_h, unit='h')
    # Portadoras e meses podem ter desempenhos distintos (hipótese fictícia).
    carrier_shift = np.select([transportadora == 'MoveCargo',
                               transportadora == 'ViaLog'], [13, 6], default=0)
    realizado_h = np.maximum(3, prazo_h + rng.normal(-17, 10, n) + carrier_shift)
    data_entrega = data_coleta + pd.to_timedelta(realizado_h, unit='h')
    status = rng.choice(['ENTREGUE', 'EM_TRANSITO', 'CANCELADO'],
                        size=n, p=[.91, .07, .02])
    motivo_atraso = rng.choice(['Capacidade operacional', 'Restricao de acesso',
                                'Ausencia do destinatario', 'Atraso na transferencia'], n)
    atrasada = (data_entrega > data_prevista) & (status == 'ENTREGUE')
    df = pd.DataFrame({
        'id_entrega': [f'ENT{i:07d}' for i in range(1, n + 1)],
        'data_coleta': data_coleta,
        'data_prevista': data_prevista,
        'data_entrega': data_entrega,
        'cd': cd,
        'uf': [cidades[c][0] for c in cd],
        'cidade': [cidades[c][1] for c in cd],
        'transportadora': transportadora,
        'status': status,
        'valor_pedido': rng.uniform(40, 1350, n).round(2),
        'peso_kg': rng.uniform(.3, 45, n).round(2),
        'tentativas': rng.choice([1, 2, 3], n, p=[.85, .12, .03]),
        'motivo_atraso': np.where(atrasada, motivo_atraso, 'Nao aplicavel'),
    })
    df.loc[df.status != 'ENTREGUE', 'data_entrega'] = pd.NaT
    # Problemas realistas: registros duplicados, campos ausentes e datas inválidas.
    df.loc[15:24, 'cd'] = None
    df.loc[25:34, 'peso_kg'] = -2
    df.loc[35:39, 'status'] = 'INDEFINIDO'
    df.loc[40:44, 'data_prevista'] = pd.NaT
    df.loc[45:49, 'data_prevista'] = df.loc[45:49, 'data_coleta'] - pd.Timedelta(hours=4)
    df = pd.concat([df, df.iloc[:60].copy()], ignore_index=True)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


def main() -> None:
    out = ROOT / 'data' / 'raw' / 'entregas_raw.csv'
    out.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    for col in ['data_coleta', 'data_prevista', 'data_entrega']:
        df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(out, index=False)
    print(f'Gerado: {out} | linhas={len(df):,}')


if __name__ == '__main__':
    main()
