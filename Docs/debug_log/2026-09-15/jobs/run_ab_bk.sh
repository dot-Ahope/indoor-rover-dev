#!/bin/bash
# 상자 뒤 목표(1.8, 0) 정지 A/B: Smac cost_penalty × minimum_turning_radius 스윕 (상자 살아 있는 상태, 주행 없음). 인자: BX BY
BX=${1:-1.2}; BY=${2:-0.0}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job317_plan_ab2.py > /tmp/job317.py; sshpass -p <PW> scp $OPT -q /tmp/job317.py $J:/tmp/job317_plan_ab2.py
timeout 500 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
P=\$(timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE 'Translation|RPY' | head -2 | grep -aoE '\[[-0-9., ]+\]' | tr -d '[]'); SX=\$(echo \"\$P\" | head -1 | cut -d, -f1); SY=\$(echo \"\$P\" | head -1 | cut -d, -f2); SYAW=\$(echo \"\$P\" | tail -1 | awk -F, '{printf \"%.2f\", \$3*57.2958}')
echo \"시작 pose \$SX \$SY \$SYAW°, 상자 $BX $BY, 목표 (1.8, 0)\"
python3 /tmp/job317_plan_ab2.py \$SX \$SY \$SYAW 1.8 0.0 $BX $BY GridBased 2>&1 | grep -av '^\[INFO\]' | grep -aE '^전역|GridBased|전진:횡'
for R in 0.10 0.15; do for CP in 1.2 2.0 3.0; do timeout 8 ros2 param set /planner_server SmacHybrid.minimum_turning_radius \$R >/dev/null 2>&1; timeout 8 ros2 param set /planner_server SmacHybrid.cost_penalty \$CP >/dev/null 2>&1; echo \"--- Smac R \$R cost \$CP ---\"; python3 /tmp/job317_plan_ab2.py \$SX \$SY \$SYAW 1.8 0.0 $BX $BY SmacHybrid 2>&1 | grep -av '^\[INFO\]' | grep -aE 'SmacHybrid|전진:횡'; done; done
timeout 8 ros2 param set /planner_server SmacHybrid.minimum_turning_radius 0.10 >/dev/null 2>&1; timeout 8 ros2 param set /planner_server SmacHybrid.cost_penalty 1.2 >/dev/null 2>&1; echo '(복원 R 0.10 / cost 1.2)'
python3 /tmp/job317_plan_ab2.py \$SX \$SY \$SYAW 1.8 0.0 $BX $BY GridBased 2>&1 | grep -av '^\[INFO\]' | grep -aE '^전역'"
