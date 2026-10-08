#!/bin/bash
# 10-08 §3: 전역 nvblox + 주기 재계획 0.5 Hz prep(B) — rf2o·G4 잔차·그림자 A, 순회라 MPPI 궤적 발행. 로버 안 움직임
export EXTRA_SENSORS="rf2o:=true shadow:=true gate_v:=on gate_vref:=wheel" EXTRA_NAV="global_camera:=nvblox replan_hz:=0.5 mppi_viz:=true"
bash /tmp/job780_prep_navmap.sh
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "  전역 obstacle 소스 $(timeout 8 ros2 param get /global_costmap/global_costmap obstacle_layer.observation_sources 2>&1 | tail -1)"
echo "  BT $(timeout 8 ros2 param get /bt_navigator default_nav_to_pose_bt_xml 2>&1 | tail -1) · RateController $(grep -o 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml)"
echo "  MPPI visualize $(timeout 8 ros2 param get /controller_server FollowPathMPPI.visualize 2>&1 | tail -1)"
head -1 /tmp/nav2_params_active.yaml
echo "  전역 nvblox 프레임 $(timeout 10 ros2 param get /global_costmap/global_costmap nvblox_layer.nav2_costmap_global_frame 2>&1 | tail -1)"
