#!/bin/bash
# (10-14 §2) '갇혔을 때만 패딩 0' 되돌림 시뮬: 정지 자세 2 곳 × us_d 3 개 × 씨앗 5, 300 주기, fpchk=1 unstuck=1 — 계산만, 로버 안 움직임
source /opt/ros/humble/setup.bash; cd /tmp; rm -rf /tmp/unstuck2; mkdir -p /tmp/unstuck2
for b in f2o1 f2p1; do [ -d /tmp/bag_$b ] || tar xzf /tmp/bag_$b.tgz -C /tmp; ls /tmp/bag_$b/metadata.yaml >/dev/null || echo "bag_$b 없음"; done
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 vx_min=-0.06 fwd_w=15 cost_w=3.81 fpchk=1 unstuck=1 cycles=300"
{ for sc in "f2o1 2026-10-13T13:33:27" "f2p1 2026-10-13T14:14:56"; do set -- $sc; for d in 0.15 0.30 0.50; do for sd in 1 2 3 4 5; do echo "$1 $(date -d $2 +%s) $d $sd"; done; done; done; } > /tmp/unstuck2/jobs.lst
echo "작업 $(wc -l < /tmp/unstuck2/jobs.lst) 개 시작 $(date +%T)"
xargs -P 3 -L 1 bash -c 'python3 /tmp/anal_mppi_sim.py /tmp/bag_$0 0 label=$0_d$2_s$3 t_abs=$1 seed=$3 us_d=$2 '"$COM"' 2>&1 | grep -av "Opened database" > /tmp/unstuck2/$0_$2_$3.txt' < /tmp/unstuck2/jobs.lst
echo "끝 $(date +%T)"
