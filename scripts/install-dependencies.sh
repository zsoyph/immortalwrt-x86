#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y build-essential gcc-multilib g++-multilib git subversion \
  binutils bzip2 ccache clang cmake cpio curl file flex gawk gettext \
  libelf-dev libncurses-dev libssl-dev llvm make patch pkgconf python3 \
  python3-pyelftools python3-setuptools rsync swig unzip wget zlib1g-dev \
  zstd dwarves bison libgnutls28-dev libgmp-dev libmpc-dev libmpfr-dev \
  libtool autoconf automake autopoint help2man gperf texinfo time jq \
  libfuse-dev liblzma-dev libzstd-dev
printf 'int x;\n' | clang -target bpf -O2 -g -x c -c - -o /tmp/immortalwrt-bpf-smoke.o
file /tmp/immortalwrt-bpf-smoke.o
