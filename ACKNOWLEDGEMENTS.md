# 来源与致谢

感谢以下项目的维护者和贡献者。具体源码提交以 [sources.lock.json](sources.lock.json) 为准，固件软件版本以本次 manifest 为准。

| 项目 | 用途 |
| --- | --- |
| [OpenWrt](https://github.com/openwrt/openwrt) | 基础构建系统与社区 |
| [ImmortalWrt](https://github.com/immortalwrt/immortalwrt) | 本项目实际固件基线 |
| [ImmortalWrt LuCI](https://github.com/immortalwrt/luci)、[packages](https://github.com/immortalwrt/packages)、[routing](https://github.com/openwrt/routing) | 官方软件源与管理界面 |
| [openwrt-daede](https://github.com/kenzok8/openwrt-daede)、[dae](https://github.com/daeuniverse/dae)、[daed](https://github.com/daeuniverse/daed) | eBPF 代理组件及 LuCI 集成 |
| [iStore](https://github.com/istoreos/istore)、[linkease/iStore](https://github.com/linkease/istore) | 软件商店；本次实际锁定 istoreos/istore |
| [nas-packages-luci](https://github.com/linkease/nas-packages-luci)、[nas-packages](https://github.com/linkease/nas-packages)、[QuickStart](https://github.com/istoreos/quickstart) | NAS 功能和 QuickStart；当前集成来自 NAS 包仓库 |
| [OpenWrt-nikki](https://github.com/nikkinikki-org/OpenWrt-nikki) | Nikki/Mihomo 集成 |
| [luci-app-bandix](https://github.com/timsaya/luci-app-bandix)、[openwrt-bandix](https://github.com/timsaya/openwrt-bandix) | 标准 Bandix 前端和后端打包 |
| [luci-app-wrtbwmon](https://github.com/brvphoenix/luci-app-wrtbwmon)、[wrtbwmon](https://github.com/brvphoenix/wrtbwmon) | 实时带宽统计 |
| [AdGuard Home](https://github.com/AdguardTeam/AdGuardHome) | DNS 过滤服务；本项目补充其 LuCI 插件中文翻译 |
| [Open-Box](https://github.com/liandu2024/Open-Box) | 用户选择的官方后安装项目，本固件未打包 |
| [GitHub Actions](https://github.com/features/actions) | 云编译执行环境 |

此外感谢内核、netfilter/nftables、Docker、Samba、OpenList、FRP、Tailscale、ZeroTier、WireGuard、OpenVPN、Nikki、OpenClash、PassWall、Argon 等所有被集成组件的上游作者。软件包的具体许可证以各包源码和安装文件为准。

本项目的配置、菜单调整和中文翻译没有改变上游软件的许可证。再分发固件时，应按各组件的许可证保留版权信息，并提供相应源码、补丁和构建信息。
