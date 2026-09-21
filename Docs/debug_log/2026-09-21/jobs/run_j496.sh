#!/bin/bash
# 마감 상태 확인·정리: 설치 .so 가 build 로의 심볼릭인지, 컨테이너에 nvblox 프로세스가 남았는지(남았으면 job473 stop 으로 정지)
H=${JETSON_HOST:-192.168.0.101}; O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 90 sshpass -p <PW> ssh $O jetson@$H 'L=/home/jetson/ros2_ws/install/nvblox_nav2/lib/libnvblox_nav2.so; echo "== install .so: $(ls -la $L | cut -c1-30) → $(readlink -f $L) ($(stat -L -c %y $L | cut -c12-19))"
echo "== 컨테이너 nvblox 프로세스(전):"; docker exec isaac_ros_dev-aarch64-container ps -eo pid,ppid,etimes,cmd 2>/dev/null | grep -a nvblox | grep -av grep | cut -c1-110
if docker exec isaac_ros_dev-aarch64-container pgrep -f nvblox_node >/dev/null 2>&1; then echo "== job473 stop 실행"; bash /tmp/job473_nvblox_run.sh stop 2>&1 | tail -3 | cut -c1-120; sleep 3; echo "== 후:"; docker exec isaac_ros_dev-aarch64-container ps -eo pid,cmd 2>/dev/null | grep -a nvblox | grep -av grep | cut -c1-110; fi
echo "== 호스트 nvblox CPU 흔적: $(top -b -n1 | awk "/nvblox/ {printf \"%s %s%% \", \$12, \$9}")"; echo "== 로드: $(cut -d" " -f1-3 /proc/loadavg)"'
