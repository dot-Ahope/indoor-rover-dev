#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 실행 중인 로컬 코스트맵 파라미터 ==="
for p in plugins voxel_layer.observation_sources voxel_layer.enabled obstacle_layer.observation_sources obstacle_layer.enabled obstacle_layer.combination_method footprint_padding; do
  printf "  %-38s " "$p"; timeout 6 ros2 param get /local_costmap/local_costmap "$p" 2>/dev/null | sed 's/^.*is: //' || echo "?"
done
echo "  depth 소스:"
for p in voxel_layer.depth.clearing voxel_layer.depth.marking voxel_layer.depth.raytrace_min_range voxel_layer.depth.raytrace_max_range voxel_layer.depth.obstacle_max_range voxel_layer.depth.min_obstacle_height; do
  printf "    %-46s " "$p"; timeout 6 ros2 param get /local_costmap/local_costmap "$p" 2>/dev/null | sed 's/^.*is: //' || echo "?"
done
echo "  scan 소스(obstacle_layer):"
for p in obstacle_layer.scan.clearing obstacle_layer.scan.raytrace_min_range; do
  printf "    %-46s " "$p"; timeout 6 ros2 param get /local_costmap/local_costmap "$p" 2>/dev/null | sed 's/^.*is: //' || echo "?"
done
echo ""
echo "=== 전역 코스트맵 ==="
for p in plugins voxel_layer.observation_sources obstacle_layer.observation_sources footprint_padding voxel_layer.depth.raytrace_min_range; do
  printf "  %-38s " "$p"; timeout 6 ros2 param get /global_costmap/global_costmap "$p" 2>/dev/null | sed 's/^.*is: //' || echo "?"
done
