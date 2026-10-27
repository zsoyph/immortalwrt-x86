#!/usr/bin/env python3
"""Fail early on configuration drift or accidentally bundled private data."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
lock = json.loads((root / 'sources.lock.json').read_text(encoding='utf-8'))
assert lock['version'] == '25.12.2' and lock['kernel'] == '6.12.103'
for name, source in lock['repositories'].items():
    assert re.fullmatch('[a-f0-9]{40}', source['commit']), name
    assert source['url'].startswith('https://github.com/') and source['url'].endswith('.git'), name
config = (root / 'configs/x86-64.config').read_text(encoding='utf-8')
selected = set(re.findall(r'^CONFIG_PACKAGE_([^=]+)=y$', config, re.M))
assert len(selected) == 695, len(selected)
assert {'luci-app-partexp', 'luci-app-poweroffdevice', 'luci-i18n-partexp-zh-cn', 'luci-i18n-poweroffdevice-zh-cn'} <= selected, 'Partition expansion and poweroff with Chinese translations are required'
for makefile in (root / 'packages').glob('*/Makefile'):
    recipe = makefile.read_text(encoding='utf-8')
    assert re.search(r'\b(?:BuildPackage|KernelPackage)\b', recipe), f'Missing OpenWrt package scan signature: {makefile}'
assert len([name for name in selected if name.startswith('luci-app-') and '_' not in name]) == 40
assert {'luci-i18n-adguardhome-zh-cn', 'luci-app-turboacc', 'luci-i18n-turboacc-zh-cn', 'kmod-tcp-bbr', 'kmod-sched', 'kmod-lib-textsearch'} <= selected
assert 'luci-app-bbr' not in selected
assert not any('bandix-plus' in name or ('tables' in name and 'legacy' in name) for name in selected)
assert 'CONFIG_BPF_TOOLCHAIN_HOST=y' in config
assert 'CONFIG_BPF_TOOLCHAIN_HOST_PATH="/usr"' in config
assert 'CONFIG_TARGET_KERNEL_PARTSIZE=128' in config
assert 'CONFIG_TARGET_ROOTFS_PARTSIZE=4096' in config
po = (root / 'translations/adguardhome.zh_Hans.po').read_text(encoding='utf-8')
assert len(re.findall(r'^msgid ".+"$', po, re.M)) == 36
assert '未知版本' in po
for directory in ['packages', 'configs', 'files', 'patches', 'scripts', 'translations', 'docs', '.github']:
    for file in (root / directory).rglob('*'):
        if not file.is_file() or '__pycache__' in file.parts:
            continue
        content = file.read_text(encoding='utf-8')
        assert not re.search(r'192\.168\.100\.7|awol[0-9]{4}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY-----', content), str(file)
print(json.dumps({'source_repositories': len(lock['repositories']), 'config_selected_symbols': len(selected),
                  'luci_apps': 40, 'translation_entries': 36,
                  'config_sha256': hashlib.sha256(config.encode()).hexdigest(), 'checks': 'passed'}))
