#!/usr/bin/env python3
"""Create a PRIVATE GitHub repo and import the exact prepared baseline.

Default is local-only verification. --execute requires Git, GitHub CLI and an
interactive confirmation. Authentication stays with the user's local `gh`.
No tokens are read, printed, embedded in URLs or uploaded by this script.
Existing unrelated repositories, public repositories and non-fast-forward
updates are rejected. The script never changes remote visibility or force-pushes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from verify_archive import ROOT, verify, verify_manifest

DEFAULT_OWNER = '1571379714-creator'
DESCRIPTION = '旗舰元年 / Flagship Era — 手机公司经营德式桌游，5.0起的完整规则、卡组、版图与设计记录'
TAG = 'v5.0'
STATE = ROOT / '.publish-state.json'


class ImportErrorSafe(RuntimeError):
    pass


def command(args: list[str], *, check: bool = True, capture: bool = True,
            cwd: Path = ROOT, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(args, cwd=cwd, text=True, encoding='utf-8', errors='replace',
                        capture_output=capture, timeout=timeout, check=False)
    if check and cp.returncode:
        detail = ((cp.stderr or '') + '\n' + (cp.stdout or '')).strip()
        raise ImportErrorSafe(f'命令失败（退出码 {cp.returncode}）：{args[0]} {args[1]}\n{detail}')
    return cp


def api(gh: str, endpoint: str) -> dict[str, Any] | None:
    cp = command([gh, 'api', '--hostname', 'github.com', endpoint], check=False)
    if cp.returncode:
        # Only an explicit HTTP 404 means missing. Never treat network/403 errors as empty.
        if 'HTTP 404' in (cp.stderr or ''):
            return None
        raise ImportErrorSafe('GitHub查询失败，未把它当作空仓库：\n' + (cp.stderr or cp.stdout or ''))
    try:
        value = json.loads(cp.stdout)
    except json.JSONDecodeError as e:
        raise ImportErrorSafe('GitHub未返回可解析的JSON。') from e
    if not isinstance(value, dict):
        raise ImportErrorSafe('GitHub返回了意外结构。')
    return value


def check_remote(meta: dict[str, Any], target: str) -> None:
    if meta.get('full_name', '').lower() != target.lower():
        raise ImportErrorSafe('返回的仓库身份与目标不一致，停止。')
    if meta.get('private') is not True:
        raise ImportErrorSafe('目标仓库不是私有仓库；停止，不上传设计，也不擅自更改可见性。')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='实际创建/上传；缺省仅校验本地文件')
    parser.add_argument('--owner', default=DEFAULT_OWNER, help='必须等于当前gh登录账号；不自动转入组织')
    parser.add_argument('--name', default='flagship-era', help='新仓库名；发生同名冲突时可另取名称')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})', args.owner):
        raise ImportErrorSafe('账号名格式无效。')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', args.name):
        raise ImportErrorSafe('仓库名格式无效。')
    target = f'{args.owner}/{args.name}'
    stats = verify(ROOT)
    expected_files = verify_manifest(ROOT, 'repository_manifest.json')
    expected_files.append('repository_manifest.json')
    manifest_digest = hashlib.sha256((ROOT/'repository_manifest.json').read_bytes()).hexdigest()
    print(f'本地基线已核验：{stats["original_files"]}个原始文件，{stats["card_designs"]}种内容牌。')
    print(f'目标：{target}；可见性：PRIVATE；上传{len(expected_files)}个文件；不修改5.0规则。')
    if not args.execute:
        print('仅检查本地文件。尚未登录、创建远程仓库或上传。')
        print('实际执行：python tools/publish_github.py --execute')
        return 0

    git = shutil.which('git')
    gh = shutil.which('gh')
    if not git or not gh:
        missing = ', '.join(name for name, found in [('Git',git),('GitHub CLI',gh)] if not found)
        raise ImportErrorSafe(f'缺少 {missing}。请按 docs/github-import.md 安装并重新打开终端。尚未创建远程仓库。')
    state: dict[str, Any] = {}
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding='utf-8'))
        if state.get('target') != target or state.get('manifest_sha256') != manifest_digest:
            raise ImportErrorSafe('发现另一次导入状态或文件已改变。停止；请使用新的解压副本，勿覆盖既有历史。')
    print('将创建新的私有仓库（或继续本包上次中断的导入），提交并推送main和v5.0标签。')
    print('登录由本机GitHub CLI打开官方浏览器流程；不需要将密码或Token发给任何人。')
    if input(f'确认目标 {target} 后，输入 CREATE 继续：').strip() != 'CREATE':
        print('已取消；未创建或上传。')
        return 0

    auth = command([gh, 'auth', 'status', '--hostname', 'github.com'], check=False)
    if auth.returncode:
        command([gh, 'auth', 'login', '--hostname', 'github.com', '--git-protocol', 'https', '--web'],
                capture=False, timeout=1200)
    user = api(gh, 'user')
    if not user or str(user.get('login', '')).lower() != args.owner.lower():
        actual = user.get('login', '(unknown)') if user else '(unknown)'
        raise ImportErrorSafe(f'当前gh账号为 {actual}，与预期 {args.owner} 不符。请在本地切换正确账号后重试。')
    login, user_id = str(user['login']), int(user['id'])

    # A repository already visible without this import's state must not be hijacked.
    meta = api(gh, f'repos/{target}')
    if meta is not None:
        check_remote(meta, target)
        if not state.get('remote_created'):
            raise ImportErrorSafe('同名仓库已存在，未覆盖或上传。请另选新名称：--name flagship-era-design。')
    elif state.get('remote_created'):
        raise ImportErrorSafe('上次已创建的仓库本次无法读取，停止；不重新创建或推送。')

    # Refuse to operate inside an unrelated or enclosing repository.
    top = command([git, 'rev-parse', '--show-toplevel'], check=False)
    if top.returncode == 0:
        if Path(top.stdout.strip()).resolve() != ROOT.resolve():
            raise ImportErrorSafe('本包位于另一个Git仓库中，停止。请解压到独立目录。')
        if not state.get('local_ready'):
            raise ImportErrorSafe('目录已有Git历史但不属于本工具的导入，停止。')
    else:
        if state.get('local_ready') or (ROOT/'.git').exists():
            raise ImportErrorSafe('本地Git状态与导入记录不一致，停止。')
        command([git, 'init', '-b', 'main'])

    if not state.get('local_ready'):
        for offset in range(0, len(expected_files), 25):
            command([git, '-c', 'core.autocrlf=false', 'add', '--', *expected_files[offset:offset+25]])
        # Use a GitHub no-reply identity for this commit only; leave global config untouched.
        identity = ['-c', f'user.name={login}', '-c', f'user.email={user_id}+{login}@users.noreply.github.com',
                    '-c', 'commit.gpgsign=false']
        command([git, *identity, 'commit', '-m', 'chore: archive Flagship Era 5.0 and design decisions'])
        command([git, '-c', 'tag.gpgsign=false', 'tag', TAG])
        local_sha = command([git, 'rev-parse', 'HEAD']).stdout.strip()
        state = {'target':target, 'manifest_sha256':manifest_digest, 'local_ready':True,
                 'local_commit':local_sha, 'remote_created':False, 'uploaded':False}
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    else:
        local_sha = command([git, 'rev-parse', 'HEAD']).stdout.strip()
        if local_sha != state.get('local_commit'):
            raise ImportErrorSafe('本地提交已变化；初次导入工具不会处理后续开发历史。')
        if command([git, 'diff', '--name-only', 'HEAD']).stdout.strip():
            raise ImportErrorSafe('本地存在已跟踪文件改动，停止。')
    if command([git, 'branch', '--show-current']).stdout.strip() != 'main':
        raise ImportErrorSafe('当前分支不是main，停止。')
    if command([git, 'rev-parse', TAG]).stdout.strip() != local_sha:
        raise ImportErrorSafe('v5.0标签不指向本次基线提交，停止。')
    tracked = set(command([git, 'ls-files', '-z']).stdout.rstrip('\x00').split('\x00'))
    if tracked != set(expected_files):
        raise ImportErrorSafe('Git跟踪清单与预期文件不一致，停止。')

    if meta is None:
        command([gh, 'repo', 'create', target, '--private', '--disable-wiki', '--description', DESCRIPTION],
                capture=False, timeout=180)
        # Record immediately, so a visibility read failure can be retried safely.
        state['remote_created'] = True
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    meta = api(gh, f'repos/{target}')
    if meta is None:
        raise ImportErrorSafe('创建后暂时无法读取仓库；尚未上传。请检查账号/网络后重试。')
    check_remote(meta, target)
    origin = f'https://github.com/{target}.git'
    existing_origin = command([git, 'remote', 'get-url', 'origin'], check=False)
    if existing_origin.returncode == 0:
        if existing_origin.stdout.strip() != origin:
            raise ImportErrorSafe('已有origin不是预期目标，不更换远端。')
    else:
        command([git, 'remote', 'add', 'origin', origin])

    # Only this push uses gh as the credential helper. Do not write global Git settings.
    gh_path = Path(gh).as_posix().replace('"', '\\"')
    helper = f'!"{gh_path}" auth git-credential'
    command([git, '-c', 'credential.helper=', '-c', 'credential.https://github.com.helper=',
             '-c', f'credential.https://github.com.helper={helper}',
             'push', '--atomic', '--set-upstream', 'origin', 'main:main', f'refs/tags/{TAG}:refs/tags/{TAG}'],
            capture=False, timeout=900)

    head = api(gh, f'repos/{target}/git/ref/heads/main')
    tag = api(gh, f'repos/{target}/git/ref/tags/{TAG}')
    if not head or not tag or head['object']['sha'] != local_sha or tag['object']['sha'] != local_sha:
        raise ImportErrorSafe('推送后远端提交/标签与本地不一致；未标为验证完成。')
    remote_commit = api(gh, f'repos/{target}/git/commits/{local_sha}')
    local_tree = command([git, 'rev-parse', 'HEAD^{tree}']).stdout.strip()
    if not remote_commit or remote_commit['tree']['sha'] != local_tree:
        raise ImportErrorSafe('远端树哈希与本地不一致。')
    check_remote(api(gh, f'repos/{target}') or {}, target)
    state['uploaded'] = True
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    result = {'status':'uploaded_and_verified', 'repository':target, 'private':True,
              'commit':local_sha, 'tree':local_tree, 'tag':TAG, 'files':len(expected_files),
              'url':meta['html_url']}
    (ROOT/'.publish-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('\n完成：已创建私有仓库，上传文件，并核对远端提交、标签及完整文件树。')
    print(result['url'])
    print('提交：'+local_sha)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ImportErrorSafe, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print('\n停止：'+str(exc), file=sys.stderr)
        print('没有执行强制推送或删除操作；本地原始5.0仍保留。中断并不表示已上传成功。', file=sys.stderr)
        raise SystemExit(1)
    except (KeyboardInterrupt, EOFError):
        print('\n已中止。没有报告远端上传成功。', file=sys.stderr)
        raise SystemExit(130)
