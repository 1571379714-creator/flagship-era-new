from pathlib import Path
import json,shutil
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];qa=R/'qa';qa.mkdir(exist_ok=True);report={}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
 for f in (R/'outputs').glob('*.html'):
  page=b.new_page(viewport={'width':1700,'height':1300});page.set_content(f.read_text(encoding='utf8'),wait_until='load');page.evaluate('document.fonts.ready');page.emulate_media(media='print');page.evaluate('document.body.classList.add("printall")')
  issues=page.evaluate('''() => {
    let out=[];for(let sel of ['.card','.refcard','.startercard','.sheet','.page','.board','.tile','.report-page']){
      for(let e of document.querySelectorAll(sel)){
       let r=e.getBoundingClientRect();if(!r.height)continue;
       let foot=e.querySelector(':scope > .bottom,:scope > .pagefoot,:scope > .foot,:scope > .legend,:scope > footer');let limit=foot?foot.getBoundingClientRect().top:r.bottom;
       let bad=[...e.children].filter(x=>x!==foot&&!['STYLE','SCRIPT'].includes(x.tagName)).filter(x=>x.getBoundingClientRect().bottom>limit+2).map(x=>({tag:x.tagName,cls:x.className,excess:x.getBoundingClientRect().bottom-limit}));
       if(e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2||bad.length)out.push({sel,id:e.id,header:e.querySelector('h2,h3,.head')?.innerText,dy:e.scrollHeight-e.clientHeight,dx:e.scrollWidth-e.clientWidth,bad});
      }
    }return out;
  }''')
  report[f.name]=issues;print(f.name,len(issues));
  if issues:print(json.dumps(issues,ensure_ascii=False)[:14000])
  if '线下版图' in f.name:
   for i,e in enumerate(page.locator('.board').all()):e.screenshot(path=str(qa/f'board_{i+1}.png'))
  if '全卡牌图鉴' in f.name:
   for id in ['C104','X164','T36','H01','Q24','V15']:page.locator('#'+id).screenshot(path=str(qa/f'card_{id}.png'))
  if '实体组件' in f.name:
   for i in [0,2,3,7,8,9]:page.locator('.sheet').nth(i).screenshot(path=str(qa/f'aids_{i+1}.png'))
  if '参考机正反面' in f.name:page.locator('.sheet').nth(8).screenshot(path=str(qa/'references_last.png'))
  page.close()
 b.close()
(R/'work/layout_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if any(report.values()):raise SystemExit('layout issues need review')
