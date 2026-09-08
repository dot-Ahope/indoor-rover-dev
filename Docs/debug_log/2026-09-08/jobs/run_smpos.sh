#!/bin/bash
# stuck_monitor 정탐 검증 — /cmd_vel 을 /cmd_vel_test 로 리매핑해 로버는 정지한 채 "지령만" 흘림
SSH="sshpass -p <PW> ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8 jetson@192.168.0.101"
for t in 1 2 3; do
  if timeout 150 $SSH 'source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
run_case () {  # $1=이름 $2=v $3=w $4=shadow
  ros2 run rover_bringup stuck_monitor.py --ros-args -r /cmd_vel:=/cmd_vel_test -p shadow_mode:=$4 > /tmp/sm_$1.log 2>&1 &
  SM=$!; sleep 3
  timeout 9 ros2 topic pub -r 20 /cmd_vel_test geometry_msgs/msg/Twist "{linear: {x: $2}, angular: {z: $3}}" > /dev/null 2>&1
  sleep 1; kill -INT $SM 2>/dev/null; sleep 1
  echo "[$1] v=$2 w=$3 shadow=$4 → STUCK 판정 $(grep -ac STUCK /tmp/sm_$1.log)회"; grep -a STUCK /tmp/sm_$1.log | head -2 | sed "s/.*\]: //"
}
run_case lin 0.05 0.0 true
run_case rot 0.0 0.3 true
run_case act 0.05 0.0 false
echo -n "실제 /cmd_vel 발행 여부(없어야 정상): "; timeout 3 ros2 topic echo --once /cmd_vel 2>/dev/null | grep -c "linear" || echo 0
echo -n "/rover/stuck 마지막: "; timeout 3 ros2 topic echo --once /rover/stuck 2>/dev/null | grep -E "message" | head -1'; then exit 0; fi; sleep 3
done
