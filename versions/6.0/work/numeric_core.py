"""6.0有限订单与生产的可检查核心，不是完整电子游戏或全卡特效解释器。"""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Iterable
PRICE_MOD={18:6,28:2,38:-2,48:-6}
INCOME={18:1,28:2,38:3,48:4}
FEATURES={'性能','影像','轻薄','续航','折叠','生态'}
@dataclass(frozen=True)
class Offer:
    owner:int
    model:int
    base:int
    age:int
    price:int
    qty:int
    traits:frozenset[str]
    new:bool=False
    deployed:bool=False
    modifier:int=0
    allowed:bool=True
    extra_preference:int=0

def reward_stars(score:int)->int:
    if score<=10:return 0
    if score<=16:return 1
    if score<=24:return 2
    return 3

def enterprise_score(income:int, technology:int)->int:
    return max(income,2*technology)

def end_triggered(income:int, technology:int)->bool:
    return income>=60 or technology>=30

def competitive(o:Offer, preferences:Iterable[str])->int:
    if o.price not in PRICE_MOD:raise ValueError('未授权价格')
    if o.qty<0 or o.age<0:raise ValueError('负批次或负年龄')
    preference=3*len(o.traits.intersection(set(preferences)))+o.extra_preference
    return max(0,o.base+preference+PRICE_MOD[o.price]+o.modifier-3*o.age)

def resolve_market(offers:list[Offer], *, preferences:list[str], budget:int, orders:int, reference:int, priority:list[int])->dict:
    """caller已处理型号进入资格/全部投放库存之和；额外特效以modifier显式传入。"""
    if orders<1:raise ValueError('每市场至少1订单')
    order={p:i for i,p in enumerate(priority)}
    if any(o.owner not in order for o in offers):raise ValueError('缺玩家同分顺序')
    rows=[]
    for o in offers:
        if o.allowed and o.price<=budget and o.qty>0:
            rows.append((competitive(o,preferences),order[o.owner],o.model,False,o))
    rows.append((reference,len(priority),0,True,None))
    rows.sort(key=lambda r:(-r[0],r[1],r[2]))
    remain=orders;sold=[];virtual=0
    for score,_,_,isref,o in rows:
        q=min(remain,1 if isref else o.qty)
        if isref:virtual=q
        elif q:
            sold.append({'owner':o.owner,'model':o.model,'qty':q,'score':score,'cash':q*o.price,'income':q*INCOME[o.price],
                         'challengeStars':reward_stars(reference) if score>reference else 0,
                         'technologyChallenge':bool(score>reference and o.new and o.deployed)})
        remain-=q
    return {'sales':sold,'referenceSold':virtual,'unfilled':remain,'orders':orders}

def reference_award(results:list[dict],owner:int,choice:str)->dict:
    """同公司最多一奖；choice=technology不合格时返回0，不自动把旧机转成技术成果。"""
    if choice not in ('income','technology'):raise ValueError('奖励只能整份一种')
    candidates=[r for m in results for r in m['sales'] if r['owner']==owner and r['challengeStars']>0
                and (choice=='income' or r['technologyChallenge'])]
    stars=max((r['challengeStars'] for r in candidates),default=0)
    return {'income':2*stars if choice=='income' else 0,'technology':stars if choice=='technology' else 0}

def matured_batch_cost(parts:list[dict],era:int,discount:int=0)->int:
    total=2
    for p in parts:
        reduction=min(2,max(0,era-p['era'])) if p['type']=='supply' else 0
        for c in p['components']:total+=max(1,c['batchCost']-reduction)
    return max(6,total-discount)

def base_prototype(parts:list[dict], *, power_reduction:dict[str,int]|None=None, supply_bonus:int=0, base_modifier:int=0)->dict:
    comps=[c for p in parts for c in p['components']]
    kinds=[c['kind'] for c in comps]
    if sorted(kinds)!=sorted(['chip','screen','camera','body']):raise ValueError('必须恰好四类，不拆多项卡')
    c={x['kind']:x for x in comps}
    if (c['screen']['form']=='fold') != (c['body']['form']=='fold'):raise ValueError('折叠必须成对')
    r=power_reduction or {}
    load=sum(max(0,c[k]['power']-r.get(k,0)) for k in ['chip','screen','camera'])
    power=c['body']['power']+supply_bonus
    if load>power:raise ValueError('功耗超过供电')
    traits=set()
    if c['chip']['spec']>=6:traits.add('性能')
    if c['camera']['spec']>=6:traits.add('影像')
    if c['body']['mark']=='轻薄':traits.add('轻薄')
    if power-load>=4:traits.add('续航')
    if c['body']['form']=='fold':traits.add('折叠')
    if c['chip']['mark']=='生态':traits.add('生态')
    return {'base':max(0,sum(x['spec'] for x in comps)+base_modifier),'load':load,'power':power,'surplus':power-load,'traits':sorted(traits)}

@dataclass(frozen=True)
class ProductionState:
    cash:int
    used_company:int
    used_platform:int
    stock:int

def produce(state:ProductionState,qty:int,cost:int, *, company_cap:int=6,platform_cap:int=2,stock_cap:int=4,action_cap:int=2)->ProductionState:
    if not (1<=qty<=action_cap):raise ValueError('本次生产数量不合法')
    if cost<6:raise ValueError('制造费至少6')
    if state.cash<qty*cost:raise ValueError('必须先有现金')
    if state.used_company+qty>company_cap:raise ValueError('公司产能不足')
    if state.used_platform+qty>platform_cap:raise ValueError('平台配额不足')
    if state.stock+qty>stock_cap:raise ValueError('库存上限')
    return ProductionState(state.cash-qty*cost,state.used_company+qty,state.used_platform+qty,state.stock+qty)
