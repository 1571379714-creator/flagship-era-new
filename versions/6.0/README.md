# 旗舰元年6.0 · 产品平台与开放市场

结构重构首测版。不是可混用5.x卡面的补丁；没有固定轮数的发布。完整现行规则在outputs，设计取舍另见规划书。

## 文件入口

- 完整规则书：outputs/旗舰元年_6.0_完整规则书.docx / .pdf（13页）。
- 设计规划书：outputs/旗舰元年_6.0_设计规划书.docx / .pdf（5页）。
- 全卡牌图鉴：outputs/旗舰元年_6.0_全卡牌图鉴.html / .pdf（47页，243种/315张）。
- 线下版图：outputs/旗舰元年_6.0_线下版图.html / .pdf（8视图）。
- 实体组件：outputs/旗舰元年_6.0_实体组件.html / .pdf（7页）。
- 实际修改、检查与未验证范围：outputs/旗舰元年_6.0_修改与校验说明.md。
- 数据与正文：work/v60_data.json、v60_rules.md、v60_planning.md、v60_catalog.md。

HTML自包含，下载到本地用浏览器打开。不是线上游戏，不提供发牌、自动结算或保存对局。成品PDF无需安装任何生成依赖即可阅读打印。

## 当前规则的关键约束

玩家每本人回合分配3工作点；只主动预热推动共同发布，2/3/4人终点12/16/20。收入60或科技30触发最后阶段，全员再各一回合后最终发布，成绩取收入与科技×2较大者。不同于原来的双轨相遇。

参考机每代6款、共30款，准备期开始随机抽一张全桌共用并公开，四市场数值和挑战奖分别印制；低值少奖/无奖，高值多奖。奖励要求严格胜出且真实零售成交，每公司每场一次；科技选项另需首发并部署研发。

型号最多4款；配件和部署持续占用至退市，库存先生产支付、再实际销售。芯片配额不因退市/改款而清零。没有必需P企划、固定上市印刷收入、无债融资、自动回款或集图标项目。

本轮没有向GitHub推送；本地交付不表示main或标签已经变更。旧版5.3保留，source仅为追溯材料，不是本版规则。

## 解压后检查完整性

```sh
python work/verify_delivery.py
```

此命令只用Python标准库；根据delivery_manifest.json核对原交付文件。如果自行修改或重新生成，哈希改变属于预期，不再是原始快照。

## 重建

Python3.10或以上，安装requirements.txt，并安装系统LibreOffice与中文字体。HTML/PDF导出使用Chromium；可设置FLAGSHIP_CHROMIUM为可执行文件绝对路径，或运行playwright安装浏览器。字体没有随包分发。

```sh
python -m pip install -r requirements.txt
python -m playwright install chromium
python work/build_all.py
python work/validate.py
python work/audit_artifacts.py
```

build_all只读取当前JSON/Markdown导出，不运行迁移。`--no-pdf`可只导出Word/HTML。work/make_data.py是从5.3重新创建数据的初次迁移/写作脚本，会覆盖手改JSON，不应作为日常构建入口。Word、LibreOffice、字体或Chromium版本不同可能改变分页；交付PDF为固定成品。

## 测试与印刷

validation_v60.json为定向数学/规则情境，不是完整游戏模拟。artifact_checks_v60.json为本轮文件检查，visual_review_v60.json记录人工检查范围。任何完整卡牌特效组合、多人平衡、实际时长和打印机套准均未声称验证。

价格页1—2长边双面，每人一套16张；其他组件单面。版图型号页每人按需重复四份；可把卡摆在对应区旁，不需要把完整卡缩小塞进展示槽。先试印，不含全卡统一卡背/出血/刀模。

本包没有指定新的开放使用许可，字体、外部商标与旧原版资料不因整理归档自动获得额外授权。
