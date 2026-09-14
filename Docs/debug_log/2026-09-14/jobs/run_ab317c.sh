#!/bin/bash
# Smac cost_penalty 스윕(정지, use_start=(0,0,0), 목표 1.8/+0.35, 주행 없음) — 라이브 코스트맵(상자 있음) 기준
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
timeout 400 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for CP in 1.2 2.0 3.0; do timeout 8 ros2 param set /planner_server SmacHybrid.cost_penalty \$CP >/dev/null 2>&1; echo \"=== cost_penalty \$CP (R 0.10) ===\"; python3 /tmp/job317_plan_ab2.py 0.0 0.0 0.0 1.8 0.35 1.082 0.001 GridBased,SmacHybrid 2>&1 | grep -av '^\[INFO\]' | grep -avE '^시작 map'; done
echo '=== non_straight_penalty 1.5 + cost 2.0 ==='; timeout 8 ros2 param set /planner_server SmacHybrid.non_straight_penalty 1.5 >/dev/null 2>&1; timeout 8 ros2 param set /planner_server SmacHybrid.cost_penalty 2.0 >/dev/null 2>&1
python3 /tmp/job317_plan_ab2.py 0.0 0.0 0.0 1.8 0.35 1.082 0.001 SmacHybrid 2>&1 | grep -av '^\[INFO\]' | grep -avE '^시작 map|^전역'
timeout 8 ros2 param set /planner_server SmacHybrid.non_straight_penalty 1.05 >/dev/null 2>&1; timeout 8 ros2 param set /planner_server SmacHybrid.cost_penalty 1.2 >/dev/null 2>&1; echo '(복원 1.2/1.05)'"
