"""Shared physical card layout; 7.0 boards and general aids are authored in surfaces_v70.py."""
import json
AIDCSS='''*{box-sizing:border-box}body{margin:0;background:#e9eef1;font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;color:#243d49}header.web{padding:16px;background:#173b49;color:white}header h1{font-size:22px;display:inline-block;margin:0 24px 0 0}.sheet{width:194mm;height:281mm;background:white;position:relative;margin:16px auto;padding:0;overflow:hidden}.head{height:14mm;border-bottom:1px solid #849eaa;display:flex;align-items:center;justify-content:space-between;font-size:12pt}.foot{position:absolute;bottom:0;width:100%;border-top:1px solid #b7c9ce;font-size:7.5pt;padding-top:2mm;color:#526f79}.items{display:grid;gap:3mm;margin-top:4mm}.tile{border:1px dashed #91a6af;padding:3mm;position:relative;overflow:hidden;background:#fff}.tile h3{font-size:12pt;margin:0 0 2mm;line-height:1.3}.tile p{font-size:8pt;line-height:1.5;margin:1mm 0}.tile .big{font-size:24pt;font-weight:bold;color:#166f7c;margin:2mm 0}.tile .sub{font-size:9pt;color:#667e87}.tile.back{background:repeating-linear-gradient(45deg,#e3ecef,#e3ecef 3mm,#e9f1f3 3mm,#e9f1f3 6mm);text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center}.tile table{border-collapse:collapse;font-size:7.5pt;width:100%}.tile td,.tile th{padding:1mm;border-bottom:1px solid #c6d7df;text-align:left}.grid4{grid-template-columns:repeat(4,1fr);grid-auto-rows:58mm}.grid3{grid-template-columns:repeat(3,1fr);grid-auto-rows:58mm}.grid2{grid-template-columns:repeat(2,1fr);grid-auto-rows:123mm}.tokens{display:grid;grid-template-columns:repeat(6,1fr);gap:2mm;margin-top:5mm}.token{border:1px dashed #78939f;text-align:center;padding:2mm;height:24mm;font-size:8pt;line-height:1.5}.a-table{width:100%;border-collapse:collapse;font-size:8pt;margin:5mm 0}.a-table th,.a-table td{border:1px solid #afc3cb;text-align:center;padding:2mm}.a-table td{height:35mm}.strip{padding:3mm;border:1px solid #a3bac3;margin:3mm 0;font-size:10pt}.cells{display:flex;gap:2mm;margin-top:2mm}.cell{flex:1;border:1px solid #98aebb;min-height:12mm;text-align:center;font-size:11pt}.notes{font-size:10pt;line-height:1.7;margin:5mm}.refgrid{grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,123mm)}.refcard{border:1px dashed #aab8c0;padding:2.7mm;overflow:hidden}.refcard h3{font-size:11pt;margin:0 0 2mm}.refcard p{font-size:7.3pt;line-height:1.42;margin:2mm 0}.refcard table{border-collapse:collapse;font-size:7pt;width:100%}.refcard th,.refcard td{border-bottom:1px solid #cddbe0;padding:1mm .4mm;text-align:center}.refcard b{color:#9b4942}.refcard.back{background:repeating-linear-gradient(45deg,#e6edf0,#e6edf0 4mm,#eef3f4 4mm,#eef3f4 8mm);display:flex;align-items:center;justify-content:center;text-align:center;flex-direction:column}.refcard.back h3{font-size:22pt;color:#214553}@page{size:A4 portrait;margin:8mm}@media print{header.web{display:none}body{background:white}.sheet{margin:0;break-after:page}.sheet:last-child{break-after:auto}*{print-color-adjust:exact;-webkit-print-color-adjust:exact}}'''

def build_reference_print(g):
 R,O,d,E,M=[g[k] for k in ('R','O','d','E','M')]
 sheets=[];manifest=[]
 short={'mass':'大众','gaming':'电竞','photo':'摄影','office':'商务'}
 for era in range(1,6):
  cards=[c for c in d['benchmarks'] if c['era']==era]
  front=[]
  for c in cards:
   rows=[]
   for m in c['markets']:rows.append([short[m['market']],m['score'],m['reward'],('无' if not m['reward'] else f'{m["incomeReward"]}/{m["technologyReward"]}'),('无' if not m['reward'] else m['specialValue'])])
   content=f'<p>{c["id"]} · 参考{era}代 · 每市场1订单</p><h3>{E(c["name"])}</h3>'+g['table'](['市场','分','星','收/科','特色值'],rows)
   content+='<p><b>'+E(c['specialName'])+'</b><br>'+E(c['specialSummary'])+'</p><p>全员锁定后现抽，扩产后最终成交且严格超过本格才合格；每公司每场最多选1奖。0星无奖。科技或工程试验另需该批已部署本人完成研发；外部授权不算。不查首发或年龄。</p>'
   front.append('<article class="refcard" id="print-'+c['id']+'">'+content+'</article>')
  back='<article class="refcard back"><p>FLAGSHIP ERA / 7.0</p><h3>参考世代 '+str(era)+'</h3><p>全部锁定后才抽取<br>六张完整洗匀，允许重复</p></article>'
  for side,body in [('正面',''.join(front)),('背面',back*6)]:
   page=len(sheets)+1;sheets.append(f'<section class="sheet"><div class="head"><b>参考{era}代 · {side}</b><span>7.0 / {page}</span></div><div class="items refgrid">'+body+'</div><div class="foot">全桌1套 · 前后页长边翻转 · 同一代背面完全一致 · 原尺寸打印</div></section>');manifest.append({'page':page,'era':era,'side':side,'cards':[c['id'] for c in cards] if side=='正面' else []})
 (O/'旗舰元年_7.0_参考机正反面.html').write_text(g['document_html']('旗舰元年7.0 · 参考机正反面',AIDCSS,''.join(sheets)),encoding='utf8');(R/'work/reference_print_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')

def build_main_print(g):
 """等尺寸63×88mm主牌：257正面，配通用背面。数据能力完整保留。"""
 from bs4 import BeautifulSoup
 R,O,d,E=[g[k] for k in ('R','O','d','E')]
 cards=[c for c in d['parts'] if c['type']!='starter']+d['technologies']+d['contracts']+d['facilities']+d['schemes']
 expanded=[(c,i+1) for c in cards for i in range(c['qty'])]
 css=g['CSS']+'''
 .sheet{width:194mm;height:281mm;background:white;margin:16px auto;position:relative;overflow:hidden}.sheet .head{height:6mm;font-size:7pt;display:flex;justify-content:space-between;border-bottom:1px solid #aaa;align-items:center}.sheet .foot{position:absolute;bottom:0;font-size:7.0pt;color:#56707b}.main-grid{display:grid;grid-template-columns:repeat(3,63mm);grid-template-rows:repeat(3,88mm);gap:2mm;margin-top:1mm;width:max-content;margin-left:auto;margin-right:auto}.main-grid .card{width:63mm;height:88mm;padding:2mm 2mm 4.5mm;border-top-width:2px}.main-grid .card h3{font-size:10.8pt;line-height:1.2;margin-bottom:1mm}.main-grid .card p{font-size:8.6pt;line-height:1.36;margin:1.1mm 0}.main-grid .card p.small,.main-grid .card p.featurehint{font-size:7.2pt;line-height:1.25}.main-grid .card p.long{font-size:8.4pt;line-height:1.34}.main-grid .card .metric{font-size:7.2pt;padding:.7mm 1mm}.main-grid .card .metric b{font-size:10pt}.main-grid .card .metrics{gap:.7mm;margin:1mm 0}.main-grid .card table{font-size:7pt;line-height:1.16}.main-grid .card th{font-size:7.0pt}.main-grid .card .sourcehint{font-size:6.1pt!important}.main-grid .card td,.main-grid .card th{padding:.55mm .35mm}.main-grid .eyebrow{font-size:6.1pt;margin-bottom:.8mm}.main-grid .bottom{font-size:5.6pt;bottom:1.1mm;left:2mm;right:2mm}.main-grid .factory{font-size:7.0pt;margin:.5mm 0;padding:.5mm 1mm}.main-grid .effect{padding-top:1mm}.main-grid .card.fullcustom p{font-size:7.9pt;line-height:1.27}.main-grid .card.fullcustom table{font-size:7.0pt;line-height:1.1}.main-grid .card.fullcustom td,.main-grid .card.fullcustom th{padding:.45mm .3mm}.main-grid .card.fullcustom .featurehint{font-size:7.0pt!important}.main-back{width:63mm;height:88mm;border:1px dashed #91a8b4;background:repeating-linear-gradient(45deg,#e8eff2,#e8eff2 3mm,#dce7ed 3mm,#dce7ed 6mm);display:flex;align-items:center;justify-content:center;text-align:center;flex-direction:column;color:#1d475b}.main-back h3{font-size:19pt}.main-back p{font-size:9pt;margin-top:4mm}.blank{width:63mm;height:88mm;border:1px dashed #cad6dc;color:#8197a2;display:flex;align-items:center;justify-content:center;font-size:8pt}@media print{.sheet{margin:0;break-after:page}.sheet:last-child{break-after:auto}}
 '''
 sheets=[];manifest=[]
 for j in range(0,len(expanded),9):
  chunk=expanded[j:j+9];front=[]
  for c,copy in chunk:
   soup=BeautifulSoup(g['render_card'](c),'html.parser');card=soup.article;card['id']='physical-'+c['id']+'-'+str(copy)
   if c['type'] in ('supply','custom'):
    for p in card.select('p.small'):
     if p.get_text()==c.get('lifecycle'):
      p.string=('实体留库；产品用代替卡引用。有引用不能换库；取消或成交只收回代替卡。' if c['type']=='supply' else '整张全部部件同批用；取消回手，成交移出，未售原样留下。')
   if c['id']=='X152':
    for p in card.select('p.sourcehint'):p.decompose()
   if c['type']=='custom' and len(c['components'])>=3:
    if len(c['components'])==4:card['class']=card.get('class',[])+['fullcustom']
    for p in card.select('p.sourcehint'):p.decompose()
    for p in card.select('p.featurehint'):
     
     if len(c['components'])==4:p.decompose()
     else:p.string='特征：性能芯片≥6；影像规格≥6；续航余量≥4；生态读芯片；轻薄读机身；折叠须屏/身配套。'
   front.append(str(card));manifest.append({'id':c['id'],'copy':copy,'frontPage':len(sheets)+1,'cell':len(front)})
  front+=['<div class="blank">空位，不是卡牌</div>']*(9-len(front))
  backs=['<div class="main-back"><h3>旗舰元年</h3><p>主牌 / 7.0</p><p>共同发布 · 单批产品</p></div>' if i<len(chunk) else '<div class="blank">空位</div>' for i in range(9)]
  mirrored=[]
  for row in range(3):mirrored+=backs[row*3:row*3+3][::-1]
  for side,body in [('正面',front),('背面',mirrored)]:
   page=len(sheets)+1;sheets.append(f'<section class="sheet"><div class="head"><b>统一主牌制卡 · {side}</b><span>63×88mm / 7.0 / {page}</span></div><div class="main-grid">'+''.join(body)+'</div><div class="foot">9卡/页 · 原尺寸A4 · 相邻页长边翻转双面 · 建议不透明牌套 · 无出血量产刀模</div></section>')
 (O/'旗舰元年_7.0_统一主牌正反面.html').write_text(g['document_html']('旗舰元年 7.0 · 257张统一主牌正反面',css,''.join(sheets)),encoding='utf8');(R/'work/main_print_manifest.json').write_text(json.dumps({'cards':manifest,'pages':len(sheets),'cardSizeMm':[63,88]},ensure_ascii=False,indent=2),encoding='utf8')


def build_starter_print(g):
 """16张真实初始通用配件，按公司各四种；不混主牌。"""
 R,O,d,E,K=[g[k] for k in ('R','O','d','E','K')]
 cards=sorted([c for c in d['parts'] if c['type']=='starter'],key=lambda c:c['id'])
 css=AIDCSS+".startergrid{grid-template-columns:repeat(3,63mm);grid-template-rows:repeat(3,88mm);gap:2mm;margin-top:1mm;width:max-content;margin-left:auto;margin-right:auto}.startercard{width:63mm;height:88mm;padding:3mm;border:1px dashed #78939f}.startercard h3{font-size:13pt;margin:2mm 0}.startercard p{font-size:8.5pt;line-height:1.4;margin:1.8mm 0}.startercard table{font-size:9pt;width:100%;border-collapse:collapse}.startercard td,.startercard th{padding:1.2mm .4mm;text-align:center;border-bottom:1px solid #bacbd0}.startercard.back{display:flex;flex-direction:column;justify-content:center;align-items:center;background:#e6eff1;text-align:center}.sheet .head{height:6mm;font-size:8pt}.sheet .foot{font-size:7.0pt}.blank{border:1px dashed #bbb;color:#78939f;text-align:center;font-size:9pt;padding-top:35mm}"
 pages=[];manifest=[]
 for j in range(0,len(cards),9):
  chunk=cards[j:j+9];front=[];backs=[]
  for c in chunk:
   a=c['components'][0];company='M0'+c['id'][2];name=K[a['kind']]
   text=f'<p>{c["id"]} / {company} 专用初始实体</p><h3>初始通用{name}</h3><p>{E(c["name"])}</p>'
   text+=g['table'](['入库费','开局执行','每批制造'],[[0,'直接入库',a['batchCost']]])
   text+=g['table'](['规格','供电' if a['kind']=='body' else '功耗','标识'],[[a['spec'],a['power'],a['mark']]])
   text+='<p>开局免费放入本人稳定库对应栏。每批仍支付制造费；产品中使用同类代替卡，实体不离库。</p><p>中立初始不建立五厂关系。对应A/B/C/D=M01/M02/M03/M04。有引用不能替换；被替换的初始实体移出本局，不进主弃牌。</p>'
   front.append('<article class="startercard">'+text+'</article>')
   backs.append('<article class="startercard back"><h3>旗舰元年</h3><p>7.0 / 初始通用配件</p><h3>'+company+'</h3><p>'+name+' · 真实供货实体</p><p>不混主牌，不是稳定代替卡</p></article>')
   manifest.append({'id':c['id'],'company':company,'kind':a['kind'],'frontPage':len(pages)+1,'cell':len(front)})
  front+=['<div class="blank">空位，不是卡牌</div>']*(9-len(chunk));backs+=['<div class="blank">空位</div>']*(9-len(chunk))
  mirror=[]
  for row in range(3):mirror+=backs[row*3:row*3+3][::-1]
  for side,items in [('正面',front),('背面',mirror)]:
   page=len(pages)+1;pages.append(f'<section class="sheet"><div class="head"><b>初始通用配件 · {side}</b><span>7.0 / {page}</span></div><div class="items startergrid">'+''.join(items)+'</div><div class="foot">全桌印一套16张 · 63×88mm · 相邻页长边翻转 · 各玩家取本人编号四张 · 不混入主牌</div></section>')
 (O/'旗舰元年_7.0_初始通用配件正反面.html').write_text(g['document_html']('旗舰元年 7.0 · 初始通用配件16张',css,''.join(pages)),encoding='utf8')
 (R/'work/starter_print_manifest.json').write_text(json.dumps({'cards':manifest,'pages':len(pages),'cardSizeMm':[63,88]},ensure_ascii=False,indent=2),encoding='utf8')
