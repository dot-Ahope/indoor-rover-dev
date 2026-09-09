#!/bin/bash
echo "=== A) Nav2 ObstacleLayer 의 observation_persistence 지원 여부 ==="
for f in /opt/ros/humble/lib/libnav2_costmap_2d_core.so /opt/ros/humble/lib/liblayers.so /opt/ros/humble/lib/libnav2_costmap_2d*.so; do
  [ -f "$f" ] && strings "$f" 2>/dev/null
done | grep -aoE "observation_persistence|expected_update_rate|observation_keep_time|min_obstacle_height|combination_method" | sort -u | sed 's/^/  /'
echo ""
echo "=== B) foxglove_bridge 기본 capabilities ==="
strings /opt/ros/humble/lib/foxglove_bridge/foxglove_bridge 2>/dev/null | grep -aoE "^(clientPublish|parameters|parametersSubscribe|services|connectionGraph|assets)$" | sort -u | sed 's/^/  /'
echo ""
echo "=== C) RealSense 고급모드/최소거리 관련 파라미터 ==="
strings /opt/ros/humble/lib/librealsense2_camera.so /opt/ros/humble/lib/realsense2_camera/realsense2_camera_node 2>/dev/null | grep -aoE "json_file_path|depth_module\.[a-z_]*|disparity_shift|DISPARITY_SHIFT" | sort -u | head -20 | sed 's/^/  /'
echo ""
echo "  librealsense 버전: $(strings /opt/ros/humble/lib/librealsense2.so* 2>/dev/null | grep -aoE '^2\.[0-9]+\.[0-9]+$' | sort -u | tail -1)"
echo ""
echo "=== D) 설치된 코스트맵 레이어 플러그인 (참고) ==="
grep -rhoE "class_name>[^<]+" /opt/ros/humble/share/nav2_costmap_2d/*.xml 2>/dev/null | sed 's/class_name>/  /' | sort -u
