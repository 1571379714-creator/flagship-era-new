"""署名和指派按真实卡面孔位尺寸制作；只负责显示和打印。"""
import json
from physical_layout import AIDCSS

def build_supplier_aids(g):
 R,O,d,E=[g[k] for k in ('R','O','d','E')]
 css=AIDCSS+'''\n.quarters{display:grid;grid-template-columns:repeat(2,94mm);gap:6mm;margin-top:7mm}.piecepanel{height:100mm;padding:5mm;border:1px solid #b9ccd3}.piecepanel h3{font-size:12pt;margin:0 0 4mm}.piecepanel p{font-size:9pt;line-height:1.7}.pointergrid{display:grid;grid-template-columns:repeat(6,10mm);grid-template-rows:repeat(2,9mm);gap:2mm;margin-left:auto;margin-right:auto;width:max-content}.pointer{width:10mm;height:9mm;border:1px dashed #536f7d;display:flex;align-items:center;justify-content:center;text-align:center;line-height:1.1;font-size:8pt;font-weight:bold;background:#e2eef1;flex-direction:column}.pointer strong{font-size:10.5pt}.pointer.back{background:repeating-linear-gradient(45deg,#d8e7ec,#d8e7ec 1mm,#edf3f5 1mm,#edf3f5 2mm)}.pointer.back b{font-size:11pt}.pointer.back span{font-size:4.7pt;line-height:1.05}.authorgrid{display:grid;grid-template-columns:repeat(7,9.5mm);gap:2mm}.author{border:1px dashed #304f5e;background:#f6f1df;width:9.5mm;height:9.5mm;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;flex-direction:column;font-size:10pt;font-weight:bold;line-height:1}.author small{font-size:4.2pt}.relationgrid{display:grid;grid-template-columns:repeat(3,20mm);gap:4mm}.relation{width:20mm;height:16mm;border:1px dashed #496776;display:flex;align-items:center;justify-content:center;font-size:8pt;line-height:1.3;text-align:center;background:#f2f6f6}.sample{font-size:12pt;line-height:1.9;padding:5mm;background:#edf5f6;margin-top:6mm}.samplegrid{display:flex;gap:3mm;align-items:center;margin:8mm 0}.sw{border:1px solid #7396a1;padding:4mm;min-width:25mm;text-align:center}.networklabels{display:grid;grid-template-columns:repeat(1,1fr);gap:5mm;margin:6mm 0}.networklabel svg{width:8mm;height:8mm;vertical-align:middle}.networklabel{height:33mm;padding:3mm 6mm;border:1px dashed #557887;display:flex;justify-content:space-between;align-items:center}.networklabel h3{font-size:17pt;margin:0}.networklabel p{font-size:9pt;line-height:1.6}.notes{font-size:9pt}'''
 pages=[];manifest=[]
 def page(title,body,note):
  n=len(pages)+1;pages.append(f'<section class="sheet"><div class="head"><b>{title}</b><span>6.9 / {n}</span></div>{body}<div class="foot">{note}</div></section>');manifest.append({'page':n,'title':title,'note':note})
 front=[];back=[];pointers=[]
 for a in 'ABCD':
  items=[]
  for prod in range(1,5):
   for j in range(3):
    idx=len(items);items.append(f'<div class="pointer" data-company="{a}" data-product="{prod}"><strong>{a}·{prod}</strong></div>');pointers.append({'company':a,'product':prod,'copy':j+1,'localCell':idx,'sizeMm':[10,9]})
  front.append(f'<div class="piecepanel"><h3>{a}公司 · 技术指派正面</h3><div class="pointergrid">'+''.join(items)+'</div><p>四个产品号各三枚，共12枚。此面在发布揭晓时朝上；只剪虚线小片，外框和说明不剪。</p><p>长方片10×9毫米，放在科技卡对应公司的使用位置，不遮盖卡面效果。</p></div>')
  back.append(f'<div class="piecepanel"><h3>{a}公司 · 指派背面</h3><div class="pointergrid">'+''.join(f'<div class="pointer back" data-company="{a}"><b>{a}</b><span>已部署</span></div>' for _ in range(12))+'</div><p>同一家公司所有背面相同，不印产品号；外框已按正面水平镜像匹配。</p><p>已公开而未售的产品，指派保持正面，不能重新反扣。</p></div>')
 page('全桌技术指派 · 正面','<div class="quarters">'+''.join(front)+'</div>','全桌1份 · 本页与下一页A4原尺寸长边翻转双面 · A=M01 / B=M02 / C=M03 / D=M04')
 page('全桌技术指派 · 镜像背面','<div class="quarters">'+''.join(back[i] for i in [1,0,3,2])+'</div>','全桌1份 · 与前页配对 · 同一公司每枚背面完全相同 · 不使用旧版无公司指派片')
 body=[]
 for a in 'ABCD':
  body.append(f'<div class="piecepanel"><h3>{a}公司 · 永久作者圆片</h3><div class="authorgrid">'+''.join(f'<div class="author" data-author="{a}">{a}<small>研发者</small></div>' for _ in range(35))+'</div><p>35枚涵盖一家公司完成全部可联合项目的理论极端；只在成果公开时放一枚。永远不随成交或取消收回。</p></div>')
 page('永久署名片 · 圆形','<div class="quarters">'+''.join(body)+'</div>','全桌1份单面 · 每公司35枚直径9.5毫米 · 公司字母不是供应商颜色')
 body=[]
 for a in 'ABCD':
  labels=[f'{a}<br>关系']*5+[f'{a}<br>唯一核心']+[f'{a}<br>联合在研']*3
  body.append(f'<div class="piecepanel"><h3>{a}公司 · 关系与立项</h3><div class="relationgrid">'+''.join('<div class="relation">'+z+'</div>' for z in labels)+'</div><p>关系5枚、核心1枚、联合在研3枚。关系放本人五厂行；核心只放一家。第三在研仍须U09。</p></div>')
 page('个人关系和研发模式片','<div class="quarters">'+''.join(body)+'</div>','全桌1份单面 · 不是入库券、授权券或奖励券 · 可用相同形状的玩家标记替代')
 frows=[]
 for f in d['factories']:
  frows.append(f'<div class="networklabel" style="border-color:{f["color"]}"><h3 style="color:{f["color"]}">{g["factory_icon"](f["id"])} {E(f["name"])}</h3><p>此处只陈列已完成联合T卡<br>圆片署名 / A—D片指派<br>无固定容量，向桌面延伸摆放</p></div>')
 page('公共供应商技术区 · 五条厂区标题','<div class="networklabels">'+''.join(frows)+'</div><div class="notes">可剪开横条作为五个公共区的标题。开局均为空；不是五个取牌市场，不发牌、不刷新。技术卡放在标题下，不叠住能力文字。</div>','全桌1份单面 · 可替代A3公共技术版图，桌面技术增多时展开摆放')
 sample='<div class="sample"><b>蓝厂的联合显示技术，研发者是A。</b><p>原T卡放蓝厂区域，上面放圆A片；A自用或别人付费使用，都在对应A/B/C/D位置放长方产品片。</p><div class="samplegrid"><div class="author">A<small>研发者</small></div><div class="sw">A<br>空</div><div class="sw">B<br><div class="pointer"><strong>B·3</strong></div></div><div class="sw">C<br>空</div><div class="sw">D<br><div class="pointer"><strong>D·1</strong></div></div></div><p>B③与D①已依法使用；A只署名但未部署，不能给自家手机自动生效。</p></div>'
 sample+='<div class="notes"><h3>组装时</h3>先查伙伴关系、关联部件、技术位与本公司是否已有占用，再把授权费付原作者，放本公司的使用片。原作者自用不付自己钱，但照查其他条件。<h3>发布时</h3>只翻片确认原产品号。扩产可按原指派再付一批授权，放＋1；不能补买其他技术或改号。科技/工程挑战要求至少部署一项本人完成研究，外部授权与集成占位不算。<h3>取消、成交与未售</h3>取消只收该产品的长方片，费用不退；成交等全场证据检查后收片。未售的片保持原样，下一场不再收费。扩产组两批一起清理，只收一次实际使用片；圆作者片始终留在原卡。</div>'
 page('署名与授权摆放示例',sample,'全桌速查 · 非新增卡牌或独立游戏阶段 · 与规则§9—10一致')
 (O/'旗舰元年_6.9_供应商署名与授权组件.html').write_text(g['document_html']('旗舰元年6.9 · 供应商署名与授权组件',css,''.join(pages)),encoding='utf8')
 (R/'work/supplier_aids_manifest.json').write_text(json.dumps({'pages':manifest,'pointers':pointers,'authorsPerCompany':35,'relationPerCompany':5,'corePerCompany':1,'jointModePerCompany':3,'authorSizeMm':9.5,'playerMap':dict(zip('ABCD',['M01','M02','M03','M04']))},ensure_ascii=False,indent=2),encoding='utf8')
