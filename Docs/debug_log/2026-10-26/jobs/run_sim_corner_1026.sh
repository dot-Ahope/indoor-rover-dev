#!/bin/bash
# 10-26 §10 MPPI 굽은 곳 안쪽 깎기 — 오프라인 시뮬(Docs/tools/anal_mppi_sim.py, Jetson, 로버 안 움직임).
#   장면: f2sh2 복귀, 13:18:22(Smac 재계획 13:18:09.9 뒤, 상자 동쪽 굽은 곳 들어가기 전)부터 16 s. 실제 이탈 최대 +15.7 cm(§9).
#   공통 = 실주행 값(job944 COM + PreferForward 15 + fpchk + Smac 경로 재표본 0.03 + bag 경로 · 코스트맵 동적).
#   변형: base(실주행) · raw(재표본 없음) · PathFollow offset 10 · 5 · PathFollow 가중 5 · 0 · PathAlign 28 · PathAlign 28 + offset 10 · PathAngle 0
source /opt/ros/humble/setup.bash; cd /tmp
TA=1792988302.0; B=/tmp/bag_f2sh2
COM="vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2 cycles=${CYC:-160} lag_steps=1 w_gain=0.7 w_acc=1.2 humble=1 temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 obst=1 seed=1 fwd_w=15 vx_min=-0.06 fpchk=1"
for v in "base resample=0.03" "raw resample=0" "Foff10 resample=0.03 follow_off=10" "Foff5 resample=0.03 follow_off=5" "Fw5 resample=0.03 follow_w=5" "Fw0 resample=0.03 follow_w=0" "A28 resample=0.03 align_w=28" "A28_Foff10 resample=0.03 align_w=28 follow_off=10" "Ang0 resample=0.03 angle_w=0"; do set -- $v; L=$1; shift
  echo "#### $L"; python3 /tmp/anal_mppi_sim.py $B 0 label=$L t_abs=$TA $COM "$@" 2>&1 | grep -aE "굽은 곳|LETHAL 여유\(|후보 전부|→ |Traceback|Error" ; done
echo "#### 끝 $(date +%T)"
