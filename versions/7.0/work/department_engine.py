"""7.0六行动、真实成果预告与对向轨道的纯规则核验器。
不提供网页游玩功能；不把卡牌/证据的外部输入当作已验证事实。
"""
from dataclasses import dataclass,field
NAMES=('调研','供应','研发','制造','合作','运营')
INITIAL=(('调研','供应','制造'),('合作','研发','运营'))
@dataclass
class Matrix:
    rows:list=field(default_factory=lambda:[list(r) for r in INITIAL])
    def location(self,name):
        for r,row in enumerate(self.rows):
            if name in row:return r,row.index(name)
        raise ValueError('没有这张行动')
    def strength(self,name):return self.location(name)[1]+1
    def finish(self,name,swap=False):
        r,c=self.location(name);strength=c+1
        rest=[x for x in self.rows[r] if x!=name]
        self.rows[r]=[name]+rest
        if swap:self.rows[0][0],self.rows[1][0]=self.rows[1][0],self.rows[0][0]
        if sorted(sum(self.rows,[]))!=sorted(NAMES):raise AssertionError('行动实体不守恒')
        return strength

def technology_distance(t):
    if not isinstance(t,int) or t<0:raise ValueError('科技为非负整数')
    return 2*t if t<=8 else 3*t-8

def income_alignment(t):return 130-technology_distance(t)
def score(income,technology):return income-income_alignment(technology)
def meets(income,technology):return score(income,technology)>=0
def unlocked_era(technologies):
    highest=max(technologies,default=0)
    return 1+sum(highest>=x for x in (4,9,15,22))

def notice_cap(department,strength,*,new_surviving=0,completed=False):
    if strength not in (1,2,3):raise ValueError('强度越界')
    if department=='制造':
        return 0 if strength==1 or new_surviving<1 else (1 if strength==2 else min(new_surviving,2))
    if department=='研发':return int(strength>=2 and completed)
    return 0

@dataclass
class Publication:
    players:int
    progress:int=0
    final_phase:bool=False
    def __post_init__(self):
        if self.players not in (2,3,4):raise ValueError('只适用2—4人')
    @property
    def end(self):return 4*self.players
    def advance(self,amount,*,legal_products):
        if amount<0:raise ValueError('不能倒退')
        maximum=self.end if legal_products else self.end-1
        self.progress=min(maximum,self.progress+amount)
        return self.progress>=self.end and not self.final_phase
    def publicity(self,strength,cash,own_products,total_products):
        if own_products<2 or total_products<own_products or cash<3:raise ValueError('宣发须本人2批合法现货及3现金')
        fire=self.advance((1,1,2)[strength-1],legal_products=total_products)
        return cash-3,fire
    def reset(self):self.progress=0
