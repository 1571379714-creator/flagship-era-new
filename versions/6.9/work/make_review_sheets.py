"""生成仅用于人工检查的页面总览；不进入实际卡组。"""
from pathlib import Path
import math
import fitz
from PIL import Image, ImageOps, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/overviews'; OUT.mkdir(parents=True,exist_ok=True)
items=[('全卡牌图鉴','catalog',False),('统一主牌正反面','main_front',True),('线下版图','boards',False),('实体组件','aids',False),('供应商署名与授权组件','suppliers',False),('参考机正反面','reference',False),('50芯片名录与特色','numeric',False)]
for zh,key,front in items:
    with fitz.open(ROOT/f'outputs/旗舰元年_6.9_{zh}.pdf') as doc:
        indices=list(range(0,len(doc),2)) if front else list(range(len(doc)))
        cells=[]
        tw,th=(290,412) if key in ('catalog','main_front') else (460,450)
        cols=4 if key in ('catalog','main_front') else 3
        per=20 if key=='catalog' else (16 if key=='main_front' else 12)
        for index in indices:
            pg=doc[index]; scale=min(tw/pg.rect.width,(th-24)/pg.rect.height)
            pix=pg.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False)
            pic=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            cell=Image.new('RGB',(tw,th),'#dddddd'); cell.paste(pic,((tw-pic.width)//2,22))
            ImageDraw.Draw(cell).text((8,4),f'{key} / page {index+1}',fill='black'); cells.append(cell)
        for start in range(0,len(cells),per):
            group=cells[start:start+per]; sheet=Image.new('RGB',(cols*tw,math.ceil(len(group)/cols)*th),'white')
            for i,cell in enumerate(group):sheet.paste(cell,((i%cols)*tw,(i//cols)*th))
            sheet.save(OUT/f'{key}_{start//per+1}.jpg',quality=88)
        if key=='numeric':
            for i,p in enumerate(doc):
                px=p.get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False); px.save(OUT/f'numeric_page_{i+1}.png')
# Zoom pages carrying changed fields and new display layout.
with fitz.open(ROOT/'outputs/旗舰元年_6.9_统一主牌正反面.pdf') as doc:
    for target in ('T03 /','T09 /','T18 /','T21 /','D111 /','X127 /'):
        for i,p in enumerate(doc):
            if target in p.get_text():
                p.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(OUT/f'zoom_{target.split()[0]}.png'); break
print('Review sheets generated')
