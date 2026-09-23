"""6.8→6.9定向迁移；仅历史复现使用，会重写现行数据。日常运行build_all.py。"""
from pathlib import Path
import json,copy,hashlib,re
R=Path(__file__).resolve().parents[1];W=R/'work';O=R/'outputs';S=R/'source'
old=json.loads((S/'v68_data.json').read_text(encoding='utf8'));d=copy.deepcopy(old)
d.update(version='6.9',subtitle='五十平台与芯片专长',date='2026-09-23',status='名单定向更新测试版；未充分多人实测')
d['provenance']={'sourceVersion':'6.8','sourceDataSha256':hashlib.sha256((S/'v68_data.json').read_bytes()).hexdigest(),'sourceDirectory':'source','scope':'批准的40款＋6猎户座＋2谷歌＋2展锐；苹果保留完整名称；芯片特色与必要重标；不改其他机制'}
p={c['id']:c for c in d['parts']};op={c['id']:c for c in old['parts']}
rows=[
('C101','Helio X30','MediaTek'),('C102','骁龙835','Qualcomm'),('C103','麒麟970','Kirin'),('C104','猎户座8895','Exynos'),
('C105','猎户座9825','Exynos'),('C106','猎户座990','Exynos'),('C107','麒麟990','Kirin'),('C108','骁龙865','Qualcomm'),
('C109','天玑1200','MediaTek'),('C110','骁龙8 Gen 1','Qualcomm'),('C111','天玑9000','MediaTek'),('C112','唐古拉T760','UNISOC'),
('C113','Google Tensor G4','Google'),('C114','猎户座2400','Exynos'),('C115','骁龙8 Elite','Qualcomm'),('C116','天玑9300','MediaTek'),
('C117','麒麟9030','Kirin'),('C118','天玑9500','MediaTek'),('C119','玄戒O1','XRing'),('C120','骁龙8 Elite Gen 5','Qualcomm'),
('X101','骁龙845','Qualcomm'),('X102','SC9863A','UNISOC'),('X109','猎户座9810','Exynos'),('X110','麒麟980','Kirin'),('X113','A11 Bionic','Apple'),('X114','A12 Bionic','Apple'),
('X115','骁龙855','Qualcomm'),('X120','天玑1000','MediaTek'),('X123','A13 Bionic','Apple'),('X124','猎户座9820','Exynos'),('X125','麒麟9000','Kirin'),('X126','A14 Bionic','Apple'),
('X127','骁龙8+ Gen 1','Qualcomm'),('X128','骁龙888','Qualcomm'),('X135','天玑9200','MediaTek'),('X136','骁龙8 Gen 2','Qualcomm'),('X137','A15 Bionic','Apple'),('X138','A16 Bionic','Apple'),
('X139','Google Tensor G3','Google'),('X144','麒麟9020','Kirin'),('X147','骁龙8 Gen 3','Qualcomm'),('X148','天玑9400','MediaTek'),('X149','A17 Pro','Apple'),('X150','A18 Pro','Apple'),
('X151','A19 Pro','Apple'),('X152','骁龙8EE6〔前瞻〕','Qualcomm'),('X159','天玑9600 Pro','MediaTek'),('X160','麒麟9050','Kirin'),('X163','玄戒O3〔待核〕','XRing'),('X164','A20 Pro','Apple')]
source_old={s['cardId']:s for s in old['chipSources']}
for cid,name,family in rows:
 c=p[cid];chip=next(a for a in c['components']if a['kind']=='chip');suffix=c['name'].split('·',1)[1]if'·'in c['name']else''
 chip['name']=name;c['name']=name+('·'+suffix if suffix else'');c['chipFamily']=family;c['chipCanonical']=re.sub(r'〔.*?〕','',name);c['chipSourceKey']='v69_'+cid
 c['evidenceStatus']='沿用6.8身份与主题资料，未对该型号重新进行统一硬件测量';c['chipTier']='旗舰方案'
 c['chipSources']=['v69_'+cid];chip['chipSource']='v69_'+cid
 c.pop('realityCalibration',None)
# Necessary revaluation only where the platform changed: spec / game load / per-batch cost.
nums={'X102':(2,3,1),'X115':(7,5,7),'X120':(7,5,6),'X124':(7,7,6),'C112':(5,3,3),'X135':(10,6,11),'X144':(9,6,9)}
for cid,vals in nums.items():
 chip=next(a for a in p[cid]['components']if a['kind']=='chip');chip.update(dict(zip(['spec','power','batchCost'],vals)))
p['C112'].update(installCost=8,installPartnerCost=2,chipYear=None,chipTier='主流5G方案',cardEvidenceNote='应用可核；首发年份待核')
p['C117'].update(chipYear=2025,chipTier='旗舰方案')
p['X102'].update(chipYear=2018,chipTier='主流成本方案')
p['X115']['chipYear']=2019;p['X120']['chipYear']=2019;p['X124']['chipYear']=None;p['X124']['cardEvidenceNote']='2018发布／2019应用';p['X128']['chipYear']=2021
p['X135']['chipYear']=2022;p['X144']['chipYear']=2024;p['X151']['chipYear']=2025
p['C107']['cardEvidenceNote']='990家族；版本参数非精确还原'
p['X160']['cardEvidenceNote']='9050家族；无后缀版本待核'
for cid,mark in {'C112':'续航','C117':'生态','X102':'续航','X124':'生态','X144':'生态','X151':'生态'}.items():
 next(a for a in p[cid]['components']if a['kind']=='chip')['mark']=mark

def field(k,f,op,val):return {'kind':k,'field':f,'op':op,'value':val}
def dep(f):return {'deployedField':f}
def anyof(*conds):return {'any':list(conds)}
def rule(op,value=None,when=(),**kw):
 z={'op':op,'when':list(when),**kw}
 if value is not None:z['value']=value
 return z

def effect(cid,txt,rs,reason):
 c=p[cid];c['effect']=txt;c['rules']=rs
 for z in rs:z['text']=txt
 c.pop('chipEffect',None);c['designRationale']=reason
Sg=lambda n:field('screen','spec','>=',n)
Cg=lambda n:field('camera','spec','>=',n)
# Boundaries are card-local, use existing product data or deployed technology; no new resource/state.
effect('X102','普及主板：屏幕与影像印刷规格均至多4时，组装费减3，最低0。',
 [rule('assemblyDiscount',3,[field('screen','spec','<=',4),field('camera','spec','<=',4)])],
 'SC9863A官方面向主流LTE终端；低规格与低制造成本定位，不冒充旗舰。主板简化优惠为游戏工程抽象。')
effect('C112','普及5G：以18或28售价投放时，可进入商务办公；不自动取得生态或安全，不绕过预算。',
 [rule('permit',None,[{'priceIn':[18,28]}],market='office')],
 'T760的第一方终端资料支持6nm与5G产品身份。以低价办公入口体现供货用途，不把网络代际直接换为通用性能。')
effect('X115','Spectra视觉处理：影像印刷规格至少5时，摄影创作竞争力加2；部署影像研发时免除本机影像的芯片兼容要求。',
 [rule('market',2,[Cg(5)],market='photo'),rule('compatibility',None,[dep('影像')])],
 '855区别于855+：围绕Spectra ISP和计算视觉设计影像入口，不再继承加强版的单一高帧能力。')
effect('X120','集成5G：屏幕印刷功耗至多2时，芯片有效功耗减1，最低0；不减少其他部件功耗。',
 [rule('powerReduction',1,[field('screen','power','<=',2)],kind='chip')],
 '天玑1000使用基础型号名称，强调集成平台与能耗配套；不把1000+的具体新增显示特性移植到本卡。')
effect('X124','NPU场景识别：影像印刷规格至少5且部署系统领域研发时，摄影创作竞争力加3。',
 [rule('market',3,[Cg(5),dep('系统')],market='photo')],
 '猎户座9820改走NPU影像配套，规格/成本/负载重新定档；2018年发布而2019年代表终端应用，置第二供货窗口。')
effect('X128','三路ISP：影像印刷规格至少6时，摄影创作竞争力加2；同时部署散热研发时再加1。',
 [rule('market',2,[Cg(6)],market='photo'),rule('market',1,[Cg(6),dep('散热')],market='photo')],
 '骁龙888保留高负载，突出三路ISP与散热取舍。以多路影像与热设计配套形成加分，不把ISP解释为联网生态。')
effect('X135','Immortalis光追：屏幕印刷规格至少7且部署平台领域研发时，电竞娱乐竞争力加4。',
 [rule('market',4,[Sg(7),dep('平台')],market='gaming')],
 '天玑9200围绕Immortalis硬件光追与驱动适配；不是9000+简单改名，规格与费用随新平台调整。')
effect('X144','鸿蒙影像适配：影像印刷规格至少7且部署系统领域研发时，摄影创作竞争力加3。',
 [rule('market',3,[Cg(7),dep('系统')],market='photo')],
 '麒麟9020身份可由华为终端参数核对；本卡为软硬协同游戏方案，不断言未取得的CPU/ISP微架构。')
effect('C117','整机协同：屏幕印刷规格至少8且部署系统领域研发时，商务办公竞争力加3。',
 [rule('market',3,[Sg(8),dep('系统')],market='office')],
 '官方Mate80Pro规格区分9030与9030Pro；使用用户指定9030，不挪用Pro独有参数，以系统研发形成办公路线。')
effect('X151','神经图形：屏幕印刷规格至少8，且部署平台或系统领域研发时，电竞娱乐竞争力加3。',
 [rule('market',3,[Sg(8),anyof(dep('平台'),dep('系统'))],market='gaming')],
 'A19 Pro的GPU神经加速器与神经引擎协作作为特色依据；N1独立网络芯片的能力不算在A19 Pro名下。')
# Distinct Apple generations, keep their complete commercial names and the original non-chip kit parts.
effect('X113','神经人像：影像印刷规格在3至5之间时，本产品取得影像特征；不改变影像规格。',
 [rule('feature',None,[Cg(3),field('camera','spec','<=',5)],feature='影像')],
 'A11 Bionic以神经引擎与人像处理作主题，帮助较低规格模组取得拍摄用途；这是游戏资格而非像素推算。')
effect('X114','Smart HDR联调：部署影像领域研发时，摄影创作竞争力加3；仍检查市场入场资格。',
 [rule('market',3,[dep('影像')],market='photo')],
 'A12 Bionic把软件影像研发变成HDR调校优势，不再只因套装自带一块相机就无条件加分。')
effect('X123','Deep Fusion：影像印刷规格至少5，且部署影像或系统领域研发时，摄影创作竞争力加3。',
 [rule('market',3,[Cg(5),anyof(dep('影像'),dep('系统'))],market='photo')],
 'A13 Bionic以计算摄影与机器学习协作为主题，允许影像和系统两种研发搭配。')
effect('X126','神经能效：部署系统领域研发时，芯片有效功耗减1，最低0。',
 [rule('powerReduction',1,[dep('系统')],kind='chip')],
 'A14 Bionic以神经引擎与系统协同体现能效路线；减1是游戏调校收益，不是官方功耗数据。')
effect('X137','电影模式：屏幕带影像标识且部署系统领域研发时，摄影创作竞争力加4。',
 [rule('market',4,[field('screen','mark','==','影像'),dep('系统')],market='photo')],
 'A15 Bionic与电影模式、视频编解码的官方关联，转化为显示监看和系统研发的创作组合。')
effect('X138','显示协同：部署显示领域研发时，屏幕有效功耗再减1，最低0。',
 [rule('powerReduction',1,[dep('显示')],kind='screen')],
 'A16 Bionic平台的低刷新率显示与节能整机应用是主题依据；不宣称本次证实一个特定独立硬件模块。')
effect('X149','硬件光追：屏幕印刷规格至少7且部署平台领域研发时，电竞娱乐竞争力加4。',
 [rule('market',4,[Sg(7),dep('平台')],market='gaming')],
 'A17 Pro以硬件加速光线追踪与软件适配作主题；仍保持整套绑定与按批费用。')
effect('X150','专业视频：以38或48售价投放摄影创作，且部署影像领域研发时，本市场竞争力加4。',
 [rule('market',4,[{'priceIn':[38,48]},dep('影像')],market='photo')],
 'A18 Pro以专业视频工作流支撑高价创作产品，而非在所有售价下自动领先。')
# Keep uncertain models honest. Their names are user-approved; unexplored variants are not official facts.
p['X160']['evidenceStatus']='麒麟9050家族名按用户指定保留；本次第一方材料明确为9050 Pro，无后缀版本独立参数未核实'
p['X160']['designRationale']='沿用受限的折叠＋系统研发组合，不把9050 Pro资料冒充无后缀9050的确切架构。'
p['X152']['cardEvidenceNote']='前瞻名称；完整官方参数待核'
p['X163']['cardEvidenceNote']='O3完整第一方参数待核'
# Freshly read primary documents, scoped to what they support (not a common benchmark).
src={
 'X102':('https://www.unisoc.com/en/product/SmartPhoneUS/9863A','官方产品页确认SC9863A、A55/LTE与主流市场定位。不能用它证明统一负载功耗或旗舰级别。','身份及功能'),
 'C112':('https://www.hmd.com/en_in/hmd-crest/specs','HMD官方终端规格明确T760、6nm与5G。未取得首发原始公告，第三代位置为批准的游戏归档，不伪造首发年份。','身份/应用；年代待核'),
 'X115':('https://www.qualcomm.com/smartphones/products/8-series/snapdragon-855-mobile-platform','官方页面列Spectra 380、Kryo 485和Adreno 640。仅用于855身份与图像处理主题，不沿用855+频率。','身份及功能'),
 'X120':('https://i.mediatek.com/mediatek-5g','官方目录单列Dimensity1000并介绍集成5G的1000家族；不把家族列表中1000+新增特性自动归给基础版。','基础名与家族范围'),
 'X124':('https://semiconductor.samsung.com/processor/mobile-processor/exynos-9-series-9820/','官方产品页列专用NPU、三丛集CPU、ISP及8nm工艺；用于场景识别主题。','身份及功能'),
 'X128':('https://www.qualcomm.com/smartphones/products/8-series/snapdragon-888-5g-mobile-platform','官方列Spectra 580三路ISP及平台功能；本卡使用888而非888+。游戏负载8不是瓦数。','身份及功能'),
 'X135':('https://www.mediatek.com/products/smartphones/mediatek-dimensity-9200','官方列Cortex-X3、Immortalis-G715硬件光追与LPDDR5X；用于高帧配套主题。','身份及功能'),
 'X144':('https://consumer.huawei.com/cn/phones/mate80/specs/','官方终端规格列麒麟9020；不提供统一横测数据。本卡第四代的历史归档另承接Mate70时代背景，不以无日期页面证明发布时间。','身份；架构推断不作事实'),
 'C117':('https://consumer.huawei.com/cn/phones/mate80-pro/specs/','官方明确12GB版本麒麟9030、16GB版本9030 Pro。本卡采用前者；不混用后者独有性能。','身份及应用'),
 'X151':('https://www.apple.com/newsroom/2025/09/apple-unveils-iphone-17-pro-and-iphone-17-pro-max/','苹果官方介绍A19 Pro GPU内神经加速器及与神经引擎协作；设备散热和N1网络芯片不能混成SoC本身规格。','身份及功能'),
 'X137':('https://www.apple.com/newsroom/2021/09/apple-unveils-iphone-13-pro-and-iphone-13-pro-max-more-pro-than-ever-before/','官方将A15 Bionic与电影模式、视频编解码相联系。游戏要求显示标识与系统研发是设计取舍。','身份及功能'),
 'X138':('https://www.apple.com/newsroom/2022/09/apple-debuts-iphone-14-pro-and-iphone-14-pro-max/','官方介绍A16 Bionic、ProMotion低刷新率显示及整机能效应用；屏幕减耗是游戏联调，不是实测公式。','身份及应用'),
 'X159':('https://www.mediatek.com/products/smartphones/mediatek-dimensity-9600-pro','官方产品页强调CPU/GPU/NPU/ISP的AI协同。游戏档位及整套配件组合仍为暂定设计。','官方功能；横测不足'),
 'X160':('https://www.huawei.com/de/news/2026/logicfolding-chiparchitektur-kommerzielle-anwendung','此官方材料写9050 Pro，不足以确证无后缀9050独立型号参数；按用户家族简称保留并显式标记缺口。','仅Pro资料；无后缀待核'),
 'X164':('https://www.apple.com/newsroom/2026/09/apple-debuts-iphone-18-pro-and-iphone-18-pro-max/','官方A20 Pro发布材料用于名称与创作/神经处理方向。游戏整机方案不宣称现实可外售授权或精确横向性能。','官方功能；横测不足')}

src.update({
 'X113':('https://www.apple.com/newsroom/2017/09/the-future-is-here-iphone-x/','官方介绍A11 Bionic神经引擎、实时场景处理和人像摄影应用。游戏影像资格是规则抽象，不是硬件像素换算。','身份及功能'),
 'X114':('https://www.apple.com/newsroom/2018/09/iphone-xs-and-iphone-xs-max-bring-the-best-and-biggest-displays-to-iphone/','官方介绍A12 Bionic神经引擎、ISP与Smart HDR的联动，用于影像研发搭配主题。','身份及功能'),
 'X123':('https://www.apple.com/newsroom/2019/09/apple-introduces-dual-camera-iphone-11/','官方明确Deep Fusion由A13 Bionic神经引擎支持，并结合机器学习处理照片。','身份及功能'),
 'X126':('https://www.apple.com/newsroom/2020/09/apple-unveils-all-new-ipad-air-with-a14-bionic-apples-most-advanced-chip/','官方A14 Bionic资料支持机器学习与系统效能方向；本卡减耗仅为游戏联调。','身份及功能'),
 'X149':('https://www.apple.com/newsroom/2023/09/apple-unveils-iphone-15-pro-and-iphone-15-pro-max/','官方A17 Pro资料支持硬件加速光线追踪；平台研发条件和加4是游戏设计。','身份及功能'),
 'X150':('https://www.apple.com/newsroom/2024/09/apple-debuts-iphone-16-pro-and-iphone-16-pro-max/','官方介绍A18 Pro平台与专业视频、4K高帧录制工作流；本卡高价条件不是现实功能锁定。','身份及功能')})

newsrc=[]
for cid,name,family in rows:
 c=p[cid];s=copy.deepcopy(source_old.get(cid,{}));s.update(key='v69_'+cid,cardId=cid,name=name,year=c.get('chipYear'),tier=c['chipTier'],gameValues='6.9游戏压缩数值；非跑分/瓦数/采购报价。套装为游戏工程方案。')
 if cid in src:
  url,basis,level=src[cid];s.update(url=url,basis=basis,checked='2026-09-23',status='本轮读取第一方材料：'+level,verificationLevel=level);s.pop('webRef',None);c['evidenceStatus']=s['status']
 else:
  s['status']='沿用6.8归档来源，6.9未逐一重新核验；新能力是游戏设计';s['verificationLevel']='历史资料/待核沿用';s['inheritedSourceKey']=source_old.get(cid,{}).get('key');s.pop('webRef',None)
 if cid in ('X152','X163'):
  s.update(status='用户指定前瞻/待核占位；本次未取得完整匹配第一方参数',verificationLevel='待核');c['evidenceStatus']=s['status']
 if cid=='C107':
  s['status']='本次按用户简称改为麒麟990；沿用990家族资料，不将5G版所有参数宣称为标准版';s['verificationLevel']='家族简称/版本边界';s['basis']='原归档为麒麟990 5G；本卡游戏参数代表用户指定990家族供货方案。'
 s['limitation']='身份/官方功能不能证明跨厂绝对性能与功耗排序；数字仍需多人实测。'+(' '+c['cardEvidenceNote'] if c.get('cardEvidenceNote')else'')
 c['chipBasis']=s['basis'];newsrc.append(s)
d['chipSources']=newsrc;d['chipRoster']=[{'card':cid,'name':name,'family':f,'era':p[cid]['era'],'type':p[cid]['type']}for cid,name,f in rows]
d['chipAuditNote']='50款唯一芯片。用户指定40款全部保留，补6猎户座2谷歌2展锐；苹果A11—A16 Bionic、A17—A20 Pro。首次发布时间与游戏两年供货窗口分开；T760年代、部分2026版本需核实。'
d['versionNote']='6.9只更新批准名单、芯片特色与必要校准，厂标移除供货前缀。继承6.8逐卡研发/伙伴价、技术授权、T21及扩产；不重构。'
d['factoryPresentation']='实际SVG图标＋厂名；无供货前缀、无图形名称'
d.pop('chipCalibration',None)
d['numericTuning']={'inheritedVersion':'6.8','description':'6.8研发两模式逐卡费用/工期、稳定伙伴价全套保留；仅C112新平台入库价改8/2；7个替换芯片数值必要调整。非芯片部件行不改。'}
d['migration']={'from':'6.8','to':'6.9','cardCountChanged':False,'sourceFrozen':True,'chipRoles':len(rows)}
# Different names must not be created by adding kit suffixes; each chip component unique.
chips=[(c,a)for c in d['parts']if c['type']!='starter'for a in c['components']if a['kind']=='chip']
assert len(chips)==50 and len({a['name']for c,a in chips})==50
assert all(next(a for a in c['components']if a['kind']=='chip')['name']==name for cid,name,f in rows for c in [p[cid]])
for key in ('technologies','contracts','facilities','schemes','benchmarks','demands','parameters','expansionRules','researchModes','supplierRules'):
 assert d[key]==old[key],key
(W/'v69_data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Full rulebook remains the same rules: revise only current-version note and explanatory card interfaces.
b=json.loads((S/'v68_rulebook.json').read_text(encoding='utf8'))
b['version']='6.9';b['subtitle']='五十平台与芯片专长'
for sec in b['sections']:
 for x in sec['blocks']:
  for k in ['title','body','aside']:x[k]=x[k].replace('6.8','6.9')
  if x['title'].startswith('5.4'):
   x['body']=x['body'].replace('供应商用图案＋厂名。','供应商只用图案＋厂名，不写“供货”前缀或图形名称。')
  if x['title'].startswith('7.2'):
   x['aside']+=' 芯片卡上的“取得特征”只改产品资格，不抬高部件规格；“可进入某市场”也不自动取得该市场偏好或安全资格。'
  if x['title'].startswith('7.6'):
   x['aside']='50款保留相对能效取舍。骁龙8 Gen 1、猎户座990和骁龙888仍为8负载；T760是低成本补充，不假装旗舰。供货窗口、现实发布时间和游戏等效负载分别记录。'
  if x['title'].startswith('15.3'):
   x['body']='本版保留用户指定40款，补入6款猎户座、2款Google Tensor及2款展锐；共50个唯一主牌芯片。20稳定、30含芯片定制不变，每代4＋6。苹果使用A11—A16 Bionic和A17—A20 Pro完整名称；初始通用芯片另计。\n\n部分改名平台重标芯片行与专长；套装内非芯片部件、研发费用/工期、伙伴待遇（C112新平台除外）、需求、参考、授权和扩产机制保持6.8。\n\n逐卡数字与效果是游戏设计；前瞻型号、家族后缀及T760首发资料缺口明列，不用虚构跑分或采购价填空。表上年份是游戏供货窗口，不构成每款真实首发证明。\n\n测试应观察：新低成本路线能否反击；各芯片专长有无实际可行配套；苹果十代的差异是否容易理解；授权与扩产叠加后有无统治组合。文件、规则情境和配套扫描均不等于多人平衡。'
   x['aside']='芯片名录给出全部50款、卡号、数值、特色与前后差异。没有减少主牌，也不额外增加供应市场。对缺资料的型号保留标识，实际打印机套准仍须试印。'
(W/'v69_rulebook.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
changes=[]
for c in d['parts']:
 prev=op[c['id']];fields={k:{'before':prev.get(k),'after':c.get(k)}for k in set(c)|set(prev)if prev.get(k)!=c.get(k)}
 if fields:changes.append({'id':c['id'],'fields':fields})
(W/'v68_to_v69_changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
print('50-chip mapping complete; renamed',sum(next(a for a in op[cid]['components']if a['kind']=='chip')['name']!=name for cid,name,f in rows),'effect changes',sum(op[cid]['effect']!=p[cid]['effect']for cid,name,f in rows))
