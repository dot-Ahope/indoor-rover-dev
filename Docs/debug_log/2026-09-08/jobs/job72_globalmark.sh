#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "== 전역 코스트맵 ASCII (상자가 어디든 찍히는지) =="
python3 /tmp/job64e_map.py 2>/dev/null | sed -n '3,16p'
echo "== 코스트맵 관련 경고 (변환 실패 등) =="
grep -aiE "transform|tolerance|observation|sensor origin|out of bounds" /tmp/nav2.log | grep -aiE "warn|error|fail" | tail -6
echo "== 전역 voxel_layer 파라미터 실제값 =="
for k in voxel_layer.enabled voxel_layer.observation_sources voxel_layer.depth.topic voxel_layer.depth.marking voxel_layer.depth.clearing voxel_layer.depth.data_type voxel_layer.combination_method voxel_layer.z_voxels voxel_layer.origin_z transform_tolerance; do
  echo -n "  $k: "; timeout 8 ros2 param get /global_costmap/global_costmap $k 2>&1 | tail -1
done
echo "== 로컬 동일 파라미터 (대조) =="
for k in voxel_layer.depth.topic voxel_layer.combination_method transform_tolerance; do
  echo -n "  $k: "; timeout 8 ros2 param get /local_costmap/local_costmap $k 2>&1 | tail -1
done
