"""6.9独立市场、现抽参考和统一取牌的定向模型；不模拟全卡特效。供应关系状态另见supplier_engine.py。"""
from dataclasses import dataclass
from random import Random
PRICES={18:(6,1),28:(2,2),38:(-2,3),48:(-6,4)}
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
    valid={'mass','gaming','photo','office','A','B','hold'}
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
