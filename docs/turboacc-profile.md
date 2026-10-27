# R6 TurboACC profile

Based on delivered R5, replacing luci-app-bbr with TurboACC 1.4-r2 and its Chinese translations. Upstream chenmozhijin/turboacc luci branch is pinned in sources.lock.json. Adaptation diff is retained here. GPL-3.0 license and original copyrights retained.

Native ImmortalWrt firewall4/nftables and fullcone modules remain unchanged. The upstream installer is not run. No SFE engine is compiled. Dependencies use existing native BBR/FQ and nft modules. IPv4 fullcone and BBR default on; IPv6 fullcone and all flow offloads default off to preserve Bandix/dae paths. The page remains under Network, order 95. Fullcone6 writes the native global firewall defaults option. FQ and congestion choice persist on sysctl reload. Upstream zh_Hans symlink is materialized for Windows archive portability.

667 expected manifest packages, 40 LuCI apps, 695 package-related config symbols. Keep partition expansion, poweroff and all other selected apps. No runtime validation is inherited from historical firmware.
