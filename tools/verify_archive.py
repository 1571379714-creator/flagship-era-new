#!/usr/bin/env python3
"""Verify unchanged 5.0 archive bytes and basic baseline structure (not game balance)."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parent.parent
FONT_EXTENSIONS = {'.ttf', '.otf', '.ttc', '.woff', '.woff2'}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe_path(root: Path, value: str) -> Path:
    rel = PurePosixPath(value)
    if not value or rel.is_absolute() or '..' in rel.parts or '\\' in value:
        raise ValueError(f'Unsafe manifest path: {value!r}')
    p = root.joinpath(*rel.parts)
    if p.is_symlink() or root.resolve() not in p.resolve().parents:
        raise ValueError(f'Symlink or out-of-root path: {value!r}')
    if p.suffix.lower() in FONT_EXTENSIONS:
        raise ValueError(f'Font binaries must not be distributed: {value}')
    return p


def verify_manifest(root: Path, manifest_name: str) -> list[str]:
    manifest = json.loads((root / manifest_name).read_text(encoding='utf-8'))
    entries = manifest['files']
    paths: list[str] = []
    for row in entries:
        rel = row['path']
        if rel in paths:
            raise ValueError(f'Duplicate manifest entry: {rel}')
        p = safe_path(root, rel)
        if not p.is_file():
            raise ValueError(f'Missing file: {rel}')
        if p.stat().st_size != row['bytes'] or sha256(p) != row['sha256']:
            raise ValueError(f'Content differs from archived baseline: {rel}')
        paths.append(rel)
    return paths


def verify(root: Path = ROOT) -> dict[str, int]:
    files = verify_manifest(root, 'archive_manifest.json')
    base = root / 'versions/5.0'
    d = json.loads((base / 'work/v50_data.json').read_text(encoding='utf-8'))
    if d['version'] != '5.0' or (root / 'VERSION').read_text().strip() != '5.0':
        raise ValueError('This first-import verifier expects version 5.0.')
    cards = [c for key in ('cards','parts','starters','projects','specialProjects','goals') for c in d[key]]
    ids = [c['id'] for c in cards]
    physical = sum(c.get('qty', 1) for c in cards)
    if len(ids) != len(set(ids)) or len(ids) != 302 or physical != 374:
        raise ValueError('Card IDs, designs or physical counts do not match 5.0.')
    track = d['scoreTrack']
    alignment = track['alignment']
    if track['incomeMax'] != 100 or track['technologyMax'] != 36 or len(alignment) != 37:
        raise ValueError('Track shape differs from the confirmed 5.0 baseline.')
    if alignment[0] != 100 or alignment[-1] != 0:
        raise ValueError('Unexpected endpoints.')
    if any(alignment[t - 1] - alignment[t] != (2 if t <= 8 else 3) for t in range(1, 37)):
        raise ValueError('The first 8 steps must span 2 income spaces; later steps span 3.')
    if {f['id'] for f in d['factories']} != {'R','Y','B','G','K'}:
        raise ValueError('Manufacturer dimensions differ from 5.0.')
    return {'original_files': len(files), 'card_designs': len(ids), 'physical_cards': physical}


if __name__ == '__main__':
    try:
        print(json.dumps(verify(), ensure_ascii=False, indent=2))
        print('PASS: archive integrity and baseline structure only; no multiplayer validation.')
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f'FAILED: {e}', file=sys.stderr)
        raise SystemExit(1)
