"""Verify the extracted delivery without render dependencies."""
from pathlib import Path
import hashlib, json, sys
root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "delivery_manifest.json").read_text(encoding="utf-8"))
errors = []
for item in manifest["files"]:
    path = (root / item["path"]).resolve()
    if not path.is_relative_to(root.resolve()):
        errors.append("Unsafe path: " + item["path"])
        continue
    if not path.is_file():
        errors.append("Missing: " + item["path"])
        continue
    raw = path.read_bytes()
    if len(raw) != item["bytes"] or hashlib.sha256(raw).hexdigest() != item["sha256"]:
        errors.append("Changed: " + item["path"])
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"Verified {len(manifest['files'])} files against the original delivery manifest.")
