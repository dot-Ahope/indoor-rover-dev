#!/bin/bash
echo "=== /tmp 잔존: bag·로그 ==="; ls -la --time-style=+%m-%d_%H:%M /tmp | grep -aE 'bag_mp|bag_pd|nav2.log|sensors.log|slam.log|base.log' | awk '{print $5, $6, $7}'
echo "=== 어제 nav2.log 마지막 목표 상태 (있으면) ==="; grep -aE 'Received goal|Begin navigating|Goal (succeeded|failed)|Aborting handle|Goal reached' /tmp/nav2.log 2>/dev/null | tail -4 | cut -c1-140
echo "=== 어제 13:00~14:30 NetworkManager/wlan 이벤트 ==="; grep -aE '^Sep 15 1(3|4):' /var/log/syslog 2>/dev/null | grep -aiE 'NetworkManager.*(wlP1p1s0|WEB_DEV|ALOPS|disconnect|deactivat|activat|dhcp4|roam|supplicant)|wpa_supplicant.*(disconnect|CTRL-EVENT|roam)|brcmfmac|kernel.*wlan' | head -20 | cut -c1-170
echo "=== 어제 13:00~14:30 그 외 오류/재부팅 흔적 ==="; grep -aE '^Sep 15 1(3|4):' /var/log/syslog 2>/dev/null | grep -aiE 'oom|Out of memory|killed process|hung task|watchdog|reboot|shutdown|Power|thermal' | head -8 | cut -c1-170
echo "=== 서비스: mavlink-router / micro-ROS 에이전트 ==="; systemctl is-enabled mavlink-router 2>/dev/null; systemctl status mavlink-router --no-pager 2>/dev/null | grep -aE 'Active|ExecStart' | head -2 | cut -c1-160; docker ps -a --format '{{.Names}} {{.Status}} {{.Image}}' | grep -a micro
echo "=== 시리얼 장치 ==="; ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
