import base64
import gzip
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'powerbi'/'projetogit.SemanticModel'/'definition'

class TestPbip(unittest.TestCase):
    def test_modelo_sem_tabelas_ociosas(self):
        tab = MODEL/'tables'
        self.assertFalse(list(tab.glob('LocalDateTable*')))
        self.assertFalse(list(tab.glob('DateTableTemplate*')))
        self.assertFalse(list(tab.glob('vw_*')))
        names = [x.stem for x in tab.glob('*.tmdl')]
        self.assertIn('dim_calendario', names)
        self.assertIn('dim_cd', names)
        self.assertIn('dim_transportadora', names)

    def test_csv_embutido_corresponde_ao_csv_versionado(self):
        s = (MODEL/'tables'/'fato_entregas.tmdl').read_text(encoding='utf-8')
        part = s[s.index('Text.Combine({'):s.index('}, ""),')]
        encoded=''.join(re.findall(r'"([A-Za-z0-9+/=]{20,})"', part))
        self.assertTrue(encoded)
        original = gzip.decompress(base64.b64decode(encoded))
        self.assertEqual(original,(ROOT/'data'/'lastmile_sintetico.csv').read_bytes())

    def test_m_embutido_nao_ultrapassa_limite_de_profundidade(self):
        s = (MODEL/'tables'/'fato_entregas.tmdl').read_text(encoding='utf-8')
        blob=s[s.index('BinarioEmbutido ='):s.index('FonteBinaria =')]
        self.assertIn('Text.Combine({', blob)
        self.assertNotIn('" &', blob)
        partes = re.findall(r'"([A-Za-z0-9+/=]{20,})"', blob)
        self.assertGreater(len(partes),1)
        self.assertLess(len(partes),100)
        self.assertTrue(all(len(p)<=8192 for p in partes))

    def test_fontes_parametrizadas(self):
        params = (MODEL/'expressions.tmdl').read_text()
        for k in ('ModoFonte','CaminhoCSV','ServidorSQL','BancoSQL'):
            self.assertIn('expression '+k,params)
        self.assertIn('"Embutido"',params)
        fact = (MODEL/'tables'/'fato_entregas.tmdl').read_text()
        self.assertIn('if ModoFonte = "CSV"',fact)
        self.assertIn('if ModoFonte = "SQL"',fact)
        self.assertNotIn('Sql.Database("localhost',fact)

    def test_visuais_json_e_referencias_validas(self):
        root = ROOT/'powerbi'/'projetogit.Report'/'definition'
        files = list(root.glob('pages/*/visuals/*/visual.json'))
        self.assertGreater(len(files),25)
        for f in files:
            d=json.loads(f.read_text())
            self.assertIn('visual',d)
        self.assertFalse(list((ROOT/'powerbi').rglob('.pbi')))

    def test_relacionamentos(self):
        rels=(MODEL/'relationships.tmdl').read_text()
        self.assertEqual(rels.count('relationship '),4)
        self.assertEqual(rels.count('isActive: false'),1)
        self.assertIn('fato_entregas.data_coleta_dia',rels)
        self.assertIn('fato_entregas.data_entrega_dia',rels)

if __name__=='__main__':
    unittest.main()
