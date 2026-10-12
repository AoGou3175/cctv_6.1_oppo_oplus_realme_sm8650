"""执行真实的 BakaSU 配置片段，核对 main 选择和上游 SUSFS 暂停处理。"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(sys.argv.pop(1))
BASH = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' else shutil.which('bash')
VERSIONS = ('57', '75', '115', '118', '128', '134', '141')
SHA = 'a' * 40


def workflow(version):
    path = ROOT / '.github/workflows' / f'fastbuild_6.1.{version}.yml'
    return yaml.load(path.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)


def execute(script, suspended, checked_sha=SHA):
    with tempfile.TemporaryDirectory(prefix='bakasu-policy-') as folder:
        root = Path(folder)
        workspace = root / 'kernel_workspace'
        config = workspace / 'common/arch/arm64/configs/gki_defconfig'
        config.parent.mkdir(parents=True)
        config.write_text('', encoding='utf-8')
        compat = workspace / 'KernelSU/kernel/tools/susfs_compat.mk'
        compat.parent.mkdir(parents=True)
        compat.write_text('$(error Please wait susfs update.)\n' if suspended else '', encoding='utf-8')
        # 仅替换外部下载和提交计数；执行的分支、检查、退出和配置写入均来自真实脚本。
        prefix = '''curl() { printf '%s\n' 'printf "%s\\n" "$1" > setup-ref'; }
git() { if [[ "$1" == "rev-parse" ]]; then printf '%s\n' "$CHECKED_SHA"; else printf '4526\n'; fi; }
export GITHUB_ENV="$PWD/github-env" GITHUB_OUTPUT="$PWD/github-output"
'''
        result = subprocess.run([BASH, '-e', '-c', prefix + script], cwd=root,
                                env={**os.environ, 'CHECKED_SHA': checked_sha},
                                capture_output=True, encoding='utf-8', errors='replace')
        ref = workspace / 'setup-ref'
        return result, ref.read_text(encoding='utf-8').strip() if ref.exists() else '', config.read_text(encoding='utf-8')


def action_script(version, kind, susfs, source_ref='main'):
    child = workflow(version)
    step = next(step for step in child['jobs']['build']['steps'] if step.get('id') == 'ksu_version')
    script = step['run'].replace('${{ inputs.ksu_type }}', kind)
    script = script.replace('${{ inputs.susfs_enable }}', 'true' if susfs else 'false')
    script = f'export KSU_REF={source_ref}\n' + script
    return re.sub(r'\$\{\{ env\.(\w+) \}\}', lambda m: child['env'][m[1]], script)


def local_script(version, branch, susfs):
    text = (ROOT / 'local' / f'builder_6.1.{version}.sh').read_text(encoding='utf-8')
    block = text.split('# ===== 拉取 KSU 并设置版本号 =====', 1)[1].split('elif ', 1)[0]
    return f'cd kernel_workspace\nKSU_BRANCH={branch}\nAPPLY_SUSFS={susfs}\n' + block + '\nfi\n'


class BakaSUPolicyTests(unittest.TestCase):
    def test_default_dispatch_does_not_request_suspended_susfs(self):
        paths = [ROOT / '.github/workflows/build-test_6.1_kpm.yml']
        paths += [ROOT / '.github/workflows' / f'fastbuild_6.1.{v}.yml' for v in VERSIONS]
        for path in paths:
            with self.subTest(path=path.name):
                data = yaml.load(path.read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
                self.assertEqual(data['on']['workflow_dispatch']['inputs']['susfs_enable']['default'], 'false')

    def check_actions(self, kind, susfs, suspended, should_pass):
        for version in VERSIONS:
            with self.subTest(version=version, kind=kind):
                result, ref, config = execute(action_script(version, kind, susfs), suspended)
                self.assertEqual(ref, 'main', result.stdout + result.stderr)
                self.assertEqual(result.returncode == 0, should_pass, result.stdout + result.stderr)
                if should_pass:
                    self.assertIn('CONFIG_KSU_FULL_NAME_FORMAT=', config)
                else:
                    self.assertIn('SUSFS', result.stdout + result.stderr)
                    self.assertEqual(config, '')

    def test_actions_latest_main_without_susfs(self):
        self.check_actions('bakasu', False, True, True)

    def test_actions_suspended_susfs_rejected_without_downgrade(self):
        self.check_actions('bakasu', True, True, False)

    def test_actions_sukisu_alias_obeys_same_suspension(self):
        self.check_actions('sukisu', True, True, False)

    def test_actions_resumed_upstream_can_enable_susfs(self):
        self.check_actions('bakasu', True, False, True)

    def test_batch_uses_exact_selected_commit(self):
        for version in VERSIONS:
            with self.subTest(version=version):
                result, ref, _ = execute(action_script(version, 'bakasu', False, SHA), True)
                self.assertEqual(ref, SHA)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_batch_rejects_setup_checkout_fallback(self):
        for version in VERSIONS:
            with self.subTest(version=version):
                result, _, _ = execute(action_script(version, 'bakasu', False, SHA), True, 'b' * 40)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('checkout', result.stdout + result.stderr)

    def check_local(self, branch, susfs, suspended, should_pass):
        for version in VERSIONS:
            with self.subTest(version=version, branch=branch):
                result, ref, config = execute(local_script(version, branch, susfs), suspended)
                self.assertEqual(ref, 'main', result.stdout + result.stderr)
                self.assertEqual(result.returncode == 0, should_pass, result.stdout + result.stderr)
                self.assertEqual(bool(config), should_pass)

    def test_local_latest_main_without_susfs(self):
        self.check_local('r', 'n', True, True)

    def test_local_suspended_susfs_rejected_without_downgrade(self):
        self.check_local('r', 'y', True, False)

    def test_local_sukisu_alias_obeys_same_suspension(self):
        self.check_local('Y', 'Y', True, False)

    def test_local_resumed_upstream_can_enable_susfs(self):
        self.check_local('r', 'y', False, True)


class ManagerAttachmentTests(unittest.TestCase):
    def check_release(self, kind, apk_name, expected_apk):
        data = yaml.load((ROOT / '.github/workflows/build-test_6.1_kpm.yml').read_text(encoding='utf-8'), Loader=yaml.BaseLoader)
        step = next(s for s in data['jobs']['release']['steps'] if s.get('name') == '创建统一 Release')
        with tempfile.TemporaryDirectory(prefix='gki-release-test-') as folder:
            root = Path(folder)
            (root / 'release_zips').mkdir()
            (root / 'bakasu_manager').mkdir()
            for version in VERSIONS:
                (root / 'release_zips' / f'AnyKernel3_6.1.{version}.zip').write_bytes(b'test-zip')
            if apk_name:
                (root / 'bakasu_manager' / apk_name).write_bytes(b'test-apk')
            env = {**os.environ, **{k: 'false' for k in step['env']},
                   'KSU_TYPE': kind, 'KSUVER': '35226', 'KSU_SHA': SHA,
                   'MANAGER_RUN_ID': '1234', 'GITHUB_REPOSITORY': 'test/local', 'GITHUB_RUN_ID': '123'}
            # 禁止真实 API 调用/发布；只记录真实脚本传给 release create 的资产。
            prefix = '''gh() {
  [[ "$1 $2" == "release create" ]] || return 91
  printf '%s\\n' "$@" > release-args
}
curl() { return 92; }
'''
            result = subprocess.run([BASH, '-e', '-c', prefix + step['run']], cwd=root, env=env,
                                    capture_output=True, encoding='utf-8', errors='replace')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            args = (root / 'release-args').read_text(encoding='utf-8').splitlines()
            self.assertEqual(len([a for a in args if a.endswith('.zip')]), 7)
            self.assertEqual([a for a in args if a.endswith('.apk')],
                             [f'release_zips/{expected_apk}'] if expected_apk else [])
            notes = (root / 'release_notes.md').read_text(encoding='utf-8')
            self.assertIn(expected_apk or '未附带', notes)
            self.assertIn('Installation Guide', notes)
            self.assertIn('6.1.128', notes)
            if kind == 'bakasu':
                self.assertIn(SHA, notes)
                self.assertIn('Build Manager', notes)

    def test_official_manager_is_attached(self):
        apk = 'BakaSU_v4.2.0_35226-arm64-v8a-release.apk'
        self.check_release('bakasu', apk, apk)

    def test_old_manager_is_not_used_as_fallback(self):
        self.check_release('bakasu', 'ReSukiSU_35203-arm64-v8a-release.apk', None)

    def test_none_publishes_seven_kernels_without_manager(self):
        self.check_release('none', None, None)


if __name__ == '__main__':
    unittest.main()
