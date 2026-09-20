"""导出与几何核对，仅渲染静态文件；不模拟桌游策略。"""
from v50_common import *
from playwright.sync_api import sync_playwright
import fitz,shutil,os
checks={}
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
 pg=browser.new_page(viewport={'width':1570,'height':1300},device_scale_factor=1)
 for suffix,kind in [('全卡牌图鉴','catalog'),('实体定价与标记','aids')]:
  pg.set_content((O/f'旗舰元年_5.0_{suffix}.html').read_text(encoding='utf8'),wait_until='load');pg.evaluate('document.fonts.ready')
  over=pg.evaluate('''()=>[...document.querySelectorAll('.sheet,.card,.price-card')].map(x=>({id:x.id||x.dataset.cardId||x.dataset.actionId||x.dataset.priceId,cls:x.className,ch:x.clientHeight,sh:x.scrollHeight,cw:x.clientWidth,sw:x.scrollWidth})).filter(x=>x.sh>x.ch+1||x.sw>x.cw+1)''')
  collisions=pg.evaluate('''()=>[...document.querySelectorAll('.card')].flatMap(el=>{let a=el.querySelector('.effect'),b=el.querySelector('.life');if(!a||!b)return [];const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();return x.bottom>y.top+1?[{id:el.dataset.cardId||el.dataset.actionId,bottom:x.bottom,foot:y.top}]:[]})''')
  checks[kind]={'pages':pg.locator('.sheet').count(),'cards':pg.locator('[data-card-id]').count(),'actionFaces':pg.locator('[data-action-id]').count(),'priceFaces':pg.locator('[data-price-id]').count(),'priceBacks':pg.locator('[data-price-back]').count(),'overflow':over,'effectFooterCollisions':collisions}
  pg.pdf(path=str(O/f'旗舰元年_5.0_{suffix}.pdf'),prefer_css_page_size=True,print_background=True)
  if kind=='catalog':
   for sel in ['#catalog-cover','#catalog-index','#cat-phone','#cat-tech','#cat-specialProject','#cat-factory','#cat-track']:
    pg.locator(sel).screenshot(path=str(Q/(sel[1:]+'.png')))
   # Record actual complete text per card for later field comparison.
   checks['catalogText']=pg.locator('[data-card-id]').evaluate_all('(xs)=>xs.map(x=>({id:x.dataset.cardId,text:x.innerText}))')
  else:
   for n in range(1,5):pg.locator(f'#aid-page-{n}').screenshot(path=str(Q/f'aid-page-{n}.png'))
   front=pg.locator('[data-price-id]').evaluate_all('(xs)=>xs.map(x=>({id:x.dataset.priceId,x:x.getBoundingClientRect().x,y:x.getBoundingClientRect().y,w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height}))')
   back=pg.locator('[data-price-back]').evaluate_all('(xs)=>xs.map(x=>({id:x.dataset.priceBack,x:x.getBoundingClientRect().x,y:x.getBoundingClientRect().y,w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height}))')
   checks['aidGeometry']={'front':front,'back':back}
 pg.set_content((O/'旗舰元年_5.0_线下版图.html').read_text(encoding='utf8'),wait_until='load');pg.evaluate('document.fonts.ready');pg.wait_for_timeout(100)
 boards=json.loads((W/'board_manifest.json').read_text());out=fitz.open();checks['boards']=[]
 for entry in boards:
  mid=entry['id'];pg.locator(f'button[data-map="{mid}"]').click();pg.wait_for_timeout(60)
  pg.locator(f'#{mid}').screenshot(path=str(Q/f'board_{mid}.png'))
  bounds=pg.locator(f'#{mid} .map').evaluate('''x=>({w:x.clientWidth,h:x.clientHeight,sw:x.scrollWidth,sh:x.scrollHeight})''')
  checks['boards'].append({'id':mid,**bounds})
  single=Q/f'board_{mid}.pdf';pg.pdf(path=str(single),prefer_css_page_size=True,print_background=True)
  with fitz.open(single) as p:out.insert_pdf(p)
 out.save(O/'旗舰元年_5.0_线下版图.pdf');out.close()
 checks['rails']=pg.evaluate('''()=>({income:[...document.querySelectorAll('[data-income]')].map(x=>+x.dataset.income),technology:[...document.querySelectorAll('[data-tech]')].map(x=>({tech:+x.dataset.tech,align:+x.dataset.incomeAlign})),release:[...document.querySelectorAll('[data-release]')].map(x=>+x.dataset.release),supplySlots:document.querySelectorAll('[data-supply-slot]').length})''')
 browser.close()
(W/'layout_checks_v50.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in checks.items() if k not in ['catalogText','aidGeometry','rails']},ensure_ascii=False,indent=2))
render=Q/'rulebook_render/旗舰元年_5.0_完整规则书.pdf'
if render.exists():shutil.copyfile(render,O/render.name)
