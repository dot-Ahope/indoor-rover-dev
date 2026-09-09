#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 실행 중 파라미터 ==="
for cm in local_costmap global_costmap; do
  echo "  [$cm]"
  for p in voxel_layer.depth.raytrace_min_range voxel_layer.depth.raytrace_max_range voxel_layer.depth.obstacle_max_range voxel_layer.depth.clearing obstacle_layer.scan.raytrace_min_range footprint_padding; do
    printf "    %-46s " "$p"; timeout 6 ros2 param get /$cm/$cm "$p" 2>/dev/null | sed 's/^.*is: //' || echo "?"
  done
done
echo ""
echo "=== 배포 파일 값 ==="
grep -nE "^ +raytrace_min_range" ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml | sed 's/^/  /'
