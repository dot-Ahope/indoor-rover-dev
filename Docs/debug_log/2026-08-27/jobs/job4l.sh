#!/bin/bash
# IMU 정밀 검증(accel/gyro 모두, iio 권한, 15s hz) + LiDAR 게이트 + 로버 토픽 확인
PW='<PW>'
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

echo "===[A] iio permissions==="
for d in /sys/bus/iio/devices/iio:device0 /sys/bus/iio/devices/iio:device1; do
  echo "$d ($(cat $d/name)): buffer/enable=$(stat -c '%A %U:%G' $d/buffer/enable) scan_elements=$(stat -c '%A %U:%G' $d/scan_elements/in_accel_x_en 2>/dev/null || stat -c '%A %U:%G' $d/scan_elements/in_anglvel_x_en 2>/dev/null)"
done
id -nG jetson | tr ' ' '\n' | grep -E "plugdev|video" | tr '\n' ' '; echo

echo "===[B] RealSense IMU 45s (accel+gyro, unite copy)==="
timeout 45 ros2 run realsense2_camera realsense2_camera_node --ros-args \
  -p enable_depth:=false -p enable_color:=false -p enable_infra1:=false -p enable_infra2:=false \
  -p enable_gyro:=true -p enable_accel:=true -p gyro_fps:=200 -p accel_fps:=200 \
  -p unite_imu_method:=1 -p initial_reset:=false > /tmp/rs_imu.log 2>&1 &
sleep 15
echo "-- imu hz (15s):"; timeout 15 ros2 topic hz /camera/camera/imu 2>&1 | grep -E "average|does not" | tail -1
echo "-- imu full sample:"; timeout 5 ros2 topic echo /camera/camera/imu --once 2>/dev/null | grep -A3 -E "angular_velocity:|linear_acceleration:" | grep -vE "covariance"
echo "-- accel/gyro raw topics:"; ros2 topic list | grep -E "accel|gyro|imu"
wait
echo "-- log warnings:"; grep -aiE "set_power|Motion Module|permission|HID|error" /tmp/rs_imu.log | sort | uniq -c | head -8

echo "===[C] LiDAR gate==="
ls -l /dev/rplidar 2>&1
pkill -f rplidar_node 2>/dev/null; sleep 1
setsid nohup ros2 launch rover_bringup lidar.launch.py > /tmp/lidar.log 2>&1 &
sleep 8
echo "-- /scan hz:"; timeout 8 ros2 topic hz /scan 2>&1 | grep -E "average|does not" | tail -1
echo "-- scan meta:"; timeout 5 ros2 topic echo /scan --once 2>/dev/null | grep -E "frame_id|angle_min|angle_max|angle_increment|range_min|range_max" 
timeout 5 ros2 topic echo /scan --once --field ranges 2>/dev/null | python3 -c "
import sys,re,math
v=[float(x) for x in re.findall(r'[-+]?\d*\.\d+|inf|nan', sys.stdin.read()) if x not in ('inf','nan')]
print(f'-- ranges: n={len(v)} finite, min={min(v):.2f} max={max(v):.2f} median={sorted(v)[len(v)//2]:.2f}') if v else print('-- ranges: none')"
grep -aiE "error|fail|mode|firmware|hardware" /tmp/lidar.log | head -6

echo "===[D] rover topics==="
timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -E "average|does not" | tail -1
timeout 6 ros2 topic hz /odometry/filtered 2>&1 | grep -E "average|does not" | tail -1
ros2 topic list | grep -E "scan|imu|odom|camera" | tr '\n' ' '; echo
