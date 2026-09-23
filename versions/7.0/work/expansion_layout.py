"""7.0扩产实体件与现有静态版图的同步。无电子发牌、自动结算或保存。"""
import json
from pathlib import Path
from physical_layout import AIDCSS

def build_expansion_aids(g):
 R,O,d,E=[g[k] for k in ('R','O','d','E')]
 css=AIDCSS+'''
 .expand-panels{display:grid;grid-template-columns:repeat(2,94mm);gap:6mm;margin-top:6mm}.expand-panel{height:114mm;border:1px solid #b6c9cf;padding:4mm}.expand-panel h3{font-size:13pt;margin:0 0 3mm}.expand-panel p{font-size:8.3pt;line-height:1.5;margin:3mm 0}.expand-tokens{display:grid;grid-template-columns:repeat(4,20mm);gap:1.5mm}.expand-token{width:20mm;height:18mm;border:1px dashed #566e77;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;line-height:1.2;background:#edf5f6}.expand-token strong{font-size:13pt}.expand-token small{font-size:6pt}.expand-token.copy{background:#fff0df;color:#90540f}.expand-token.state{background:#e6edef}.expand-note{font-size:10pt;line-height:1.65;margin:5mm 0;padding:4mm;background:#eef5f6}.expand-box{padding:4mm;border:1px solid #b7c9d1;margin:4mm 0}.expand-box h3{font-size:13pt;color:#156c78;margin:0 0 2mm}.expand-box p{font-size:10pt;line-height:1.65;margin:1.5mm 0}.expand-box table{width:100%;border-collapse:collapse;font-size:9pt}.expand-box table th,.expand-box table td{padding:2mm 3mm;text-align:left;border-bottom:1px solid #b7ccd2}.expand-box table th{background:#e4eff0}.expand-box .status-table tbody td{height:20mm}.expand-box .status-table th:first-child,.expand-box .status-table td:first-child{width:12%}.expand-box .status-table th:not(:first-child),.expand-box .status-table td:not(:first-child){width:44%}.expand-table{width:100%;font-size:9pt;border-collapse:collapse}.expand-table td,.expand-table th{border-bottom:1px solid #b7ccd2;padding:2mm;text-align:left}.expand-table th{background:#e4eff0}.flowrank{display:flex;gap:2mm;margin:4mm 0}.flowrank span{border:1px solid #8aa6af;padding:3mm;font-size:11pt}.flowrank .loss{background:#eee;color:#77858b}.flowrank .win{background:#e5f2ef}.flowrank .copy{background:#fff0df}.rulewarning{font-size:10pt;color:#904d25;border-left:3px solid #bc743f;padding:3mm}
 '''
 pages=[];manifest=[]
 def page(title,body,note):
  n=len(pages)+1;pages.append(f'<section class="sheet"><div class="head"><b>{title}</b><span>7.0 / {n}</span></div>{body}<div class="foot">{note}</div></section>');manifest.append({'page':n,'title':title,'note':note})
 panels=[];tokens=[]
 for a in 'ABCD':
  tiles=[]
  for copy in (False,True):
   for slot in range(1,5):
    label=f'{a}{slot}'+('＋' if copy else '')
    tiles.append(f'<div class="expand-token {"copy" if copy else "original"}" data-company="{a}" data-product="{slot}" data-kind="{"expansion" if copy else "original"}"><strong>{label}</strong><small>{"扩产批" if copy else "原批队列"}</small></div>')
    tokens.append({'company':a,'slot':slot,'kind':'expansion' if copy else 'original','sizeMm':[20,18]})
  tiles.append(f'<div class="expand-token copy" data-company="{a}" data-kind="group"><strong>＋1</strong><small>{a}·放原产品旁</small></div>')
  tiles.append(f'<div class="expand-token state" data-company="{a}" data-kind="status"><strong>{a}</strong><small>扩产状态</small></div>')
  tokens.extend([{'company':a,'kind':'group','sizeMm':[20,18]},{'company':a,'kind':'status','sizeMm':[20,18]}])
  panels.append(f'<div class="expand-panel"><h3>{a}公司 · 扩产组件</h3><div class="expand-tokens">'+''.join(tiles)+'</div><p>原批片排临时队列；扩产只用与选中产品同号的＋片。另放一枚＋1到原配置旁。公司状态片从可用移到已用。</p><p>每人10件：4原批＋4扩产编号＋1组旁＋1状态。全场只使用其中1枚扩产编号，不是每种各能扩一次。</p></div>')
 page('扩产标记 · 全桌40件 · 单面剪取','<div class="expand-panels">'+''.join(panels)+'</div>','全桌印1份，不是每人印一整页 · 不混主牌 · 原有订单/参考标记继续使用 · 20×18毫米')
 table=g['table'](['公司','可用','已用'],[[a,'放状态片','成功付款后移到这里'] for a in 'ABCD']).replace('<table>', '<table class="status-table">')
 body='<div class="expand-note"><b>每公司每场一次，追加1批。</b> 初步有单不等于成交，全部市场扩产结束前，不收合同、销售或挑战款。</div>'
 body+='<div class="expand-box"><h3>四市场固定顺序</h3><p>大众消费 → 电竞娱乐 → 摄影创作 → 商务办公。</p><p>各市场按初步原批排名从高到低；轮到时仍有单才可选。放弃不回头，未用公司机会可留后面。</p></div>'
 body+='<div class="expand-box"><h3>每次三步</h3><p>① 试排：复制批与原批都能获单。</p><p>② 付费：完整制造款＋各项外部授权款；不执行部门行动，不付入库费。</p><p>③ 放片：原配置旁＋1、排名中公司产品＋；公司标为已用。</p></div>'
 body+='<div class="expand-box"><h3>同分次序</h3><p>真人原批 → 真人扩产批 → 参考机。</p><p>同一真人身份内：合格Q16 → 玩家顺序 → 产品位。Q16扩产批也不能压过同分原批。</p></div>'
 body+='<div class="expand-box"><h3>公司本场状态</h3>'+table+'</div>'
 page('扩产流程与限次面板 · 全桌共用',body,'整页不剪 · 普通发布整理后状态移回可用 · 最终发布照常扩产 · 不增加轮次')
 body='<div class="expand-box"><h3>三份订单的例子</h3><p>初步：A1=28，B1=25，B2=22，参考=20。</p><p>A1付款扩产后，顺序变成：</p><div class="flowrank"><span class="win">A1<br>28</span><span class="copy">A1＋<br>28</span><span class="win">B1<br>25</span><span class="loss">B2<br>22</span><span class="loss">参考<br>20</span></div><p>前三获单，B2被挤出。B1复制会排第四，不可扩产。B2原配置留到下一场，仍锁稳定栏。</p></div>'
 body+='<div class="expand-box"><h3>价牌基础收款小表</h3>'+g['table'](['售价','原批1批：现金/收入','原批＋扩产：现金/收入'],[[18,'18 / 1','36 / 2'],[28,'28 / 2','56 / 4'],[38,'38 / 3','76 / 6'],[48,'48 / 4','96 / 8']])+'<p>卡牌明确的逐批奖励另算。以上现金均在扩产结束后发放，不能预领。</p></div>'
 body+='<div class="expand-box"><h3>不要重复的东西</h3><p>挑战仍每公司每场1次；Q21只回实际一张；T41只转所选组原批收入；另一产品/另一市场/两样机不能由复制批凑出。</p><p>U11等首次正常组装优惠不用于扩产。外部技术再付1批许可，仍用原指派；授权费不被制造优惠减免。</p></div><div class="rulewarning">扩产不是新型号：不得改配置、改价格、改市场或再扩产。实际定制、Q、技术位和代替卡只清理一次；永久署名不收回。</div>'
 page('扩产收款与占用速查',body,'全桌印1份单面；也可每人自选复印速查 · 不是新增效果牌或跨场保留券')
 (O/'旗舰元年_7.0_扩产组件与速查.html').write_text(g['document_html']('旗舰元年7.0 · 扩产组件与速查',css,''.join(pages)),encoding='utf8')
 (R/'work/expansion_aids_manifest.json').write_text(json.dumps({'pages':manifest,'tokens':tokens,'physicalTokens':40,'countsPerCompany':{'originalRank':4,'expansionRank':4,'groupPlusOne':1,'status':1}},ensure_ascii=False,indent=2),encoding='utf8')

