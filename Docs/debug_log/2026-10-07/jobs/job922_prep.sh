#!/bin/bash
# 10-07 §8.2: 전역 카메라 STVL 층(global_camera:=stvl) prep — rf2o·G4 잔차 그대로. 로버 안 움직임
export EXTRA_SENSORS="rf2o:=true shadow:=true gate_v:=on gate_vref:=wheel" EXTRA_NAV="global_camera:=stvl"
bash /tmp/job780_prep_navmap.sh
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "  전역 obstacle 소스 $(timeout 8 ros2 param get /global_costmap/global_costmap obstacle_layer.observation_sources 2>&1 | tail -1)"
for p in stvl_layer.voxel_decay stvl_layer.depth_clear.min_z stvl_layer.depth_clear.decay_acceleration; do echo "  $p $(timeout 8 ros2 param get /global_costmap/global_costmap $p 2>&1 | tail -1)"; done
head -1 /tmp/nav2_params_active.yaml
