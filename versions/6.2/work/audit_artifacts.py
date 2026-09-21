"""成品可读性与一致性检查；不模拟整局，也不代替视觉和打印机检查。"""
from pathlib import Path
from collections import Counter
import json, re, unicodedata, zipfile, shutil
import fitz
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from sync_rules_text import check as check_rules
R=Path(__file__).resolve().parents[1];O=R/'outputs'
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(s))).replace('\u00ad','')
d=json.loads((R/'work/v62_data.json').read_text(encoding='utf8'))
allcards=sum([d[k] for k in ['parts','technologies','contracts','facilities','schemes','benchmarks','demands']],[])
D={c['id']:c for c in allcards};checks=[]
def check(ok,label):
 checks.append(label)
 if not ok:raise AssertionError(label)
check_rules();check(len(allcards)==243 and sum(c['qty'] for c in allcards)==315,'243 designs /315 copies')
cm=json.loads((R/'work/catalog_manifest.json').read_text());cat=BeautifulSoup((O/'旗舰元年_6.2_全卡牌图鉴.html').read_text(),'html.parser');pdf=fitz.open(O/'旗舰元年_6.2_全卡牌图鉴.pdf');cp=[norm(p.get_text()) for p in pdf]
check(len(cp)==cm['pages'],'catalog page count')
check(len(cat.select('article.card'))==243,'catalog all designs')
for m in cm['cards']:
 c=D[m['id']];el=cat.select_one('#'+c['id']);body=norm(el.get_text());ptext=cp[m['page']-1]
 for s in [c['name'],c['effect']]:
  check(norm(s) in body,c['id']+' HTML full field')
  check(norm(s) in ptext,c['id']+' PDF full field at named page')
 check(c['id'] in ptext,c['id']+' PDF id')
 if c['type'] in ('supply','custom','starter'):
  rows=el.select('table tr')[1:];check(len(rows)==len(c['components']),c['id']+' all component rows')
  for row,a in zip(rows,c['components']):
   vals=[norm(x.get_text()) for x in row.select('td')]
   check(vals[1:4]==list(map(str,[a['batchCost'],a['spec']]))+[('供' if a['kind']=='body' else '耗')+str(a['power'])],c['id']+' exact printed manufacture/spec/power cells')
 elif c['type']=='technology':
  check(norm(c['proof']) in body and norm(c['proof']) in ptext,c['id']+' complete proof')
  nums=[norm(x.get_text()) for x in el.select('.metric b')];check(nums[:3]==list(map(str,[c['cost'],c['work'],c['gain']])),c['id']+' research numeric cells')
 elif c['type']=='contract':
  check(norm(c['requirement']) in body and norm(c['requirement']) in ptext,c['id']+' contract full requirement')
 elif c['type']=='scheme':check(norm(c['requirement']) in body and norm(c['requirement']) in ptext,c['id']+' scheme full requirement')
mp=json.loads((R/'work/main_print_manifest.json').read_text());main=BeautifulSoup((O/'旗舰元年_6.2_统一主牌正反面.html').read_text(),'html.parser');mdoc=fitz.open(O/'旗舰元年_6.2_统一主牌正反面.pdf');mtext=[norm(p.get_text()) for p in mdoc]
check(len(mdoc)==mp['pages']==58,'main 58 double-sided pages')
check(len(main.select('article.card'))==257 and len(main.select('.main-back'))==257,'main 257 fronts and common backs')
check(Counter(m['id'] for m in mp['cards'])==Counter({c['id']:c['qty'] for c in allcards if c.get('deck')=='main'}),'main exact physical duplicates')
check(len({norm(el.get_text()) for el in main.select('.main-back')})==1,'all main backs identical content')
for m in mp['cards']:
 c=D[m['id']];el=main.select_one('#physical-'+m['id']+'-'+str(m['copy']));pt=mtext[m['frontPage']-1]
 check(el is not None and norm(c['effect']) in norm(el.get_text()),m['id']+' compact front complete effect')
 check(norm(c['name']) in pt and norm(c['effect']) in pt,m['id']+' compact PDF complete effect')
sheets=main.select('.sheet')
for i in range(0,len(sheets),2):
 f=list(sheets[i].select_one('.main-grid').children);f=[x for x in f if getattr(x,'name',None)]
 b=list(sheets[i+1].select_one('.main-grid').children);b=[x for x in b if getattr(x,'name',None)]
 check(len(f)==len(b)==9,'main9cells')
 for j in range(9):
  mirror=(j//3)*3+2-j%3
  check(('blank' in f[j].get('class',[]))==('blank' in b[mirror].get('class',[])),'main paired last-page blanks mirrored')
book=json.loads((R/'work/v62_rulebook.json').read_text());ruletext=norm(''.join(p.get_text() for p in fitz.open(O/'旗舰元年_6.2_完整规则书.pdf')))
for s in book['sections']:
 check(norm(s['title']) in ruletext,'rule section '+s['number'])
 for b in s['blocks']:
  for t in [b['title'],b['aside']]:check(norm(t.replace('**','').replace('`','')) in ruletext,'rule block heading/aside '+b['title'])
  for line in b['body'].splitlines():
   if not line.strip():continue
   if line.startswith('|'):
    for cell in line.strip('|').split('|'):
     cell=cell.strip()
     if not re.fullmatch(r'[-: ]+',cell):check(norm(cell.replace('**','')) in ruletext,'rule table cell '+b['title'])
   else:check(norm(line.replace('**','').replace('`','')) in ruletext,'rule complete body '+b['title'])
check('翻已售' not in ruletext and '翻已交付' not in ruletext,'physical state uses movement not missing token face')
for f in O.glob('*.docx'):
 with zipfile.ZipFile(f) as z:check(z.testzip() is None and 'word/document.xml' in z.namelist(),f.name+' docx valid')
pdfs={}
for f in sorted(O.glob('*.pdf')):
 doc=fitz.open(f);outside=[]
 for i,p in enumerate(doc):
  pix=p.get_pixmap(matrix=fitz.Matrix(.25,.25),alpha=False)
  check(pix.width>0 and pix.height>0,f.name+f' page{i+1} decoded')
  for line in p.get_text('blocks'):
   rect=fitz.Rect(line[:4])
   if not (p.rect+(-1,-1,1,1)).contains(rect):outside.append({'page':i+1,'rect':list(rect),'text':line[4][:70]})
 check(not outside,f.name+' no text beyond page bounds')
 pdfs[f.name]={'pages':len(doc),'bytes':f.stat().st_size,'allPagesRendered':True};doc.close()
geom={}
with sync_playwright() as pw:
 br=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox']);p=br.new_page()
 p.set_content((O/'旗舰元年_6.2_统一主牌正反面.html').read_text(),wait_until='load');p.evaluate('document.fonts.ready');p.emulate_media(media='print')
 rects=p.locator('article.card,.main-back').evaluate_all('(els)=>els.map(e=>({w:e.getBoundingClientRect().width*25.4/96,h:e.getBoundingClientRect().height*25.4/96}))')
 check(all(abs(r['w']-63)<.2 and abs(r['h']-88)<.2 for r in rects),'all 514 front/back cards 63x88mm')
 geom={'mainFrontBackRects':len(rects),'mainSizeMm':[63,88]}
 p.set_content((O/'旗舰元年_6.2_实体组件.html').read_text(),wait_until='load');p.evaluate('document.fonts.ready')
 for f,b in [(0,1),(5,6)]:
  aa=p.locator('.sheet').nth(f).locator('.tile');bb=p.locator('.sheet').nth(b).locator('.tile')
  A=aa.evaluate_all('(es)=>es.map(e=>{let a=e.getBoundingClientRect(),s=e.closest(".sheet").getBoundingClientRect();return{x:a.x-s.x,y:a.y-s.y,w:a.width,h:a.height,sw:s.width}})');B=bb.evaluate_all('(es)=>es.map(e=>{let a=e.getBoundingClientRect(),s=e.closest(".sheet").getBoundingClientRect();return{x:a.x-s.x,y:a.y-s.y,w:a.width,h:a.height,sw:s.width}})')
  check(len(A)==len(B),'aid paired count')
  for a in A:check(any(abs(b['y']-a['y'])<1 and abs((a['sw']-a['x']-a['w'])-b['x'])<1 and abs(a['w']-b['w'])<1 and abs(a['h']-b['h'])<1 for b in B),'aid backside long-edge geometric pairing')
 p.set_content((O/'旗舰元年_6.2_参考机正反面.html').read_text(),wait_until='load')
 check(p.locator('.refcard').count()==60,'30 reference fronts /30 era backs')
 for e in range(5):check(len(set(p.locator('.sheet').nth(e*2+1).locator('.refcard').all_text_contents()))==1,'reference backs identical within era')
 br.close()
report={'version':'6.2','contentDesigns':243,'physicalContentCards':315,'mainPhysicalCards':257,'checks':len(checks),'success':True,'pdfs':pdfs,'totalPdfPages':sum(v['pages'] for v in pdfs.values()),'geometry':geom,'limits':['文本和浏览器几何检查不等于所有字形逐一放大审阅。','未作真实打印机正反面对位测试。','不是完整游戏、全部卡牌连锁或策略平衡模拟。']}
(R/'work/artifact_audit_v62.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
