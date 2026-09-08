#!/bin/bash
source /opt/ros/humble/setup.bash
echo "== points 토픽 =="; ros2 topic list | grep -iE "points|pointcloud" || echo "(없음)"
echo -n "depth 이미지 Hz: "; timeout 6 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
echo "== realsense 파라미터 실제값 =="; for k in pointcloud.enable decimation_filter.enable decimation_filter.filter_magnitude pointcloud.stream_filter depth_module.depth_profile enable_color; do echo -n "  $k: "; timeout 8 ros2 param get /camera/camera $k 2>&1 | tail -1; done
echo "== sensors.log (pointcloud/decimation/param 경고) =="; grep -aiE "pointcloud|decimation|not declared|unknown|invalid|param" /tmp/sensors.log | grep -viE "declare_parameter" | head -8
echo "== 카메라 노드 오류 =="; grep -aiE "error|fail" /tmp/sensors.log | grep -ai camera | head -4
