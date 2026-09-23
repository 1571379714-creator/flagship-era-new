"""7.0实际线下阵列、对向轨道、行动牌与通用实体件。仅展示/切页/打印。"""
import json,math
from physical_layout import AIDCSS

BOARD_CSS='''*{box-sizing:border-box}body{margin:0;background:#e8eff2;color:#223e4a;font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif}header{background:#163f4d;color:white;padding:12px;position:sticky;top:0;z-index:5}header h1{font-size:20px;margin:0 10px 8px}button{padding:7px 13px;margin:3px;border:1px solid #8eaeb8;border-radius:4px;background:white;color:#244d5c}.board{display:none;width:400mm;height:277mm;background:white;margin:15px auto;padding:7mm;position:relative;overflow:hidden}.board.active{display:block}.title{display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid #316674;height:18mm}.title h2{font-size:22pt;margin:0}.title p{font-size:10pt}.subtitle{font-size:10pt;margin:3mm 0 5mm;line-height:1.6}.panel{border:1px solid #9db6bf;padding:5mm;min-width:0}.panel h3{font-size:15pt;margin:0 0 3mm}.panel h4{font-size:11pt;margin:3mm 0 1mm}.panel p{font-size:10pt;line-height:1.65;margin:2mm 0}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:5mm}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm}.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}table{border-collapse:collapse;width:100%;font-size:10pt;margin:3mm 0}th,td{border:1px solid #b6cbd1;padding:2mm;text-align:left}th{background:#e8f1f3}.legend{position:absolute;left:7mm;bottom:3mm;font-size:8pt;color:#52717d}.cardspace{border:1.3px dashed #a7bec6;border-radius:3mm;display:flex;align-items:center;justify-content:center;text-align:center;flex-direction:column;padding:3mm}.cells{display:flex;gap:1.5mm;flex-wrap:wrap;margin:3mm 0}.cell{width:16mm;height:16mm;border:1px solid #8eabb8;display:flex;align-items:center;justify-content:center;font-size:14pt}.factoryicon{width:6mm;height:6mm;vertical-align:middle}.tracksvg{width:386mm;height:230mm}.pointermini{width:10mm;height:9mm;border:1px dashed #346270;display:inline-flex;align-items:center;justify-content:center;margin:2mm;font-size:8pt}.array{display:grid;grid-template-columns:repeat(3,63mm);grid-template-rows:10mm 88mm 88mm;gap:4mm;width:max-content;margin:3mm auto}.array .label{text-align:center;font-size:15pt;font-weight:bold}.array .cardspace{width:63mm;height:88mm}.arraywrap{display:grid;grid-template-columns:225mm 1fr;gap:6mm}.rankgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:2mm}.rankcell{height:21mm;border:1px dashed #8ba4ad;padding:2mm;font-size:9pt;display:flex;align-items:center;gap:2mm}.rankcell b{font-size:13pt}.statewell{height:23mm;border:1px dashed #9bb4bc}.printall .board{display:block}@page{size:A3 landscape;margin:10mm}@media print{header{display:none}body{background:white}.board,.board.active{display:block;margin:0;break-after:page}.board:last-of-type{break-after:auto}*{print-color-adjust:exact;-webkit-print-color-adjust:exact}}'''

def opposed_track_svg():
    # U has 130 equal income steps: 32 up, 66 across, 32 down. T shares exact perimeter positions.
    def pt(v):
        if v<=32:return (12,218-6*v)
        if v<=98:return (12+(v-32)*5.5,26)
        return (375,26+(v-98)*6)
    a=['<svg class="tracksvg" viewBox="0 0 386 230" xmlns="http://www.w3.org/2000/svg" aria-label="收入0到130及科技0到46对向轨道">']
    a+=['<path d="M12 218V26H375V218" fill="none" stroke="#afc4cb" stroke-width="5"/>']
    for r in range(131):
        x,y=pt(r);fill='#d7e8ed' if r%5==0 else '#f2f6f7'
        a.append(f'<rect x="{x-2.6}" y="{y-2.65}" width="5.2" height="5.3" fill="{fill}" stroke="#5c7f8b" stroke-width=".2"/>')
        a.append(f'<text x="{x}" y="{y+.85}" font-size="2.5" text-anchor="middle" fill="#163f4d">{r}</text>')
    for t in range(47):
        v=130-(2*t if t<=8 else 3*t-8);x,y=pt(v)
        if v<32:tx,ty=x+14,y
        elif v>98:tx,ty=x-14,y
        else:tx,ty=x,y+14
        col='#d79f58' if t in (4,9,15,22) else '#3a6979'
        a.append(f'<line x1="{x}" y1="{y}" x2="{tx}" y2="{ty}" stroke="#bacad0" stroke-width=".3"/>')
        a.append(f'<circle cx="{tx}" cy="{ty}" r="2.7" fill="white" stroke="{col}" stroke-width=".45"/>')
        a.append(f'<text x="{tx}" y="{ty+.9}" text-anchor="middle" font-size="2.8" fill="#193f4c">{t}</text>')
    a+=['<text x="46" y="65" font-size="8" font-weight="bold" fill="#204a5a">收入 →　　　　　← 科技</text>',
        '<text x="46" y="78" font-size="4.2">收入 0—130  ·  科技 0—46</text>',
        '<text x="46" y="89" font-size="4">科技前8步一对二，此后每步一对三；对齐的收入格是交会线。</text>',
        '<text x="46" y="105" font-size="5" font-weight="bold">换代阈值　4 → Ⅱ　9 → Ⅲ　15 → Ⅳ　22 → Ⅴ</text>',
        '<text x="46" y="119" font-size="4">只看科技领先者；本人回合末开放；本准备期的参考世代不追涨。</text>',
        '<text x="46" y="141" font-size="5" font-weight="bold">同公司两标记相遇或越过 → 完成本回合 → 每人再行动一次</text>',
        '<text x="46" y="155" font-size="4">最后举行最终发布。没有收入60／科技30独立终局，也不取两项较大者。</text>',
        '<text x="46" y="180" font-size="4.2">读轨例：科技22对齐收入72。收入80为＋8，收入65为−7。</text>',
        '<text x="46" y="193" font-size="4">超收入130，每多1仍一格；超科技46，每多1仍跨三格，用数字片记录。</text>',
        '<text x="46" y="209" font-size="3.7">每家公司各放一枚收入标记、一枚科技标记。使用公司字母，不等同五厂颜色。</text>','</svg>']
    return ''.join(a)

def build_boards(g):
 R,O,d,E=g['R'],g['O'],g['d'],g['E'];table=g['table'];views=[]
 def add(id,title,subtitle,body,legend='原尺寸A3横向 · 仅线下展示/打印，无游玩或自动结算功能'):
  views.append((id,title,f'<section class="board" id="{id}"><div class="title"><h2>{title}</h2><p>旗舰元年 7.0</p></div><p class="subtitle">{subtitle}</p>{body}<div class="legend">{legend}</div></section>'))
 add('tracks','对向双轨 · 企业成绩','只看本人两标记是否相遇。线下将筹码放在编号格；连接线明确两条轨的对齐关系。',opposed_track_svg())
 add('market','共同市场与发布轨','需求提前公开；参考机只标世代，待全员锁定后才现抽。',
 '<div class="grid4">'+''.join(f'<div class="panel"><h3>{x["name"]}</h3><div class="cardspace" style="height:55mm">依需求卡预算/偏好<br>放本市场订单片</div><p>真人原批 → 扩产批 → 参考（同分）</p></div>' for x in d['markets'])+'</div>'+
 '<div class="grid2" style="margin-top:5mm"><div class="panel"><h3>发布轨　2人终点8／3人12／4人16</h3><div class="cells">'+''.join(f'<div class="cell">{i}</div>' for i in range(17))+'</div><p>制造与科研成果可预告；运营宣发需已有两批现货，放弃拿钱并付3现金。全桌无合法现货时最多到终点前一格。</p></div><div class="panel"><h3>本期公开信息</h3><div class="grid2"><div class="cardspace" style="height:52mm">当前需求N<br>每场仅1张</div><div class="cardspace" style="height:52mm">本场参考世代<br>Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ</div></div><p>供应换代不回头更换本场参考世代；末尾再标下场。</p></div></div>')
 add('array','个人行动阵列 · 六部门','每本人回合任选一张，按选前列号执行；行动后本行回1，再可交换两个1。所有行动始终可选。',
 '<div class="arraywrap"><div class="array">'+''.join(f'<div class="label">强度 {i}</div>' for i in (1,2,3))+''.join(f'<div class="cardspace"><b>{name}</b><p>放实际行动牌</p></div>' for name in ('调研','供应','制造','合作','研发','运营'))+'</div><div class="panel"><h3>整理只看本行</h3><p>①取出刚使用的牌。</p><p>②其余两张保持顺序，放到2、3。</p><p>③用过的牌放本行1。</p><p>④可以交换上下两个1，只换一次。</p><h3>另一行不升强度</h3><p>用1后，本行次序不变，仍可换两个1。没有禁用，没有全体恢复。</p><h3>发布不重置阵列</h3><p>完成行动、预告与阵列整理后才进入发布。额外拿牌、签装、研究进度、扩产均不移动阵列。</p></div></div>')
 add('action_summary','六行动 · 三档速查','一次行动读一格，不再分配3个通用工作点。研发的进度不能挪去造机。',
 table(['行动','强度1','强度2','强度3'],[[c['name']]+c['levels'] for c in d['actions']])+ '<div class="grid3"><div class="panel"><h3>制造预告</h3><p>强度1：无。强度2实际留1批，可＋1。强度3按本次新货，可＋至多2。</p></div><div class="panel"><h3>研发预告</h3><p>强度2或3真正完成该项目，可＋1。验证、奖励完成不预告。</p></div><div class="panel"><h3>运营宣发</h3><p>自己先有2批合法现货，付3现金，按1/2/3强度推进1/1/2。与拿钱二选一。</p></div></div>')
 add('supply','个人稳定库 · 四栏','实体不离库；同类代替卡读取本栏。只要仍有一个引用就不能替换。',
 '<div class="grid4">'+''.join(f'<div class="panel"><h3>{n}</h3><div class="cardspace" style="height:100mm">稳定实体<br>或初始通用件<br><br>此栏最多一张</div><p>普通／伙伴入库价读卡<br>每批制造费另付</p></div>' for n in ('芯片','屏幕','影像','机身'))+'</div><div class="panel" style="margin-top:6mm"><h3>供应不是制造</h3><p>供应强度1/2/3可安装1/1/2张；两张须不同类别。强度2/3实际安装后可盲抽一张，抽牌后不能继续安装它。T36可加一次安装，最多三类。</p><p>未来件可以入库，但不能参加制造或样机验证。被替换的旧稳定进主弃，初始件移出。已经组装的货不因新研究或换代自动变强。</p></div>')
 add('research','个人研发与合同','研究进度只看所选模式终点。先付完整研发费；联合另有核心/关联部件要求。',
 '<div class="grid2"><div class="panel"><h3>在研槽1／2</h3>'+''.join('<div class="cardspace" style="height:33mm;margin-bottom:3mm">在研实体T＋联合模式片（或自主）</div><div class="cells">'+''.join(f'<div class="cell" style="width:13mm;height:13mm">{v}</div>' for v in range(9))+'</div>' for _ in range(2))+'<p>U09才开启第三槽；不增加每次研发可处理的项目数。缺证据停待验证。</p></div><div class="panel"><h3>合同A · 开局唯一槽</h3><div class="cardspace" style="height:74mm">实际H卡<br>押金用现金筹码压在卡上<br>期限片按每次发布减少</div><h3>合同B · U10建成才开放</h3><div class="cardspace" style="height:45mm">未开放时不要放合同</div><p>关系、核心不占合同槽。签约不等于完成合作，不立即建立伙伴。</p></div></div>')
 add('product','单批产品面板 · 每人使用四个编号','完整四类＋可选一张Q＋合法技术指派。普通一个产品位就是一批货。',
 '<div class="grid4">'+''.join(f'<div class="panel"><h3>产品 {i}</h3><div class="cardspace" style="height:70mm">实际定制／稳定代替卡<br>芯片・屏幕・影像・机身</div><div class="cardspace" style="height:25mm;margin-top:3mm">可选产品方案Q</div><p>通常技术位2；指派片放T卡，不在本板抄技术名。</p><div class="cardspace" style="height:22mm">锁价片＋去向片</div><p>扩产时原组旁放＋1，不是新增产品位。</p></div>' for i in range(1,5))+'</div><p class="subtitle">T21仅在原始集成至少1时可用：自身0位、集成合计−1。仍用现有每产品三枚指派，无第四技术格。</p>')
 add('allocation','唯一投放 · 只移动产品编号','每个产品号仅放一处；公布后不可改价、改配件或临时改投。',
 table(['去向','待分单／交货','最终已售／已交付'],[[x['name'],'放①②③④号片','确认扩产结束后再移入'] for x in d['markets']]+[['合同A／B','按整单所有批次一起投','一次恰好交齐'],['留库','原样保留','不参加回购／扩产']])+ '<div class="grid2"><div class="panel"><h3>未售</h3><p>保持现配置与原授权，继续占位和锁库。下一场可重新选价与去向；不老化、不重复付款。</p></div><div class="panel"><h3>取消</h3><p>本人行动前或制造中取消，定制/Q回手，技术指派释放；原制造/授权款不退。不刷新任何限次。</p></div></div>')
 add('relations','供应商关系 · 不是五色阵营','任何玩家可与多厂合作，只能有一家核心；普通与伙伴安装价分别直接印卡。',
 table(['厂家','普通客户','合作伙伴','核心指示'],[[g['F'][f]['name'],'起始关系','已有真实业务后移入','仅一家'] for f in 'RYBGK'])+'<div class="grid2"><div class="panel"><h3>实际业务建立伙伴</h3><p>正式安装该厂非初始稳定件；用其定制实际付费组装；完成其订单或验证合同。先付旧关系价，结算后升级，不回溯。</p><h3>核心合作</h3><p>合作行动付12；已是伙伴、无未完联合项目。首次核心可并入第一次联合立项，研发行动取得完整1/2/4进度，不额外送1格。</p></div><div class="panel"><h3>公共技术不属于整个公司</h3><p>原作者也必须配套、放指派。外部使用需伙伴＋本厂关联部件＋逐批授权款。扩产再付一批，不重复科技。</p><h3>研究与授权</h3><p>独占更贵更久，但不开放给对手且配套自由。联合节省投入，完成后固定放核心厂公共区并永久署名。</p></div></div>')
 add('publictech','公共技术区 · 已完成的联合成果','可按五厂分开放置更多实际T卡；本页只是区域标题，不形成牌堆或市场。',
 '<div class="grid3">'+''.join(f'<div class="panel"><h3>{g["factory_icon"](f)} {g["F"][f]["name"]}</h3><div class="cardspace" style="height:72mm">放已完成联合技术<br>圆形署名＝作者<br>长方指派＝公司/产品</div></div>' for f in 'RYBGK')+'<div class="panel"><h3>授权只给这一产品组</h3><p>同项技术每公司通常一批。放指派前付全款；卖出或取消后收使用片，作者片整局不动。</p><p>原批未售：保留指派，后场不重付。扩产：原组＋1，再付每批授权，不生成新的技术实体。</p></div></div>')
 add('expansion','发布扩产 · 订单排序','每公司每场一次；先试排确认原批和追加批都获单，再付完整制造/授权款。',
 '<div class="grid2"><div class="panel"><h3>按行阅读：从高到低</h3><div class="rankgrid">'+''.join(f'<div class="rankcell"><b>{i}</b><span>原批 / ＋批 / 参考</span></div>' for i in range(1,22))+'</div></div><div class="panel"><h3>四市场依次处理</h3><p>大众 → 电竞 → 摄影 → 商务。同分真人原批先于真人扩产，真人先于参考；同类才比Q16、玩家序、产品号。</p>'+table(['公司','可用','已扩产'],[[a,'放状态片','全四市场共用'] for a in 'ABCD'])+'<h3>只复制一批同配置</h3><p>同定制/Q/技术、原价原市场，不新占位。后加入的批次不再扩产，不留下库存。</p><h3>先现金，后全部销售</h3><p>不能预支合同、退押、售价或挑战。已实际收取的他人扩产授权款可用于随后机会。</p></div></div>')
 add('workflow','发布与终局 · 完整顺序','先完成行动与阵列整理，再举行发布；发布期间没有新的六行动机会。',
 '<div class="grid2"><div class="panel"><h3>发布七步</h3>'+''.join(f'<p><b>{i+1}.</b> {t}</p>' for i,t in enumerate(['全员锁价、去向、指派；揭晓再现抽参考。','核验合同整单，暂不发钱、退押、清卡。','冻结分数和扩产费用；四市场临时分单→扩产→最终分单。','冻结最终成交、挑战与全部配置证据。','领取销售与成果，再结清现金、抽牌、工程、回购。','处理出口/返还及证据，统一收已结束产品与使用片；作者片不动。','结清签装/建设；期限、维护、牌市/N刷新；开放世代并标下场；发布复位。']))+'</div><div class="panel"><h3>绝不提前做</h3><p>四市场扩产未结束，不领取本场销售/合同/退押款。订单只是临时分到，不等于成交。新研究、关系、设施不重算本场产品。</p><h3>相遇后的最后阶段</h3><p>先完整结算当前回合；从当前行动者下一位起每人再一回合，行动者最后。推满不另开普通发布；最后统一最终发布，照常扩产和挑战。</p><h3>刷新一次就够</h3><p>牌市弃最左两张、左移补满8。换代不加牌。N换一张，V回同代完整6张候选。阵列永不因发布复位。</p></div></div>')
 nav=''.join(f'<button onclick="show(\'{i}\')">{t.split(" · ")[0]}</button>' for i,t,_ in views)
 html='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>旗舰元年7.0 线下版图</title><style>'+BOARD_CSS+'</style><body><header><h1>旗舰元年 7.0 · 线下版图</h1>'+nav+'<button onclick="document.body.classList.add(\'printall\');window.print();document.body.classList.remove(\'printall\')">打印全部</button></header>'+''.join(x[2] for x in views)+"<script>function show(id){document.querySelectorAll('.board').forEach(x=>x.classList.toggle('active',x.id===id));}show('tracks');</script></body></html>"
 (O/'旗舰元年_7.0_线下版图.html').write_text(html)
 (R/'work/boards_manifest.json').write_text(json.dumps({'views':[{'id':a,'title':b} for a,b,_ in views],'pages':len(views)},ensure_ascii=False,indent=2))

def build_action_cards(g):
 R,O,d=g['R'],g['O'],g['d'];E=g['E']
 css=AIDCSS+'''.actiongrid{display:grid;grid-template-columns:repeat(3,63mm);grid-template-rows:repeat(2,88mm);gap:2mm;margin:4mm auto;width:max-content}.actioncard{width:63mm;height:88mm;border:1px dashed #6a8997;padding:3mm;overflow:hidden}.actioncard h3{font-size:20pt;margin:0 0 3mm;color:#236171}.actioncard .line{display:grid;grid-template-columns:7mm 1fr;gap:1.5mm;padding:2mm 0;border-top:1px solid #bbcfd4;font-size:8.2pt;line-height:1.4}.line b{font-size:13pt}.actioncard .small{font-size:7.5pt;line-height:1.4;margin-top:2mm}.actioncard.back{background:#e7f0f2;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center}.actioncard.back p{font-size:10pt}'''
 fronts=[]
 for a in d['actions']:
  fronts.append(f'<article class="actioncard" id="action-{a["id"]}"><h3>{a["name"]}</h3>'+''.join(f'<div class="line"><b>{i+1}</b><span>{E(x)}</span></div>' for i,x in enumerate(a['levels']))+f'<p class="small">{E(a["note"])}</p></article>')
 back='<article class="actioncard back"><h3>旗舰元年</h3><p>部门行动 / 7.0</p><p>本行回1<br>可交换两个1<br>发布不重置</p></article>'
 pages=[]
 for side,items in [('正面',''.join(fronts)),('背面',back*6)]:
  pages.append(f'<section class="sheet"><div class="head"><b>六张部门行动 · {side}</b><span>63×88mm / 7.0</span></div><div class="actiongrid">{items}</div><div class="notes"><b>每人一套；全桌实际玩家数份。</b><p>初始：上行调研／供应／制造，下行合作／研发／运营，各行强度1／2／3。任选一张执行，本行其余保序入2／3，用牌回1，再可交换两个1。</p><p>每次只选一张行动；额外效果不另移牌。低强度可连续执行，发布不刷新阵列。</p></div><div class="foot">相邻页双面长边翻转 · 100%原尺寸 · 不混主牌 · 24张行动实体不计315张内容牌</div></section>')
 (O/'旗舰元年_7.0_六部门行动正反面.html').write_text(g['document_html']('旗舰元年7.0 六行动实体牌',css,''.join(pages)))
 (R/'work/action_cards_manifest.json').write_text(json.dumps({'perPlayer':6,'pages':2,'sizeMm':[63,88],'initial':d['actionSystem']['initialRows'],'ids':[a['id'] for a in d['actions']]},ensure_ascii=False,indent=2))

def build_aids(g):
 R,O,d,E,K=[g[k] for k in ('R','O','d','E','K')];pages=[];manifest=[]
 def page(title,body,note):
  n=len(pages)+1;pages.append(f'<section class="sheet"><div class="head"><b>{title}</b><span>7.0 / {n}</span></div>{body}<div class="foot">{note}</div></section>');manifest.append({'page':n,'title':title,'note':note})
 css=AIDCSS+'table{width:100%;border-collapse:collapse;font-size:8.3pt;line-height:1.5}th,td{border:1px solid #b5c8d0;padding:1.5mm}th{background:#eaf1f3}.pricegrid{grid-template-columns:repeat(4,1fr);grid-auto-rows:57mm}.tag{border:1px dashed #678791;display:flex;align-items:center;justify-content:center;width:22mm;height:17mm;font-size:13pt}.taggrid{display:grid;grid-template-columns:repeat(7,22mm);gap:4mm;margin:6mm 0}.smallnotes{font-size:9pt;line-height:1.8;margin:4mm}.proxygrid{grid-template-columns:repeat(4,1fr);grid-auto-rows:56mm}.a-table td{height:19mm}.strip .cell{min-height:10mm}'
 prices=[]
 for slot in range(1,5):
  for price,mod,inc in zip(d['parameters']['prices'],d['parameters']['priceScore'],d['parameters']['incomePerBatch']):
   prices.append(f'<div class="tile"><h3>产品 {slot}</h3><div class="big">{price}</div><p>竞争力 {mod:+d}</p><p>1批：{price}现金／{inc}收入<br>扩产2批：{price*2}现金／{inc*2}收入</p><p class="sub">48价另查基础28＋芯12或影像8</p></div>')
 page('四产品秘密价牌 · 正面','<div class="items pricegrid">'+''.join(prices)+'</div>','每人1套16张 · 下一页为背面 · 长边翻转双面')
 backs=[]
 for slot in range(1,5):
  backs+= [f'<div class="tile back"><h3>产品 {slot}</h3><p>秘密价格<br>锁定后一起揭晓</p></div>']*4
 page('四产品秘密价牌 · 背面','<div class="items pricegrid">'+''.join(backs)+'</div>','同行四张背面相同，镜像后对应同一产品号；实际打印先试一页')
 page('稳定部件代替卡 · 四类各四张','<div class="items proxygrid">'+''.join(f'<div class="tile"><h3>稳定部件</h3><div class="big">{name}</div><p>读取本人稳定库同类实体。<br>这是引用，不是初始通用件。</p><p>有任何引用，就不能换库。</p></div>' for name in ('芯片','屏幕','影像','机身') for _ in range(4))+'</div>','每人16张 · 单面 · 不混牌堆 · 原实体始终留库')
 page('投放与最终成交','<table class="a-table"><tr><th>去向</th><th>锁定／临时</th><th>最终成交</th></tr>'+''.join(f'<tr><td>{m}</td><td>放产品号片</td><td>全部扩产后再移动</td></tr>' for m in ('大众消费','电竞娱乐','摄影创作','商务办公','合同A／B','留库'))+'</table><div class="taggrid">'+''.join(f'<div class="tag">{i}</div>' for i in range(1,5))+'</div><p class="smallnotes">每产品一个目的地；扩产沿原目的地且必当场卖完。未售原产品回保留状态，既有授权不用重新付款，不设置年龄。</p>','每人一张表＋四产品号片；不得把同一批重复承诺给两个市场/合同')
 body=''
 for name in ['在研1','在研2','在研3（U09才开放）']:
  body+=f'<div class="strip"><b>{name}</b><div class="cells">'+''.join(f'<div class="cell">{i}</div>' for i in range(9))+'</div></div>'
 body+='<div class="strip"><b>独立验证 · 每当前世代至多一次</b><div class="cells">'+''.join(f'<div class="cell">{e}</div>' for e in ('Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ'))+'</div></div><p class="smallnotes">每次研发只选1项目，强度1／2／3推进1／2／4（已含立项）。联合与自主终点直接读卡，不乘倍数。独立验证替代常规研发，付12，基础≥12且至少2特征；T32等按卡例外。</p>'
 page('在研进度与验证标记',body,'每人一份 · 每项目一枚进度片 · 不新增工作点或额外技术格')
 page('原有技术指派 · 使用速查','<div class="notes"><h2>不在这里重复剪一套技术片</h2><p>实际指派和署名请用独立《供应商署名与授权组件》。每人12枚指派：四个产品号各三枚；无需增加到16枚。</p><h3>研发者与使用者分开</h3><p>圆形署名永久留在公开技术上；长方指派表示哪家公司哪批在使用。准备期背面只露公司，发布翻出产品号。</p><h3>T21专门处理集成</h3><p>仅当原始部件集成≥1才能部署。自身0技术位、集成合计减1，普通总容量仍2。最多T21＋两项其他技术，用三枚现有指派。</p><h3>扩产的授权</h3><p>同产品原组＋1，不再放第二套指派；外部技术再付一份卡面每批授权款。取消/销售后一次清理实体，作者圆片不动。</p></div>','此页仅速查，不是功能片新增页')
 page('核心、合同与即时奖励','<div class="notes"><h2>一个合同槽，不等于一个供应商</h2><p>默认执行合同槽A；U10可开放B。供应商关系和一家核心身份不占槽。先支付费用/押金，期限定在实际发布减少。</p><h2>首次核心合并研发</h2><p>已是伙伴、尚无核心、满足项目及本厂关联部件时，支付12＋联合费，一次研发立项取得该强度完整进度。之后换核心用合作行动，未完联合项目先完成或放弃。</p><h2>不保留三类券</h2><p>供货签装、建设支持在本场配置清理后执行；不算供应/合作，不附抽、不额外移行动。渠道回购只处置另一批合法未售零售原货，不重复成交奖励。</p><h2>宣发不是免费预热</h2><p>运营拿6／12／18现金，或本人原有至少两批合法货时，放弃拿钱并付3，推进1／1／2。制造与科研预告当场可放弃。</p></div>','核心费、研究费、入库费和每批制造/授权费分别计算')
 states=['已收款','待验证','期限1','期限2','已用','停用','集成1','进度']
 page('通用状态与订单片','<div class="tokens">'+''.join(f'<div class="token">{name}<br>{i+1}</div>' for name in states for i in range(3))+'</div><div class="smallnotes">“已用”放来源卡，回合或准备期限次依卡面复位。取消不复位。状态片不是可以兑换的资源；没有通用工作点。</div>','每人一套或用普通方块替代；订单片在下一页全桌准备')
 page('公共订单／时代与越界','<div class="tokens">'+''.join(f'<div class="token">零售订单<br>{i}</div>' for i in range(1,17))+'</div><div class="taggrid">'+''.join(f'<div class="tag">{x}</div>' for x in ['Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ','＋1','＋3','＋5','＋10','＋20','＋50'])+'</div><div class="smallnotes">需求每市场最多5单，总量最多16；不需为每市场另印16片。超收入130的现金形数字片在轨旁记录，不当现金使用。超科技46每1科技跨三收入格，保持两种越界状态分开放。</div>','全桌一套 · 数字筹码可用通用游戏筹码补足，不从牌堆抽取')
 page('一页行动与支付速查',g['table'](['行动','强度1','强度2','强度3'],[[a['name']]+a['levels'] for a in d['actions']])+'<div class="smallnotes"><b>制造费</b>＝四部件制造费＋组装费8＋Q费−合法减免，最低6；授权款另加、付原作者。<br><b>入库</b>读普通/伙伴价，不同卡差额不同；首次业务不回溯优惠。<br><b>48售价</b>通常基础≥28，并满足芯片≥12或影像≥8至少一项。<br><b>相遇</b>130收入对46科技，前8步一对二、后面一对三；相遇完成当回合后每人再行动一次。</div>','纯速查 · 强度不是工作点，不可拆成跨部门自由操作')

 cash_values=[1]*32+[5]*12+[10]*12+[20]*12+[50]*12+[100]*12
 cash_html='<div style="display:grid;grid-template-columns:repeat(10,18mm);gap:1mm;margin-top:5mm">'+''.join(f'<div style="height:15mm;border:1px dashed #719099;text-align:center;display:flex;flex-direction:column;justify-content:center"><b style="font-size:15pt">{v}</b><small style="font-size:6pt">现金</small></div>' for v in cash_values)+'</div>'
 cash_html+='<p class="smallnotes">可选现金纸片：总值2252，初始每人120。全桌印1份，可复印补足找零；也可用现成现金筹码。现金不放收入轨，以下小片才是成绩指示。</p><div style="display:flex;gap:3mm;margin:6mm 0">'+''.join(f'<div style="width:4.5mm;height:4.5mm;border:1px solid #315561;font-size:6pt;text-align:center;line-height:4.5mm">{a}</div>' for a in 'AABBCCDD')+'</div><p class="smallnotes">每家公司2个小指示片，一个放收入轨、一个放科技轨；字母区分公司，所在轨区分意义。现金纸片与成绩超出数字片分开使用。实际打印可用4毫米棋钉替换。</p>'
 page('现金纸片与成绩指示 · 可选剪取',cash_html,'全桌1份；找零不足可复印 · 不新增资源种类 · 使用现成现金/小棋钉时可不印')
 (O/'旗舰元年_7.0_实体组件.html').write_text(g['document_html']('旗舰元年7.0 实体组件',css,''.join(pages)))
 (R/'work/aids_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
