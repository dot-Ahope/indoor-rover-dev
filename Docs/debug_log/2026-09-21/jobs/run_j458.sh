#!/bin/bash
# 인자: NAME D_FRONT DEC [SEC]. 측정 앞뒤로 realsense·depth_relay CPU 와 EKF 위반 증분도 함께.
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job458_nearrange.py > /tmp/job458_nearrange.py; sshpass -p <PW> scp $O -q /tmp/job458_nearrange.py jetson@$H:/tmp/ || exit 1
timeout 120 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
E0=\$(grep -ac 'Failed to meet update rate' /tmp/sensors.log)
top -b -n2 -d3 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk 'NR>1 && (\$12 ~ /realsen|depth_re|python3/) {printf \"  cpu %-14s %5s%%\n\", \$12, \$9}' &
python3 /tmp/job458_nearrange.py $1 $2 $3 ${4:-10} ${5:-0.18} ${6:-0.14} ${7:-0.11} ${8:-3} ${9:-} 2>&1 | grep -av '^\['
wait; echo \"  EKF 위반 증분(측정 중): \$(( \$(grep -ac 'Failed to meet update rate' /tmp/sensors.log) - E0 )) | load \$(cut -d' ' -f1-3 /proc/loadavg) | dec 파라미터: \$(timeout 8 ros2 param get /camera/camera decimation_filter.filter_magnitude 2>&1 | tail -1)\""
