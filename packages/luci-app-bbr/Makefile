include $(TOPDIR)/rules.mk

LUCI_TITLE:=TCP BBR network acceleration
LUCI_DEPENDS:=+luci-base +kmod-tcp-bbr +kmod-sched
LUCI_PKGARCH:=all
PKG_VERSION:=1.0.0
PKG_RELEASE:=1
PKG_LICENSE:=MIT

define Package/luci-app-bbr/conffiles
/etc/config/bbr
endef

include $(TOPDIR)/feeds/luci/luci.mk

# call BuildPackage - OpenWrt buildroot signature
