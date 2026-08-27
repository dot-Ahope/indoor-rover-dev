#!/bin/bash
# 현재 Jetson의 RealSense 준비 상태 진단 (JETSON_REALSENSE_INSTALL.md 게이트 기준)
echo "===KERNEL==="; uname -r
echo "===L4T==="; head -1 /etc/nv_tegra_release
echo "===HID_MODULES(lsmod)==="; lsmod | grep -E "hid_sensor|uvcvideo" || echo NONE_LOADED
echo "===HID_MODULES(files)==="; find /lib/modules/$(uname -r) -name "hid-sensor*" -o -name "hid_sensor*" 2>/dev/null | head -5 || true
echo "===IIO==="; ls /sys/bus/iio/devices/ 2>/dev/null || echo NO_IIO
echo "===REALSENSE_UDEV==="; ls /etc/udev/rules.d/ | grep -i realsense || echo NO_REALSENSE_UDEV
echo "===PKGS==="; dpkg -l | grep -E "librealsense2|realsense2-camera|realsense2-description" | awk '{print $2, $3}'
echo "===INTEL_APT_REPO==="; ls /etc/apt/sources.list.d/ | grep -i realsense || echo NONE
echo "===DKMS==="; dpkg -l | grep -i dkms | awk '{print $2}' || echo NONE
echo "===USR_LOCAL_LIBS==="; ldconfig -p | grep realsense | grep local || echo NONE
echo "===GROUPS==="; groups
echo "===JETSONHACKS_CLONE==="; ls -d ~/jetson-orin-librealsense 2>/dev/null || echo NOT_CLONED
echo "===RPLIDAR_UDEV==="; ls /etc/udev/rules.d/ | grep -i rplidar || echo NO_RPLIDAR_UDEV
echo "===HOME_WS_HINTS==="; ls ~ | grep -iE "isaac|workspaces|handheld|bags" || echo NONE
