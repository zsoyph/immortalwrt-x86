#!/usr/bin/env python3
"""Validate newly built artifacts; historical runtime reports are never reused."""
import argparse
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess

PROJECT = Path(__file__).resolve().parents[1]


def partitions(data):
    result = []
    if data[512:520] == b'EFI PART':
        start = struct.unpack_from('<Q', data, 584)[0] * 512
        count, size = struct.unpack_from('<II', data, 592)
        for index in range(count):
            offset = start + index * size
            if data[offset:offset + 16] != bytes(16):
                first, last = struct.unpack_from('<QQ', data, offset + 32)
                result.append((last - first + 1) * 512)
    else:
        assert data[510:512] == b'\x55\xaa', 'Invalid MBR'
        for index in range(4):
            offset = 446 + index * 16
            if data[offset + 4]:
                result.append(struct.unpack_from('<I', data, offset + 12)[0] * 512)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, default=PROJECT / 'work')
    parser.add_argument('--output', type=Path, default=PROJECT / 'output')
    args = parser.parse_args()
    core = args.work.resolve() / 'immortalwrt'
    target = core / 'bin/targets/x86/64'
    subprocess.run(['sha256sum', '-c', 'sha256sums'], cwd=target, check=True)
    names = {line.split(' - ')[0] for line in next(target.glob('*.manifest')).read_text(encoding='utf-8').splitlines()}
    required_apps = {line.split(' - ')[0] for line in (PROJECT / 'docs/baseline-r4/firmware.manifest').read_text(encoding='utf-8').splitlines() if line.startswith('luci-app-')}
    required_apps |= {'luci-app-turboacc', 'luci-app-partexp', 'luci-app-poweroffdevice', 'luci-app-easytier'}
    assert required_apps <= names, sorted(required_apps - names)
    assert {'kmod-tcp-bbr', 'kmod-sched', 'kmod-lib-textsearch', 'bandix', 'dae', 'daed', 'firewall4', 'nftables-json', 'iptables-nft', 'ip6tables-nft', 'kmod-fs-cifs', 'vlmcsd', 'luci-i18n-adguardhome-zh-cn'} <= names
    assert {'luci-i18n-partexp-zh-cn', 'luci-i18n-poweroffdevice-zh-cn'} <= names
    assert {'luci-i18n-turboacc-zh-cn', 'kmod-nft-fullcone', 'kmod-nft-offload'} <= names
    removed = {'luci-app-bbr', 'luci-app-acme', 'luci-app-https-dns-proxy', 'luci-app-irqbalance', 'luci-app-banip', 'luci-app-passwall2', 'luci-app-transmission', 'luci-app-nlbwmon', 'luci-app-adblock-fast'}
    assert not names & removed
    assert not any('bandix-plus' in name or ('tables' in name and 'legacy' in name) for name in names)
    assert len(required_apps) == 40
    assert len(names) == 667, f'Unexpected manifest package count: {len(names)}'
    images = []
    for filesystem in ['ext4', 'squashfs']:
        for boot in ['combined', 'combined-efi']:
            image = target / f'immortalwrt-x86-64-generic-{filesystem}-{boot}.img.gz'
            with gzip.open(image, 'rb') as stream:
                sizes = partitions(stream.read(131072))
            assert 128 * 1024**2 in sizes and 4096 * 1024**2 in sizes, (image.name, sizes)
            images.append({'name': image.name, 'bytes': image.stat().st_size, 'partition_bytes': sizes})
    kernel = next((core / 'build_dir/target-x86_64_musl/linux-x86_64').glob('linux-6.12.*/.config'))
    text = kernel.read_text(encoding='utf-8')
    flags = ['BPF', 'BPF_SYSCALL', 'BPF_JIT', 'DEBUG_INFO_BTF', 'CGROUP_BPF', 'NET_CLS_BPF', 'NET_ACT_BPF', 'TCP_CONG_BBR', 'NET_SCH_FQ']
    assert all(re.search(r'^CONFIG_' + flag + r'=[ym]$', text, re.M) for flag in flags)
    root = core / 'build_dir/target-x86_64_musl/root-x86'
    for app in ['partexp', 'poweroffdevice']:
        menu = root / f'usr/share/luci/menu.d/luci-app-{app}.json'
        assert f'admin/system/{app}' in json.loads(menu.read_text(encoding='utf-8')), app
        translation = root / f'usr/lib/lua/luci/i18n/{app}.zh-cn.lmo'
        assert translation.is_file() and translation.stat().st_size > 0, app
    for relative in ['etc/config/turboacc', 'etc/init.d/turboacc', 'usr/lib/lua/luci/controller/turboacc.lua', 'usr/lib/lua/luci/model/cbi/turboacc.lua', 'usr/lib/lua/luci/i18n/turboacc.zh-cn.lmo']:
        assert (root / relative).is_file(), relative
    assert list((root / 'etc/rc.d').glob('S90turboacc')), 'TurboACC boot service must be enabled'
    for relative in ['etc/init.d/bbr', 'etc/config/bbr', 'www/luci-static/resources/view/network/bbr.js', 'usr/share/luci/menu.d/luci-app-bbr.json']:
        assert not (root / relative).exists(), relative
    config = (root / 'etc/config/turboacc').read_text(encoding='utf-8')
    for name in ['sw_flow', 'hw_flow', 'sfe_flow']:
        assert "option " + name + " '0'" in config, name
    assert "option fullcone_nat '1'" in config and "option bbr_cca '1'" in config
    init = (root / 'etc/init.d/turboacc').read_text(encoding='utf-8')
    assert 'firewall.@defaults[0].fullcone6' in init
    lmo = root / 'usr/lib/lua/luci/i18n/adguardhome.zh-cn.lmo'
    assert lmo.is_file() and lmo.stat().st_size > 0
    view = root / 'www/luci-static/resources/view/adguardhome/config.js'
    assert "_('Unknown version')" in view.read_text(encoding='utf-8')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    for file in target.iterdir():
        if file.is_file():
            shutil.copy2(file, output / file.name)
    shutil.copy2(core / '.config', output / 'firmware.config')
    shutil.copy2(kernel, output / 'kernel.config')
    shutil.copy2(PROJECT / 'sources.lock.json', output / 'sources.lock.json')
    shutil.copy2(lmo, output / lmo.name)
    report = {'checked': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'baseline': '20261023-r4', 'profile': '20261027-r6-turboacc', 'packages': len(names), 'luci_apps': len(required_apps),
              'images': images, 'kernel_flags_verified': flags, 'adguardhome_lmo_in_rootfs': True,
              'runtime_boot_tested_this_build': False, 'runtime_translation_http_tested_this_build': False}
    (output / 'build-verification.json').write_text(json.dumps(report, indent=2))
    sums = []
    for file in sorted(output.iterdir()):
        with file.open('rb') as stream:
            sums.append(hashlib.file_digest(stream, 'sha256').hexdigest() + '  ' + file.name)
    (output / 'artifact-sha256sums.txt').write_text('\n'.join(sums) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
