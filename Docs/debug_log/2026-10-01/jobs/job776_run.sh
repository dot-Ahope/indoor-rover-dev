#!/bin/bash
# 10-01 §8.29: 회전 방식 시뮬 — 두 장면 × 세 설정. 공통 = job452 의 실측 구동계 모델(COM) + 경로·로컬 코스트맵 시간 재생.
#   DD   = 기존(차동구동, vx_min −0.06, 전진선호 5) / DD0 = 지금 적용(vx_min 0) / ACK = 절충(최소 반경 0.22 m, vx_min −0.04, 전진선호 15)
source /opt/ros/humble/setup.bash; cd /tmp
t0() { python3 -c "
import rosbag2_py,sys
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='$1',storage_id='sqlite3'),rosbag2_py.ConverterOptions('cdr','cdr'))
first=None
while r.has_next():
    tp,d,ts=r.read_next()
    if first is None: first=ts*1e-9
    if '$2'=='plan' and tp=='/plan': print(ts*1e-9); break
else: print(first)
if '$2'!='plan': print(first)" | head -1; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=150 lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 seed=1"
for sc in ${SCENES:-"bag_f2a8 1.0 출발방_남쪽_U턴 plan"}; do :; done
for sc in "bag_f2a10 75.3 서쪽통로입구_북쪽꺾기 first" "bag_f2a8 1.0 출발방_남쪽_U턴 plan"; do set -- $sc; B=$1; OFF=$2; NM=$3; MODE=$4
  TA=$(python3 -c "print($(t0 /tmp/$B $MODE)+$OFF)")
  echo "######## $NM ($B +$OFF s)"
  for v in ${VARS2:-"ACK22F5 vx_min=-0.06 fwd_w=5 ack_r=0.22" "ACK10F5 vx_min=-0.06 fwd_w=5 ack_r=0.10"}; do set -- $v; L=$1; shift
    python3 /tmp/job776_mppi_sim_ack.py /tmp/$B 0 label=${L}_$NM t_abs=$TA $COM "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|후진 거리|흔들림|LETHAL 여유|Traceback|Error"
    echo
  done
done
echo "######## 끝 $(date +%T)"
