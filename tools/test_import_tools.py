"""Offline tests. The successful upload scenario uses a fake remote, not GitHub."""
from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import publish_github as p
from verify_archive import safe_path, verify


class ImportToolTests(unittest.TestCase):
    def test_original_archive(self):
        result = verify()
        self.assertEqual(result, {'original_files':54, 'card_designs':302, 'physical_cards':374})

    def test_traversal_rejected(self):
        for value in ['../secret','/outside','folder/../../secret','folder\\secret']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                safe_path(p.ROOT, value)

    def test_fonts_rejected(self):
        for ext in ['ttf','otf','ttc','woff','woff2']:
            with self.subTest(ext=ext), self.assertRaises(ValueError):
                safe_path(p.ROOT, 'assets/font.'+ext)

    def test_public_repo_rejected(self):
        with self.assertRaises(p.ImportErrorSafe):
            p.check_remote({'full_name':'owner/repo','private':False},'owner/repo')

    def test_wrong_repo_rejected(self):
        with self.assertRaises(p.ImportErrorSafe):
            p.check_remote({'full_name':'owner/another','private':True},'owner/repo')

    def test_read_404_is_missing(self):
        cp = subprocess.CompletedProcess([],1,'','gh: Not Found (HTTP 404)')
        with patch.object(p,'command',return_value=cp):
            self.assertIsNone(p.api('gh','repos/owner/repo'))

    def test_permission_and_network_errors_not_missing(self):
        for error in ['HTTP 403','connection refused','request timeout','HTTP 401']:
            cp = subprocess.CompletedProcess([],1,'',error)
            with self.subTest(error=error), patch.object(p,'command',return_value=cp):
                with self.assertRaises(p.ImportErrorSafe):
                    p.api('gh','repos/owner/repo')

    def test_default_does_no_network_or_git(self):
        with patch.object(sys,'argv',['publish_github.py']), patch.object(p,'command') as cmd:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(p.main(),0)
            cmd.assert_not_called()

    def test_missing_dependencies_stops_before_confirmation(self):
        with patch.object(sys,'argv',['publish_github.py','--execute']), patch.object(p.shutil,'which',return_value=None):
            with patch('builtins.input') as inp, contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(p.ImportErrorSafe): p.main()
                inp.assert_not_called()

    def test_isolated_success_and_retry_use_fake_remote(self):
        real_root = p.ROOT
        git = shutil.which('git')
        if not git: self.skipTest('Git missing; isolated import test requires local Git')
        with tempfile.TemporaryDirectory() as td:
            target_root=Path(td)/'flagship-era'
            shutil.copytree(real_root,target_root,ignore=shutil.ignore_patterns('__pycache__','.git','.publish-state.json','.publish-result.json'))
            remote={'exists':False,'head':None,'tag':None,'tree':None}
            calls=[]
            def fake_api(gh,endpoint):
                if endpoint=='user':return {'login':p.DEFAULT_OWNER,'id':256153459}
                if endpoint==f'repos/{p.DEFAULT_OWNER}/flagship-era':
                    return {'full_name':f'{p.DEFAULT_OWNER}/flagship-era','private':True,
                            'html_url':f'https://github.com/{p.DEFAULT_OWNER}/flagship-era'} if remote['exists'] else None
                if endpoint.endswith('/git/ref/heads/main'):return {'object':{'sha':remote['head']}}
                if endpoint.endswith('/git/ref/tags/v5.0'):return {'object':{'sha':remote['tag']}}
                if '/git/commits/' in endpoint:return {'tree':{'sha':remote['tree']}}
                self.fail('Unexpected remote read: '+endpoint)
            def fake_command(args,*,check=True,capture=True,cwd=None,timeout=180):
                calls.append(args)
                if args[0]=='FAKE_GH':
                    if args[1:3]==['repo','create']:
                        self.assertIn('--private',args);remote['exists']=True
                    elif args[1:3]!=['auth','status']:
                        self.fail('Unexpected gh call')
                    return subprocess.CompletedProcess(args,0,'','')
                if 'push' in args:
                    self.assertNotIn('--force',args);self.assertIn('--atomic',args)
                    remote['head']=subprocess.check_output([git,'rev-parse','HEAD'],cwd=target_root,text=True).strip()
                    remote['tag']=subprocess.check_output([git,'rev-parse','v5.0'],cwd=target_root,text=True).strip()
                    remote['tree']=subprocess.check_output([git,'rev-parse','HEAD^{tree}'],cwd=target_root,text=True).strip()
                    return subprocess.CompletedProcess(args,0,'','')
                cp=subprocess.run(args,cwd=target_root,text=True,encoding='utf8',capture_output=True)
                if check and cp.returncode: raise p.ImportErrorSafe(cp.stderr)
                return cp
            def fake_which(name):return git if name=='git' else 'FAKE_GH'
            with patch.object(p,'ROOT',target_root), patch.object(p,'STATE',target_root/'.publish-state.json'), \
                 patch.object(sys,'argv',['publish_github.py','--execute']), patch.object(p,'api',side_effect=fake_api), \
                 patch.object(p,'command',side_effect=fake_command), patch.object(p.shutil,'which',side_effect=fake_which), \
                 patch('builtins.input',return_value='CREATE'), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(p.main(),0)
                self.assertEqual(p.main(),0)
            creates=[c for c in calls if c[:3]==['FAKE_GH','repo','create']]
            self.assertEqual(len(creates),1)
            result=json.loads((target_root/'.publish-result.json').read_text())
            self.assertEqual(result['status'],'uploaded_and_verified')
            # Check Git did not normalize any of the archived bytes.
            for row in json.loads((target_root/'archive_manifest.json').read_text())['files']:
                blob=subprocess.check_output([git,'show','HEAD:'+row['path']],cwd=target_root)
                self.assertEqual(blob,(target_root/row['path']).read_bytes())


if __name__=='__main__':
    unittest.main(verbosity=2)
