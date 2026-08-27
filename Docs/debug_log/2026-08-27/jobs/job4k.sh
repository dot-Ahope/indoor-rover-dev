#!/bin/bash
# (1) 패치 uvcvideo 교체 + USB 재열거 → HID 재바인딩·iio 확인 (2) RealSense 게이트 (3) bringup 복구
PW='<PW>'
S() { echo "$PW" | sudo -S -p '' "$@"; }
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

echo "===[1] uvcvideo swap + USB re-enumerate==="
pkill -f realsense2_camera_node 2>/dev/null; sleep 1
S modprobe -r uvcvideo && echo "uvcvideo unloaded" || echo "!! uvcvideo unload failed (in use?)"
S modprobe uvcvideo && echo "uvcvideo reloaded: $(modinfo -F filename uvcvideo)"
DEV=""; for d in /sys/bus/usb/devices/*; do [ -f $d/idVendor ] && [ "$(cat $d/idVendor)" = "8086" ] && [ "$(cat $d/idProduct)" = "0b5c" ] && DEV=$d; done
echo "realsense sysfs: $DEV  speed=$(cat $DEV/speed 2>/dev/null)Mbps"
if [ -n "$DEV" ]; then
  echo 0 | S tee $DEV/authorized >/dev/null; sleep 2; echo 1 | S tee $DEV/authorized >/dev/null; sleep 4
  echo "re-enumerated"
fi
echo "-- iio devices:"; ls /sys/bus/iio/devices/ 2>/dev/null || echo NONE
for i in /sys/bus/iio/devices/iio:device*; do [ -d $i ] && echo "  $i: $(cat $i/name 2>/dev/null)"; done
echo "-- hid binding:"; ls -l /sys/bus/hid/devices/ 2>/dev/null | head -3; for h in /sys/bus/hid/devices/*; do [ -e $h/driver ] && echo "  $(basename $h) -> $(basename $(readlink $h/driver))"; done
echo "-- dmesg:"; S dmesg 2>/dev/null | tail -12 | grep -iE "hid|uvc|iio|realsense" | tail -6
echo "-- lsusb -t (RealSense speed):"; lsusb -t | grep -iB1 -A3 "0b5c\|uvcvideo" | head -8

echo "===[2] RealSense gate: depth 640x480x30 + IMU 200Hz (45s)==="
timeout 45 ros2 run realsense2_camera realsense2_camera_node --ros-args \
  -p enable_depth:=true -p enable_color:=false -p enable_infra1:=false -p enable_infra2:=false \
  -p depth_module.depth_profile:=640x480x30 \
  -p enable_gyro:=true -p enable_accel:=true -p gyro_fps:=200 -p accel_fps:=200 \
  -p unite_imu_method:=1 -p initial_reset:=true > /tmp/rs_gate.log 2>&1 &
sleep 22
echo "-- depth hz:"; timeout 7 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -E "average|does not" | tail -1
echo "-- imu hz:";   timeout 8 ros2 topic hz /camera/camera/imu 2>&1 | grep -E "average|does not" | tail -1
echo "-- imu sample:"; timeout 5 ros2 topic echo /camera/camera/imu --once --field angular_velocity 2>/dev/null | head -3
wait
echo "-- node log (USB type / errors / IMU):"
grep -aiE "USB type|Built with|Running with|permission denied|No HID|failed|error|imu|gyro" /tmp/rs_gate.log | grep -v "^$" | head -12

echo "===[3] restore bringup (agent+RSP+EKF)==="
docker rm -f microros_agent >/dev/null 2>&1
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
sleep 3
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 12
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_CONTAINER_DOWN
ros2 node list
grep -aE "error|died" /tmp/bringup.log /tmp/ekf.log | tail -3 || true
echo "NEXT: 보드 RESET → /rover_jupiter 세션 재수립"
