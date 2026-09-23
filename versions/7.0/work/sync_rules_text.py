from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def text():
 b=json.loads((R/'work/v70_rulebook.json').read_text());lines=['# 旗舰元年7.0 完整规则书','双行排程与世代竞逐 · 2026年9月23日']
 for s in b['sections']:
  lines+=['\n## '+s['number']+' '+s['title'],s['intro']]
  for x in s['blocks']:lines+=['\n### '+x['title'],x['body'],'\n> '+x['asideKind']+'：'+x['aside'].replace('\n','\n> ')]
 return '\n\n'.join(lines)+'\n'
def check():
 if (R/'work/v70_rules.md').read_text()!=text():raise ValueError('正文与结构化规则不一致')
if __name__=='__main__':check()
