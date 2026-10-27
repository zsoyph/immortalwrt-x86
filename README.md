# ImmortalWrt x86/64 定制云编译

[![Build ImmortalWrt x86 r4](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml/badge.svg)](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml)

以已验收的 **2026-10-23 r4** 为基线：ImmortalWrt **25.12.2**、Linux **6.12.103**、x86/64，标准 Bandix、AdGuard Home LuCI 简体中文、firewall4/nftables、dae eBPF 支持。

这是配置、补丁和构建自动化仓库。16 个上游源码仓库均锁定完整提交，不随分支漂移；没有将编译主机、登录凭据、用户代理订阅或临时会话放进仓库。

## 开始云编译

1. 打开 [Actions → Build ImmortalWrt x86 r4](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml)。
2. 点击 **Run workflow**，选择 `main` 后运行。`main` 的配置、补丁或脚本变化也会自动触发。
3. 成功后在本次运行的 **Artifacts** 下载 `immortalwrt-25.12.2-x86-64-r4-运行编号`。该包包含固件、manifest、配置、源码锁及校验清单，保留 14 天。
4. 失败时下载 `build-logs-r4-运行编号`，按失败原因修复；不通过删插件、换源码基线或跳过哈希检查来让任务变绿。

不需要配置个人访问令牌或编译主机 Secret，使用 GitHub 托管 Ubuntu 24.04。工作流仅申请 `contents: read`，不会连接家中设备，也不会刷机。默认只生成 Actions 下载产物，不自动发布 Release。

首次从零编译包含 Rust、Go 和 LLVM 相关组件，耗时以 Actions 的实际记录为准；本地 r4 的约 9 分钟是已有工具链和缓存时的增量耗时，不能用作云端首次编译预估。任务上限 6 小时。

## 固件与默认访问

| 项目 | 配置 |
| --- | --- |
| 平台 | x86/64 generic |
| 镜像 | ext4、squashfs，各提供 BIOS 和 UEFI 整盘镜像 |
| 分区 | 128 MiB 引导分区 + 4096 MiB 根分区 |
| LAN | `192.168.1.1/24`，管理地址 `http://192.168.1.1` |
| 登录 | `root`，初始密码为空，首次登录后设置 |
| 防火墙 | firewall4 + nftables；允许 iptables-nft 兼容层，禁止 legacy |
| eBPF | BPF/JIT、BTF、cgroup、TC/XDP 相关能力 |
| 语言 | 简体中文，包含新增 AdGuard Home LuCI 中文翻译 |

本地基线整盘镜像压缩后约 298～369 MiB，解压后约 4.13 GiB，主要包含预留根分区空间；云端实际大小见本次构建报告。

可选服务默认关闭，首次登录后按需配置启用（Netdata 也在其中）。流量卸载默认关闭。AdGuard Home 的独立 Web 控制台没有在本项目中修改源码，本轮翻译范围是 LuCI 插件。

## 插件与菜单

成品基线共 666 个软件包、40 个 LuCI 应用；配置中 694 个包相关符号还包含构建/变体选项，不等于成品包数。完整清单见 [manifest](docs/baseline-r4/firmware.manifest)。

| 分类 | 主要应用 |
| --- | --- |
| 状态 | 系统默认状态项，Netdata 位于末项 |
| 系统 | 软件包管理、Argon 主题配置、终端、计划重启、关机（PowerOff）、一键分区扩容（Partition Expansion）等 |
| 服务 | AdGuard Home、SmartDNS、DDNS、DDNS-Go、HomeProxy、OpenClash、PassWall、Nikki、DAE/DAED、vlmcsd、UPnP |
| VPN | OpenVPN、Tailscale、ZeroTier、FRP 客户端、FRP 服务端、EasyTier；同时保留 WireGuard 协议支持 |
| NAS | 磁盘管理、文件管理、Samba4、SMB/CIFS 远程挂载、OpenList、Aria2、MiniDLNA |
| Docker | 独立一级菜单 |
| 网络 | 接口、路由、防火墙、SQM、多 WAN、wrtbwmon、标准 Bandix（状态/连接/DNS/设置）、网络加速（BBR） |
| 首页/商店 | QuickStart、iStore |

菜单迁移保留旧链接的隐藏别名，以兼容原插件内部跳转。原有 PassWall2、AdBlock Fast、Transmission、nlbwmon、acme、https-dns-proxy、irqbalance、banIP 及 Bandix Plus 不在成品中。Open-Box 继续采用官方后安装方案，不打包。

## 本地构建

在独立 Ubuntu 24.04 x86_64 环境运行（不要以 root 编译）：

```sh
git clone https://github.com/zsoyph/immortalwrt-x86.git
cd immortalwrt-x86
bash scripts/install-dependencies.sh
python3 scripts/check-project.py
python3 scripts/prepare.py
bash scripts/build.sh
```

需要足够的磁盘空间；工作流会清理临时托管机器的预装 SDK，并要求准备阶段至少空闲 55 GiB。本地脚本不清理用户磁盘。`prepare.py` 拒绝覆盖已有工作目录，重做准备请指定新的 `--work` 路径，并将同一路径传给 `build.sh`。

```sh
python3 scripts/prepare.py --work /path/to/new-work
bash scripts/build.sh /path/to/new-work
```

## 验证与已知限制

云端本次构建会检查：四种镜像分区和 SHA256、成品 manifest、40 个应用、移除项、eBPF 内核标志、实际 rootfs 中的 AdGuard Home LMO 和脚本。只有校验通过才生成固件下载包。

历史本地 r4 已通过 BIOS/UEFI VirtIO 隔离启动、br-lan/LAN、LuCI 页面和实际返回的 35 条中文译文验证，见 [测试报告](docs/baseline-r4/test-report.zh-CN.md)。**每次云构建不会继承这份历史报告作为运行验收结果**，输出 JSON 明确记录本次未运行的启动/HTTP 测试。

- HTTPS 默认未启用 443 监听。
- squashfs 版 Docker 需要独立 ext4 数据目录，默认 overlay 叠加限制未修复。
- OpenClash 独立核心仍缺失，需要按上游说明安装。
- 实际飞牛虚拟机曾出现只有 lo 的问题，尚未定位；不能用隔离 VirtIO 测试宣称已修复。
- 未验证 Secure Boot、squashfs 启动、真实代理/VPN 节点或长时间负载。

## 文件与来源

- `sources.lock.json`：完整上游提交锁。
- `configs/`：完整基线配置及固定 feeds。
- `patches/`：内核 eBPF、LuCI 菜单/翻译调用、Go 下载配置及 dae 错误处理修补。
- `translations/`：AdGuard Home 简体中文 PO。
- `files/`：默认时区、可选服务初始状态、流量卸载配置。
- `scripts/`：环境准备、源码还原、构建、检查与产物核验。
- `docs/baseline-r4/`：已完成的本地基线报告、manifest 和校验和。

上游项目与致谢见 [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md)。各软件包和补丁保留其上游许可证；本仓库不改变第三方软件授权，也不声称所有插件二进制均由完整源码重编。标准 Bandix 后端使用上游发布资产，打包定义及散列均锁定。

## BBR 网络加速扩展

新增本仓库维护的轻量 `luci-app-bbr` 中文页面，入口为 **网络 → 网络加速（BBR）**，默认开启原生 BBR + FQ。关闭开关切回 CUBIC。使用锁定源码的 `kmod-tcp-bbr`、`kmod-sched`，保留 firewall4/nftables，流量卸载仍关闭。

BBR 影响路由器本机建立的 TCP（含代理、下载）；普通 LAN 转发流量不保证提速。保存应用仅影响新连接；默认队列变化需要新建接口或重启，已有 SQM 配置保持优先。页面显示实际生效算法、可用算法及默认队列。云端检查新增模块、页面和启动服务，未进行本次实际运行及吞吐测试。历史 r4 manifest 仍保留原样，新增构建以其自身 manifest 为准。
