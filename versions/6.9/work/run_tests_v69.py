from pathlib import Path
import unittest,json,io
R=Path(__file__).resolve().parents[1]
log=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromNames(['test_v69','test_expansion_v69','test_roster_v69']);res=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
(R/'qa/unit_tests.log').write_text(log.getvalue(),encoding='utf8')
report={'version':'6.9','testsRun':res.testsRun,'failures':len(res.failures),'errors':len(res.errors),'success':res.wasSuccessful(),'inheritedTests':77,'newRosterAndAbilityTests':39,'inheritedAdaptations':['原数值断言每代稳定规格差≤3改为≤4，体现获批的低价T760；非玩家规则','输入快照路径改为当前6.8源；其余无关字段继续检查不变'],'includedScenarios':{'singleMarket':600,'fourMarketExpansion':1200},'notWholeGames':True,'limitations':['模型仅解释声明支持的配件和部分研发数值','合同与设施复杂前置在定向测试中由夹具给出','不模拟实际拿牌路径、完整策略、胜率或实际印刷']}
(R/'work/test_results_v69.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if not res.wasSuccessful():raise SystemExit(1)
