#!/usr/bin/env bash
set -euo pipefail
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
work=${1:-"$project/work"}
mkdir -p "$project/logs"
cd "$work/immortalwrt"
export LANG=C.UTF-8
export GOPROXY='https://goproxy.cn|https://proxy.golang.org|direct'
export GOSUMDB=sum.golang.org
jobs=${BUILD_JOBS:-$(nproc)}
make download -j"$jobs" V=s 2>&1 | tee "$project/logs/download.log"
# A fresh runner has no staging_dir/host tools or target toolchain yet.
# Build them before invoking an individual package target such as bpf-headers.
for stage in tools/install toolchain/install; do
    label=${stage//\//-}
    if ! make -j"$jobs" "$stage" V=s 2>&1 | tee "$project/logs/$label.log"; then
        make -j1 "$stage" V=s 2>&1 | tee "$project/logs/$label-retry.log"
    fi
done
# Let the standard world target prepare/configure the kernel before packages.
# bpf-headers reads the target kernel .config, which does not exist yet on a
# clean runner even after tools/install and toolchain/install have completed.
if ! make -j"$jobs" V=s 2>&1 | tee "$project/logs/build.log"; then
    make -j1 V=s 2>&1 | tee "$project/logs/build-retry.log"
fi
make -j1 package/kernel/bpf-headers/compile V=s 2>&1 | tee "$project/logs/bpf-headers.log"
python3 "$project/scripts/verify-output.py" --work "$work" --output "$project/output"
