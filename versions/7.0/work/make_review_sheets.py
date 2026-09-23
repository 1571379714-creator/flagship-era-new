"""Render every delivered PDF page; create contact sheets for visual review only."""
from pathlib import Path
import json,math,fitz
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/overviews';OUT.mkdir(parents=True,exist_ok=True)
items=[('全卡牌图鉴','catalog',False),('统一主牌正反面','main_front',True),('线下版图','boards',False),('实体组件','aids',False),('供应商署名与授权组件','suppliers',False),('参考机正反面','references',False),('初始通用配件正反面','starters',False),('扩产组件与速查','expansion',False),('芯片与市场校准表','chips',False),('六部门行动正反面','actions',False)]
rendered={}
for p in sorted((ROOT/'outputs').glob('*.pdf')):
    with fitz.open(p) as doc:
        assert not doc.is_encrypted
        for page in doc: page.get_pixmap(matrix=fitz.Matrix(.6,.6),alpha=False)
        rendered[p.name]={'pages':len(doc),'allPagesRendered':True,'bytes':p.stat().st_size}
for zh,key,front in items:
    with fitz.open(ROOT/f'outputs/旗舰元年_7.0_{zh}.pdf') as doc:
        indices=list(range(0,len(doc),2)) if front else list(range(len(doc)))
        tw,th=(330,470) if key in ('catalog','main_front') else (510,400)
        cols=4 if key in ('catalog','main_front') else 3
        per=20 if key=='catalog' else (16 if key=='main_front' else 12)
        cells=[]
        for index in indices:
            pg=doc[index];scale=min(tw/pg.rect.width,(th-24)/pg.rect.height)
            pix=pg.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
            pic=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            cell=Image.new('RGB',(tw,th),'#dddddd');cell.paste(pic,((tw-pic.width)//2,22))
            ImageDraw.Draw(cell).text((8,4),f'{key} / page {index+1}',fill='black');cells.append(cell)
        for start in range(0,len(cells),per):
            group=cells[start:start+per];sheet=Image.new('RGB',(cols*tw,math.ceil(len(group)/cols)*th),'white')
            for i,cell in enumerate(group):sheet.paste(cell,((i%cols)*tw,(i//cols)*th))
            sheet.save(OUT/f'{key}_{start//per+1}.jpg',quality=90)
        if key=='actions':doc[0].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(OUT/'actions_front.png')
(ROOT/'work/pdf_render_audit_v70.json').write_text(json.dumps(rendered,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'pdfs':len(rendered),'pages':sum(x['pages'] for x in rendered.values()),'files':rendered},ensure_ascii=False,indent=2))
