#!/bin/bash
# 빌드된 HID 모듈·패치 uvcvideo 라이브 로드 검증 (재부팅 없이)
PW='<PW>'
S() { echo "$PW" | sudo -S -p '' "$@"; }
echo "===MODINFO==="
for m in hid_sensor_hub hid_sensor_iio_common hid_sensor_trigger hid_sensor_accel_3d hid_sensor_gyro_3d; do
  printf "%-24s %s\n" "$m" "$(modinfo -F vermagic $m 2>&1)"
done
echo "===MODPROBE_HID==="
S modprobe hid_sensor_hub && echo "hid_sensor_hub loaded"
S modprobe hid_sensor_accel_3d && echo "hid_sensor_accel_3d loaded"
S modprobe hid_sensor_gyro_3d && echo "hid_sensor_gyro_3d loaded"
lsmod | grep -E "^hid_sensor|^industrialio" 
echo "===UVCVIDEO_SWAP (카메라 미연결 → 안전)==="
lsusb | grep -i -E "8086|intel" && echo "!! RealSense 연결됨 — uvcvideo 교체 보류" || {
  S modprobe -r uvcvideo && echo "uvcvideo unloaded"
  S modprobe uvcvideo && echo "uvcvideo (patched) loaded"
  modinfo -F vermagic uvcvideo; modinfo -F filename uvcvideo
}
echo "===DMESG==="
S dmesg 2>/dev/null | tail -8 | grep -iE "hid|uvc|taint|version|symbol" || S dmesg 2>/dev/null | tail -4
echo "===BRINGUP_ALIVE==="
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_DOWN
pgrep -af "ekf_node|robot_state_publisher" | cut -c1-80
