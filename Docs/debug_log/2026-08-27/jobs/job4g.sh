#!/bin/bash
# RealSense IMU용 HID 센서 커널 모듈 소스 빌드 (root로 실행, 백그라운드, 로그 /tmp/hid_build.log)
# 절차: JetsonHacks jetson-orin-kernel-builder + jetson-orin-librealsense/build 를 비대화식으로 재구성
LOG=/tmp/hid_build.log
exec > >(tee -a "$LOG") 2>&1
set -o pipefail
echo "# HID MODULE BUILD START $(date '+%F %T')"
KVER=$(uname -r); echo "kernel: $KVER"
SRC=/usr/src/kernel/kernel-jammy-src
export HOME=/root

echo "== [1/6] build deps"
apt-get install -y -qq build-essential bc flex bison libssl-dev libelf-dev kmod wget 2>&1 | tail -1

echo "== [2/6] kernel sources (auto-detect L4T)"
cd /home/jetson/jetson-orin-kernel-builder
if [ ! -f "$SRC/Makefile" ]; then
  bash scripts/get_kernel_sources.sh --force-replace 2>&1 | grep -vE "^Linux_for_Tegra|^kernel/|^nvidia" | tail -15
  [ -f "$SRC/Makefile" ] || { echo "FAIL:get_sources"; exit 1; }
else
  echo "sources exist — reuse"
fi
head -5 "$SRC/Makefile" | grep -E "VERSION|PATCHLEVEL|SUBLEVEL"
grep CONFIG_LOCALVERSION= "$SRC/.config"

echo "== [3/6] uvc patches (optional — 실패 시 HID 모듈만 진행)"
cd /home/jetson/jetson-orin-librealsense/build
PATCH_OK=0
if bash patch-for-realsense.sh; then PATCH_OK=1; echo "PATCH_OK"; else echo "PATCH_FAILED -> continue without uvcvideo patch"; fi

echo "== [4/6] config: HID sensor modules = m"
cd "$SRC"
bash scripts/config --file .config \
  --module CONFIG_HID_SENSOR_HUB \
  --module CONFIG_HID_SENSOR_IIO_COMMON \
  --module CONFIG_HID_SENSOR_IIO_TRIGGER \
  --module CONFIG_HID_SENSOR_ACCEL_3D \
  --module CONFIG_HID_SENSOR_GYRO_3D
make olddefconfig >/dev/null
grep -E "CONFIG_HID_SENSOR_(HUB|IIO_COMMON|IIO_TRIGGER|ACCEL_3D|GYRO_3D)=|CONFIG_MODVERSIONS|CONFIG_LOCALVERSION=" .config

echo "== [5/6] build Image + modules (long)"
JOBS=$(( $(nproc) - 1 )); [ $JOBS -lt 1 ] && JOBS=1
time make -j$JOBS Image modules 2>&1 | grep -E "error|Error|warning: .*hid|CC .*hid-sensor|LD .*uvcvideo|Kernel: arch" | tail -40
MODS="drivers/hid/hid-sensor-hub.ko drivers/iio/common/hid-sensors/hid-sensor-iio-common.ko drivers/iio/common/hid-sensors/hid-sensor-trigger.ko drivers/iio/accel/hid-sensor-accel-3d.ko drivers/iio/gyro/hid-sensor-gyro-3d.ko"
for m in $MODS; do [ -f "$m" ] || { echo "FAIL:missing $m"; exit 1; }; done
echo "-- vermagic:"; modinfo drivers/hid/hid-sensor-hub.ko | grep -E "vermagic|depends"

echo "== [6/6] install to /lib/modules/$KVER + depmod"
B=/lib/modules/$KVER/kernel
for m in $MODS; do install -D "$m" "$B/$m" && echo "installed $B/$m"; done
if [ $PATCH_OK -eq 1 ] && [ -f drivers/media/usb/uvc/uvcvideo.ko ]; then
  cp -n "$B/drivers/media/usb/uvc/uvcvideo.ko" "$B/drivers/media/usb/uvc/uvcvideo.ko.original"
  install -D drivers/media/usb/uvc/uvcvideo.ko "$B/drivers/media/usb/uvc/uvcvideo.ko" && echo "installed patched uvcvideo.ko (backup .original)"
fi
depmod -a "$KVER"
modinfo hid_sensor_hub | grep -E "filename|vermagic"
echo "# BUILD DONE $(date '+%F %T')"
echo "BUILD_SUCCESS"
