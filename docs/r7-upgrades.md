# r7 定向升级与 PassWall 修复

系统仍为 ImmortalWrt 25.12.2 / Linux 6.12.103 / x86-64，128 MiB 启动分区与 4096 MiB 根分区。保持 40 个应用、原菜单与中文翻译，标准 Bandix、TurboACC fw4/nftables 适配不变。

升级清单及精确包版本见 `updates.lock.json`；每个上游仓库锁定完整提交，改动过的配方记录 SHA256。仅复制所列包目录，不整体更新 feeds。Netdata、EasyTier、sing-box、Docker、Samba、Shadowsocks Rust、Nikki 页面等保留基线版本；成品验证会逐项检查升级与保留版本。

PassWall 问题：项目旧默认脚本禁用了系统服务入口，网页保存代理总开关后缺少完整服务生命周期。现在保留 PassWall 自启入口，代理总开关仍为上游默认关闭，保留用户升级时的已有配置。采用所选 26.10.22-r1 上游启动锁改进。成品静态检查验证启动链接；运行时开机→配置应用→有效测试节点启动链路需要在本轮隔离虚拟机中验收，静态通过不等于运行测试通过。

Tailscale 1.104.4、OpenList 4.2.9 和 Xray 26.10.21 单独使用 Go 1.27.3 编译工具链；其余包继续使用基线 Go 1.26。只增加主机编译器，不向固件选入 Go 运行工具包。局域网 make defconfig 核验保持 696 个选包配置项（包含新版 PassWall 的 SmartDNS 编译选项；SmartDNS 核心本已选中，版本不变）、40 个应用，无丢包和新增目标运行依赖。

保留限制：OpenClash 页面更新不代表单独内置其独立核心；Open-Box 仍按官方方式后安装。历史版本的运行验收不能代替本轮验证。仅编译和隔离测试，不刷机或部署。

构建完成后会校验四种 BIOS/UEFI、ext4/squashfs 镜像分区与 SHA256、原有全部包、升级版本、保留版本、eBPF/BBR/FQ、无 iptables-legacy、AdGuard Home 中文资源，并导出 manifest 和本轮检查报告。云端构建不宣称已完成本轮启动测试。
