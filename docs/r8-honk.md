# r8 Honk
在 r7 全部插件和锁定版本上新增 Honk 官方 v0.1.0-beta.3 完整版（预发布），官方 LuCI 管理页及中文共享组件。Honk 核心使用官方已编译的 x86_64 静态 musl 完整包，在 OpenWrt 中打包进固件，不宣称本地重编译 Rust 核心。包含真实 eBPF 和嵌入式 Doona。
服务/Honk：状态、配置编辑、日志。Doona 默认仅监听 127.0.0.1:9527，SSH 端口转发访问；Clash API 127.0.0.1:19090。默认总开关关闭、服务入口启用，以保留网页配置变更生命周期。与 DAE/DAED 不能同时运行，启动前检查进程，不修改现有 DAE 配置。
新增 NFQUEUE 内核模块，复核 BTF/eBPF/cgroup v2。Netdata、EasyTier及其余 r7 包不升级；不刷机部署。
锁定来源、SHA256、GPL许可证及 Doona 第三方声明见 honk.lock.json、固件 /usr/share/licenses/honk；对应源码见 https://github.com/daeuniverse/honk/tree/v0.1.0-beta.3 和锁定的 Doona 源码归档。
静态打包检查与运行测试分别报告，未进行的测试不称通过。
