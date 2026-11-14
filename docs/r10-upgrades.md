# r10 五包升级方案（2026-11-14）

在 r9 OAF 版（run#24 / `c46ee06`）成功基线上的一次保守升级。基线、内核、OAF、quickstart 补丁、网口规划、南大源、开机自启逻辑全部不动。

## 范围

老板从 [上游可升级清单] 中选定 **1 / 2 / 3 / 4 / 6** 五项；其余（frp 0.72.0、sing-box、netdata 2.x、Samba、Docker、ss-rust、Rust 1.96.1）本轮不升，linkease quickstart 源、核心基线、Netdata/EasyTier 冻结项继续冻结。

| # | 包 | 当前 → 目标 | 锁定来源 |
| --- | --- | --- | --- |
| 1 | ddns-scripts / ddns-scripts-services | 2.8.4-r8 → **2.8.5-r1** | `immortalwrt/packages` `12ec335dae2f`（2026-11-10 `ddns-scripts: update to 2.8.5`），整目录 `net/ddns-scripts` |
| 2 | luci-app-partexp | `236187c` → **`ef79d6b8`** | sirpdboy 上游合并 `fix/overlay-copy`，仅改 `root/usr/bin/partexp` |
| 3 | Go 1.27 主机工具链 | 1.27.3 → **1.27.4** | 上游 `db68036`（`golang: bump 1.27 to 1.27.4`），两行补丁：`GO_VERSION_PATCH` + `PKG_HASH` |
| 4 | Tailscale | 1.104.6-r2 → **1.104.7-r1** | 官方 2026-11-12 release；`go.mod` 要求 `go 1.27.4` |
| 6 | Honk 核心 | beta.3 → **beta.6** | `daeuniverse/honk` 2026-11-08 预发布，x86_64 静态 musl full 包 + Doona rc.6 源码归档 |

## 依赖链

```
Go 1.27.4 (#3)
   └── Tailscale 1.104.7 (#4)   ← go.mod: go 1.27.4，1.27.3 编不过
```

Go 工具链仍由 `golang1.27/host` 提供，AGH / Xray / daed / OpenList 同步使用 1.27.4（同 minor，向后兼容）。Tailscale **只在 overlay 里改版本号和源码 hash**，`PKG_BUILD_DEPENDS:=golang1.27/host` 保持不变；之前撤销过的 init/ucode 功能改动本轮没有恢复。

## 改动文件

- `sources.lock.json`：新增 `packages-ddns`（不可变 commit）；`partexp` commit 更新
- `updates.lock.json`：`net/ddns-scripts` 改从 `packages-ddns` 取；三项 `expected_versions`；`host_toolchains` 说明；两条 `overlay_sha256`
- `overlays/packages/net/tailscale/Makefile`：`PKG_VERSION` / `PKG_RELEASE` / `PKG_HASH`
- `overlays/packages/lang/golang/golang1.27/Makefile`：新增，逐字复制 `006a19cb` 版 + 上游两行 bump
- `packages/honk/Makefile`、`honk.lock.json`、`local-downloads.json`：beta.6 包名、URL、三处 sha256
- `scripts/verify-output.py`：`honk-core --version` 断言改 `0.1.0-beta.6`
- `.github/workflows/build-immortalwrt.yml`：构建摘要版本串
- `README.md`、`docs/r10-upgrades.md`：升级说明

所有新 hash 均在本地下载原始包复算：

| 包 | sha256 |
| --- | --- |
| `tailscale-1.104.7.tar.gz`（codeload，Makefile 同款 URL） | `fa1c922b33d0f6db6b073800d7a62fa84081323d247b21547c63a98ed7ecac14` |
| `honk-core-v0.1.0-beta.6-x86_64-unknown-linux-musl-full.tar.gz` | `2783b8f0856fc1aecd1cd1d911d9a904c593cd507cf61e5fa24fbd7075317244` |
| `doona-source-0.1.0-rc.6.tar.gz` | `c972116aa66aa27e76f27ccea92b661ecbc09d3c1c3e2e8ba3d31e489bdacb3a` |
| `go1.27.4.src.tar.gz` | `73cfb8571aec0c01177687db87163d46aa20e9779672772891aa17654d9a6099`（上游 bump 提交给出） |

## 风险控制

- 版本与二进制由 `overlay_sha256` / `package_sha256` 双锁固定，任何回退或误改都会让 `check-project.py` 在编译前失败
- quickstart 0.13.0 的 NJU ELF 补丁、rc.local 守卫、S42 清缓存逻辑一字未动，**不升级 linkease 源**（上游已到 0.17.1-rc，会让补丁失效）
- Netdata / EasyTier / sing-box / Docker / Samba 等冻结项不动；核心 25.12.2 / 6.12.103 不动，OAF kmod 无需重编
- Honk beta.6 包结构（`honk-core`、`LICENSE`、`doona/`）与 beta.3 一致；release 说明里的变更为新增 `global.syslog_*` 可选项和移除 mimalloc 环境变量，现有 `config.dae` 无这些字段，保持兼容
- ddns-scripts 取自滚动 master，相对稳定分支存在服务商脚本增删；云端只校验包版本，**未做 DDNS 上机实测**

## 云端验证点

1. `check-project.py`：706 符号 / 42 应用 / config_sha256 不变，overlay 与 Honk 配方 hash 全匹配
2. 编译期：Go 1.27.4 能正常构建 host 工具链并编出 Tailscale 1.104.7
3. `verify-output.py`：manifest 中 `ddns-scripts`、`ddns-scripts-services`、`tailscale`、`honk` 四项版本精确匹配；`honk-core --version` 含 `0.1.0-beta.6`；6 个镜像 + manifest 校验和全 OK
4. 未做：本轮隔离启动、DDNS 拨测、Honk 流量识别与 Doona 实测

## 回滚

`git revert <本轮提交>` 后重新触发云编译即可回到 run#24 的 r9 基线；已刷入设备的固件需重新刷回 r9 镜像（保留配置时建议核对 `honk` 与 `tailscale` 的配置项）。
