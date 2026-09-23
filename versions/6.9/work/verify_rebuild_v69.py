"""在干净副本中重建，比较HTML字节与PDF页数/文字，不比较PDF时间戳。"""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys, tempfile
import fitz

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    dst = args.destination or Path(tempfile.mkdtemp(prefix='flagship69-rebuild-'))
    dst = dst.resolve()
    if dst == ROOT or ROOT in dst.parents:
        raise ValueError('重建目录必须独立于当前交付目录')
    dst.mkdir(parents=True, exist_ok=True)
    if any(dst.iterdir()):
        raise ValueError('重建目录必须为空，拒绝覆盖已有内容')
    for folder in ('work', 'assets', 'source'):
        (dst / folder).mkdir()
        for path in (ROOT / folder).iterdir():
            if not path.is_file():
                continue
            if folder != 'work' or path.suffix == '.py' or path.name.startswith('v69_'):
                shutil.copy2(path, dst / folder / path.name)
    (dst / 'outputs').mkdir()
    (dst / 'qa').mkdir()
    proc = subprocess.run([sys.executable, str(dst / 'work/build_all.py')], text=True, capture_output=True, timeout=240)
    (ROOT / 'qa/rebuild.log').write_text(proc.stdout + proc.stderr, encoding='utf-8')
    if proc.returncode:
        raise RuntimeError('重建失败，查看qa/rebuild.log')
    records, errors = [], []
    for path in sorted((ROOT / 'outputs').iterdir()):
        other = dst / 'outputs' / path.name
        if path.suffix not in ('.pdf', '.html'):
            continue
        record = {'name': path.name, 'kind': path.suffix, 'exists': other.is_file()}
        if not other.is_file():
            errors.append(path.name + ': missing')
        elif path.suffix == '.html':
            record['identicalBytes'] = path.read_bytes() == other.read_bytes()
            record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            if not record['identicalBytes']:
                errors.append(path.name + ': HTML differs')
        else:
            with fitz.open(path) as one, fitz.open(other) as two:
                record['pages'] = len(one)
                record['samePageCount'] = len(one) == len(two)
                record['identicalPageText'] = record['samePageCount'] and all(a.get_text() == b.get_text() for a, b in zip(one, two))
            if not record['identicalPageText']:
                errors.append(path.name + ': PDF page text differs')
        records.append(record)
    result = {'version':'6.9', 'independentBuild':True, 'files':records, 'errors':errors,
              'scope':'HTML字节、PDF页数与逐页文字相同；不宣称PDF二进制逐字节相同。'}
    (ROOT/'work/rebuild_audit_v69.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'checkedFiles':len(records), 'errors':errors}, ensure_ascii=False))
    if errors:
        raise RuntimeError('重建对照未通过')

if __name__ == '__main__':
    main()
