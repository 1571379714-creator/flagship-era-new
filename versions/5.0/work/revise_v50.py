"""从4.8原始数据生成5.0测试数据；原编号保留，新增牌使用新编号。"""
from pathlib import Path
from collections import Counter, defaultdict
import json, copy, re, hashlib
ROOT=Path(__file__).resolve().parent.parent
S=ROOT/'source'; W=ROOT/'work'
old=json.loads((S/'v48_data.json').read_text(encoding='utf-8'))
v47=json.loads((S/'v47_data.json').read_text(encoding='utf-8'))
d=copy.deepcopy(old)
lookup47={c['id']:c for group in ['cards','parts','starters'] for c in v47[group]}
oldby={c['id']:c for group in ['cards','parts','starters','projects','goals'] for c in old[group]}
FACTORIES=[
 {'id':'R','name':'红厂','color':'#B94E48','symbol':'三角','shape':'triangle'},
 {'id':'Y','name':'黄厂','color':'#AD8024','symbol':'六角','shape':'hexagon'},
 {'id':'B','name':'蓝厂','color':'#386F9D','symbol':'菱形','shape':'diamond'},
 {'id':'G','name':'绿厂','color':'#3B805C','symbol':'三叶','shape':'clover'},
 {'id':'K','name':'黑厂','color':'#303B43','symbol':'圆环','shape':'ring'},
]
FN={f['id']:f['name'] for f in FACTORIES}

def scaled_text(text):
    # 只扩大有明确量纲的数值；不改编号、标签数、张数、行动强度或科技点。
    text=re.sub(r'(\d+)现金', lambda m:f'{int(m[1])*3}现金',text)
    text=re.sub(r'(费用减)(\d+)',lambda m:m[1]+str(int(m[2])*3),text)
    text=re.sub(r'(印刷费用合计不超过)(\d+)',lambda m:m[1]+str(int(m[2])*3),text)
    prefixes=[r'吸引力(?:合计)?(?:均)?(?:额外)?(?:至少|至多|不超过|达到|加|减)',
              r'(?:有效|印刷)?功耗(?:合计)?(?:均)?(?:至少|至多|不超过|加|减)',
              r'(?:有效|印刷)?供电(?:余量)?(?:合计)?(?:至少|至多|不超过|加|减)',
              r'验收值减']
    for prefix in prefixes:
        text=re.sub('('+prefix+r')(\d+)',lambda m:m[1]+str(int(m[2])*2),text)
    text=text.replace('计入整机最多减2的上限','计入整机最多减4的上限')
    text=text.replace('公司标签','公司类别标签').replace('不同标签','不同类别标签').replace('种标签','种类别标签')
    return text

d['version']='5.0'
d['status']='五厂协同综合测试版；尚未完成充分多人对局，不宣称平衡。'
d['provenance']={'baseVersion':'4.8','baseDataSha256':hashlib.sha256((S/'v48_data.json').read_bytes()).hexdigest(),
 'revisionDate':'2026-09-20','preserveOriginalIds':True,'newDesign':'五厂标签、较大经济/硬件尺度、多源科技、36格双轨',
 'chipReferences':'沿用4.7/4.8存档；没有把五厂颜色指认为现实品牌。'}
d['factories']=FACTORIES

gain_zero={1,2,3,4,6,19,20,23,25,31,33,34,36}
gain_two={13,14,17,18,27,29,35}
for c in d['cards']:
    b=lookup47[c['id']]
    c['factoryTags']=[];c['factoryRequirements']={}
    c['effect']=scaled_text(c['effect'])
    c['tech']=b['tech']
    if c['type']=='phone':
        c['appeal']*=2
        c['development']*=3
        c['income']={2:3,3:4,4:6,5:8}[c['income']]
    elif c['type']=='business':c['cost']*=3
    elif c['type']=='tech':
        n=int(c['id'][1:]);gain=0 if n in gain_zero else 2 if n in gain_two else 1
        if n==18:gain=3
        oldgain=c['gain'];c['gain']=gain
        c['cost']=c['cost']*3+max(0,gain-oldgain)*4
        c['researchClass']='应用技术' if not gain else '成果技术'
        c['priorTechCardsRequired']=2 if n in range(13,19) else 1 if n in range(7,13) else 0
# Restore outcome-based product research, not arbitrary ranking-only points.
restore=[17,21,22,23,28,30,33,36,38,47,51,55,58,61,63,64,67,76,96]
for c in d['cards']:
    if c['id'] in [f'P{n:02}' for n in restore]:c['effect']=scaled_text(lookup47[c['id']]['effect'])
    if c['id'] in ['P24','P48','P71','P80','P86','P92']:
        c['effect']=c['effect'].replace('增加1科技','增加2科技')
# A performance-engineering result should not depend on finishing second.
by={c['id']:c for c in d['cards']}
by['P24']['effect']='若本机芯片印刷吸引力至少8，且供电余量至少2，额外增加2科技。'
by['P64']['effect']='若本机四项原始吸引力合计至少16，且供电余量至少4，额外增加1科技。'
by['P76']['effect']='若本场你的另一款有效新机也带生态企划标签，且两款企划分属不同厂家，额外增加1科技。无厂标企划不能满足“不同厂家”。'
# Printed phone factories: 4 starter plans are neutral, leaving no excluded fifth starting faction.
# Greedy allocation balances count/market/technology band/category coverage; no color maps to one category.
counts=Counter(); markets=defaultdict(Counter); bands=defaultdict(Counter); tags=defaultdict(Counter)
for c in [x for x in d['cards'] if x['type']=='phone' and int(x['id'][1:])>4]:
    band='entry' if c['tech']<=1 else 'middle' if c['tech']<=4 else 'high'
    choices=[f['id'] for f in FACTORIES]
    n=int(c['id'][1:]);rotation=n%5
    priority=choices[rotation:]+choices[:rotation]
    f=min(priority,key=lambda x:(counts[x],markets[x][c['market']],bands[x][band],sum(tags[x][t] for t in c['tags'])))
    c['factoryTags']=[f];counts[f]+=1;markets[f][c['market']]+=1;bands[f][band]+=1
    for t in c['tags']:tags[f][t]+=1
# 15 old technologies and 15 old business cards also provide printed factories.
for ids in [[1,2,3,4,6],[7,8,9,10,11],[13,14,15,16,17]]:
    for n,f in zip(ids,FACTORIES):by[f'T{n:02}']['factoryTags']=[f['id']]
for ids in [[1,2,3,4,5],[7,8,9,10,11],[13,14,15,16,17]]:
    for n,f in zip(ids,FACTORIES):by[f'B{n:02}']['factoryTags']=[f['id']]
# Ten company-factory gates. They use previously ungated middle/high plans: avoid universal triple gating.
new_gate_ids=[]
for f in FACTORIES:
    cs=[c for c in d['cards'] if c['type']=='phone' and c['factoryTags']==[f['id']] and c['tech']>=2 and not c['tagRequirements']]
    cs.sort(key=lambda c:(c['tech'],c['strength'],c['id']))
    picks=[cs[0],cs[-1]]
    for c,k in zip(picks,[1,2]):c['factoryRequirements']={f['id']:k};new_gate_ids.append(c['id'])
# Five concrete same-factory commercial effects, on existing simpler outcomes.
commercial_candidates={
 'R':[5,8,19,29,35,39,42,65,69,74,78,82,87,90,94],
 'Y':[5,8,19,29,35,39,42,65,69,74,78,82,87,90,94],
 'B':[5,8,19,29,35,39,42,65,69,74,78,82,87,90,94],
 'G':[5,8,19,29,35,39,42,65,69,74,78,82,87,90,94],
 'K':[5,8,19,29,35,39,42,65,69,74,78,82,87,90,94]}
same_factory_effects=[]
for f in FACTORIES:
    available=[by[f'P{n:02}'] for n in commercial_candidates[f['id']] if by[f'P{n:02}']['factoryTags']==[f['id']]]
    c=available[0]
    c['effect']=f'若你的公司有至少3个{f["name"]}厂标，额外获得12现金。本场已成功上市的厂标可以计入。'
    same_factory_effects.append(c['id'])
# Hardware magnitudes. Public generation availability stays exactly as 4.8.
for c in d['parts']+d['starters']:
    c['factoryTags']=[]
    c['effect']=scaled_text(c['effect'])
    c['rulesNote']='世代与个人科技分别检查；配件类别标签不计公司，配件没有五厂厂标。'
    for p,b in zip(c['components'],lookup47[c['id']]['components']):
        p['cost']*=3;p['appeal']*=2;p['load']*=2;p['tech']=b['tech']
parts={c['id']:c for c in d['parts']+d['starters']}
# Nonuniform refinements use the larger integer space. Units are fictional design values.
refinements={
 'C02':{'cost':7,'appeal':3},'C03':{'cost':8},'C04':{'cost':10,'appeal':5},
 'C05':{'appeal':7,'load':9},'C06':{'cost':10,'load':7},'C07':{'cost':13,'appeal':7},
 'C08':{'cost':16,'appeal':9},'C09':{'cost':17,'appeal':11,'load':9},
 'C10':{'cost':19,'appeal':11,'load':5},'C11':{'cost':13,'appeal':7},'C12':{'cost':22,'appeal':13},
 'C13':{'cost':8,'appeal':5},'C01':{'cost':4,'appeal':5},
 'D02':{'cost':5,'appeal':3},'D03':{'appeal':5,'load':5},'D04':{'cost':11,'appeal':5},
 'D05':{'appeal':7},'D07':{'cost':8,'appeal':5},'D08':{'cost':13,'appeal':7,'load':7},
 'D09':{'cost':11,'appeal':5},
 'I02':{'cost':5,'appeal':3},'I03':{'cost':8,'appeal':5},'I04':{'cost':10,'appeal':7},
 'I05':{'cost':16,'appeal':9,'load':7},'I06':{'cost':20,'appeal':11,'load':7},
 'I07':{'cost':11,'appeal':7},'I08':{'appeal':7},'I09':{'cost':11,'appeal':9,'load':9},
 'F02':{'cost':7,'appeal':5,'load':7},'F03':{'cost':8,'load':13},'F04':{'cost':10,'load':18},
 'F05':{'cost':13,'appeal':7,'load':11},'F06':{'cost':16,'appeal':5,'load':13},
 'F07':{'cost':11,'appeal':7,'load':9},'F08':{'cost':11,'appeal':3,'load':9},'F09':{'cost':13,'appeal':5,'load':15},
}
for cid,vals in refinements.items():parts[cid]['components'][0].update(vals)
# Tune custom single-part designs to remain distinct from repeatable supply.
for n in [1,2,3,5,6,9,10,11,13,14]:parts[f'X{n:02}']['components'][0]['appeal']=9
for n in [7,8,12,15,16]:parts[f'X{n:02}']['components'][0]['appeal']=11
parts['X04']['components'][0].update(cost=21,appeal=14,load=7)
parts['X13']['components'][0]['load']=16
parts['X14']['components'][0]['load']=9
# Scale tuning objects (if present) alongside printed text, not only the human description.
for c in d['parts']:
    if isinstance(c.get('tuning'),dict):
        for k,v in c['tuning'].items():
            if isinstance(v,(int,float)) and not isinstance(v,bool):c['tuning'][k]=v*2
# Parallel machine-readable conditions must match the new card text.
for c in d['parts']:
    if c.get('compatibility'):c['compatibility']['chipAppealAtLeast']*=2
by['T19']['tuning']['loadDelta']=-2
by['T19']['tuning']['appealDelta']=-2
parts['F05']['effect']=parts['F05']['effect'].replace('销售现金额外加1','销售现金额外加3')
# Five new factory-specific technology cards: three engineering abilities, two conditional research engines.
tech_new=[
 ('T37','平台复用接口','R','生态',3,2,27,'组装或返工红厂企划机型时，行动要求减1，最低1。不增加任务，不跳过科技、验收或配件完整性检查。'),
 ('T38','影像模组适配层','Y','影像',3,2,28,'黄厂机型的影像部件“平台兼容”条件视为满足；不跳过科技门槛、功耗、验收或折叠配套。'),
 ('T39','能效验证体系','B','续航',4,3,32,'每场发布若你有蓝厂有效新机，其四项原始吸引力至少14且供电余量至少4，增加1科技。每场至多一次；空发布不触发。'),
 ('T40','柔性结构协同','G','折叠',3,2,29,'绿厂机型使用配套折叠屏与折叠机身时，有效供电加3。不增加厂标或类别标签，不改变印刷供电。'),
 ('T41','跨厂互联验证','K','生态',4,3,34,'每场发布若你有带生态类别标签的黑厂有效新机，并有另一款非黑厂、且有厂标的有效新机，增加1科技。每场至多一次；旧机不触发。'),
]
for cid,name,f,tag,s,t,cost,effect in tech_new:
    d['cards'].append({'id':cid,'name':name,'type':'tech','qty':1,'strength':s,'tech':t,'cost':cost,'gain':1,
       'tags':[tag],'factoryTags':[f],'factoryRequirements':{f:2},'priorTechCardsRequired':0,
       'researchClass':'成果技术','effect':effect})
# Five accessible factory contracts; their one printed mark is not a fixed player identity.
for i,(f,tag,cost) in enumerate(zip(FACTORIES,['影像','性能','轻薄','生态','续航'],[19,19,19,19,19]),37):
    name=f['name']+'合作协议'
    effect=f'带{f["name"]}厂标的企划机型，整机费用减3；打出带{f["name"]}厂标的科技卡，费用减3。分别按最低支付3现金处理；不限制使用其他厂牌。'
    d['cards'].append({'id':f'B{i:02}','name':name,'type':'business','qty':1,'strength':2,'tech':0,'cost':cost,
       'tags':[tag],'factoryTags':[f['id']],'factoryRequirements':{},'effect':effect})
# Base projects retain identity/thresholds/rewards. Special projects enter main deck and can be introduced by players.
for j in d['projects']:
    j['qty']=1;j['type']='project';j['label']=j['label'].replace('公司标签','公司类别标签')
    j['effect']='用合作行动占一个合格空档，获得对应科技，推进发布2。每档全桌一人；每人每项目整局一次。'
d['specialProjects']=[]
for n,f in enumerate(FACTORIES,1):
    d['specialProjects'].append({'id':f'R{n:02}','name':f['name']+'平台标准','type':'specialProject','qty':1,
      'metric':'factory','value':f['id'],'label':f['name']+'公司厂标数','thresholds':[2,4,6],'rewards':[1,2,3],
      'factoryTags':[],'proposalCost':6,
      'effect':'可从手牌提出并立即完成：先满足合格空档并额外支付6现金，再公开为全桌项目。完成获得对应科技，推进发布2。其后其他玩家无需申报费；每人每项目仅一次。'})
d['specialProjects'].append({'id':'R06','name':'跨厂互联标准','type':'specialProject','qty':1,
      'metric':'factoryTypes','label':'公司不同厂家种类','thresholds':[3,4,5],'rewards':[2,3,4],
      'factoryTags':[],'proposalCost':6,
      'effect':'可从手牌提出并立即完成：先满足合格空档并额外支付6现金，再公开为全桌项目。完成获得对应科技，推进发布2。其后其他玩家无需申报费；每人每项目仅一次。'})
# Goals don't provide factory marks. Existing O11 qualifying set follows the restored 4.7 gates.
for g in d['goals']:g['qty']=1;g['type']='goal'
next(g for g in d['goals'] if g['id']=='O11')['effect']='每张已上市且印刷科技门槛至少4的企划得2分，最多6分。'
for n,f in enumerate(FACTORIES,13):
    d['goals'].append({'id':f'O{n:02}','name':f['name']+'产品体系','type':'goal','qty':1,'metric':'factoryPhones','value':f['id'],
       'effect':f'每张已上市且印有{f["name"]}厂标的企划得2分，最多6分。科技与企业厂标不按企划计数。'})
d['goals'].append({'id':'O18','name':'跨厂产品组合','type':'goal','qty':1,'metric':'phoneFactoryTypes','value':'',
       'effect':'已上市企划覆盖3／4／5种厂家，得2／4／6分；不足3种得0分。只看企划厂标，不把科技或企业算成产品。'})
# Core parameters: geometric endgame, not a weighted-sum ending rule.
d['scoreTrack']={'incomeMax':100,'technologyMax':36,'earlyStep':2,'lateStep':3,'changeAt':8,
 'technologyUpgradeAt':[3,7],'endCondition':'同一玩家的收入与科技标记相遇或越过；完成当前完整回合后全员各再一回合，再最终发布。',
 'alignment':[100-(2*t if t<=8 else 16+3*(t-8)) for t in range(37)],
 'scoring':'按科技标记指向的收入对齐线计带正负号的收入格距离，再加终局目标。',
 'overflowTechnologyStep':3}
d['economy']={'startingCash':60,'startingIncome':5,'startingTechnology':0,'payoutBase':20,'payoutIncomeMultiplier':1,
 'marketingCash':[12,15,18,21,24],'marketingUpgradedCash':[18,21,24,27,30],
 'financeCash':[18,21,24,27,30],'financeUpgradedCash':[24,27,30,33,36],
 'readyCash':9,'minimumPayment':3,'upgradeDiscount':6,'extraUpgradeCash':9}
d['assembly']={'tagMatchAppeal':2,'maxAcceptanceReduction':4,'thirdSlotTech':5,'thirdSlotPhones':2}
for p in d['pricing']['strategies']:
    p['appealDelta']*=2;p['cashByRank']=[v*3 for v in p['cashByRank']]
    p['incomeByRank']=([3,0,0,0] if p['id']=='price_volume' else [4,2,0,0] if p['id']=='price_standard' else [6,2,0,0])
d['pricing']['settlement']='每公司每市场仅代表机，按定价及名次领取一次市场收入与销售现金；每台有效企划印刷收入及效果另计。'
d['supply']['thresholdStatus']='5.0首测阈值，仍为2／4／6／8；随新科技来源重新测试时点。'
d['supply']['maintenanceTiming']='完整回合末，发布/成长/行动升级后统一维护；最终发布后不维护。'
for a in d['achievements']:
    if a['id']=='A1':a['reward']='一次性获得9现金'
    if a['id']=='A3':a['condition']='科技≥5且已上市企划≥2'
    if a['id']=='A5':a['reward']='永久使科技卡研发费用减3'
    if a['id']=='A6':a['reward']='一次性增加3收入'
    if a['id']=='A7':a['reward']='永久使对应类别标签新机费用减3'
for b in d['boards']:b['special']=b['special'].replace('费用减1','费用减3').replace('公司拥有','公司类别积累拥有')
tech=[c for c in d['cards'] if c['type']=='tech']
d['technology']={'principle':'科技来源多元而有投入；并非每张科技自动给点。',
 'applicationIds':[c['id'] for c in tech if not c['gain']],
 'resultIds':[c['id'] for c in tech if c['gain']],
 'printedGainTotal':sum(c['gain'] for c in tech),
 'productTechIds':[c['id'] for c in d['cards'] if c['type']=='phone' and re.search(r'增加\d+科技',c['effect'])],
 'engineIds':['T39','T41'],
 'basicResearch':{'usesPerGame':None,'normalStrength':4,'normalCost':24,'upgradedStrength':3,'upgradedCost':18,'gain':1,
                  'perAction':1,'note':'每次占用整个研发行动；无整局次数上限，不受科技卡费用减免。'},
 'industryRewards':[1,2,3],'specialCrossFactoryRewards':[2,3,4]}
d['factoryRules']={'providerTypes':['phone','tech','business'],'starterPlansNeutral':True,'partsProvideMarks':False,
 'marksAreNonConsumable':True,'noAutomaticAppeal':True,'noFixedPlayerFaction':True,
 'planGateIds':sorted(new_gate_ids),'existingPlanFactoryEffectIds':same_factory_effects,
 'publishedPlanCounts':dict(counts),'terminology':'类别标签与厂家标签分别计数，绝不合并为十一种。'}
d['physicalAids']={'priceCardsPerPlayer':9,'tuningMarkersPerPlayer':3,'basicResearchMarkersPerPlayer':0,
 'projectMarkersPerPlayer':10,'overflowMarkersPerPlayer':{'income100':1,'technology36':1},'penRequired':False,
 'tuning':'标记放实际调校来源；T19放对应筹备位格。每机至多一个方案。'}
# Keep source action structure; rewrite complete numeric summaries.
d['actions'][1]['front']='二选一：打出1张科技卡，先满足科技、行动、研发基础及厂标门槛，再付费，获得卡面科技并启用能力。或强度至少4，付24现金进行基础研究，增加1科技；每次行动至多一次，整局可重复。'
d['actions'][1]['back']='打出1张科技卡，费用减6，最低3现金，其他前置照常。或强度至少3，付18现金基础研究，增加1科技；每次行动至多一次，整局可重复。不能同次打牌又基础研究。'
d['actions'][3]['front']='打出1张企业卡，满足行动、科技、厂标及费用条件。或强度至少4，完成1个公开产业突破；也可从手牌提出1张专项，额外付6现金并立即完成。两种用途不能混用。'
d['actions'][3]['back']='按顺序打出至多2张企业卡，调整后行动要求之和不超过强度。或强度至少3，完成1个公开项目，或从手牌付6现金提出并完成1个专项；两种用途不能混用。'
d['actions'][4]['front']='市场预热：按强度1至5获得12／15／18／21／24现金，自选推进1至强度格。或融资：获得18／21／24／27／30现金，不推进。不产生债务。'
d['actions'][4]['back']='市场预热：按强度1至5获得18／21／24／27／30现金，自选推进1至强度＋1格。或融资：获得24／27／30／33／36现金，不推进。不产生债务。'
# Deck accounting is explicit, not guessed from source totals.
content=[c for key in ['cards','parts','starters','projects','specialProjects','goals'] for c in d[key]]
d['counts']={'designs':len(content),'physical':sum(c.get('qty',1) for c in content),
 'phone':96,'tech':41,'business':41,'stablePhysical':80,'customPhysical':64,'starterPhysical':16,'baseProjects':12,
 'specialProjects':6,'goals':18,'initialMain':204,'eventualMainExcludingStarting':244,'mainIncludingStarting':248}
assert d['counts']['designs']==302 and d['counts']['physical']==374
assert sum(c['gain'] for c in tech)==36
assert len({c['id'] for c in content})==len(content)
assert all(len(c['factoryTags'])<=1 for c in d['cards'])
W.mkdir(exist_ok=True)
(W/'v50_data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
# Full field-level trace. Additions, replacements and scalar edits are distinguishable.
changes=[]
def walk(before,after,path):
    if isinstance(before,dict) and isinstance(after,dict):
        for k in sorted(before.keys()|after.keys()):
            if k not in before:changes.append({'path':path+'/'+k,'kind':'added','after':after[k]})
            elif k not in after:changes.append({'path':path+'/'+k,'kind':'removed','before':before[k]})
            else:walk(before[k],after[k],path+'/'+k)
    elif before!=after:changes.append({'path':path,'kind':'changed','before':before,'after':after})
for key in ['cards','parts','starters','projects','specialProjects','goals']:
    orig={c['id']:c for c in old.get(key,[])}
    for c in d[key]:
        if c['id'] in orig:walk(orig[c['id']],c,key+'/'+c['id'])
        else:changes.append({'path':key+'/'+c['id'],'kind':'new-card','after':c})
for k in d.keys()-set(['cards','parts','starters','projects','specialProjects','goals']):
    walk(old.get(k),d[k],k)
(W/'v48_to_v50_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('5.0',d['counts']);print('factory phones',counts);print('gates',new_gate_ids,'effect cards',same_factory_effects)
print('Tech totals',len(tech),sum(bool(c['gain']) for c in tech),sum(c['gain'] for c in tech),'product tech',len(d['technology']['productTechIds']))
print('Field changes',len(changes))
