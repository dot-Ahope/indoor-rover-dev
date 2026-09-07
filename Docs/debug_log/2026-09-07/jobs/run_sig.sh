#!/bin/bash
# 사용: run_sig.sh <출력이름> <DUR> <VX>
SSH="sshpass -p <PW> ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=5 jetson@192.168.0.101"
for t in 1 2 3; do
  if timeout 90 $SSH "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job40a_stalltest.py $2 $3 2>&1 | tee /tmp/$1.txt"; then exit 0; fi; sleep 2
done
