#!/usr/bin/env python3
"""Recreate the accepted r4 source tree using immutable Git commits."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

PROJECT = Path(__file__).resolve().parents[1]


def run(args, cwd):
    subprocess.run(args, cwd=cwd, check=True)


def selected(text):
    return set(re.findall(r'^CONFIG_PACKAGE_([^=]+)=y$', text, re.M))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, default=PROJECT / 'work')
    args = parser.parse_args()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    lock = json.loads((PROJECT / 'sources.lock.json').read_text(encoding='utf-8'))
    core = work / 'immortalwrt'
    paths = {'core': core}
    paths.update({name: core / 'feeds' / name for name in ['packages', 'luci', 'routing']})
    paths.update({name: work / 'addons' / name for name in lock['repositories'] if name not in paths})
    for name, source in lock['repositories'].items():
        path = paths[name]
        if path.exists():
            raise RuntimeError(f'{path} already exists; use a new work directory')
        path.mkdir(parents=True)
        run(['git', 'init', '-q'], path)
        run(['git', 'remote', 'add', 'origin', source['url']], path)
        run(['git', 'fetch', '--depth=1', 'origin', source['commit']], path)
        run(['git', '-c', 'advice.detachedHead=false', 'checkout', '--detach', 'FETCH_HEAD'], path)
        actual = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip()
        assert actual == source['commit'], name
    for patch in sorted((PROJECT / 'patches').glob('*.patch')):
        target = paths[patch.stem]
        run(['git', 'apply', '--check', str(patch)], target)
        run(['git', 'apply', str(patch)], target)
    po = core / 'feeds/luci/applications/luci-app-adguardhome/po/zh_Hans/adguardhome.po'
    po.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PROJECT / 'translations/adguardhome.zh_Hans.po', po)
    shutil.copyfile(PROJECT / 'configs/feeds.conf', core / 'feeds.conf')
    links = {
        'daede': paths['daede'], 'istore': paths['istore'],
        # The accepted configuration uses the stable core. Loading the unused
        # alpha recipe as well creates a mutual-CONFLICTS Kconfig cycle.
        'luci-app-nikki': paths['nikki'] / 'luci-app-nikki',
        'nikki': paths['nikki'] / 'nikki',
        'mihomo-meta': paths['nikki'] / 'mihomo-meta',
        'luci-app-bandix': paths['bandix-luci'] / 'luci-app-bandix',
        'openwrt-bandix': paths['bandix-backend'] / 'openwrt-bandix',
        'wrtbwmon-luci': paths['wrtbwmon-luci'], 'wrtbwmon': paths['wrtbwmon'] / 'wrtbwmon',
        'quickstart': paths['nas-packages'] / 'network/services/quickstart',
        'luci-app-quickstart': paths['nas-luci'] / 'luci/luci-app-quickstart',
    }
    custom = core / 'package/custom'
    custom.mkdir(parents=True)
    for name, source in links.items():
        assert (source / 'Makefile').is_file() or name in ['nikki', 'daede', 'istore', 'wrtbwmon-luci'], source
        (custom / name).symlink_to(source, target_is_directory=True)
    run(['./scripts/feeds', 'update', '-i', 'packages', 'luci', 'routing'], core)
    run(['./scripts/feeds', 'install', '-a'], core)
    for name in ['dae', 'daed', 'luci-app-dae', 'luci-app-daed']:
        for link in (core / 'package/feeds').glob('*/' + name):
            if link.is_symlink():
                link.unlink()
    shutil.copytree(PROJECT / 'files', core / 'files', dirs_exist_ok=True)
    for file in (core / 'files/etc/uci-defaults').iterdir():
        file.chmod(0o755)
    seed = (PROJECT / 'configs/x86-64.config').read_text(encoding='utf-8')
    assert 'mihomo-meta' in selected(seed) and 'mihomo-alpha' not in selected(seed), 'r4 requires the selected stable Mihomo core'
    (core / '.config').write_text(seed)
    run(['make', 'defconfig'], core)
    resolved = (core / '.config').read_text(encoding='utf-8')
    missing, extra = selected(seed) - selected(resolved), selected(resolved) - selected(seed)
    assert not missing and not extra, {'packages_missing': sorted(missing), 'packages_extra': sorted(extra)}
    assert len([name for name in selected(resolved) if name.startswith('luci-app-') and '_' not in name]) == 36
    assert 'CONFIG_TARGET_ROOTFS_PARTSIZE=4096' in resolved
    assert 'CONFIG_TARGET_KERNEL_PARTSIZE=128' in resolved
    (work / 'preparation.json').write_text(json.dumps({
        'baseline': lock['baseline'], 'selected_packages': len(selected(resolved)),
        'config_sha256': hashlib.sha256(resolved.encode()).hexdigest(),
        'source_commits_verified': True, 'selected_packages_match': True,
    }, indent=2))


if __name__ == '__main__':
    main()
