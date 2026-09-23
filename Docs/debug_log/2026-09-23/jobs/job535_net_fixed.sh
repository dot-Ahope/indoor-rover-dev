#!/bin/bash
# 2026-09-23 사용자 지시: 고정 IP(공유기 DHCP 예약) 방식으로 WEB_DEV_5G 로 되돌리고, IP 충돌을 잡도록 설정. sudo 사용(비밀번호는 표준입력).
#   1) NM 두 프로파일에 ipv4.dad-timeout 3000(ms): 주소 설정 전 ARP 중복 검사 — 충돌이면 활성화 실패 + NM 로그 "duplicate address"
#   2) wifi_mon.sh 15 s 루프에 arping -D(중복 주소 탐지) 추가 → mon.log "ARP_DUP" + 스냅샷 (iputils-arping 설치 필요)
#   3) WEB_DEV_5G 로 전환(nmcli con up) — 이 ssh 세션은 끊긴다(백그라운드로 실행)
set +u
PW=<PW>
S() { echo "$PW" | sudo -S -p '' "$@" 2>&1 | grep -av '^\[sudo\]'; }
echo "## 1. 도구 설치(apt, 60 s 한도)"; S timeout 90 apt-get install -y -qq iputils-arping tcpdump 2>&1 | tail -2; echo "  arping=$(command -v arping || echo 없음) tcpdump=$(command -v tcpdump || echo 없음)"
echo "## 2. NM DAD 3 s"; for c in WEB_DEV_5G ALOPS_ROBOTICS_5G; do S nmcli con modify "$c" ipv4.dad-timeout 3000; echo "  $c dad-timeout=$(nmcli -t -f ipv4.dad-timeout con show "$c" | cut -d: -f2)"; done
echo "## 3. wifi_mon.sh 에 ARP 중복 검사 추가"
if grep -q ARP_DUP /usr/local/sbin/wifi_mon.sh; then echo "  이미 있음"; else
python3 - <<'PY'
p='/usr/local/sbin/wifi_mon.sh'; s=open(p).read()
old='  log "LINK bssid=${bssid:-none} ssid=${ssid:-} freq=${freq:-} sig=${sig:-} rx=${rx:-} tx=${tx:-} ip=${ip4:-} $st"\n'
new=old+'''  # 2026-09-23: IP 충돌 감지 — 내 IP 로 ARP 중복 탐지(arping -D). 다른 MAC 이 응답하면 ARP_DUP 기록 + 스냅샷(5 분에 1 번만)
  if [ -n "$ip4" ] && command -v arping >/dev/null 2>&1; then
    dup=$(timeout 5 arping -D -c 2 -w 2 -I $IF "${ip4%%/*}" 2>&1 | grep -a "Unicast reply" | head -1)
    if [ -n "$dup" ]; then log "ARP_DUP ip=${ip4%%/*} $dup"; now=$(date +%s); if [ $((now - ${last_dup:-0})) -ge 300 ]; then snapshot "arp dup ${ip4%%/*}"; last_dup=$now; fi; fi
  fi
'''
assert old in s; open('/tmp/wifi_mon.new','w').write(s.replace(old,new,1)); print('  패치 생성')
PY
bash -n /tmp/wifi_mon.new && S cp /tmp/wifi_mon.new /usr/local/sbin/wifi_mon.sh && S systemctl restart wifi-mon && sleep 2 && echo "  wifi-mon: $(systemctl is-active wifi-mon) | ARP_DUP 줄 $(grep -c ARP_DUP /usr/local/sbin/wifi_mon.sh)"
fi
echo "## 4. WEB_DEV_5G 로 전환(3 s 뒤, 백그라운드) — 이 세션은 끊김"; echo "$PW" | nohup sudo -S -p '' bash -c 'sleep 3; nmcli con up WEB_DEV_5G' >/tmp/net_switch.log 2>&1 &
sleep 1; echo "  요청됨 $(date +%T)"
