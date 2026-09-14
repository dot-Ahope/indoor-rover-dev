#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. 재기동 (job240) ==="
bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|최소폭'
echo "=== 2. 릴레이 고아 정리 ==="
bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -aE '남은 릴레이|out hz|발행자'
tr -d '\r' < $SPS/job312_box_edge.py > /tmp/job312.py; sshpass -p <PW> scp $OPT -q /tmp/job312.py $J:/tmp/job312_box_edge.py || exit 1
echo "=== 3. 상자 가장자리 띠 z 분포 (필터 토픽, 20 s) — 상자 위치는 감사값 ==="
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; L=\$(BOX_HINT='1.15 -0.04' python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:'); echo \"\$L\"; BX=\$(echo \"\$L\" | grep -aoE 'x=[0-9.]+' | cut -d= -f2); BY=\$(echo \"\$L\" | grep -aoE 'y=[-+0-9.]+' | cut -d= -f2); echo \"BX=\$BX BY=\$BY\"; TOPIC=/camera/depth/points_filtered ZTH=0.08 python3 /tmp/job312_box_edge.py \$BX \$BY 20 2>&1 | grep -av '^\[INFO\]'; echo '--- 원본 토픽 (참고) ---'; ZTH=0.08 python3 /tmp/job312_box_edge.py \$BX \$BY 15 2>&1 | grep -av '^\[INFO\]' | grep -avE '코스트맵|y 열별'"
