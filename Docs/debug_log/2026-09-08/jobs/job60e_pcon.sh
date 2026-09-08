#!/bin/bash
source /opt/ros/humble/setup.bash
ros2 param set /camera/camera pointcloud__neon_.allow_no_texture_points true | tail -1
ros2 param set /camera/camera pointcloud__neon_.enable true | tail -1
sleep 4
echo "== points 토픽 =="; ros2 topic list | grep -iE "points" || echo "(없음)"
echo -n "pointcloud Hz: "; timeout 8 ros2 topic hz /camera/camera/depth/color/points 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
echo -n "포인트 수(width×height): "; timeout 8 ros2 topic echo --once /camera/camera/depth/color/points --field width 2>/dev/null | head -1; timeout 8 ros2 topic echo --once /camera/camera/depth/color/points --field height 2>/dev/null | head -1
echo -n "frame: "; timeout 8 ros2 topic echo --once /camera/camera/depth/color/points --field header.frame_id 2>/dev/null | head -1
sleep 3; echo "== CPU (3초 평균) =="; top -bn4 -d1 | awk '/^top/{i++} i>=2 && /python3|realsen|async_s|rplidar|ekf_node|controller|planner/ {c[$12]+=$9; n[$12]++} END{for(k in c) printf "%5.1f%% %s\n", c[k]/n[k], k}' | sort -rn | head -7
echo -n "load: "; cut -d" " -f1-3 /proc/loadavg
