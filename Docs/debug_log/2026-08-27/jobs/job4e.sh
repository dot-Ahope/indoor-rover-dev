#!/bin/bash
# Step 4 준비 (저리스크): rplidar_ros 설치, RealSense 패키지 업그레이드, udev 규칙 2종
PW='<PW>'
S() { echo "$PW" | sudo -S -p '' "$@"; }
echo "===APT_UPDATE==="
S apt-get update -qq 2>&1 | tail -2
echo "===INSTALL_RPLIDAR==="
S apt-get install -y ros-humble-rplidar-ros 2>&1 | tail -2
echo "===UPGRADE_REALSENSE==="
S apt-get install -y --only-upgrade ros-humble-librealsense2 ros-humble-realsense2-camera ros-humble-realsense2-camera-msgs ros-humble-realsense2-description 2>&1 | tail -3
dpkg -l | grep -E "librealsense2 |realsense2-camera |rplidar-ros" | awk '{print $2, $3}'
echo "===UDEV_RPLIDAR==="
S bash -c 'cat > /etc/udev/rules.d/99-rplidar.rules << "EOR"
# RPLidar S2L (CP210x 10c4:ea60) -> /dev/rplidar
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="rplidar", GROUP="dialout", MODE="0660"
EOR'
echo "===UDEV_REALSENSE==="
RULES_SRC=$(dpkg -L ros-humble-librealsense2 2>/dev/null | grep "99-realsense-libusb.rules" | head -1)
if [ -n "$RULES_SRC" ]; then
  echo "from deb: $RULES_SRC"; cp "$RULES_SRC" /tmp/99-realsense-libusb.rules
else
  VER=$(dpkg -l | grep "ros-humble-librealsense2 " | awk '{print $3}' | cut -d- -f1)
  echo "deb has no rules; fetching tag v$VER"
  curl -fsSL -o /tmp/99-realsense-libusb.rules "https://raw.githubusercontent.com/IntelRealSense/librealsense/v$VER/config/99-realsense-libusb.rules" \
   || curl -fsSL -o /tmp/99-realsense-libusb.rules https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules
fi
[ -s /tmp/99-realsense-libusb.rules ] && S install -m 644 /tmp/99-realsense-libusb.rules /etc/udev/rules.d/99-realsense-libusb.rules && echo "installed ($(wc -l < /tmp/99-realsense-libusb.rules) lines)" || echo "!! realsense rules NOT obtained"
S udevadm control --reload-rules && S udevadm trigger
ls -l /etc/udev/rules.d/ | grep -E "rplidar|realsense|rover"
echo "===DISK==="
df -h / | tail -1
