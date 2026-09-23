"""从现行数据导出50芯片、需求及参考的完整对照；不是基准测试报告。"""
from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1];O=R/'outputs';E=lambda v:html.escape(str(v))
def build_chip_report():
 d=json.loads((R/'work/v70_data.json').read_text());old=json.loads((R/'source/v69_data.json').read_text());before={c['id']:c for c in old['parts']};ps=[c for c in d['parts'] if c['type']!='starter' and any(a['kind']=='chip' for a in c['components'])];pages=[];md=['# 7.0 芯片与市场校准总表','全部数字为游戏设计。以实际6.9数据逐字段对照；不声称统一跑分或实测瓦数。']
 css='''*{box-sizing:border-box}body{font-family:"Noto Sans CJK SC",sans-serif;color:#203e4a;margin:0;background:#e7eff2}.report{width:190mm;height:277mm;background:white;padding:4mm;margin:12px auto;position:relative}h1{font-size:23pt;margin:1mm 0 6mm}h2{font-size:17pt;margin:4mm 0}p{font-size:10pt;line-height:1.65}table{border-collapse:collapse;width:100%;font-size:8.3pt;line-height:1.5}th,td{border:1px solid #a8bec7;padding:2mm;vertical-align:top}th{background:#e7f0f3}.foot{position:absolute;bottom:2mm;font-size:8pt;color:#5a7a86}@page{size:A4 portrait;margin:10mm}@media print{body{background:white}.report{margin:0;break-after:page}.report:last-child{break-after:auto}}'''
 def table(headers,rows):return '<table><tr>'+''.join('<th>'+E(h)+'</th>'for h in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+E(x)+'</td>'for x in r)+'</tr>' for r in rows)+'</table>'
 def pg(title,body):pages.append(f'<section class="report"><h1>{title}</h1>{body}<div class="foot">旗舰元年7.0 · 数据直接导出 · {len(pages)+1}</div></section>')
 for era in range(1,6):
  eraCards=[c for c in ps if c['era']==era];rows=[]
  for c in eraCards:
   a=next(x for x in c['components'] if x['kind']=='chip');b=next(x for x in before[c['id']]['components'] if x['kind']=='chip')
   rows.append([c['id']+' '+a['name'],f'{b["spec"]} → {a["spec"]}',a['power'],f'{b["batchCost"]} → {a["batchCost"]}',f'{c["installCost"]}/{c["installPartnerCost"]}'if c['type']=='supply'else'定制不入库'])
  pg(f'第{era}代 · 芯片数值',table(['型号','规格','负载','芯片费','入库普/伙'],rows)+'<p>稳定每次制造与扩产照付芯片费；入库是一次投入。负载保持6.9，不因规格提高机械增加。初始四套另计。</p>')
  pg(f'第{era}代 · 全部芯片特色',table(['卡号与芯片','完整效果'],[[c['id']+' '+next(x['name']for x in c['components'] if x['kind']=='chip'),c['effect']]for c in eraCards]))
  md+=['\n## 第'+str(era)+'代','| 卡号/型号 | 规格旧→新 | 负载 | 芯片费旧→新 | 入库普/伙 |','|---|---|---|---|---|']+['| '+' | '.join(map(str,row))+' |'for row in rows]
  for c in eraCards:md.append(c['id']+'：'+c['effect'])
 rows=[]
 for n in d['demands']:
  rows.append([n['id']+' '+n['name']]+[' / '.join(str(m['ordersByPlayers'][str(k)])for m in n['markets'])for k in (2,3,4)])
 pg('需求分布与参考尺度',table(['需求','2人四市场','3人四市场','4人四市场'],rows)+'<p>四市场顺序：大众、电竞、摄影、商务。每张需求总量为7–8／11–12／15–16。预算与偏好照需求卡，不随本场现货临时缩放。</p>'+table(['参考格竞争力','星级','收入奖','科技奖'],[['0–14',0,0,0],['15–27',1,2,1],['28–41',2,3,1],['42及以上',3,4,2]])+'<p>星级已印卡。达标仍需严格胜过参考且真实零售成交；每公司每场只领一个挑战。</p>')
 (O/'旗舰元年_7.0_芯片与市场校准表.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>7.0芯片与市场校准表</title><style>'+css+'</style><body>'+''.join(pages)+'</body></html>')
 (O/'旗舰元年_7.0_芯片与市场校准表.md').write_text('\n\n'.join(md)+'\n')
 (R/'work/chip_report_manifest.json').write_text(json.dumps({'pages':len(pages),'chips':len(ps)},ensure_ascii=False,indent=2))
