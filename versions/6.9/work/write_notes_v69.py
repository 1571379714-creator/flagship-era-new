from pathlib import Path
from collections import Counter
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'outputs';W=R/'work';D=json.loads((W/'v69_data.json').read_text());B=json.loads((R/'source/v68_data.json').read_text());P={c['id']:c for c in D['parts']};BP={c['id']:c for c in B['parts']}
chips=D['chipRoster'];named=[];num=[];effects=[]
for r in chips:
 c=P[r['card']];b=BP[c['id']];x=next(a for a in c['components']if a['kind']=='chip');y=next(a for a in b['components']if a['kind']=='chip')
 if x['name']!=y['name']:named.append(c['id'])
 if any(x[k]!=y[k]for k in ['spec','power','batchCost']):num.append(c['id'])
 if c['effect']!=b['effect']:effects.append(c['id'])
lines=['# 旗舰元年6.8 → 6.9 修改与校验说明','## 实际输入与边界','底稿是实际6.8完整包，source保留原数据与正文、逐文件SHA256。原6.8不覆盖。本次没有读取或写入GitHub远端；本地文件不等于已提交。','## 范围','指定40款全部保留：骁龙12、联发科9、苹果10、麒麟7、玄戒2；补猎户座6、Google2、展锐2，合计50。每代4稳定＋6含芯片定制；稳定80、定制64、主牌257、内容315不变；16初始通用配件保持。','苹果全称为A11—A16 Bionic、A17—A20 Pro。名录与卡标题、内部芯片行同名。未通过“+”或套装后缀制造假唯一型号。厂标仅SVG与厂名，去掉供货前缀；屏幕/机身保留形态，芯片/影像不印直板。',f'名称变化12处：{", ".join(named)}。',f'芯片规格/功耗/每批费变化7处：{", ".join(num)}。其余43个芯片行这三项原值保留。C112普通/伙伴入库价从12/4改为8/2，其他79张稳定价对保留6.8。',f'机械效果文字变化18张：{", ".join(effects)}。其他32个含芯片位置保留原特性；个别名称与资料说明虽变不计新机制。','41科技、30合同、18设施、24方案、30参考、12需求的完整机械数据保持6.8。套装内部非芯片行、四类/世代/厂商配比、T21、逐卡研究费用和工期、核心合作和扩产机制均不重做。','## 所有芯片当前值与变更','下面以当前数据生成完整50行，规格/负载/芯片行费用均为游戏设计，不能读成跑分/瓦数/现实价格。']
lines+=['| 卡号 | 原名 → 现名 | 规格 | 负载 | 芯片费 |','|---|---|---:|---:|---:|']
for r in chips:
 c=P[r['card']];b=BP[c['id']];x=next(a for a in c['components']if a['kind']=='chip');y=next(a for a in b['components']if a['kind']=='chip');lines.append('| '+c['id']+' | '+y['name']+' → '+x['name']+' | '+' | '.join(str(y[k])+'→'+str(x[k])for k in ['spec','power','batchCost'])+' |')
lines+=['## 18张效果前后对照']
for cid in effects:
 lines += ['### '+cid+' '+P[cid]['name'],'**6.8：** '+BP[cid]['effect'],'**6.9：** '+P[cid]['effect'],'**理由：** '+P[cid]['designRationale']]
lines+=['## 不确定性与旧断言','T760第一方终端资料可核型号、制程与5G应用，但首发原始档案不充分。第三代仍为经确认的游戏归档并在卡面标记待核。麒麟9030与9030Pro在官网分别列出，采用9030；9050第一方只明确Pro，家族简称留存，不冒充标准版完整参数。8EE6/O3继续前瞻待核。',
'加入T760后第三代稳定规格为7、8、9、5，差4。旧“稳定每代差≤3”是先前数值检查，不是玩家规则；本次明确改为≤4并保留其他约束，不为通过测试虚构T760旗舰性能。',
'21个位置本轮读取第一方材料（包括有明确缺口者），29个位置沿用历史来源。完全没有50芯片共同测试条件的性能/功耗测量。',
'## 实际测试与运行方法','运行python work/run_tests_v69.py执行116个单元测试，其中77个继承、39个名录与特色条件测试。前述继承中两处输入/数值断言适配已明列。内部包括600个单市场、1200个四市场扩产情境，不是1800局。',
'运行python work/check_components_v69.py记录160个部件可组装见证；python work/scan_chip_routes_v69.py为50个芯片寻找能触发其特性的实际配件组合。假设已经取得配件并完成指定自主技术，资金、工作足够；不证明实际取得路径。能力夹具的正反测试与实际配件见证分开，不把合成测试配置当成牌库设计。',
'文件检查、PDF逐页渲染、HTML边界与独立重建记录另见交付核对。没有真人多人实测、全卡策略穷举或实际打印机套准。',
'## 数据与构建','build_all.py只导出现行v69_data.json与结构化正文；不自动运行revise_v69.py。后者是本次历史迁移脚本，会覆盖手改数据，日常不要运行。字体依赖环境安装，不随包分发。']
(O/'旗舰元年_6.9_修改与校验说明.md').write_text('\n\n'.join(lines)+'\n',encoding='utf8')
printing='''# 6.9 打印与实体准备

## 选择完整版本，不重复混牌
主牌正反面58页：257张，已按实体份数展开，每种1张。A4原尺寸、相邻页正反、长边翻转。全卡图鉴按315种供阅读，不再从中重复剪出一套主牌。

初始通用配件4页：全桌16张，每人按M01—M04领取芯片、屏幕、影像、机身各1张，免费入四栏。两三人局其余留盒内。初始不是产品代替卡，不混主牌。

30参考机使用独立10页正反面，按世代六张收纳，锁价后当场随机抽。12张需求仍从图鉴最后3页取用，一次公开一张；它们不是购买区。

## 6.8可继续使用的组件
每人16张稳定部件代替卡；每人12枚公司/产品指派片（每产品号3枚）；原作者署名片、五厂关系/核心片、0—8研发进度条、合同期限片、价牌和扩产＋1标记均不新增。新版厂标显示更简洁，但不用为此重新制作所有旧通用小标记。

供应商组件第1—2页是公司/产品指派正反，其他页包含永久署名与厂区等；通用组件中的相应页是速查，不当成额外一套指派。稳定代替卡与初始实体分别发放。扩产3页组件全桌一套，仍是每公司每场最多一次。

## 卡面换印范围
所有主牌的厂标视觉前缀更新。12个含芯片卡名称变化、18个效果变化、7个芯片数值变化；其中有重叠，具体见work/reprint_manifest_v69.json。机械变更不能只改标题而继续用旧数值/效果。局部换印请全套使用同款不透明牌套，避免卡背、纸张泄露信息。

## 尺寸与文件角色
统一主牌63×88mm；卡背已镜像对位，不使用“适合纸张”缩放。先试印一对正反检查打印机偏移。初始配件同尺寸，参考机为独立功能卡尺寸。线下版图是A3横向展示/打印视图集合；个人部分按人数准备，公共部分一份。

50芯片名录与特色9页是阅读与审核资料，不混主牌。来源说明中保留待核边界，不是玩家需要查询的额外效果。卡面已经写明全部游戏数值与条件。

没有进行真实打印机套准或商业出血、刀模/CMYK验证。浏览器/PDF像素检查不等于实际印厂确认。包内不含字体文件，只列环境依赖。
'''
(O/'旗舰元年_6.9_打印与实体准备.md').write_text(printing,encoding='utf8')
rename=set(named);eff=set(effects);mechanical=set(num)|eff|{'C112'}
(W/'reprint_manifest_v69.json').write_text(json.dumps({'version':'6.9','nameChanged':named,'numericChanged':num,'effectChanged':effects,'mechanicalCards':sorted(mechanical),'titleOrMechanicalCards':sorted(mechanical|rename),'factoryDisplayChangedOnAllBadgedCards':True,'componentsUnchanged':True},ensure_ascii=False,indent=2),encoding='utf8')
(R/'README.md').write_text('''# 旗舰元年 6.9 · 五十平台与芯片专长

现行底稿从6.8延续，不与旧卡面混用。本包含完整规则、315种图鉴、257主牌正反、初始16张、参考/需求与所有功能组件；另有50芯片名录与特色。

## 阅读顺序
先看outputs内完整规则书；卡牌以v69_data.json与全卡图鉴为准。核对芯片先读50芯片名录；设计取舍看规划书；修改前后对照、来源边界和打印份数分别有说明。

## 构建
环境：Python 3.12或更新、requirements.txt依赖、LibreOffice、Chromium、Noto Sans CJK SC。没有捆绑字体或凭据。使用：

```text
python work/build_all.py
python work/run_tests_v69.py
python work/check_components_v69.py
python work/scan_chip_routes_v69.py
python work/check_layout.py
python work/check_delivery_v69.py
```

结构化正文在work/v69_rulebook.json，核实修改后用sync_rules_text.py同步Markdown。revise_v69.py只供迁移复现，会覆盖手改数据，不作为普通构建步骤。静态验证器不提供电子发牌、自动游玩或保存对局。

source是原6.8快照，SHA256可核对。本次未推送GitHub，没有选择新许可或修改远端历史。测试仅证明其注明范围，不声称游戏平衡、完整对局或真实硬件横测。
''',encoding='utf8')
print('Release notes written; mechanical cards',len(mechanical),'title or mechanical',len(mechanical|rename))
