"""检查实际成品，不执行游戏仿真；不把断言数量解释为平衡程度。"""
from pathlib import Path
import json,re,unicodedata,hashlib
import fitz
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1];O=R/'outputs';W=R/'work'
D=json.loads((W/'v69_data.json').read_text(encoding='utf8'))
allcards=sum([D[k] for k in ('parts','technologies','contracts','facilities','schemes','benchmarks','demands')],[])
C={c['id']:c for c in allcards};checks=[];errors=[]
def ck(b,label):
 checks.append(label)
 if not b:errors.append(label)
def norm(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(s)))
ck(len(C)==len(allcards)==315,'315 unique content designs')
ck(sum(c['qty'] for c in allcards)==315,'315 physical content cards')
ck(sum(c.get('deck')=='main' for c in allcards)==257,'257 main cards')
ck(all(c['qty']==1 for c in allcards),'all current card quantities are one')
# All pages really decoded and converted to raster, with text-boundary checks.
pdfs={};fulltexts={}
for f in sorted(O.glob('*.pdf')):
 with fitz.open(f) as doc:
  texts=[];out=[];glyph=[]
  for i,p in enumerate(doc):
   pix=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
   ck(pix.width>0 and pix.height>0,f'{f.name}: page {i+1} raster')
   text=p.get_text();texts.append(text)
   for block in p.get_text('dict')['blocks']:
    if 'lines' not in block:continue
    for line in block['lines']:
     for s in line['spans']:
      rect=fitz.Rect(s['bbox'])
      if rect.x0 < -1 or rect.y0 < -1 or rect.x1>p.rect.width+1 or rect.y1>p.rect.height+1:out.append({'page':i+1,'text':s['text'],'bbox':s['bbox']})
      if '\ufffd' in s['text']:glyph.append({'page':i+1,'text':s['text']})
  ck(not out,f'{f.name}: no text outside page')
  ck(not glyph,f'{f.name}: no extraction replacement glyph')
  pdfs[f.name]={'pages':len(doc),'bytes':f.stat().st_size,'outOfPage':out,'replacementGlyphs':glyph,'rasterizedPages':len(doc)};fulltexts[f.name]=texts
catf='旗舰元年_6.9_全卡牌图鉴';mainf='旗舰元年_6.9_统一主牌正反面'
cm=json.loads((W/'catalog_manifest.json').read_text());mm=json.loads((W/'main_print_manifest.json').read_text())
cat=BeautifulSoup((O/f'{catf}.html').read_text(encoding='utf8'),'html.parser')
main=BeautifulSoup((O/f'{mainf}.html').read_text(encoding='utf8'),'html.parser')
ck(len(cat.select('article.card'))==315,'HTML catalog all cards present')
ck(len(main.select('article.card'))==257,'HTML main all cards present')
for m in cm['cards']:
 c=C[m['id']];el=cat.find(id=c['id']);ptext=norm(fulltexts[f'{catf}.pdf'][m['page']-1]);etext=norm(el.get_text(' ',strip=True)) if el else ''
 for k in ('name','effect'):
  ck(norm(c[k]) in etext,f'{c["id"]} catalog HTML {k}')
  ck(norm(c[k]) in ptext,f'{c["id"]} catalog PDF assigned page {k}')
 if c['type'] in ('supply','custom','starter'):
  rows=el.select('table tr')[1:]
  ck(len(rows)==len(c['components']),f'{c["id"]} part row count')
  for j,(a,row) in enumerate(zip(c['components'],rows)):
   cells=[x.get_text(' ',strip=True) for x in row.select('td')]
   ck(norm(a['name']) in norm(cells[0]),f'{c["id"]}/{j} chip/part name row')
   ck(cells[1:4]==[str(a['batchCost']),str(a['spec']),('供' if a['kind']=='body' else '耗')+str(a['power'])],f'{c["id"]}/{j} cost spec power row')
   ck(norm(a['name']) in ptext,f'{c["id"]}/{j} PDF part name')
 elif c['type']=='technology':
  for k in ('proof','field'):ck(norm(c[k]) in etext and norm(c[k]) in ptext,f'{c["id"]} {k} rendered')
  if c['jointEligible']:
   rows=[[x.get_text(strip=True) for x in row.select('td')]for row in el.select('.researchmodes tr')[1:]]
   ck(rows==[['联合',str(c['jointCost']),str(c['jointWork'])],['自主',str(c['cost']),str(c['selfWork'])]],f'{c["id"]} both mode rows correct')
   for mode,cost,work in rows:ck(norm(mode+cost+work)in ptext,f'{c["id"]} PDF mode {mode}')
  else:
   ck('仅自主研发' in etext,f'{c["id"]} process self only')
for m in mm['cards']:
 c=C[m['id']];el=main.find(id=f'physical-{c["id"]}-{m["copy"]}');ptext=norm(fulltexts[f'{mainf}.pdf'][m['frontPage']-1]);etext=norm(el.get_text(' ',strip=True))if el else''
 for k in ('name','effect'):
  ck(norm(c[k])in etext,f'{c["id"]} main HTML {k}')
  ck(norm(c[k])in ptext,f'{c["id"]} main PDF front {k}')
 if c['type']=='technology' and c['jointEligible']:
  rows=[[x.get_text(strip=True) for x in row.select('td')]for row in el.select('.researchmodes tr')[1:]]
  ck(rows==[['联合',str(c['jointCost']),str(c['jointWork'])],['自主',str(c['cost']),str(c['selfWork'])]],f'{c["id"]} main mode values')
  for mode,cost,work in rows:ck(norm(mode+cost+work) in ptext,f'{c["id"]} main PDF mode {mode}')
for f in O.glob('*.html'):
 soup=BeautifulSoup(f.read_text(encoding='utf8'),'html.parser')
 for i,el in enumerate(soup.select('.factory')):
  ck(not any(s in el.get_text()for s in ('三角','六角','菱形','三叶','圆环','供货')),f'{f.name} factory badge {i} no shape word')
  if '中立' not in el.get_text():ck(el.find('svg')is not None,f'{f.name} factory badge {i} actual SVG')
# Source originals remain byte-identical to recorded input.
src=json.loads((R/'source/SHA256.json').read_text())
if isinstance(src,dict):
 for name,value in src.items():
  expected=value if isinstance(value,str)else value.get('sha256');fp=R/'source'/name
  ck(fp.exists() and hashlib.sha256(fp.read_bytes()).hexdigest()==expected,f'original source {name} unchanged')
pm=json.loads((W/'supplier_aids_manifest.json').read_text());ck(len(pm['pointers'])==48,'48 pointers total unchanged')
for company in 'ABCD':
 ck(sum(p['company']==company for p in pm['pointers'])==12,f'{company}: 12 pointers')
 for i in range(1,5):ck(sum(p['company']==company and p['product']==i for p in pm['pointers'])==3,f'{company}{i}: 3 pointers')
ck(len(json.loads((W/'component_witnesses_v69.json').read_text())['witnesses'])==160,'160 component configuration witnesses')
# Document renderer output compared to delivered source-PDF text, excluding PDF IDs/timestamps.
for label,stem in [('rulebook_render','完整规则书'),('planning_render','设计规划书')]:
 candidates=list((R/'qa'/label).glob('*.pdf'))
 if candidates:
  with fitz.open(candidates[0]) as doc:
   ck([p.get_text()for p in doc]==fulltexts[f'旗舰元年_6.9_{stem}.pdf'],f'{stem} final PDF equals inspected DOCX-render text')
report={'version':'6.9','checks':len(checks),'passed':len(checks)-len(errors),'errors':errors,'contentDesigns':len(C),'physicalCards':sum(c['qty']for c in allcards),'mainCards':257,'pdfs':pdfs,'totalPdfPages':sum(x['pages']for x in pdfs.values()),'remoteWritten':False,'scope':'字段、份数、页面渲染与边界；不是完整对局或实测平衡。'}
(W/'delivery_audit_v69.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit('Delivery checks failed')
