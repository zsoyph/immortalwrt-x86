'use strict';
'require view';
'require form';
'require fs';

return view.extend({
	load: function() {
		return Promise.all([
			L.resolveDefault(fs.read('/proc/sys/net/ipv4/tcp_congestion_control'), '未知'),
			L.resolveDefault(fs.read('/proc/sys/net/ipv4/tcp_available_congestion_control'), '未知'),
			L.resolveDefault(fs.read('/proc/sys/net/core/default_qdisc'), '未知')
		]);
	},
	render: function(data) {
		var m = new form.Map('bbr', '网络加速（BBR）',
			'BBR 用于路由器本机建立的 TCP 连接，包括代理、下载等；普通 LAN 转发流量不会因此自动提速。保留 firewall4/nftables，流量卸载继续关闭。');
		var s = m.section(form.NamedSection, 'main', 'bbr', 'TCP 拥塞控制');
		var o = s.option(form.DummyValue, '_current', '当前算法');
		o.cfgvalue = function() { return data[0].trim(); };
		o = s.option(form.DummyValue, '_available', '可用算法');
		o.cfgvalue = function() { return data[1].trim(); };
		o = s.option(form.DummyValue, '_qdisc', '默认队列');
		o.cfgvalue = function() { return data[2].trim(); };
		o = s.option(form.Flag, 'enabled', '启用 BBR',
			'开启使用 BBR，关闭切回 CUBIC；均使用 FQ 默认队列。保存并应用后影响新建 TCP 连接。默认队列变化不会替换现有接口队列，需重启后生效；SQM 的接口队列配置保持优先。');
		o.default = '1';
		o.rmempty = false;
		return m.render();
	}
});
