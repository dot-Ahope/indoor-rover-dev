#!/bin/bash
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true; bash -n /tmp/wifi_mon.sh || exit 1
S install -o root -g root -m 0755 /tmp/wifi_mon.sh /usr/local/sbin/wifi_mon.sh
S systemctl restart wifi-mon; sleep 80
S tail -n 8 /var/log/wifi_mon/mon.log | cut -c1-200
echo "wpa_debug.log $(S stat -c %s /var/log/wifi_mon/wpa_debug.log) B, 로그 수준 $(S wpa_cli log_level | awk -F': ' '/Current/{print $2}'), 서비스 $(systemctl is-active wifi-mon)/$(systemctl is-enabled wifi-mon)"
