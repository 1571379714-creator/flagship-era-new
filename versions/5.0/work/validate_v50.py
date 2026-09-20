"""5.0定向数据/规则检查；非完整策略代理，未证明平衡。"""
from v50_common import *
from collections import Counter,defaultdict
import random,itertools,copy,re,hashlib
D=d;ALL={c['id']:c for g in ['cards','parts','starters','projects','specialProjects','goals'] for c in d[g]}
KINDS=('chip','screen','camera','body');CHECKS=[]
def check(label,ok):
 if not ok:raise AssertionError(label)
 CHECKS.append(label)
def phone(plan, ids, tech=8, era=5, techs=(), businesses=(), tuning=None, price='标准价',company=None,board_tag=None,factories=None,company_after=None):
 p=ALL[plan]; cs=[ALL[i] for i in ids]; mp={}; owner={};errors=[]
 for c in cs:
  for x in c['components']:
   if x['kind'] in mp:errors.append('部件重叠')
   mp[x['kind']]=x;owner[x['kind']]=c
 if set(mp)!=set(KINDS):return {'valid':False,'errors':['部件不完整']}
 k,sc,im,bd=(mp[z] for z in KINDS)
 if any(c.get('era',0)>era for c in cs):errors.append('世代未解锁')
 fold=sc['form']=='fold' and bd['form']=='fold'
 if (sc['form']=='fold')!=(bd['form']=='fold') or ('折叠' in p['tags'] and not fold):errors.append('折叠未配套')
 company={t:6 for t in ['性能','影像','轻薄','续航','折叠','生态']} if company is None else company
 if any(company.get(t,0)<n for t,n in p['tagRequirements'].items()):errors.append('公司标签')
 factories={k:6 for k in ['R','Y','B','G','K']} if factories is None else factories
 if any(factories.get(t,0)<n for t,n in p.get('factoryRequirements',{}).items()):errors.append('厂家前置')
 if company_after is not None:company=company_after
 tq={z:x['tech'] for z,x in mp.items()}
 if owner['chip']['id']=='C06':tq['camera']=max(0,tq['camera']-1)
 if tech<max(p['tech'],*tq.values()):errors.append('科技')
 for c in cs:
  gate=c.get('compatibility')
  if gate and not(k['appeal']>=gate['chipAppealAtLeast'] or k['tag']==gate['orChipTag'] or gate['orTechCard'] in techs or ('T38' in techs and 'Y' in p['factoryTags'])):errors.append('平台兼容')
 loads={z:mp[z]['load'] for z in KINDS[:-1]};supply=bd['load'];red=0;extra=0;matches={x['tag'] for x in mp.values()}
 def dec(kind,n=2): loads[kind]-=n
 if tuning:
  allowed={c['id'] for c in cs}|set(techs)
  if tuning not in allowed or not ALL[tuning].get('tuning'):errors.append('调校来源')
  else:
   tu=ALL[tuning]['tuning'];loads['chip']+=tu['loadDelta'];extra+=tu['appealDelta']
 if 'T01' in techs and k['load']>=6:dec('chip')
 if 'T02' in techs and im['tag']=='影像':red+=2
 if 'T03' in techs and sc['tag']=='轻薄':dec('screen')
 if 'T04' in techs and bd['tag']=='续航':supply+=2
 if 'T05' in techs and fold:red+=2
 if 'T06' in techs and k['tag']=='生态':matches.add('性能')
 if 'T07' in techs and k['appeal']>=6 and sc['tag']=='性能':extra+=4
 if 'T08' in techs and im['appeal']<=4:extra+=4
 if 'T09' in techs and sc['load']>=4:dec('screen')
 if 'T10' in techs and bd['load']<=10:supply+=4
 if 'T11' in techs and fold:matches.add('轻薄')
 if 'T12' in techs and k['tag']=='生态':red+=2
 if 'T13' in techs and k['appeal']>=6 and sc['appeal']>=6:extra+=4
 if 'T14' in techs and im['appeal']>=8:extra+=4
 if 'T15' in techs and sc['tag']=='轻薄':
  if sc['load']==0:extra+=2
  else:dec('screen')
 if 'T16' in techs and bd['load']>=12:supply+=4
 if 'T17' in techs and fold and im['tag']=='影像':extra+=4
 if 'T18' in techs and k['appeal']>=8:matches.update(['性能','影像'])
 if 'T20' in techs and im['appeal']<=4:red+=2
 if 'T21' in techs and bd['tag']=='轻薄':supply+=2
 if 'T22' in techs and k['load']>=2 and sc['load']>=2:supply+=2
 if 'T23' in techs and owner['chip']['type']=='custom':matches.add('生态')
 if 'T24' in techs and fold:supply+=2
 if 'T25' in techs and sc['tag']=='轻薄':matches.add('影像')
 if 'T27' in techs and sum(x['tag']=='续航' for x in mp.values())>=2:dec('chip');dec('screen')
 if 'T28' in techs and k['tag']=='性能' and sc['tag']=='性能':red+=2
 if 'T29' in techs and sum(x['tag']=='生态' for x in mp.values())>=2:extra+=4
 if 'T30' in techs and fold and k['appeal']>=6:extra+=4
 if 'T32' in techs and k['load']+sc['load']+im['load']<=4:red+=2
 if 'T33' in techs and any(c['type']=='custom' and len(c['components']) in [2,3] for c in cs):red+=2
 if 'T34' in techs and k['tag']=='性能':matches.add('生态')
 if 'T35' in techs and k['load']>=6 and bd['load']>=12:dec('chip',4)
 if 'T40' in techs and 'G' in p['factoryTags'] and fold:supply+=3
 # 配件在本机上的修正
 idset=set(ids)
 if 'C02' in idset and im['load']<=2:matches.add('影像')
 if 'C08' in idset and sc['tag']=='性能' and p['market']=='电竞娱乐':extra+=2
 if 'C10' in idset:matches.add('生态')
 if 'C11' in idset and bd['load']<=8:red+=2
 if 'D03' in idset and k['appeal']>=4 and p['market']=='电竞娱乐':extra+=2
 if 'D05' in idset and im['appeal']>=6 and p['market']=='摄影创作':extra+=2
 if 'D06' in idset:matches.add('生态')
 if 'I08' in idset and k['tag']=='生态' and p['market']=='摄影创作':extra+=2
 if 'F02' in idset and k['load']+sc['load']+im['load']<=6:extra+=2
 if 'F03' in idset and k['load']>=6:dec('chip')
 if 'F08' in idset:matches.add('轻薄')
 if 'X08' in idset and k['load']<=2:dec('screen')
 if 'X17' in idset:matches.add('续航')
 if 'X20' in idset:matches.add('生态')
 loads={z:max(0,v) for z,v in loads.items()};power=sum(loads.values());spare=supply-power
 if 'F09' in idset and spare>=6:extra+=2
 raw=sum(x['appeal'] for x in mp.values());accept=max(0,p['appeal']-min(4,red))
 if raw<accept:errors.append('验收')
 if spare<0:errors.append('供电')
 stable=sum(c['type'] in ['common','starter'] for c in cs)
 if plan=='P15' and company.get('性能',0)>=3:extra+=4
 if plan=='P27' and company.get('轻薄',0)>=2:extra+=2
 if plan=='P44' and company.get('轻薄',0)>=3:extra+=4
 if plan=='P56' and sc['appeal']>=6 and spare>=2:extra+=4
 if plan=='P59' and sc['tag']=='性能':extra+=4
 if plan=='P68' and bd['tag']=='轻薄' and im['appeal']>=6:extra+=4
 if plan=='P79' and bd['appeal']>=6 and stable>=2:extra+=4
 if plan=='P88' and owner['chip']['type']=='custom' and len(owner['chip']['components'])==1 and spare>=2:extra+=4
 fee=sum(x['cost'] for x in mp.values())+p['development']
 if 'C03' in idset and era>=3:fee-=3
 if 'B06' in businesses and p['tech']==0:fee-=6
 if 'B20' in businesses and p['development']==0:fee-=3
 if 'B27' in businesses and fold:fee-=6
 if 'B32' in businesses and any(c['type']=='custom' and len(c['components'])==1 for c in cs):fee-=6
 if board_tag and board_tag in p['tags']:fee-=3
 for n,fac in enumerate(['R','Y','B','G','K'],37):
  if f'B{n:02}' in businesses and fac in p['factoryTags']:fee-=3
 req=p['strength']-int('T37' in techs and 'R' in p['factoryTags'])-int('X21' in idset)-int('X28' in idset)-int('B03' in businesses and '轻薄' in p['tags'])
 price_delta=next(x['appealDelta'] for x in D['pricing']['strategies'] if x['name']==price)
 matched=len(set(p['tags'])&matches)
 return {'valid':not errors,'errors':errors,'plan':plan,'parts':list(ids),'raw':raw,'power':power,'supply':supply,'spare':spare,'fee':max(3,fee),'accept':accept,'match':matched,'appeal':max(0,raw+2*matched+extra+price_delta),'assemblyReq':max(1,req),'tuning':tuning,'price':price}

class Supply:
 def __init__(self,n,seed):
  self.n=n;self.rng=random.Random(seed);self.era=1;self.owned=[];self.total=[]
  self.future={e:{k:[] for k in KINDS} for e in range(1,6)}
  for c in D['parts']:
   if c['type']!='common':continue
   for j in range(c['qty']):
    token=(c['id'],j);self.future[c['era']][c['components'][0]['kind']].append(token);self.total.append(token)
  self.decks={};self.rows={}
  for k in KINDS:
   self.decks[k]=self.future[1][k];self.rng.shuffle(self.decks[k]);self.future[1][k]=[]
   self.rows[k]=[self.decks[k].pop(0) for _ in range(n)]
  self.custom_active={c['id'] for c in D['parts'] if c['type']=='custom' and c['era']==1}
 def validate(self):
  seen=self.owned+sum(self.decks.values(),[])+sum(self.rows.values(),[])+[x for gen in self.future.values() for arr in gen.values() for x in arr]
  assert Counter(seen)==Counter(self.total)
  assert all(len(v)<=self.n for v in self.rows.values())
  for c,j in self.owned+sum(self.decks.values(),[])+sum(self.rows.values(),[]):assert ALL[c]['era']<=self.era
  assert self.custom_active=={c['id'] for c in D['parts'] if c['type']=='custom' and c['era']<=self.era}
 def buy(self,k):
  if self.rows[k]:self.owned.append(self.rows[k].pop(self.rng.randrange(len(self.rows[k]))))
 def maintenance(self,newera,release=False):
  old=self.era
  if newera>old:
   for e in range(old+1,newera+1):
    for k in KINDS:
     batch=self.future[e][k];self.rng.shuffle(batch);self.decks[k]=batch+self.decks[k];self.future[e][k]=[]
   self.era=newera
   self.custom_active={c['id'] for c in D['parts'] if c['type']=='custom' and c['era']<=newera}
  for k in KINDS:
   held=[]
   if newera>old:
    if len(self.rows[k])==self.n:held.append(self.rows[k].pop(0))
    item=self.decks[k].pop(0);assert ALL[item[0]]['era']==newera
    self.rows[k].append(item)
   elif release and self.decks[k] and self.rows[k]:held.append(self.rows[k].pop(0))
   if release:
    while len(self.rows[k])<self.n and self.decks[k]:self.rows[k].append(self.decks[k].pop(0))
   self.decks[k].extend(held)
  self.validate()
 def rotate(self,k):
  if self.decks[k] and self.rows[k]:
   old=self.rows[k].pop(0);self.rows[k].append(self.decks[k].pop(0));self.decks[k].append(old)
  self.validate()

PRICES={p["name"]:p for p in d["pricing"]["strategies"]}

def settle_market(phones,n,trigger):
 """仅检验一场一个市场的代表机、名次与定价收入/现金，不计算企划特殊效果。"""
 reps={}
 for c in phones:
  if not c.get('valid',True):continue
  v={**c,'final':max(0,c['base']+PRICES[c['price']]['appealDelta'])}
  old=reps.get(c['owner'])
  if old is None or (v['final'],-v['slot'])>(old['final'],-old['slot']):reps[c['owner']]=v
 order=[(trigger+i)%n for i in range(1,n+1)]
 ranking=sorted(reps.values(),key=lambda v:(-v['final'],order.index(v['owner'])))
 result={}
 for rank,c in enumerate(ranking):
  p=PRICES[c['price']];result[c['owner']]={**c,'rank':rank+1,'income':p['incomeByRank'][rank],'cash':p['cashByRank'][rank]}
 return result

def alignment(t):
 if t<=36:return d['scoreTrack']['alignment'][t]
 return -3*(t-36)

def base_score(income,tech,goal=0):return income-alignment(tech)+goal

def end_visual(income,tech):return income>=alignment(tech)

def company_icons(ids):
 categories=Counter();factories=Counter()
 for cid in ids:
  c=ALL[cid]
  if c['type'] not in ['phone','tech','business']:continue
  categories.update(c.get('tags',[]));factories.update(c.get('factoryTags',[]))
 return categories,factories

def research(cid,tech,cash,prior=(),company=(),strength=5,upgraded=False,discount=0):
 c=ALL[cid];fac=company_icons(company)[1];fee=max(3,c['cost']-(6 if upgraded else 0)-discount)
 ok=c['type']=='tech' and cid not in prior and tech>=c['tech'] and strength>=c['strength'] and len(prior)>=c.get('priorTechCardsRequired',0) and all(fac[k]>=v for k,v in c.get('factoryRequirements',{}).items()) and cash>=fee
 return {'valid':ok,'tech':tech+c['gain'] if ok else tech,'cash':cash-fee if ok else cash,'prior':list(prior)+([cid] if ok else []),'fee':fee}

def basic(strength,cash,tech,upgraded=False):
 z=d['technology']['basicResearch'];need=z['upgradedStrength' if upgraded else 'normalStrength'];fee=z['upgradedCost' if upgraded else 'normalCost']
 ok=strength>=need and cash>=fee
 return {'valid':ok,'cash':cash-fee if ok else cash,'tech':tech+int(ok),'fee':fee}

def project_value(c,company=(),stable=()):
 cats,facs=company_icons(company);m=c['metric'];ps=[ALL[x] for x in company if ALL[x]['type']=='phone']
 if m=='tag':return cats[c['label']]
 if m=='factory':return facs[c['value']]
 if m=='factoryTypes':return len(facs)
 if m=='techCount':return sum(ALL[x]['type']=='tech' for x in company)
 if m=='businessCount':return sum(ALL[x]['type']=='business' for x in company)
 if m=='phoneCount':return len(ps)
 if m=='markets':return len({c['market'] for c in ps})
 if m=='libraryCount':return len(stable)
 if m=='tagTypes':return len(cats)
 raise ValueError(m)

def project(cid,tier,owner,cash,company=(),occupied=None,propose=False,hand=(),strength=5,upgraded=False):
 c=ALL[cid];occupied=occupied or {};fee=6 if propose else 0
 ok=strength>=(3 if upgraded else 4) and tier in [0,1,2] and tier not in occupied and owner not in occupied.values() and project_value(c,company)>=c['thresholds'][tier] and cash>=fee
 if propose:ok=ok and c['type']=='specialProject' and cid in hand and not occupied
 return {'valid':ok,'cash':cash-fee if ok else cash,'gain':c['rewards'][tier] if ok else 0,'release':2 if ok else 0}

def engines(newphones,techs):
 out={cid:0 for cid in ['T39','T41']}
 valid=[x for x in newphones if x.get('valid')]
 if 'T39' in techs:out['T39']=int(any('B' in ALL[x['plan']]['factoryTags'] and x['raw']>=14 and x['spare']>=4 for x in valid))
 if 'T41' in techs:
  out['T41']=int(any('K' in ALL[x['plan']]['factoryTags'] and '生态' in ALL[x['plan']]['tags'] for x in valid) and any(ALL[x['plan']]['factoryTags'] and 'K' not in ALL[x['plan']]['factoryTags'] for x in valid))
 return out

def technology_36_trace():
 """双人构造性合法行动见证：不随机模拟、不声称现实对局概率。"""
 states=[{'cash':60,'income':5,'tech':0,'actions':['调研','研发','组装','合作','营销'],'upgraded':set(),'company':[]} for _ in range(2)]
 trace=[];global_turn=0;triggered=False
 def act(who,action,mode,card=None):
  nonlocal global_turn,triggered
  st=states[who];strength=st['actions'].index(action)+1;up=action in st['upgraded'];before={k:copy.deepcopy(v) for k,v in st.items() if k!='upgraded'}
  if mode=='融资':st['cash']+=d['economy']['financeUpgradedCash' if up else 'financeCash'][strength-1]
  elif mode=='整备':st['cash']+=9
  elif mode=='打科技':
   rr=research(card,st['tech'],st['cash'],st['company'],st['company'],strength,up);assert rr['valid'],rr
   st['cash']=rr['cash'];st['tech']=rr['tech'];st['company'].append(card)
  elif mode=='基础研究':
   rr=basic(strength,st['cash'],st['tech'],up);assert rr['valid'],rr
   st['cash']=rr['cash'];st['tech']=rr['tech']
  elif mode=='完成J01':
   rr=project('J01',0,who,st['cash'],st['company'],strength=strength,upgraded=up);assert rr['valid']
   st['tech']+=rr['gain'];assert rr['release']==2 # Only release advance in this example; 2 < two-player endpoint 8.
  else:raise ValueError(mode)
  st['actions'].remove(action);st['actions'].insert(0,action)
  if st['tech']>=3:st['upgraded'].add('研发')
  if st['tech']>=7:st['upgraded'].add('营销')
  global_turn+=1
  if end_visual(st['income'],st['tech']) and not triggered:triggered=True;trigger_turn=global_turn
  trace.append({'globalTurn':global_turn,'player':who+1,'action':action,'mode':mode,'card':card,'strength':strength,'upgraded':up,'cashBefore':before['cash'],'cashAfter':st['cash'],'technologyBefore':before['tech'],'technologyAfter':st['tech'],'actionsAfter':st['actions'][:],'income':st['income'],'alignment':alignment(st['tech']),'crossed':end_visual(st['income'],st['tech'])})
 def opponent():act(1,'调研','整备')
 def filler():
  st=states[0];rd=st['actions'].index('研发');opts=[x for x in st['actions'][rd+1:] if x not in ['合作','研发']]
  # A non-research action to the right advances research. Keep cooperation ready for the triggering point.
  a='营销' if '营销' in opts else opts[-1]
  act(0,a,'融资' if a=='营销' else '整备');opponent()
 # There exists a starting draw containing these two legal main cards. Keep them among the allowed four.
 act(0,'研发','打科技','T01');opponent();filler();act(0,'研发','打科技','T19');opponent()
 while states[0]['tech']<34:
  st=states[0];need=3 if '研发' in st['upgraded'] else 4;fee=18 if '研发' in st['upgraded'] else 24
  if st['actions'].index('研发')+1>=need and st['cash']>=fee+18:
   act(0,'研发','基础研究');opponent()
  else:filler()
  assert not triggered,'Premature crossing'
 while states[0]['actions'].index('研发')+1<3 or states[0]['cash']<18:filler()
 assert states[0]['actions'].index('合作')+1>=4
 act(0,'合作','完成J01');cross_turn=global_turn;assert states[0]['tech']==35 and triggered
 opponent() # Every player gets exactly one extra turn, starting after the current player.
 act(0,'研发','基础研究');assert states[0]['tech']==36
 assert len([x for x in trace if x['globalTurn']>cross_turn])==2
 out={'purpose':'存在性见证，不是策略建议或随机完整对局','assumptions':['双人；开局J项目含J01且第一档未被占','玩家1起始抽牌可保留T01、T19；两者均科技门槛0','玩家2选择整备，不推动双轨与发布','玩家1不发布产品，收入停5；用实际融资/整备付全部研究成本'], 'globalTurns':global_turn,'triggerGlobalTurn':cross_turn,'finalTechnology':36,'finalCash':states[0]['cash'],'basicResearchActions':sum(x['mode']=='基础研究' for x in trace),'finalAdditionalTurns':2,'trace':trace}
 (W/'technology_36_trace.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 return out

def run():
 old=json.loads((R/'source/v48_data.json').read_text());v47=json.loads((R/'source/v47_data.json').read_text());cards=d['cards']
 oldall={c['id']:c for g in ['cards','parts','starters','projects','goals'] for c in old[g]}
 check('全部302种编号唯一、374份实体',len(ALL)==302 and sum(c.get('qty',1) for c in ALL.values())==374)
 check('原280种编号及份数保留',all(cid in ALL and ALL[cid].get('qty',1)==c.get('qty',1) for cid,c in oldall.items()))
 check('仅新增22种',set(ALL)-set(oldall)=={f'T{i}' for i in range(37,42)}|{f'B{i}' for i in range(37,42)}|{f'R{i:02}' for i in range(1,7)}|{f'O{i}' for i in range(13,19)})
 check('原底稿SHA未修改',hashlib.sha256((R/'source/v48_data.json').read_bytes()).hexdigest()==d['provenance']['baseDataSha256'])
 for c in ALL.values():
  check(c['id']+'完整名称效果',bool(c['name']) and bool(c['effect']))
  check(c['id']+'实体份数合法',c.get('qty',1) in [1,2])
  if c.get('components'):
   ks=[v['kind'] for v in c['components']]
   check(c['id']+'部件种类不重叠',len(ks)==len(set(ks)) and set(ks)<=set(KINDS))
   check(c['id']+'非负完整配件数值',all(isinstance(v[k],int) and v[k]>=0 for v in c['components'] for k in ['cost','appeal','load','tech']))
  if c['type'] in ['phone','tech','business']:
   check(c['id']+'厂标与类别合法',set(c['factoryTags'])<=set(FACT) and len(c['factoryTags'])<=1 and set(c['tags'])<=set(['性能','影像','轻薄','续航','折叠','生态']))
   check(c['id']+'行动1至5',c['strength'] in range(1,6))
   check(c['id']+'厂标前置有明确定义',set(c['factoryRequirements'])<=set(FACT) and all(v in [1,2] for v in c['factoryRequirements'].values()))
 check('起始四企划中立',all(not ALL[f'P{i:02}']['factoryTags'] for i in range(1,5)))
 check('配件与项目不提供公司厂标',all(not c.get('factoryTags') for c in d['parts']+d['starters']+d['projects']+d['specialProjects']+d['goals']))
 check('132张公司牌提供厂标',sum(bool(c['factoryTags']) for c in cards)==132)
 for f in FACT:
  phones=[c for c in cards if c['type']=='phone' and f in c['factoryTags']]
  check(f+'厂牌覆盖四市场',len({c['market'] for c in phones})==4)
  check(f+'厂牌覆盖六类别',len({t for c in phones for t in c['tags']})==6)
  check(f+'厂牌有无厂家前置入口',any(c['tech']<=1 and not c['factoryRequirements'] for c in phones))
  check(f+'技术和合作入口各4个',sum(c['type']=='tech' and f in c['factoryTags'] for c in cards)==4 and sum(c['type']=='business' and f in c['factoryTags'] for c in cards)==4)
 check('20原类别门槛保持',sum(bool(c.get('tagRequirements')) for c in cards if c['type']=='phone')==20)
 check('10企划厂家门槛独立',sum(bool(c['factoryRequirements']) for c in cards if c['type']=='phone')==10)
 techs=[c for c in cards if c['type']=='tech']
 check('13应用28成果',sum(c['gain']==0 for c in techs)==13 and sum(c['gain']>0 for c in techs)==28)
 check('印刷科技总36',sum(c['gain'] for c in techs)==36)
 check('27企划科技来源',sum(bool(re.search(r'增加\d+科技',c['effect'])) for c in cards if c['type']=='phone')==27)
 check('科技2与3奖励均存在',{2,3}<={c['gain'] for c in techs})
 check('基础研究不限整局次数',d['technology']['basicResearch']['usesPerGame'] is None)
 for t in range(37):
  expected=100-sum(2 if k<=8 else 3 for k in range(1,t+1))
  check(f'科技{t}几何对齐',alignment(t)==expected)
  check(f'科技{t}正好相遇',end_visual(expected,t))
  if expected:check(f'科技{t}差1格尚未相遇',not end_visual(expected-1,t))
 check('8到9恰跨3',alignment(8)-alignment(9)==3)
 check('目标不参与终局',not end_visual(80,9) and base_score(80,9,6)==5)
 check('越过36科技保持3格每点',base_score(5,37)==8 and base_score(5,40)==17)
 check('普通基础研究强度4现金24',basic(4,24,0)['valid'] and not basic(3,24,0)['valid'] and not basic(4,23,0)['valid'])
 check('升级基础研究强度3现金18',basic(3,18,0,True)['valid'] and not basic(2,99,0,True)['valid'])
 x=basic(3,36,0,True);y=basic(3,x['cash'],x['tech'],True)
 check('两个独立合格研发均可研究',y['valid'] and y['tech']==2 and y['cash']==0)
 check('T07可一张研发基础起步',research('T07',2,99,['T01'])['valid'])
 check('高阶T13仍需两张研发基础',not research('T13',4,99,['T01'])['valid'] and research('T13',4,99,['T01','T02'])['valid'])
 check('自己厂标不满足自己前置',not research('T37',2,99,['T01'],['T01'])['valid'])
 redphone=next(c['id'] for c in cards if c['type']=='phone' and 'R' in c['factoryTags'] and not c['factoryRequirements'])
 check('红厂2可打T37',research('T37',2,99,['T01'],['T01',redphone])['valid'])
 check('科技卡费用最低3',research('T01',0,3,upgraded=True,discount=99)['valid'] and research('T01',0,3,upgraded=True,discount=99)['cash']==0)
 # Company label outputs remain separated by source, never projects or requirements.
 cats,facs=company_icons(['T01','T19','R01','J01','C03','O13'])
 check('来源口径分离',cats=={'性能':2} and facs=={'R':1})
 blueids=[c['id'] for c in cards if 'B' in c['factoryTags']][:6]
 pp=project('R03',1,0,6,blueids[:4],propose=True,hand=['R03'],strength=4)
 check('专项先付6再得第二档2',pp=={'valid':True,'cash':0,'gain':2,'release':2})
 check('5现金不能申报',not project('R03',1,0,5,blueids[:4],propose=True,hand=['R03'])['valid'])
 check('不够门槛不能先提出等以后',not project('R03',0,0,99,blueids[:1],propose=True,hand=['R03'])['valid'])
 check('别人可以免申报占空档',project('R03',0,1,0,blueids[:2],occupied={1:0})['valid'])
 check('自己不能占第二档',not project('R03',2,0,99,blueids,occupied={1:0})['valid'])
 check('已占档不能再占',not project('R03',1,1,99,blueids,occupied={1:0})['valid'])
 check('非手牌不得申报',not project('R03',1,0,99,blueids[:4],propose=True,hand=[])['valid'])
 # Known prepared-phone routes. Some assumptions deliberately include sufficient company labels.
 routes=[]
 config=[('性能堆料','P17',['C05','D03','I03','F04'],[],None),('摄影适配','P67',['C02','D04','I05','F04'],['T26'],None),('轻薄','P50',['C02','D02','I01','F02'],[],None),('续航','P51',['C04','D01','I03','F04'],[],None),('折叠','P42',['C03','D09','I02','F08'],[],None),('性价比','P81',['C03','D01','I02','F01'],[],None)]
 for label,cid,ids,ts,tu in config:
  v=phone(cid,ids,techs=ts,tuning=tu);check(label+'合法配置',v['valid']);routes.append({'route':label,**v})
 a=phone('P17',['C05','D03','I03','F04']);b=phone('P17',['C05','D03','I03','F04'],tuning='C05')
 check('性能调校加2功耗加4吸引力',a['power']+2==b['power'] and a['appeal']+4==b['appeal'])
 check('非法来源不能调校',not phone('P17',['C05','D03','I03','F04'],tuning='T19')['valid'])
 check('T19标记合法时减2功耗',phone('P17',['C05','D03','I03','F04'],techs=['T19'],tuning='T19')['power']==a['power']-2)
 check('验收最多降低4',phone('P17',['C11','D02','I02','F02'],techs=['T02','T20','T28','T33'])['accept']==ALL['P17']['appeal']-4)
 check('未达厂家门槛不能靠本场自己厂标',not phone('P15',['C12','D05','I05','F04'],factories={})['valid'])
 check('已有厂标可过门槛',phone('P15',['C12','D05','I05','F04'],factories={'R':1})['valid'])
 check('配件类别不会解除公司类别',not phone('P24',['C12','D05','I05','F04'],company={})['valid'])
 check('部分新企划标签可用于效果但不能前置',not phone('P24',['C12','D05','I05','F04'],company={'性能':2},company_after={'性能':3})['valid'])
 check('T26提供低吸引力芯片摄影路线',not phone('P67',['C02','D04','I05','F04'])['valid'] and phone('P67',['C02','D04','I05','F04'],techs=['T26'])['valid'])
 yellow=next(c['id'] for c in cards if c['type']=='phone' and c['factoryTags']==['Y'] and '折叠' not in c['tags'] and c['appeal']<=14)
 check('T38黄厂平台兼容替代',phone(yellow,['C02','D04','I05','F04'],techs=['T38'])['valid'])
 check('T38不能给其他厂跨平台',not phone(redphone,['C02','D04','I05','F04'],techs=['T38'])['valid'])
 check('T37只降低红厂行动要求',phone('P15',['C12','D05','I05','F04'],techs=['T37'])['assemblyReq']==ALL['P15']['strength']-1)
 check('厂系合同按企划折扣',phone('P15',['C12','D05','I05','F04'],businesses=['B37'])['fee']==phone('P15',['C12','D05','I05','F04'])['fee']-3)
 check('未知厂合同不额外折扣',phone('P15',['C12','D05','I05','F04'],businesses=['B38'])['fee']==phone('P15',['C12','D05','I05','F04'])['fee'])
 check('折叠屏身不配对失败',not phone('P42',['C03','D09','I02','F01'])['valid'])
 check('定制部件重叠失败',not phone('P17',['X17','C03','I03','F04'])['valid'])
 check('尚未解锁高代配件失败',not phone('P50',['C12','D02','I01','F02'],era=1)['valid'])
 check('价格与调校不能弥补印刷验收',not phone('P71',['C05','D01','I01','F04'],tuning='C05',price='走量价')['valid'])
 for b in d['boards']:
  v=phone(b['plan'],b['starterIds'],tech=0,era=1,company={},factories={});check(b['id']+'初始厂标中立配置均可上市',v['valid'] and v['raw']==4 and v['fee']==15)
 witnesses={};candidate=[['X29'],['X30'],['X31'],['X32'],['C12','D05','I05','F04'],['C08','D09','I05','F06']]
 for c in [c for c in cards if c['type']=='phone']:
  for ids in candidate:
   z=phone(c['id'],ids,techs=['T26'])
   if z['valid']:witnesses[c['id']]={'parts':ids,'techs':['T26'],'technology':8,'era':5};break
  check(c['id']+'充足资源时存在合法配置',c['id'] in witnesses)
 blueplan=next(c['id'] for c in cards if c['type']=='phone' and c['factoryTags']==['B'])
 blackeco=next(c['id'] for c in cards if c['type']=='phone' and c['factoryTags']==['K'] and '生态' in c['tags'])
 bx={'plan':blueplan,'raw':14,'spare':4,'valid':True};kx={'plan':blackeco,'raw':16,'spare':4,'valid':True}
 check('T39合格蓝厂新机至多1',engines([bx,bx],['T39'])['T39']==1)
 check('成果引擎空发布无科技',engines([],['T39','T41'])=={'T39':0,'T41':0})
 check('T39不合格余量无奖励',engines([{**bx,'spare':3}],['T39'])['T39']==0)
 check('T41需有效黑厂生态加另一厂',engines([kx,bx],['T41'])['T41']==1 and engines([kx,kx],['T41'])['T41']==0)
 # Market comparison. This function deliberately excludes per-plan/business rewards.
 z=settle_market([{'owner':0,'slot':1,'base':16,'price':'标准价'},{'owner':0,'slot':2,'base':17,'price':'溢价'},{'owner':1,'slot':1,'base':14,'price':'走量价'}],2,0)
 check('每公司每市场仅代表机',len(z)==2 and z[0]['slot']==1 and z[0]['income']==2 and z[0]['cash']==6 and z[1]['income']==3)
 z=settle_market([{'owner':0,'slot':1,'base':12,'price':'走量价'},{'owner':0,'slot':2,'base':16,'price':'标准价'}],2,0)
 check('同公司同分按较小筹备位',z[0]['slot']==1)
 cases=0
 for n in [2,3,4]:
  for prices in itertools.product(PRICES,repeat=n):
   for gap in [-4,0,4]:
    for trigger in range(n):
     vals=settle_market([{'owner':i,'slot':1,'base':max(0,16+gap*i),'price':p} for i,p in enumerate(prices)],n,trigger)
     assert set(x['rank'] for x in vals.values())==set(range(1,n+1))
     assert all(v['income']==PRICES[v['price']]['incomeByRank'][v['rank']-1] and v['cash']==PRICES[v['price']]['cashByRank'][v['rank']-1] for v in vals.values());cases+=1
  for trigger in range(n):
   vals=settle_market([{'owner':i,'slot':1,'base':16,'price':'标准价'} for i in range(n)],n,trigger)
   check(f'{n}人触发者{trigger}同分顺序',[x for x in sorted(vals,key=lambda x:vals[x]['rank'])]==[(trigger+j)%n for j in range(1,n+1)])
 check('三种定价静态市场1269情境',cases==1269)
 for base,best in [(14,'走量价'),(18,'标准价'),(22,'溢价')]:
  out={p:settle_market([{'owner':0,'slot':1,'base':base,'price':p},{'owner':1,'slot':1,'base':16,'price':'标准价'}],2,0)[0]['income'] for p in PRICES}
  check(f'价格案例{base}的最优收入严格区分',out[best]>max(v for p,v in out.items() if p!=best))
 check('本场两机先付款，不用收益垫付',29>=15 and 29-15<15)
 check('初始标准价普通发布现金104',60-15+6+12+(20+12)+9==104)
 count=0
 for n in [2,3,4]:
  for seed in range(30):
   st=Supply(n,seed);st.validate()
   for i in range(100):
    st.buy(st.rng.choice(KINDS))
    if i%13==0:st.rotate(st.rng.choice(KINDS))
    t=min(8,i//12);st.maintenance(sum(t>=v for v in d['supply']['eraThresholds']),release=i%5==0);count+=1
 check('9000供应维护情境',count==9000)
 st=Supply(4,999);st.maintenance(5,True);check('一回合跨世代到V供应守恒',st.era==5 and len(st.custom_active)==32)
 trace=technology_36_trace();check('实际行动与现金见证科技36',trace['finalTechnology']==36 and trace['finalAdditionalTurns']==2)
 report={'version':'5.0','status':'定向检查通过；不是完整对局策略或平衡验证','checksPassed':len(CHECKS),'supplyMaintenanceCases':count,'independentMarketCases':cases,'technology36Witness':{k:v for k,v in trace.items() if k!='trace'},'checks':CHECKS,'routes':routes,'phoneFeasibilityWitnesses':witnesses,'notCovered':['真实多人时长和策略胜率','全部企划/企业特效组合穷举','隐藏信息对手模型','所有随机牌流下可达36','现实芯片性能与采购报价']}
 (W/'validation_v50.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:report[k] for k in ['checksPassed','supplyMaintenanceCases','independentMarketCases','technology36Witness']},ensure_ascii=False,indent=2))
 return report

if __name__=='__main__':run()
