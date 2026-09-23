#!/bin/bash
# PC: 네트워크 전환 실행 → 90 s 동안 두 IP 핑 → 붙은 쪽에서 상태·NM 로그 확인
NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
tr -d '\r' < $NSPS/job535_net_fixed.sh > /tmp/job535_net_fixed.sh; sshpass -p <PW> scp $O -q /tmp/job535_net_fixed.sh jetson@172.30.1.8:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $O jetson@172.30.1.8 "bash /tmp/job535_net_fixed.sh"
echo "## 전환 대기(핑)"; T0=$(date +%s); H=""
while [ $(( $(date +%s) - T0 )) -lt 120 ]; do
  for c in 192.168.0.101 172.30.1.8; do ping -c1 -W1 $c >/dev/null 2>&1 && { H=$c; break; }; done
  [ -n "$H" ] && [ "$H" = 192.168.0.101 ] && break; [ -n "$H" ] && [ $(( $(date +%s) - T0 )) -gt 60 ] && break
  sleep 3
done
echo "  $(( $(date +%s) - T0 )) s 뒤 응답: ${H:-없음}"
[ -z "$H" ] && exit 1
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'echo "## 결과: $(nmcli -t -f NAME,DEVICE con show --active | grep wl) | IP $(ip -4 -o addr show dev wlP1p1s0 | awk "{print \$4}")"; echo "## net_switch.log: $(cat /tmp/net_switch.log 2>/dev/null | tr "\n" "|" | cut -c1-200)"; echo "## NM 로그(최근 3 분): "; journalctl -u NetworkManager --since "-3 min" --no-pager 2>/dev/null | grep -aiE "WEB_DEV|dhcp4|duplicate|dad|activated|failed|ALOPS" | tail -12 | cut -c1-160; echo "## mon.log 꼬리:"; tail -3 /var/log/wifi_mon/mon.log | cut -c1-150'
