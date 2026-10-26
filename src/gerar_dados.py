#!/usr/bin/env python3
"""Gera uma base sintética e reprodutível de entregas last mile.

Somente biblioteca padrão. Os alvos de volume são constantes INTENCIONAIS para
facilitar testes e comparação com a primeira versão do dashboard.
Não representa qualquer operação real.
"""
from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

TOTAL = 11965
CONCLUIDAS = 10886
NO_PRAZO = 9705
DATA_CORTE = datetime(2026, 10, 26, 23, 59, 59)
SEMENTE = 20261026

COLUNAS = [
    "id_entrega", "data_coleta", "data_prevista", "data_entrega", "cd", "uf",
    "cidade", "transportadora", "status", "valor_pedido", "peso_kg", "tentativas",
    "motivo_atraso", "data_coleta_dia", "mes_referencia", "entregue", "no_prazo",
    "atraso_horas", "tempo_ciclo_horas",
]
CDS = {
    "RJ01": [("RJ", "Rio de Janeiro"), ("RJ", "Niterói"), ("RJ", "Nova Iguaçu")],
    "SP01": [("SP", "São Paulo"), ("SP", "Guarulhos"), ("SP", "Campinas")],
    "MG01": [("MG", "Belo Horizonte"), ("MG", "Contagem"), ("MG", "Betim")],
    "PR01": [("PR", "Curitiba"), ("PR", "São José dos Pinhais"), ("PR", "Londrina")],
}
TRANSPORTADORAS = ["Atlas Log", "Rota Sul", "Veloz Express", "TransBrasil", "Norte Cargo", "Entrega Mais"]
MOTIVOS = ["Trânsito intenso", "Ausência do destinatário", "Restrição de acesso", "Falha operacional", "Condição climática"]

def dt(v: datetime | None) -> str:
    return v.strftime("%Y-%m-%dT%H:%M:%S") if v else ""

def gerar(seed: int = SEMENTE):
    rng = random.Random(seed)
    classes = ["pontual"] * NO_PRAZO + ["atrasada"] * (CONCLUIDAS - NO_PRAZO) + ["pendente"] * (TOTAL - CONCLUIDAS)
    rng.shuffle(classes)
    cds = list(CDS)
    inicio = datetime(2026, 1, 1)
    dias = (datetime(2026, 10, 16) - inicio).days
    for i, classe in enumerate(classes, 1):
        coleta = inicio + timedelta(days=rng.randint(0, dias), hours=rng.randint(6, 17), minutes=rng.randint(0, 59))
        if classe == "pendente" and rng.random() < 0.22:
            # Uma parcela das pendências é recente e ainda está dentro do prazo.
            coleta = datetime(2026, 10, 24) + timedelta(days=rng.randint(0, 2), hours=rng.randint(6, 17))
        cd = rng.choice(cds)
        uf, cidade = rng.choice(CDS[cd])
        transp = rng.choice(TRANSPORTADORAS)
        prazo = coleta + timedelta(hours=rng.randint(24, 120))
        if classe == "pontual":
            # Tempo positivo entre coleta e limite previsto.
            intervalo = (prazo - coleta).total_seconds() / 3600
            ciclo = rng.uniform(3.0, intervalo)
            entrega = coleta + timedelta(hours=ciclo)
            tentativas = rng.choices([1, 2, 3], [88, 10, 2])[0]
            atraso, motivo, status, entregue, pontual = 0.0, "", "Entregue", 1, 1
        elif classe == "atrasada":
            demora = rng.uniform(0.5, 96)
            entrega = prazo + timedelta(hours=demora)
            tentativas = rng.choices([1, 2, 3], [63, 28, 9])[0]
            atraso, motivo, status, entregue, pontual = demora, rng.choice(MOTIVOS), "Entregue fora do prazo", 1, 0
        else:
            entrega = None
            tentativas = rng.choices([0, 1, 2], [48, 46, 6])[0]
            atraso, motivo, status, entregue, pontual = None, "", rng.choice(["Em trânsito", "Pendente"]), 0, 0
        ciclo = (entrega - coleta).total_seconds() / 3600 if entrega else None
        yield {
            "id_entrega": f"LM-{i:06d}",
            "data_coleta": dt(coleta),
            "data_prevista": dt(prazo),
            "data_entrega": dt(entrega),
            "cd": cd, "uf": uf, "cidade": cidade, "transportadora": transp,
            "status": status,
            "valor_pedido": f"{rng.uniform(35, 1800):.2f}",
            "peso_kg": f"{rng.uniform(0.2, 75):.2f}",
            "tentativas": tentativas,
            "motivo_atraso": motivo,
            "data_coleta_dia": coleta.strftime("%Y-%m-%d"),
            "mes_referencia": coleta.strftime("%Y-%m-01"),
            "entregue": entregue,
            "no_prazo": pontual,
            "atraso_horas": "" if atraso is None else f"{atraso:.2f}",
            "tempo_ciclo_horas": "" if ciclo is None else f"{ciclo:.2f}",
        }

def salvar(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/lastmile_sintetico.csv")
    parser.add_argument("--sample", default="data/lastmile_amostra.csv")
    parser.add_argument("--seed", type=int, default=SEMENTE)
    args = parser.parse_args()
    dados = list(gerar(args.seed))
    salvar(Path(args.output), dados)
    salvar(Path(args.sample), dados[:250])
    print(f"Gerados {len(dados):,} pedidos; concluídos: {sum(x['entregue'] for x in dados):,}; no prazo: {sum(x['no_prazo'] for x in dados):,}")

if __name__ == "__main__":
    main()
