"""Regression tests for the accessible, synced navigation introduced in v6."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REP=ROOT/'powerbi'/'projetogit.Report'/'definition'
PAGES=['cd3f1f43335c0ced6755','ec4814b076a92d35c8f2']
FIELDS={
 'lm_filtro_data':('dim_calendario','Date','Between','lastmile_periodo_v6'),
 'lm_filtro_cd':('dim_cd','cd','Dropdown','lastmile_cd_v6'),
 'lm_filtro_transp':('dim_transportadora','transportadora','Dropdown','lastmile_transportadora_v6'),
}

class TestUXv6(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pages=[]
  for pg in PAGES:
   folder=REP/'pages'/pg/'visuals'
   cls.pages.append({v.parent.name:json.loads(v.read_text(encoding='utf-8')) for v in folder.glob('*/visual.json')})

 def test_native_slicers_synced_across_pages(self):
  for vv in self.pages:
   for name,(tab,col,mode,group) in FIELDS.items():
    v=vv[name]
    self.assertEqual(v['visual']['visualType'],'slicer')
    self.assertEqual(v['visual']['syncGroup']['groupName'],group)
    self.assertTrue(v['visual']['syncGroup']['filterChanges'])
    projection=v['visual']['query']['queryState']['Values']['projections'][0]
    self.assertEqual(projection['field']['Column']['Expression']['SourceRef']['Entity'],tab)
    self.assertEqual(projection['field']['Column']['Property'],col)
    self.assertEqual(v['visual']['objects']['data'][0]['properties']['mode']['expr']['Literal']['Value'],"'"+mode+"'")
    self.assertGreaterEqual(v['position']['height'],92)

 def test_navigation_targets_pages(self):
  for vv in self.pages:
   links=[v for v in vv.values() if v['visual']['visualType']=='actionButton']
   self.assertEqual(len(links),3)
   targets=set()
   for v in links:
    props=v['visual']['visualContainerObjects']['visualLink'][0]['properties']
    action=props['type']['expr']['Literal']['Value']
    if action=="'PageNavigation'":
     targets.add(props['navigationSection']['expr']['Literal']['Value'].strip("'"))
    else:
     self.assertEqual(action,"'ClearAllSlicers'")
   self.assertEqual(targets,set(PAGES))

 def test_no_overlapping_old_chart_and_matrix(self):
  self.assertNotIn('5b9285bac54e1f0b7a46',self.pages[0])
  matrix=self.pages[1]['lm_matriz_priorizacao']
  self.assertEqual(matrix['visual']['visualType'],'tableEx')
  self.assertEqual(len(matrix['visual']['query']['queryState']['Values']['projections']),7)
  self.assertEqual(matrix['visual']['query']['sortDefinition']['sort'][0]['direction'],'Ascending')
  self.assertNotIn('465e2cd40f4401f1322d',self.pages[1])

 def test_presentation_canvas_and_unique_taborder(self):
  for vv in self.pages:
   tabs=[]
   for v in vv.values():
    p=v['position']
    self.assertGreaterEqual(p['x'],-0.001)
    self.assertGreaterEqual(p['y'],-0.001)
    self.assertLessEqual(p['x']+p['width'],1921)
    self.assertLessEqual(p['y']+p['height'],1081)
    self.assertIn('tabOrder',p)
    tabs.append(p['tabOrder'])
   # Decorative background/text may still have a dedicated order; names are unique per page.
   self.assertEqual(len(tabs),len(set(tabs)))

 def test_calendar_trend_uses_same_dimension_as_slicer(self):
  trend=self.pages[0]['eadf52930990a3d5d807']
  col=trend['visual']['query']['queryState']['Category']['projections'][0]['field']['Column']
  self.assertEqual(col['Expression']['SourceRef']['Entity'],'dim_calendario')
  self.assertEqual(col['Property'],'MesAno')
  self.assertIn('sortByColumn: AnoMes',(ROOT/'powerbi/projetogit.SemanticModel/definition/tables/dim_calendario.tmdl').read_text())

if __name__=='__main__':unittest.main()
