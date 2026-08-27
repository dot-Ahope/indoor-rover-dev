#!/bin/bash
# 동시 부하 재측정: LiDAR 발행 확인 후 scan/depth/color/imu/odom 5개 동시 15s (window 100)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
hz() { timeout $2 ros2 topic hz $1 --window 100 2>&1 | grep -aE "average|min:" | tail -2 | tr '\n' ' ' | sed 's/\t/ /g'; echo; }
echo "-- precheck scan:"; timeout 5 ros2 topic hz /scan 2>&1 | grep -aE "average|does not" | tail -1
echo "-- precheck depth:"; timeout 5 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -aE "average|does not" | tail -1
echo "===SIMULTANEOUS 15s==="
hz /scan 15 > /tmp/hzS_scan.txt & P1=$!; hz /camera/camera/depth/image_rect_raw 15 > /tmp/hzS_depth.txt & P2=$!; hz /camera/camera/color/image_raw 15 > /tmp/hzS_color.txt & P3=$!; hz /camera/camera/imu 15 > /tmp/hzS_imu.txt & P4=$!; hz /wheel_odom 15 > /tmp/hzS_odom.txt & P5=$!
wait $P1 $P2 $P3 $P4 $P5
for t in scan depth color imu odom; do printf "  %-6s %s\n" $t "$(cat /tmp/hzS_$t.txt)"; done
echo "-- dmesg usb errors (since boot):"; echo '<PW>' | sudo -S -p '' dmesg 2>/dev/null | grep -aiE "xhci|usb [0-9]|uvc" | grep -aiE "error|fail|reset|bandwidth|babble|overflow|no space|timed out" | tail -3 || echo "  none"
echo "-- lidar log:"; grep -aiE "error|fail|timeout" /tmp/lidar.log | tail -2 || echo "  none"
