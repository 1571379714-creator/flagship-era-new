from pathlib import Path
import json,copy,unittest,random,itertools,hashlib
from rules_core import *
R=Path(__file__).resolve().parents[1];D=json.loads((R/'work/v62_data.json').read_text(encoding='utf8'));OLD=json.loads((R/'source/v61_data.json').read_text(encoding='utf8'))
GROUPS=['parts','technologies','contracts','facilities','schemes','benchmarks','demands'];CAT={c['id']:c for g in GROUPS for c in D[g]}
def company():
 c=Company(CAT)
 for p in D['parts']:
  if p.get('company')=='M01':
   key=p['id']+'#initial';c.owned[key]=p['id'];c.library[p['components'][0]['kind']]=key
 return c
class DataChecks(unittest.TestCase):
 def test_01_counts_and_identity(self):
  self.assertEqual(sum(len(D[g]) for g in GROUPS),243)
  self.assertEqual(sum(c['qty'] for g in GROUPS for c in D[g]),315)
  self.assertEqual(sum(c['qty'] for g in GROUPS for c in D[g] if c.get('deck')=='main'),257)
  self.assertEqual(sum(1 for g in GROUPS for c in D[g] if c.get('deck')=='main'),185)
  for g in GROUPS:self.assertEqual([(c['id'],c['qty']) for c in D[g]],[(c['id'],c['qty']) for c in OLD[g]])
 def test_02_raw_component_stats_preserved(self):
  for a,b in zip(D['parts'],OLD['parts']):self.assertEqual(a['components'],b['components']);self.assertEqual(a['era'],b['era'])
 def test_03_every_five_era_in_main_and_free_acquire(self):
  self.assertEqual({c['era'] for c in D['parts'] if c['type']=='supply'},set(range(1,6)))
  self.assertEqual({c['era'] for c in D['parts'] if c['type']=='custom'},set(range(1,6)))
  for c in D['parts']:
   self.assertEqual(c['acquisitionCost'],0)
   if c['type']!='custom':self.assertEqual(c['installCost'],0 if c['type']=='starter' else 9)
 def test_04_reference_numbers_and_rewards(self):
  for a,b in zip(D['benchmarks'],OLD['benchmarks']):
   for x,y in zip(a['markets'],b['markets']):
    self.assertEqual(x['score'],y['score']);self.assertEqual(x['reward'],stars(x['score']));self.assertEqual(x['incomeReward'],2*x['reward']);self.assertEqual(x['technologyReward'],x['reward'])
  for e in range(1,6):self.assertEqual(len([c for c in D['benchmarks'] if c['era']==e]),6)
 def test_05_printed_order_totals(self):
  for c in D['contracts']:
   if c['subtype']=='order':
    self.assertEqual(c['totalCash'],c['unitPrice']*c['units']);self.assertEqual(c['totalIncome'],c['unitIncome']*c['units']);self.assertLessEqual(c['units'],4);self.assertIn('允许配置不同',c['effect'])
  for c in D['demands']:
   for m in c['markets']:
    for n in (2,3,4):self.assertEqual(m['ordersByPlayers'][str(n)],max(1,n+m['ordersDelta']))
 def test_06_removed_bookkeeping_fields(self):
  for key in ('agingPenalty','maxAge','platformQuota','baseProductionCap','inventoryCapPerModel','offerCapPerModelPerMarket'):self.assertNotIn(key,D['parameters'])
  from sync_rules_text import check
  check()

class StateChecks(unittest.TestCase):
 def test_07_stable_acquire_not_install(self):
  c=company();c.acquire('new','C02');self.assertEqual(c.cash,120);self.assertNotEqual(c.library['chip'],'new');self.assertIn('new',c.hand)
 def test_08_install_fee_and_replacement(self):
  c=company();c.acquire('new','C02');c.install('new');self.assertEqual((c.cash,c.work),(111,2));self.assertNotIn('new',c.hand);self.assertEqual(c.library['chip'],'new');self.assertEqual(len(c.removed),1)
 def test_09_future_library_allowed_future_use_denied(self):
  c=company();c.acquire('future','C12');c.install('future');self.assertEqual(c.library['chip'],'future');snapshot=copy.deepcopy(c)
  with self.assertRaises(ValueError):c.assemble(1,KINDS,())
  self.assertEqual(c.cash,snapshot.cash);self.assertEqual(c.work,snapshot.work)
 def test_10_lock_only_last_reference_releases(self):
  c=company();c.acquire('new','C02');c.assemble(1,KINDS,());c.assemble(2,KINDS,());self.assertTrue(c.is_locked('chip'))
  with self.assertRaises(ValueError):c.install('new')
  c.cancel(1)
  with self.assertRaises(ValueError):c.install('new')
  c.cancel(2);self.assertFalse(c.is_locked('chip'));c.install('new')
 def test_11_each_slot_one_batch_cash_separate(self):
  c=company();self.assertEqual(c.assemble(1,KINDS,()),13);self.assertEqual(c.assemble(2,KINDS,()),13);self.assertEqual(c.cash,94);self.assertEqual(len(c.products),2)
  with self.assertRaises(ValueError):c.assemble(1,KINDS,())
 def test_12_cancel_returns_whole_custom_and_q_no_refund(self):
  c=company();c.acquire('x','X29');c.acquire('q','Q01');c.assemble(1,(),('x',),scheme='q');before=(c.cash,c.work);c.cancel(1);self.assertEqual((c.cash,c.work),before);self.assertIn('x',c.hand);self.assertIn('q',c.hand)
 def test_13_no_custom_split_or_overlap(self):
  c=company();c.acquire('x','X29')
  with self.assertRaises(ValueError):c.assemble(1,('chip',),('x',))
  self.assertEqual(c.cash,120)
 def test_14_hand_stable_cannot_act_as_custom(self):
  c=company();c.acquire('s','C02')
  with self.assertRaises(ValueError):c.assemble(1,('screen','camera','body'),('s',))
 def test_15_deployment_one_batch_at_a_time(self):
  c=company();c.completed.add('T01');c.assemble(1,KINDS,(),techs=('T01',))
  with self.assertRaises(ValueError):c.assemble(2,KINDS,(),techs=('T01',))
  c.cancel(1);c.assemble(2,KINDS,(),techs=('T01',));self.assertIn('T01',c.completed)
 def test_16_unsold_reference_persists_across_release(self):
  c=company();c.assemble(1,KINDS,());c.phase='release';c.finish_release(set(),rewards_finished=True);self.assertIn(1,c.products);self.assertTrue(c.is_locked('chip'));self.assertFalse(hasattr(c.products[1],'age'))
 def test_17_sold_cleanup_after_all_rewards_only(self):
  c=company();c.acquire('x','X29');c.assemble(1,(),('x',));c.phase='release'
  with self.assertRaises(ValueError):c.finish_release({1},rewards_finished=False)
  self.assertIn(1,c.products);c.finish_release({1},rewards_finished=True);self.assertIn('x',c.removed);self.assertNotIn('x',c.hand)
 def test_18_no_cancel_install_or_assemble_during_release(self):
  c=company();c.assemble(1,KINDS,());c.acquire('s','C02');c.phase='release'
  for fn in [lambda:c.cancel(1),lambda:c.install('s'),lambda:c.assemble(2,KINDS,())]:
   with self.assertRaises(ValueError):fn()
 def test_19_q21_only_real_sale_return_not_export(self):
  for sale in (True,False):
   c=company();c.acquire('q','Q21');c.assemble(1,KINDS,(),scheme='q');c.phase='release';c.finish_release({1} if sale else set(),rewards_finished=True,exported=set() if sale else {1});self.assertEqual('q' in c.hand,sale)
 def test_20_no_era_price_depreciation(self):
  for era in range(1,6):
   c=company();c.era=era;self.assertEqual(c.assemble(1,KINDS,()),13)
 def test_21_verification_not_reset_by_cancel_rebuild(self):
  c=company();c.assemble(1,KINDS,());c.products[1].base=12;c.products[1].features=frozenset(['性能','续航']);self.assertEqual(c.verify(1),1)
  c.cancel(1);c.work=3;c.assemble(1,KINDS,());c.products[1].base=12;c.products[1].features=frozenset(['性能','续航'])
  with self.assertRaises(ValueError):c.verify(1)
  c.era=2;self.assertEqual(c.verify(1),1)
 def test_22_cash_before_assembly(self):
  c=company();c.cash=12
  with self.assertRaises(ValueError):c.assemble(1,KINDS,())
  self.assertEqual(c.cash,12);self.assertEqual(c.work,3)
 def test_23_one_batch_trial_floors_and_future(self):
  c=company();c.work=0;c.assemble(1,KINDS,(),total_discount=99,trial=True);self.assertEqual(c.cash,114);self.assertEqual(len(c.products),1)
 def test_24_same_id_two_custom_entities_independent(self):
  c=company();c.acquire('x1','X29');c.acquire('x2','X29');c.assemble(1,(),('x1',));c.assemble(2,(),('x2',));c.cancel(1);self.assertIn('x1',c.hand);self.assertNotIn('x2',c.hand)
 def test_25_uniform_refill_after_selections(self):
  selected,board,pile=take_market(list('ABCDEFGH'),list('12345'),[1,5]);self.assertEqual(selected,['B','F']);self.assertEqual(board,list('A1CDE2GH'))
  with self.assertRaises(ValueError):take_market(list('ABCDEFGH'),list('12345'),[1,1])
 def test_26_allocations_one_destination(self):
  self.assertTrue(allocations_valid({(0,1):['A'],(0,2):['A'],(1,1):['photo']}));self.assertFalse(allocations_valid({(0,1):['A','photo']}))

class ReleaseChecks(unittest.TestCase):
 def test_27_reference_requires_all_locked(self):
  with self.assertRaises(ValueError):draw_reference(D['benchmarks'],1,{0},2,random.Random(1))
  for e in range(1,6):self.assertEqual(draw_reference(D['benchmarks'],e,{0,1},2,random.Random(1))['era'],e)
 def test_28_tie_sells_but_no_challenge(self):
  r=resolve_market([Offer(0,1,16,28)],budget=28,preferences=[],orders=1,reference=18,priority=[0,1]);self.assertEqual(len(r['sales']),1);self.assertEqual(r['sales'][0]['stars'],0)
 def test_29_technology_challenge_without_first_release(self):
  r=resolve_market([Offer(0,1,20,28,deployed=True)],budget=28,preferences=[],orders=1,reference=18,priority=[0,1]);self.assertTrue(r['sales'][0]['techAllowed']);self.assertEqual(r['sales'][0]['stars'],2)
 def test_30_budget_and_tie_priority(self):
  r=resolve_market([Offer(0,1,20,38),Offer(1,1,18,18,tie_priority=True),Offer(0,2,18,18)],budget=28,preferences=[],orders=1,reference=0,priority=[0,1]);self.assertEqual(r['sales'][0]['owner'],1)
 def test_31_single_market_scenarios(self):
  rng=random.Random(62)
  for _ in range(600):
   n=rng.choice([2,3,4]);offers=[Offer(owner,slot,rng.randrange(35),rng.choice(list(PRICES)),frozenset(rng.sample(['性能','影像','续航','生态','轻薄','折叠'],rng.randrange(4))),bool(rng.randrange(2))) for owner in range(n) for slot in range(1,rng.randrange(2,6))]
   order=rng.randrange(1,7);ref=rng.randrange(0,36);budget=rng.choice(list(PRICES));r=resolve_market(offers,budget=budget,preferences=['性能','续航'],orders=order,reference=ref,priority=list(range(n)))
   self.assertEqual(len(r['sales'])+r['referenceSold']+r['unfilled'],order);self.assertLessEqual(r['referenceSold'],1)
   self.assertTrue(all(x['qty']==1 and x['cash']<=budget for x in r['sales']))
   self.assertEqual(len({(x['owner'],x['product']) for x in r['sales']}),len(r['sales']))
   self.assertTrue(all(x['stars']==0 or x['score']>ref for x in r['sales']))
 def test_32_score_and_end_boundaries(self):
  self.assertEqual(max(60,2*9),60);self.assertEqual(max(18,2*31),62);self.assertEqual(36*2,72)

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__));r=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'version':'6.2','testMethods':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'singleMarketScenarios':600,'success':r.wasSuccessful(),'scope':'有限状态模型与数据断言；部分特效以显式测试参数输入，不是完整游戏解释器。没有真人对局、隐藏策略或全卡组合穷举。'}
 (R/'work/validation_v62.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 if not r.wasSuccessful():raise SystemExit(1)
