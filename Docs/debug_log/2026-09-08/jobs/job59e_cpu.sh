#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
bash /tmp/job25e_nav2start.sh > /tmp/nav2start.out 2>&1
sleep 10
echo -n "stuck_monitor 인스턴스: "; pgrep -fc "stuck_monitor.py"
P=$(pgrep -f stuck_monitor.py | tail -1)
echo -n "stuck_monitor 현재 CPU(top 4s): "; top -bn5 -d1 -p $P | awk '/^top/{i++} i>=2 && /python3/ {s+=$9;n++} END{printf "%.1f%%\n", s/n}'
echo -n "모드: "; grep -a "stuck_monitor 시작" /tmp/nav2.log | tail -1 | sed "s/.*, //"
echo "== 상위 CPU(3초 평균) =="; top -bn4 -d1 | awk '/^top/{i++} i>=2 && /python3|realsen|depthimag|async_s|rplidar|ekf_node|controller|planner/ {c[$12]+=$9; n[$12]++} END{for(k in c) printf "%5.1f%% %s\n", c[k]/n[k], k}' | sort -rn | head -7
echo -n "load: "; cut -d" " -f1-3 /proc/loadavg
