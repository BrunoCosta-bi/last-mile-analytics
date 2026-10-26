import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REP=ROOT/'powerbi'/'projetogit.Report'/'definition'
PAGES=['cd3f1f43335c0ced6755','ec4814b076a92d35c8f2']
class TestVisualV62(unittest.TestCase):
    def v(self,p,n):return json.loads((REP/'pages'/p/'visuals'/n/'visual.json').read_text(encoding='utf8'))
    def test_header_contrast(self):
        for p,n in zip(PAGES,['187db57c5b9cbd2b01cf','73264360161f6702729a']):
            v=self.v(p,n); run=v['visual']['objects']['general'][0]['properties']['paragraphs'][0]['textRuns'][0]
            self.assertEqual(run['textStyle']['color'],'#FFFFFF')
            if p == PAGES[0]:
                self.assertIn('Análise de entregas',run['value'])
            else:
                self.assertIn('Desempenho por transportadora',run['value'])
    def test_sidebar_meets_content(self):
        for p in PAGES:
            rail=self.v(p,'lm_rail_bg');self.assertEqual(rail['position']['width'],360)
    def test_nav_rounded_and_filters_synced(self):
        for p,navs in zip(PAGES,[('02a2c89b89b5552211ae','37fe0d114c114e1a7c6c'),('77dee70f455ee1f6b8d7','06b1c578cc3933d20ecb')]):
            for n in navs:
                v=self.v(p,n);self.assertEqual(v['visual']['objects']['shape'][0]['properties']['tileShape']['expr']['Literal']['Value'],"'rectangleRounded'")
            for n in ['lm_filtro_data','lm_filtro_transp','lm_filtro_cd']:
                v=self.v(p,n); self.assertTrue(v['visual']['syncGroup']['filterChanges'])
                self.assertGreaterEqual(int(v['visual']['visualContainerObjects']['border'][0]['properties']['radius']['expr']['Literal']['Value'].removesuffix('D')),14)
    def test_trend_blank_filter(self):
        v=self.v(PAGES[0],'eadf52930990a3d5d807')
        self.assertTrue(any(f.get('name')=='e596f2683a204e6b18f4' for f in v['filterConfig']['filters']))
        self.assertEqual(v['visual']['objects']['legend'][0]['properties']['show']['expr']['Literal']['Value'],'false')
    def test_no_duplicate_tab_order(self):
        for p in PAGES:
            vv=[json.loads(f.read_text(encoding='utf8')) for f in (REP/'pages'/p/'visuals').glob('*/visual.json')]
            orders=[v['position']['tabOrder'] for v in vv]
            self.assertEqual(len(orders),len(set(orders)))
if __name__=='__main__':unittest.main()
