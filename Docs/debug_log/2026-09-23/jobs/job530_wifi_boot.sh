#!/bin/bash
# 읽기 전용: 오늘 부팅 직후(NTP 전, 1970 타임스탬프) 구간의 무선 이벤트 — mon.log·wpa_debug·syslog, 그리고 AP 재스캔
echo "## mon.log: 오늘 부팅 블록(마지막 1970 블록 + 첫 2026 줄)"; awk '/^1970-01-01/ {b=b"\n"$0; n++} /^2026-09-23/ && !p {print b; print "--- 첫 2026 줄:"; print; p=1}' /var/log/wifi_mon/mon.log | grep -av "^$" | tail -45 | cut -c1-170
echo "## wpa_debug.log: 오늘 부팅 블록의 이벤트(Jan  1 09:0x)"; grep -aE "^Jan  1 09:0[0-9]" /var/log/wifi_mon/wpa_debug.log | grep -aE "deauth|disassoc|reason|Authentication|ASSOC|CTRL-EVENT|Trying to associate|Associated with|4-Way|EAPOL|SSID-TEMP|BEACON-LOSS|roam|Skip|blacklist|BSS .* ignore|WPA: Key negotiation" | tail -60 | cut -c1-175
echo "## syslog: 오늘 부팅 블록 NM(Jan  1 09:0x)"; grep -aE "^Jan  1 09:0[0-9]" /var/log/syslog | grep -aE "NetworkManager|wpa_supplicant" | grep -aiE "deauth|disconnect|auth|assoc|reason|fail|timeout|roam|activat|WEB_DEV|ALOPS|supplicant interface state|no-secrets|secrets" | tail -50 | cut -c1-190
echo "## AP 재스캔"; nmcli dev wifi rescan 2>/dev/null; sleep 4; nmcli -t -f SSID,BSSID,CHAN,FREQ,SIGNAL dev wifi list 2>/dev/null | grep -aE "WEB_DEV|ALOPS" | head -6
echo "## NM 로그(현재 부팅, journal) WEB_DEV 관련 마지막 30 줄"; journalctl -b -u NetworkManager --no-pager 2>/dev/null | grep -aiE "WEB_DEV|deauth|reason|auth|no-secrets|activation|fail" | tail -30 | cut -c1-190
