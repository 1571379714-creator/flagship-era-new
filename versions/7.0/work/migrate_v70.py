"""7.0 one-off migration from immutable 6.9 source. Not called by build_all.py."""
from pathlib import Path
import json,copy,re,hashlib
R=Path(__file__).resolve().parents[1]; W=R/'work'; S=R/'source'
old=json.loads((S/'v69_data.json').read_text()); d=copy.deepcopy(old)
d.update(version='7.0',subtitle='双行排程与世代竞逐',date='2026-09-23',status='结构改版首测；尚未多人平衡验证')
d['provenance']={'base':'source/v69_data.json','source':'实际6.9完整交付包','remoteWrite':False,'note':'先前7.0只留预览，本次从实际6.9续建；所有7.0输出本次重新生成。'}
p=d['parameters']
for k in ['workPerTurn','drawPerWork','installWork','assemblyWork','cancelWork','coreWork','firstCoreCombinedWork','expansionWork','incomeEnd','technologyEnd']:
 p.pop(k,None)
p.update(releaseLengths={'2':8,'3':12,'4':16},eraThresholds=[0,4,9,15,22],incomeTrackEnd=130,technologyTrackEnd=46,score='收入标记超过科技对应位置的收入格数；未相遇为负分',normalRefreshDiscard=2,performanceThreshold=6,flagshipPriceBase=28,flagshipPriceChip=12,flagshipPriceCamera=8,independentVerificationBase=12)
p['actionsPerTurn']=1;p['firstCoreCombinedAction']='研发';p['expansionActionCost']=0
p['trackSegments']=[{'from':0,'to':8,'incomeCellsPerStep':2},{'from':8,'to':46,'incomeCellsPerStep':3}]
p['noticeCashCost']=3;p['noticeMinimumProducts']=2
names=['调研','供应','研发','制造','合作','运营']
levels=[
 ['取至多2张主牌。','取至多3张主牌。','取至多4张主牌。'],
 ['付费安装1张稳定件。','付费安装1张稳定件；完成后可盲抽1张。','依次付费安装至多2张不同类别稳定件；完成至少1次后可盲抽1张。'],
 ['给1个项目推进1格，可立项。','给1个项目推进2格，可立项。','给1个项目推进4格，可立项。'],
 ['逐批验收付款，组装至多1批。','逐批验收付款，组装至多2批。','逐批验收付款，组装至多3批。'],
 ['处理1项企业事项。','处理1项企业事项；完成后可盲抽1张。','处理1项企业事项；完成后可盲抽2张。'],
 ['取得6现金；或满足宣发条件后付3现金，发布＋1。','取得12现金；或满足宣发条件后付3现金，发布＋1。','取得18现金；或满足宣发条件后付3现金，发布＋2。']]
notes=[
 '牌市与盲抽可混选。选完一次补空位；取得不等于安装或打出。',
 '从手牌选；照卡面普通/伙伴价付款。有引用不能换库。附抽发生在安装之后；不能用刚附抽的牌继续安装。',
 '一次只处理一个项目，不溢出转移。强度2/3实际完成项目，可预告发布＋1。或整次独立验证：付12，真实产品基础≥12且至少2特征，每世代一次得1科技；验证不预告。',
 '每批需独立定制实体与合法技术指派；稳定可共享。每位一批。按强度2/3且实际产出，行动结束可预告＋1/至多2；强度1不预告。',
 '签1合同、建1设施、建立/切换核心（三选一），付款和前置照常。不同时处理两项；抽牌只入手。',
 '宣发须行动开始时本人已有至少2批合法现货；与拿现金二选一。不能空宣发或预领销售款。']
d['actions']=[{'id':f'A0{i+1}','name':n,'type':'action','levels':lv,'note':note} for i,(n,lv,note) in enumerate(zip(names,levels,notes))]
d['actionSystem']={'initialRows':[['调研','供应','制造'],['合作','研发','运营']],'strengthColumns':[1,2,3],'move':'用前位置决定强度；本行其余两张保持顺序放2/3，用牌回1，然后可交换两个1。另一行不自动移动。','resetOnRelease':False,'allAlwaysSelectable':True,'researchProgress':[1,2,4],'manufactureBatches':[1,2,3],'drawCounts':[2,3,4],'installCounts':[1,1,2],'incomeCash':[6,12,18],'noticeSteps':[1,1,2],'noExtraActionDefault':True}
d['publicationAdvance']={'manufacture':'强度2且本次产出并保留≥1批，可＋1；强度3按本次实际产出并保留的批数可＋至多2；强度1不可。','research':'强度2/3研发行动真正完成所选项目可＋1；只立项、只推进、独立验证和奖励完成不预告。','operations':'本人已有2批合法现货，放弃现金并付3，按1/2/3强度可＋1/1/2。','timing':'本次行动全部效果后、阵列整理前决定。可放弃、不存券。只有一项行动，预告达终点后不再取消/换配件。','emptyGuard':'无合法现货时普通推进最多到终点前1；最终发布可为空。'}
d['supplierRules']['core']='已有本厂伙伴，用合作行动选择核心并付12现金。同时至多一家；无未结束联合项目才能切换。首次核心可并入研发立项，费用均照付。'
d['supplierRules']['firstCoreWithJointStart']='已有目标厂伙伴且核心尚未选择时，可在一次研发行动中同付12核心费和联合费，立项并获得本次完整进度额度；费用、前置、同厂部件全满足才执行。以后切换须合作行动。'
d['challengeRewardFamilies'][2]['rule']=d['challengeRewardFamilies'][2]['rule'].replace('工作加速','研发行动加速')
d['challengeRewardFamilies'][4]['rule']=d['challengeRewardFamilies'][4]['rule'].replace('安装工作0','不执行供应行动')
d['challengeRewardFamilies'][5]['rule']=d['challengeRewardFamilies'][5]['rule'].replace('建设工作0','不执行合作行动')
d['researchModes']['progress']='一枚进度片沿0—8条；研发行动强度1/2/3给所选同一项目1/2/4进度（含立项，无额外赠送1格），最多完成一个项目；不溢出转移，合法实验室只给本项目一次加速。'
d['physicalProtocol']['actions']='每人6张行动牌；固定2行3列强度1/2/3；不设通用工作点、禁用区或强度计数器。'
d['physicalProtocol']['tracks']='共享版图上各公司各有收入/科技标记。收入0—130，科技0—46反向。超过端点用数字筹码继续记录，不重走前8步比例。'
d['expansionRules']['cost']=d['expansionRules']['cost'].replace('不花工作','不执行制造行动')
d['expansionRules']['noNormalAssemblyTriggers']=['T31','H16','H20','U01','U02','U11','U14']
d['lifecycle']={k:v.replace('工作阶段','行动阶段').replace('工作点','行动机会') if isinstance(v,str) else v for k,v in d['lifecycle'].items()}
# Fixed anchors plus a gradual series-wide scale. Not benchmark conversion.
specs={'C101':3,'C102':5,'C103':4,'C104':5,'C105':6,'C106':7,'C107':7,'C108':9,'C109':8,'C110':10,'C111':11,'C112':5,'C113':9,'C114':12,'C115':17,'C116':13,'C117':12,'C118':18,'C119':16,'C120':19,
'X101':6,'X102':2,'X109':6,'X110':7,'X113':6,'X114':7,'X115':7,'X120':7,'X123':9,'X124':7,'X125':9,'X126':10,'X127':11,'X128':9,'X135':12,'X136':12,'X137':11,'X138':12,'X139':8,'X144':10,'X147':14,'X148':16,'X149':13,'X150':16,'X151':18,'X152':21,'X159':20,'X160':14,'X163':20,'X164':21}
newcosts={'C108':9,'C110':8,'C111':10,'C114':11,'C115':17,'C116':12,'C117':11,'C118':17,'C119':15,'C120':18,'X127':11,'X135':12,'X136':13,'X137':11,'X138':12,'X144':10,'X147':14,'X148':15,'X149':13,'X150':15,'X151':17,'X152':19,'X159':18,'X160':15,'X163':17,'X164':16}
renames={'X152':('骁龙8EE6〔前瞻〕','骁龙8 Elite Extreme Gen 6'),'X163':('玄戒O3〔待核〕','玄戒O3')}
for c in d['parts']:
 if c['id'] in specs:
  a=next(a for a in c['components'] if a['kind']=='chip');a['spec']=specs[c['id']]
  if c['id'] in newcosts:a['batchCost']=newcosts[c['id']]
  if c['id'] in renames:
   fr,to=renames[c['id']];c['name']=c['name'].replace(fr,to);a['name']=to
   for k in ['chipModel','chipName']:
    if k in c:c[k]=to
   c['cardEvidenceNote']='名称已更新；规格与等效负载为游戏值，不代表统一实测排名。'
 if c['type']=='starter':c['effect']='初始通用配件：开局免费入库，不执行供应行动；每批仍支付本卡制造费。'
 c['lifecycle']=c.get('lifecycle','').replace('工作','行动')
# Rules are declarative; update only concrete matching thresholds, not every number.
for c in d['parts']:
 if c['id'].startswith(('D','I')) or c['type']=='custom' and not any(a['kind']=='chip' for a in c['components']):
  scale={1:{3:3},2:{3:4,4:5},3:{4:6,5:7,6:8},4:{5:8,6:9,7:10},5:{6:10,7:12,8:14}}[c['era']]
  for r in c.get('rules',[]):
   if r.get('op')=='requireChip':
    v=r['value'];nv=scale.get(v,v);r['value']=nv
    c['effect']=c['effect'].replace(f'芯片规格须至少{v}',f'芯片规格须至少{nv}')
   for cond in r.get('when',[]):
    if cond.get('kind')=='chip' and cond.get('field')=='spec':
     v=cond['value'];nv=scale.get(v,v);cond['value']=nv
     c['effect']=c['effect'].replace(f'芯片规格至少{v}',f'芯片规格至少{nv}')
parts={c['id']:c for c in d['parts']}
parts['X136']['effect']='硬件光追：屏幕印刷规格至少7且部署平台领域研发时，电竞娱乐竞争力加3。'
parts['X147']['effect']='高帧光追：屏幕印刷规格至少7且部署平台领域研发时，电竞娱乐竞争力加3。'
for cid in ['X136','X147']:
 parts[cid]['rules']=[{'op':'market','market':'gaming','value':3,'when':[{'kind':'screen','field':'spec','op':'>=','value':7},{'deployedField':'平台'}]}]
parts['X152']['effect']='Adreno Neural Fusion：屏幕印刷规格至少8，且部署平台或系统研发时，电竞娱乐竞争力加4。集成调校占1技术位，不算部署研发。'
parts['X152']['rules']=[{'op':'market','market':'gaming','value':4,'when':[{'kind':'screen','field':'spec','op':'>=','value':8},{'any':[{'deployedField':'平台'},{'deployedField':'系统'}]}]}]
parts['X163']['effect']='端侧AI协同：部署系统研发时，本产品取得生态；若同时部署影像研发，摄影创作竞争力加3。'
parts['X163']['rules']=[{'op':'feature','feature':'生态','when':[{'deployedField':'系统'}]},{'op':'market','market':'photo','value':3,'when':[{'deployedField':'系统'},{'deployedField':'影像'}]}]
# New chip cost preserved as per-batch pressure; keep varied 6.8 relationship discounts.
for cid,inc in {'C108':1,'C111':2,'C115':3,'C116':2,'C118':2,'C119':2,'C120':2}.items():
 parts[cid]['installCost']+=inc;parts[cid]['installPartnerCost']+=inc
# Research/contract/plan interfaces and predicates.
T={c['id']:c for c in d['technologies']}; H={c['id']:c for c in d['contracts']};U={c['id']:c for c in d['facilities']};Q={c['id']:c for c in d['schemes']}
T['T07']['proof']='完成时展示芯片规格至少8的合法样机。'
T['T13']['proof']='完成时展示芯片规格至少10且屏幕规格至少6的合法样机。'
T['T13']['effect']='部署：芯片规格至少10、屏幕规格至少6时，本产品以38或48售价投电竞娱乐或商务办公，竞争力加3。'
T['T18']['proof']='完成时展示芯片规格至少14且具有生态的合法样机。'
T['T28']['effect']='部署：芯片规格至少4即可取得性能特征；不改变芯片印刷规格。'
T['T31']['effect']='工艺：制造行动中，取消一批后紧接着在同产品位组装，本次组装费减6，最低0；每次制造行动最多一次。原款不退，发布扩产不触发。'
T['T32']['effect']='工艺：独立验证门槛改为真实产品基础竞争力至少10、至少1种特征；仍占整次研发行动，付12现金，每当前世代一次得1科技。'
T['T36']['effect']='工艺：每次供应行动的安装上限加1，最多3张不同类别；分别付费并检查引用锁定。奖励签装不受本卡影响，不增加制造或扩产次数。'
T['T39']['proof']='完成时展示基础竞争力至少24、供电余量至少4的合法样机。'
T['T39']['effect']='工艺：选择独立验证的研发行动，完成验证后可给一个已有在研项目追加1进度；不可立项、不溢出、不叠实验室加速，也不预告。验证现金和每世代一次限制照常。'
H['H02']['requirement']='具有性能；芯片印刷规格至少8。'
H['H08']['requirement']='具有折叠，且芯片印刷规格至少7。'
H['H11']['requirement']='基础竞争力至少30；芯片规格至少12或影像规格至少8。'
H['H11'].update(unitPrice=54,totalCash=54)
H['H11']['effect']='签约后2次发布内，一次交付1批满足要求的现货，得54现金、4收入并退6押金。不允许扩产补单。'
H['H18']['effect']='有效期2次发布。安装蓝厂稳定件时，从当前关系卡价再减3，最低0；不增加安装次数，不放宽引用锁定，奖励签装可用。'
H['H19']['effect']='有效期2次发布。每准备期一次，在自己六行动之一开始前可额外安装1张手中绿厂稳定件，支付卡价并查锁定；不执行供应行动、不移动阵列、不触发供应附抽。'
for cid in ['H16','H20']:H[cid]['effect']=H[cid]['effect'].replace('每本人回合首次正常组装','每次制造行动的第一批组装')
U['U01']['effect']='每次制造行动的第一批组装前，可先安装1张手中稳定件；照付入库费并查无引用。不增加制造额度，不触发供应附抽；发布扩产不触发。'
U['U02']['effect']='制造行动组装上限加1，最多4批；逐批付款与占位照常，预告仍最多2格。普通发布末付6维护，否则停用；以后本人行动开始前付6启用。不增加发布扩产。'
U['U03']['effect']='调研行动的取牌上限加1，即强度1/2/3为3/4/5张。先选完再补牌；不作用于供应、合作和奖励附抽。'
U['U04']['effect']='每准备期一次，调研行动可改为看主堆顶5张，留至多2张自己已是伙伴的厂的配件；余牌原顺序置底。不同时拿牌市，也不安装；未来件仍禁提前使用。'
for cid,fields in [('U05','影像'),('U06','电源或散热'),('U07','结构或显示'),('U08','系统或平台')]:
 U[cid]['effect']=f'研发行动推进{fields}项目时，该次所选项目额外推进1格。每次行动一次，不超工期、不转移、不作用于独立验证或发布奖励。'
U['U09']['effect']='同时在研上限从2提高到3。不增加每回合行动次数，也不允许一次研发行动处理多个项目。'
U['U11']['effect']='每次制造行动的第一批组装，通用组装费8减6，最低0；部件、Q、授权费照付。发布扩产不享受本优惠。'
U['U14']['effect']='每次制造行动最多一次：取消一批后紧接同位重新组装，制造总费减3，最低6。不退原款、不增加制造额度；发布扩产不触发。'
U['U18']['effect']='每准备期一次，另一公司实际付正数授权费使用本人署名技术后，可取牌市1张并补空位。含扩产授权；只取牌，不执行额外行动或改变已锁配置。'
for c in d['facilities']:
 c.pop('work',None);c['action']='合作';c['buildActionCost']=1
Q['Q02']['requirement']='引用库内稳定芯片，且芯片规格至多8。'
Q['Q04']['effect']='芯片规格至少5时，本产品取得性能特征。'
Q['Q06']['effect']='48售价的通用门槛改为基础竞争力至少24；不另要求芯片12或影像8。'
Q['Q07']['requirement']='芯片规格至少12。'
Q['Q20']['requirement']='折叠配套且芯片规格至少8。'
Q['Q24']['requirement']='基础竞争力至少24。'
# Demand totals: 7-8 / 11-12 / 15-16. Printed once, never based on player's current inventory.
orders=[(3,1,1,2),(3,2,1,1),(1,1,3,2),(1,1,2,3),(3,1,2,2),(3,1,1,2),(1,2,3,2),(3,1,2,1),(1,1,2,3),(2,2,1,2),(2,1,2,2),(2,2,2,2)]
for c,row in zip(d['demands'],orders):
 for m,base in zip(c['markets'],row):m['ordersByPlayers']={str(n):base+n-2 for n in [2,3,4]}
 c['effect']='本卡在准备期开始公开；按2/3/4人列直接放订单片，不按本场现货动态增减。偏好每项＋3、各一次；预算为最高售价。普通发布整理末更换。'
# Reference scores re-scaled with specs and full product, not multiplied rewards.
baseScores=[[7,4,4,6],[15,13,13,15],[12,22,11,12],[13,11,22,13],[12,12,14,22],[20,20,20,20]]
inc=[0,6,13,20,27]
# Explicit varied per-generation tiers; scores larger do not grant runaway technology.
for c in d['benchmarks']:
 e=c['era']; j=int(c['id'][-1])-1
 for i,m in enumerate(c['markets']):
  score=baseScores[j][i]+inc[e-1]
  m['score']=score;star=0 if score<=14 else 1 if score<=27 else 2 if score<=41 else 3
  m['reward']=star;m['incomeReward']=[0,2,3,4][star];m['technologyReward']=[0,1,1,2][star]
  fam=c['rewardFamily']; val={'cash':[0,8,16,24],'cards':[0,1,2,3],'engineering':[0,1,2,3],'buyback':[0,12,20,28],'installation':[0,3,6,9],'construction':[0,0,3,6]}
  # Source uses persistent internal family keys; map below from display name.
  array={'市场回款':[0,8,16,24],'商情报告':[0,1,2,3],'工程试验':[0,1,2,3],'渠道回购':[0,12,20,28],'供货签装':[0,3,6,9],'建设支持':[0,0,3,6]}[c['specialName']]
  m['specialValue']=array[star]
  if not star:m['specialText']='无'
  else:
   m['specialText']={'市场回款':f'现金＋{array[star]}','商情报告':f'取{array[star]}张','工程试验':f'进度＋{array[star]}','渠道回购':f'另一未售批回购{array[star]}','供货签装':f'安装1张，费减{array[star]}','建设支持':f'建1设施，费减{array[star]}'}[c['specialName']]
 c['effect']='全员锁定后現抽，扩产后最终零售成交且严格超过本格才挑战；每公司每场一次，从本格收入/科技/特色选1。科技及工程奖励须实际部署本人研发。全部当场结清。'.replace('現','现')
d['referenceRules']['rewardScale']='逐格直接读卡：1/2/3星收入2/3/4，科技1/1/2。按难度先区分能否得奖，非所有数值乘倍放大。'
d['versionNote']='7.0整合六卡2×3阵列、成果预告/有货宣发、科技领先换代4/9/15/22、对向130/46双轨，重标全芯片相关门槛与参考/需求。'
d['migration']={'base':'6.9','version':'7.0','mechanicalScope':['action_system','release','dual_tracks','era_thresholds','card_action_interfaces','chip_scale','demand','benchmarks'],'noRemoteWrite':True}
d['numericTuning']['v70']={'status':'首测参数，不宣称平衡','anchors':{'8 Gen 2':12,'8 Gen 3':14,'8 Elite':17},'demandTotals':'7—8/11—12/15—16','publicationLength':[8,12,16]}
# Remove stale version caches; recreate concise chip roster and source display names.
d['chipRoster']=[]
for c in d['parts']:
 if c['id'] in specs:
  a=next(a for a in c['components'] if a['kind']=='chip')
  d['chipRoster'].append({'id':c['id'],'name':a['name'],'era':c['era'],'type':c['type'],'spec':a['spec'],'load':a['power'],'cost':a['batchCost'],'effect':c['effect']})
for x in d.get('chipSources',[]):
 st=json.dumps(x,ensure_ascii=False)
 for fr,to in [v for v in renames.values()]:st=st.replace(fr,to)
 x.update(json.loads(st))
# Clean obsolete working-phase phrases in all current card strings. Historical sources stay unaltered.
for group in ['parts','technologies','contracts','facilities','schemes','benchmarks','demands']:
 for c in d[group]:
  for key in ['effect','lifecycle','expansionPolicy','specialSummary']:
   if isinstance(c.get(key),str):c[key]=c[key].replace('本人工作阶段','本人行动阶段').replace('取消回件、成交消耗','取消回件、成交消耗').replace('安装工作0','不执行供应行动').replace('建设工作0','不执行合作行动').replace('工作加速','研发行动加速')
(W/'v70_data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
changes=[]
for group in ['parts','technologies','contracts','facilities','schemes','benchmarks','demands']:
 prev={x['id']:x for x in old[group]}
 for c in d[group]:
  fields={k:{'old':prev[c['id']].get(k),'new':c.get(k)} for k in set(c)|set(prev[c['id']]) if prev[c['id']].get(k)!=c.get(k)}
  if fields:changes.append({'id':c['id'],'name':c['name'],'group':group,'fields':fields})
(W/'v69_to_v70_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
print('MIGRATED',len(changes),'cards; all',sum(len(d[g]) for g in ['parts','technologies','contracts','facilities','schemes','benchmarks','demands']))
