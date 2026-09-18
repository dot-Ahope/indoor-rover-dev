#!/bin/bash
# CostCritic 사전 검증 (2026-09-18 §17): dy2·dy4·dy6 bag 의 세 장면(입구 차선변경 goal+8 s, 복귀 회전 시작 goal+16.5 s, 상자 뒤 모서리 goal+20 s)
# 에서 obst=0(현재) vs 1(CostCritic) 을 seed 2 개로. 공통 = job421b(09-17 실측 구동계 모델) + temperature 0.15(기준 구성) + near_thr 0.5 + 경로·코스트맵 시간 재생.
source /opt/ros/humble/setup.bash; cd /tmp
run() { local BAG_=$1; shift; python3 /tmp/job452_mppi_sim_cc.py /tmp/bag_$BAG_ 0 "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|흔들림|유효 표본|LETHAL 여유|동적 입력|Traceback|Error"; echo; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=60 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1"
for sc in "dy4 1789709828.4526" "dy6 1789711764.2988" "dy2 1789705905.1535"; do set -- $sc; B=$1; G=$2
  for off in 8 16.5 20; do TA=$(python3 -c "print($G+$off)")
    echo "######## $B goal+$off s"
    for seed in 1 2; do for ob in 0 1; do
      run $B label=S${seed}_${B}_g${off}_obst${ob} $COM obst=$ob seed=$seed t_abs=$TA
    done; done
  done
done
echo "######## 끝 $(date +%T)"
