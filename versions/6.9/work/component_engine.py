"""6.9配件与部分数值研发的验证模型。非电子游戏；不模拟全套合同/需求/Q效果。"""
from collections import Counter
from dataclasses import dataclass
KINDS=('chip','screen','camera','body')
MARKETS=('mass','gaming','photo','office')

def evaluate(cards,techs=(),tech_catalog=None,era=5,price=28,external_techs=(),joint_factories=None):
 """检查真实卡完整覆盖。cards元素是已解析稳定或定制来源，不修改状态。"""
 rows=[r for c in cards for r in c['components']]
 if Counter(r['kind'] for r in rows)!=Counter(KINDS):raise ValueError('四类必须完整且不重叠')
 if any(c['era']>era for c in cards):raise ValueError('未来配件')
 if len({c['id'] for c in cards})!=len(cards):raise ValueError('重复实体')
 if len(techs)!=len(set(techs)):raise ValueError('重复部署')
 comp={r['kind']:r for r in rows};fold=comp['body']['form']=='fold'
 if fold!=(comp['screen']['form']=='fold'):raise ValueError('折叠不配套')
 raw_integrated=sum(c.get('integratedSlots',0) for c in cards)
 if 'T21' in techs and raw_integrated<1:raise ValueError('T21仅适用原始集成位至少1')
 occupied=max(0,raw_integrated-int('T21' in techs))+len(techs)-int('T21' in techs)
 if occupied>2:raise ValueError('集成与部署超位')
 stable={r['kind'] for c in cards if c['type'] in ('supply','starter') for r in c['components']}
 fields={tech_catalog[t]['field'] for t in techs} if tech_catalog else set()
 def cond(z):
  if 'any' in z:return any(cond(i) for i in z['any'])
  if 'priceIn' in z:return price in z['priceIn']
  if 'fold' in z:return fold==z['fold']
  if 'stableKinds' in z:return set(z['stableKinds'])<=stable
  if 'deployedField' in z:return z['deployedField'] in fields
  a=comp[z['kind']][z['field']];b=z['value'];op=z['op']
  return {'>=':lambda:a>=b,'<=':lambda:a<=b,'==':lambda:a==b}[op]()
 rules=[r for c in cards for r in c.get('rules',[]) if all(cond(z) for z in r.get('when',[]))]
 codes={c.get('chipEffect') for c in cards}
 waived=any(r['op']=='compatibility' for r in rules) or bool(set(techs)&{'T26','T38'}) or ('limitedISP' in codes and comp['camera']['power']<=5)
 for r in rules:
  if r['op']=='requireChip' and not waived and comp['chip']['spec']<r['value']:raise ValueError('平台兼容不足')
 red={k:0 for k in KINDS[:3]};supply=comp['body']['power'];base=sum(r['spec'] for r in rows);feat=set();bonus={m:0 for m in MARKETS}
 afee=0;totaldisc=0
 for r in rules:
  if r['op']=='powerReduction':red[r['kind']]+=r['value']
  elif r['op']=='market':bonus[r['market']]+=r['value']
  elif r['op']=='feature':feat.add(r.get('feature',r.get('value')))
  elif r['op']=='assemblyDiscount':afee+=r['value']
  elif r['op']=='totalDiscount':totaldisc+=r['value']
 # Supported research subset used in witness search; others' nonnumeric events are not inferred.
 if 'T01' in techs and comp['chip']['spec']>=6:red['chip']+=2
 if 'T03' in techs and comp['screen']['mark']=='轻薄':red['screen']+=2
 if 'T04' in techs and comp['body']['mark']=='续航':supply+=3
 if 'T09' in techs:red['screen']+=3
 if 'T10' in techs:supply+=4
 if 'T15' in techs:
  if comp['screen']['power']==0:base+=2
  else:red['screen']+=2
 if 'T22' in techs and all(comp[k]['power']>=1 for k in ['chip','screen']):
  red['chip']+=1;red['screen']+=1
 if 'T24' in techs and fold:supply+=3
 if 'T27' in techs:red['chip']+=2;red['screen']+=2
 if 'T35' in techs:red['chip']+=4
 if 'bodySupply1' in codes and 'body' in stable and comp['screen']['power']<=2:supply+=1
 load=sum(max(0,comp[k]['power']-red[k]) for k in KINDS[:3])
 if load>supply:raise ValueError('供电不足')
 if comp['chip']['spec']>=6:feat.add('性能')
 if comp['camera']['spec']>=6:feat.add('影像')
 if comp['body']['mark']=='轻薄':feat.add('轻薄')
 if supply-load>=4:feat.add('续航')
 if fold:feat.add('折叠')
 if comp['chip']['mark']=='生态':feat.add('生态')
 if 'T02' in techs and comp['camera']['spec']>=3:feat.add('影像')
 if 'T06' in techs:feat.add('生态')
 if 'T11' in techs and fold:feat.add('轻薄')
 if 'T20' in techs and comp['camera']['spec']<=5 and comp['chip']['spec']>=3:feat.add('影像')
 if 'T23' in techs and 'chip' not in stable:feat|={'生态','安全'}
 if 'T34' in techs and '性能' in feat:feat|={'生态','安全'}
 if 'T07' in techs and '性能' in feat:bonus['gaming']+=3
 if 'T08' in techs and comp['camera']['spec']<=5:bonus['photo']+=4
 # Legacy non-chip roles; 6.9 chips are fully declarative.
 if 'systemOffice' in codes and '系统' in fields:bonus['office']+=2
 if 'photoRange2' in codes and 3<=comp['camera']['spec']<=6:bonus['photo']+=2
 if 'bodyOffice1' in codes and comp['body']['mark']=='续航':bonus['office']+=1
 if 'gamingFeature' in codes and comp['screen']['mark']=='性能':feat.add('性能')
 if 'gamingHeadroom' in codes and comp['screen']['mark']=='性能' and supply-load>=2:bonus['gaming']+=3
 if 'systemEco' in codes and '系统' in fields:feat.add('生态')
 if 'gamingMark2' in codes and comp['screen']['mark']=='性能':bonus['gaming']+=2
 permits={r['market'] for r in rules if r['op']=='permit'}
 if price in (18,28):
  if 'officeLowPrice' in codes:permits.add('office')
  if 'massLowPrice3' in codes:bonus['mass']+=3
  if 'massLowMid3' in codes and all(comp[k]['spec']<=7 for k in ('screen','camera')):bonus['mass']+=3
  if 'smoothUI' in codes:bonus['mass']+=2+int(comp['screen']['spec']>=5)
 ids={c['id'] for c in cards}
 if 'T29' in techs and '生态' in feat and external_techs:bonus['office']+=3
 if 'T33' in techs and any(c['type']=='custom' and len(c['components']) in (2,3) for c in cards):
  afee+=3
  if any(c['type']=='custom' and len(c['components']) in (2,3) and c.get('supplier') in set((joint_factories or {}).values()) for c in cards):afee+=2
 return dict(base=base,load=load,supply=supply,headroom=supply-load,features=sorted(feat),bonuses=bonus,permits=sorted(permits),slots=occupied,assemblyFee=max(0,8-afee),cost=max(6,sum(r['batchCost'] for r in rows)+max(0,8-afee)-totaldisc))
