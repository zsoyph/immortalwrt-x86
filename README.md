# ImmortalWrt x86/64 r9：OAF + Honk

[![Build](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml/badge.svg)](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml)

当前版本 **25.12.2 / Linux 6.12.103**，新增 OpenAppFilter/OAF 官方最新源码 **7.0.2**，最新正式发布tag仍为7.0.1。锁定源码提交，针对本内核自行编译，不混装其他固件kmod。42个应用、706选包，原41应用含Honk及冻结版本完整保留。Netdata/EasyTier不升级。

## OAF 使用

菜单【服务 → 应用过滤】。默认不启用appfilter启动项；需要使用时在【系统 → 启动项】启用并启动appfilter，再配置过滤规则。包中已建立配置文件。特征识别受加密、特征库和代理/eBPF绕行影响，不承诺识别全部Honk/DAE代理流量。

后端7.0.2-r2，LuCI7.0-r2，kmod-oaf6.12.103-r1；本地修订用于配置安装及加速设置适配。OAF“关闭加速”只处理流量卸载，不自动关闭TurboACC的全锥形或BBR。源码和适配见 [oaf.lock.json](oaf.lock.json)、[r9说明](docs/r9-oaf.md)、[适配补丁](patches/oaf.patch)。GPL许可证和原作者引用保留。

为排除旧feed同名配方，准备脚本只移除旧open-app-filter的feed入口；新内核模块、后端、LuCI分别来自同一锁定官方源码，后端使用custom/oaf-daemon。其余已选插件保留。

## 云编译与产物

[Actions](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml) 可手动运行，main配置变更自动触发。成功后在该次运行Artifacts下载 **immortalwrt-25.12.2-x86-64-r9-oaf-运行编号**，保留14天，诊断日志7天。仅所有成品校验通过后上传固件，不自动发布Release，不刷机部署，不需局域网凭据。

四种ext4/squashfs BIOS/UEFI整盘镜像，启动128MiB/根4096MiB；默认192.168.1.1、root、初始空密码。原生fw4/nftables，iptables-nft兼容且无legacy；TurboACC BBR/FQ/IPv4全锥形默认开，软件/硬件/SFE卸载默认关。标准Bandix、AdGuard中文和PassWall系统启动入口修复保留。

云端核对完整基线包、42应用、升级/冻结版本、分区、SHA256、内核/eBPF、Honk及OAF模块/菜单/中文资源/默认设置。未做本轮云端隔离启动或流量识别测试；历史本地测试不能代替。

## 构建

    bash scripts/install-dependencies.sh
    python3 scripts/check-project.py
    python3 scripts/prepare.py
    bash scripts/build.sh

依赖来源见 [sources.lock.json](sources.lock.json)、[updates.lock.json](updates.lock.json)、[Honk锁](honk.lock.json)。引用和许可见 [致谢](ACKNOWLEDGEMENTS.md)。

---

# 沿用的 r8 Honk 说明（历史）

Honk **v0.1.0-beta.3（预发布版）**，保留 r7 完整应用及锁定版本、PassWall 启动入口修复，Netdata/EasyTier不升级。系统25.12.2/Linux6.12.103，41应用/702选包，128/4096MiB分区。

采用官方已编译 x86_64 静态 musl full 包（真实eBPF+嵌入式Doona）打包进固件，不宣称本项目从Rust重编核心。菜单【服务/Honk】，默认关闭；系统入口enable以保留配置触发链路。启动拒绝与DAE/DAED并行，不修改其UCI。Doona仅回环127.0.0.1:9527，SSH转发访问；Clash API回环19090。

官方来源和SHA256见 [honk.lock.json](honk.lock.json)，[适配说明](docs/r8-honk.md)。核心GPL及Doona第三方声明随固件保留。DAED使用Go1.27.3修复旧配方编译器版本不足。

云端产物 immortalwrt-25.12.2-x86-64-r9-oaf-运行编号 保留14天，诊断7天。只在全部成品检查成功后上传固件。云端未做本轮隔离启动和Honk实际流量测试，历史本地测试不能代替。

---

# ImmortalWrt x86/64 r8 Honk 云编译

[![Build](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml/badge.svg)](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml)

ImmortalWrt **25.12.2 / Linux 6.12.103**，x86/64。r6 用 **TurboACC 1.4** 替换独立 BBR 页面，保留标准 Bandix、AdGuard Home LuCI 中文、分区扩容、关机及其余已选插件。完整源码提交锁定在 [sources.lock.json](sources.lock.json)。

## 云编译与下载

打开 [Actions](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml)，选择 **Run workflow**。main 的构建配置或源码变化也会触发。成功后在本次运行的 Artifacts 下载 `immortalwrt-25.12.2-x86-64-r9-oaf-运行编号`，保留 **14 天**；诊断日志保留 7 天。不自动发布 Release、不刷机，不需要个人令牌或局域网编译机凭据。云端使用 GitHub 托管 Ubuntu 24.04，工作流只申请 contents:read。

## 本版配置

| 项目 | 内容 |
| --- | --- |
| 镜像 | ext4、squashfs，分别提供 BIOS/UEFI 整盘镜像 |
| 分区 | 引导 128 MiB，根分区 4096 MiB |
| 默认访问 | 192.168.1.1，root，初始密码为空，首次登录后设置 |
| 防火墙 | 原生 firewall4/nftables；保留 iptables-nft 兼容层，禁用 legacy |
| 网络加速 | 网络 → Turbo ACC 网络加速；默认开启 BBR + FQ、IPv4 全锥形 NAT |
| 流量卸载 | 软件、硬件、SFE 默认关闭，IPv6 全锥形默认关闭；不编译 SFE |
| 应用 | 41 个 LuCI 应用；702 个包相关配置符号含构建选项，成品包核对完整基线且新增 Honk 依赖 |

TurboACC 基于 chenmozhijin 的 firewall4 分支，固定上游提交，保留 GPL-3.0 许可证。没有运行替换 firewall4/nftables 的上游安装器。适配说明与完整差异见 [配置说明](docs/turboacc-profile.md) 和 [适配补丁](docs/turboacc-immortalwrt-adaptation.diff)。准备脚本会将该差异应用到锁定上游并逐文件核对打包源码。BBR 作用于本机建立的 TCP 连接，普通 LAN 转发不保证提速。流量卸载保持关闭以保留 Bandix、dae 的统计与转发路径。

## 菜单与应用

| 分类 | 主要应用 |
| --- | --- |
| 状态 | 默认状态项，Netdata 最后 |
| 系统 | 软件包、Argon 配置、终端、计划重启、关机、分区扩容 |
| 服务 | AdGuard Home、SmartDNS、DDNS、DDNS-Go、HomeProxy、OpenClash、PassWall、Nikki、DAE/DAED、Honk、vlmcsd、UPnP |
| VPN | OpenVPN、Tailscale、ZeroTier、FRP 客户端/服务端、EasyTier；WireGuard 协议支持 |
| NAS | 磁盘/文件管理、Samba4、远程 CIFS 挂载、OpenList、Aria2、MiniDLNA |
| Docker | 独立一级菜单 |
| 网络 | 接口、路由、防火墙、SQM、多 WAN、wrtbwmon、标准 Bandix、TurboACC |
| 首页/商店 | QuickStart、iStore |

不包含独立 luci-app-bbr、Bandix Plus、PassWall2、AdBlock Fast、Transmission、nlbwmon、acme、https-dns-proxy、irqbalance、banIP。Open-Box 按官方后安装方案处理。

## 构建与验证

在独立 Ubuntu 环境使用非 root 用户：

```sh
bash scripts/install-dependencies.sh
python3 scripts/check-project.py
python3 scripts/check-padding.py
python3 scripts/prepare.py
bash scripts/build.sh
```

prepare 拒绝覆盖已有工作目录；可指定 `--work /new/path`，build.sh 同步传入此路径。下载、工具链、内核与软件包分阶段构建，最终单路打包。镜像零填充改为稀疏复制与按相同块边界扩展，避免为 4GiB 块申请巨量内存；输入边界测试与旧 dd 方法逐字节比对。实际分区和镜像哈希仍须通过成品检查。

本次云构建核验四镜像、分区、SHA256、包清单、移除项、BBR/FQ/eBPF、TurboACC 页面/中文资源/默认值，以及旧独立 BBR 页面和服务确实移除。只有通过后才上传固件。云构建 **不做启动、实际 NAT/代理/吞吐运行测试**，报告明确记录为 false。本地 r6 编译成功不代表本次云任务已通过。历史 r4 测试仅作背景，见 docs/baseline-r4。

## 已知限制

- HTTPS 默认未监听 443。
- squashfs 的 Docker 需要独立 ext4 数据目录。
- OpenClash 独立核心需要按上游说明安装。
- 曾有实际飞牛虚拟机仅出现 lo 的问题，尚未定位，不能视为已修复。
- 未验证本版 Secure Boot、真实代理/VPN 节点、全锥形 NAT 行为或长期负载。

来源和致谢见 [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md)。上游软件与补丁保留各自许可证。
