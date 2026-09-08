#!/bin/bash
# 사용: run_param.sh <node> <param=value> ...  (런타임 파라미터 변경 + 확인)
SSH="sshpass -p <PW> ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8 jetson@192.168.0.101"
NODE=$1; shift
CMD="source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash;"
for kv in "$@"; do k=${kv%%=*}; v=${kv#*=}; CMD="$CMD echo -n \"$k: \"; timeout 10 ros2 param set $NODE $k $v | tail -1; timeout 10 ros2 param get $NODE $k | tail -1;"; done
for t in 1 2 3; do if timeout 120 $SSH "$CMD" 2>&1; then exit 0; fi; sleep 3; done
