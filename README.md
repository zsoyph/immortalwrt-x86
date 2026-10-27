# ImmortalWrt x86/64 r6 TurboACC 云编译

[![Build](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml/badge.svg)](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml)

ImmortalWrt **25.12.2 / Linux 6.12.103**，x86/64。r6 用 **TurboACC 1.4** 替换独立 BBR 页面，保留标准 Bandix、AdGuard Home LuCI 中文、分区扩容、关机及其余已选插件。完整源码提交锁定在 [sources.lock.json](sources.lock.json)。

## 云编译与下载

打开 [Actions](https://github.com/zsoyph/immortalwrt-x86/actions/workflows/build-immortalwrt.yml)，选择 **Run workflow**。main 的构建配置或源码变化也会触发。成功后在本次运行的 Artifacts 下载 `immortalwrt-25.12.2-x86-64-r6-turboacc-运行编号`，保留 **14 天**；诊断日志保留 7 天。不自动发布 Release、不刷机，不需要个人令牌或局域网编译机凭据。云端使用 GitHub 托管 Ubuntu 24.04，工作流只申请 contents:read。

## 本版配置

| 项目 | 内容 |
| --- | --- |
| 镜像 | ext4、squashfs，分别提供 BIOS/UEFI 整盘镜像 |
| 分区 | 引导 128 MiB，根分区 4096 MiB |
| 默认访问 | 192.168.1.1，root，初始密码为空，首次登录后设置 |
| 防火墙 | 原生 firewall4/nftables；保留 iptables-nft 兼容层，禁用 legacy |
| 网络加速 | 网络 → Turbo ACC 网络加速；默认开启 BBR + FQ、IPv4 全锥形 NAT |
| 流量卸载 | 软件、硬件、SFE 默认关闭，IPv6 全锥形默认关闭；不编译 SFE |
| 应用 | 40 个 LuCI 应用，预期 667 个成品软件包；695 个包相关配置符号含构建选项 |

TurboACC 基于 chenmozhijin 的 firewall4 分支，固定上游提交，保留 GPL-3.0 许可证。没有运行替换 firewall4/nftables 的上游安装器。适配说明与完整差异见 [配置说明](docs/turboacc-profile.md) 和 [适配补丁](docs/turboacc-immortalwrt-adaptation.diff)。准备脚本会将该差异应用到锁定上游并逐文件核对打包源码。BBR 作用于本机建立的 TCP 连接，普通 LAN 转发不保证提速。流量卸载保持关闭以保留 Bandix、dae 的统计与转发路径。

## 菜单与应用

| 分类 | 主要应用 |
| --- | --- |
| 状态 | 默认状态项，Netdata 最后 |
| 系统 | 软件包、Argon 配置、终端、计划重启、关机、分区扩容 |
| 服务 | AdGuard Home、SmartDNS、DDNS、DDNS-Go、HomeProxy、OpenClash、PassWall、Nikki、DAE/DAED、vlmcsd、UPnP |
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
