# 旗舰元年 7.0 · 双行排程与世代竞逐

2–4人手机公司经营桌游，结构首测版。以实际6.9归档迁移，不覆盖历史版本。尚未充分多人实测，不承诺固定时长或每代恰好两次发布。

先读 `outputs/旗舰元年_7.0_完整规则书.pdf`；印制见 `outputs/旗舰元年_7.0_打印与实体准备.md`。完整图鉴315种；主牌257张＋初始16＋参考30＋需求12；另每人6张行动，不算内容牌。

- `work/v70_data.json`：所有内容牌与通用参数，唯一现行数据。
- `work/v70_rulebook.json`：结构化正文与例子侧栏。
- `work/v70_rules.md`：由同一正文同步的易读文字。
- `work/v70_planning.md`：设计取舍。
- `source/`：原6.9只读基线与哈希；不是现行规则。
- `outputs/`：完整规则、图鉴、制卡、行动、版图、组件、校准及说明。
- `qa/`：本轮实际日志；页图仅用于内部检查，交付包不包含大量预览图。

## 从本目录重建

需要 Python 3.12+、pip依赖、LibreOffice、Chromium、Noto Sans/Serif CJK SC等中文字体。字体不随包分发。Linux示例：

```sh
pip install -r requirements.txt
python -m playwright install chromium
python work/sync_rules_text.py --check
python work/build_all.py
python -m unittest discover -s work -p 'test*70.py' -v
python work/check_components_v70.py
python work/pace_analysis_v70.py
python work/check_layout.py
python work/write_reports_v70.py
```

`build_all.py --no-pdf`只导出HTML/DOCX。构建器只读取现行v70数据，**不会运行迁移脚本**。

`migrate_v70.py`与`write_rules_v70.py`仅为6.9→7.0初次迁移记录，日常编辑现行JSON后不要再运行它们，否则会覆盖手改。`make_review_sheets.py`生成视觉检查缩略图，不属于游戏组件。

测试分为规则单元、有限市场情境、条件配置见证和显式输入的节奏预算。没有完整多人AI游戏引擎，不以静态情境数量冒充对局数。实际完整覆盖和不足见交付核对记录。

本次不执行GitHub操作；用户自行上传。HTML只展示、切换和打印，不能发牌、自动裁定或保存对局。
