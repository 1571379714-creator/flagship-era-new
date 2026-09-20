"""5.0线下静态版图及可反复使用的组件。按钮仅切换视图或打印。"""
from v50_common import *
from collections import Counter

BOARD_CSS='''
*{box-sizing:border-box}body{margin:0;color:#28463c;background:#dce3d9;font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif}header{padding:17px 22px;background:#243f36;color:#f9f6e8;display:flex;gap:15px;align-items:center;flex-wrap:wrap}header h1{font:700 24px "Noto Serif CJK SC";margin:0;letter-spacing:4px}header small{font-size:10px;color:#c5cebb}nav{display:flex;gap:5px;flex-wrap:wrap;flex:1}button,header a{font:12px "Noto Sans CJK SC";color:inherit;border:1px solid #8caa9580;background:transparent;padding:8px 11px;text-decoration:none;cursor:pointer}button.selected{background:#ebedda;color:#2c493c}main{padding:18px;max-width:1580px;margin:auto}.viewport{position:relative;width:100%;overflow:hidden;display:none;box-shadow:0 9px 30px #16332520}.viewport.active{display:block}.map{position:absolute;width:1480px;height:960px;left:0;top:0;transform-origin:top left;background:#f0eddd;isolation:isolate;overflow:hidden}.map:before{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(140deg,#f6f3e7d9,#e3e9dacc),repeating-linear-gradient(90deg,transparent,transparent 29px,#a5ab9060 30px),repeating-linear-gradient(0deg,transparent,transparent 29px,#a5ab9060 30px)}.map:after{content:"";position:absolute;inset:12px;border:1px solid #b8bea052;pointer-events:none}.map-head{position:absolute;left:75px;right:75px;top:38px;display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid #4e705b;padding-bottom:18px}.map-head h2{font:700 33px "Noto Serif CJK SC";letter-spacing:4px;margin:0 0 9px}.map-head p{font-size:13px;letter-spacing:1px;color:#71816d;margin:0}.edition{font:42px Georgia;color:#a38a58}.footnote{position:absolute;left:75px;right:75px;bottom:28px;font-size:12px;color:#77816b;border-top:1px solid #bdc6ac;padding-top:10px;display:flex;justify-content:space-between}.panel{background:#fffdf4d9;border:1px solid #b2c0a6;border-radius:7px;padding:20px;box-shadow:0 3px 10px #25463109}.panel h3{font:700 23px "Noto Serif CJK SC";margin:0 0 14px;color:#315c48}.panel p{font-size:14px;line-height:1.9;margin:5px 0}.box-label{font-size:11px;letter-spacing:2px;color:#8b8a6b}.empty{border:1px dashed #a7b699;border-radius:4px;text-align:center;color:#89967c;background:#f3f5eaaa;display:flex;align-items:center;justify-content:center;flex-direction:column}.empty strong{font:32px Georgia;color:#9e956e}.empty small{font-size:11px;line-height:1.8}.screen-note{max-width:1550px;margin:0 auto 18px;padding:0 20px;font-size:12px;line-height:1.9;color:#6d7e69}.rail{position:absolute;inset:0;pointer-events:none}.central-head{left:145px;right:145px;top:38px}.card-market{position:absolute;left:145px;right:145px;top:186px;display:grid;grid-template-columns:repeat(8,1fr);gap:12px}.card-market .empty{height:220px}.card-market .empty strong{font-size:34px;margin-bottom:12px}.market-grid{position:absolute;left:145px;right:145px;top:433px;display:grid;grid-template-columns:repeat(4,1fr);gap:15px}.market-grid .panel{height:221px;padding:18px}.market-grid h3{font-size:24px;text-align:center;margin-bottom:14px}.market-grid p{font-size:12px;text-align:center;line-height:1.7}.compact-price{width:100%;font-size:11px;border-collapse:collapse;margin-top:10px}.compact-price td{border-bottom:1px solid #d9dfca;padding:4px 3px;text-align:center}.compact-price th{font-weight:500;color:#72816d;font-size:10px;text-align:center}.release{position:absolute;left:145px;right:145px;top:677px;background:#e7dfc4;border:1px solid #b4a176;border-radius:7px;padding:15px 19px}.release h3{font-size:18px;margin:0 0 12px}.releasecells{display:flex;gap:6px}.release-cell{flex:1;height:49px;background:#f4ecd6;border:1px solid #b8aa86;text-align:center;border-radius:3px;padding:4px 0}.release-cell b{display:block;font:20px Georgia;color:#786244}.release-cell small{font-size:9px}.release-cell.end{border:2px solid #9f7f47;background:#dac395}.release p{font-size:11px;margin:10px 0 0}.central-sub{position:absolute;left:150px;right:150px;top:143px;display:flex;justify-content:space-between;font-size:12px;color:#6f7b65}.era-grid{position:absolute;left:75px;right:75px;top:161px;display:grid;grid-template-columns:repeat(5,1fr);gap:15px}.era{padding:14px 18px;background:#e8ecd9;border:1px solid #b6c4a4;border-top:4px solid #718a5c;border-radius:5px}.era b{font-size:19px}.era span{float:right;font:22px Georgia;color:#967b45}.era p{font-size:12px;line-height:1.7;margin:7px 0 0}.supply-rows{position:absolute;left:75px;right:75px;top:285px;display:flex;flex-direction:column;gap:14px}.supply-row{height:132px;display:grid;grid-template-columns:150px repeat(4,1fr);gap:14px;background:#fffdf2bd;border:1px solid #b8c8ae;border-radius:7px;padding:13px}.supply-kind{display:flex;flex-direction:column;justify-content:center;border-right:1px solid #d3dbbd}.supply-kind b{font:23px "Noto Serif CJK SC"}.supply-kind small{font-size:10px;margin-top:8px}.supply-row .empty{position:relative}.supply-row .empty>span{font-size:12px}.supply-row .empty small{margin-top:7px}.supply-row .empty strong{font-size:25px}.prices-main{position:absolute;left:90px;right:90px;top:175px}.price-table{width:100%;border-collapse:collapse;background:#fffdf4;border:1px solid #aec0a8;table-layout:fixed}.price-table th{background:#345642;color:white;font-size:18px;padding:17px}.price-table td{font-size:27px;text-align:center;padding:25px 10px;border:1px solid #cad5bd}.price-table td:first-child{font:25px "Noto Serif CJK SC"}.price-notes{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:25px}.price-notes .panel{height:231px}.personal-body{position:absolute;left:65px;right:65px;top:163px;display:grid;grid-template-columns:370px 1fr;gap:25px}.bank{height:407px}.bank table{width:100%;border-collapse:collapse;margin-top:16px;font-size:12px}.bank td,.bank th{border-bottom:1px solid #d1d9c5;padding:8px 3px;text-align:left}.bank th{color:#7a866c}.stats{display:flex;gap:9px;margin:8px 0}.stats span{background:#e7eddc;padding:8px 14px;border-radius:5px;font-size:12px}.stats b{font:23px Georgia;margin-left:8px}.preps{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.prep{height:407px;text-align:center;padding:17px}.prep .prep-n{font:33px Georgia;color:#a58a52}.prep h3{font-size:22px}.prep p{font-size:12px}.prep .empty{height:128px;margin:15px 0;font-size:16px;gap:8px}.prep.locked{background:repeating-linear-gradient(45deg,#e7e7d7,#e7e7d7 6px,#eeeddf 6px,#eeeddf 12px)}.t19{border:1px solid #adba9f;padding:8px;font-size:11px;color:#768267;border-radius:20px;margin-top:10px}.company-note{position:absolute;left:65px;right:65px;top:590px;display:flex;justify-content:space-between;font-size:12px;color:#6b7c67}.growth-grid{position:absolute;left:65px;right:65px;top:626px;display:grid;grid-template-columns:repeat(7,1fr);gap:12px}.growth{height:155px;border:1px solid #b4c1a5;background:#f9f7e9e8;border-radius:5px;padding:13px;position:relative}.growth h4{font:18px "Noto Serif CJK SC";margin:9px 0}.growth small{font-size:11px;color:#a1864f}.growth p{font-size:11px;line-height:1.7;margin:0 0 6px}.growth b{font-size:11px;font-weight:500}.dot{width:15px;height:15px;border:1px solid #8d9e79;border-radius:50%;position:absolute;right:10px;top:12px;background:#fffdf2}.actionrow{position:absolute;left:65px;right:65px;top:810px;display:grid;grid-template-columns:repeat(5,1fr);gap:17px}.actionpos{border-top:4px solid #4e7257;background:#e2e9d6;padding:12px 16px;height:70px}.actionpos strong{float:right;font:30px Georgia;color:#9f8251}.actionpos b{font-size:17px}.actionpos p{margin:5px 0 0;font-size:10px}.project-headnote{position:absolute;left:75px;right:75px;top:165px;line-height:1.9;font-size:15px;text-align:center}.project-grid{position:absolute;left:65px;right:65px;top:256px;display:grid;grid-template-columns:repeat(4,1fr);gap:22px}.project-slot{height:457px;text-align:center}.project-slot .empty{height:210px;margin:18px 0}.tier-slots{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:20px}.tier-slot{height:95px;border:1px solid #b4c0a5;background:#edf0df;position:relative;padding-top:40px;font-size:14px}.tier-slot .dot{left:calc(50% - 8px);right:auto;top:12px}.tier-slot small{display:block;font-size:10px;margin-top:4px}.project-bottom{position:absolute;left:75px;right:75px;top:748px;display:grid;grid-template-columns:1fr 1fr;gap:25px}.project-bottom .panel{height:128px}.project-bottom h3{font-size:19px}.project-bottom p{font-size:12px}.special-grid{position:absolute;left:75px;right:75px;top:220px;display:grid;grid-template-columns:repeat(3,1fr);gap:20px;grid-auto-rows:284px}.special-slot{padding:17px}.special-slot h3{font-size:20px}.special-slot .empty{height:115px;margin:15px 0}.special-slot p{font-size:12px}.factory-panels{position:absolute;left:75px;right:75px;top:185px;display:grid;grid-template-columns:repeat(5,1fr);gap:20px}.factory-panel{text-align:center;height:340px;border-top:5px solid var(--factory)}.factory-panel h3{margin:18px 0 13px}.factory-panel .numbers{font:20px Georgia;color:#9f8452}.factory-lower{position:absolute;left:75px;right:75px;top:557px;display:grid;grid-template-columns:repeat(3,1fr);gap:22px}.factory-lower .panel{height:278px}.factory-lower p{font-size:14px}.factory-lower h3{font-size:21px}@page{size:A3 landscape;margin:5mm}@media print{body{background:white}header,.screen-note{display:none}main{padding:0;max-width:none}.viewport{display:none!important;box-shadow:none}.viewport.active{display:block!important;width:410mm;height:266mm!important}.map{transform:scale(1.047)!important}*{print-color-adjust:exact;-webkit-print-color-adjust:exact}}@media(max-width:850px){header{padding:12px}nav{flex-basis:100%}main{padding:8px}button{padding:6px;font-size:10px}}
'''+FACTORY_CSS

def point(i,inner=False):
 if i<=24:x,y=38,130+758*i/24
 elif i<=75:x,y=38+1404*(i-24)/51,888
 else:x,y=1442,888-758*(i-75)/25
 if not inner:return x,y
 # Parallel straight segments share exact alignment; only corners need diagonal guides.
 if i<=24:return 82,min(y,844)
 if i<=75:return max(82,min(x,1398)),844
 return 1398,min(y,844)

def rail_svg():
 s='<svg class="rail" viewBox="0 0 1480 960" xmlns="http://www.w3.org/2000/svg"><path d="M38 130V888H1442V130" fill="none" stroke="#a9baa0" stroke-width="33" stroke-linejoin="round"/><path d="M82 130V844H1398V130" fill="none" stroke="#92adb4" stroke-width="34" stroke-linejoin="round"/><path d="M82 130V844H1398V130" fill="none" stroke="#e6eef0" stroke-width="30" stroke-linejoin="round"/>'
 for i in range(101):
  x,y=point(i);w,h=(36,26) if i<=24 or i>=75 else (24,29)
  fill='#587455' if i%10==0 else '#faf8ea';col='white' if i%10==0 else '#496647'
  s+=f'<g data-income="{i}"><rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="#90a184"/><text x="{x}" y="{y+4}" text-anchor="middle" font-family="Noto Sans CJK SC" font-size="12" fill="{col}">{i}</text></g>'
 alignment=d['scoreTrack']['alignment']
 for t,pos in enumerate(alignment):
  x,y=point(pos,True);ox,oy=point(pos)
  s+=f'<g data-tech="{t}" data-income-align="{pos}"><path d="M{x} {y}L{ox} {oy}" stroke="#7b9ca4" stroke-width="1" stroke-dasharray="2 3"/><rect x="{x-15}" y="{y-13}" width="30" height="26" rx="7" fill="'+('#335f70' if t in [0,8,36] else '#eef3f3')+'" stroke="#7797a0"/>'
  s+=f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Noto Sans CJK SC" font-weight="600" font-size="13" fill="'+('white' if t in [0,8,36] else '#315b69')+f'">{t}</text></g>'
  if t<len(alignment)-1:
   mid=(pos+alignment[t+1])/2;xx,yy=point(mid,True)
   if mid<=24 or mid>=75:s+=f'<path d="M{xx-17} {yy}H{xx+17}" stroke="#91adb2"/>'
   else:s+=f'<path d="M{xx} {yy-17}V{yy+17}" stroke="#91adb2"/>'
 s+='<text x="38" y="87" text-anchor="middle" font-size="12" fill="#486244">收入</text><text x="82" y="105" text-anchor="middle" font-size="11" fill="#315b69">科技36</text><text x="1398" y="87" text-anchor="middle" font-size="12" fill="#315b69">科技</text><text x="1442" y="105" text-anchor="middle" font-size="11" fill="#486244">收入100</text><text x="740" y="943" text-anchor="middle" font-size="12" fill="#54735c">外侧收入0→100　·　内侧科技0→36反向前进　·　以科技对齐线判断同一玩家的标记相遇或越过</text></svg>'
 return s

def head(title,sub,central=False):return f'<div class="map-head {"central-head" if central else ""}"><div><h2>{title}</h2><p>{sub}</p></div><div class="edition">5.0</div></div>'
def foot(left,right='旗舰元年 · 线下展示 / 打印'):return f'<div class="footnote"><span>{left}</span><span>{right}</span></div>'
def mini_price():
 out='<table class="compact-price"><tr><th>价格</th><th>第一</th><th>第二</th></tr>'
 for p in d['pricing']['strategies']:out+=f'<tr><td>{p["name"]}</td><td>{p["incomeByRank"][0]} / {p["cashByRank"][0]}</td><td>{p["incomeByRank"][1]} / {p["cashByRank"][1]}</td></tr>'
 return out+'</table>'

def central():
 s=rail_svg()+head('旗舰元年 · 中央市场','秘密组装  /  同时定价  /  共同发布',True)
 s+='<div class="central-sub"><span>牌市：取走立即左移补牌；普通调研选序号≤强度，升级可选全部8位</span><span>正常回款：20＋当前收入　｜　最终发布不回款</span></div>'
 s+='<div class="card-market">'+''.join(f'<div class="empty" data-market-slot="{i}"><strong>{i}</strong><span>主牌陈列</span><small>企划 · 科技 · 企业<br>专项 · 已解锁定制</small></div>' for i in range(1,9))+'</div>'
 s+='<div class="market-grid">'+''.join(f'<div class="panel"><h3>{m}</h3><p>每公司只用最强新机作为代表<br>收益显示：收入 / 现金</p>{mini_price()}</div>' for m in ['大众消费','电竞娱乐','摄影创作','商务办公'])+'</div>'
 s+='<div class="release"><h3>共同发布轨 <small style="font-size:11px;font-weight:400;margin-left:18px">到达人数终点：当前行动完成后立即发布，无响应回合</small></h3><div class="releasecells">'
 for i in range(15):s+=f'<div class="release-cell {"end" if i in [8,11,14] else ""}" data-release="{i}"><b>{i}</b><small>'+({0:'起点',8:'2人终点',11:'3人终点',14:'4人终点'}.get(i,''))+'</small></div>'
 s+='</div><p>定价并揭晓 → 按筹备位验收付款 → 有效新机同时上市 → 代表机排名与奖励 → 正常回款 / 归库 / 消耗；回合末成长、升级、供应维护。</p></div>'
 return s

def supply():
 s=head('分代供应链','公开限量供应 · 先拿先得 · 买走不立即补货')
 s+='<div class="era-grid">'+''.join(f'<div class="era"><b>{ROM[i]}　{d["supply"]["eraNames"][i-1]}</b><span>{"开局" if i==1 else "科"+str(d["supply"]["eraThresholds"][i-1])}</span><p>稳定批次加入活动供应堆<br>定制批次洗入剩余主牌</p></div>' for i in range(1,6))+'</div><div class="supply-rows">'
 for kind in ['chip','screen','camera','body']:
  s+=f'<div class="supply-row"><div class="supply-kind"><b>{KINDS[kind]}</b><small>活动供应堆置邻侧<br>左旧 → 右新</small></div>'
  for i in range(1,5):s+=f'<div class="empty" data-supply-kind="{kind}" data-supply-slot="{i}"><strong>{i}</strong><span>公开配件</span><small>'+('各人数均使用' if i<=2 else '3／4人使用' if i==3 else '仅4人使用')+'</small></div>'
  s+='</div>'
 s+='</div>'+foot('通常每次调研最多采购1张，花1个基础额度；不付采购价，每次制造仍付款。','回合末统一补货／换代；同回合合并处理，不连续双刷。')
 return s

def pricing():
 s=head('秘密定价 · 公开收益','每人三套定价牌，每个筹备位从自己的三张中选一张；先锁定，再一起翻开')
 s+='<div class="prices-main"><table class="price-table"><tr><th>定价策略</th><th>吸引力修正</th><th>第一名<br><small>收入 / 现金</small></th><th>第二名<br><small>收入 / 现金</small></th><th>第三／第四<br><small>收入 / 现金</small></th></tr>'
 for p in d['pricing']['strategies']:s+=f'<tr><td>{p["name"]}</td><td>{p["appealDelta"]:+d}</td>'+''.join(f'<td>{p["incomeByRank"][i]} / {p["cashByRank"][i]}</td>' for i in range(3))+'</tr>'
 s+='</table><div class="price-notes"><div class="panel"><h3>只有代表机领奖</h3><p>每公司、每市场，最终吸引力最高的新机为代表。同公司同分取较小筹备位。按代表机价格结算一次。</p><p>同市场其他新机仍取得企划收入与自身效果，不再另领市场收益。</p></div><div class="panel"><h3>先付款，后领钱</h3><p>价格不改变验收、科技、制造费或厂标门槛。低价不能救活不合法配置。</p><p>所有制造费付完后，才领取本场销售与企划现金；不能垫付。</p></div><div class="panel"><h3>每场重新秘密选择</h3><p>允许三台全部同价。未选牌留屏后；漏放、多放或编号错误按标准价。</p><p>最终发布也按表增加收入。价格牌和调校标记结算后收回。</p></div></div></div>'
 return s+foot('完整收益表替代旧版固定3／1收入，不叠加旧市场奖励。')

def personal(b):
 s=head(b['name'],'个人版图 · 类别专长：'+b['tag']+' · 不绑定厂家阵营')
 parts={c['id']:c for c in d['starters']};plan=next(c for c in d['cards'] if c['id']==b['plan'])
 s+='<div class="personal-body"><div class="panel bank"><h3>公司资源与稳定配件库</h3><div class="stats"><span>现金<b>60</b></span><span>收入<b>5</b></span><span>科技<b>0</b></span></div><p style="font-size:12px">起始企划 '+b['plan']+' '+plan['name']+'<br>无厂标；不是第六厂，不是任意厂通配。</p><table><tr><th>初始配件</th><th>制造</th><th>吸引力</th><th>功／供</th></tr>'
 for cid in b['starterIds']:
  c=parts[cid];v=c['components'][0];s+=f'<tr><td>{cid} {c["name"]}</td><td>{v["cost"]}</td><td>{v["appeal"]}</td><td>'+('供' if v['kind']=='body' else '耗')+str(v['load'])+'</td></tr>'
 s+='</table><p style="font-size:11px;margin-top:13px">稳定卡公开持有；每张本场只供一机。发布后回库，每次使用仍付制造费。</p></div><div class="preps">'
 for i in range(1,4):s+=f'<div class="panel prep {"locked" if i==3 else ""}"><span class="prep-n">{i:02}</span><h3>秘密筹备位</h3><p>'+('科技≥5且已上市≥2张<br>达成A3永久开放' if i==3 else '完整四类部件<br>企划与配置保持秘密')+f'</p><div class="empty">企划＋芯片＋屏幕<br>影像＋机身<small>一个实体不能重复占用</small></div><p>价格牌编号 {i} · 发布前秘密三选一</p><div class="t19">T19节能调校 · 标记格 {i}</div></div>'
 s+='</div></div><div class="company-note"><span>公司区域：已上市企划＋已打科技＋已打企业　｜　类别与厂家分开累计</span><span>起始牌之外的公司牌摆在版图邻侧；R/J项目均为公共牌</span></div><div class="growth-grid">'
 for a in d['achievements']:
  s+=f'<div class="growth"><i class="dot"></i><small>{a["id"]}</small><h4>{a["name"]}</h4><p>{E(a["condition"])}</p><b>{"对应专长类别的新机<br>永久费用减3" if a["id"]=="A7" else E(a["reward"])}</b></div>'
 s+='</div><div class="actionrow">'
 for i,a in enumerate(d['actions'],1):s+=f'<div class="actionpos"><strong>{i}</strong><b>强度位置 {i}</b><p>开局放：{a["name"]}普通面；以后照常轮转</p></div>'
 s+='</div>'+foot('科技3、7各一次升级；回合末领取，不能强化正在执行的行动。','基础研究可重复：普通S4付24；升级S3付18。')
 return s

def industry():
 s=head('产业协作 · 基础突破','开局随机展示4张J项目，整局不替换；此版图不设置外侧计分轨')
 s+='<div class="project-headnote">普通合作S≥4；升级合作S≥3。完成一个合格空档，得对应科技，推进发布2。<br>每档全桌一人，每人每项目一次；满足条件的图标与牌不消耗。</div><div class="project-grid">'
 for i in range(1,5):
  s+=f'<div class="panel project-slot"><span class="box-label">公共项目 {i:02}</span><h3>基础产业突破</h3><div class="empty">放置一张J项目<small>统计对象与具体门槛见该卡</small></div><div class="tier-slots">'+''.join(f'<div class="tier-slot"><i class="dot"></i>＋{j} 科技<small>门槛见牌面</small></div>' for j in range(1,4))+'</div></div>'
 s+='</div><div class="project-bottom"><div class="panel"><h3>首次完成触发成长A4</h3><p>额外行动升级留到回合末。只完成一档，不可以后补差升级。自己的标记标识玩家，而不是厂家。</p></div><div class="panel"><h3>专项R放在独立扩展区</h3><p>从手牌提出需另付6并立即完成，随后供全桌争档。项目不提供公司类别或厂标，也不属于提出者。</p></div></div>'
 return s+foot('J项目最多4张在场；R专项至多6张在场。每人准备10枚本人项目标记。')

def special():
 s=head('专项项目 · 公共陈列区','R01—R06从主牌取得；只有被玩家通过合作提出后，才放到此处')
 s+='<div class="project-headnote" style="top:157px">提出者先付6现金并立即完成一个合格空档；以后其他玩家完成该项目不再付申报费。</div><div class="special-grid">'
 for i in range(1,7):s+=f'<div class="panel special-slot"><h3>公开专项位置 {i}</h3><div class="empty">放置已提出的R卡<small>门槛与三档奖励完整印在卡上</small></div><p>每档全桌限一人；每人每项目整局一次。<br>项目只提供奖励，不提供厂标或类别。</p></div>'
 s+='</div>'+foot('R01—R05：对应厂标2／4／6，得1／2／3科技。','R06：公司厂家种类3／4／5，得2／3／4科技。')
 return s

def factories():
 s=head('五厂协同 · 标签速查','所有玩家均可积累五个厂系，类别与厂家是相互独立的两套标签')
 s+='<div class="factory-panels">'
 for f in d['factories']:
  vals=[sum(f['id'] in c.get('factoryTags',[]) for c in d['cards'] if c['type']==typ) for typ in ['phone','tech','business']]
  s+=f'<div class="panel factory-panel" style="--factory:{f["color"]}">{symbol(f["id"],82)}<h3>{f["name"]}</h3><p>{f["symbol"]}标志 · {f["id"]}</p><div class="numbers">企划 {vals[0]}　科技 {vals[1]}<br>企业 {vals[2]}</div><p style="font-size:12px;margin-top:18px">各类别与市场交叉分布<br>不是固定玩家阵营</p></div>'
 s+='</div><div class="factory-lower"><div class="panel"><h3>提供厂标的牌</h3><p>只统计公司中已上市企划、已打科技和已打企业的印刷厂标。没有厂标就是不提供，不是通配。</p><p>起始P01—P04没有厂标，所有玩家都从正常牌流进入五厂。</p></div><div class="panel"><h3>需求不是产出</h3><p>门槛栏写“红厂2”，不等于这张卡提供2个红厂图标。R专项、O目标、配件、个人版图不提供厂标。</p><p>科技/企业打出前检查；企划发布前只看此前公开公司。</p></div><div class="panel"><h3>类别依旧独立</h3><p>性能、影像、轻薄、续航、折叠、生态。每个企划类别被本机覆盖加2吸引力，厂标不自动加分。</p><p>公司厂系包含科技与企业；产品厂系只数上市企划。两者不混用。</p></div></div>'
 return s+foot('五厂图形为虚构游戏标识；未对应现实品牌，无商业授权或背书含义。')

def build_boards():
 views=[('central','中央市场',central()),('supply','供应链',supply()),('pricing','定价速查',pricing())]+[(b['id'],b['name'],personal(b)) for b in d['boards']]+[('industry','产业协作',industry()),('special','专项陈列',special()),('factories','五厂标签',factories())]
 nav=''.join(f'<button data-map="{cid}" class="{"selected" if i==0 else ""}">{title}</button>' for i,(cid,title,_) in enumerate(views))
 body=''.join(f'<section class="viewport {"active" if i==0 else ""}" id="{cid}"><div class="map">{content}</div></section>' for i,(cid,title,content) in enumerate(views))
 js="""const vs=[...document.querySelectorAll('.viewport')];function size(){vs.forEach(v=>{const w=v.clientWidth;if(w){v.style.height=(w*960/1480)+'px';v.firstElementChild.style.transform='scale('+(w/1480)+')'}})}document.querySelectorAll('button[data-map]').forEach(b=>b.addEventListener('click',()=>{vs.forEach(v=>v.classList.toggle('active',v.id===b.dataset.map));document.querySelectorAll('button[data-map]').forEach(x=>x.classList.toggle('selected',x===b));size()}));window.addEventListener('resize',size);size();"""
 h=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>旗舰元年5.0 · 线下版图</title><style>{BOARD_CSS}</style></head><body><header><div><h1>旗舰元年</h1><small>5.0 · 静态线下版图</small></div><nav>{nav}</nav><button onclick="window.print()">打印当前版图</button></header><main>{body}</main><p class="screen-note">仅用于线下展示、切换和打印，不记录玩家状态，不进行电子游玩。默认A3横向；卡位为区域示意，实体牌可放邻侧，需足尺寸卡位时可放大至A2。厂标、需求与玩家标记分别辨认。</p><script>{js}</script></body></html>'
 (O/'旗舰元年_5.0_线下版图.html').write_text(h,encoding='utf8')
 (W/'board_manifest.json').write_text(json.dumps([{'id':i,'title':t} for i,t,_ in views],ensure_ascii=False,indent=2),encoding='utf8')
 print('Static boards',len(views))

def build_aids():
 css=(A/'aids.css').read_text()+FACTORY_CSS+'''.price-card table{margin-top:2mm}.price-card td{padding:1mm .4mm}.project-tokens{display:grid;grid-template-columns:repeat(5,26mm);gap:6mm;margin:4mm 0}.project-tokens .token{width:22mm;height:22mm;border-radius:50%}.factory-caption{font-size:10px;line-height:1.8}.mats{margin-top:3mm}.cut-strip{padding:4mm;border:1px dashed #a6b898;background:#eff3e6;margin:5mm 0}.cut-strip p{font-size:11px;line-height:1.8;margin:2mm 0}.factory-strip{margin:3mm 0;padding:3mm 0}.factory-strip small{font-size:8px}.sheet{page-break-after:always}.sheet:last-child{page-break-after:auto}'''
 sheets=[]
 def sheet(body,title,note,pn):
  sheets.append(f'<section class="sheet" id="aid-page-{pn}"><div class="heading"><h1>{title}</h1><p>{note}</p></div>{body}<div class="foot"><span>旗舰元年5.0 · 100%原尺寸 · {"全桌一份" if pn==4 else "每人一套"}</span><span>{pn} / 4</span></div></section>')
 front='<div class="price-grid">'
 for prep in [1,2,3]:
  for p in d['pricing']['strategies']:
   front+=f'<article class="price-card" data-price-id="{prep}-{p["id"]}"><div class="price-top"><span>旗舰元年5.0</span><b>筹备位 {prep}</b></div><h2>{p["name"]}</h2><div class="delta"><span>市场吸引力</span><b>{p["appealDelta"]:+d}</b></div><table><tr><th>名次</th><th>收入</th><th>现金</th></tr>'+''.join(f'<tr><td>{["第一","第二","第三／四"][i]}</td><td>{p["incomeByRank"][i]}</td><td>{p["cashByRank"][i]}</td></tr>' for i in range(3))+'</table><div class="life">每公司每市场仅代表机领奖。<br>企划自身收入及效果另计。<br>锁定后不换价；发布后收回。</div></article>'
 sheet(front+'</div>','实体定价牌 · 正面','第1—2页A4原尺寸，长边翻转双面打印；先试印检查套准。',1)
 back='<div class="price-grid">'
 for prep in [1,2,3]:
  for col in [2,1,0]:back+=f'<article class="price-card price-back" data-price-back="{prep}-{col}"><div class="brand">旗舰元年</div><div class="num">{prep}</div><p>筹备位 · 秘密定价</p><small>5.0</small></article>'
 sheet(back+'</div>','实体定价牌 · 统一背面','同一行三张背面完全相同，只能识别筹备位，不能辨认价格。',2)
 third='<h2 class="aid-h">T19节能调校小垫板</h2><p class="aid-note">选配件调校：标记直接放在本机来源配件。选T19：放下列对应格。没有标记即默认模式。</p><div class="mats">'
 for prep in [1,2,3]:third+=f'<div class="tuning-mat"><h3>筹备位 {prep} · T19</h3><div class="place"></div><small>芯片有效功耗−2<br>市场吸引力−2</small></div>'
 third+='</div><h2 class="aid-h">调校标记（每机最多一枚）</h2><div class="tokens">'+''.join(f'<div class="token"><b>{i}</b><small>调校</small></div>' for i in [1,2,3])+'<span>仅正常组装／返工时选定。<br>发布前选价格不能改调校。<br>结束后收回，下场不继承。</span></div><h2 class="aid-h">轨道越界标记</h2><div class="tile-row"><div class="tile"><b>收入 ＋100</b><p>收入棋子置余数格。<br>结算补回100格。</p></div><div class="tile"><b>科技 ＋36</b><p>科技棋子置余数格。<br>超36部分每点计3分。</p></div><div class="tile"><b>最终发布</b><p>双轨相遇后全员再一回合。<br>追加回合中途不发布。</p></div><div class="tile"><b>最后一轮</b><p>标记在当前玩家处。<br>其下一位起各再一回合。</p></div></div><div class="tech-summary"><b>基础研究不再需要一次性标记</b><br>普通研发S≥4，付24现金得1科技。<br>升级研发S≥3，付18现金得1科技。<br>每次占整个研发行动，每次至多一次；整局可以重复。<br>科技卡减费不适用于基础研究。</div><p class="aid-small">此页单面打印。最终发布／最后一轮各全桌只需一枚，多余可备用。五厂不是玩家颜色，玩家用自己已有棋子或编号区分。</p>'
 sheet(third,'调校、越界与流程标记','本页单面打印；基础研究不使用“已完成”标记。',3)
 fourth='<h2 class="aid-h">公共项目占位 · 四名玩家各10枚</h2><p class="aid-note">按自己的个人版图编号领取对应一行。一个项目只放一枚，颜色与厂家无关；不必手写，也可用已有本人棋子替代。</p>'
 for b in d['boards']:
  fourth+=f'<p class="aid-small" style="margin:2mm 0 1mm"><b>{b["id"]} {b["name"]}</b></p><div style="display:grid;grid-template-columns:repeat(10,18mm);gap:1mm;margin-bottom:2mm">'
  for n in range(10):fourth+=f'<div class="token" data-project-marker="{b["id"]}-{n}" style="width:18mm;height:18mm;border-radius:3mm"><b style="font-size:14px">{b["id"]}</b><small style="font-size:8px">项目占位</small></div>'
  fourth+='</div>'
 fourth+='<h2 class="aid-h">五厂速查 · 不提供可获得厂标</h2>'+factory_strip_html()+'<div class="cut-strip"><p><b>公司厂标</b>：已上市企划＋已打科技＋已打企业。</p><p><b>产品厂系</b>：只看已上市企划；无厂标不是通配。</p><p><b>提出R项目</b>：合作从手牌提出，先付6并立即完成，随后留公共区供全桌争档。</p><p>需求、配件、项目、目标、版图、速查页不提供厂标。</p></div><p class="aid-small">本页全桌印一份即可。正常回款＝20＋当前收入；全桌空发布、最终发布不回款。科技3和7各一次行动升级；科技5且上市2张开第三筹备位。</p>'
 sheet(fourth,'项目标记与五厂速查','此页单面全桌印一份；按M01—M04编号区分玩家，占位不需笔。',4)
 h=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>旗舰元年5.0 · 实体定价与标记</title><style>{css}</style></head><body><header class="tools"><b>旗舰元年5.0 · 定价与调校每人一套</b><button onclick="window.print()">打印组件</button><span style="font-size:11px">第1—2页双面，第3页单面每人印；第4页全桌一份</span></header>'+''.join(sheets)+'</body></html>'
 (O/'旗舰元年_5.0_实体定价与标记.html').write_text(h,encoding='utf8')
 print('Physical aids 4 pages, 9 price fronts +9 backs per player')

if __name__=='__main__':build_boards();build_aids()
