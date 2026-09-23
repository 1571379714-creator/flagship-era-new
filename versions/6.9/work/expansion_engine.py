"""6.9 扩产与订单争夺的定向验证模型，不是可游玩的完整引擎。

输入分数、资格与费用由锁定配置计算后传入；本模块不解释全部卡面文本。
覆盖多市场顺序、一次限额、同分次序、预付款/授权转账与最终分单。
"""
from dataclasses import dataclass
from typing import Mapping, Iterable
from collections import Counter, defaultdict
from copy import deepcopy

MARKETS=('mass','gaming','photo','office')
PRICE_INCOME={18:1,28:2,38:3,48:4}

@dataclass(frozen=True)
class LockedProduct:
    owner:int
    slot:int
    market:str
    score:int
    price:int=28
    eligible:bool=True
    priority_ability:bool=False
    manufacturing:int=13
    royalties:tuple[tuple[int,int],...]=()
    own_research:bool=False

@dataclass(frozen=True)
class Entry:
    source:LockedProduct|None
    score:int
    kind:str  # original, expansion, reference
    @property
    def key(self):
        return ('reference',) if self.source is None else (self.source.owner,self.source.slot,self.kind)

@dataclass(frozen=True)
class MarketSpec:
    orders:int
    reference_score:int
    budget:int=48

class ExpansionError(ValueError):pass

def rank(entries:Iterable[Entry],priority:tuple[int,...]):
    turn={p:i for i,p in enumerate(priority)}
    def key(e):
        if e.kind=='reference':return (-e.score,2,2,len(turn),0)
        p=e.source
        return (-e.score,0 if e.kind=='original' else 1,0 if p.priority_ability else 1,turn[p.owner],p.slot)
    return sorted(entries,key=key)

def allocate(entries,market,priority):
    ordered=rank(entries,priority)
    return ordered,ordered[:market.orders]

class ExpansionRelease:
    """All payments in run precede any sales settlement. Inputs are copied."""
    def __init__(self,products:Iterable[LockedProduct],markets:Mapping[str,MarketSpec],cash:Mapping[int,int],priority:Iterable[int]):
        self.products=tuple(products);self.markets=dict(markets);self.cash=dict(cash);self.priority=tuple(priority)
        if len(self.priority)!=len(set(self.priority)) or not 2<=len(self.priority)<=4 or set(self.priority)!=set(self.cash):raise ExpansionError('玩家及顺序无效')
        if any(not isinstance(v,int) or v<0 for v in self.cash.values()):raise ExpansionError('现金无效')
        if set(self.markets)!=set(MARKETS):raise ExpansionError('需要四个固定市场')
        for m in self.markets.values():
            if not isinstance(m.orders,int) or m.orders<0 or m.reference_score<0 or m.budget not in PRICE_INCOME:raise ExpansionError('订单/参考/预算无效')
        keys=[(p.owner,p.slot) for p in self.products]
        if len(keys)!=len(set(keys)):raise ExpansionError('原产品不可重复占位或跨市场承诺')
        for p in self.products:
            if p.owner not in self.cash or p.slot not in (1,2,3,4) or p.market not in MARKETS+('A','B','hold'):raise ExpansionError('原产品身份或去向无效')
            if p.price not in PRICE_INCOME or p.score<0 or p.manufacturing<6:raise ExpansionError('锁定数值无效')
            authors=[a for a,v in p.royalties]
            if len(authors)!=len(set(authors)) or any(a not in self.cash or a==p.owner or not isinstance(v,int) or v<=0 for a,v in p.royalties):raise ExpansionError('授权必须按外部作者合并正数费用')
        self.done=False
    def run(self,decisions:Mapping[tuple[int,int],bool]|None=None,*,final_release=False):
        if self.done:raise ExpansionError('本场扩产已经结算，不能重复付款或分单')
        self.done=True;decisions=decisions or {};used=set();log=[];payments=[];final={};initial_cash=dict(self.cash)
        for name in MARKETS:
            spec=self.markets[name]
            originals=[Entry(p,p.score,'original') for p in self.products if p.market==name and p.eligible and p.price<=spec.budget]
            entries=originals+[Entry(None,spec.reference_score,'reference')]
            initial_order,initial_sold=allocate(entries,spec,self.priority)
            initial_winners={x.key for x in initial_sold};queue=[e for e in initial_order if e.kind=='original']
            for e in queue:
                p=e.source;key=(p.owner,p.slot)
                _,current=allocate(entries,spec,self.priority)
                if e.key not in initial_winners:reason='initial_no_order'
                elif e.key not in {x.key for x in current}:reason='displaced'
                elif p.owner in used:reason='company_used'
                elif not decisions.get(key,False):reason='declined'
                else:
                    copy=Entry(p,e.score,'expansion');_,trial=allocate(entries+[copy],spec,self.priority)
                    if e.key not in {x.key for x in trial} or copy.key not in {x.key for x in trial}:reason='copy_no_order'
                    elif self.cash[p.owner]<p.manufacturing+sum(v for a,v in p.royalties):reason='insufficient_cash'
                    else:
                        self.cash[p.owner]-=p.manufacturing+sum(v for a,v in p.royalties)
                        for a,v in p.royalties:self.cash[a]+=v
                        payments.append({'owner':p.owner,'slot':p.slot,'bank':p.manufacturing,'royalties':[list(x) for x in p.royalties]})
                        entries.append(copy);used.add(p.owner);reason='expanded'
                log.append({'market':name,'owner':p.owner,'slot':p.slot,'status':reason})
            ordered,sold=allocate(entries,spec,self.priority)
            # From-high-to-low insertion guarantees accepted copies survive final allocation.
            assert all(x in sold for x in entries if x.kind=='expansion')
            sales=[{'owner':e.source.owner,'slot':e.source.slot,'copy':e.kind=='expansion','score':e.score,'price':e.source.price,'cash':e.source.price,'income':PRICE_INCOME[e.source.price],
                    'strictReferenceWin':e.score>spec.reference_score,'ownResearch':e.source.own_research} for e in sold if e.kind!='reference']
            final[name]={'ranking':[list(e.key) for e in ordered],'sales':sales,'referenceSold':any(e.kind=='reference' for e in sold),'unfilled':max(0,spec.orders-len(sold)),'orders':spec.orders}
        cleanup=defaultdict(set)
        for m in final.values():
            for s in m['sales']:cleanup[s['owner']].add(s['slot'])
        bank=sum(p['bank'] for p in payments)
        assert sum(initial_cash.values())-sum(self.cash.values())==bank
        return {'markets':final,'decisions':log,'expansions':payments,'cashBefore':initial_cash,'cashAfterExpansion':dict(self.cash),'bankPaid':bank,'usedCompanies':sorted(used),
                'cleanupOriginalGroups':{str(a):sorted(slots) for a,slots in cleanup.items()},'finalRelease':final_release,
                'notSimulated':['卡面全部资格/分数计算','合同整单付款与完整奖励解释器','主牌抽取、U18选牌及隐藏对手策略']}

def retail_card_rewards(sales,*,q15_groups=(),q21_groups=(),q24_groups=(),h28_eligible=(),t41_group=None):
    """Targeted batch-vs-group reward cases. Every other effect is excluded."""
    totals=defaultdict(lambda:{'cash':0,'income':0,'technology':0,'q21Returns':0,'q24Income':0})
    q15=set(q15_groups);q21=set(q21_groups);q24=set(q24_groups);h28=set(h28_eligible)
    soldgroups={(s['owner'],s['slot']) for s in sales};eligible18=[]
    for s in sales:
        k=(s['owner'],s['slot']);t=totals[s['owner']]
        t['cash']+=s['cash'];t['income']+=s['income']
        if k in q15 and s['price']==18:t['income']+=1
        if k==t41_group and not s['copy']:
            t['income']-=s['income'];t['technology']+=1
        if k in h28 and s['price']==18:eligible18.append(s)
    for a in totals:
        eligible=sorted([s for s in eligible18 if s['owner']==a],key=lambda s:(s['slot'],s['copy']))[:2]
        totals[a]['cash']+=3*len(eligible)
        totals[a]['q21Returns']=len({k for k in q21 if k[0]==a and k in soldgroups})
        # Caller supplies groups whose cross-market requirement has already been checked.
        totals[a]['q24Income']=len({k for k in q24 if k[0]==a and k in soldgroups})
        totals[a]['income']+=totals[a]['q24Income']
    return dict(totals)

def manufacturing_quote(data,parts,techs=(),scheme=None,*,active_cards=(),joint_factories=(),other_original_stable_chip=False):
    """Expansion cost only. No first-normal-assembly, cancellation or turn triggers.
    Card legality/proof is checked before calling; uses current/frozen parameters,
    not historical cash spent. Does not recalculate the locked market score.
    """
    from component_engine import evaluate
    tech_catalog={t['id']:t for t in data['technologies']}
    stats=evaluate(parts,techs,tech_catalog,era=5,joint_factories={str(i):f for i,f in enumerate(joint_factories)})
    cards={c['id']:c for g in ['schemes','facilities','contracts','technologies'] for c in data[g]}
    s=cards.get(scheme);active=set(active_cards);ts=set(techs)
    stable={r['kind'] for p in parts if p['type'] in ('supply','starter') for r in p['components']}
    components={r['kind']:r for p in parts for r in p['components']}
    suppliers={r['kind']:p.get('supplier') for p in parts for r in p['components']}
    # evaluate covers declared part discounts and T33; quote adds remaining eligible cost-only effects.
    afee=stats['assemblyFee'];extra_total=0
    if 'T05' in ts and components['body']['form']=='fold':afee=max(0,afee-6)
    if 'T37' in active and 'chip' in stable and other_original_stable_chip:afee=max(0,afee-3)
    discounts={'Q01':4,'Q02':3,'Q19':3,'Q23':4}
    if scheme in discounts:afee=max(0,afee-discounts[scheme])
    if scheme=='Q05' and other_original_stable_chip:afee=max(0,afee-6)
    if 'H17' in active and suppliers.get('camera')=='Y':extra_total+=2
    if 'U15' in active and len(stable)==4:extra_total+=2
    # Preserve declared total discounts already returned by the part evaluator.
    part_cost=sum(x['batchCost'] for p in parts for x in p['components'])
    declared_total=part_cost+stats['assemblyFee']-stats['cost']
    amount=max(6,part_cost+afee+(s['developmentCost'] if s else 0)-max(0,declared_total)-extra_total)
    return {'parts':part_cost,'assembly':afee,'scheme':s['developmentCost'] if s else 0,'manufacturing':amount,
            'excludedNormalTriggers':sorted(active&{'T31','H16','H20','U01','U02','U11','U14'}),'royaltiesExcluded':True}
