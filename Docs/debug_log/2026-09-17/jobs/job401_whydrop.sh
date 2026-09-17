#!/bin/bash
echo "host $(hostname) $(date +%T) uptime $(uptime -p) ip $(ip -4 -o addr show wlP1p1s0 | awk '{print $4}') ssid $(nmcli -t -f NAME,DEVICE con show --active 2>/dev/null | grep -a wlP1p1s0 | cut -d: -f1)"
echo "=== syslog 13:3x Wi-Fi ==="; grep -aE "^Sep 17 13:3[0-7]" /var/log/syslog | grep -aiE "CTRL-EVENT|deauth|disconnect|AUTH|reason|activated|DHCP" | tail -8 | cut -c1-160
echo "=== 스택 상태 ==="; for p in job240_clean sensors.launch slam.launch navigation.launch microros_agent ekf_node slam_toolbox controller_server; do printf "%s:%s " $p $(pgrep -fc $p); done; echo
echo "sensors.log $(wc -l < /tmp/sensors.log) 줄, nav2.log $(wc -l < /tmp/nav2.log) 줄, 최근 수정 $(stat -c %y /tmp/nav2.log | cut -c12-19)"
