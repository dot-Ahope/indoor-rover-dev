#!/bin/bash
# job156 이 'ros2 topic pub -1 /cmd_vel' 에서 무한 대기(옛 참가자와 매칭 불가) → 죽이고 데몬 재시작
echo "걸린 pub: $(pgrep -fc 'ros2 topic pub')  job156: $(pgrep -fc job156_stop)"
pkill -f 'ros2 topic pub' 2>/dev/null; pkill -f job156_stop.sh 2>/dev/null; sleep 1
source /opt/ros/humble/setup.bash; ros2 daemon stop >/dev/null 2>&1; sleep 1
echo "후: pub $(pgrep -fc 'ros2 topic pub') job156 $(pgrep -fc job156_stop)  $(date +%T)"
