# 旗舰元年 6.9 · 五十平台与芯片专长

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
