"""Validate the seven-version reusable workflow contracts and Bash syntax.

Run with PyYAML installed: python tests/validate_workflows.py
"""
from pathlib import Path
import re
import subprocess
import os
import yaml

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / '.github' / 'workflows'
VERSIONS = {'build_57': '57', 'build_75': '75', 'build_115': '115',
            'build_118': '118', 'build_128': '128', 'build_134': '134',
            'build_141': '141'}
BASH = Path('C:/Program Files/Git/bin/bash.exe')
if not BASH.exists():
    BASH = 'bash'

def load(path):
    text = path.read_text(encoding='utf-8')
    assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)', text, re.M), path
    return yaml.load(text, Loader=yaml.BaseLoader), text

parent, _ = load(WF / 'build-test_6.1_kpm.yml')
dispatch = parent['on']['workflow_dispatch']['inputs']
assert dispatch['ksu_type']['default'] == 'bakasu', 'obsolete default KSU branch'
assert 'bakasu' in dispatch['ksu_type']['options']
assert dispatch['kpm_enable']['default'] == 'true'
assert dispatch['susfs_enable']['default'] == 'false', 'BakaSU currently forbids SUSFS builds'
assert set(parent['jobs']) == set(VERSIONS) | {'prepare', 'release'}
assert set(parent['jobs']['release']['needs']) == set(VERSIONS) | {'prepare'}
assert parent['jobs']['release']['permissions']['contents'] == 'write'
manager_step = next(s for s in parent['jobs']['release']['steps'] if s.get('name') == '下载同提交的官方 BakaSU 管理器')
assert manager_step['with']['repository'] == 'Baka-SU/BakaSU'
assert manager_step['with']['run-id'] == '${{ needs.prepare.outputs.manager_run_id }}'
assert manager_step['continue-on-error'] == 'true'
files = [(WF / 'build-test_6.1_kpm.yml', parent)]
names = []
for job, version in VERSIONS.items():
    call = parent['jobs'][job]
    path = ROOT / call['uses'].removeprefix('./')
    assert path.name == f'fastbuild_6.1.{version}.yml'
    child, text = load(path)
    interface = child['on']['workflow_call']
    assert set(call['with']) == set(interface['inputs']) == set(dispatch) | {'ksu_ref', 'batch_mode'}
    assert call['needs'] == 'prepare'
    assert call['with']['ksu_ref'] == "${{ needs.prepare.outputs.ksu_ref || 'main' }}"
    assert call['with']['batch_mode'] == 'true'
    assert interface['inputs']['ksu_ref']['type'] == 'string'
    assert child['on']['workflow_dispatch']['inputs']['susfs_enable']['default'] == 'false'
    for name, value in dispatch.items():
        kind = 'string' if value['type'] == 'choice' else value['type']
        assert interface['inputs'][name]['type'] == kind, (version, name)
        assert call['with'][name] == '${{ inputs.' + name + ' }}'
    assert set(interface['outputs']) >= {'ksuver', 'ak3name', 'ksu_sha'}
    for output in ('ksuver', 'ak3name', 'ksu_sha'):
        assert interface['outputs'][output]['value'] == '${{ jobs.build.outputs.' + output + ' }}'
        assert output in child['jobs']['build']['outputs']
    assert child['env']['SUB_VERSION'] == version
    assert 'github.event.inputs.' not in text, path
    assert '"bakasu"' in text and 'Baka-SU/BakaSU' in text
    templates = re.findall(r'^\s+AK3_NAME=(.*)$', text, re.M)
    assert len(templates) == 2
    assert all('${{ env.KERNEL_VERSION }}.${{ env.SUB_VERSION }}' in t for t in templates)
    names.append(f'AnyKernel3_BakaSU_35203_6.1.{version}_AoGou.zip')
    files.append((path, child))
assert len(set(names)) == 7
legacy, _ = load(WF / 'build-test.yml')
assert legacy['on']['workflow_dispatch']['inputs']['ksu_type']['default'] == 'bakasu'
files.append((WF / 'build-test.yml', legacy))
count = 0
for path, workflow in files:
    for job in workflow['jobs'].values():
        for step in job.get('steps', []):
            if 'run' not in step or step.get('shell', 'bash') != 'bash':
                continue
            script = re.sub(r'\$\{\{.*?\}\}', 'test', step['run'])
            result = subprocess.run([str(BASH), '-n'], input=script, text=True,
                                    encoding='utf-8', capture_output=True)
            assert result.returncode == 0, (path.name, step.get('name'), result.stderr)
            count += 1
for version in VERSIONS.values():
    path = ROOT / 'local' / f'builder_6.1.{version}.sh'
    content = path.read_bytes()
    assert b'\r' not in content, f'{path.name}: Shell scripts must use LF'
    result = subprocess.run([str(BASH), '-n'], input=content.decode('utf-8'), text=True,
                            encoding='utf-8', capture_output=True)
    assert result.returncode == 0, (path.name, result.stderr)
print(f'PASS: 7 versions (57/75/115/118/128/134/141), input/output contracts, unique ZIP names, {count} Bash steps, 7 local scripts')
