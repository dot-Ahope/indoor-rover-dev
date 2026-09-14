#!/bin/bash
# 정지 계획 A/B: 재기동(새 YAML: SmacHybrid 등록) → 릴레이 정리 → 계획기 목록 확인 → 상자 감사 → job317 (GridBased vs SmacHybrid), 주행 없음
GF=${1:-1.8}; GL=${2:-0.0}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. 재기동 ==="; bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|최소폭'
echo "=== 2. 릴레이 정리 ==="; bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -aE '남은 릴레이|발행자'
echo "=== 3. 계획기 플러그인 확인 ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; timeout 8 ros2 param get /planner_server planner_plugins 2>&1 | tail -1; timeout 8 ros2 param get /planner_server SmacHybrid.minimum_turning_radius 2>&1 | tail -1; grep -ac 'SmacPlannerHybrid' /tmp/nav2.log; grep -aiE 'smac.*(error|fail|exception)' /tmp/nav2.log | head -3"
echo "=== 4. 상자 감사 + 정지 A/B ==="
tr -d '\r' < $SPS/job317_plan_ab2.py > /tmp/job317.py; sshpass -p <PW> scp $OPT -q /tmp/job317.py $J:/tmp/job317_plan_ab2.py || exit 1
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; L=\$(BOX_HINT='1.1 -0.05' python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:'); echo \"\$L\"; BX=\$(echo \"\$L\" | grep -aoE 'x=[0-9.]+' | cut -d= -f2); BY=\$(echo \"\$L\" | grep -aoE 'y=[-+0-9.]+' | cut -d= -f2 | tr -d +); P=\$(timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE 'Translation|RPY' | head -2 | grep -aoE '\[[-0-9., ]+\]' | tr -d '[]'); SXY=\$(echo \"\$P\" | head -1); SYAW=\$(echo \"\$P\" | tail -1 | awk -F, '{printf \"%.2f\", \$3*57.2958}'); SX=\$(echo \$SXY | cut -d, -f1); SY=\$(echo \$SXY | cut -d, -f2); echo \"시작 pose \$SX \$SY \$SYAW°  상자 \$BX \$BY\"; for i in 1 2; do echo \"--- 시행 \$i ---\"; python3 /tmp/job317_plan_ab2.py \$SX \$SY \$SYAW $GF $GL \$BX \$BY GridBased,SmacHybrid 2>&1 | grep -av '^\[INFO\]'; sleep 2; done"
