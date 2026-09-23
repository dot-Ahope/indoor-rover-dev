#!/bin/bash
# wifi-mon ARP 중복 검사 패치가 실제 적용됐는지 확인·미적용이면 적용(sudo)
PW=<PW>; S() { echo "$PW" | sudo -S -p '' "$@" 2>&1 | grep -av '^\[sudo\]'; }
if ! grep -q ARP_DUP /usr/local/sbin/wifi_mon.sh; then
  echo "미적용 → 적용"; [ -f /tmp/wifi_mon.new ] && bash -n /tmp/wifi_mon.new && S cp /tmp/wifi_mon.new /usr/local/sbin/wifi_mon.sh && S systemctl restart wifi-mon; sleep 2
fi
echo "wifi_mon.sh ARP_DUP 줄: $(grep -c ARP_DUP /usr/local/sbin/wifi_mon.sh) | 서비스: $(systemctl is-active wifi-mon) | 최근 mon.log: $(tail -2 /var/log/wifi_mon/mon.log | cut -c1-110 | tr '\n' '|')"
echo "ARP_DUP 기록: $(grep -ac ARP_DUP /var/log/wifi_mon/mon.log) 건 | 수동 arping -D 검사: $(timeout 5 arping -D -c 2 -w 2 -I wlP1p1s0 192.168.0.101 2>&1 | tail -1)"
echo "NM DAD: WEB_DEV=$(nmcli -t -f ipv4.dad-timeout con show WEB_DEV_5G | cut -d: -f2) ALOPS=$(nmcli -t -f ipv4.dad-timeout con show ALOPS_ROBOTICS_5G | cut -d: -f2)"
