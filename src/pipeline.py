"""ETL da operação: deduplicação, quarentena, indicadores e auditoria."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATES = ['data_coleta', 'data_prevista', 'data_entrega']
REQUIRED = ['id_entrega', 'cd', 'uf', 'cidade', 'transportadora', 'status']
ALLOWED_STATUS = {'ENTREGUE', 'EM_TRANSITO', 'CANCELADO'}


def transform(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    df = raw.copy()
    for c in DATES:
        df[c] = pd.to_datetime(df[c], errors='coerce')
    for c in ['peso_kg', 'valor_pedido', 'tentativas']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    reasons = pd.Series('', index=df.index, dtype='string')

    def flag(mask: pd.Series, reason: str) -> None:
        nonlocal reasons
        mask = mask.fillna(True)
        reasons.loc[mask] = reasons.loc[mask] + reason + '; '

    flag(df.duplicated('id_entrega', keep='first'), 'id_entrega duplicado')
    flag(df[REQUIRED].isna().any(axis=1), 'campo obrigatorio nulo')
    flag(~df['status'].isin(ALLOWED_STATUS), 'status invalido')
    flag(df['data_coleta'].isna() | df['data_prevista'].isna(), 'data obrigatoria invalida')
    flag(df['data_prevista'] < df['data_coleta'], 'previsao anterior a coleta')
    flag(df['peso_kg'].isna() | (df['peso_kg'] <= 0), 'peso invalido')
    flag(df['valor_pedido'].isna() | (df['valor_pedido'] < 0), 'valor invalido')
    flag(df['tentativas'].isna() | (df['tentativas'] < 1), 'tentativas invalidas')
    flag((df['status'] == 'ENTREGUE') & df['data_entrega'].isna(), 'entrega sem data')
    flag((df['status'] == 'ENTREGUE') & (df['data_entrega'] < df['data_coleta']),
         'entrega antes da coleta')
    flag((df['status'] != 'ENTREGUE') & df['data_entrega'].notna(),
         'data de entrega em status nao entregue')

    rejected = df.loc[reasons.ne('')].copy()
    rejected['motivo_rejeicao'] = reasons.loc[rejected.index].str.strip('; ')
    clean = df.loc[reasons.eq('')].copy()
    clean['data_coleta_dia'] = clean['data_coleta'].dt.normalize()
    clean['mes_referencia'] = clean['data_coleta'].dt.to_period('M').dt.to_timestamp()
    clean['entregue'] = (clean['status'] == 'ENTREGUE').astype(int)
    clean['no_prazo'] = ((clean['status'] == 'ENTREGUE') &
                         (clean['data_entrega'] <= clean['data_prevista'])).astype(int)
    atraso = (clean['data_entrega'] - clean['data_prevista']).dt.total_seconds() / 3600
    tempo = (clean['data_entrega'] - clean['data_coleta']).dt.total_seconds() / 3600
    clean['atraso_horas'] = atraso.clip(lower=0).fillna(0).round(2)
    clean['tempo_ciclo_horas'] = tempo.fillna(0).round(2)
    metrics = {
        'linhas_entrada': int(len(raw)),
        'linhas_aprovadas': int(len(clean)),
        'linhas_rejeitadas': int(len(rejected)),
        'ids_unicos_aprovados': int(clean['id_entrega'].nunique()),
        'entregues': int(clean['entregue'].sum()),
        'no_prazo': int(clean['no_prazo'].sum()),
        'taxa_no_prazo': round(clean['no_prazo'].sum() / max(clean['entregue'].sum(), 1), 4),
        'nota': 'Dados 100% sinteticos. Nao representam empresa real.'
    }
    assert metrics['linhas_entrada'] == metrics['linhas_aprovadas'] + metrics['linhas_rejeitadas']
    assert metrics['ids_unicos_aprovados'] == metrics['linhas_aprovadas']
    return clean, rejected, metrics


def main() -> None:
    file = ROOT / 'data/raw/entregas_raw.csv'
    if not file.exists():
        raise SystemExit('Arquivo raw ausente. Execute: python -m src.generate_data')
    raw = pd.read_csv(file)
    clean, rejected, stats = transform(raw)
    out = ROOT / 'data/processed'
    out.mkdir(parents=True, exist_ok=True)
    # Exportar string ISO para evitar ambiguidades de localidade no SQL Server e Power BI.
    clean.to_csv(out / 'fato_entregas.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')
    rejected.to_csv(out / 'entregas_rejeitadas.csv', index=False,
                    date_format='%Y-%m-%d %H:%M:%S')
    delivered = clean.loc[clean.entregue == 1].copy()
    diario = (clean.groupby(['data_coleta_dia', 'cd'], as_index=False)
              .agg(total_entregas=('id_entrega', 'size'), entregues=('entregue', 'sum'),
                   pontuais=('no_prazo', 'sum')))
    diario['on_time_pct'] = (100 * diario['pontuais'] / diario['entregues'].replace(0, np.nan)).round(2)
    diario.to_csv(out / 'resumo_diario.csv', index=False, date_format='%Y-%m-%d')
    transp = (delivered.groupby('transportadora', as_index=False)
              .agg(entregues=('entregue', 'sum'), pontuais=('no_prazo', 'sum'),
                   lead_time_medio_h=('tempo_ciclo_horas', 'mean')))
    transp['on_time_pct'] = (100 * transp['pontuais'] / transp['entregues']).round(2)
    transp['lead_time_medio_h'] = transp['lead_time_medio_h'].round(2)
    transp.to_csv(out / 'resumo_transportadoras.csv', index=False)
    (out / 'qualidade.json').write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
