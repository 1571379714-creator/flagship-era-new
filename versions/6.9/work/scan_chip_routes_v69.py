"""给每张芯片寻找至少一个在实际配件内可触发其特性的配置。
假设拥有所列配件并自主完成所列技术，现金/工作充分；不证明取得路径或多人平衡。
"""
from pathlib import Path
from itertools import product,combinations
import json,copy
from component_engine import evaluate,KINDS
R=Path(__file__).resolve().parents[1];D=json.loads((R/'work/v69_data.json').read_text());P=D['parts'];T={t['id']:t for t in D['technologies']}
base_ts=['T01','T02','T03','T06','T07','T09','T10','T20','T25','T26','T27','T35']
opts=[()]+[(t,)for t in base_ts]+list(combinations(base_ts,2))+[('T21','T09','T10')]
results={};attempts=0
for target in [c for c in P if c['type']!='starter' and any(a['kind']=='chip'for a in c['components'])]:
 era=target['era'];missing=[k for k in KINDS if k not in {a['kind']for a in target['components']}]
 choices=[]
 for k in missing:
  cs=[c for c in P if len(c['components'])==1 and c['era']<=era and c['components'][0]['kind']==k]
  cs.sort(key=lambda c:(-c['components'][0]['power']if k=='body'else c['components'][0]['power'],c['components'][0]['batchCost']))
  choices.append(cs)
 found=None
 for ts in opts:
  fields0={T[t]['field']for t in ts}
  def potential(z):
   if 'deployedField'in z:return z['deployedField']in fields0
   if 'any'in z:return any(potential(i)for i in z['any'])
   return True
  if not any(all(potential(z)for z in rr.get('when',[]))for rr in target.get('rules',[])):continue
  if target.get('integratedSlots',0)+len(ts)-2*int('T21'in ts)>2:continue
  for fill in product(*choices):
   cards=[target,*fill];attempts+=1
   for price in (28,38,18,48):
    comp={a['kind']:a for item in cards for a in item['components']};fields={T[t]['field']for t in ts}
    def active(z):
     if 'any'in z:return any(active(x)for x in z['any'])
     if 'deployedField'in z:return z['deployedField']in fields
     if 'priceIn'in z:return price in z['priceIn']
     if 'fold'in z:return (comp['body']['form']=='fold')==z['fold']
     if 'stableKinds'in z:return set(z['stableKinds'])<={a['kind']for item in cards if item['type']in('supply','starter')for a in item['components']}
     a=comp[z['kind']][z['field']];b=z['value'];return a>=b if z['op']=='>='else a<=b if z['op']=='<='else a==b
    if not any(all(active(z)for z in rr.get('when',[]))for rr in target.get('rules',[])):continue
    try:after=evaluate(cards,ts,T,era,price)
    except ValueError:continue
    stripped=copy.deepcopy(cards);stripped[0]['rules']=[];stripped[0].pop('chipEffect',None)
    try:before=evaluate(stripped,ts,T,era,price)
    except ValueError:before={'withoutTargetRules':'配置不合法；本卡兼容/减耗令其合法'}
    delta={k:{'without':before.get(k),'with':v}for k,v in after.items()if before.get(k)!=v}
    if delta:
     found={'era':era,'parts':[c['id']for c in cards],'ownPrivateTechnologies':list(ts),'priceForTest':price,'stats':after,'effectDifference':delta};break
   if found:break
  if found:break
 if not found:raise AssertionError('未找到实际配件中可触发的能力:'+target['id'])
 results[target['id']]=found;print(target['id'],attempts,flush=True)
report={'version':'6.9','chipsChecked':len(results),'attemptedConfigurations':attempts,'witnesses':results,'scope':'实际牌内可组装并触发差异的条件见证；不证明每局可得、科研路径、全部Q/H/U或对手策略。'}
(R/'work/chip_route_witnesses_v69.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('active chip witnesses',len(results),'configuration attempts',attempts)
