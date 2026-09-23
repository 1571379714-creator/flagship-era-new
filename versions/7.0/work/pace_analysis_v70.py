"""排程枚举与输入增长轨迹核算；不是完整对局模拟，不输出胜率。"""
from pathlib import Path
import json
from department_engine import Matrix,notice_cap,score,unlocked_era
R=Path(__file__).resolve().parents[1]
schedule=['调研','供应','制造','研发','运营','合作'];m=Matrix();rows=[]
for turn in range(1,19):
 action=schedule[(turn-1)%6];s=m.strength(action);rows.append({'turn':turn,'action':action,'strength':s,'rowsBefore':[r[:] for r in m.rows]});m.finish(action)
# These are declared inputs, NOT simulated choices, actual trades, probabilities or historical game records.
profiles={
 '均衡输入':[([4,5,6,6,7,7,7,8,8],[2,2,2,3,3,3,3,4,5])],
 '科研偏向输入':[([3,3,4,4,4,5,5,6,7,7],[2,2,3,3,3,3,3,3,4,4])],
 '商业偏向输入':[([6,8,9,10,10,11,12,12,12,12],[1,1,1,1,1,1,1,1,2,1])]
}
trajectories={}
for name,arr in profiles.items():
 incrementsR,incrementsT=arr[0];rr=tt=0;history=[];end=None
 for i,(ir,it) in enumerate(zip(incrementsR,incrementsT),1):
  rr+=ir;tt+=it;history.append({'release':i,'incomeIncrement':ir,'techIncrement':it,'income':rr,'technology':tt,'signedDistance':score(rr,tt),'selfLedEra':unlocked_era([tt])})
  if end is None and score(rr,tt)>=0:end=i
 trajectories[name]={'declaredInput':True,'history':history,'crossesAtRelease':end,'finalReleaseIfNoEarlierOtherTrigger':end+1 if end else None,'note':'商业路径需其他玩家推动技术进入第五代；不能据此声称独立商业领航也能两场换代。'}
report={'version':'7.0','type':'排程枚举＋公开输入的增长轨迹算例','isFullGameSimulation':False,'matrixSchedule':rows,'steadyCycle':'每行三卡轮换，第二轮起本序列六行动均强度3；不交换也可持续，但不代表该序列总是最优。','noticeBudget':{'allCashSixTurnsPerCompany':3,'withPublicityInsteadOfCash':5,'publishedTrackPerCompanyEquivalent':4,'assumption':'制造足额3批且仍存在，研发每轮完成1项目。未完成项目则减1推进；无钱或无卡会更慢。'},'trajectories':trajectories,'limits':['输入收入/科技增量是设计预算，不是已执行的完整取得/生产/销售策略','不包括真实牌序、合同、研究证明、全部卡牌联动、定价心理或对手','换代只取全桌最大科技，产量/合同分流/参考竞争仍待多人实测','约2场/代、第五代约2场尚未得到完整对局统计验证']}
(R/'work/pace_budget_v70.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print({k:(v['crossesAtRelease'],v['finalReleaseIfNoEarlierOtherTrigger']) for k,v in trajectories.items()})
