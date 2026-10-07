#!/bin/bash
# 10-07 §6: rf2o + G4(휠 잔차) + 그림자 A + MPPI transform_tolerance 0.5 prep — 로버 안 움직임
export EXTRA_SENSORS="rf2o:=true shadow:=true gate_v:=on gate_vref:=wheel"
bash /tmp/job780_prep_navmap.sh
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "  게이트 v_mode $(timeout 8 ros2 param get /rf2o_gate v_mode 2>&1 | tail -1) · v_ref $(timeout 8 ros2 param get /rf2o_gate v_ref 2>&1 | tail -1)"
echo "  MPPI transform_tolerance $(timeout 8 ros2 param get /controller_server FollowPath.transform_tolerance 2>&1 | tail -1)"
for n in controller_server behavior_server bt_navigator; do echo "  $n: $(timeout 10 ros2 lifecycle get /$n 2>&1 | tail -1)"; done
