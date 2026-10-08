#!/bin/bash
# 10-08 §6: job944 의 F5·F15 를 seed 2·3 으로 반복(표본 잡음 확인). 로버 안 움직임.
#   장면 1 W3 출발(f2e2, 목표 3 첫 경로 bag +116.6 s): 실제로는 51 s 후진. 장면 2 서쪽 통로 입구(f2a10 +75.3 s, 10-01 §8.29): 좁은 곳 회귀 확인.
#   설정: F5 = 지금(전진선호 5·후진 −0.06) / F15 / F30 / F60 = 전진선호 가중 / V03 = 후진 한도 −0.03(전진선호 5)
source /opt/ros/humble/setup.bash; cd /tmp
[ -d /tmp/bag_f2a10 ] || tar xzf /tmp/bag_f2a10.tgz -C /tmp
first() { python3 -c "
import rosbag2_py
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='$1',storage_id='sqlite3'),rosbag2_py.ConverterOptions('cdr','cdr'))
print(r.read_next()[2]*1e-9)"; }
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=${CYC:-200} lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1"
T1=1791437906.27; T2=$(python3 -c "print($(first /tmp/bag_f2a10)+75.3)")
for sc in "bag_f2e2 $T1 W3출발" "bag_f2a10 $T2 서쪽통로입구"; do set -- $sc; B=$1; TA=$2; NM=$3
  echo "######## $NM ($B t_abs $TA)"
  for SEED in 2 3; do for v in "F5 vx_min=-0.06 fwd_w=5" "F15 vx_min=-0.06 fwd_w=15"; do set -- $v; L=$1; shift
    python3 /tmp/job776_mppi_sim_ack.py /tmp/$B 0 label=${L}s${SEED}_$NM t_abs=$TA $COM seed=$SEED "$@" 2>&1 | grep -av 'Opened database' | grep -aE "^[A-Z0-9]+_|→|후진 거리|LETHAL 여유|목표\(|Traceback|Error"
    echo
  done; done
done
echo "######## 끝 $(date +%T)"
