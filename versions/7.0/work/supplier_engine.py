"""7.0定向状态验证器，不是全卡解释器或电子游玩功能。
验证供应关系、科研所有权、授权资金、单批使用和清理；合同/设施事件及
原科研证据用调用方已核验的布尔证据注入，不能据此声称穷举全卡。
"""
from __future__ import annotations
from dataclasses import dataclass,field
from collections import Counter
from component_engine import evaluate,KINDS

@dataclass
class Research:
    tid:str
    owner:str
    factory:str|None
    progress:int

@dataclass
class PublicTechnology:
    tid:str
    author:str
    factory:str
    uses:dict[str,int]=field(default_factory=dict)

@dataclass
class Product:
    cards:list[str]
    stable:tuple[str,...]
    custom:tuple[str,...]
    techs:tuple[str,...]
    scheme:str|None
    cost:int
    fees:dict[str,int]
    component_suppliers:dict[str,str|None]

@dataclass
class Player:
    name:str
    cash:int=120
    partners:set[str]=field(default_factory=set)
    core:str|None=None
    library:dict[str,str]=field(default_factory=dict)
    hand:set[str]=field(default_factory=set)
    completed:set[str]=field(default_factory=set)
    products:dict[int,Product]=field(default_factory=dict)
    research:dict[str,Research]=field(default_factory=dict)
    tech:int=0

class Network:
    def __init__(self,data,players='ABCD'):
        self.cards={c['id']:c for c in data['parts']+data['technologies']+data['schemes']}
        self.techs={c['id']:c for c in data['technologies']}
        self.players={n:Player(n) for n in players};self.public={};self.phase='action';self.era=1;self.active=None
        self.removed=[];self.discarded=[];self.bank_paid=0
    def begin(self,name,department,strength):
        if self.phase!='action' or self.active is not None:raise ValueError('已有行动或发布中')
        if department not in ('调研','供应','研发','制造','合作','运营') or strength not in (1,2,3):raise ValueError('行动/强度无效')
        self.active={'owner':name,'department':department,'strength':strength,'used':0,'kinds':set()}
    def end(self):
        if self.active is None:raise ValueError('没有进行中的行动')
        result=self.active;self.active=None;return result
    def working(self):
        if self.phase!='action':raise ValueError('只能在本人正常行动阶段处理')
    def require_action(self,name,department):
        self.working()
        if self.active is None or self.active['owner']!=name or self.active['department']!=department:raise ValueError('不是所需部门行动')
        return self.active
    def locked(self,p,kind):return any(kind in b.stable for b in p.products.values())
    def add_partner(self,p,factory,event):
        if factory and event in ('install','custom_assembly','order_fulfilled','validation_fulfilled'):
            p.partners.add(factory)
    def install(self,name,cid,discount=0,*,reward=False):
        if reward:
            if self.phase!='post_cleanup':raise ValueError('奖励安装要等统一清理')
        else:self.require_action(name,'供应')
        p=self.players[name];c=self.cards[cid]
        if cid not in p.hand or c['type']!='supply':raise ValueError('非手中稳定')
        kind=c['components'][0]['kind']
        if self.locked(p,kind):raise ValueError('稳定仍被引用')
        fee=max(0,(c['installPartnerCost'] if c['supplier'] in p.partners else c['installCost'])-discount)
        if not reward:
            a=self.active;cap=(1,1,2)[a['strength']-1]
            if a['used']>=cap or kind in a['kinds']:raise ValueError('供应安装额度或类别重复')
        if p.cash<fee:raise ValueError('现金不足')
        if not reward:a['used']+=1;a['kinds'].add(kind)
        p.cash-=fee;self.bank_paid+=fee;p.hand.remove(cid)
        old=p.library.get(kind)
        if old:(self.removed if self.cards[old]['type']=='starter' else self.discarded).append(old)
        p.library[kind]=cid;self.add_partner(p,c['supplier'],'install');return fee
    def core_cooperate(self,name,factory):
        a=self.require_action(name,'合作');p=self.players[name]
        if a['used']:raise ValueError('已处理企业事项')
        if factory not in p.partners:raise ValueError('尚非伙伴')
        if p.core==factory:raise ValueError('已是本厂核心，无需重复投入')
        if any(r.factory for r in p.research.values()):raise ValueError('联合项目未结束')
        if p.cash<12:raise ValueError('费用不足')
        a['used']=1;p.cash-=12;self.bank_paid+=12;p.core=factory
    def _available_evidence_part(self,p,factory,kind):
        ids=set(p.hand)|set(p.library.values())
        return any(c.get('supplier')==factory and c.get('era',1)<=self.era and
                   c['type'] in ('supply','custom') and any(x['kind']==kind for x in c['components']) and
                   (c['type']=='custom' or p.library.get(kind)==c['id'])
                   for c in (self.cards[cid] for cid in ids) if 'components' in c)
    def research_action(self,name,tid,joint=False,discount=0,slots=2,*,first_core=None,original_proof=False,prototype_cards=None,bonus_progress=0):
        a=self.require_action(name,'研发');p=self.players[name];t=self.techs[tid]
        if a['used']:raise ValueError('一次研发只能处理一个项目')
        if bonus_progress<0:raise ValueError('加速不能为负')
        fee=0
        if tid not in p.research:
            if tid not in p.hand or tid in self.public or any(tid in q.completed or tid in q.research for q in self.players.values()):raise ValueError('项目非手中未使用实体')
            if len(p.completed)<t['prerequisiteProjects'] or len(p.research)>=slots:raise ValueError('项目数或槽位不足')
            factory=None;core_fee=0
            if first_core is not None:
                if not joint or p.core is not None or first_core not in p.partners:raise ValueError('首次核心合并前置不足')
                core_fee=12
            if joint:
                if not t['jointEligible'] or not (p.core or first_core):raise ValueError('不允许联合')
                factory=p.core or first_core
                if not self._available_evidence_part(p,factory,t['relatedPart']):raise ValueError('无可用本厂关联部件')
            fee=max(6,(t['jointCost'] if joint else t['cost'])-discount)+core_fee
            if p.cash<fee:raise ValueError('费用不足')
            p.cash-=fee;self.bank_paid+=fee;p.hand.remove(tid)
            if first_core is not None:p.core=first_core
            p.research[tid]=Research(tid,name,factory,0)
        r=p.research[tid];target=t['jointWork'] if r.factory is not None else t['selfWork']
        a['used']=1;r.progress=min(target,r.progress+(1,2,4)[a['strength']-1]+bonus_progress)
        if r.progress<target or not original_proof:return {'fee':fee,'completed':False,'progress':r.progress}
        if r.factory:
            if not prototype_cards:return {'fee':fee,'completed':False,'progress':r.progress}
            try:evaluate(prototype_cards,era=self.era)
            except ValueError:return {'fee':fee,'completed':False,'progress':r.progress}
            if not any(c.get('supplier')==r.factory and any(x['kind']==t['relatedPart'] for x in c['components']) for c in prototype_cards):return {'fee':fee,'completed':False,'progress':r.progress}
        p.completed.add(tid);p.tech+=t['gain'];del p.research[tid]
        if r.factory:self.public[tid]=PublicTechnology(tid,name,r.factory)
        return {'fee':fee,'completed':True,'progress':target}
    def abandon(self,name,tid):
        self.working();p=self.players[name];del p.research[tid];self.discarded.append(tid)
    def assemble(self,name,slot,stable=(),custom=(),techs=(),scheme=None,*,total_discount=0):
        a=self.require_action(name,'制造');p=self.players[name]
        if a['used']>=a['strength']:raise ValueError('制造额度已用完')
        if not 1<=slot<=4 or slot in p.products:raise ValueError('产品位不空')
        if len(stable)!=len(set(stable)) or len(custom)!=len(set(custom)) or len(techs)!=len(set(techs)):raise ValueError('重复来源')
        parts=[]
        for k in stable:
            if k not in p.library:raise ValueError('无库内来源')
            parts.append(self.cards[p.library[k]])
        for cid in custom:
            if cid not in p.hand or self.cards[cid]['type']!='custom':raise ValueError('定制已占用或非手中')
            parts.append(self.cards[cid])
        qfee=0
        if scheme:
            if scheme not in p.hand or self.cards[scheme]['type']!='scheme' or self.cards[scheme]['era']>self.era:raise ValueError('Q来源或世代')
            qfee=self.cards[scheme]['developmentCost']
        suppliers={a['kind']:c.get('supplier') for c in parts for a in c['components']}
        used={t for b in p.products.values() for t in b.techs};mismatch=[];payments={};outside=[]
        for tid in techs:
            if tid not in self.techs or self.techs[tid]['scope']!='deployment':raise ValueError('非部署技术')
            if tid in used:raise ValueError('本公司同项已有一批')
            if tid in self.public:
                tech=self.public[tid];t=self.techs[tid]
                if tech.factory not in p.partners:raise ValueError('无本厂伙伴')
                if suppliers.get(t['relatedPart'])!=tech.factory:mismatch.append(tid)
                if tech.author!=name:
                    payments[tech.author]=payments.get(tech.author,0)+t['licenseFee'];outside.append(tid)
            elif tid not in p.completed:raise ValueError('不是自有成果或公开技术')
        # Q08 prerequisite proof is included for this targeted modifier.
        if scheme=='Q08':
            rows={a['kind']:a for c in parts for a in c['components']}
            if not any(t in self.public for t in techs) or any(rows.get(k,{}).get('spec',0)<5 for k in ('screen','camera')):raise ValueError('Q08前置不足')
        if mismatch:
            if len(mismatch)!=1 or not ('T34' in techs or scheme=='Q08'):raise ValueError('关联部件不匹配')
            if mismatch==['T34'] and scheme!='Q08':raise ValueError('T34不能豁免自身')
        stats=evaluate(parts,techs,self.techs,self.era,external_techs=outside,joint_factories={t:self.public[t].factory for t in techs if t in self.public})
        cost=max(6,stats['cost']+qfee-total_discount)
        if p.cash<cost+sum(payments.values()):raise ValueError('制造和全部授权必须预付')
        # All guards passed: atomic payment and pointers. Triggered card rewards are outside this finite model.
        a['used']+=1;p.cash-=cost+sum(payments.values());self.bank_paid+=cost
        for author,fee in payments.items():self.players[author].cash+=fee
        for cid in custom:p.hand.remove(cid)
        if scheme:p.hand.remove(scheme)
        p.products[slot]=Product([c['id'] for c in parts],tuple(stable),tuple(custom),tuple(techs),scheme,cost,payments,suppliers)
        for tid in techs:
            if tid in self.public:self.public[tid].uses[name]=slot
        for c in parts:
            if c['type']=='custom':self.add_partner(p,c['supplier'],'custom_assembly')
        return cost,payments
    def own_deployed(self,name,slot):return any(t in self.players[name].completed for t in self.players[name].products[slot].techs)
    def temporary_technology_allowed(self,name,tid):
        p=self.players[name]
        return tid in p.completed and all(tid not in b.techs for b in p.products.values())
    def _release(self,name,slot,cancel=False):
        p=self.players[name];b=p.products.pop(slot)
        for tid in b.techs:
            if tid in self.public:self.public[tid].uses.pop(name,None)
        if cancel:p.hand.update(b.custom);p.hand.update([b.scheme] if b.scheme else [])
        else:self.removed.extend(b.custom+((b.scheme,) if b.scheme else ()))
    def cancel(self,name,slot):self.working();self._release(name,slot,True)
    def finish_release(self,finished,*,evidence_done=False):
        if self.phase!='release' or not evidence_done:raise ValueError('发布证据未完')
        for name,slots in finished.items():
            if any(slot not in self.players[name].products for slot in slots):raise ValueError('无实际产品')
        for name,slots in finished.items():
            for slot in slots:self._release(name,slot)
        self.phase='post_cleanup'
