#!/bin/bash
# Jetson Wi-Fi 끊김 진단 (읽기 전용)
IF=$(iw dev 2>/dev/null | awk '$1=="Interface"{print $2}' | head -1)
echo "IF=$IF  uptime: $(uptime -p)"
echo "== link =="; iw dev "$IF" link 2>/dev/null | grep -E "SSID|signal|freq|rx bitrate|tx bitrate"
echo "== power_save =="; iw dev "$IF" get power_save 2>/dev/null
echo "== nmcli 연결 =="; nmcli -t -f DEVICE,STATE,CONNECTION dev status 2>/dev/null | grep -E "^$IF"
nmcli -t -f 802-11-wireless.powersave,connection.autoconnect-retries con show "$(nmcli -t -f DEVICE,CONNECTION dev status | grep "^$IF" | cut -d: -f2)" 2>/dev/null
echo "== NetworkManager 최근 20분 (연결/끊김) =="; journalctl -u NetworkManager --since "20 min ago" --no-pager 2>/dev/null | grep -iE "disconnect|deactivat|activated|roam|auth|dhcp4.*(address|lease)" | tail -12
echo "== dmesg wifi 드라이버 =="; dmesg 2>/dev/null | grep -iE "wlan|rtw|rtl88|iwlwifi|brcm|wlP" | tail -8
echo "== ip =="; ip -4 -br addr show "$IF"
