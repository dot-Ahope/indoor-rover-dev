#!/bin/bash
# 10-22 §5.2 13:30~13:45 Wi-Fi 끊김 · 재연결 사건만
ls /var/log/wifi_mon/ 2>/dev/null | tail -3
grep -ahE "DISCONNECTED|CONNECTED|deauth|Deauth|reason=|SSID-TEMP-DISABLED|DHCP|beacon loss|signal" /var/log/wifi_mon/*.log 2>/dev/null | grep -a "Oct 22 13:[34]" | tail -25
journalctl --since "13:30" --until "13:45" -u NetworkManager --no-pager 2>/dev/null | grep -aE "state change|dhcp|DISCONN|reason" | tail -15
