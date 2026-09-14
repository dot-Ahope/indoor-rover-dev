#!/bin/bash
# Smac 파라미터 2안 (R 0.10, cost_penalty 1.2, non_straight 1.05) 라이브 적용 → 두 목표(정면 1.8,0 / 통로선 1.8,+0.35)로 정지 A/B, 주행 없음
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
timeout 400 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo '=== 로컬 코스트맵 상자 최대 y (job315) vs 전역 ==='
python3 /tmp/job315_boxcells.py 1.036 -0.005 2>&1 | tail -1
echo '=== Smac 2안 적용 ==='
for kv in 'SmacHybrid.minimum_turning_radius 0.10' 'SmacHybrid.cost_penalty 1.2' 'SmacHybrid.non_straight_penalty 1.05'; do timeout 8 ros2 param set /planner_server \$kv 2>&1 | tail -1; done
for G in '1.8 0.0' '1.8 0.35'; do echo \"=== 목표 전진/횡 \$G ===\"; python3 /tmp/job317_plan_ab2.py 0.0 0.0 0.23 \$G 1.036 -0.005 GridBased,SmacHybrid 2>&1 | grep -av '^\[INFO\]' | grep -avE '^시작 map'; done
echo '=== Smac 3안: R 0.05 (거의 제자리 회전 허용) ==='
timeout 8 ros2 param set /planner_server SmacHybrid.minimum_turning_radius 0.05 2>&1 | tail -1
python3 /tmp/job317_plan_ab2.py 0.0 0.0 0.23 1.8 0.0 1.036 -0.005 SmacHybrid 2>&1 | grep -av '^\[INFO\]' | grep -avE '^시작 map|^전역'"
