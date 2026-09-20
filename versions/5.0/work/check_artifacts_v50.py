"""成品内容、分页与实体几何核对。不是多人对局模拟。"""
from v50_common import *
from bs4 import BeautifulSoup
from collections import Counter
import fitz,re,unicodedata,hashlib
checks=[]; fail=[]
def ck(ok,msg):
 (checks if ok else fail).append(msg)
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(s))).replace('／','/').replace('—','-').replace('–','-')
cat=BeautifulSoup((O/'旗舰元年_5.0_全卡牌图鉴.html').read_text(encoding='utf8'),'html.parser')
manifest=json.loads((W/'catalog_manifest.json').read_text())
layout=json.loads((W/'layout_checks_v50.json').read_text())
allc={c['id']:c for g in ['cards','parts','starters','projects','specialProjects','goals'] for c in d[g]}
ck(len(cat.select('[data-card-id]'))==len(allc)==302,'HTML 302种卡面恰好一次')
cpdf=fitz.open(O/'旗舰元年_5.0_全卡牌图鉴.pdf')
for ent in manifest['cards']:
 cid=ent['id'];c=allc[cid];el=cat.select_one(f'[data-card-id="{cid}"]');txt=norm(el.get_text());pdftext=norm(cpdf[ent['page']-1].get_text())
 ck(norm(c['name']) in txt and norm(c['name']) in pdftext,cid+'：卡名在HTML与索引指定PDF页')
 ck(norm(c['effect']) in txt and norm(c['effect']) in pdftext,cid+'：完整效果在HTML与指定PDF页')
 ck(f'{c.get("qty",1)}张' in norm(el.select_one('.card-top').get_text()),cid+'：实体份数')
 typ=ent['type']
 if typ in ['phone','tech','business']:
  badges=el.select('.factory-badge b');ck([v.get_text() for v in badges]==[FACT[x]['name'] for x in c['factoryTags']],cid+'：产出厂标')
  ck([v.get_text() for v in el.select('.tagsline .tag')]==c['tags'],cid+'：产出类别独立')
  expected=[c['strength'],c['tech']]+([c['development'],c['appeal'],c['income']] if typ=='phone' else [c['cost'],c['gain']] if typ=='tech' else [c['cost']])
  actual=[int(x.get_text()) for x in el.select('.metric b')];ck(actual==expected,cid+'：全部基础数值逐栏')
  gate=norm(el.select_one('.gate').get_text());ck(norm(factory_req(c)) in gate,cid+'：厂家需求独立显示')
  if typ=='phone':ck(norm(category_req(c)) in gate and c['market'] in txt,cid+'：类别门槛与市场')
  if typ=='tech':ck((f'至少{c["priorTechCardsRequired"]}张' in gate) if c['priorTechCardsRequired'] else ('无额外科技卡张数前置' in gate),cid+'：已有科技卡前置')
 elif typ in ['common','custom','starter']:
  rows=el.select('.parttable tbody tr');ck(len(rows)==len(c['components']),cid+'：整合部件行数')
  for n,(row,p) in enumerate(zip(rows,c['components'])):
   cols=[norm(x.get_text()) for x in row.select('td')]
   expected=[str(p['cost']),str(p['appeal']),('供' if p['kind']=='body' else '耗')+str(p['load']),str(p['tech']),p['tag']]
   ck(cols[1:]==expected,cid+f'：部件{n+1}制造/吸引力/功供/科技/类别')
   ck(('折叠' in cols[0])==(p['form']=='fold'),cid+f'：部件{n+1}形态')
  if typ!='starter':ck(f'{ROM[c["era"]]}代' in txt,cid+'：供应世代')
 elif typ in ['project','specialProject']:
  ck([int(v.get_text()) for v in el.select('.tier b')]==c['thresholds'],cid+'：项目全部门槛')
  ck([norm(v.get_text()) for v in el.select('.tier span')]==[f'取得{v}科技' for v in c['rewards']],cid+'：项目全部奖励')
  ck(c['label'] in txt,cid+'：统计对象')
 else:ck('6分上限' in txt,cid+'：终局上限与时点')
cpdf.close()
for a in d['actions']:
 for face in ['front','back']:
  el=cat.select_one(f'[data-action-id="{a["id"]}-{face}"]');ck(el is not None and norm(a[face])==norm(el.select_one('.effect').get_text()),a['id']+' '+face+'：完整行动正文')
# Complete PDFs: page sizes, empty pages, off-page text and missing glyph replacement marks.
pdfchecks={}
for name,expected in [('完整规则书',19),('全卡牌图鉴',59),('实体定价与标记',4),('线下版图',10)]:
 doc=fitz.open(O/f'旗舰元年_5.0_{name}.pdf');empty=[];outside=[];replacement=[];pages=[]
 ck(len(doc)==expected,name+'：实际PDF页数')
 for i,p in enumerate(doc):
  text=p.get_text();pages.append({'page':i+1,'textCharacters':len(text),'widthPt':p.rect.width,'heightPt':p.rect.height})
  if not text.strip():empty.append(i+1)
  if '\ufffd' in text:replacement.append(i+1)
  for b in p.get_text('dict')['blocks']:
   if b['type']!=0:continue
   for line in b['lines']:
    for sp in line['spans']:
     if not sp['text'].strip():continue
     x0,y0,x1,y1=sp['bbox']
     if x0<-1 or y0<-1 or x1>p.rect.width+1 or y1>p.rect.height+1:outside.append({'page':i+1,'text':sp['text'],'bbox':sp['bbox']})
 ck(not empty,name+'：无空白页');ck(not outside,name+'：无页外文字');ck(not replacement,name+'：无Unicode替代字')
 pdfchecks[name]={'pages':len(doc),'empty':empty,'offPageText':outside,'replacementCharacterPages':replacement,'pageStats':pages};doc.close()
# Visual meeting rule intact, not weighted formula.
rd=fitz.open(O/'旗舰元年_5.0_完整规则书.pdf');rules=norm(''.join(p.get_text() for p in rd));rd.close()
approved='当任意玩家的两个标记相遇或越过，完成当前回合的全部结算后，所有玩家各再进行一个回合，随后举行最终发布并计分。秘密终局目标只在最终计分时加入，不会提前触发游戏结束。'
ck(norm(approved) in rules,'规则书完整保留批准的终局段落')
ck('5×科技' not in rules and '5*科技' not in rules and 'G(T)' not in rules,'无旧固定五倍科技判定')
ck('0-36' in rules and '8到9是第一个跨度为3' in rules,'规则书36格与8→9长步边界')
rails=layout['rails'];ck(rails['income']==list(range(101)),'版图收入101个位置');ck(rails['release']==list(range(15)),'发布0至14共15格')
ck(rails['technology']==[{'tech':i,'align':v} for i,v in enumerate(d['scoreTrack']['alignment'])],'37个科技位置与对齐表逐项一致')
ck(rails['supplySlots']==16,'四类稳定供应最多16位置')
ck(not layout['catalog']['overflow'] and not layout['catalog']['effectFooterCollisions'],'图鉴容器无溢出、效果不压页脚')
ck(not layout['aids']['overflow'] and not layout['aids']['effectFooterCollisions'],'实体组件容器无溢出')
ck(len(layout['boards'])==10 and all(b['w']==b['sw'] and b['h']==b['sh'] for b in layout['boards']),'10个线下版图根容器无溢出')
# Back/front geometry: mirrors within A4 sheet, prep numbering retained.
aids=BeautifulSoup((O/'旗舰元年_5.0_实体定价与标记.html').read_text(encoding='utf8'),'html.parser')
ck(len(aids.select('[data-price-id]'))==9 and len(aids.select('[data-price-back]'))==9,'实体9定价正面与9背面')
geo=layout['aidGeometry'];f=geo['front'];b=geo['back'];
xs=sorted(set(round(x['x'],3) for x in f));ys=sorted(set(round(x['y'],3) for x in f));ysb=sorted(set(round(x['y'],3) for x in b));
err=[]
for z in f:
 row=min(range(3),key=lambda i:abs(z['y']-ys[i]));col=min(range(3),key=lambda i:abs(z['x']-xs[i]));
 other=min(b,key=lambda q:abs(q['y']-ysb[row])+abs(q['x']-xs[2-col]));
 err.extend([abs(z['w']-other['w']),abs(z['h']-other['h']),abs((z['x']+other['x']+z['w'])-(xs[0]+xs[-1]+z['w']))])
maxerrmm=max(err)*25.4/96
ck(maxerrmm<.1,'定价正背长边翻转镜像几何误差小于0.1mm（非实机套准）')
backrows=[]
for n in range(3):
 rr=[x for x in b if abs(x['y']-ysb[n])<1]
 texts=[norm(aids.select_one(f'[data-price-back="{x["id"]}"]').get_text()) for x in rr]
 ck(len(set(texts))==1,f'筹备位{n+1}三张卡背文字完全一致')
 backrows.append(texts)
# Derived counts, not a claim based solely on stored summary numbers.
initial=sum(c.get('qty',1) for c in d['cards'] if c['id'] not in ['P01','P02','P03','P04'])+sum(c.get('qty',1) for c in d['specialProjects'])+sum(c['qty'] for c in d['parts'] if c['type']=='custom' and c['era']==1)
eventual=sum(c.get('qty',1) for c in d['cards'] if c['id'] not in ['P01','P02','P03','P04'])+sum(c.get('qty',1) for c in d['specialProjects'])+sum(c['qty'] for c in d['parts'] if c['type']=='custom')
ck(initial==204 and eventual==244,'实际逐牌推导开局204／累计244主牌')
# Static only: no persistent game states or network-backed play.
for suffix in ['全卡牌图鉴','实体定价与标记','线下版图']:
 text=(O/f'旗舰元年_5.0_{suffix}.html').read_text(encoding='utf8')
 ck(not any(x in text for x in ['localStorage','sessionStorage','fetch(','WebSocket','XMLHttpRequest']),suffix+'：无存档／网络电子游玩代码')
report={'version':'5.0','passed':not fail,'checksPassed':len(checks),'failures':fail,'checks':checks,'pdf':pdfchecks,'duplexMirrorMaxErrorMm':maxerrmm,'derivedMainDeck':{'initial':initial,'eventual':eventual},'note':'文字、字段、分页、静态排版与几何检查，不是实际打印设备套准或多人平衡验证。'}
(W/'artifact_checks_v50.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['checks','pdf']},ensure_ascii=False,indent=2))
if fail:raise SystemExit(1)
