"""6.2有限规则模型：统一取牌、稳定引用、单批取消、单市场分单。
用于定向测试，不是全卡特效解释器或电子游玩程序。特效数值由测试显式输入。
不维护年龄、多批库存、平台配额或历史制造成本。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from random import Random
KINDS=('chip','screen','camera','body')
PRICES={18:(6,1),28:(2,2),38:(-2,3),48:(-6,4)}
@dataclass
class Batch:
    stable:tuple[str,...]
    custom:tuple[str,...]
    techs:tuple[str,...]=()
    scheme:str|None=None
    base:int=0
    features:frozenset[str]=frozenset()

@dataclass
class Company:
    catalog:dict[str,dict]
    cash:int=120
    work:int=3
    era:int=1
    library:dict[str,str]=field(default_factory=dict)
    hand:dict[str,str]=field(default_factory=dict) # physical serial -> printed id
    owned:dict[str,str]=field(default_factory=dict)
    products:dict[int,Batch]=field(default_factory=dict)
    completed:set[str]=field(default_factory=set)
    used_verification_eras:set[int]=field(default_factory=set)
    discarded:list[str]=field(default_factory=list)
    removed:list[str]=field(default_factory=list)
    phase:str='work'

    def _work_phase(self):
        if self.phase!='work':raise ValueError('发布锁定后不能安排工作或取消')
    def acquire(self,serial:str,id:str):
        self._work_phase()
        if serial in self.owned:raise ValueError('重复实体序号')
        self.owned[serial]=id;self.hand[serial]=id # no cash payment
    def is_locked(self,kind:str)->bool:
        return any(kind in p.stable for p in self.products.values())
    def install(self,serial:str,discount:int=0):
        self._work_phase()
        if serial not in self.hand:raise ValueError('必须在手中')
        c=self.catalog[self.hand[serial]]
        if c['type'] not in ('supply','starter') or len(c['components'])!=1:raise ValueError('定制不能入稳定库')
        kind=c['components'][0]['kind'];cost=max(0,c['installCost']-discount)
        if self.is_locked(kind):raise ValueError('稳定栏仍有引用')
        if self.work<1 or self.cash<cost:raise ValueError('工作或现金不足')
        if kind in self.library:
            old=self.library[kind];bucket=self.removed if self.catalog[self.owned[old]]['type']=='starter' else self.discarded;bucket.append(old)
        self.work-=1;self.cash-=cost;self.library[kind]=serial;del self.hand[serial]
    def refs(self,stable,custom):
        rows=[];cards=[]
        if len(stable)!=len(set(stable)) or len(custom)!=len(set(custom)):raise ValueError('重复实体或代替种类')
        for kind in stable:
            if kind not in self.library:raise ValueError('无对应库卡')
            c=self.catalog[self.owned[self.library[kind]]]
            if c['era']>self.era:raise ValueError('未来稳定配件不可使用')
            cards.append(c);rows+=c['components']
        for key in custom:
            if key not in self.hand:raise ValueError('定制须在手中且未占用')
            c=self.catalog[self.hand[key]]
            if c['type']!='custom' or c['era']>self.era:raise ValueError('类型或世代不合法')
            cards.append(c);rows+=c['components']
        if Counter(x['kind'] for x in rows)!=Counter(KINDS):raise ValueError('必须恰好完整四类，不拆多项')
        return cards, {x['kind']:x for x in rows}
    def assemble(self,slot:int,stable:tuple[str,...],custom:tuple[str,...],techs=(),scheme=None,*,fee_discount=0,total_discount=0,power_reduction=None,supply_bonus=0,trial=False):
        self._work_phase()
        if not 1<=slot<=4 or slot in self.products:raise ValueError('产品位不空或越界')
        if len(techs)!=len(set(techs)) or len(techs)>2:raise ValueError('普通技术位或重复技术不合法')
        used={t for p in self.products.values() for t in p.techs}
        if set(techs)-self.completed or set(techs)&used:raise ValueError('技术未完成或已占用')
        cards,comps=self.refs(stable,custom)
        if (comps['screen']['form']=='fold') != (comps['body']['form']=='fold'):raise ValueError('折叠不配套')
        red=power_reduction or {};load=sum(max(0,comps[k]['power']-red.get(k,0)) for k in KINDS[:-1]);power=comps['body']['power']+supply_bonus
        if load>power:raise ValueError('供电不足')
        qfee=0
        if scheme:
            if scheme not in self.hand:raise ValueError('Q不在手中')
            q=self.catalog[self.hand[scheme]]
            if q['type']!='scheme' or q['era']>self.era:raise ValueError('Q类型/世代错误')
            qfee=q['developmentCost']
        price=max(6,sum(c['batchCost'] for c in comps.values())+max(0,8-fee_discount)+qfee-total_discount)
        points=0 if trial else 1
        if self.work<points or self.cash<price:raise ValueError('先付款，工作或现金不足')
        f=set()
        if comps['chip']['spec']>=6:f.add('性能')
        if comps['camera']['spec']>=6:f.add('影像')
        if comps['body']['mark']=='轻薄':f.add('轻薄')
        if power-load>=4:f.add('续航')
        if comps['body']['form']=='fold':f.add('折叠')
        if comps['chip']['mark']=='生态':f.add('生态')
        self.work-=points;self.cash-=price
        for key in custom:del self.hand[key]
        if scheme:del self.hand[scheme]
        self.products[slot]=Batch(tuple(stable),tuple(custom),tuple(techs),scheme,sum(c['spec'] for c in comps.values()),frozenset(f))
        return price
    def cancel(self,slot):
        self._work_phase()
        p=self.products.pop(slot)
        for key in p.custom+( (p.scheme,) if p.scheme else () ):self.hand[key]=self.owned[key]
        # cash, work, completed technology and era validation intentionally unchanged
    def verify(self,slot,*,work_cost=2,cash_cost=12,min_base=10,min_features=2):
        self._work_phase();p=self.products[slot]
        if self.era in self.used_verification_eras:raise ValueError('本世代已验证')
        if p.base<min_base or len(p.features)<min_features:raise ValueError('证据不足')
        if self.work<work_cost or self.cash<cash_cost:raise ValueError('费用不足')
        self.work-=work_cost;self.cash-=cash_cost;self.used_verification_eras.add(self.era);return 1
    def finish_release(self,sold:set[int],*,rewards_finished:bool,exported:set[int]|None=None):
        if self.phase!='release' or not rewards_finished:raise ValueError('全部奖励结束前不可释放配置')
        exported=exported or set()
        if sold&exported:raise ValueError('同一批不能成交又出口')
        for slot in sorted(sold|exported):
            p=self.products.pop(slot)
            self.removed.extend(p.custom)
            if p.scheme:
                if slot in sold and self.owned[p.scheme]=='Q21':self.hand[p.scheme]=self.owned[p.scheme]
                else:self.removed.append(p.scheme)
        self.phase='work' # turn sequencing is controlled by caller

@dataclass(frozen=True)
class Offer:
    owner:int
    product:int
    base:int
    price:int
    features:frozenset[str]=frozenset()
    deployed:bool=False
    modifier:int=0
    allowed:bool=True
    tie_priority:bool=False

def stars(score):return 0 if score<=10 else 1 if score<=16 else 2 if score<=24 else 3

def resolve_market(offers,*,budget,preferences,orders,reference,priority):
    if orders<1:raise ValueError('订单至少1')
    if len({(x.owner,x.product) for x in offers})!=len(offers):raise ValueError('同一批重复投放')
    player_rank={p:i for i,p in enumerate(priority)};rows=[]
    for o in offers:
        if o.price not in PRICES or o.owner not in player_rank:raise ValueError('价格或玩家无效')
        if not o.allowed or o.price>budget:continue
        score=max(0,o.base+3*len(o.features&set(preferences))+PRICES[o.price][0]+o.modifier)
        rows.append((score,0 if o.tie_priority else 1,player_rank[o.owner],o.product,o))
    rows.append((reference,2,len(priority),0,None));rows.sort(key=lambda r:(-r[0],r[1],r[2],r[3]))
    left=orders;sales=[];virtual=0
    for score,_,_,_,o in rows:
        if left==0:break
        if o is None:virtual=1
        else:sales.append({'owner':o.owner,'product':o.product,'qty':1,'cash':o.price,'income':PRICES[o.price][1],'score':score,'stars':stars(reference) if score>reference else 0,'techAllowed':o.deployed and score>reference})
        left-=1
    return {'sales':sales,'referenceSold':virtual,'unfilled':left,'orders':orders}

def allocations_valid(destinations:dict[tuple[int,int],list[str]])->bool:
    valid={'mass','gaming','photo','office','A','B','C','hold'}
    return all(len(ds)==1 and ds[0] in valid for ds in destinations.values())

def draw_reference(cards,era,locked,players,rng:Random):
    if set(locked)!=set(range(players)):raise ValueError('尚未全员锁定')
    pool=[c for c in cards if c['era']==era]
    if len(pool)!=6:raise ValueError('必须完整6张候选')
    return rng.choice(pool)

def take_market(display:list,deck:list,selections:list):
    """display含8位，操作选择仅来自开始时公开卡，结束统一补空位。"""
    selected=[];board=display[:];pile=deck[:]
    for x in selections:
        if x=='blind':
            if pile:selected.append(pile.pop(0))
        else:
            if not isinstance(x,int) or not 0<=x<len(board) or board[x] is None:raise ValueError('不能取空位/本次新补牌')
            selected.append(board[x]);board[x]=None
    for i,v in enumerate(board):
        if v is None and pile:board[i]=pile.pop(0)
    return selected,board,pile
