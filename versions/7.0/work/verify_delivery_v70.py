"""Verify original bytes, every card's printed effect, print counts and actual PDF pages."""
from pathlib import Path
import json,re,hashlib,unicodedata,collections,fitz
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1];W=R/'work';O=R/'outputs';issues=[]
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(s)))
def check(ok,msg):
 if not ok:issues.append(msg)
d=json.loads((W/'v70_data.json').read_text());cards=sum((d[k] for k in ['parts','technologies','contracts','facilities','schemes','benchmarks','demands']),[]);byid={c['id']:c for c in cards};main=[c for c in cards if c.get('deck')=='main']
check(len(cards)==315 and len(byid)==315,'315 unique content designs');check(len(main)==257,'257 main')
chips=[p for c in d['parts'] if c['type']!='starter' for p in c['components'] if p['kind']=='chip'];check(len(chips)==50 and len({p['name'] for p in chips})==50,'50 unique chips')
orig=json.loads((R/'source/SHA256.json').read_text());sourceOK={n:hashlib.sha256((R/'source'/n).read_bytes()).hexdigest()==h for n,h in orig.items()};check(all(sourceOK.values()),'source hash changed')
catSoup=BeautifulSoup((O/'旗舰元年_7.0_全卡牌图鉴.html').read_text(),'html.parser');mainSoup=BeautifulSoup((O/'旗舰元年_7.0_统一主牌正反面.html').read_text(),'html.parser')
check(len(catSoup.select('article.card'))==315,'catalog DOM count');check(len(mainSoup.select('article.card'))==257,'main DOM count')
for c in cards:
 el=catSoup.find(id=c['id']);check(el is not None,f'catalog missing {c["id"]}')
 if el:
  txt=norm(el.get_text());check(norm(c['name']) in txt,f'catalog name {c["id"]}');check(norm(c['effect']) in txt,f'catalog full effect {c["id"]}')
for c in main:
 el=mainSoup.find(id='physical-'+c['id']+'-1');check(el is not None,f'main missing {c["id"]}')
 if el:check(norm(c['effect']) in norm(el.get_text()),f'main full effect {c["id"]}')
cm=json.loads((W/'catalog_manifest.json').read_text())['cards'];mm=json.loads((W/'main_print_manifest.json').read_text())['cards']
for suffix,manifest in [('全卡牌图鉴',cm),('统一主牌正反面',mm)]:
 with fitz.open(O/f'旗舰元年_7.0_{suffix}.pdf') as pdf:
  pages=[norm(p.get_text()) for p in pdf]
  for row in manifest:
   c=byid[row['id']];idx=row.get('page',row.get('frontPage'))-1
   check(norm(c['id']) in pages[idx],f'{suffix} ID PDF {c["id"]}')
   check(norm(c['name']) in pages[idx],f'{suffix} name PDF {c["id"]}')
   check(norm(c['effect']) in pages[idx],f'{suffix} effect PDF {c["id"]}')
# PDF binary opening/rasterization is independent of browser DOM.
pdfs={}
for path in sorted(O.glob('*.pdf')):
 with fitz.open(path) as doc:
  check(len(doc)>0 and not doc.is_encrypted,'empty/encrypted '+path.name)
  for p in doc:p.get_pixmap(matrix=fitz.Matrix(.35,.35),alpha=False)
  pdfs[path.name]={'pages':len(doc),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'allPagesRendered':True}
# Check figures + documents match their last canonical DOCX renders text.
canonical={}
for suffix,folder in [('完整规则书','rulebook_render'),('设计规划书','planning_render')]:
 paths=list((R/'qa'/folder).glob('*.pdf'))
 if paths:
  with fitz.open(paths[0]) as prev,fitz.open(O/f'旗舰元年_7.0_{suffix}.pdf') as now:
   same=len(prev)==len(now) and all(norm(a.get_text())==norm(b.get_text()) for a,b in zip(prev,now));canonical[suffix]=same;check(same,'Canonical render text mismatch '+suffix)
check(len(BeautifulSoup((O/'旗舰元年_7.0_六部门行动正反面.html').read_text(),'html.parser').select('.actioncard'))==12,'6 action fronts+6backs')
layout=json.loads((W/'layout_audit.json').read_text());layoutIssues=sum(len(v.get('issues',[])) if isinstance(v,dict) else len(v) for v in layout.values());check(layoutIssues==0,'DOM layout issues')
report={'version':'7.0','contentCards':len(cards),'mainCards':len(main),'chipNames':len(chips),'pdfs':pdfs,'pdfCount':len(pdfs),'pdfPages':sum(p['pages'] for p in pdfs.values()),'sourceUnchanged':sourceOK,'canonicalDOCXTextMatches':canonical,'fullCardEffectsChecked':{'catalog':315,'main':257},'layoutIssues':layoutIssues,'issues':issues,'notVerified':['full multiplayer games','full generic interpreter for all H/U/Q effects','physical printer registration','commercial bleed/die cutting']}
(W/'delivery_audit_v70.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='pdfs'},ensure_ascii=False,indent=2))
if issues:raise SystemExit(1)
