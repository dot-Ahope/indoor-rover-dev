#!/bin/bash
# 10-07 §2: prep 뒤 확인(읽기만) — Nav2 상태, rf2o·게이트 발행률, 정지 중 CPU
for n in controller_server behavior_server bt_navigator; do echo "  $n: $(timeout 10 ros2 lifecycle get /$n 2>&1 | tail -1)"; done
for t in /odom_rf2o /odom_rf2o/gated /odometry/ekf_a; do echo "  $t $(timeout 6 ros2 topic hz $t 2>&1 | grep -a average | tail -1)"; done
top -b -n 2 -d 5 | awk '/^top -/{n++} n==2 && /^ *[0-9]/{print $1, $9, $12}' > /tmp/top907.txt
for p in rf2o_gate rf2o_laser ekf_node; do for pid in $(pgrep -f "[${p:0:1}]${p:1}"); do grep "^$pid " /tmp/top907.txt | awk -v n=$p '{printf "  CPU %s %s%%\n", n, $2}'; done; done
grep -a "EKF 위반" /tmp/live/current.log | tail -1; uptime
