"""定向规则单元测试；不宣称全卡解释或多人实测。"""
import json,unittest,random,copy
from pathlib import Path
from collections import Counter
from supplier_engine import Network,PublicTechnology
from component_engine import evaluate,KINDS
from rules_core import Offer,resolve_market,take_market,draw_reference
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'work/v69_data.json').read_text());PART={c['id']:c for c in D['parts']};T={c['id']:c for c in D['technologies']};ALL={c['id']:c for k in ('parts','technologies','contracts','facilities','schemes','benchmarks','demands') for c in D[k]}

def net():
 n=Network(D);n.era=5
 for i,name in enumerate('ABCD',1):
  p=n.players[name];p.cash=500
  p.library={c['components'][0]['kind']:c['id'] for c in D['parts'] if c['type']=='starter' and c['id'].startswith('S0'+str(i))}
 return n

def pub(n,tid='T09',factory='B',author='A'):
 n.public[tid]=PublicTechnology(tid,author,factory);n.players[author].completed.add(tid);n.players[author].partners.add(factory)

def matching_library(n,name,factory='B',kind='screen',offset=0):
 c=sorted([c for c in D['parts'] if c['type']=='supply' and c['supplier']==factory and c['components'][0]['kind']==kind and c['components'][0]['form']!='fold'],key=lambda c:c['components'][0]['power'])[offset]
 n.players[name].library[kind]=c['id'];return c

class Rules69(unittest.TestCase):
 def test_exact_counts_and_uniqueness(self):
  self.assertEqual(len(ALL),315);self.assertTrue(all(c['qty']==1 for c in ALL.values()));self.assertEqual(sum(c.get('deck')=='main' for c in ALL.values()),257)
 def test_stable_balanced_each_era_kind(self):
  count=Counter((c['era'],c['components'][0]['kind']) for c in D['parts'] if c['type']=='supply')
  self.assertEqual(set(count.values()),{4});self.assertEqual(len(count),20)
 def test_suppliers_balanced(self):
  stable=[c for c in D['parts'] if c['type']=='supply'];self.assertEqual(Counter(c['supplier'] for c in stable),dict.fromkeys('RYBGK',16))
  for f in 'RYBGK':
   self.assertEqual(Counter(c['components'][0]['kind'] for c in stable if c['supplier']==f),dict.fromkeys(KINDS,4))
 def test_custom_supplier_each_era_all_kinds(self):
  custom=[c for c in D['parts'] if c['type']=='custom']
  self.assertEqual(Counter(c['era'] for c in custom),{1:14,2:12,3:12,4:12,5:14})
  for e in range(1,6):
   self.assertEqual(Counter(a['kind'] for c in custom if c['era']==e for a in c['components']),dict.fromkeys(KINDS,6))
   for f in 'RYBGK':
    counts=Counter(a['kind'] for c in custom if c['era']==e and c['supplier']==f for a in c['components'])
    self.assertEqual(set(counts),set(KINDS));self.assertTrue(all(1<=v<=2 for v in counts.values()))
 def test_stable_reality_bands_not_artificial_midrange(self):
  maxima=[]
  for e in range(1,6):
   cs=[c for c in D['parts'] if c['type']=='supply' and c['era']==e and c['components'][0]['kind']=='chip']
   self.assertEqual(len(cs),4)
   specs=[c['components'][0]['spec']for c in cs];maxima.append(max(specs))
   self.assertTrue(all(3<=v<=12 for v in specs));self.assertLessEqual(max(specs)-min(specs),4) # T760 is a deliberate lower-cost nonflagship addition
  self.assertEqual(maxima,sorted(maxima))
 def test_initial_unchanged_and_neutral(self):
  old=json.loads((R/'source/v68_data.json').read_text());before={c['id']:c for c in old['parts'] if c['type']=='starter'}
  now=[c for c in D['parts'] if c['type']=='starter'];self.assertEqual(len(now),16)
  for c in now:self.assertEqual(c['components'],before[c['id']]['components']);self.assertIsNone(c['supplier']);self.assertEqual(c['installCost'],0)
 def test_default_contract_and_new_h30(self):
  h=ALL['H30'];self.assertEqual(h['units'],1);self.assertIn('黑厂',h['effect']);self.assertEqual(h['factory'],'K')
 def test_research_split(self):
  self.assertEqual(sum(t['jointEligible'] for t in T.values()),35)
  for t in T.values():
   if t['jointEligible']:
    self.assertLess(t['jointCost'],t['cost']);self.assertGreater(t['licenseFee'],0);self.assertIn(t['relatedPart'],KINDS)
   else:self.assertEqual(t['scope'],'process');self.assertIsNone(t['licenseFee'])
 def test_install_first_no_retroactive_discount(self):
  n=net();p=n.players['B'];c=PART['C101'];p.hand.add(c['id']);before=p.cash
  self.assertEqual(n.install('B',c['id']),c['installCost']);self.assertEqual(before-p.cash,c['installCost']);self.assertIn(c['supplier'],p.partners)
 def test_partner_price_not_double_discount(self):
  n=net();p=n.players['A'];c=PART['C115'];p.hand.add(c['id']);p.partners.add(c['supplier'])
  self.assertEqual(n.install('A',c['id'],3),c['installPartnerCost']-3)
 def test_future_install_allowed_and_no_future_use(self):
  n=net();n.era=1;p=n.players['A'];p.hand.add('C120');n.install('A','C120')
  with self.assertRaises(ValueError):n.assemble('A',1,KINDS)
 def test_library_locked_by_remaining_batch(self):
  n=net();p=n.players['A'];n.assemble('A',1,KINDS);n.assemble('A',2,KINDS);p.hand.add('C101');n.cancel('A',1)
  with self.assertRaises(ValueError):n.install('A','C101')
  n.cancel('A',2);n.install('A','C101');self.assertEqual(p.library['chip'],'C101')
 def test_relationship_nonbusiness_events(self):
  n=net();p=n.players['A']
  for event in ['draw','cancel','prototype','sign','expire','buyback','export']:n.add_partner(p,'R',event)
  self.assertNotIn('R',p.partners);n.add_partner(p,'R','order_fulfilled');self.assertIn('R',p.partners)
 def test_core_requires_partner_and_fixed_cost(self):
  n=net();p=n.players['A']
  with self.assertRaises(ValueError):n.core_cooperate('A','R')
  p.partners|={'R','B'};cash=p.cash;n.core_cooperate('A','R');self.assertEqual(cash-p.cash,12)
  n.core_cooperate('A','B');self.assertEqual(p.core,'B');self.assertIn('R',p.partners)
 def test_multiple_companies_same_core(self):
  n=net()
  for a in 'AB':n.players[a].partners.add('R');n.core_cooperate(a,'R')
  self.assertEqual(n.players['A'].core,n.players['B'].core)
 def test_joint_requires_core_and_associated_part(self):
  n=net();p=n.players['A'];p.hand.add('T19')
  with self.assertRaises(ValueError):n.start('A','T19',True)
  p.partners.add('B');n.core_cooperate('A','B')
  with self.assertRaises(ValueError):n.start('A','T19',True)
  matching_library(n,'A','B','chip');self.assertEqual(n.start('A','T19',True),T['T19']['jointCost'])
 def test_joint_switch_block_and_abandon_no_refund(self):
  n=net();p=n.players['A'];p.partners|={'B','R'};n.core_cooperate('A','B');matching_library(n,'A','B','chip');p.hand.add('T19');n.start('A','T19',True)
  with self.assertRaises(ValueError):n.core_cooperate('A','R')
  before=p.cash;n.abandon('A','T19');self.assertEqual(p.cash,before);n.core_cooperate('A','R')
 def test_joint_original_no_proof_still_needs_full_supplier_sample(self):
  n=net();p=n.players['A'];p.partners.add('B');n.core_cooperate('A','B');matching_library(n,'A','B','chip');p.hand.add('T19');n.start('A','T19',True)
  self.assertFalse(n.advance('A','T19',original_proof=True));p.work=3
  neutral=[PART[c['id']] for c in D['parts'] if c['type']=='starter' and c['id'].startswith('S02')]
  self.assertFalse(n.advance('A','T19',original_proof=True,prototype_cards=neutral))
  sample=[PART[x] for x in p.library.values()];self.assertTrue(n.advance('A','T19',original_proof=True,prototype_cards=sample));self.assertEqual(n.public['T19'].author,'A');self.assertEqual(n.public['T19'].factory,'B')
 def test_process_only_private(self):
  n=net();p=n.players['A'];p.core='R';p.partners.add('R');tid=next(t['id'] for t in T.values() if not t['jointEligible']);p.hand.add(tid);p.completed={'T01','T03','T04'}
  with self.assertRaises(ValueError):n.start('A',tid,True)
 def test_private_exclusive(self):
  n=net();n.players['A'].completed.add('T09')
  with self.assertRaises(ValueError):n.assemble('B',1,KINDS,techs=['T09'])
 def test_license_pays_author_once_and_counts_not_ownership(self):
  n=net();pub(n);matching_library(n,'B');p=n.players['B'];p.partners.add('B');old=[n.players[a].cash for a in 'AB'];bank=n.bank_paid
  cost,fees=n.assemble('B',3,KINDS,techs=['T09']);fee=T['T09']['licenseFee'];self.assertEqual(fees,{'A':fee});self.assertEqual(n.players['A'].cash-old[0],fee);self.assertEqual(old[1]-p.cash,cost+fee);self.assertEqual(n.bank_paid-bank,cost);self.assertFalse(n.own_deployed('B',3));self.assertNotIn('T09',p.completed);self.assertEqual(n.public['T09'].uses,{'B':3})
 def test_one_company_one_use_and_other_companies_can_share(self):
  n=net();pub(n)
  for idx,a in enumerate('AB'):
   n.players[a].partners.add('B');matching_library(n,a,offset=idx);n.assemble(a,1,KINDS,techs=['T09'])
  self.assertEqual(len(n.public['T09'].uses),2)
  with self.assertRaises(ValueError):n.assemble('B',2,KINDS,techs=['T09'])
 def test_self_use_free_not_automatic(self):
  n=net();pub(n);matching_library(n,'A');p=n.players['A'];self.assertEqual(n.public['T09'].uses,{})
  cost,fees=n.assemble('A',1,KINDS,techs=['T09']);self.assertEqual(fees,{});self.assertTrue(n.own_deployed('A',1))
 def test_self_use_also_requires_matching_supplier(self):
  n=net();pub(n)
  with self.assertRaises(ValueError):n.assemble('A',1,KINDS,techs=['T09'])
 def test_cannot_get_partner_from_same_assembly_to_pay_license(self):
  n=net();p=n.players['B'];custom=next(c for c in D['parts'] if c['type']=='custom' and len(c['components'])==1 and c['components'][0]['kind']=='chip');pub(n,'T19',custom['supplier']);p.hand.add(custom['id'])
  with self.assertRaises(ValueError):n.assemble('B',1,('screen','camera','body'),(custom['id'],),['T19'])
  self.assertFalse(p.partners)
 def test_manufacturing_discount_does_not_discount_license(self):
  n=net();pub(n);p=n.players['B'];p.partners.add('B');matching_library(n,'B');cost,fees=n.assemble('B',1,KINDS,techs=['T09'],total_discount=999)
  self.assertEqual(cost,6);self.assertEqual(fees['A'],T['T09']['licenseFee'])
 def test_atomic_cash_failure_no_author_payout(self):
  n=net();pub(n);p=n.players['B'];p.partners.add('B');matching_library(n,'B');p.cash=6;before=n.players['A'].cash
  with self.assertRaises(ValueError):n.assemble('B',1,KINDS,techs=['T09'],total_discount=999)
  self.assertEqual(n.players['A'].cash,before);self.assertEqual(p.cash,6);self.assertFalse(p.products);self.assertFalse(n.public['T09'].uses)
 def test_cancel_relicense_and_unsold_no_repeat_fee(self):
  n=net();pub(n);p=n.players['B'];p.partners.add('B');matching_library(n,'B');n.assemble('B',1,KINDS,techs=['T09']);cash=p.cash;n.phase='release';n.finish_release({},evidence_done=True);self.assertEqual(p.cash,cash);self.assertEqual(n.public['T09'].uses['B'],1)
  n.phase='work';n.cancel('B',1);self.assertEqual(p.cash,cash);self.assertEqual(n.public['T09'].uses,{});n.assemble('B',2,KINDS,techs=['T09']);self.assertLess(p.cash,cash)
 def test_release_frozen_and_signature_permanent(self):
  n=net();pub(n);p=n.players['B'];p.partners.add('B');matching_library(n,'B');n.assemble('B',3,KINDS,techs=['T09']);n.phase='release'
  with self.assertRaises(ValueError):n.cancel('B',3)
  with self.assertRaises(ValueError):n.finish_release({'B':[3]},evidence_done=False)
  n.finish_release({'B':[3]},evidence_done=True);self.assertEqual(n.public['T09'].author,'A');self.assertFalse(n.public['T09'].uses);self.assertIn('T09',n.players['A'].completed)
 def test_core_switch_does_not_move_public_research(self):
  n=net();pub(n);p=n.players['A'];p.core='B';p.partners.add('R');n.core_cooperate('A','R');self.assertEqual(n.public['T09'].factory,'B');self.assertEqual(n.public['T09'].author,'A')
 def test_borrowed_not_free_temporary_prototype(self):
  n=net();pub(n);self.assertFalse(n.temporary_technology_allowed('B','T09'));self.assertTrue(n.temporary_technology_allowed('A','T09'))
 def test_cross_supplier_one_exception_and_partner_still_required(self):
  n=net();pub(n);p=n.players['B'];p.partners.add('B');p.completed.add('T34');n.assemble('B',1,KINDS,techs=['T09','T34'])
  n.cancel('B',1);p.partners.clear()
  with self.assertRaises(ValueError):n.assemble('B',2,KINDS,techs=['T09','T34'])
 def test_t34_cannot_waive_itself(self):
  n=net();pub(n,'T34');p=n.players['B'];p.partners.add('B')
  with self.assertRaises(ValueError):n.assemble('B',1,KINDS,techs=['T34'])
 def test_two_mismatch_not_both_waived(self):
  n=net();pub(n,'T09');pub(n,'T34');p=n.players['B'];p.partners.add('B')
  with self.assertRaises(ValueError):n.assemble('B',1,KINDS,techs=['T09','T34'])
 def test_integrated_slot_cannot_skip(self):
  c=PART['X164']
  with self.assertRaises(ValueError):evaluate([c],['T09','T10'],T,era=5)
 def test_renamed_flagship_no_legacy_lowend_permit(self):
  n=net();p=n.players['A'];p.library['chip']='C109';out=evaluate([PART[x]for x in p.library.values()],tech_catalog=T,price=18)
  self.assertNotIn('office',out['permits']);self.assertIn('性能',out['features']);self.assertEqual(PART['C109']['components'][0]['spec'],7)

 def test_three_cash_resources_royalty_not_technology(self):
  n=net();pub(n);matching_library(n,'B');p=n.players['B'];p.partners.add('B');tech=n.players['A'].tech;n.assemble('B',1,KINDS,techs=['T09']);self.assertEqual(n.players['A'].tech,tech)
 def test_take_refill_only_at_end(self):
  got,display,deck=take_market(list(range(8)),list(range(8,15)),[1,6]);self.assertEqual(got,[1,6]);self.assertEqual(display[1],8);self.assertEqual(display[6],9)
  with self.assertRaises(ValueError):take_market(list(range(8)),list(range(8,15)),[1,1])
 def test_reference_lock_before_random(self):
  rng=random.Random(64)
  with self.assertRaises(ValueError):draw_reference(D['benchmarks'],1,[0],2,rng)
  cards={draw_reference(D['benchmarks'],1,[0,1],2,rng)['id'] for _ in range(100)};self.assertEqual(len(cards),6)
 def test_600_market_cases(self):
  rng=random.Random(64)
  for i in range(600):
   n=rng.choice([2,3,4]);offers=[Offer(p,k,rng.randint(4,40),rng.choice([18,28,38,48]),frozenset(rng.sample(['性能','影像','生态'],rng.randint(0,3))),rng.choice([False,True])) for p in range(n) for k in range(1,rng.randint(1,4)+1)]
   orders=rng.randint(1,8);budget=rng.choice([18,28,38,48]);ref=rng.randint(0,35)
   out=resolve_market(offers,budget=budget,preferences=['生态'],orders=orders,reference=ref,priority=list(range(n)))
   self.assertEqual(len(out['sales'])+out['referenceSold']+out['unfilled'],orders);self.assertTrue(all(s['cash']<=budget for s in out['sales']));self.assertEqual(len({(s['owner'],s['product']) for s in out['sales']}),len(out['sales']))
   for sale in out['sales']:
    if sale['stars']:self.assertGreater(sale['score'],ref)

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Rules69);result=unittest.TextTestRunner(verbosity=2).run(suite)
 report={'version':'6.9','testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'marketScenarios':600,'success':result.wasSuccessful(),'limits':['原科研证据在供应状态模型中作为已核验参数传入','不穷举全卡Q、H、U效果和所有联动','没有智能对手、整局时长或真人平衡测试']}
 (R/'work/test_results_v69.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if not result.wasSuccessful():raise SystemExit(1)
