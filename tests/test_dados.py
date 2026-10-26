import csv
import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gerar_dados import gerar, TOTAL, CONCLUIDAS, NO_PRAZO, DATA_CORTE, COLUNAS

class TestDadosSinteticos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = list(gerar())

    def test_reprodutibilidade(self):
        self.assertEqual(self.rows, list(gerar()))

    def test_volumes_e_chaves(self):
        self.assertEqual(len(self.rows), TOTAL)
        self.assertEqual(len({r['id_entrega'] for r in self.rows}), TOTAL)
        self.assertEqual(sum(r['entregue'] for r in self.rows), CONCLUIDAS)
        self.assertEqual(sum(r['no_prazo'] for r in self.rows), NO_PRAZO)

    def test_validade_temporal_e_status(self):
        for r in self.rows:
            coleta = datetime.fromisoformat(r['data_coleta'])
            prazo = datetime.fromisoformat(r['data_prevista'])
            self.assertGreaterEqual(prazo, coleta)
            if r['entregue']:
                entrega = datetime.fromisoformat(r['data_entrega'])
                self.assertGreater(entrega, coleta)
                self.assertEqual(bool(r['no_prazo']), entrega <= prazo)
            else:
                self.assertEqual(r['data_entrega'], '')
                self.assertEqual(r['no_prazo'], 0)

    def test_pendentes_vencidos_na_data_de_corte(self):
        vencidos = sum(
            not r['entregue'] and datetime.fromisoformat(r['data_prevista']) < DATA_CORTE
            for r in self.rows
        )
        self.assertGreater(vencidos, 0)
        self.assertLessEqual(vencidos, TOTAL - CONCLUIDAS)

    def test_schema_csv(self):
        path = ROOT / 'data' / 'lastmile_sintetico.csv'
        with path.open(encoding='utf-8', newline='') as f:
            rd = csv.DictReader(f)
            self.assertEqual(rd.fieldnames, COLUNAS)
            self.assertEqual(sum(1 for _ in rd), TOTAL)

if __name__ == '__main__':
    unittest.main()
