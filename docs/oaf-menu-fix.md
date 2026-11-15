# OAF 单菜单 / quickstart 首页直连（r10 热修）

## 现象

【服务】下出现两个「应用过滤」入口。直接删掉别名后，quickstart 首页卡片「家长控制」又报 404 —— 浏览器还缓存着指向旧别名的 JS。

## 根因

`luci-app-oaf` 的 controller 为兼容 quickstart 首页链接，额外注册了
`admin/services/appfilter` 这个 alias，并标了 `page.hidden = true`。但 ImmortalWrt 25.12 的
ucode dispatcher 和 argon 主题菜单渲染都**不处理 hidden**，别名照常渲染成第二个菜单。
quickstart 前端 `index.js` 里有 2 处链接指向该别名，所以不能只删 entry 了事。

## 修复（11-15 另一会话上机实测，本仓库固化）

1. `patches/oaf.patch`：删掉 alias entry，只保留 `admin/services/oaf`（标题「应用过滤」）。
2. `files/www/luci-static/quickstart/index.js`：2 处 `admin/services/appfilter` →
   `admin/services/oaf`。该文件与 nas-luci 锁定提交 `93e94175` 的源码逐字节一致，
   仅这两处替换（498237 → 498225 B）。
3. `files/usr/lib/lua/luci/view/quickstart/main.htm`：3 处静态资源版本串由模板占位
   `<%# ?v=PKG_VERSION %>` 写死为 `?v=0.12.10-r1qs2`，强制浏览器丢弃缓存的旧 JS。
4. `files/etc/uci-defaults/96-quickstart-nju`：首启把上述 3 个包文件备份到
   `/root/oaf-single-menu`；`rc.local` 的 `oaf-menu-guard` 在 `apk upgrade` 还原官方文件后
   自动恢复，并清掉 `/tmp/luci-indexcache.*.json` 重建菜单。

三个文件都通过 `files/` overlay 覆盖进 rootfs，与 quickstart 补丁 ELF 同一机制；
OAF controller 由源码补丁直接生成。

## 云端验证

`check-project.py` 与 `verify-output.py` 断言：oaf.lua 无 alias、index.js 零 `appfilter`
且 2 处 `admin/services/oaf`、main.htm 3 处 `r1qs2`、守卫存在。
本轮云编译只做产物校验，未做上机启动与点击测试。
