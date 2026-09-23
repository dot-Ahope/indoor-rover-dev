#!/bin/bash
# 읽기 전용: 09-18 설치한 wifi-mon 기록과 syslog 의 무선 이벤트 회수 (2026-09-23 끊김 분석)
echo "## 지금: $(date '+%F %T') | 부팅 $(uptime -s) | $(nmcli -t -f NAME,DEVICE,STATE con show --active | tr '\n' ' ')"
echo "## nmcli 프로파일(autoconnect·우선순위·절전)"; for c in WEB_DEV_5G ALOPS_ROBOTICS_5G; do echo "  $c: $(nmcli -t -f connection.autoconnect,connection.autoconnect-priority,802-11-wireless.powersave con show "$c" 2>/dev/null | tr '\n' ' ')"; done
echo "## 보이는 AP"; nmcli -t -f SSID,BSSID,CHAN,SIGNAL,SECURITY dev wifi list 2>/dev/null | grep -aE "WEB_DEV|ALOPS" | head -6
echo "## wifi_mon 디렉터리"; ls -la --time-style=+%m-%d_%H:%M /var/log/wifi_mon/ 2>/dev/null | awk '{print $6, $5, $7}' | tail -15
echo "## wifi-mon 서비스: $(systemctl is-active wifi-mon 2>/dev/null)"
echo "## mon.log 마지막 40 줄"; tail -40 /var/log/wifi_mon/mon.log 2>/dev/null | cut -c1-160
echo "## event 스냅샷(최근 2 개) 머리"; for f in $(ls -t /var/log/wifi_mon/event_*.txt 2>/dev/null | head -2); do echo "--- $f"; head -25 "$f" | cut -c1-160; done
echo "## wpa_debug.log: deauth/disassoc/reason/auth 실패 (09-22 16:00 이후)"; grep -aE "deauth|disassoc|reason=|Authentication|4-Way|EAPOL.*fail|CTRL-EVENT-(DISCONNECTED|CONNECTED|ASSOC-REJECT|AUTH-REJECT|SSID-TEMP-DISABLED|BEACON-LOSS)|Trying to associate" /var/log/wifi_mon/wpa_debug.log 2>/dev/null | grep -aE "Sep 2[23]" | grep -avE "Sep 22 (0[0-9]|1[0-5]):" | tail -60 | cut -c1-170
echo "## syslog NM/wpa/커널 무선 (09-22 16:00 이후)"; grep -aE "NetworkManager|wpa_supplicant|iwlwifi|wlP1p1s0|rtw|brcm" /var/log/syslog 2>/dev/null | grep -aE "^Sep 2[23]" | grep -avE "^Sep 22 (0[0-9]|1[0-5]):" | grep -aiE "deauth|disconnect|auth|assoc|reason|fail|timeout|roam|dhcp|activated|ALOPS|WEB_DEV|link|carrier" | tail -80 | cut -c1-190
