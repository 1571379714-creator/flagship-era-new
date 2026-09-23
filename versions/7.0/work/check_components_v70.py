"""每张配件一种有条件可行配置，非取得路径或平衡见证。"""
import json,itertools
from pathlib import Path
from component_engine import evaluate,KINDS
R=Path(__file__).resolve().parents[1];d=json.loads((R/'work/v70_data.json').read_text());ts={c['id']:c for c in d['technologies']}
parts=d['parts'];witnesses={};attempts=0
tech_options=[(),('T26',),('T09',),('T10',),('T27',),('T35',),('T09','T10'),('T26','T10'),('T26','T27'),('T09','T27'),('T21','T09','T10')]
for target in parts:
 era=target['era'];present={x['kind'] for x in target['components']};missing=[k for k in KINDS if k not in present]
 needed=[]
 for k in missing:
  candidates=[c for c in parts if c['type'] in ('supply','starter') and c['era']<=era and c['components'][0]['kind']==k]
  candidates.sort(key=lambda c:(-c['components'][0]['power'] if k=='body' else c['components'][0]['power'],-c['components'][0]['spec']))
  needed.append(candidates)
 found=None
 for opt in tech_options:
  for fill in itertools.product(*needed):
   cards=[target,*fill];attempts+=1
   try:stats=evaluate(cards,opt,ts,era)
   except ValueError:continue
   found={'parts':[c['id'] for c in cards],'ownPrivateTechnologies':list(opt),'era':era,'result':stats};break
  if found:break
 if not found:raise AssertionError('没有在支持范围内找到配置: '+target['id'])
 witnesses[target['id']]=found
report={'version':'7.0','partWitnesses':len(witnesses),'searchAttempts':attempts,'assumptions':['所选配件实际可取得，芯片和技术先验已可用','所列技术均由本人自主完成，不需外部授权','行动机会、资金、产品位足够；不保证实际牌流或科技前置取得路径'],'limits':['只验证配件数值/兼容与部分研发修正','不穷举价格、偏好、Q/H/U或全部供应关系联动'],'witnesses':witnesses}
(R/'work/component_witnesses_v70.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('part witnesses',len(witnesses),'attempts',attempts)
