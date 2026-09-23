from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
def text():
 b=json.loads((R/'work/v69_rulebook.json').read_text(encoding='utf8'));lines=['# 旗舰元年','## 6.9 完整规则书','五十平台与芯片专长 · 2—4人 · 测试版']
 for s in b['sections']:
  lines += ['','## '+s['number']+' '+s['title'],s['intro']]
  for x in s['blocks']:lines+=['','### '+x['title'],x['body'],'','> 【侧栏：'+x['asideKind']+'】'+x['aside'].replace('\n','\n> ')]
 return '\n\n'.join(lines)+'\n'
def check():
 if (R/'work/v69_rules.md').read_text(encoding='utf8')!=text():raise ValueError('正文与规则JSON不同；先确定哪份修改正确，再同步。')
if __name__=='__main__':
 (R/'work/v69_rules.md').write_text(text(),encoding='utf8')
