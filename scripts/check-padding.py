#!/usr/bin/env python3
"""Ensure sparse padding preserves the original dd conv=sync byte semantics."""
import hashlib
from pathlib import Path
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    for block in [1, 3, 4096, 65536]:
        for size in [0, 1, block - 1, block, block + 1, block * 2 + 17]:
            source, old, new = (root / name for name in ['source', 'old', 'new'])
            source.write_bytes(bytes(range(256)) * (size // 256) + bytes(range(size % 256)))
            subprocess.run(['dd', f'if={source}', f'of={old}', f'bs={block}', 'conv=sync', 'status=none'], check=True)
            subprocess.run(['cp', '--sparse=always', str(source), str(new)], check=True)
            subprocess.run(['truncate', '-s', f'%{block}', str(new)], check=True)
            assert old.stat().st_size == new.stat().st_size, (size, block)
            assert hashlib.sha256(old.read_bytes()).digest() == hashlib.sha256(new.read_bytes()).digest(), (size, block)
print('Sparse image padding matches dd byte-for-byte in all boundary cases')
