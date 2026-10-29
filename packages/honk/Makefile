# SPDX-License-Identifier: GPL-3.0-only
# Runtime integration from daeuniverse/openwrt-packages; official static full release.
include $(TOPDIR)/rules.mk

PKG_NAME:=honk
PKG_VERSION:=0.1.0_beta3
PKG_RELEASE:=1
PKG_SOURCE:=honk-core-v0.1.0-beta.3-x86_64-unknown-linux-musl-full.tar.gz
PKG_SOURCE_URL:=https://github.com/daeuniverse/honk/releases/download/v0.1.0-beta.3/
PKG_HASH:=101b1f9bed80eff0a9287fbb7a6d9b933f30e8d9b511fad738d48c501cb8e55c
PKG_LICENSE:=GPL-3.0-only
PKG_LICENSE_FILES:=LICENSE
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk

define Package/honk
  SECTION:=net
  CATEGORY:=Network
  SUBMENU:=Web Servers/Proxies
  TITLE:=Honk eBPF transparent proxy with embedded Doona
  URL:=https://github.com/daeuniverse/honk
  DEPENDS:=@TARGET_x86_64 +ca-bundle +kmod-veth +kmod-sched-core +kmod-sched-bpf +kmod-nft-core +kmod-nft-queue +kmod-nfnetlink-queue +kmod-nf-conntrack +v2ray-geoip +v2ray-geosite +jsonfilter
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(TAR) -xzf $(DL_DIR)/$(PKG_SOURCE) -C $(PKG_BUILD_DIR) --strip-components=1
endef

define Build/Configure
endef

define Build/Compile
endef

define Package/honk/conffiles
/etc/config/honk
/etc/honk/config.dae
endef

define Package/honk/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/honk-core $(1)/usr/bin/honk-core
	$(INSTALL_DIR) $(1)/usr/share/licenses/honk
	$(INSTALL_DATA) $(PKG_BUILD_DIR)/LICENSE $(1)/usr/share/licenses/honk/LICENSE
	$(CP) $(PKG_BUILD_DIR)/doona $(1)/usr/share/licenses/honk/doona
	$(INSTALL_DIR) $(1)/etc/init.d $(1)/etc/config $(1)/etc/honk $(1)/usr/share/honk
	$(INSTALL_BIN) ./files/honk.init $(1)/etc/init.d/honk
	$(INSTALL_CONF) ./files/honk.config $(1)/etc/config/honk
	$(INSTALL_CONF) ./files/config.dae $(1)/etc/honk/config.dae
	$(LN) ../v2ray/geoip.dat $(1)/usr/share/honk/geoip.dat
	$(LN) ../v2ray/geosite.dat $(1)/usr/share/honk/geosite.dat
endef

$(eval $(call BuildPackage,honk))
