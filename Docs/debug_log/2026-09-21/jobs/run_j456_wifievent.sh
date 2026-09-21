#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'f=$(ls -t /var/log/wifi_mon/event_*.txt | head -1); echo "== $f ($(wc -l < $f) 줄)"; head -40 $f | cut -c1-160
echo "== wifi_mon.log 09-18 17:3x~17:4x"; grep -a "2026-09-18 17:[34]" /var/log/wifi_mon/wifi_mon.log 2>/dev/null | grep -av "BEACON" | head -12 | cut -c1-160
echo "== wpa_debug 17:39~17:41 (DISCONNECT/ASSOC/reason/CSA/DFS)"; grep -aE "17:(39|40|41):" /var/log/wifi_mon/wpa_debug.log 2>/dev/null | grep -aiE "disconnect|reason|assoc|auth|CSA|DFS|beacon loss|radar" | head -15 | cut -c1-170
echo "== syslog 09-18 17:39~17:41 NM/wpa"; grep -aE "^Sep 18 17:(39|40|41)" /var/log/syslog 2>/dev/null | grep -aiE "wpa_supplicant|NetworkManager" | grep -aiE "disconnect|reason|connected|activat|deactiv|fail|auth" | head -12 | cut -c1-170
echo "== 오늘 부팅 후 접속: $(grep -a "$(date +%b\ %e)" /var/log/syslog | grep -a "CTRL-EVENT-CONNECTED\|CTRL-EVENT-DISCONNECTED" | tail -3 | cut -c1-110 | tr "\n" ";")"'
