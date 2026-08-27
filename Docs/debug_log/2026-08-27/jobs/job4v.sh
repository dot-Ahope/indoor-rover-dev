#!/bin/bash
# USB 대역폭 테스트: 토폴로지 + (A) 카메라 풀스트림+LiDAR 동시 vs (B) 카메라 단독 비교
PW='<PW>'
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
hz() { timeout $2 ros2 topic hz $1 --window 100 2>&1 | grep -aE "average|min:" | tail -2 | tr '\n' ' ' | sed 's/\t/ /g'; echo; }

echo "===[0] USB topology==="
lsusb -t
for d in /sys/bus/usb/devices/*; do
  [ -f $d/idVendor ] || continue
  v=$(cat $d/idVendor); p=$(cat $d/idProduct)
  case "$v:$p" in 8086:0b5c|10c4:ea60|1a86:7523) echo "  $(basename $d): $v:$p speed=$(cat $d/speed)M  $(cat $d/product 2>/dev/null)";; esac
done
echo "===[1] restart camera FULL (depth 640x480x30 + color 640x480x15 + IMU)==="
if ! grep -aq 'Open profile.*Color' /tmp/camera.log 2>/dev/null; then pkill -f "camera.launch" 2>/dev/null; pkill -f realsense2_camera_node 2>/dev/null; sleep 2; setsid nohup ros2 launch rover_bringup camera.launch.py > /tmp/camera.log 2>&1 & sleep 15; else echo 'camera FULL already running'; fi
grep -aE "USB type|Open profile" /tmp/camera.log | head -6 | cut -c1-140
echo "$PW" | sudo -S -p '' dmesg -C 2>/dev/null

echo "===[A] camera FULL + LiDAR simultaneous (15s, window 100)==="
pgrep -f rplidar_node >/dev/null || { setsid nohup ros2 launch rover_bringup lidar.launch.py > /tmp/lidar.log 2>&1 & sleep 6; }
hz /scan 15 > /tmp/hzA_scan.txt & P1=$!; hz /camera/camera/depth/image_rect_raw 15 > /tmp/hzA_depth.txt & P2=$!; hz /camera/camera/color/image_raw 15 > /tmp/hzA_color.txt & P3=$!; hz /camera/camera/imu 15 > /tmp/hzA_imu.txt & P4=$!; hz /wheel_odom 15 > /tmp/hzA_odom.txt & P5=$!
wait $P1 $P2 $P3 $P4 $P5
for t in scan depth color imu odom; do printf "  %-6s %s\n" $t "$(cat /tmp/hzA_$t.txt)"; done
echo "-- dmesg usb errors during A:"; echo "$PW" | sudo -S -p '' dmesg 2>/dev/null | grep -aiE "usb|xhci|uvc" | grep -aiE "error|fail|reset|bandwidth|babble|overflow|no space" | head -5 || echo "  none"
echo "-- camera log drops:"; grep -aiE "drop|missed|didn't arrive|Hardware Notification|error" /tmp/camera.log | sort | uniq -c | sort -rn | head -4 || echo "  none"

echo "===[B] camera FULL alone (LiDAR stopped, 15s)==="
pkill -f "lidar.launch" 2>/dev/null; pkill -f rplidar_node 2>/dev/null; sleep 3
echo "$PW" | sudo -S -p '' dmesg -C 2>/dev/null
hz /camera/camera/depth/image_rect_raw 15 > /tmp/hzB_depth.txt & P1=$!; hz /camera/camera/color/image_raw 15 > /tmp/hzB_color.txt & P2=$!; hz /camera/camera/imu 15 > /tmp/hzB_imu.txt & P3=$!
wait $P1 $P2 $P3
for t in depth color imu; do printf "  %-6s %s\n" $t "$(cat /tmp/hzB_$t.txt)"; done
echo "-- dmesg usb errors during B:"; echo "$PW" | sudo -S -p '' dmesg 2>/dev/null | grep -aiE "usb|xhci|uvc" | grep -aiE "error|fail|reset|bandwidth|babble|overflow|no space" | head -5 || echo "  none"

echo "===[C] LiDAR restart + CPU==="
setsid nohup ros2 launch rover_bringup lidar.launch.py > /tmp/lidar.log 2>&1 &
sleep 6; hz /scan 8
top -bn1 | head -4 | tail -2
top -bn1 -o %CPU | sed -n '8,13p' | awk '{printf "  %-22s cpu=%s%% mem=%s%%\n", $12, $9, $10}'
