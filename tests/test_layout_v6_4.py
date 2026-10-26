import json, unittest, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'powerbi/projetogit.Report/definition/pages/ec4814b076a92d35c8f2/visuals'
MODEL=ROOT/'powerbi/projetogit.SemanticModel/definition/tables/%2A Medidas.tmdl'

class TestTransportVisualV64(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views={p.parent.name:json.loads(p.read_text()) for p in BASE.glob('*/visual.json')}

    def test_four_kpis_plus_two_charts(self):
        v=self.views
        self.assertEqual(sum(d['visual']['visualType']=='lineChart' for d in v.values()),1)
        self.assertEqual(sum(d['visual']['visualType']=='clusteredBarChart' for d in v.values()),1)
        for n in ('lm_transport_trend','lm_transport_rank'):
            self.assertIn(n,v)
        for n in ('147960280d932f47b248','98b51ca915dd844c21a7','975b1be60f12665acff4','27a8a5047e920b896514'):
            self.assertEqual(v[n]['position']['y'],145)

    def test_comparative_table(self):
        m=self.views['lm_matriz_priorizacao']
        self.assertEqual(len(m['visual']['query']['queryState']['Values']['projections']),7)
        self.assertEqual(m['visual']['query']['sortDefinition']['sort'][0]['direction'],'Ascending')
        self.assertLessEqual(m['position']['height'],260)
        self.assertGreaterEqual(m['position']['y'],600)
        self.assertLessEqual(m['position']['y']+m['position']['height'],870)

    def test_three_insights_measures_and_space(self):
        v=self.views
        metrics=['Destaque Menor Pontualidade %','Destaque Pendentes Vencidos','Destaque Tentativas Extras']
        for i,m in enumerate(metrics,1):
            val=v[f'lm_alert_number_{i}']
            self.assertEqual(val['visual']['query']['queryState']['Data']['projections'][0]['field']['Measure']['Property'],m)
            self.assertLessEqual(val['position']['y']+val['position']['height'],1024)
            self.assertEqual(v[f'lm_alert_{i}']['visual']['visualType'],'shape')
        t=MODEL.read_text()
        for m in metrics:
            self.assertIn("measure '"+m+"'",t)
        self.assertIn("measure 'Atraso Médio Exibição'",t)

    def test_layout_not_clipped_and_nav_preserved(self):
        tabs=[]
        for obj in self.views.values():
            x=obj['position']['x']; y=obj['position']['y'];width=obj['position']['width'];height=obj['position']['height']
            self.assertGreaterEqual(x,0);self.assertGreaterEqual(y,0)
            self.assertLessEqual(x+width,1920)
            self.assertLessEqual(y+height,1080)
            tabs.append(obj['position']['tabOrder'])
        self.assertEqual(len(set(tabs)),len(tabs))
        slicers=[k for k in self.views if k.startswith('lm_filtro_')]
        self.assertEqual(len(slicers),3)

    def test_no_unverified_deltas_in_kpis(self):
        for obj in self.views.values():
            if obj['visual']['visualType']=='textbox':
                text=obj['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]['value']
                self.assertNotIn('vs. período anterior',text)

if __name__=='__main__':unittest.main()
