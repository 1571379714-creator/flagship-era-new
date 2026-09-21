# 旗舰元年 · Flagship Era

**手机公司经营主题的大型德式桌游｜当前归档基线：6.2「统一牌流与单批产品」结构简化测试版**

6.2 基于 6.1 交付底稿重构为统一主牌流与单批产品：稳定、定制、研发、合同、设施与产品方案使用同一主牌堆；每次组装只形成一批现货，未售批次原样留存。它不是可与 6.0 或更早版本卡牌混用的补丁。

适合 2—4 人。6.2 仍未完成充分多人实桌平衡验证，游戏时长也未实测确认。

## 从这里开始

| 内容 | 文件 |
| --- | --- |
| 6.2 完整规则 | [PDF](versions/6.2/outputs/旗舰元年_6.2_完整规则书.pdf) · [Word](versions/6.2/outputs/旗舰元年_6.2_完整规则书.docx) · [HTML](versions/6.2/outputs/旗舰元年_6.2_完整规则书.html) · [Markdown 正文](versions/6.2/work/v62_rules.md) |
| 6.2 设计规划 | [PDF](versions/6.2/outputs/旗舰元年_6.2_设计规划书.pdf) · [Word](versions/6.2/outputs/旗舰元年_6.2_设计规划书.docx) · [Markdown 正文](versions/6.2/work/v62_planning.md) |
| 6.2 全卡牌图鉴 | [PDF](versions/6.2/outputs/旗舰元年_6.2_全卡牌图鉴.pdf) · [HTML](versions/6.2/outputs/旗舰元年_6.2_全卡牌图鉴.html) · [文字图鉴](versions/6.2/work/v62_catalog.md) |
| 6.2 主牌与参考机打印件 | [统一主牌 PDF](versions/6.2/outputs/旗舰元年_6.2_统一主牌正反面.pdf) · [参考机 PDF](versions/6.2/outputs/旗舰元年_6.2_参考机正反面.pdf) · [打印说明](versions/6.2/PRINTING.md) |
| 6.2 版图与实体组件 | [版图 PDF](versions/6.2/outputs/旗舰元年_6.2_线下版图.pdf) · [实体 PDF](versions/6.2/outputs/旗舰元年_6.2_实体组件.pdf) |
| 6.2 数据与交付记录 | [数据 JSON](versions/6.2/work/v62_data.json) · [规则源 JSON](versions/6.2/work/v62_rulebook.json) · [交付说明](versions/6.2/outputs/旗舰元年_6.2_修改与校验说明.md) · [交付清单](versions/6.2/delivery_manifest.json) |
| 历史快照 | [6.0](versions/6.0/) · [5.0](versions/5.0/) |

HTML 用于本地查阅和打印，不是电子游玩系统；它不提供自动发牌、对局结算或存档。

## 6.2 的核心结构

- 一套 257 张主牌与 8 张牌市；稳定、定制、研发、合同、设施和方案从开局进入同一牌流。
- 稳定与定制牌可免费取得；稳定进库时才支付入库费，任一现存产品引用都会锁定该库栏。
- 每次组装为一批现货、占一个产品位；一批只能投一个零售市场、一张合同或留库，未售配置原样等待。
- 保留每位玩家每回合 3 工作点、玩家主动推动发布，以及收入 60 或科技 30 触发最后阶段的双路线结算。
- 参考机在全员锁价和投放后随机抽取并保留；科技和工程奖励检查已部署完成研发。

完整 6.2 卡组为 **243 种设计、315 张实体内容牌**；其中主牌打印件已展开为 257 张副本。具体规则、卡面与实体准备以 6.2 归档文件为准。

## 文件组织

```text
versions/6.2/        6.2 原始交付快照：规则、规划、打印件、卡组、版图、组件、数据与校验
versions/6.0/        6.0 原始交付快照
versions/5.0/        5.0 原始交付快照
docs/design/         5.0 历史设计记录；不替代当前版本的规划书
docs/playtesting/    试玩计划与记录模板
.github/             Issue 与 PR 模板
AGENTS.md            后续协作者与 AI 代理的版本边界和操作约束
CHANGELOG.md         仓库版本记录
VERSION              当前归档游戏版本
```

各历史版本及其 `source/` 内资料仅作追溯，不能与 6.2 卡牌或规则混用。

## 校验与重建

`versions/6.2/delivery_manifest.json` 记录 6.2 原始交付的文件、字节数和 SHA-256。阅读或打印已有成品无需重建。若要重新导出，请在独立工作分支或副本中操作，并先阅读 [6.2 README](versions/6.2/README.md)。

修改规则源后，先同步 Markdown 再导出。`work/migrate_v62.py` 与 `work/write_rulebook.py` 是初次迁移/写作记录，会覆盖手改内容，不能作为日常构建命令。重建还需 Chromium、LibreOffice 与中文字体，且不同环境可能改变 PDF 分页。

## 协作约定

设计讨论、已确认规则和未验证参数必须分开记录。没有明确修改授权时只讨论，不修改规则或生成新版；已发布的版本快照必须保留不动。未经明确授权，不得改变仓库可见性、添加许可或上传字体、凭据、个人备份及无关聊天内容。
