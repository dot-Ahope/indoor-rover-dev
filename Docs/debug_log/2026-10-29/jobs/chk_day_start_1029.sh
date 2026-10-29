#!/bin/bash
# 10-29 하루 시작 점검(읽기만): 가동 시간 · Wi-Fi · 스택 프로세스 · 컨디셔너 ZUPT 로그
echo "== $(date '+%F %T')  up $(uptime -p)  load $(cut -d' ' -f1-3 /proc/loadavg)"
nmcli -t -f ACTIVE,SSID dev wifi 2>/dev/null | grep '^yes' | head -1
echo "-- 스택 프로세스"
for p in micro_ros_agent sensor_conditioner ekf_node slam_toolbox controller_server planner_server bt_navigator nvblox cuvslam vslam_twist place_server place_web; do
  printf '  %-20s %s\n' $p "$(pgrep -fc $p)"; done
echo "-- /tmp 로그"; ls -la --time-style=+%m-%d_%H:%M /tmp/*.log 2>/dev/null | awk '{print "  "$6, $5, $7}' | head -30
echo "-- 컨디셔너 로그(ZUPT · 캘리브) — 처음 3 · 마지막 8"
L=$(grep -l "ZUPT\|gyro bias" /tmp/*.log /tmp/logkeep/*.log 2>/dev/null | head -3); echo "  파일: $L"
for f in $L; do echo "  [$f] ZUPT 줄 수 $(grep -c ZUPT $f)"; grep -a "gyro bias\|not stationary" $f | head -3; grep -a ZUPT $f | head -3; echo "  ..."; grep -a ZUPT $f | tail -8; done
