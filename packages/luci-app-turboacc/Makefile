# SPDX-Identifier-License: GPL-3.0-only
#
# Copyright (C) 2023-2024 沉默の金 <cmzj@cmzj.org>
# Copyright (C) 2022 Lean <coolsnowwolf@gmail.com>
# Copyright (C) 2019-2022 ImmortalWrt.org

include $(TOPDIR)/rules.mk

PKG_NAME:=luci-app-turboacc
PKG_VERSION:=1.4
PKG_RELEASE:=2
PKG_LICENSE:=GPL-3.0-only
PKG_MAINTAINER:=chenmozhijin <cmzj11@gmail.com>
LUCI_TITLE:=TurboACC for native ImmortalWrt firewall4
LUCI_DEPENDS:=+luci-base +luci-compat +kmod-tcp-bbr +kmod-nft-offload +kmod-nft-fullcone +kmod-sched
LUCI_PKGARCH:=all

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature
