"""6.9新增名录、冻结字段与特色条件测试。synthetic配置仅用于隔离条件，不称为实局。"""
from pathlib import Path
from collections import Counter
import unittest,json,copy,re
from component_engine import evaluate,KINDS
from expansion_engine import manufacturing_quote
R=Path(__file__).resolve().parents[1];D=json.loads((R/'work/v69_data.json').read_text());B=json.loads((R/'source/v68_data.json').read_text());P={c['id']:c for c in D['parts']};BP={c['id']:c for c in B['parts']};T={c['id']:c for c in D['technologies']}
RO=D['chipRoster'];EC={'C112','C117','X102','X113','X114','X115','X120','X123','X124','X126','X128','X135','X137','X138','X144','X149','X150','X151'}
def strip(s):return re.sub(r'〔.*?〕','',s)
def isolated(cid,techs=(),price=28,**edits):
 c=copy.deepcopy(P[cid]);present={a['kind']for a in c['components']};cards=[c]
 for k in KINDS:
  if k not in present:cards.append({'id':'synthetic_'+k,'type':'supply','era':c['era'],'integratedSlots':0,'rules':[],'components':[{'kind':k,'name':'条件测试夹具','batchCost':1,'spec':8,'power':50 if k=='body' else 2,'mark':'影像'if k=='screen'else'续航','form':'slab'}]})
 for item in cards:
  for a in item['components']:
   for key,value in edits.items():
    k,field=key.split('_',1)
    if a['kind']==k:a[field]=value
  if item is not c:item['rules']=[]
 # Supply enough test power and align shapes; isolate rule effect from unrelated shape/power failures.
 comp={a['kind']:a for x in cards for a in x['components']};comp['body']['power']=50;comp['body']['form']=comp['screen']['form']
 out=evaluate(cards,techs,T,era=5,price=price)
 baseline=copy.deepcopy(cards);baseline[0]['rules']=[];baseline[0].pop('chipEffect',None)
 bare=evaluate(baseline,techs,T,era=5,price=price)
 return out,bare,cards
class Roster69(unittest.TestCase):
 def test_50_unique_real_positions(self):
  xs=[a['name']for c in D['parts']if c['type']!='starter'for a in c['components']if a['kind']=='chip'];self.assertEqual(len(xs),50);self.assertEqual(len(set(map(strip,xs))),50)
 def test_exact_family_counts(self):self.assertEqual(Counter(x['family']for x in RO),{'Qualcomm':12,'MediaTek':9,'Apple':10,'Kirin':7,'XRing':2,'Exynos':6,'Google':2,'UNISOC':2})
 def test_exact_snapdragon_set(self):self.assertEqual({strip(x['name'])for x in RO if x['family']=='Qualcomm'},{'骁龙'+x for x in ['835','845','855','865','888','8 Gen 1','8+ Gen 1','8 Gen 2','8 Gen 3','8 Elite','8 Elite Gen 5','8EE6']})
 def test_exact_mediatek_nine(self):self.assertEqual({x['name']for x in RO if x['family']=='MediaTek'},{'Helio X30',*['天玑'+x for x in ['1000','1200','9000','9200','9300','9400','9500','9600 Pro']]})
 def test_apple_complete_names(self):self.assertEqual({x['name']for x in RO if x['family']=='Apple'},{*['A'+str(i)+' Bionic'for i in range(11,17)],*['A'+str(i)+' Pro'for i in range(17,21)]})
 def test_kirin_exact_family_set(self):self.assertEqual({x['name']for x in RO if x['family']=='Kirin'},{'麒麟'+x for x in ['970','980','990','9000','9020','9030','9050']})
 def test_stable_4_custom_6_each_era(self):
  for e in range(1,6):self.assertEqual(Counter(x['type']for x in RO if x['era']==e),{'supply':4,'custom':6})
 def test_kit_coverage_preserved(self):
  for c in D['parts']:self.assertEqual([a['kind']for a in c['components']],[a['kind']for a in BP[c['id']]['components']])
 def test_all_nonchip_rows_exactly_frozen(self):
  for c in D['parts']:
   for a,b in zip(c['components'],BP[c['id']]['components']):
    if a['kind']!='chip' or c['type']=='starter':self.assertEqual(a,b)
 def test_110_nonchip_or_starter_cards_frozen(self):
  changed={x['card']for x in RO};count=0
  for c in D['parts']:
   if c['id']not in changed:self.assertEqual(c,BP[c['id']]);count+=1
  self.assertEqual(count,110)
 def test_all_nonpart_categories_frozen(self):
  for k in ('technologies','contracts','facilities','schemes','benchmarks','demands'):self.assertEqual(D[k],B[k])
 def test_mechanics_and_rates_frozen(self):
  for k in ('parameters','supplierRules','researchModes','expansionRules'):self.assertEqual(D[k],B[k])
 def test_only_seven_numeric_chip_rows_changed(self):
  ids=set()
  for x in RO:
   a=next(v for v in P[x['card']]['components']if v['kind']=='chip');b=next(v for v in BP[x['card']]['components']if v['kind']=='chip')
   if any(a[k]!=b[k]for k in ('spec','power','batchCost')):ids.add(x['card'])
  self.assertEqual(ids,{'X102','X115','X120','X124','C112','X135','X144'})
 def test_only_t760_install_revalued(self):
  ids={c['id']for c in D['parts']if c['type']=='supply'and(c['installCost'],c['installPartnerCost'])!=(BP[c['id']]['installCost'],BP[c['id']]['installPartnerCost'])};self.assertEqual(ids,{'C112'})
 def test_exact_18_effects_changed(self):self.assertEqual({x['card']for x in RO if P[x['card']]['effect']!=BP[x['card']]['effect']},EC)
 def test_12_name_changes(self):self.assertEqual(sum(P[x['card']]['name']!=BP[x['card']]['name']for x in RO),12)
 def test_game_reality_gap_marks_present(self):
  for id in ('C112','C107','X160','X152','X163'):self.assertTrue(P[id].get('cardEvidenceNote'))
 def test_no_wrong_old_source_for_new_name(self):
  for s in D['chipSources']:self.assertEqual(s['name'],next(a for a in P[s['cardId']]['components']if a['kind']=='chip')['name'])
 def test_t760_market_entry_does_not_create_features(self):
  a,b,_=isolated('C112',price=28);self.assertIn('office',a['permits']);self.assertEqual(a['features'],b['features']);c,_,_=isolated('C112',price=38);self.assertNotIn('office',c['permits'])
 def test_sc9863A_low_config_only(self):
  a,b,_=isolated('X102',screen_spec=4,camera_spec=4);self.assertEqual(b['cost']-a['cost'],3);c,e,_=isolated('X102',screen_spec=5,camera_spec=4);self.assertEqual(c['cost'],e['cost'])
 def test_855_compatibility_requires_imaging(self):
  a,_,_=isolated('X115',['T02']);self.assertEqual(a['bonuses']['photo'],2)
  cards=isolated('X115',['T02'])[2];next(x for x in cards if x['id']=='synthetic_camera')['rules']=[{'op':'requireChip','value':9,'when':[]}]
  evaluate(cards,['T02'],T)
  with self.assertRaises(ValueError):evaluate(cards,[],T)
 def test_1000_screen_power_condition(self):
  a,b,_=isolated('X120',screen_power=2);self.assertEqual(b['load']-a['load'],1);a,b,_=isolated('X120',screen_power=3);self.assertEqual(a['load'],b['load'])
 def test_9820_requires_camera_and_system(self):
  a,b,_=isolated('X124',['T06'],camera_spec=5);self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],3)
  for techs,cam in [((),5),(('T06',),4)]:
   a,b,_=isolated('X124',techs,camera_spec=cam);self.assertEqual(a['bonuses']['photo'],b['bonuses']['photo'])
 def test_888_thermal_extra_not_eco(self):
  a,b,_=isolated('X128',camera_spec=6);self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],2);self.assertEqual(a['features'],b['features'])
  a,b,_=isolated('X128',['T01'],camera_spec=6);self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],3)
 def test_9200_needs_real_display_and_platform(self):
  a,b,_=isolated('X135',['T07'],screen_spec=7);self.assertEqual(a['bonuses']['gaming']-b['bonuses']['gaming'],4)
  a,b,_=isolated('X135',['T07'],screen_spec=6);self.assertEqual(a['bonuses']['gaming'],b['bonuses']['gaming'])
 def test_9020_system_camera_joint_condition(self):
  a,b,_=isolated('X144',['T06'],camera_spec=7);self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],3)
  a,b,_=isolated('X144',camera_spec=7);self.assertEqual(a['bonuses']['photo'],b['bonuses']['photo'])
 def test_9030_display_and_system_not_automatic(self):
  a,b,_=isolated('C117',['T06'],screen_spec=8);self.assertEqual(a['bonuses']['office']-b['bonuses']['office'],3)
  a,b,_=isolated('C117',['T06'],screen_spec=7);self.assertEqual(a['bonuses']['office'],b['bonuses']['office'])
 def test_A11_grants_feature_not_printed_spec(self):
  a,b,c=isolated('X113',camera_spec=5);self.assertIn('影像',a['features']);self.assertNotIn('影像',b['features']);self.assertEqual(next(v['spec']for x in c for v in x['components']if v['kind']=='camera'),5)
 def test_A12_requires_imaging_not_any_research(self):
  a,b,_=isolated('X114',['T02']);self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],3)
  a,b,_=isolated('X114',['T06']);self.assertEqual(a['bonuses']['photo'],b['bonuses']['photo'])
 def test_A13_accepts_two_alternative_domains(self):
  for ts in [('T02',),('T06',)]:
   a,b,_=isolated('X123',ts,camera_spec=5);self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],3)
  a,b,_=isolated('X123',['T06'],camera_spec=4);self.assertEqual(a['bonuses']['photo'],b['bonuses']['photo'])
 def test_A14_efficiency_only_system(self):
  a,b,_=isolated('X126',['T06']);self.assertEqual(b['load']-a['load'],1)
  a,b,_=isolated('X126',['T02']);self.assertEqual(a['load'],b['load'])
 def test_A15_monitoring_mark_and_system(self):
  a,b,_=isolated('X137',['T06'],screen_mark='影像');self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],4)
  a,b,_=isolated('X137',['T06'],screen_mark='性能');self.assertEqual(a['bonuses']['photo'],b['bonuses']['photo'])
 def test_A16_display_power_floor(self):
  a,b,_=isolated('X138',['T25'],screen_power=4);self.assertEqual(b['load']-a['load'],1)
  a,b,_=isolated('X138',['T25'],screen_power=0);self.assertEqual(a['load'],b['load'])
 def test_A17_platform_required(self):
  a,b,_=isolated('X149',['T07'],screen_spec=7);self.assertEqual(a['bonuses']['gaming']-b['bonuses']['gaming'],4)
  a,b,_=isolated('X149',screen_spec=7);self.assertEqual(a['bonuses']['gaming'],b['bonuses']['gaming'])
 def test_A18_premium_price_required(self):
  for price in (38,48):
   a,b,_=isolated('X150',['T02'],price=price);self.assertEqual(a['bonuses']['photo']-b['bonuses']['photo'],4)
  a,b,_=isolated('X150',['T02'],price=28);self.assertEqual(a['bonuses']['photo'],b['bonuses']['photo'])
 def test_A19_neural_domains_not_imaging(self):
  for ts in [('T07',),('T06',)]:
   a,b,_=isolated('X151',ts,screen_spec=8);self.assertEqual(a['bonuses']['gaming']-b['bonuses']['gaming'],3)
  a,b,_=isolated('X151',['T02'],screen_spec=8);self.assertEqual(a['bonuses']['gaming'],b['bonuses']['gaming'])
 def test_A20_integrated_cost_and_condition_preserved(self):
  self.assertEqual(P['X164']['integratedSlots'],BP['X164']['integratedSlots']);self.assertEqual(P['X164']['rules'],BP['X164']['rules']);self.assertEqual(T['T21'],next(t for t in B['technologies']if t['id']=='T21'))
 def test_expansion_pays_revised_chip_cost_not_old(self):
  for cid in ('X102','C112','X124'):
   _,_,cards=isolated(cid)
   q=manufacturing_quote(D,cards)
   self.assertEqual(q['manufacturing'],evaluate(cards,tech_catalog=T)['cost'])
 def test_no_new_physical_random_pile_or_tokens(self):
  for key in ('physicalProtocol','deckStructure','lifecycle'):self.assertEqual(D[key],B[key])
if __name__=='__main__':unittest.main(verbosity=2)
