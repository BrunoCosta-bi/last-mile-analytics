import pandas as pd
from src.pipeline import transform


def sample():
    return pd.DataFrame([
        {'id_entrega':'E1', 'data_coleta':'2026-01-01 08:00:00',
         'data_prevista':'2026-01-02 08:00:00', 'data_entrega':'2026-01-02 06:00:00',
         'cd':'RJ01','uf':'RJ','cidade':'Rio de Janeiro','transportadora':'A',
         'status':'ENTREGUE','valor_pedido':10,'peso_kg':1,'tentativas':1,'motivo_atraso':'Nao aplicavel'},
        {'id_entrega':'E1', 'data_coleta':'2026-01-01 08:00:00',
         'data_prevista':'2026-01-02 08:00:00', 'data_entrega':'2026-01-02 10:00:00',
         'cd':'RJ01','uf':'RJ','cidade':'Rio de Janeiro','transportadora':'A',
         'status':'ENTREGUE','valor_pedido':10,'peso_kg':1,'tentativas':1,'motivo_atraso':'Capacidade operacional'},
    ])


def test_dedup_and_ontime():
    clean, rejected, metrics = transform(sample())
    assert len(clean) == 1 and len(rejected) == 1
    assert clean.iloc[0]['no_prazo'] == 1
    assert metrics['taxa_no_prazo'] == 1
    assert 'duplicado' in rejected.iloc[0]['motivo_rejeicao']


def test_invalid_weight_quarantined():
    data = sample().iloc[:1].copy()
    data.loc[0, 'peso_kg'] = -1
    clean, rejected, _ = transform(data)
    assert clean.empty
    assert 'peso invalido' in rejected.iloc[0]['motivo_rejeicao']
