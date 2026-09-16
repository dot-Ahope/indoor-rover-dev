#!/bin/bash
# 주행 준비만(주행 없음): 재기동(job240, 에이전트 유지) → 릴레이 고아 정리 → 파라미터 readback → 상자 감사 → 게이트 수치
BXH=${1:-1.19}; BYH=${2:-0.07}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
echo "=== 1. 재기동 ==="; bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|최소폭|wheel_odom|gyro|map->odom|활성|단일|프로세스'
echo "=== 2. 릴레이 정리 ==="; bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -aE '남은 릴레이|발행자'
for f in job248_audit.py job315_boxcells.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f $J:/tmp/$f || exit 1; done
echo "=== 3. readback (MPPI 변경 3개 + 패딩) ==="
timeout 90 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; for p in time_steps PathAlignCritic.offset_from_furthest PathAngleCritic.max_angle_to_furthest; do printf '  %-42s ' FollowPathMPPI.\$p; timeout 8 ros2 param get /controller_server FollowPathMPPI.\$p 2>&1 | tail -1; done; printf '  %-42s ' local footprint_padding; timeout 8 ros2 param get /local_costmap/local_costmap footprint_padding 2>&1 | tail -1; grep -ac 'missed its desired rate\|Control loop' /tmp/nav2.log | sed 's/^/  루프 지연 경고(기동 후): /'"
echo "=== 4. 상자 감사 + 게이트 ==="
A=$(timeout 150 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BXH $BYH' python3 /tmp/job248_audit.py 2>&1")
echo "$A" | grep -aE '^상자:|최소폭|^   1\.[0-3]0 '
BX=$(echo "$A" | grep -aoE 'x=[0-9.]+' | head -1 | cut -d= -f2); BY=$(echo "$A" | grep -aoE 'y=[-+0-9.]+' | head -1 | cut -d= -f2 | tr -d +)
NB=$(echo "$A" | grep -aE '^  로컬\[' -A1 | grep -aoE '\(\+?[-0-9.]+,[-+0-9.]+\)' | tr -d '()+' | awk -F, '$1>0.3 && $1<1.6 && $2>-0.10 && $2<0.50' | wc -l)
BM=$(timeout 60 sshpass -p <PW> ssh $O $J "source /opt/ros/humble/setup.bash; python3 /tmp/job315_boxcells.py $BX $BY 2>&1 | grep -av '^\[' | tail -1")
# 좌측 경계: x 1.10~1.30 행의 기준1 구간 중 **하한이 상자 셀 최대 y 보다 큰 것**(왼쪽 통로)만 — 09-16 mp3 게이트에서 1.00 행의 우측 구간 [-0.35~+0.00] 이 섞여 창이 -0.365 로 오판
LB=$(echo "$A" | grep -aE '^   1\.[1-3]0 ' | awk '{print $2}' | tr -d '[]' | awk -F'~' -v bm="$BM" '$1+0 > bm+0 {print $2+0}' | sort -n | head -1)
W2=$(awk -v lb="$LB" -v bm="$BM" 'BEGIN{ if (bm=="nan"||bm=="") print "nan"; else printf "%.3f", lb - (bm + 0.195) }')
echo "상자 x=$BX y=$BY | 통로 띠 근거 없는 셀 $NB (≤1) | 창 $W2 m (≥0.20; 좌측 $LB, 상자 셀 최대 y $BM)"
