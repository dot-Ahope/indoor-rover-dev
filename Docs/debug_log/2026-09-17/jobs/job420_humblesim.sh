#!/bin/bash
# Humble 1.1.20 동작 모드 시뮬레이터 검증 (2026-09-17 §14): 실측(T0.15 mp9~11 반전 10.3~14.8 /m·RMS 0.058~0.076, T0.3 mp12 8.8 /m·0.059) 재현 여부
source /opt/ros/humble/setup.bash; cd /tmp
run() { B=$1; T=$2; shift 2; python3 /tmp/job419_mppi_sim_humble.py /tmp/bag_$B $T "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|흔들림|유효 표본|Traceback|Error|error"; echo; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=60 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1"
echo "######## 통로 mp11 t=19"
for seed in 1 2 3; do
  run mp11 19 label=H${seed}_mp11_T0.15 $COM temperature=0.15 seed=$seed
  run mp11 19 label=H${seed}_mp11_T0.3 $COM temperature=0.3 seed=$seed
done
echo "######## 통로 mp12 (t=17, 19)"
for at in 17 19; do for seed in 1 2; do
  run mp12 $at label=K${seed}_mp12t${at}_T0.15 $COM temperature=0.15 seed=$seed
  run mp12 $at label=K${seed}_mp12t${at}_T0.3 $COM temperature=0.3 seed=$seed
done; done
echo "######## 끝 $(date +%T)"
