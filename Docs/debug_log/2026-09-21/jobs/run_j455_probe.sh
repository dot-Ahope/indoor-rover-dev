#!/bin/bash
# 09-21 시작 점검: Jetson 도달 IP, 가동 시간, Wi-Fi 상태, wifi-mon 이벤트(주말 끊김?), CostCritic YAML 유지, /tmp 러너·bag 잔존, 디스크
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=6"
for H in 192.168.0.101 172.30.1.8; do
  if timeout 12 sshpass -p <PW> ssh $O jetson@$H true 2>/dev/null; then echo "REACH $H"; break; else echo "no $H"; H=""; fi
done
[ -n "$H" ] || exit 1
timeout 90 sshpass -p <PW> ssh $O jetson@$H 'echo "up: $(uptime -p) | load $(cut -d" " -f1-3 /proc/loadavg) | $(date "+%F %T")"
echo "wifi: $(nmcli -t -f NAME,DEVICE con show --active 2>/dev/null | grep wlan | head -1) | $(iw dev wlan0 link 2>/dev/null | grep -E "SSID|signal" | tr "\n" " ")"
echo "wifi-mon: $(systemctl is-active wifi-mon) | 이벤트 스냅샷 $(ls /var/log/wifi_mon/event_*.txt 2>/dev/null | wc -l) 개 $(ls -t /var/log/wifi_mon/event_*.txt 2>/dev/null | head -3 | xargs -n1 basename 2>/dev/null | tr "\n" " ")"
echo "wifi-mon 로그 크기: $(du -sh /var/log/wifi_mon 2>/dev/null | cut -f1) | BSSID 변화 줄: $(grep -ac "BSSID" /var/log/wifi_mon/wifi_mon.log 2>/dev/null)"
echo "syslog 재인증 거부(주말): $(grep -a "reason=23\|reason=2 " /var/log/syslog 2>/dev/null | tail -2 | cut -c1-120 | tr "\n" ";")"
I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml; echo "yaml md5 $(md5sum $I | cut -c1-12) (배포본 2a91eb8a3f47) critics: $(grep -a "^      critics:" $I | cut -c1-80)"
echo "/tmp 러너: $(ls /tmp/job*.sh /tmp/job*.py 2>/dev/null | wc -l) 개, bag: $(ls -d /tmp/bag_* 2>/dev/null | wc -l), 디스크 여유 $(df -h /tmp | tail -1 | awk "{print \$4}")"
echo "ros 프로세스: $(pgrep -fc "ros2|nav2|slam_toolbox|micro_ros_agent|realsense|rplidar") 개"'
