from pathlib import Path
from dataclasses import replace
import json,random,re,itertools
from numeric_core import *
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'work/v60_data.json').read_text())
checks=0
def ck(x,msg):
 global checks
 checks+=1
 if not x:raise AssertionError(msg)
def fails(fn):
 try:fn()
 except ValueError:return True
 return False
allcards=sum((d[k] for k in ['parts','technologies','contracts','facilities','schemes','benchmarks','demands']),[])
ck(len(allcards)==243,'243 designs')
ck(sum(c['qty'] for c in allcards)==315,'315 physical')
ids={c['id'] for c in allcards};ck(len(ids)==243,'unique IDs')
for c in allcards:
 ck(bool(c['effect']) and c['qty']>0,'complete card')
 for ref in re.findall(r'\b(?:T|U|Q|H)\d\d\b',c['effect']):ck(ref in ids,f'bad card ref {ref}')
for p in d['parts']:
 ck(len({c['kind'] for c in p['components']})==len(p['components']),'no duplicate component')
 ck(all(0<=c['spec']<=10 and c['batchCost']>=1 for c in p['components']),'component bounds')
for v in d['benchmarks']:
 for m in v['markets']:ck(m['reward']==reward_stars(m['score']),'cell reward')
for g in range(1,6):
 deck=[v for v in d['benchmarks'] if v['era']==g]
 ck(len(deck)==6,'six reference options')
 ck(len({tuple(m['score'] for m in v['markets']) for v in deck})==6,'distinct reference styles')
for n in d['demands']:
 for m in n['markets']:
  ck(len(set(m['preferences']))==2,'2 distinct demand preferences')
  ck(m['budget'] in PRICE_MOD,'budget')
  ck(all(t in FEATURES for t in m['preferences']),'traits')
parts={p['id']:p for p in d['parts']}
for company in ['M01','M02','M03','M04']:
 ps=[p for p in d['parts'] if p.get('company')==company]
 pr=base_prototype(ps)
 ck(pr['load']<=pr['power'],'starter valid')
 ck(matured_batch_cost(ps,1)==matured_batch_cost(ps,5),'starter never discounts')
ck(fails(lambda:base_prototype([parts['X29'],parts['D01']])),'cannot overlap full kit')
ck(fails(lambda:base_prototype([parts['C02'],parts['D09'],parts['I01'],parts['F01']])),'fold pair')
# 订单核心与逐批展开的独立核对，包含2—4人；不是完整对局。
rng=random.Random(60092026);market_cases=0
for players in (2,3,4):
 for case in range(400):
  priority=list(range(players));rng.shuffle(priority)
  prefs=rng.sample(sorted(FEATURES),2)
  offers=[Offer(p,i,rng.randint(0,32),rng.randrange(3),rng.choice(list(PRICE_MOD)),rng.randrange(5),frozenset(rng.sample(sorted(FEATURES),rng.randrange(7))),new=bool(rng.randrange(2)),deployed=bool(rng.randrange(2)),allowed=bool(rng.randrange(5))) for p in range(players) for i in range(1,rng.randint(2,5))]
  budget=rng.choice(list(PRICE_MOD));orders=rng.randint(1,6);reference=rng.randint(2,35)
  out=resolve_market(offers,preferences=prefs,budget=budget,orders=orders,reference=reference,priority=priority)
  ck(sum(r['qty'] for r in out['sales'])+out['referenceSold']+out['unfilled']==orders,'order conservation')
  expanded=[]
  for o in offers:
   if o.allowed and o.price<=budget:
    for u in range(o.qty):expanded.append((-competitive(o,prefs),priority.index(o.owner),o.model,u,(o.owner,o.model)))
  expanded.append((-reference,players,0,0,('ref',0)))
  chosen=sorted(expanded,key=lambda r:r[:4])[:orders]
  expected={}
  for row in chosen:expected[row[-1]]=expected.get(row[-1],0)+1
  actual={(r['owner'],r['model']):r['qty'] for r in out['sales']}
  if out['referenceSold']:actual[('ref',0)]=out['referenceSold']
  ck(actual==expected,'unit expansion independent match')
  for s in out['sales']:
   o=next(o for o in offers if o.owner==s['owner'] and o.model==s['model'])
   ck(s['qty']<=o.qty and s['cash']==o.price*s['qty'],'stock cash')
   ck((s['challengeStars']>0)==(s['score']>reference and reward_stars(reference)>0),'strict reference')
  market_cases+=1
# 击败参考不能跨市场叠四份，也不能用旧机选科技
op=Offer(0,1,30,0,28,2,frozenset({'生态'}),True,True)
out=resolve_market([op],preferences=['生态','续航'],budget=48,orders=2,reference=25,priority=[0,1])
ck(reference_award([out]*4,0,'technology')=={'income':0,'technology':3},'one award per company')
ck(reference_award([out]*4,0,'income')=={'income':6,'technology':0},'not 4 rewards')
old=resolve_market([replace(op,new=False)],preferences=['生态','续航'],budget=48,orders=2,reference=25,priority=[0,1])
ck(reference_award([old],0,'technology')['technology']==0,'old no tech challenge')
equal=resolve_market([Offer(0,1,16,0,28,1,frozenset())],preferences=[],budget=28,orders=1,reference=18,priority=[0,1])
ck(equal['sales'][0]['qty']==1 and equal['sales'][0]['challengeStars']==0,'tie sells no reward')
zero=resolve_market([op],preferences=[],budget=18,orders=2,reference=25,priority=[0,1]);ck(not zero['sales'],'budget cannot be bypassed')
# 生产支付与保留已用量
s=ProductionState(120,0,0,0);q=produce(s,2,12);ck(q==ProductionState(96,2,2,2),'prepay')
ck(fails(lambda:produce(q,1,12)),'cannot overproduce quota')
# 退市只清型号库存，不清公司/平台已用量。
after_retire=replace(q,stock=0)
ck(fails(lambda:produce(after_retire,1,12)),'retire does not replenish platform')
ck(fails(lambda:produce(ProductionState(5,0,0,0),1,6)),'no spending future sale')
# 两条独立主线不求和；36可以继续记录。
ck(not end_triggered(59,29),'no track meeting/sum trigger')
ck(end_triggered(60,0) and end_triggered(0,30),'either track trigger')
ck(enterprise_score(60,9)==60 and enterprise_score(18,31)==62,'main routes')
ck(enterprise_score(18,36)==72,'tech36')
ck(29+1+3+3==36,'boundary scenario arithmetic, not full trace')
# 给定样机证明，不用强制企划卡。
fold=base_prototype([parts['X32']]);ck('折叠' in fold['traits'],'fold model without Q')
# 字段与正文基本约束检查
rules=(R/'work/v60_rules.md').read_text()
for t in ['没有固定轮数','每家公司每场最多领取一次','严格超过','18、28、38或48','所有玩家各再进行一个完整回合','不清除本期已用量']:
 ck(t in rules,'required rule '+t)
report={'version':'6.0','passed':checks,'independentMarketCases':market_cases,'status':'passed','coverage':['卡牌ID/份数/引用','参考逐格星级和同代差异','独立逐批排序对照','真实成交/预算/并列/奖励上限','生产预付款/产能/平台保留','四套初始样机与基本完整性','两条独立终局与科技36边界'],
'notCovered':['完整隐藏信息对局与胜率','全部243卡特效解释或穷举','完整科技36多回合合法路线','实际供货取得概率','多人实桌结算用时','打印机双面套准']}
(R/'work/validation_v60.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
