#!/bin/bash
echo "=== 설치 전 ==="
apt-cache policy ros-humble-spatio-temporal-voxel-layer 2>/dev/null | head -3 | sed 's/^/  /'
echo "  디스크 여유: $(df -h / | tail -1 | awk '{print $4}')"
echo "=== 설치 (sudo) ==="
echo <PW> | sudo -S apt-get install -y ros-humble-spatio-temporal-voxel-layer 2>&1 | tail -8 | sed 's/^/  /'
echo "=== 설치 확인 ==="
source /opt/ros/humble/setup.bash
ros2 pkg list 2>/dev/null | grep -ai spatio | sed 's/^/  pkg: /' || echo "  pkg 없음"
ls /opt/ros/humble/lib/ 2>/dev/null | grep -ai spatio | sed 's/^/  lib: /'
echo "=== 등록된 플러그인 클래스 ==="
grep -rhoE 'type="[^"]*SpatioTemporal[^"]*"' /opt/ros/humble/share/spatio_temporal_voxel_layer/*.xml 2>/dev/null | sed 's/^/  /'
cat /opt/ros/humble/share/spatio_temporal_voxel_layer/*.xml 2>/dev/null | head -12 | sed 's/^/  /'
