#!/bin/bash
# 10-07 §2: rf2o + G4 + 그림자 EKF A 켠 prep(위치 추정 office_v3·Nav2) — 로버 안 움직임
export EXTRA_SENSORS="rf2o:=true shadow:=true gate_v:=on"
bash /tmp/job780_prep_navmap.sh
echo "  sensors 인자 확인: $(grep -a "sensors 인자" /tmp/live/current.log | tail -1)"
echo "  게이트 파라미터: $(source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; timeout 8 ros2 param get /rf2o_gate v_mode 2>&1 | tail -1)"
