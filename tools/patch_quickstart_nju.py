#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给 iStore quickstart 二进制打补丁（完整版，共 3 处）：

1. 软件源下拉「清华大学」槽位 -> 「南京大学」+ ImmortalWrt 仓库
     name: 清华大学 -> 南京大学（12B 等长）
     url:  https://mirrors.tuna.tsinghua.edu.cn/openwrt/   (45)
        -> https://mirror.nju.edu.cn/immortalwrt/           (38)
   南方科技大学槽位保持原样；identity 仍为 Tsinghua（前端只传 identity）。

2. 网络检测模板 `%v://%v/openwrt/` -> `%v://%v/immortalwrt/`
   quickstart 检测逻辑（vaddr 0x79a9e0 起的函数）：url.Parse(distfeeds 第一行)
   取 scheme+host，若 host 含 "openwrt" 走 `%v://%v/` 分支，否则用 16 字节
   模板拼 base 去内置列表全等匹配，匹配不到即判「软件源错误」。
   mirror.nju.edu.cn 永远不含 openwrt，必须把模板改成 immortalwrt 路径。
   新模板 20B 放不进原位（后面紧邻其它常量），改放 PT_LOAD3 段尾页内填充区
   （文件 0xa27b78 / vaddr 0xe27b78，1160B 全 0，按页映射可读），并同步改：
     - LEA rax,[rip+rel32] @0x39abbc (48 8d 05 ...) 重算 rel32 -> 新地址
     - mov ebx,0x10 @0x39abc3 (bb 10 00 00 00) -> 0x14（模板长度 16->20）

3. 跳过软件源签名校验（修「软件源错误」红标）
   quickstart 网络检测（vaddr 0x7bd420 函数）在网络/DNS 检测通过后，会用
   curl 去拉 <distfeeds 第二行>.asc 签名文件校验软件源，任一失败即
   softSourceFailed（页面显示「软件源错误」）。但 ImmortalWrt 25.12 的
   apk 仓库（官方/南大/iStore compat）均不发布 .asc 文件，官方源也 404，
   导致任何源都必然红标。补丁：NOP 掉 vaddr 0x7bd5d5 的
   `jne 0x7bd5e5`（75 0e -> 90 90），校验 curl 块变成死代码，
   状态直接走 netSuccess（网络/DNS 检测逻辑保留不受影响）。

注意：输入必须是**未打补丁的原始 quickstart**（同版本原包里的那个）。

用法：python patch_quickstart_nju.py <原二进制> <输出二进制>
升级 quickstart 包后重新拉一次原二进制、重跑本脚本即可。
"""
import re
import struct
import sys

# ---- 补丁 1/2：清华槽位 -> 南京大学 immortalwrt ----
OLD_URL = b"https://mirrors.tuna.tsinghua.edu.cn/openwrt/"
NEW_URL = b"https://mirror.nju.edu.cn/immortalwrt/"
OLD_NAME = "清华大学".encode()
NEW_NAME = "南京大学".encode()

# 南方科技大学必须原样保留（sanity 检查）
KEEP = [
    b"SUSTech",
    "南方科技大学".encode(),
    b"https://mirrors.sustech.edu.cn/openwrt/",
]

# ---- 补丁 3：检测模板 openwrt -> immortalwrt ----
TPL_OLD = b"%v://%v/openwrt/"
TPL_NEW = b"%v://%v/immortalwrt/"
PAD_OFF = 0xA27B78          # PT_LOAD3 段尾页内填充区（全 0）
LEA_OFF = 0x39ABBC          # lea rax,[rip+rel32] 引用旧模板
LEN_IMM_OFF = 0x39ABC4      # mov ebx,imm32 的立即数字节（0x10 -> 0x14）
CODE_BASE = 0x400000        # PT_LOAD2 vaddr（文件偏移 + 0x400000）

# ---- 补丁 4：跳过 .asc 签名校验（修「软件源错误」） ----
ASC_JNE_OFF = 0x3BD5D5      # vaddr 0x7bd5d5: jne 0x7bd5e5（curl 校验失败分支）
ASC_JNE_OLD = b"\x75\x0e"   # jne +14
ASC_JNE_NEW = b"\x90\x90"   # nop nop


def load_segments(data):
    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_phentsize = struct.unpack_from("<H", data, 54)[0]
    e_phnum = struct.unpack_from("<H", data, 56)[0]
    segs = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type = struct.unpack_from("<I", data, off)[0]
        p_offset, p_vaddr, _, p_filesz, _ = struct.unpack_from("<QQQQQ", data, off + 8)
        if p_type == 1:  # PT_LOAD
            segs.append((p_offset, p_vaddr, p_filesz))
    return segs


def off_to_vaddr(segs, off):
    for p_offset, p_vaddr, p_filesz in segs:
        if p_offset <= off < p_offset + p_filesz:
            return p_vaddr + (off - p_offset)
    raise RuntimeError("offset %#x not in any PT_LOAD" % off)


def replace_string(data, old, new, label):
    hits = [m.start() for m in re.finditer(re.escape(old), data)]
    if len(hits) != 1:
        raise RuntimeError("%s: expected 1 occurrence, got %d" % (label, len(hits)))
    off = hits[0]
    if len(new) > len(old):
        raise RuntimeError("%s: new string longer than old" % label)
    segs = load_segments(data)
    va = off_to_vaddr(segs, off)
    hdr_hits = [m.start() for m in re.finditer(re.escape(struct.pack("<Q", va)), data)]
    if len(hdr_hits) != 1:
        raise RuntimeError("%s: expected 1 string header, got %d" % (label, len(hdr_hits)))
    hdr = hdr_hits[0]
    cur_len = struct.unpack_from("<Q", data, hdr + 8)[0]
    if cur_len != len(old):
        raise RuntimeError("%s: header len %d != %d" % (label, cur_len, len(old)))
    data[off:off + len(old)] = new + b"\x00" * (len(old) - len(new))
    struct.pack_into("<Q", data, hdr + 8, len(new))
    print("%-10s off=%#x vaddr=%#x header=%#x len %d -> %d" %
          (label, off, va, hdr, cur_len, len(new)))


def patch_template(data):
    """把检测模板 %v://%v/openwrt/ 换成 immortalwrt 版（新地址 + LEA + len）。"""
    segs = load_segments(data)
    # 旧模板位置与 LEA 引用必须自洽
    old_hits = [m.start() for m in re.finditer(re.escape(TPL_OLD), data)]
    if len(old_hits) != 1:
        raise RuntimeError("template: expected 1 occurrence, got %d" % len(old_hits))
    old_va = off_to_vaddr(segs, old_hits[0])
    rel = struct.unpack_from("<i", data, LEA_OFF + 3)[0]
    lea_target = CODE_BASE + LEA_OFF + 7 + rel
    if lea_target != old_va:
        raise RuntimeError("template: LEA target %#x != old vaddr %#x" % (lea_target, old_va))
    # 填充区必须全 0（不影响段 4 及其它数据）
    if any(data[PAD_OFF:PAD_OFF + len(TPL_NEW) + 16]):
        raise RuntimeError("template: padding area not zero")
    # 段尾填充区在原 filesz 之外：把 PT_LOAD3 的 p_filesz/p_memsz 扩到页对齐，
    # 让填充区正式纳入加载映射（加载器本就按页映射到该页，仅改声明）
    pad_end = PAD_OFF + len(TPL_NEW)
    if pad_end % 0x1000:
        pad_end = (pad_end // 0x1000 + 1) * 0x1000
    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_phentsize = struct.unpack_from("<H", data, 54)[0]
    e_phnum = struct.unpack_from("<H", data, 56)[0]
    patched_seg = False
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        if struct.unpack_from("<I", data, off)[0] != 1:
            continue
        po, va, pa, fs, ms = struct.unpack_from("<QQQQQ", data, off + 8)
        if po <= PAD_OFF < po + fs + 0x1000:  # 段 3（PAD_OFF 恰在其 filesz 终点的页内）
            new_fs = max(fs, pad_end - po)
            struct.pack_into("<QQ", data, off + 32, new_fs, new_fs)  # p_filesz, p_memsz
            print("%-10s phdr@%#x filesz/memsz %#x -> %#x" % ("segment", off, fs, new_fs))
            patched_seg = True
            break
    if not patched_seg:
        raise RuntimeError("template: PT_LOAD3 phdr not found")
    segs = load_segments(data)
    new_va = off_to_vaddr(segs, PAD_OFF)
    # 写新模板到填充区
    data[PAD_OFF:PAD_OFF + len(TPL_NEW)] = TPL_NEW
    # 重算 LEA rel32
    new_rel = new_va - (CODE_BASE + LEA_OFF + 7)
    struct.pack_into("<i", data, LEA_OFF + 3, new_rel)
    # 长度立即数 0x10 -> 0x14
    if data[LEN_IMM_OFF] != 0x10:
        raise RuntimeError("template: len imm byte is %#x, expected 0x10" % data[LEN_IMM_OFF])
    data[LEN_IMM_OFF] = len(TPL_NEW)
    print("%-10s pad_off=%#x vaddr=%#x lea@%#x rel %#x -> %#x len 16 -> %d" %
          ("template", PAD_OFF, new_va, LEA_OFF, rel, new_rel, len(TPL_NEW)))


def patch_asc_check(data):
    """NOP 掉 curl .asc 校验失败分支（0x7bd5d5 jne -> nop nop）。"""
    cur = bytes(data[ASC_JNE_OFF:ASC_JNE_OFF + 2])
    if cur != ASC_JNE_OLD:
        raise RuntimeError("asc: bytes @%#x are %s, expected %s"
                           % (ASC_JNE_OFF, cur.hex(), ASC_JNE_OLD.hex()))
    data[ASC_JNE_OFF:ASC_JNE_OFF + 2] = ASC_JNE_NEW
    print("%-10s off=%#x vaddr=0x7bd5d5 jne -> nop nop（跳过 .asc 校验）"
          % ("asc-skip", ASC_JNE_OFF))


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    data = bytearray(open(src, "rb").read())
    if data[:4] != b"\x7fELF" or data[4] != 2:
        raise RuntimeError("not a 64-bit ELF binary")
    replace_string(data, OLD_URL, NEW_URL, "url")
    replace_string(data, OLD_NAME, NEW_NAME, "name")
    patch_template(data)
    patch_asc_check(data)
    open(dst, "wb").write(bytes(data))
    print("written:", dst, "size:", len(data))

    # sanity：新槽位就位、旧清华串消失、南科大原样、模板补丁生效
    chk = open(dst, "rb").read()
    assert NEW_URL in chk and NEW_NAME in chk
    assert OLD_URL not in chk and OLD_NAME not in chk
    assert b"Tsinghua" in chk, "identity Tsinghua 必须保留"
    for s in KEEP:
        assert s in chk, "南方科技大学原串丢失: %r" % s
    assert TPL_NEW in chk
    rel = struct.unpack_from("<i", chk, LEA_OFF + 3)[0]
    assert CODE_BASE + LEA_OFF + 7 + rel == 0xE27B78, "LEA 未指向新模板"
    assert chk[LEN_IMM_OFF] == 0x14, "长度立即数未更新"
    assert chk[ASC_JNE_OFF:ASC_JNE_OFF + 2] == ASC_JNE_NEW, ".asc 跳转未 NOP"
    print("sanity: OK (南科大原样, identity=Tsinghua, 检测模板=immortalwrt, .asc 校验已跳过)")


if __name__ == "__main__":
    main()
