#!/bin/bash
# Step 0 추가 점검: L4T/JetPack 버전, USB 장치, CH340 인식 여부
echo "===L4T==="
cat /etc/nv_tegra_release 2>/dev/null || echo NO_TEGRA_RELEASE
echo "===JETPACK_PKGS==="
dpkg -l | grep -iE "jetpack|nvidia-l4t-core" | head -5
echo "===LSUSB==="
lsusb
echo "===TTY_ALL==="
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || echo NONE
echo "===CH341_MODULE==="
lsmod | grep -i ch34 || echo CH341_NOT_LOADED
modinfo ch341 >/dev/null 2>&1 && echo CH341_MODULE_AVAILABLE || echo CH341_MODULE_MISSING
echo "===DMESG_USB==="
dmesg 2>/dev/null | grep -iE "ch34|ttyUSB|1a86" | tail -10 || echo DMESG_DENIED
