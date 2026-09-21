"""静态线下版图与实体组件；无对局逻辑、无联网功能。"""
import json,html

def build_boards(g):
 R,O,d,E,M,K=[g[k] for k in ('R','O','d','E','M','K')]
 css=(R/'assets/boards.css').read_text()+'''\n.cardwell{min-height:86mm;border:1px dashed #7896A3;background:white;padding:4mm;font-size:10pt}.four{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}.mainwell{height:90mm}.dest td{height:22mm;text-align:center;font-size:9pt}.dest th{font-size:9pt}.dest .zones{font-size:7pt;color:#597785}.stablewell{height:130mm}.panel.compact p{font-size:9pt}#research .slot{min-height:17mm;padding:2mm}#research .panel{padding:3mm;margin-bottom:3mm}#research .panel p{font-size:9pt;line-height:1.4}#research .tick{height:10mm}#dest .panel{padding:3mm}.board h4{margin:2mm 0}.pill{display:inline-block;border:1px solid #8AA5B3;padding:2mm;margin:1mm}'''
 def p(h,t):return '<div class="panel"><h3>'+h+'</h3>'+t+'</div>'
 def track(n,start=0):return '<div class="track">'+''.join('<span class="tick">'+str(i)+'</span>' for i in range(start,n+1))+'</div>'
 def tbl(h,rows):return g['table'](h,rows)
 boards=[]
 def add(id,title,sub,body):
  boards.append((id,title,'<section class="board '+('active' if not boards else '')+'" id="'+id+'"><div class="title"><h2>'+title+'</h2><p>旗舰元年 6.2</p></div><p class="subtitle">'+sub+'</p>'+body+'<div class="legend">静态线下展示 / A3横向打印 · 不提供发牌、结算、存局或网络游玩</div></section>'))
 add('release','共同发布','没有固定轮次；玩家花工作点推进。',p('预热：1工作点，自选＋1—3，每本人回合一次',track(20)+'<p>2人终点12 · 3人16 · 4人20。到顶后当前玩家做完剩余工作，马上全桌锁定。</p>')+'<div class="grid2">'+p('需求卡N：提前公开','<div class="cardwell">放本场N卡<br>读预算、2/3/4人订单数和偏好</div>')+p('参考机V：锁定后才现抽','<div class="cardwell">先放参考世代标记，不翻V<br>I / II / III / IV / V<br>全员锁价与去向后，从该代6张洗匀抽1张</div>')+'</div>'+p('四个市场的有限订单','<div class="four">'+''.join('<div class="slot">'+n+'<br>未分配 / 已分配</div>' for n in M.values())+'</div>'))
 add('main','唯一公开牌市','主牌257张：全部五代稳定、定制、研发、合同、设施、方案；取得均无额外现金费。','<div class="four">'+''.join(f'<div class="cardwell mainwell"><b>{i}</b><br>主牌陈列位<br>取走留空，本次选完再补</div>' for i in range(1,9))+'</div><div class="row">'+p('一次取牌','<p>1工作点取至多2张，可混选当前牌市与盲抽。不得再选择本次补出的新牌。</p>')+p('普通发布末','<p>最左2张弃置 → 剩余左移 → 补8。换代不加牌、不另刷新。</p>')+'</div>')
 add('library','公司稳定配件库','四类各一个栏位。初始0；新稳定按卡面入库费。拿到手牌不等于入库。','<div class="four">'+''.join('<div class="cardwell stablewell"><h3>'+n+'</h3><p>实际稳定卡一直放这里</p><p>最多1张<br>新卡替换旧同类<br>不得叠放备用</p><p><b>桌上仍有该类代替卡<br>＝不能换库卡</b></p><p>未来世代可以付费入库<br>但不能被组装或验证样机引用</p></div>' for n in K.values())+'</div>'+p('引用解除，不靠回合或发布自动复位','<p>取消：只收回该批代替卡。成交：全场所有奖励结束后统一收回。未售：继续引用，跨场不减分。</p><p>其他产品仍有引用，即使只剩一款，该栏也继续锁定。旧稳定被替换进主弃牌，旧初始移出。</p>')+p('回合资源','<div class="slots"><div class="slot">工作1</div><div class="slot">工作2</div><div class="slot">工作3</div><div class="slot">U02专用组装点<br>只有建成启用才有</div></div>'))
 add('product','单批产品面板','每家公司有1—4号四个产品位；此面板可重复打印4份并放产品号片。', '<div class="four">'+''.join('<div class="cardwell"><h3>'+n+'</h3>放“稳定部件·'+n+'”代替卡<br>或实际定制部件</div>' for n in K.values())+'</div><div class="grid2">'+p('部署与可选方案','<div class="slots"><div class="slot">技术1</div><div class="slot">技术2</div><div class="slot">Q方案<br>至多1</div></div><p>T21可扩第3技术槽，自身占1。技术实体留完成区，用对应产品号指派。</p>')+p('付费就是生产','<p>组装1工作 → 检查四类、世代、配套、供电和技术 → 支付部件费＋组装费8＋Q费，应用合法减免后至少6。</p><p><b>现在就是一批待售货，不再另点生产，不叠加库存。</b></p>')+'</div>'+p('取消与结束','<p>本人工作阶段免费取消：定制、Q回手；技术释放，代替卡收回；原款不退。改款就是取消后重新组装付费。</p><p>成交后定制、Q移出（Q21例外）；未售配置原样保留，不用年龄、旧分或历史成本。</p>'))
 headers=['产品','留库','合同A','合同B','合同C','大众消费','电竞娱乐','摄影创作','商务办公']
 rows=[]
 for i in range(1,5):rows.append([f'{i}号']+['待售\n↓已售\n↓收款']*8)
 add('dest','秘密投放','每批一个产品号去向片，只能放一处。每行一张价牌，推荐章与入场许可也先锁定。', '<div class="dest">'+tbl(headers,rows)+'</div>'+p('先锁定，后现抽','<p>实际只有4批，就只有4个去向片。合同要2批，必须用两个产品位各交一批；每批分别达标，可不同配置。</p><p>揭晓以后未售不能改投。已售配置和片留到挑战等条件确认并完成所有奖励；不要先拆掉成交产品。</p>')+p('价格速查',tbl(['售价','修正','该批现金','该批收入'],[[18,'+6',18,1],[28,'+2',28,2],[38,'−2',38,3],[48,'−6',48,4]])+'<p>48通常要求基础≥22且某部件规格≥8；其他许可看卡。所有价格仍查预算。</p>'))
 add('research','研究、合同与世代','进度和期限放在实际卡旁；不要记已售型号或它的首次发布。','<div class="grid2">'+p('在研槽：默认2，U09到3',''.join(f'<h4>项目{i}</h4>'+track(4) for i in range(1,4))+'<p>付立项费，首个工作已有1格。到线缺证据放待验证；再复核花1点。</p>')+p('执行合同：默认A/B，U10到C',''.join(f'<h4>合同{x}</h4><div class="slots"><div class="slot">期限1</div><div class="slot">期限2</div><div class="slot">压实际押金</div></div>' for x in 'ABC')+'<p>每次发布去1期限；履约拿回押金，逾期押金入银行。</p>')+'</div>'+p('本公司独立验证：当前世代各一次','<div class="slots">'+''.join('<div class="slot">'+e+'<br>已用片永久放这里</div>' for e in ['I','II','III','IV','V'])+'</div><p>工作2、现金12、基础≥10、特征≥2，奖励1科技。T32/T39/U12/Q22例外见卡。取消、换位、成交均不复位。</p>')+p('全桌世代：只改标记，不再加牌','<div class="slots">'+''.join('<div class="slot">'+str(e)+'代<br>科技'+str(t)+'</div>' for e,t in zip(range(1,6),d['parameters']['eraThresholds']))+'</div>'))
 add('scores','收入与科技','收入60或科技30触发最后阶段。两条可选主线，不相加，也不按双轨相遇判终局。',p('收入：0—100','<div class="scores">'+''.join(f'<span class="tick">{i}</span>' for i in range(101))+'</div>')+p('科技：格内小字是终局对应成绩','<div class="techscores">'+''.join(f'<span class="tick"><b>{i}</b><small>成绩{i*2}</small></span>' for i in range(37))+'</div>')+p('最终成绩与顺序','<p>取收入和科技×2较大者。同分看另一项，再比现金。触发后完成当前回合，所有玩家各再一个回合，然后最终发布。</p><p>收入超过100用＋100片；科技超过36用＋36片，其成绩对应＋72。</p>'))
 add('workflow','桌边流程与通用数值','具体费用、工期、订单、星级与奖励都直接读卡；这里打印共用规则。','<div class="grid2">'+p('发布七步','<p>①锁价、选唯一去向，揭晓，再现抽V</p><p>②整单合同核验与交付</p><p>③四市场有限订单逐批分配</p><p>④冻结挑战和卡牌奖励，用片保留证据</p><p>⑤先全桌收款／普通成果，再特色奖</p><p>⑥出口等处置后，统一结束成交占用</p><p>⑦合同、维护、牌市一次刷新、换N、标参考代</p>')+p('产品生命周期','<p><b>组装＝生产1批</b>；先付钱，不能借未来售价。</p><p><b>未售</b>：完整配置留下，不减分，不补制造费。</p><p><b>取消</b>：本人工作阶段，定制/Q回手，钱不退。</p><p><b>成交</b>：定制/Q消耗，部署释放，代替卡收回。</p><p>无年龄、无芯片配额、无公司产能条、无多批库存。</p>')+'</div>'+p('六种特征',tbl(['性能','影像','轻薄','续航','折叠','生态'],[['芯片≥6','影像≥6','机身轻薄','余量≥4','屏/身配套','芯片生态或卡授予']]))+p('暂存奖励','<p>推荐章（+2/+4/+6）、入库券（3/6/9）、单批试产券（减0/3/6）各只能留1件；以后本人工作或锁定时按相应规则使用。最终未用不加分。</p>'))
 nav=''.join('<button onclick="show(\''+i+'\')">'+t+'</button>' for i,t,_ in boards)
 script="<script>function show(id){document.querySelectorAll('.board').forEach(x=>x.classList.toggle('active',x.id===id));}function printAll(){document.body.classList.add('printall');window.print();document.body.classList.remove('printall');}</script>"
 h='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>旗舰元年6.2线下版图</title><style>'+css+'</style><body><header><h1>旗舰元年6.2</h1>'+nav+'<button onclick="window.print()">打印当前</button><button onclick="printAll()">打印全部</button></header>'+''.join(v for _,_,v in boards)+script+'</body></html>'
 (O/'旗舰元年_6.2_线下版图.html').write_text(h,encoding='utf8');(R/'work/boards_manifest.json').write_text(json.dumps({'views':[{'id':i,'title':t} for i,t,_ in boards]},ensure_ascii=False,indent=2),encoding='utf8')

AIDCSS='''*{box-sizing:border-box}body{margin:0;background:#e9eef1;font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;color:#243d49}header.web{padding:16px;background:#173b49;color:white}header h1{font-size:22px;display:inline-block;margin:0 24px 0 0}.sheet{width:194mm;height:281mm;background:white;position:relative;margin:16px auto;padding:0;overflow:hidden}.head{height:14mm;border-bottom:1px solid #849eaa;display:flex;align-items:center;justify-content:space-between;font-size:12pt}.foot{position:absolute;bottom:0;width:100%;border-top:1px solid #b7c9ce;font-size:7.5pt;padding-top:2mm;color:#526f79}.items{display:grid;gap:3mm;margin-top:4mm}.tile{border:1px dashed #91a6af;padding:3mm;position:relative;overflow:hidden;background:#fff}.tile h3{font-size:12pt;margin:0 0 2mm;line-height:1.3}.tile p{font-size:8pt;line-height:1.5;margin:1mm 0}.tile .big{font-size:24pt;font-weight:bold;color:#166f7c;margin:2mm 0}.tile .sub{font-size:9pt;color:#667e87}.tile.back{background:repeating-linear-gradient(45deg,#e3ecef,#e3ecef 3mm,#e9f1f3 3mm,#e9f1f3 6mm);text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center}.tile table{border-collapse:collapse;font-size:7.5pt;width:100%}.tile td,.tile th{padding:1mm;border-bottom:1px solid #c6d7df;text-align:left}.grid4{grid-template-columns:repeat(4,1fr);grid-auto-rows:58mm}.grid3{grid-template-columns:repeat(3,1fr);grid-auto-rows:58mm}.grid2{grid-template-columns:repeat(2,1fr);grid-auto-rows:123mm}.tokens{display:grid;grid-template-columns:repeat(6,1fr);gap:2mm;margin-top:5mm}.token{border:1px dashed #78939f;text-align:center;padding:2mm;height:24mm;font-size:8pt;line-height:1.5}.a-table{width:100%;border-collapse:collapse;font-size:8pt;margin:5mm 0}.a-table th,.a-table td{border:1px solid #afc3cb;text-align:center;padding:2mm}.a-table td{height:35mm}.strip{padding:3mm;border:1px solid #a3bac3;margin:3mm 0;font-size:10pt}.cells{display:flex;gap:2mm;margin-top:2mm}.cell{flex:1;border:1px solid #98aebb;min-height:12mm;text-align:center;font-size:11pt}.notes{font-size:10pt;line-height:1.7;margin:5mm}.refgrid{grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,123mm)}.refcard{border:1px dashed #aab8c0;padding:2.7mm;overflow:hidden}.refcard h3{font-size:11pt;margin:0 0 2mm}.refcard p{font-size:7.3pt;line-height:1.42;margin:2mm 0}.refcard table{border-collapse:collapse;font-size:7pt;width:100%}.refcard th,.refcard td{border-bottom:1px solid #cddbe0;padding:1mm .4mm;text-align:center}.refcard b{color:#9b4942}.refcard.back{background:repeating-linear-gradient(45deg,#e6edf0,#e6edf0 4mm,#eef3f4 4mm,#eef3f4 8mm);display:flex;align-items:center;justify-content:center;text-align:center;flex-direction:column}.refcard.back h3{font-size:22pt;color:#214553}@page{size:A4 portrait;margin:8mm}@media print{header.web{display:none}body{background:white}.sheet{margin:0;break-after:page}.sheet:last-child{break-after:auto}*{print-color-adjust:exact;-webkit-print-color-adjust:exact}}'''

def build_aids(g):
 R,O,d,E,K,M=[g[k] for k in ('R','O','d','E','K','M')]
 sheets=[];manifest=[]
 def sheet(title,body,copies):
  n=len(sheets)+1;sheets.append(f'<section class="sheet"><div class="head"><b>{title}</b><span>6.2 / {n:02}</span></div>{body}<div class="foot">{copies} · A4原尺寸 · 正反面配对见PRINTING.md</div></section>');manifest.append({'page':n,'title':title,'copies':copies})
 def tile(title,body='',cls=''):return '<div class="tile '+cls+'"><h3>'+title+'</h3>'+body+'</div>'
 # price row=product, columns=four prices. All four backs identical within a product.
 tiles=[];back=[]
 for i in range(1,5):
  for price,mod,inc in zip(d['parameters']['prices'],d['parameters']['priceScore'],d['parameters']['incomePerBatch']):
   tiles.append(tile(f'{i}号产品 · 售价',f'<div class="big">{price}</div><p>竞争修正 {mod:+}</p><p>成交1批：{price}现金 / {inc}收入</p><p>48：基础≥22且一部件≥8；卡面另许可除外。预算仍检查。</p>'))
  for _ in range(4):back.append(tile('价格已锁定',f'<div class="big">{i}号产品</div><p>所有人锁定后才翻开</p>','back'))
 sheet('价牌正面：四批各四档','<div class="items grid4">'+''.join(tiles)+'</div>','每人1份；与第2页双面')
 sheet('价牌背面：同一产品四价完全相同','<div class="items grid4">'+''.join(back)+'</div>','每人1份；与第1页长边翻转')
 tiles=[]
 for i in range(1,5):
  for kind,name in K.items():tiles.append(tile('稳定部件',f'<div class="big">{name}</div><p>{i}号产品专用代替卡</p><p>数值与能力读本人库内{name}。实体留库；只要仍引用，该栏不能替换。</p><p>取消或全场成交整理收回。</p>'))
 sheet('稳定部件代替卡：4类×4产品＝16张','<div class="items grid4">'+''.join(tiles)+'</div>','每人1份，单面；不混主牌')
 heads=['产品','留库','合同A','合同B','合同C','大众','电竞','摄影','商务']
 rows='<tr>'+''.join('<th>'+x+'</th>' for x in heads)+'</tr>'
 for i in range(1,5):rows+=f'<tr><th>{i}号</th>'+''.join('<td>待售<br>↓<br>已售</td>' for _ in heads[1:])+'</tr>'
 sheet('一批一个去向：放在屏风内','<table class="a-table">'+rows+'</table><div class="notes">每行只放1枚产品号片。该片代表这一整批，不是库存数量。已售时向下移；收款后加“已收款”片，仍留配置到全部奖励结束。<br><br>合同需2批＝两行各放一枚到同一合同。无效投放不得现场改去另一处。</div>','每人1份，单面，不用剪开')
 def strip(title,labels):return '<div class="strip"><b>'+title+'</b><div class="cells">'+''.join('<div class="cell">'+str(x)+'</div>' for x in labels)+'</div></div>'
 body=''.join(strip('在研项目 '+str(i)+'（默认2槽，U09开放第3）',[0,1,2,3,4,'待验证']) for i in range(1,4))
 body+=''.join(strip('合同'+x+'：放实际押金，发布末移除一期',[1,2,'押金']) for x in 'ABC')
 body+=strip('独立验证：当前供应世代，每格最多用一次',['I','II','III','IV','V'])
 body+='<div class="notes">验证工作2、现金12、基础≥10、至少2特征，得1科技。例外读T32/T39/U12/Q22。取消不复位。<br>不再使用年龄、产能、芯片用量和型号库存数值条。</div>'
 sheet('研究、合同与本世代验证',''+body,'每人1份，单面；可以分条剪开')
 front=[];backs=[]
 for i in range(1,5):
  for _ in range(3):front.append(tile('部署指派',f'<div class="big">产品{i}</div><p>放在已完成T卡上。本技术只供这批；取消或成交整理释放。</p>'))
  for _ in range(3):backs.append(tile('技术已占用','<p>指派对象保密<br>不印产品号<br>全员锁定后揭晓</p>','back'))
 sheet('技术指派正面：每号3片','<div class="items grid3">'+''.join(front)+'</div>','每人1份；与第7页双面')
 sheet('技术指派背面：全部相同','<div class="items grid3">'+''.join(backs)+'</div>','每人1份；与第6页长边翻转')
 coupons=[]
 for v in (2,4,6):coupons.append(tile('渠道推荐',f'<div class="big">＋{v}</div><p>未来锁定时给一批一个零售市场。揭晓消耗，未售也交回。不绕预算。</p><p>本类至多留1枚。</p>'))
 for v in (3,6,9):coupons.append(tile('稳定入库券',f'<div class="big">减{v}</div><p>未来本人回合安装1张稳定时抵现金，最低0。不省工作，不解除引用锁定。</p><p>本类至多留1张。</p>'))
 for v in (0,3,6):coupons.append(tile('单批试产券',f'<div class="big">减{v}</div><p>未来本人回合组装恰好1批，不花工作，总费再减{v}、至少6。照查世代、空位、技术与现金。</p><p>不是正常组装工作；本类至多1张。</p>'))
 sheet('三类奖励：各至多保留一件','<div class="items grid3">'+''.join(coupons)+'</div>','每人1份，单面；没有未用券终局换分')
 labels=['产品'+str(i) for i in range(1,5)]+['已收款']*4+['已锁定','挑战选择','转换1科技','已部署']+['本人回合已用']*8+['本期已用']*6+['维护停用','待验证']*2+['验证已用']*5+['工作1','工作2','工作3','U02专用']+['＋100收入','＋36科技\n成绩＋72']
 sheet('状态标记：放在实际来源卡上','<div class="tokens">'+''.join('<div class="token">'+s.replace('\n','<br>')+'</div>' for s in labels)+'</div><div class="notes">“已收款”覆盖在已售去向片旁，不先撤产品；所有奖励结束再一起清空。</div>','每人1份，单面；同类可用通用小方块替代')
 work=g['table'](['工作','点数'],[['取主牌至多2',1],['安装稳定1张',1],['组装1批',1],['推进/复核研发',1],['签约合同',1],['设施建设',2],['预热+1—3',1],['技术服务6/10',1],['独立验证12现金',2],['取消未成交产品',0]])
 summary=[tile('工作速查',work+'<p>预热与服务每本人回合各一次。每回合3点，不保留余点。</p>'),tile('组装费用与库存','<p>四部件印刷制造费＋组装费8＋Q费；先减组装费到0，再减总费到最低6。</p><p>配件取得0现金。稳定入库读卡（初始0，新稳定本版9）。</p><p>每产品位恰好1批，不另记库存数。</p><p>未来配件可拿可入库，不可组装。</p>'),tile('特征与市场','<p>性能：芯片规格≥6<br>影像：影像规格≥6<br>轻薄：机身轻薄<br>续航：供电余量≥4<br>折叠：屏幕机身配套<br>生态：芯片标识或能力</p><p>大众任意合法；电竞性能；摄影影像；商务续航/生态/折叠。</p>'),tile('取消与成交','<p>本人工作阶段可免费取消：定制与Q回手、T释放、代替卡收回；钱和点不退。</p><p>成交结束：定制与Q移出（Q21例外）；未售原样跨场，不扣年龄。</p><p>有任何同类代替卡引用就不能换该库栏。发布中一律不换库。</p>')]
 sheet('共用数字直接印在速查卡','<div class="items grid2">'+''.join(summary)+'</div>','每人1份，单面')
 # token set for public order sorting.
 pub=['订单']*20+['参考机']*4+['参考世代I','II','III','IV','V']+['供应世代I','II','III','IV','V']+['发布标记']
 sheet('公共标记与换代速查','<div class="tokens">'+''.join('<div class="token">'+s+'</div>' for s in pub)+'</div><div class="notes">供应：科技3/7/13/20于回合末开放II/III/IV/V。只改标记，不洗新包。<br>参考：准备期开始标定，所有人锁定后才抽该代6张中的1张。<br>2/3/4人发布终点12/16/20，收入60或科技30触发最后阶段。</div>','全桌1份，单面')
 h=g['document_html']('旗舰元年 6.2 · 实体组件',AIDCSS,''.join(sheets))
 (O/'旗舰元年_6.2_实体组件.html').write_text(h,encoding='utf8');(R/'work/aids_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')

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
   content+='<p><b>'+E(c['specialName'])+'</b><br>'+E(c['specialSummary'])+'</p><p>全员锁定后现抽。严格超过本格且该批真实零售成交才合格；每公司每场最多选1奖。0星无奖。科技或工程试验另需该批已部署完成研发。不查首发或年龄。</p>'
   front.append('<article class="refcard" id="print-'+c['id']+'">'+content+'</article>')
  back='<article class="refcard back"><p>FLAGSHIP ERA / 6.2</p><h3>参考世代 '+str(era)+'</h3><p>全部锁定后才抽取<br>六张完整洗匀，允许重复</p></article>'
  for side,body in [('正面',''.join(front)),('背面',back*6)]:
   page=len(sheets)+1;sheets.append(f'<section class="sheet"><div class="head"><b>参考{era}代 · {side}</b><span>6.2 / {page}</span></div><div class="items refgrid">'+body+'</div><div class="foot">全桌1套 · 前后页长边翻转 · 同一代背面完全一致 · 原尺寸打印</div></section>');manifest.append({'page':page,'era':era,'side':side,'cards':[c['id'] for c in cards] if side=='正面' else []})
 (O/'旗舰元年_6.2_参考机正反面.html').write_text(g['document_html']('旗舰元年6.2 · 参考机正反面',AIDCSS,''.join(sheets)),encoding='utf8');(R/'work/reference_print_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')

def build_main_print(g):
 """等尺寸63×88mm主牌：257正面，配通用背面。数据能力完整保留。"""
 from bs4 import BeautifulSoup
 R,O,d,E=[g[k] for k in ('R','O','d','E')]
 cards=[c for c in d['parts'] if c['type']!='starter']+d['technologies']+d['contracts']+d['facilities']+d['schemes']
 expanded=[(c,i+1) for c in cards for i in range(c['qty'])]
 css=g['CSS']+'''
 .sheet{width:194mm;height:281mm;background:white;margin:16px auto;position:relative;overflow:hidden}.sheet .head{height:6mm;font-size:7pt;display:flex;justify-content:space-between;border-bottom:1px solid #aaa;align-items:center}.sheet .foot{position:absolute;bottom:0;font-size:6.5pt;color:#56707b}.main-grid{display:grid;grid-template-columns:repeat(3,63mm);grid-template-rows:repeat(3,88mm);gap:2mm;margin-top:1mm}.main-grid .card{width:63mm;height:88mm;padding:2mm 2mm 4.5mm;border-top-width:2px}.main-grid .card h3{font-size:10.8pt;line-height:1.2;margin-bottom:1mm}.main-grid .card p{font-size:8.6pt;line-height:1.36;margin:1.1mm 0}.main-grid .card p.small,.main-grid .card p.featurehint{font-size:7.2pt;line-height:1.25}.main-grid .card p.long{font-size:8.4pt;line-height:1.34}.main-grid .card .metric{font-size:7.2pt;padding:.7mm 1mm}.main-grid .card .metric b{font-size:10pt}.main-grid .card .metrics{gap:.7mm;margin:1mm 0}.main-grid .card table{font-size:7.5pt;line-height:1.23}.main-grid .card td,.main-grid .card th{padding:.65mm .5mm}.main-grid .eyebrow{font-size:6.1pt;margin-bottom:.8mm}.main-grid .bottom{font-size:5.6pt;bottom:1.1mm;left:2mm;right:2mm}.main-grid .factory{font-size:6.5pt;margin:.5mm 0;padding:.5mm 1mm}.main-grid .effect{padding-top:1mm}.main-back{width:63mm;height:88mm;border:1px dashed #91a8b4;background:repeating-linear-gradient(45deg,#e8eff2,#e8eff2 3mm,#dce7ed 3mm,#dce7ed 6mm);display:flex;align-items:center;justify-content:center;text-align:center;flex-direction:column;color:#1d475b}.main-back h3{font-size:19pt}.main-back p{font-size:9pt;margin-top:4mm}.blank{width:63mm;height:88mm;border:1px dashed #cad6dc;color:#8197a2;display:flex;align-items:center;justify-content:center;font-size:8pt}@media print{.sheet{margin:0;break-after:page}.sheet:last-child{break-after:auto}}
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
   front.append(str(card));manifest.append({'id':c['id'],'copy':copy,'frontPage':len(sheets)+1,'cell':len(front)})
  front+=['<div class="blank">空位，不是卡牌</div>']*(9-len(front))
  backs=['<div class="main-back"><h3>旗舰元年</h3><p>主牌 / 6.2</p><p>共同发布 · 单批产品</p></div>' if i<len(chunk) else '<div class="blank">空位</div>' for i in range(9)]
  mirrored=[]
  for row in range(3):mirrored+=backs[row*3:row*3+3][::-1]
  for side,body in [('正面',front),('背面',mirrored)]:
   page=len(sheets)+1;sheets.append(f'<section class="sheet"><div class="head"><b>统一主牌制卡 · {side}</b><span>63×88mm / 6.2 / {page}</span></div><div class="main-grid">'+''.join(body)+'</div><div class="foot">9卡/页 · 原尺寸A4 · 相邻页长边翻转双面 · 建议不透明牌套 · 无出血量产刀模</div></section>')
 (O/'旗舰元年_6.2_统一主牌正反面.html').write_text(g['document_html']('旗舰元年 6.2 · 257张统一主牌正反面',css,''.join(sheets)),encoding='utf8');(R/'work/main_print_manifest.json').write_text(json.dumps({'cards':manifest,'pages':len(sheets),'cardSizeMm':[63,88]},ensure_ascii=False,indent=2),encoding='utf8')
