"""Verify immutable delivery hashes before locally modifying or rebuilding the package."""
from pathlib import Path
import hashlib
import json
import sys

def main() -> int:
    root=Path(__file__).resolve().parents[1]
    manifest=root/'SHA256.json'
    if not manifest.is_file():
        print('Missing SHA256.json. Extract the complete package first.'); return 2
    hashes=json.loads(manifest.read_text(encoding='utf-8'))
    failures=[]
    for relative,expected in hashes.items():
        path=(root/relative).resolve()
        if root not in path.parents or not path.is_file():
            failures.append(relative+': missing or outside package'); continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            failures.append(relative+': changed')
    print(f'Checked {len(hashes)} files; mismatches: {len(failures)}')
    for issue in failures:print(issue)
    return 1 if failures else 0

if __name__=='__main__':sys.exit(main())
