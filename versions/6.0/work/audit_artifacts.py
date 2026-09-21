from pathlib import Path
import fitz,json,re,hashlib,os,shutil
from playwright.sync_api import sync_playwright
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).resolve().parents[1];O=R/'outputs';Q=R/'qa';Q.mkdir(exist_ok=True)
d=json.loads((R/'work/v60_data.json').read_text());manifest=json.loads((R/'work/catalog_manifest.json').read_text())
checks=0;errors=[];report={'pdfs':{},'html':{}}
def ck(x,msg):
 global checks
 checks+=1
 if not x:errors.append(msg)
def compact(t):return re.sub(r'\s+','',t)
for p in O.glob('*.pdf'):
 doc=fitz.open(p);texts=[]
 for i,page in enumerate(doc):
  txt=page.get_text();texts.append(txt);ck(len(txt.strip())>20,f'blank {p.name} {i+1}')
  pix=page.get_pixmap(matrix=fitz.Matrix(.35,.35));ck(pix.width>0,f'render {p.name} {i+1}')
  for b in page.get_text('blocks'):
   if b[6]==0:ck(b[0]>=-1 and b[1]>=-1 and b[2]<=page.rect.width+1 and b[3]<=page.rect.height+1,f'offpage {p.name} {i+1}')
 report['pdfs'][p.name]={'pages':len(doc),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decodedEveryPage':True}
 if '全卡牌' in p.name:
  byid={c['id']:c for g in ['parts','technologies','contracts','facilities','schemes','benchmarks','demands'] for c in d[g]}
  ck(len(doc)==manifest['pages'],'catalog page total')
  for c in manifest['cards']:
   txt=compact(texts[c['page']-1]);s=byid[c['id']]
   ck(compact(c['name']) in txt,f'card name {c["id"]}')
   ck(compact(s['effect']) in txt,f'card effect {c["id"]}')
   ck(c['id'] in txt,f'card id {c["id"]}')
  # 所有卡片的数据字段以HTML自动生成，另外核对DOM文本与JSON。
with sync_playwright() as pw:
 options={'headless':True,'args':['--no-sandbox']}
 chrome=os.environ.get('FLAGSHIP_CHROMIUM') or shutil.which('chromium') or shutil.which('chromium-browser')
 if chrome:options['executable_path']=chrome
 b=pw.chromium.launch(**options)
 p=b.new_page(viewport={'width':1600,'height':1200},device_scale_factor=1)
 for fn in ['旗舰元年_6.0_全卡牌图鉴.html','旗舰元年_6.0_线下版图.html','旗舰元年_6.0_实体组件.html']:
  p.set_content((O/fn).read_text(),wait_until='load');p.evaluate('document.fonts.ready')
  if '全卡牌' in fn:
   results=p.evaluate('''() => [...document.querySelectorAll('.card')].map(c=>{const r=c.getBoundingClientRect(),f=c.querySelector('.bottom').getBoundingClientRect();const kids=[...c.children].filter(x=>!x.classList.contains('bottom'));return {id:c.id,h:c.scrollHeight-clientSafe(c),last:Math.max(...kids.map(e=>e.getBoundingClientRect().bottom)),limit:f.top,scroll:c.scrollHeight,client:c.clientHeight};function clientSafe(x){return x.clientHeight}})''')
   for x in results:ck(x['last']<=x['limit']+1,f'card footer overlap {x["id"]} {x["last"]-x["limit"]}');ck(x['h']<=2,f'card overflow {x["id"]}')
   report['html']['catalogCards']=len(results)
   for id in ['T18','H08','Q24','V26','X32']:
    p.locator('#'+id).screenshot(path=str(Q/f'card_{id}.png'))
  elif '线下版图' in fn:
   results=[]
   for loc in p.locator('.board').all():
    id=loc.get_attribute('id')
    p.evaluate("id=>document.querySelectorAll('.board').forEach(x=>x.classList.toggle('active',x.id===id))",id)
    x=loc.evaluate('''c=>{let f=c.querySelector('.legend').getBoundingClientRect();let kids=[...c.children].filter(x=>!x.classList.contains('legend'));return {id:c.id,last:Math.max(...kids.map(e=>e.getBoundingClientRect().bottom)),limit:f.top,overflow:c.scrollHeight-c.clientHeight}}''')
    results.append(x);ck(x['last']<=x['limit']+1,f'board footer overlap {id} {x["last"]-x["limit"]}');ck(x['overflow']<=2,f'board clipped {id}')
    loc.screenshot(path=str(Q/f'board_{id}.png'))
   report['html']['boards']=results
  else:
   result=[]
   for i,loc in enumerate(p.locator('.sheet').all(),1):
    x=loc.evaluate('''c=>{let f=c.querySelector('.foot').getBoundingClientRect();let kids=[...c.children].filter(x=>!x.classList.contains('foot'));return {last:Math.max(...kids.map(e=>e.getBoundingClientRect().bottom)),limit:f.top,overflow:c.scrollHeight-c.clientHeight}}''')
    result.append(x);ck(x['last']<=x['limit']+1,f'aid footer {i} {x["last"]-x["limit"]}');ck(x['overflow']<=2,f'aid clipped {i}')
    loc.screenshot(path=str(Q/f'aid_{i}.png'))
   # 双面背面是相同的型号行；验证镜像位置与尺寸。
   fronts=p.locator('.sheet').nth(0).locator('.price').evaluate_all('(els)=>els.map(e=>{let a=e.getBoundingClientRect();let s=e.closest(".sheet").getBoundingClientRect();return {model:e.querySelector(".n").textContent,x:a.x-s.x,y:a.y-s.y,w:a.width,h:a.height}})')
   backs=p.locator('.sheet').nth(1).locator('.price').evaluate_all('(els)=>els.map(e=>{let a=e.getBoundingClientRect();let s=e.closest(".sheet").getBoundingClientRect();return {model:e.querySelector(".v").textContent,x:a.x-s.x,y:a.y-s.y,w:a.width,h:a.height}})')
   sw=p.locator(".sheet").nth(0).evaluate("e=>e.getBoundingClientRect().width")
   mirror_errors=[]
   for i,f in enumerate(fronts):
    bb=backs[(i//4)*4+3-i%4];model=i//4+1
    ck(bb['model']==str(model),'duplex no price reveal')
    ck(abs(f['y']-bb['y'])<.1 and abs(f['w']-bb['w'])<.1 and abs(f['h']-bb['h'])<.1,'duplex same size')
    err=abs(f['x']+bb['x']+bb['w']-sw);mirror_errors.append(err)
    ck(err<.2,f'duplex mirror x {i}: {err}')
   report['html']['priceDuplexMaxMirrorErrorMM']=max(mirror_errors)*25.4/96
   report['html']['aids']=result
 b.close()
report['checks']=checks;report['errors']=errors;report['passed']=not errors
(R/'work/artifact_checks_v60.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
