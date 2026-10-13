#!/bin/bash
# (10-13 §8) MPPI 오프라인 시뮬(anal_mppi_sim, EXTRA 로 fpchk=1 등 추가 인자)로 f2o1·f2p1 상자 옆 정지를 재현해 본다 — 계산만, 로버 안 움직임. 인자: 추가 key=val(없으면 현재 값), 환경 SEEDS·LABEL
source /opt/ros/humble/setup.bash; cd /tmp
EXTRA="$*"; LABEL=${LABEL:-$(echo "$*" | tr -cd "a-z0-9._" | cut -c1-24)}; [ -z "$LABEL" ] && LABEL=cur
for b in f2o1 f2p1; do [ -d /tmp/bag_$b ] || { [ -f /tmp/bag_$b.tgz ] && tar xzf /tmp/bag_$b.tgz -C /tmp; }; ls -d /tmp/bag_$b >/dev/null || echo "bag_$b 없음"; done
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 vx_min=-0.06 fwd_w=15 cost_w=3.81"
for sc in "bag_f2o1 13:32:59 300" "bag_f2p1 14:14:22 350"; do set -- $sc; B=$1; TA=$(date -d "$2" +%s); CY=$3
  for sd in 4 5 6 7 8 9 10; do
    echo "######## $B 시작 $2 · ${CY} 주기 · 씨앗 $sd · ${LABEL:-현재값} $*"
    python3 /tmp/anal_mppi_sim.py /tmp/$B 0 label=${LABEL:-cur}_s$sd t_abs=$TA cycles=$CY seed=$sd $COM "${@:4}" $EXTRA 2>&1 | grep -av 'Opened database' > /tmp/sim_${B}_${LABEL:-cur}_$sd.txt
    awk -F'|' '/^ +[0-9]+ \|/{n=$1+0; if (n%60==0 || n>='"$CY"'-1) print}' /tmp/sim_${B}_${LABEL:-cur}_$sd.txt | cut -c1-175
    grep -aE "→|후진 거리|후보 전부 충돌|LETHAL 여유|Traceback|Error" /tmp/sim_${B}_${LABEL:-cur}_$sd.txt | cut -c1-200
  done
done
echo "######## 끝 $(date +%T)"
