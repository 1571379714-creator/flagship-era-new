"""7.0结构与卡面接口核验；项目原始证据的布尔输入不代表自动穷举。"""
import json,random,itertools,copy,unittest
from pathlib import Path
from collections import Counter,deque
from department_engine import *
from component_engine import evaluate,KINDS
from supplier_engine import Network,PublicTechnology
from rules_core import Offer,resolve_market,take_market,draw_reference,stars
R=Path(__file__).resolve().parents[1];D=json.loads((R/'work/v70_data.json').read_text());OLD=json.loads((R/'source/v69_data.json').read_text())
ALL={c['id']:c for k in ('parts','technologies','contracts','facilities','schemes','benchmarks','demands') for c in D[k]};T={c['id']:c for c in D['technologies']};PART={c['id']:c for c in D['parts']}
def net():
 n=Network(D);n.era=5
 for i,a in enumerate('ABCD',1):
  p=n.players[a];p.cash=500;p.library={c['components'][0]['kind']:c['id'] for c in D['parts'] if c['type']=='starter' and c['id'].startswith('S0'+str(i))}
 return n

def matching(n,a,f='B',kind='screen'):
 c=min((c for c in D['parts'] if c['type']=='supply' and c['supplier']==f and c['components'][0]['kind']==kind and c['components'][0]['form']=='slab'),key=lambda c:c['components'][0]['power'])
 n.players[a].library[kind]=c['id'];return c
class DataTests(unittest.TestCase):
 def test_counts(self):
  self.assertEqual(len(ALL),315);self.assertEqual(sum(c.get('deck')=='main' for c in ALL.values()),257);self.assertTrue(all(c['qty']==1 for c in ALL.values()))
 def test_fifty_unique(self):
  models=[a['name'] for c in D['parts'] if c['type']!='starter' for a in c['components'] if a['kind']=='chip'];self.assertEqual(len(models),50);self.assertEqual(len(set(models)),50)
 def test_era_kind_counts(self):
  self.assertEqual(set(Counter((c['era'],c['components'][0]['kind']) for c in D['parts'] if c['type']=='supply').values()),{4})
  for e in range(1,6):self.assertEqual(Counter(a['kind'] for c in D['parts'] if c['type']=='custom' and c['era']==e for a in c['components']),dict.fromkeys(KINDS,6))
 def test_initial_parts_data(self):
  before={c['id']:c for c in OLD['parts'] if c['type']=='starter'}
  for c in D['parts']:
   if c['type']=='starter':self.assertEqual(c['components'],before[c['id']]['components']);self.assertIsNone(c['supplier'])
 def test_chip_anchors(self):
  for cid,v in {'X136':12,'X147':14,'C115':17}.items():self.assertEqual(next(a['spec'] for a in PART[cid]['components'] if a['kind']=='chip'),v)
 def test_no_extra_power_inflation(self):
  for a,b in zip(D['parts'],OLD['parts']):self.assertEqual([x['power'] for x in a['components']],[x['power'] for x in b['components']])
 def test_research_prices_and_periods_unchanged(self):
  old={t['id']:t for t in OLD['technologies']}
  for t in T.values():
   for k in ('cost','jointCost','selfWork','jointWork','gain','licenseFee'):self.assertEqual(t[k],old[t['id']][k])
 def test_no_work_budget(self):
  self.assertNotIn('workPerTurn',D['parameters']);self.assertEqual(D['parameters']['actionsPerTurn'],1)
  self.assertTrue(all('work' not in c for c in D['facilities']));self.assertFalse(hasattr(net().players['A'],'work'))
 def test_contract_financial_consistency(self):
  for h in D['contracts']:
   if h['subtype']=='order':self.assertEqual(h['totalCash'],h['unitPrice']*h['units']);self.assertEqual(h['totalIncome'],h['unitIncome']*h['units'])
 def test_demands(self):
  for c in D['demands']:
   for n in (2,3,4):self.assertIn(sum(m['ordersByPlayers'][str(n)] for m in c['markets']),{4*n-1,4*n})
 def test_references(self):
  self.assertEqual(Counter(c['era'] for c in D['benchmarks']),dict.fromkeys(range(1,6),6))
  for c in D['benchmarks']:
   for m in c['markets']:
    s=stars(m['score']);self.assertEqual(m['reward'],s);self.assertEqual(m['incomeReward'],[0,2,3,4][s]);self.assertEqual(m['technologyReward'],[0,1,1,2][s])
 def test_48_predicate_not_old_or(self):
  self.assertEqual(D['parameters']['flagshipPriceBase'],28);self.assertEqual(D['parameters']['flagshipPriceChip'],12)
 def test_each_supplier_four_kinds(self):
  for f in 'RYBGK':self.assertEqual(Counter(c['components'][0]['kind'] for c in D['parts'] if c['type']=='supply' and c['supplier']==f),dict.fromkeys(KINDS,4))
 def test_no_renewed_empty_publish(self):self.assertIn('终点前1',D['publicationAdvance']['emptyGuard'])
class MatrixTests(unittest.TestCase):
 def test_all_8640_transitions(self):
  for perm in itertools.permutations(NAMES):
   for name in NAMES:
    for sw in (False,True):
     m=Matrix([list(perm[:3]),list(perm[3:])]);r,c=m.location(name);other=m.rows[1-r][:];rest=[x for x in m.rows[r] if x!=name];self.assertEqual(m.finish(name,sw),c+1)
     self.assertEqual(m.rows[r][1:],rest);self.assertEqual(m.rows[1-r][1:],other[1:]);self.assertEqual(m.strength(name),1);self.assertEqual(set(sum(m.rows,[])),set(NAMES))
 def test_reachable_permutations(self):
  start=tuple(sum([list(x) for x in INITIAL],[]));seen={start};q=deque([start])
  while q:
   p=q.popleft()
   for name in NAMES:
    for sw in (False,True):
     m=Matrix([list(p[:3]),list(p[3:])]);m.finish(name,sw);n=tuple(sum(m.rows,[]))
     if n not in seen:seen.add(n);q.append(n)
  self.assertEqual(len(seen),720)
 def test_user_example(self):
  m=Matrix([['A','B','C'],['D','E','F']])
  # Use actual card names to keep conservation guard.
  m=Matrix();m.finish('研发',True);self.assertEqual(m.rows,[['研发','供应','制造'],['调研','合作','运营']])
 def test_repeat_stays_one(self):
  m=Matrix();self.assertEqual(m.finish('制造'),3)
  for _ in range(20):self.assertEqual(m.finish('制造'),1)
 def test_other_row_does_not_recharge(self):
  m=Matrix();row=m.rows[0][:];m.finish('运营');self.assertEqual(m.rows[0],row)
 def test_high_three_cycle(self):
  m=Matrix()
  for _ in range(10):
   for name in ['制造','供应','调研']:self.assertEqual(m.finish(name),3)
 def test_release_not_matrix_mutation(self):
  m=Matrix();m.finish('制造',True);old=copy.deepcopy(m.rows);Publication(2).reset();self.assertEqual(m.rows,old)
class ClockTests(unittest.TestCase):
 def test_endpoints(self):self.assertEqual(technology_distance(46),130);self.assertEqual(income_alignment(0),130)
 def test_all_track_intersections(self):
  for t in range(80):
   for inc in range(180):self.assertEqual(meets(inc,t),inc>=income_alignment(t))
 def test_score_examples(self):self.assertEqual(score(80,22),8);self.assertEqual(score(65,22),-7);self.assertEqual(score(2,47),5)
 def test_tech_steps(self):
  for t in range(1,60):self.assertEqual(technology_distance(t)-technology_distance(t-1),2 if t<=8 else 3)
 def test_thresholds(self):
  for t,era in [(0,1),(3,1),(4,2),(8,2),(9,3),(14,3),(15,4),(21,4),(22,5),(46,5)]:self.assertEqual(unlocked_era([t,0]),era)
 def test_no_fixed_two_publications(self):self.assertEqual(unlocked_era([22,0]),5)
 def test_notice_caps(self):
  for s in (1,2,3):
   self.assertEqual(notice_cap('制造',s,new_surviving=0),0);self.assertEqual(notice_cap('研发',s,completed=False),0)
  self.assertEqual(notice_cap('制造',3,new_surviving=3),2);self.assertEqual(notice_cap('制造',1,new_surviving=2),0)
 def test_reward_completion_not_department(self):self.assertEqual(notice_cap('奖励',3,completed=True),0)
 def test_no_goods_empty_guard(self):
  p=Publication(2)
  for _ in range(100):self.assertFalse(p.advance(2,legal_products=0))
  self.assertEqual(p.progress,7);self.assertTrue(p.advance(1,legal_products=1))
 def test_publicity_cost_and_own_stock(self):
  p=Publication(3)
  with self.assertRaises(ValueError):p.publicity(3,20,1,6)
  self.assertEqual(p.publicity(3,20,2,6)[0],17);self.assertEqual(p.progress,2)
 def test_1000_idle_operations(self):
  p=Publication(4);m=Matrix()
  for _ in range(1000):s=m.strength('运营');self.assertEqual(notice_cap('运营',s),0);m.finish('运营')
  self.assertEqual(p.progress,0)
 def test_final_never_extra_normal(self):
  p=Publication(2,final_phase=True);self.assertFalse(p.advance(8,legal_products=4));self.assertEqual(p.progress,8)
class NetworkTests(unittest.TestCase):
 def test_install_has_action_quota(self):
  n=net();p=n.players['A'];p.hand|={'C101','D101'};n.begin('A','供应',1);n.install('A','C101')
  with self.assertRaises(ValueError):n.install('A','D101')
 def test_first_partner_price(self):
  n=net();p=n.players['A'];p.hand.add('C101');n.begin('A','供应',1);self.assertEqual(n.install('A','C101'),PART['C101']['installCost']);self.assertIn('R',p.partners)
 def test_cannot_free_install_wrong_action(self):
  n=net();n.players['A'].hand.add('C101');n.begin('A','运营',3)
  with self.assertRaises(ValueError):n.install('A','C101')
 def test_three_batches_need_one_manufacture_action(self):
  n=net();n.begin('A','制造',3)
  for s in (1,2,3):n.assemble('A',s,stable=KINDS)
  with self.assertRaises(ValueError):n.assemble('A',4,stable=KINDS)
 def test_stable_lock_across_products(self):
  n=net();p=n.players['A'];p.hand.add('C101');n.begin('A','制造',2)
  for s in (1,2):n.assemble('A',s,stable=KINDS)
  n.end();n.cancel('A',1);n.begin('A','供应',1)
  with self.assertRaises(ValueError):n.install('A','C101')
  n.end();n.cancel('A',2);n.begin('A','供应',1);n.install('A','C101')
 def test_one_research_no_overflow(self):
  n=net();p=n.players['A'];p.hand|={'T01','T02'};n.begin('A','研发',3);r=n.research_action('A','T01',original_proof=True);self.assertEqual(r['progress'],4)
  with self.assertRaises(ValueError):n.research_action('A','T02',original_proof=True)
  self.assertIn('T02',p.hand)
 def test_first_core_uses_complete_strength_no_free_one(self):
  n=net();p=n.players['A'];p.hand.add('T01');p.library['chip']='C101';p.partners.add('R');cards=[PART[x] for x in p.library.values()];n.begin('A','研发',3)
  r=n.research_action('A','T01',joint=True,first_core='R',original_proof=True,prototype_cards=cards)
  self.assertEqual(r['fee'],12+T['T01']['jointCost']);self.assertEqual(r['progress'],T['T01']['jointWork']);self.assertTrue(r['completed']);self.assertEqual(n.public['T01'].author,'A')
 def test_failed_core_atomic(self):
  n=net();p=n.players['A'];p.cash=12;p.hand.add('T01');p.partners.add('R');p.library['chip']='C101';n.begin('A','研发',1)
  with self.assertRaises(ValueError):n.research_action('A','T01',joint=True,first_core='R')
  self.assertEqual(p.cash,12);self.assertIsNone(p.core);self.assertIn('T01',p.hand)
 def test_author_cash_and_no_scientific_credit(self):
  n=net();p=n.players['B'];p.partners.add('B');matching(n,'B');n.public['T09']=PublicTechnology('T09','A','B');n.players['A'].completed.add('T09');before=n.players['A'].cash
  n.begin('B','制造',2);n.assemble('B',1,stable=KINDS,techs=('T09',));self.assertEqual(n.players['A'].cash-before,T['T09']['licenseFee']);self.assertFalse(n.own_deployed('B',1))
  with self.assertRaises(ValueError):n.assemble('B',2,stable=KINDS,techs=('T09',))
  n.end();cash=p.cash;n.cancel('B',1);self.assertEqual(p.cash,cash);self.assertEqual(n.public['T09'].uses,{})
 def test_t21_requires_integrated(self):
  cards=[PART[f'S01{i}'] for i in range(1,5)]
  with self.assertRaises(ValueError):evaluate(cards,('T21',),T)
class MarketTests(unittest.TestCase):
 def test_reference_hidden_until_lock(self):
  with self.assertRaises(ValueError):draw_reference(D['benchmarks'],1,{0},2,random.Random(1))
 def test_cards_refresh_once(self):
  h,b,p=take_market(list(range(8)),list(range(20,40)),[0,1]);self.assertEqual(h,[0,1]);self.assertEqual(b[:2],[20,21])
 def test_600_single_markets(self):
  rng=random.Random(70001)
  for _ in range(600):
   n=rng.choice((2,3,4));orders=rng.randint(1,7);ofs=[Offer(i,j,rng.randint(5,65),rng.choice((18,28,38,48)))for i in range(n)for j in range(rng.randint(1,4))]
   r=resolve_market(ofs,budget=rng.choice((18,28,38,48)),preferences=[],orders=orders,reference=rng.randint(0,60),priority=list(range(n)))
   self.assertEqual(len(r['sales'])+r['referenceSold']+r['unfilled'],orders)
if __name__=='__main__':unittest.main(verbosity=2)
