"""5.0排版共享数据与功能厂标，不含电子游玩状态。"""
from pathlib import Path
import json,html,math
R=Path(__file__).resolve().parent.parent;W=R/'work';O=R/'outputs';A=R/'assets';Q=R/'qa'
for p in [O,A,Q]:p.mkdir(exist_ok=True)
d=json.loads((W/'v50_data.json').read_text(encoding='utf-8'))
E=html.escape
ROM=['初始','I','II','III','IV','V'];KINDS={'chip':'芯片','screen':'屏幕','camera':'影像','body':'机身'}
FACT={f['id']:f for f in d['factories']}

def symbol_inner(fid,color=None):
 f=FACT[fid];c=color or f['color'];sh=f['shape']
 if sh=='triangle':s=f'<path d="M32 7 58 54H6Z" fill="{c}"/><path d="m32 24 12 22H20Z" fill="white"/>'
 elif sh=='hexagon':s=f'<path d="M18 7h28l14 25-14 25H18L4 32Z" fill="{c}"/><path d="M24 19h16l8 13-8 13H24l-8-13Z" fill="white"/>'
 elif sh=='diamond':s=f'<path d="M32 3 61 32 32 61 3 32Z" fill="{c}"/><path d="m32 18 14 14-14 14-14-14Z" fill="white"/>'
 elif sh=='clover':s=f'<circle cx="32" cy="20" r="16" fill="{c}"/><circle cx="19" cy="42" r="16" fill="{c}"/><circle cx="45" cy="42" r="16" fill="{c}"/><circle cx="32" cy="34" r="6" fill="white"/>'
 else:s=f'<circle cx="32" cy="32" r="27" fill="{c}"/><circle cx="32" cy="32" r="17" fill="white"/><circle cx="32" cy="32" r="6" fill="{c}"/>'
 return s

def symbol(fid,size=22):
 return f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" aria-label="{FACT[fid]["name"]}厂标" role="img">{symbol_inner(fid)}</svg>'

def badge(fid):
 f=FACT[fid];return f'<span class="factory-badge" style="--factory:{f["color"]}">{symbol(fid,18)}<b>{f["name"]}</b></span>'

def factory_text(arr):return '、'.join(FACT[x]['name'] for x in arr) or '无厂标'
def factory_req(c):return '且'.join(FACT[k]['name']+str(v) for k,v in c.get('factoryRequirements',{}).items()) or '无'
def category_req(c):return '且'.join(k+str(v) for k,v in c.get('tagRequirements',{}).items()) or '无'

def factory_strip_html():return '<div class="factory-strip">'+''.join('<div>'+symbol(f['id'],46)+f'<b>{f["name"]}</b><small>{f["symbol"]}</small></div>' for f in d['factories'])+'</div>'

def create_icons():
 import cairosvg
 for f in d['factories']:
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">{symbol_inner(f["id"])}</svg>'
  (A/f'factory_{f["id"]}.svg').write_text(svg)
  cairosvg.svg2png(bytestring=svg.encode(),write_to=str(A/f'factory_{f["id"]}.png'),output_width=256,output_height=256)
 # Text-free vector strip: labels below are ordinary Word text, not baked font assets.
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="120" viewBox="0 0 1000 120"><rect width="1000" height="120" fill="#f4f5ec"/>'
 for i,f in enumerate(d['factories']):svg+=f'<g transform="translate({72+i*200} 28)">{symbol_inner(f["id"])}</g>'
 svg+='</svg>';(A/'factory_strip.svg').write_text(svg)
 cairosvg.svg2png(bytestring=svg.encode(),write_to=str(A/'factory_strip.png'),output_width=2000,output_height=240)

FACTORY_CSS='''
.factory-badge{display:inline-flex;align-items:center;gap:4px;color:var(--factory);border:1px solid var(--factory);padding:1px 5px;border-radius:4px;white-space:nowrap;font-size:11px;line-height:1.4;vertical-align:middle}.factory-badge svg{flex-shrink:0}.factory-strip{display:flex;justify-content:space-around;align-items:center;padding:6mm 0;border-top:1px solid #c9d4c8;border-bottom:1px solid #c9d4c8;margin:5mm 0}.factory-strip>div{display:flex;flex-direction:column;align-items:center;gap:2mm}.factory-strip b{font-size:14px}.factory-strip small{font-size:9px;color:#7b8578}
'''
