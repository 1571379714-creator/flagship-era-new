# 旗舰元年6.2 · 统一牌流与单批产品

实际底稿：用户6.1交付包。状态：结构简化测试版，不是充分实测的平衡发行版。本包未推送GitHub，原6.1不覆盖。

## 内容入口
- 完整规则：outputs/旗舰元年_6.2_完整规则书.docx、PDF与HTML。16页，13章，41段正文与41个侧栏；正文是规则，侧栏是示例。
- 全卡图鉴：50页、243设计/315实体；完整数值不是节选。
- 主牌制卡：257张已展开副本，63×88毫米、共同卡背，58页正反；不要再按×2重复整套。
- 参考机：10页配对正反；需求与初始卡见图鉴及PRINTING.md。
- 版图：8个静态视图；实体组件：11页。
- 规划和修改：outputs下设计规划书、修改与校验说明、打印与实体准备。

## 现行源文件
work/v62_data.json 是卡面及系统参数；work/v62_rulebook.json 是含侧栏的规则源；work/v62_rules.md 为同步文本；work/v62_planning.md 为设计说明。source/保存6.1输入用于追溯，不能混用旧卡。

## 修改与导出
从当前文件继续编辑，不从聊天摘要重造卡牌。改了rulebook.json后先同步Markdown，再导出。不要运行migrate_v62.py或write_rulebook.py覆盖手改内容；它们只是初次迁移/写作的记录。

```bash
python -m pip install -r requirements.txt
python work/sync_rules_text.py
python work/build_all.py
python work/validate_v62.py
python work/check_layout.py
python work/audit_artifacts.py
```

导出DOCX/PDF需要LibreOffice、Chromium和本机中文字体。Chromium路径可由FLAGSHIP_CHROMIUM设置；本包未分发任何字体文件。HTML自包含，无需服务器，仅查阅/切换/打印，不提供自动发牌、对局结算或存档。排版跨机器可能改变分页，固定PDF为本次交付页数。

初次迁移脚本与成品构建职责不同；build_all.py不改变卡牌设计。tests里的rules_core.py是有限状态测试模型，不是可玩的电子桌游；没有完整特效解释器或AI对手。

## 关键裁定
拿稳定/定制免费入手，稳定安装才付款；四类各一栏，任何现存代理引用阻止替换。组装一次就是一批。未售原样等待，取消回件不退款，成交后整场整理才释放。未来配件可入库不可使用。收入/科技双路线、玩家推动发布、锁定后随机参考保留。

本轮首测值：非初始入库9、组装费8、总费最低6，取牌1工作拿2，开局抽8留5。单批化可能影响路线速度，不宣称90—150分钟已经达成。

## 校验记录
work/validation_v62.json、artifact_audit_v62.json、layout_audit.json记录本次程序检查；visual_review_v62.json说明视觉范围；rebuild_v62.json说明独立副本重建。delivery_manifest.json逐文件记录字节数及SHA256。
原图鉴、组件和主牌制卡都是可测试排版，不是商业量产出血刀模稿。真实打印机套准、全卡联动、隐藏信息策略和真人多人平衡尚待验证。
