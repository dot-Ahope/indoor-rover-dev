#!/bin/bash
# JetsonHacks 저장소 2종 클론 + 빌드 스크립트 원문 확인
cd ~
[ -d jetson-orin-kernel-builder ] || git clone -q https://github.com/jetsonhacks/jetson-orin-kernel-builder.git
[ -d jetson-orin-librealsense ] || git clone -q https://github.com/jetsonhacks/jetson-orin-librealsense.git
echo "===KB_TREE==="; ls jetson-orin-kernel-builder jetson-orin-kernel-builder/scripts
echo "===RS_BUILD_TREE==="; ls jetson-orin-librealsense jetson-orin-librealsense/build
echo "=====get_kernel_sources.sh====="; cat jetson-orin-kernel-builder/scripts/get_kernel_sources.sh
echo "=====make_kernel_modules.sh====="; cat jetson-orin-kernel-builder/scripts/make_kernel_modules.sh
echo "=====patch-for-realsense.sh====="; cat jetson-orin-librealsense/build/patch-for-realsense.sh
echo "=====build/README====="; cat jetson-orin-librealsense/build/README.md 2>/dev/null | head -120
echo "=====install-realsense-modules.sh (from prebuilt tar)====="; cd jetson-orin-librealsense && tar xzf install-modules.tar.gz -C /tmp 2>/dev/null; find /tmp -name "install-realsense-modules.sh" -exec cat {} \; 2>/dev/null | head -60
echo "===PROC_CONFIG==="; ls -l /proc/config.gz; zcat /proc/config.gz | grep -E "CONFIG_HID_SENSOR|CONFIG_USB_VIDEO_CLASS|CONFIG_IIO=|LOCALVERSION" 
