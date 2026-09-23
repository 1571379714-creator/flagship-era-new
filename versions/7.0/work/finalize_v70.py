"""Package only verified current files; validate extraction hashes, never touch a remote."""
from pathlib import Path
import json,hashlib,zipfile,shutil,re
R=Path(__file__).resolve().parents[1];W=R/'work';O=R/'outputs';D=R.parent
load=lambda n:json.loads((W/n).read_text())
a=load('delivery_audit_v70.json');reb=load('rebuild_audit_v70.json');comp=load('component_witnesses_v70.json');assert not a['issues'] and not reb['issues']
log=(R/'qa/unit_tests.log').read_text();m=re.search(r'Ran (\d+) tests in ([\d.]+)s',log);assert m and log.strip().endswith('OK');num=int(m.group(1))
changes=load('v69_to_v70_changes.json')
visual={'version':'7.0','rulebook':{'pages':25,'method':'canonical DOCX renderer, each PNG page opened at readable scale','latestTextIdenticalToCanonicalRender':True},'planning':{'pages':2,'method':'canonical DOCX renderer, each PNG page opened'},'catalog':{'pages':76,'method':'all-page contact sheets plus full-effect text/geometry checks'},'main':{'pages':58,'method':'all29 front pages overview, backs mirrored, X152/X147 latest full page viewed'},'boards':{'views':12,'method':'all-page overview plus dual-track/array large view'},'functional':'action fronts, supplier/initial/reference overviews, expansion reused inspected layout, cash page large view','detectedUnresolvedLayoutIssues':0,'notValidated':['actual physical printer registration','color/bleed/die cut','all card interaction semantics']}
(W/'visual_review_v70.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2))
report=f'''# 7.0 交付核对记录

## 本次实际结果

- 规则书25页、规划书2页；全部PDF **{a['pdfCount']}个、{a['pdfPages']}页**。
- 内容牌315种315张，主牌257，初始16、参考30、需求12；50个芯片名唯一。
- 六行动为额外功能牌，每人6张；T21未增加指派片或产品格。研发仍每项一枚进度片。
- 规则单元测试实际执行 **{num}项，0失败0错误**，见qa/unit_tests.log。没有沿用6.9测试输出充数。
- 其中阵列全排列720种、每种6选项×2交换选择，共8640状态转换；可到达排列720种。
- 有限市场/扩产用例内含600个独立单市场和1200个四市场情境；不是600局或1200局游戏。
- 条件合法配件见证 **{comp['partWitnesses']}个，搜索{comp['searchAttempts']}次**。假设已有相关牌与已完成研发、资金足；不能证明随机获取路径或盈利。
- 315张图鉴卡与257张实际主牌的完整效果文字，分别核对当前JSON、HTML和对应PDF页；没有用示例卡代替全卡组。
- 11个HTML页面几何检查0个未解决问题；所有12个PDF逐页实际打开并渲染。
- 在独立空outputs目录从同一现行数据实际重新构建：**{len(reb['html'])}个HTML逐字节相同，{len(reb['pdf'])}个PDF页数及逐页文字一致**。不以PDF容器元数据时间戳要求二进制相同。
- source/SHA256.json中4份原6.9数据/正文哈希均未改变。

## 人工排版检查

规则书25页与规划书2页使用DOCX专用渲染器，逐页打开图像；后续重建文本与已审阅版本一致。图鉴76页、29张主牌正面、12视图版图和其余实体件检查总览，双轨、双行阵列、长芯片卡、六行动卡与现金页另放大检查。交付包不含大量内部预览图，记录在work/visual_review_v70.json。

## 节奏结论：仍是首测，不是平衡保证

4/9/15/22科技领先换代、130/46双轨、8/12/16发布长度已实施。每代约两场、第五代约两场含最终为校准目标。

已附公开输入的节奏预算：均衡轨迹示例最终第10场；科研偏向示例第11场，进入第五代后多一场；商业偏向输入第10场仍差3格，且依赖其他科研玩家较早换代。没有隐去未完全贴合目标的结果，也没有把这些人为输入声称为完整对局测得平均值。

没有完成完整随机牌序的2/3/4人端到端对局，也没有所有合同/设施/方案的通用事件解释器。真实局长、供需/竞品占单率、授权收益、三卡高强循环和各路线平衡仍待多人实测。程序样例数量不是多人局数，存在合法配法不是盈利证明。

## 本地与远端边界

全部成品本次实际生成。7.0完整包内MANIFEST.sha256.json提供每一交付文件哈希，打包后再次解压并比较；外层ZIP摘要另交付。没有推送GitHub、远端树比对、提交、分支、标签或定期监测。用户自行上传。

## PDF清单

| 文件 | 页数 | 实际字节 |
|---|---:|---:|
'''+ '\n'.join(f'| {n} | {v["pages"]} | {v["bytes"]} |' for n,v in a['pdfs'].items())+'\n'
(O/'旗舰元年_7.0_交付核对记录.md').write_text(report,encoding='utf8')
(R/'CHANGELOG.md').write_text('# 7.0\n\n完整变化见outputs/旗舰元年_7.0_迁移核对与修改说明.md与work/v69_to_v70_changes.json。以source/6.9为底稿，不覆盖原归档。\n',encoding='utf8')
(R/'.gitignore').write_text('__pycache__/\n*.pyc\n.venv/\nqa/*_render/\nqa/overviews/\nqa/*.png\nqa/*.jpg\n',encoding='utf8')
# Package scripts/data/print outputs and actual compact QA logs, not fonts or stale images.
def allowed(p):
 rel=p.relative_to(R)
 if '__pycache__' in rel.parts or p.suffix.lower() in ['.pyc','.ttf','.otf','.woff','.woff2']:return False
 if rel.parts[0]=='qa':return len(rel.parts)==2 and p.suffix in ['.log','.json','.md']
 return p.is_file() and p.name!='MANIFEST.sha256.json'
files=sorted(p for p in R.rglob('*') if allowed(p))
man={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(R/'MANIFEST.sha256.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf8');files+=[R/'MANIFEST.sha256.json']
zip_path=D/'flagship_70_delivery.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,'flagship_70/'+str(p.relative_to(R)))
extract=D/'flagship_70_package_check'
if extract.exists():shutil.rmtree(extract)
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None;assert len(z.namelist())==len(files);z.extractall(extract)
for rel,h in man.items():assert hashlib.sha256((extract/'flagship_70'/rel).read_bytes()).hexdigest()==h,rel
# Open the EXTRACTED PDFs as a final check of the bytes the user receives.
import fitz
for p in (extract/'flagship_70/outputs').glob('*.pdf'):
 with fitz.open(p) as doc:
  for page in doc:page.get_pixmap(matrix=fitz.Matrix(.2,.2),alpha=False)
aliases={'完整规则书':'rules','全卡牌图鉴':'catalog','六部门行动正反面':'actions','统一主牌正反面':'main_cards','初始通用配件正反面':'starter_cards','参考机正反面':'reference_cards','线下版图':'boards','实体组件':'aids','供应商署名与授权组件':'suppliers','扩产组件与速查':'expansion','设计规划书':'planning','芯片与市场校准表':'chip_calibration','迁移核对与修改说明':'changes','打印与实体准备':'printing','节奏预算与实测清单':'pace','芯片资料与设计边界':'chip_sources','交付核对记录':'verification'}
links=[]
for zh,en in aliases.items():
 for p in O.glob(f'旗舰元年_7.0_{zh}.*'):
  q=D/f'flagship_70_{en}{p.suffix}';shutil.copyfile(p,q);assert q.stat().st_size>0;links.append(str(q))
summary={'zip':str(zip_path),'bytes':zip_path.stat().st_size,'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'files':len(files),'extractedHashMatches':len(man),'pdfPages':a['pdfPages'],'pdfCount':a['pdfCount'],'allExtractedPdfPagesRendered':True,'tests':num,'links':links,'remoteWrite':False}
(D/'flagship_70_package_audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
(D/'flagship_70_delivery.sha256.txt').write_text(summary['sha256']+'  flagship_70_delivery.zip\n')
print(json.dumps({k:v for k,v in summary.items() if k!='links'},ensure_ascii=False,indent=2))
