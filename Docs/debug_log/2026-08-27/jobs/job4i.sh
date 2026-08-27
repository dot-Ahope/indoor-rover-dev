#!/bin/bash
# 재부팅 후 복구·검증: HID 모듈 로드 확인 → bringup(base+ekf+static TF) 복구
PW='<PW>'
echo "===UPTIME==="; uptime
echo "===HID_MODULES==="
modinfo hid_sensor_hub 2>/dev/null | grep -E "filename|vermagic" || echo "hid_sensor_hub NOT INDEXED"
echo "$PW" | sudo -S -p '' modprobe hid_sensor_hub && echo "modprobe hid_sensor_hub OK"
echo "$PW" | sudo -S -p '' modprobe hid_sensor_gyro_3d && echo "modprobe hid_sensor_gyro_3d OK"
echo "$PW" | sudo -S -p '' modprobe hid_sensor_accel_3d && echo "modprobe hid_sensor_accel_3d OK"
lsmod | grep -E "hid_sensor|uvcvideo"
echo "$PW" | sudo -S -p '' dmesg 2>/dev/null | grep -iE "hid_sensor|hid-sensor|uvcvideo|taint" | tail -5
echo "===IIO (카메라 미연결이면 비어 있음)==="; ls /sys/bus/iio/devices/ 2>/dev/null || echo NONE
echo "===DEVICES==="; ls -l /dev/rover /dev/rplidar 2>&1
echo "===RESTORE_BRINGUP==="
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
docker rm -f microros_agent >/dev/null 2>&1
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
sleep 3
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 12
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_CONTAINER_DOWN
ros2 node list
grep -aE "error|died" /tmp/bringup.log /tmp/ekf.log | tail -3 || true
echo "NEXT: 보드 RESET 버튼 → 세션 재수립 후 토픽 검증"
