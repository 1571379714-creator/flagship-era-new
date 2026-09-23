"""Build delivery verification and package actual files. Does not edit cards or push GitHub."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
import fitz

ROOT = Path(__file__).resolve().parents[1]
W, O, Q = ROOT/'work', ROOT/'outputs', ROOT/'qa'

def load(name: str):
    return json.loads((W/name).read_text(encoding='utf-8'))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    tests = load('test_results_v69.json')
    audit = load('delivery_audit_v69.json')
    rebuild = load('rebuild_audit_v69.json')
    components = load('component_witnesses_v69.json')
    chips = load('chip_route_witnesses_v69.json')
    layout = load('layout_audit.json')
    assert tests['success'] and tests['failures'] == tests['errors'] == 0
    assert not audit['errors'] and not rebuild['errors']
    assert audit['contentDesigns'] == audit['physicalCards'] == 315
    assert audit['mainCards'] == 257
    assert len(components['witnesses']) == 160 and len(chips['witnesses']) == 50
    # These rendered pages were opened and visually reviewed; images remain QA-only.
    reviewed = []
    for folder, count in [('rulebook_render',26),('planning_render',2)]:
        for n in range(1,count+1):
            path=Q/folder/f'page-{n}.png'
            assert path.stat().st_size > 0
            reviewed.append({'name':path.relative_to(ROOT).as_posix(), 'sha256':digest(path)})
    for name in ('catalog_1.jpg','catalog_2.jpg','catalog_3.jpg','catalog_4.jpg',
                 'main_front_1.jpg','main_front_2.jpg','boards_1.jpg','aids_1.jpg',
                 'suppliers_1.jpg','reference_1.jpg'):
        path=Q/'overviews'/name
        assert path.stat().st_size > 0
        reviewed.append({'name':path.relative_to(ROOT).as_posix(),'sha256':digest(path)})
    for n in range(1,10):
        path=Q/'overviews'/f'numeric_page_{n}.png'
        reviewed.append({'name':path.relative_to(ROOT).as_posix(),'sha256':digest(path)})
    for code in ('C112','X102','X113','X123','X138','X151','X160'):
        path=Q/f'main_{code}.png'
        reviewed.append({'name':path.relative_to(ROOT).as_posix(),'sha256':digest(path)})
    (W/'visual_review_v69.json').write_text(json.dumps({
        'version':'6.9','rulebookAll26PagesOpened':True,'planningAll2PagesOpened':True,
        'catalogAndMain':'All page contact sheets inspected; selected cards also enlarged.',
        'reviewedImageHashes':reviewed,'imagesIncludedInPackage':False,
        'scope':'Layout review, not physical printer registration or proof of game balance.'
    },ensure_ascii=False,indent=2),encoding='utf-8')
    lines=[
        '# 旗舰元年6.9 · 实际交付核对', '',
        '以实际6.8文件为输入，当前数据和全部输出位于本包；原6.8不覆盖，本轮没有读写GitHub远端。', '',
        '## 内容与文件',
        '50个主牌芯片位置、50个不同名称：20稳定＋30含芯片定制；每代4＋6。指定40款及补充10款均已核对。',
        '全套315种／315张内容牌，主牌257；初始16、参考30、需求12另备。每张主牌一份，不加重复副本。', '',
        '|实际PDF|页数|字节数|', '|---|---:|---:|',
    ]
    for name,v in audit['pdfs'].items():
        lines.append(f"|{name}|{v['pages']}|{v['bytes']}|")
    lines += [
        '', f"共{len(audit['pdfs'])}个PDF、{audit['totalPdfPages']}页，全部实际打开并转为像素；未检出文本越页面边界或替换字形。",
        '完整规则DOCX及规划DOCX均经LibreOffice渲染，分别打开26页和2页PNG检查；对应PDF文字与交付PDF一致。图鉴与主牌检查全页总览及重点放大，芯片名录9页逐页查看。', '',
        '## 数据与规则检查',
        f"本轮单元测试{tests['testsRun']}项通过：{tests['inheritedTests']}项继承回归＋{tests['newRosterAndAbilityTests']}项新名单／特色测试。",
        '继承测试包含600个单市场与1200个四市场扩产情境；不是1800局完整游戏。部分设施/合同在测试中由夹具表示，不等于全部前置已穷举。',
        '继承适配明确两处：输入快照变为6.8；加入T760后同代稳定规格差检查允许4而非3。后者不是玩家规则，也没有为通过断言抬高T760性能。',
        f"部件可组装检查：{len(components['witnesses'])}个部件记录了见证，搜索{components['searchAttempts']}个候选配置。",
        f"芯片能力检查：{chips['chipsChecked']}个芯片均找到使用真实卡牌并能发挥其特性的合法配置，共尝试{chips['attemptedConfigurations']}种配置。",
        '配置见证假定玩家已取得那些牌、完成所列自主技术且现金和工作足够；没有证明完整抽牌路径、盈利或多人胜率。',
        f"成品字段与渲染核对{audit['checks']}条均通过，仅为检查条目，不是对局次数或平衡评分。",
        'JSON、卡面HTML、图鉴指定PDF页与主牌指定正面页核对名称、完整效果和参数；厂标无“供货”及形状文字前缀，芯片/影像无“直板”显示。', '',
        '## 独立重建',
        f"在不含排版缓存的独立空目录复制现行数据与脚本，实际执行build_all.py。核对{len(rebuild['files'])}个HTML/PDF：HTML字节相同，PDF页数及每页文字相同。",
        '不声称PDF二进制逐字节相同（生成时间与文档ID可不同），也不将重建当成真人试玩。', '',
        '## 现实资料和打印边界',
        '21个芯片位置有本轮读取的第一方资料，29个沿用历史归档，不能称50款本轮全部横测。T760首发档案、麒麟9050无后缀版本及8EE6/O3分别注明局限。',
        '苹果完整名称为A11—A16 Bionic、A17—A20 Pro；方案和参数是游戏抽象，不宣称真实折叠苹果、自由裸片销售或真实授权关系。',
        '未完成多人实测、全卡联动穷举、真实硬件统一横测或打印机正反套准。卡片为实测制卡文件，未完成商业出血、刀模和色彩打样。', '',
        '## 包内追溯',
        'source/SHA256.json保存6.8输入摘要，SHA256.json保存本包文件摘要（不包含清单自身）。先解压再运行work/check_package_integrity.py可查每个文件。',
        '正常重建只运行work/build_all.py；revise_v69.py是历史迁移脚本，会覆盖手改数据，不是普通构建步骤。'
    ]
    (O/'旗舰元年_6.9_交付核对记录.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Content-only deliverables; no rendered QA images, caches, external fonts or credentials.
    entries=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if any(s in {'__pycache__','.git'} for s in rel.parts):continue
        if rel.parts[0]=='qa' and p.suffix not in {'.log','.json','.md'}:continue
        if rel.as_posix()=='SHA256.json':continue
        if rel.parts[0] not in {'source','work','outputs','assets','qa'} and rel.name not in {'README.md','VERSION','requirements.txt'}:continue
        if p.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.pyc'}:raise RuntimeError(f'Forbidden package suffix: {p}')
        if p.stat().st_size==0:raise RuntimeError(f'Empty file: {p}')
        entries.append(p)
    sums={p.relative_to(ROOT).as_posix():digest(p) for p in entries}
    (ROOT/'SHA256.json').write_text(json.dumps(sums,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    entries.append(ROOT/'SHA256.json')
    zpath=ROOT.parent/'flagship_69_delivery.zip'
    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in entries:z.write(p,'flagship_69/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        for name,sha in sums.items():assert hashlib.sha256(z.read('flagship_69/'+name)).hexdigest()==sha
    fresh=ROOT.parent/'flagship_69_archive_check'
    if fresh.exists():shutil.rmtree(fresh)
    with zipfile.ZipFile(zpath) as z:z.extractall(fresh)
    extracted=fresh/'flagship_69'
    for name,sha in sums.items():assert digest(extracted/name)==sha
    pages=0
    for path in (extracted/'outputs').glob('*.pdf'):
        with fitz.open(path) as doc:
            for page in doc:
                pix=page.get_pixmap(matrix=fitz.Matrix(.5,.5),alpha=False)
                assert pix.width and pix.height
                pages+=1
    assert pages==audit['totalPdfPages']
    names={
        'rules':'完整规则书','catalog':'全卡牌图鉴','main_cards':'统一主牌正反面',
        'starter_cards':'初始通用配件正反面','reference_cards':'参考机正反面',
        'aids':'实体组件','suppliers':'供应商署名与授权组件','expansion':'扩产组件与速查',
        'boards':'线下版图','planning':'设计规划书','chip_roster':'50芯片名录与特色',
        'chip_sources':'芯片资料与设计边界','changes':'修改与校验说明',
        'printing':'打印与实体准备','verification':'交付核对记录',
    }
    delivered=[]
    for key,stem in names.items():
        for ext in ['pdf','docx','html','md']:
            src=O/f'旗舰元年_6.9_{stem}.{ext}'
            if src.is_file():
                dst=ROOT.parent/f'flagship_69_{key}.{ext}'
                shutil.copy2(src,dst)
                assert digest(src)==digest(dst)
                delivered.append(str(dst))
    result={'version':'6.9','zip':str(zpath),'zipBytes':zpath.stat().st_size,
            'zipSha256':digest(zpath),'filesInZip':len(entries),'manifestFiles':len(sums),
            'extractedHashesMatch':True,'reopenedPdfPages':pages,'remotePushed':False,
            'convenienceFiles':delivered}
    (ROOT.parent/'flagship_69_final_delivery.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
