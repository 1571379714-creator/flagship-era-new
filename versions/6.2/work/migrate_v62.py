"""一次性6.1→6.2迁移；不会由日常构建自动执行。"""
from pathlib import Path
import json, hashlib, copy
R=Path(__file__).resolve().parents[1]
p=R/'source/v61_data.json';old=json.loads(p.read_text(encoding='utf8'));d=copy.deepcopy(old)
d.update(version='6.2',subtitle='统一牌流与单批产品',status='结构简化测试版；尚未充分多人实测',date='2026-09-22')
d['provenance']={'sourceVersion':'6.1','sourceFile':'source/v61_data.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'repository':'1571379714-creator/flagship-era-new','remoteStatus':'本轮未读取或修改远端；以用户实际6.1交付包为底稿。'}
p=d['parameters']
for k in ['baseProductionCap','platformQuota','inventoryCapPerModel','agingPenalty','maxAge','offerCapPerModelPerMarket']:p.pop(k,None)
p.update(mainDisplay=8,drawPerWork=2,startingDraw=8,startingKeep=5,installWork=1,assemblyWork=1,batchesPerAssembly=1,assemblyFee=8,minimumAssemblyTotal=6,startingProductCount=0,stableSlotsPerKind=1,independentVerification='每公司每个当前世代至多一次，取消不复位',cancelWork=0,cancelRefund=0,normalRefreshDiscard=2)
d['migration']={'from':'6.1','note':'243种/315张不变；主牌257张开局全入，16初始/30参考/12需求独立。删除年龄、型号库存数、公司产能和芯片配额，所有冲突效果重写。'}
d['deckStructure']={'main':257,'mainDesigns':185,'starters':16,'benchmarks':30,'demands':12,'refresh':'取牌事项/完整奖励结束后一次补空位；期间不滑动、不立即补新选。普通发布末统一弃最左2张、左移补8。'}
d['lifecycle']={'product':'一个产品位＝一批已付款现货；所有配件恰好覆盖四种','stable':'真实卡留四栏库，产品以代替卡引用；任一现存引用都会锁该栏','cancel':'本人工作阶段免费取消；定制及Q回手，代替片收回，部署释放；现金和工作不退','sold':'整场所有奖励处理后，成交批次定制和Q移出（Q21例外），代替片收回，技术释放，产品位清空','unsold':'保持配置与部署及库引用，不老化、不折价；下场重新选择一处去向和价格','replacement':'只在无产品引用时，1工作点从手牌安装1张稳定，支付印刷入库费；撤下稳定进主弃牌，初始移出；无找零/返现','future':'可取得、可付费入库；未来配件不得用于组装或样机；新世代回合末开放，不加牌不洗牌'}
for group in ['technologies','contracts','facilities','schemes']:
 for c in d[group]:c['era']=1;c['deck']='main'
for c in d['parts']:
 c['deck']='initial' if c['type']=='starter' else 'main'
 c['acquisitionCost']=0
 if c['type'] in ('supply','starter'):
  c['installCost']=0 if c['type']=='starter' else 9
  c['lifecycle']='实体一直留同类库栏；产品放稳定部件代替卡。仍有任何产品引用就不能替换。取消/成交不消耗本卡。'
 else:c['lifecycle']='手牌中直接用于组装；整张全部部件同批使用。取消整张回手，成交后整张移出，未售原样留产品中。'
 c['effect']=c['effect'].replace('定型时','组装时').replace('才可定型','才可组装').replace('定型开发费','组装费').replace('通用开发费','组装费').replace('定型不再支付通用6现金开发费','组装费减6，最低0')
parts={c['id']:c for c in d['parts']}
parts['C03']['effect']='成熟平台：本产品四类全部用稳定部件代替卡时，组装总费用减1，最低6；不随世代自动降价。'
parts['C07']['effect']='平台适配：本产品引用稳定屏幕，且屏幕带性能标识时，电竞娱乐竞争力加2。不改变一次组装1批。'
parts['X29']['effect']='整机参考：组装费8减6，最低0；本卡制造费及Q方案费用仍照付。'
# Remove lifecycle/per-generation/capacity references in otherwise simple parts.
for id in ['X30','X31']:parts[id]['effect']=parts[id]['effect'].replace('组装费仍照付','组装费8仍照付')
T={c['id']:c for c in d['technologies']}
for c in T.values():
 c['effect']=c['effect'].replace('定型或无库存改款时','组装时').replace('定型时','组装时').replace('通用开发费','组装费').replace('每型号','每产品')
newT={
'T05':'部署：配套折叠产品的组装费8减6，最低0；本技术须在该次组装中部署。',
'T13':'部署：芯片和屏幕规格均至少6时，本产品以38或48售价投放电竞娱乐或商务办公，竞争力加3。',
'T18':'部署：锁定投放时，可以选择一个本来不合格的零售市场，作为本批唯一去向；不新增特征，不绕预算，不允许一批投两处。',
'T16':'部署：本产品有续航特征且供电余量至少4时，在商务办公把续航偏好计2次；只在需求卡偏好含续航时生效。',
'T19':'部署：组装时可选节能调校，芯片功耗减2、基础竞争力减1。全机至多一种调校，取消重组才可更换。',
'T29':'部署：本产品有生态特征，且本场另有一款己方生态产品投向不同零售市场时，本产品所投市场竞争力加3；双方都须有合法投放，不要求已成交。',
'T31':'工艺：在本人工作阶段取消一批产品后，紧接着花1工作点在刚释放的同一产品位组装时，该次组装费减6，最低0。每本人回合一次；原费用不退。',
'T32':'工艺：独立验证的产品门槛改为基础竞争力至少8且至少1种特征；工作2、现金12和每公司每世代一次仍不变。',
'T33':'部署：本产品含至少1张二项或三项定制时，组装费减3，最低0。本卡也占1个技术槽。',
'T36':'工艺：一次安装工作可依次安装至多2张不同类别的稳定配件，各自支付入库费并检查锁定；不增加组装批数。',
'T37':'工艺：组装的新产品与另一款现存待售产品都引用库内稳定芯片时，本次组装费减3，最低0。共享供货本身无需本卡许可。',
'T39':'工艺：独立验证工作由2降为1，现金仍12；每公司每当前世代只可验证一次，取消产品不能恢复次数。',
'T40':'部署：本产品有效供电加3；折叠配套且机身使用稳定部件代替卡时，商务办公竞争力另加2。',
}
for id,e in newT.items():T[id]['effect']=e
T['T36']['proof']='完成时展示两批现存合法产品；两批均以稳定部件代替卡引用芯片。'
for c in T.values():c['proof']=c['proof'].replace('型号','产品')
H={c['id']:c for c in d['contracts']}
for c in H.values():
 if c['subtype']=='order':
  n=c['units'];price=c['unitPrice'];income=c['unitIncome'];deposit=c['deposit']
  c['requirement']=c['requirement'].replace('同一型号，','每批均须').replace('全部四部件为稳定或初始配件','全部四部件使用稳定部件代替卡')
  c['effect']=f'在签约后2次发布内，一次交付{n}个产品位的现货（每位1批），每批均须满足本卡条件，允许配置不同；不能分次交付。每批得{price}现金、{income}收入；整单{n*price}现金、{n*income}收入，并退{deposit}押金。未交付到期只没收押金，不增加债务。'
  c['batchPolicy']='允许不同配置、每批逐一达标、同场一次交齐'
  c['totalCash']=n*price;c['totalIncome']=n*income
updatesH={
'H16':('库内已有稳定芯片（含初始），本合同不绑定具体卡号。','有效期2次发布。每个本人回合首次组装引用库内稳定芯片的产品，总费用减3，最低6。免费取消不恢复本人回合次数。'),
'H17':('库内已有稳定影像（含初始），本合同不绑定具体卡号。','有效期2次发布。每次组装引用稳定影像的产品，总费用减2，最低6；不是旧部件折价。'),
'H18':('无。','有效期2次发布。安装稳定屏幕的入库费减6，最低0；仍花安装工作，且屏幕栏不能被任何产品引用。'),
'H19':('无。','有效期2次发布。每准备期一次，可在本人工作阶段不花工作点安装1张手中稳定机身；照付入库费且不得解除锁定。'),
'H20':('无。','有效期2次发布。每个本人回合首次组装包含多项定制的产品，总费用减4，最低6；每次仍只生产1批。'),
'H26':('无。','有效期2次发布。每场锁定时选1批产品：该批可投向电竞娱乐而不要求性能特征；仍查预算，且不能再投第二处。'),
'H27':('无。','有效期2次发布。己方合格产品投放摄影创作时，竞争力加2；仍须满足入场资格与预算。'),
'H28':('无。','有效期2次发布。每场己方18售价零售成交的前2批（产品位较小者先），每批额外3现金，不加收入。'),
'H29':('无。','有效期2次发布。分单后可出口1批本场实际投放零售但未成交的合法产品，获得8现金；按成交结束占用并消耗定制和Q，不回手。不加收入、不领挑战奖。不是免费取消。出口不触发Q21等成交奖励。'),
'H30':('另有执行订单合同时才有收益。','有效期2次发布。每完整交付1张H01—H15订单，额外获得6现金；每合同一次。仍需另一个合同槽。'),
}
for id,(req,e) in updatesH.items():
 H[id]['requirement']=req;H[id]['effect']=e;H[id].pop('scope',None)
H['H26']['name']='红厂试销陈列'
U={c['id']:c for c in d['facilities']}
updatesU={
'U01':'每个本人回合首次正常组装前，可顺带从手牌安装1张稳定配件，不另花安装工作；仍付入库费并检查无引用。然后照常组装1批并付款。',
'U02':'每个本人回合另有1枚专用工作点，只能用于一次正常的单批组装，不可保存或挪作他用。每次普通发布末付6维护费，否则停用；本人回合付6可重新启用，但本回合专用点仍只一次。',
'U03':'每个本人回合首次取牌工作可取得至多3张主牌，而非2张；可混选当前牌市与盲抽，全部选完后统一补牌。',
'U04':'每准备期一次，取牌工作可改为查看主牌堆顶5张，留至多2张，其余按原顺序置底。不同时取牌市；未来卡可拿但不可提前用于组装。',
'U11':'每个本人回合首次正常组装的组装费8减6，最低0；工作点、部件制造费及Q费用照付。试产券不触发。',
'U12':'独立验证现金费12减6，最低0；每公司每世代次数不增加。',
'U13':'手牌上限由8提高到10；不增加稳定库栏位或产品位，也不允许未来配件提前用于组装。拆除后本人回合末弃至恢复后的上限。',
'U14':'在本人工作阶段取消一批产品后，紧接着进行的同产品位改款组装，总费用减3，最低6。每本人回合一次；不退原制造费，仍花组装工作。',
'U15':'四种部件全部使用稳定部件代替卡的产品，组装总费用减2，最低6。',
}
for id,e in updatesU.items():U[id]['effect']=e
Q={c['id']:c for c in d['schemes']}
for c in Q.values():
 c['effect']=c['effect'].replace('本型号','本产品').replace('每批','该批').replace('通用开发费','组装费')
 c['lifecycle']='可选，每批至多1张；取消回手，成交移出。每次再组装仍付方案费；Q21按例外。'
updatesQ={
'Q02':('引用库内稳定芯片，且芯片规格至多5。','组装费减3，最低0；不依赖当前世代或旧配件折价。'),
'Q05':('已完成T37；本机与另一现存产品都引用稳定芯片。','本机组装费减6，最低0；不增加生产批次。可与T37叠加，但组装费最低0。'),
'Q11':('影像规格至少6且具有生态。','本机投放摄影或商务，且另一己方合法产品投放其中另一市场时，本机竞争力加2；不要求另一批已成交。'),
'Q16':('芯片规格至少3，且有续航或轻薄。','本机18售价投放大众消费时，与无同类优先能力的其他真人产品同分，本机优先。与同类优先产品同分仍按玩家顺序、产品位顺序。'),
'Q19':('折叠屏与折叠机身配套。','本机具有轻薄，且组装费减3，最低0。'),
'Q21':('至少3种部件使用稳定部件代替卡。','本产品实际成交结束后，只有本Q方案回手而非移出；定制配件照常消耗。下次使用本方案仍付3方案费。取消也按通用规则回手。'),
'Q22':('本机具有生态。','用本产品做独立验证时现金费减6，最低0；每公司每当前世代一次，取消、再造或换产品位不恢复。'),
'Q23':('至少1张多项定制。','本机组装费减4，最低0；可作为需要整合定制属性的研发样机，不因此多生产一批。'),
'Q24':('基础竞争力至少18。','本产品与至少另一批己方产品在不同零售市场实际成交时，额外增加1收入；每场只加一次，不把同一批投到两处。'),
}
for id,(req,e) in updatesQ.items():Q[id]['requirement']=req;Q[id]['effect']=e
# Uniform object naming on active card text.
for group in ['parts','technologies','contracts','facilities','schemes']:
 for c in d[group]:
  for k in ['effect','requirement','proof']:
   if k in c:c[k]=c[k].replace('型号','产品')
# Print actual reference choices per row (no rulebook reward multiplier needed).
d['referenceRules']['technologyGate']='挑战产品在锁定时已部署至少1张完成研发；不再检查首发或代龄。成交后该批清空，不能重复成交领奖。'
d['referenceRules']['specialResolution']='全桌收款和普通成果后、成交产品清空前，按触发者下一位顺时针结算特色奖；新技术不追溯。'
fam={
'cash':('市场回款','按本市场格直接取得印刷现金。',[0,8,16,24]),
'insight':('商情报告','从统一牌市或主牌堆取印刷张数；取得不等于使用，结束后一次补牌。',[0,1,2,3]),
'engineering':('工程试验','已有1项在研增加印刷进度；需挑战批次已部署完成研发，不立项、不溢出、不跳过证明。',[0,1,2,3]),
'endorsement':('渠道推荐','取得印刷加值的推荐章，未来一次发布给一批一个市场；每公司至多留1枚。',[0,2,4,6]),
'sourcing':('供货引荐','取得印刷面额的入库券，未来一次稳定入库减现金；不省工作、不解锁引用，每公司至多1券。',[0,3,6,9]),
'pilot':('试产支持','取得印刷面额的试产券；未来本人回合免费工作组装恰好1批，总费减券面值、最低6；照查世代与空位，每公司至多1券。',[0,0,3,6]),
}
d['challengeRewardFamilies']=[]
for f,(name,summary,vals) in fam.items():d['challengeRewardFamilies'].append({'id':f,'name':name,'description':summary,'byStars':vals})
for c in d['benchmarks']:
 name,summary,values=fam[c['rewardFamily']];c['specialName']=name;c['specialSummary']=summary
 for m in c['markets']:
  s=m['reward'];m['incomeReward']=2*s;m['technologyReward']=s;m['specialValue']=values[s]
  m['specialText']='无奖' if not s else (f'{values[s]}现金' if c['rewardFamily']=='cash' else f'取{values[s]}张' if c['rewardFamily']=='insight' else f'进度+{values[s]}' if c['rewardFamily']=='engineering' else f'推荐+{values[s]}' if c['rewardFamily']=='endorsement' else f'入库券{values[s]}' if c['rewardFamily']=='sourcing' else f'单批试产券 减{values[s]}')
 c['effect']='全员锁价并选定唯一投放后，从本场参考世代6张中现抽。各市场只占1订单，同分真人先。实际零售成交且严格超过本格才可选本格收入、科技或特色其中1奖；每公司每场最多1奖。0星无奖。科技或工程试验另需该批锁定时已部署完成研发；不要求首次参加发布。'
for c in d['demands']:
 for m in c['markets']:
  m['ordersByPlayers']={str(n):max(1,n+m['ordersDelta']) for n in (2,3,4)};m['preferenceBonus']=3
 c['effect']='本卡提前公开；订单按本卡2/3/4人列直接取片。每种已满足偏好加3，通常各一次。预算为最高可接受售价。实际普通发布末才更换。'
d['physicalProtocol']={'handwritingRequired':False,'workTokensPerPlayer':3,'productSlotsPerPlayer':4,'stableSubstitutesPerPlayer':{'chip':4,'screen':4,'camera':4,'body':4},'productDestinationTokensPerPlayer':4,'deployedTechNumberPairs':12,'researchProgressTracks':3,'contractDeadlineTracks':3,'independentVerificationEraCells':5,'retainedRewardTokens':{'endorsement':1,'installVoucher':1,'pilot':1},'stockRule':'每完整配置只是一批，不另用库存数量条。放一个去向片于每产品行，成交时移到已售区；整场结算完才清空。','bankDeposit':'实际现金压合同，退押收回','retiredRecords':'不保留已售产品档案、代龄、型号终身验证、历史制造费','sidebars':'仅例子/操作提示；强制规则仍写正文。'}
(R/'work/v62_data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
# all field-level changes, JSON pointer-style paths.
changes=[]
def diff(a,b,path=''):
 if type(a)!=type(b):changes.append({'path':path,'before':a,'after':b});return
 if isinstance(a,dict):
  for k in sorted(a.keys()|b.keys()):
   if k not in a:changes.append({'path':path+'/'+k,'before':None,'after':b[k]})
   elif k not in b:changes.append({'path':path+'/'+k,'before':a[k],'after':None})
   else:diff(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):changes.append({'path':path,'before':a,'after':b})
  else:
   for i,(x,y) in enumerate(zip(a,b)):diff(x,y,path+'/'+str(i))
 elif a!=b:changes.append({'path':path,'before':a,'after':b})
diff(old,d)
(R/'work/v61_to_v62_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
print('wrote 6.2',len(changes),'field changes')
