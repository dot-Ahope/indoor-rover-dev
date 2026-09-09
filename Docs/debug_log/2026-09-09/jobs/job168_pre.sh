#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "  로컬 레이어: $(timeout 8 ros2 param get /local_costmap/local_costmap plugins 2>/dev/null | sed 's/^.*is: //')"
for p in stvl_layer.voxel_decay stvl_layer.decay_model stvl_layer.depth_clear.min_z stvl_layer.depth_clear.decay_acceleration; do
  printf "  %-42s " "$p"; timeout 6 ros2 param get /local_costmap/local_costmap "$p" 2>/dev/null | sed 's/^.*is: //'
done
echo "  보드: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음')"
echo -n "  배터리: "; timeout 5 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+"
printf "  %-20s " /wheel_odom; timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
