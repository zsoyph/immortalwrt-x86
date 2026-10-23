# ImmortalWrt r4：AdGuard Home LuCI 中文版

2026-10-23（北京时间）。基于 r3 标准 Bandix 版，仅增加 AdGuard Home LuCI 插件简体中文翻译。编译于 09:52:28 开始、10:01:11 成功结束，耗时约 8 分 43 秒；隔离启动测试于 10:07:13 完成。未刷机或部署。

## 改动与版本

- ImmortalWrt 25.12.2、Linux 6.12.103、x86/64；保留标准 Bandix，其余插件与菜单不变。
- 新增 `luci-i18n-adguardhome-zh-cn`，成品 manifest 共 649 包、36 个 LuCI 应用。
- 翻译目录新增 `po/zh_Hans/adguardhome.po`，36 条条目包括 35 条中文翻译及保留的品牌名 AdGuard Home。
- 覆盖运行状态、配置项、说明、输入校验和权限说明；原来硬编码的“unknown version”已接入翻译，显示“未知版本”。配置键、路径和 Go 环境变量名保持原样。
- 中文翻译编译为 `/usr/lib/lua/luci/i18n/adguardhome.zh-cn.lmo` 并纳入固件。归档附 PO 和包含新增文件的完整补丁，便于复现与审查。
- 本轮汉化范围为 LuCI 插件。独立 AdGuard Home Web 控制台未修改；服务默认仍不自启，DNS 配置不变。

## 实际验证

使用镜像快照副本，在隔离网络中分别以 BIOS/VirtIO 和 UEFI/VirtIO 启动，两者均通过以下检查：

| 项目 | 结果 |
| --- | --- |
| LAN | br-lan 存在，地址 192.168.1.1/24，LuCI 可访问 |
| AdGuard Home 页面 | LuCI 插件页面及对应配置脚本均 HTTP 200 |
| 中文资源 | 实际 `/cgi-bin/luci/admin/translations/zh-cn` 响应包含全部 35 条中文译文和保留品牌条目 |
| 翻译调用 | 配置脚本的未知版本提示已使用翻译函数 |
| 成品资源 | LMO 存在，manifest 含中文语言包 |
| 防火墙 | fw4 检查通过，iptables 使用 nf_tables 兼容层 |
| 镜像 | 四种整盘镜像的校验和及 128/4096 MiB 分区检查通过 |

没有进行图形浏览器截图验收，不能据此声称已逐项视觉检查页面；上述结论来自实际运行页面、脚本和翻译 HTTP 响应，而非仅检查 PO 文件存在。没有启用 AdGuard Home 做 DNS 解析测试，其他未修改插件本轮没有重复功能测试。

## 本地验收基线产物

本报告记录已完成的本地 r4 验收，不代表后续云编译产物自动通过同样的运行测试。云端固件从 Actions 构建记录的 Artifacts 下载。

| 整盘镜像 | 压缩大小（约） |
| --- | --- |
| squashfs BIOS | 298.2 MiB |
| squashfs UEFI | 298.4 MiB |
| ext4 BIOS | 368.6 MiB |
| ext4 UEFI | 368.8 MiB |

解压后约 4.13 GiB，包含 4096 MiB 根分区预留空间。旧 r2、r3 产物独立保留。

默认 LAN 为 `192.168.1.1/24`，管理地址 `http://192.168.1.1`，账号 `root`，初始密码为空，首次登录后设置。

## 保留限制

- HTTPS 默认未监听 443。
- squashfs 版 Docker 需要独立 ext4 数据目录，默认 overlay 叠加限制未修复。
- OpenClash 独立核心仍缺失。
- 实际飞牛虚拟机只有 lo 的问题仍未定位，隔离 VirtIO 测试不能替代该环境实测。
- Open-Box 沿用确认过的官方后安装方案，没有打包进固件。
- 未测试 Secure Boot、squashfs 启动、真实外部代理/VPN 节点或长时间负载。

此前版本做过标准 Bandix/dae 共存和 CIFS/vlmcsd 功能检查；这些功能本轮未重复测试。

## 证据与交付状态

归档包含 `adguardhome.po`、`adguardhome-zh.patch`、`runtime-test-summary.json`、脱敏的 `vm-r4-test.json`、实际翻译响应、manifest、配置和源码提交记录。

配置 SHA256：`450e671a55e13916df5951b148bbce7ab25512ca0f84662d6e6a46a13c0e5457`。

本地传输于 10:47:25 完成；10:49:31 独立复核全部 33 个归档文件的 SHA256 均通过，连同校验清单共 34 个文件。网络中断期间使用断点续传，最终没有跳过散列核验。两项旧传输临时文件已清理。
