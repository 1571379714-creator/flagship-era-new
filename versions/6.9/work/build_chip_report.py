"""导出完整50芯片名单、苹果专长、改名前后值与证据边界；不改数据。"""
from pathlib import Path
from collections import Counter
import json,html
R=Path(__file__).resolve().parents[1];W=R/'work';O=R/'outputs';E=lambda x:html.escape(str(x))
def build_chip_report():
 d=json.loads((W/'v69_data.json').read_text());old=json.loads((R/'source/v68_data.json').read_text());p={c['id']:c for c in d['parts']};op={c['id']:c for c in old['parts']};src={s['cardId']:s for s in d['chipSources']};f={x['id']:x['name'] for x in d['factories']};roster=d['chipRoster'];pages=[];md=['# 旗舰元年6.9 · 50芯片名录与特色','每款只出现一次。规格／负载／费用均为游戏数值；没有跨芯片统一实测证明。苹果保留完整名称；定制套装是游戏工程方案。']
 def tb(h,rr):return '<table><thead><tr>'+''.join('<th>'+E(x)+'</th>'for x in h)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+E(x)+'</td>'for x in r)+'</tr>'for r in rr)+'</tbody></table>'
 def mdt(h,rr):return '\n'.join(['| '+' | '.join(h)+' |','| '+' | '.join(['---']*len(h))+' |']+['| '+' | '.join(str(x).replace('\n','<br>')for x in r)+' |'for r in rr])
 def page(title,content):
  n=len(pages)+1;pages.append(f'<section class="report-page"><header><b>旗舰元年 / 6.9</b><span>五十平台与芯片专长</span></header><h1>{E(title)}</h1>{content}<footer>卡面参数为游戏设计；来源支持范围与待核内容见资料说明。<span>{n}</span></footer></section>')
 counts=Counter(x['family']for x in roster);summary=[['骁龙',counts['Qualcomm']],['曦力／天玑',counts['MediaTek']],['苹果',counts['Apple']],['麒麟',counts['Kirin']],['玄戒',counts['XRing']],['猎户座',counts['Exynos']],['Google Tensor',counts['Google']],['紫光展锐',counts['UNISOC']]]
 page('01 五十款，一款不重复','<div class="lead">指定40款＋补充10款＝50款。<br>20张稳定芯片＋30张含芯片定制，每代4＋6。<br>没有删天玑1200，没有把芯片池缩成40，也不改变主牌257张。</div>'+tb(['芯片系列','款数'],summary)+'<h2>读表方式</h2><p>后五页分别列出每代10个芯片：卡号、来源方式、规格、等效负载、芯片行制造费、伙伴入库价与完整特性。套装其余部件仍须全部使用并另外支付对应制造费。</p><p>普通／伙伴只用于稳定入库；定制不入库。苹果全称：A11—A16 Bionic，A17—A20 Pro。初始通用芯片另计。</p><div class="note">新确定的名单不代表每个最新型号都已取得完整现实参数。8EE6/O3保留前瞻待核；9050无后缀版本和T760原始发布档案的缺口另列，不伪造精确参数。</div>')
 md+=['## 总数',mdt(['系列','款数'],summary)]
 for era in range(1,6):
  rr=[]
  for x in [x for x in roster if x['era']==era]:
   c=p[x['card']];a=next(v for v in c['components']if v['kind']=='chip');rr.append([c['id']+'\n'+a['name'],('稳定'if c['type']=='supply'else str(len(c['components']))+'项定制')+'\n'+f[c['supplier']],f'{a["spec"]} / {a["power"]} / {a["batchCost"]}',(f'{c["installCost"]} / {c["installPartnerCost"]}'if c['type']=='supply'else'—'),c['effect']])
  title=f'0{era+1} 第{era}代 / {2015+2*era}—{2016+2*era}'
  page(title,'<p>规格／负载／芯片费三数分别列示；最后一项不是整机总制造费。此页世代是游戏使用窗口，不是十款芯片的共同发布年份。</p>'+tb(['卡号与完整名称','卡种／厂','规格 / 负载 / 芯片费','入库 普/伙','卡面完整特色'],rr))
  md+=['## '+title,mdt(['卡号与完整名称','卡种/厂','规格/负载/芯片费','入库普/伙','完整特色'],rr)]
 changed=[]
 for x in roster:
  c=p[x['card']];b=op[c['id']];aa=next(v for v in c['components']if v['kind']=='chip');bb=next(v for v in b['components']if v['kind']=='chip')
  if aa['name']!=bb['name']:
   changed.append([c['id'],bb['name'],aa['name'],' / '.join(str(bb[k])+'→'+str(aa[k])for k in ['spec','power','batchCost'])])
 page('07 十二处名称变更','<p>其余38个芯片名称保持；有些保留名称的苹果技术特色重新设计。X102不再是骁龙710；最新麒麟按用户指定家族名，不擅自补Pro后缀。</p>'+tb(['卡号','6.8原名称','6.9完整名称','规格／负载／芯片费'],changed)+'<div class="note">七个更换平台的芯片行发生数值变更；C112同时重定入库价8／2。套装非芯片行、研发模式费用与工期、科技收益、需求和参考值均未改动。来源身份、时代与能力强度分别检查，不强迫不同平台保留原值。</div>')
 md+=['## 十二处名称变化',mdt(['卡号','原名','现名','规格/负载/芯片费'],changed)]
 apples=[]
 for x in roster:
  if x['family']=='Apple':
   c=p[x['card']];apples.append([c['id']+' '+x['name'],c['effect']])
 page('08 苹果十代，不只加同一个分','<p>完整商业名称用于所有卡标题、套装芯片行和名录。每项特色是游戏工程方案，不意味着可以向现实中的苹果购买对应裸芯片或授权。</p>'+tb(['完整名称','玩法角色'],apples)+'<div class="note">技术必须实际部署并满足授权、关联厂商和技术位；单有芯片名称不等于已研究任何技术。A20 Pro和8EE6等集成占位规则继续有效，扩产不重复释放技术位。</div>')
 md+=['## 苹果十代',mdt(['完整名称','特色'],apples)]
 page('09 证据和验证边界','<h2>本轮新读取与沿用明确分开</h2><p>本轮针对更换型号、苹果特色及部分新平台读取了第一方资料。未重新核对的旧来源明确标为沿用，不把历史浏览当作本轮核验。完整50项来源说明见《芯片资料与设计边界》。</p><h2>四类需要保留的限定</h2>'+tb(['对象','处理'],[['唐古拉T760','HMD终端资料确认型号、6nm与5G应用；原始首发年月未完整取得，第三代窗口是批准的游戏归档。'],['麒麟990／9050','使用家族简称。990历史资料包含5G变体；9050本轮第一方资料明确Pro，不能冒充无后缀版本的参数。'],['骁龙8EE6／玄戒O3','仍为前瞻／待核占位，不编造性能测量和供货关系。'],['苹果与其他垂直平台','套装是游戏整合方案，不声称存在真实折叠苹果或跨厂裸片出售。']])+'<h2>平衡检查关注实际使用条件</h2><p>检查所有配件的可行组合；给重写能力做达标和不达标的条件测试；保留授权付款、扩产先付款和初始配件回归测试。已有“每代稳定规格差不超过3”并不是玩家规则，加入较弱T760后不能为了通过旧断言而虚增它的规格。</p><p>这些不是完整对局。实际牌流、资本周转、真人反制、全卡能力叠加、打印机套准与真实硬件统一功耗测试，均未由静态检查证明。</p>')
 css='''@page{size:A4;margin:8mm}*{box-sizing:border-box}body{margin:0;background:#edf2f4;color:#203b45;font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif}.report-page{width:194mm;min-height:281mm;height:281mm;position:relative;background:#fff;margin:15px auto;padding:6mm 4mm 14mm;break-after:page}.report-page:last-child{break-after:auto}header{display:flex;justify-content:space-between;font-size:8pt;border-bottom:1px solid #aac3cc;padding-bottom:3mm;color:#56727c}h1{font-size:20pt;color:#196676;margin:5mm 0 3mm}h2{font-size:12pt;margin:4mm 0 2mm}p{font-size:9.4pt;line-height:1.6;margin:2mm 0}.lead,.note{padding:3mm 4mm;background:#edf5f7;border-left:3px solid #397d8b;font-size:10pt;line-height:1.65;margin:3mm 0}table{border-collapse:collapse;width:100%;font-size:8.2pt;line-height:1.4;margin:3mm 0}th,td{padding:1.4mm 1.2mm;border-bottom:1px solid #c9d9df;vertical-align:top;text-align:left;white-space:pre-line}th{background:#e4eff2}tr:nth-child(even){background:#f5f8f9}td:first-child{min-width:26mm}td:last-child{min-width:45mm}tr{break-inside:avoid}footer{position:absolute;bottom:4mm;left:4mm;right:4mm;display:flex;justify-content:space-between;border-top:1px solid #b8ccd4;padding-top:2mm;font-size:7.3pt;color:#647c84}@media print{body{background:white}.report-page{margin:0}}'''
 (O/'旗舰元年_6.9_50芯片名录与特色.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>旗舰元年6.9 50芯片名录与特色</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>',encoding='utf8')
 md+=['## 来源与边界','来源逐卡记录于《芯片资料与设计边界》。本轮新读取与历史沿用分开。T760年代、9050后缀、8EE6/O3完整参数缺口保留。所有卡面数字与套装均为游戏抽象，不是现实性能排名或供货合同。']
 (O/'旗舰元年_6.9_50芯片名录与特色.md').write_text('\n\n'.join(md)+'\n',encoding='utf8')
 (W/'chip_report_manifest.json').write_text(json.dumps({'version':'6.9','pages':len(pages),'chipRows':50,'appleRows':10,'renamedRows':len(changed),'families':dict(counts)},ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':build_chip_report()
