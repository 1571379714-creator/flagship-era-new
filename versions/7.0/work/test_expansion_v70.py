"""已确认扩产细则的定向测试；包括多市场、资金流、同分和卡牌批次边界。"""
import json, random, unittest, copy
from collections import Counter
from pathlib import Path
from expansion_engine import *
R=Path(__file__).resolve().parents[1];D=json.loads((R/'work/v70_data.json').read_text())
PART={c['id']:c for c in D['parts']};T={c['id']:c for c in D['technologies']}
def specs(orders=3,reference=20):return {m:MarketSpec(orders,reference) for m in MARKETS}
def flat(result):return [s for m in result['markets'].values() for s in m['sales']]
def run(ps,orders=3,ref=20,decisions=None,cash=None,priority=(0,1),markets=None,final=False):
 return ExpansionRelease(ps,markets or specs(orders,ref),cash or dict.fromkeys(priority,100),priority).run(decisions if decisions is not None else {(p.owner,p.slot):True for p in ps},final_release=final)
class ExpansionTests(unittest.TestCase):
 def test_confirmed_displacement(self):
  r=run([LockedProduct(0,1,'mass',28),LockedProduct(1,1,'mass',25),LockedProduct(1,2,'mass',22)])
  self.assertEqual([(s['owner'],s['slot'],s['copy']) for s in r['markets']['mass']['sales']],[(0,1,False),(0,1,True),(1,1,False)])
  self.assertIn({'market':'mass','owner':1,'slot':2,'status':'displaced'},r['decisions'])
 def test_two_equal_originals_block_copy(self):
  r=run([LockedProduct(0,1,'mass',28),LockedProduct(1,1,'mass',28)],orders=2)
  self.assertFalse(r['expansions']);self.assertEqual([s['owner'] for s in flat(r)],[0,1])
 def test_q16_copy_never_beats_normal_original(self):
  r=run([LockedProduct(0,1,'mass',28,priority_ability=True),LockedProduct(1,1,'mass',28)],orders=2)
  self.assertFalse(r['expansions'])
 def test_q16_inside_original_group(self):
  r=run([LockedProduct(0,1,'mass',28),LockedProduct(1,1,'mass',28,priority_ability=True)],orders=1,decisions={})
  self.assertEqual(flat(r)[0]['owner'],1)
 def test_same_score_copy_beats_reference(self):
  r=run([LockedProduct(0,1,'mass',20)],orders=2,ref=20)
  self.assertEqual(len(flat(r)),2);self.assertFalse(r['markets']['mass']['referenceSold']);self.assertFalse(any(s['strictReferenceWin'] for s in flat(r)))
 def test_lower_original_not_allowed_when_no_initial_order(self):
  r=run([LockedProduct(0,1,'mass',30),LockedProduct(1,1,'mass',10)],orders=1)
  self.assertFalse(any(x['owner']==1 for x in r['expansions']))
 def test_insufficient_cash_no_partial_payment(self):
  p=LockedProduct(0,1,'mass',30,manufacturing=13,royalties=((1,4),));r=run([p],cash={0:16,1:100})
  self.assertEqual(r['cashAfterExpansion'],{0:16,1:100});self.assertEqual(r['bankPaid'],0)
 def test_exact_cash_and_royalty(self):
  p=LockedProduct(0,1,'mass',30,manufacturing=13,royalties=((1,4),));r=run([p],cash={0:17,1:100})
  self.assertEqual(r['cashAfterExpansion'],{0:0,1:104});self.assertEqual(r['bankPaid'],13)
 def test_cannot_use_sales_from_earlier_market(self):
  ps=[LockedProduct(0,1,'mass',30,price=48),LockedProduct(0,2,'gaming',40,manufacturing=13)]
  r=run(ps,cash={0:12,1:100},decisions={(0,1):False,(0,2):True})
  self.assertEqual(r['cashAfterExpansion'][0],12);self.assertFalse(r['expansions'])
 def test_real_royalty_can_finance_later_market(self):
  ps=[LockedProduct(0,1,'mass',30,royalties=((1,4),)),LockedProduct(1,1,'gaming',30)]
  r=run(ps,cash={0:17,1:9});self.assertEqual(len(r['expansions']),2);self.assertEqual(r['cashAfterExpansion'],{0:0,1:0})
 def test_no_sales_paid_even_final_release(self):
  r=run([LockedProduct(0,1,'mass',30,price=48)],final=True)
  self.assertEqual(r['cashAfterExpansion'][0],87);self.assertTrue(r['finalRelease'])
 def test_one_company_across_all_markets(self):
  ps=[LockedProduct(0,i,m,40) for i,m in enumerate(MARKETS,1)]
  r=run(ps);self.assertEqual(len(r['expansions']),1);self.assertEqual(r['expansions'][0]['slot'],1)
 def test_decline_can_save_for_later_product(self):
  ps=[LockedProduct(0,1,'mass',40),LockedProduct(0,2,'photo',40)]
  r=run(ps,decisions={(0,1):False,(0,2):True});self.assertEqual(r['expansions'][0]['slot'],2)
 def test_no_return_to_declined_opportunity(self):
  ps=[LockedProduct(0,1,'mass',40),LockedProduct(0,2,'mass',39)]
  r=run(ps,orders=2,decisions={(0,1):False,(0,2):True});self.assertFalse(r['expansions'])
 def test_multiple_companies_if_orders_sufficient(self):
  r=run([LockedProduct(0,1,'mass',30),LockedProduct(1,1,'mass',25)],orders=4)
  self.assertEqual(len(r['expansions']),2)
 def test_zero_orders(self):
  r=run([LockedProduct(0,1,'mass',30)],orders=0);self.assertFalse(r['expansions'])
 def test_invalid_budget_no_expansion(self):
  ms=specs();ms['mass']=MarketSpec(3,20,18)
  r=run([LockedProduct(0,1,'mass',30,price=48)],markets=ms);self.assertFalse(r['expansions'])
 def test_hold_and_contract_excluded(self):
  r=run([LockedProduct(0,1,'A',30),LockedProduct(0,2,'hold',50)]);self.assertFalse(r['expansions']);self.assertEqual(flat(r),[])
 def test_illegal_product_not_a_candidate(self):
  r=run([LockedProduct(0,1,'mass',99,eligible=False)]);self.assertFalse(r['expansions'])
 def test_four_slots_full_still_expand_no_new_slot(self):
  ps=[LockedProduct(0,i,m,40) for i,m in enumerate(MARKETS,1)];r=run(ps)
  self.assertEqual(len([s for s in flat(r) if s['owner']==0]),5)
  self.assertEqual(r['cleanupOriginalGroups']['0'],[1,2,3,4]);self.assertEqual(len(ps),4)
 def test_copies_do_not_recursively_expand(self):
  r=run([LockedProduct(0,1,'mass',40)],orders=20);self.assertEqual(len(flat(r)),2);self.assertEqual(len(r['decisions']),1)
 def test_cleanup_group_once(self):
  r=run([LockedProduct(0,3,'mass',40)]);self.assertEqual(r['cleanupOriginalGroups'],{'0':[3]})
 def test_cash_model_cannot_run_twice(self):
  session=ExpansionRelease([LockedProduct(0,1,'mass',40)],specs(),{0:100,1:100},(0,1));session.run({(0,1):True})
  with self.assertRaises(ExpansionError):session.run({(0,1):True})
 def test_self_royalty_rejected(self):
  with self.assertRaises(ExpansionError):run([LockedProduct(0,1,'mass',30,royalties=((0,4),))])
 def test_duplicate_product_cross_market_rejected(self):
  with self.assertRaises(ExpansionError):run([LockedProduct(0,1,'mass',30),LockedProduct(0,1,'gaming',30)])
 def test_q15_two_batches_h28_total_two(self):
  r=run([LockedProduct(0,1,'mass',40,price=18)]);s=flat(r);out=retail_card_rewards(s,q15_groups={(0,1)},h28_eligible={(0,1)})[0]
  self.assertEqual(out['cash'],42);self.assertEqual(out['income'],4)
 def test_h28_not_four_times(self):
  s=flat(run([LockedProduct(0,1,'mass',40,price=18),LockedProduct(0,2,'mass',39,price=18)],orders=4))
  out=retail_card_rewards(s,h28_eligible={(0,1),(0,2)})[0];self.assertEqual(out['cash'],60)
 def test_t41_one_conversion_not_double(self):
  r=run([LockedProduct(0,1,'mass',40,price=38)]);out=retail_card_rewards(flat(r),t41_group=(0,1))[0]
  self.assertEqual((out['cash'],out['income'],out['technology']),(76,3,1))
 def test_q21_returns_one_actual_card(self):
  r=run([LockedProduct(0,1,'mass',40)]);self.assertEqual(retail_card_rewards(flat(r),q21_groups={(0,1)})[0]['q21Returns'],1)
 def test_q24_no_duplicate_once_reward(self):
  r=run([LockedProduct(0,1,'mass',40)]);self.assertEqual(retail_card_rewards(flat(r),q24_groups={(0,1)})[0]['q24Income'],1)
 def test_plain_starting_cost_thirteen(self):
  p=[PART['S01'+str(i)] for i in range(1,5)];q=manufacturing_quote(D,p);self.assertEqual(q['manufacturing'],13)
 def test_normal_first_discounts_not_reused(self):
  p=[PART['S01'+str(i)] for i in range(1,5)];q=manufacturing_quote(D,p,active_cards=['U11','H16','H20','U14','T31'])
  self.assertEqual(q['manufacturing'],13)
 def test_persistent_stable_discount_applies(self):
  p=[PART['S01'+str(i)] for i in range(1,5)];self.assertEqual(manufacturing_quote(D,p,active_cards=['U15'])['manufacturing'],11)
 def test_t37_not_self_copy_as_other(self):
  p=[PART['S01'+str(i)] for i in range(1,5)]
  self.assertEqual(manufacturing_quote(D,p,active_cards=['T37'])['manufacturing'],13)
  self.assertEqual(manufacturing_quote(D,p,active_cards=['T37'],other_original_stable_chip=True)['manufacturing'],10)
 def test_scheme_cost_charged_again(self):
  p=[PART['S01'+str(i)] for i in range(1,5)]
  q=manufacturing_quote(D,p,scheme='Q21');self.assertEqual(q['manufacturing'],16)
 def test_expansion_still_uses_current_printed_chip_costs(self):
  before=json.loads((R/'source/v69_data.json').read_text())
  for a,b in zip(before['parts'],D['parts']):
   self.assertEqual(a['id'],b['id']);self.assertEqual(a['qty'],b['qty']);self.assertEqual(a['integratedSlots'],b['integratedSlots'])
   for x,y in zip(a['components'],b['components']):
    if x['kind']!='chip' or a['type']=='starter':self.assertEqual(x,y)
  card=PART['C101'];cards=[card,*[PART['S01'+str(i)]for i in (2,3,4)]]
  q=manufacturing_quote(D,cards)
  self.assertGreaterEqual(q['manufacturing'],6)
 def test_1200_multi_market_scenarios(self):
  rng=random.Random(6501)
  for case in range(1200):
   n=rng.choice([2,3,4]);ps=[]
   for a in range(n):
    for slot in range(1,rng.randint(1,4)+1):
     roy=() if rng.random()<.6 else (((a+1)%n,rng.choice([2,3,4])),)
     ps.append(LockedProduct(a,slot,rng.choice(MARKETS+('hold','A')),rng.randint(0,50),rng.choice(tuple(PRICE_INCOME)),rng.random()>.07,rng.random()<.15,rng.randint(6,38),roy,rng.random()<.5))
   ms={m:MarketSpec(rng.randint(0,7),rng.randint(0,36),rng.choice(tuple(PRICE_INCOME))) for m in MARKETS}
   priority=tuple(rng.sample(range(n),n));cash={a:rng.randint(0,90) for a in range(n)};decision={(p.owner,p.slot):rng.random()<.75 for p in ps}
   r=run(ps,cash=cash,priority=priority,markets=ms,decisions=decision,final=case%2==0)
   self.assertEqual(len(r['usedCompanies']),len(r['expansions']));self.assertTrue(all(v>=0 for v in r['cashAfterExpansion'].values()))
   self.assertEqual(sum(cash.values())-sum(r['cashAfterExpansion'].values()),r['bankPaid'])
   counts=Counter((s['owner'],s['slot']) for s in flat(r));self.assertTrue(all(v<=2 for v in counts.values()))
   for m,info in r['markets'].items():
    self.assertEqual(len(info['sales'])+int(info['referenceSold'])+info['unfilled'],info['orders'])
    for s in info['sales']:
     self.assertLessEqual(s['price'],ms[m].budget)
     if s['copy']:self.assertEqual(counts[(s['owner'],s['slot'])],2)
   for e in r['expansions']:
    p=next(p for p in ps if p.owner==e['owner'] and p.slot==e['slot'])
    clones=[s for s in r['markets'][p.market]['sales'] if s['owner']==p.owner and s['slot']==p.slot]
    self.assertEqual(len(clones),2);self.assertTrue(all(s['score']==p.score and s['price']==p.price for s in clones))
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(ExpansionTests);result=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'version':'7.0','testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'multiMarketScenarios':1200,'success':result.wasSuccessful(),'limitations':['输入的完整配置合法性、锁定竞争力和卡面适用范围由调用者预先核验','有限成本模型不代替全部合同/设施/方案解释器','情境不是整局、不是胜率或真人实测']}
 (R/'work/expansion_test_results_v70.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if not result.wasSuccessful():raise SystemExit(1)
