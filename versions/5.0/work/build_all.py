"""用已有5.0 JSON/MD重建成品，不回滚用户手改数据。"""
from pathlib import Path
import argparse,os,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent.parent;WORK=ROOT/'work';OUT=ROOT/'outputs';QA=ROOT/'qa';QA.mkdir(exist_ok=True)
def run(script):subprocess.run([sys.executable,str(WORK/script)],check=True,cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--render-only',action='store_true',help='跳过已完成的HTML/DOCX生成');args=p.parse_args()
 if not args.render_only:
  run('build_v50.py');run('boards_and_aids_v50.py');run('validate_v50.py')
 lo=os.environ.get('LIBREOFFICE_PATH') or shutil.which('libreoffice') or shutil.which('soffice')
 if not lo:raise SystemExit('未找到LibreOffice。请安装，或设置LIBREOFFICE_PATH为soffice可执行文件路径。')
 if 'CHROMIUM_PATH' not in os.environ:
  browser=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
  if browser:os.environ['CHROMIUM_PATH']=browser
 target=QA/'rulebook_render';target.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='flagship_lo_') as profile:
  subprocess.run([lo,'-env:UserInstallation='+Path(profile).as_uri(),'--headless','--convert-to','pdf','--outdir',str(target),str(OUT/'旗舰元年_5.0_完整规则书.docx')],check=True,timeout=180)
 result=target/'旗舰元年_5.0_完整规则书.pdf'
 if not result.exists():raise SystemExit('LibreOffice未生成规则PDF，请检查中文字体与文档。')
 run('export_v50.py');run('check_artifacts_v50.py');run('make_release_notes_v50.py')
 print('已生成并检查5.0交付物。规则文字/卡牌改动仍须人工复核与多人试玩。')
if __name__=='__main__':main()
