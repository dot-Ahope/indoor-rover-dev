#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 사용 중인 코스트맵 레이어 플러그인 ==="
grep -aE "plugin: \"nav2_costmap_2d|plugin: \"spatio" ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml | sed 's/^/  /'
echo ""
echo "=== STVL 설치 여부 ==="
dpkg -l 2>/dev/null | grep -ai "spatio\|stvl" | sed 's/^/  /' || echo "  apt 패키지 없음"
ls /opt/ros/humble/lib/ 2>/dev/null | grep -ai spatio | sed 's/^/  lib: /' || echo "  /opt/ros/humble/lib 에 없음"
ros2 pkg list 2>/dev/null | grep -ai spatio | sed 's/^/  pkg: /' || echo "  ros2 pkg list 에 없음"
echo ""
echo "=== apt 에서 설치 가능한가 ==="
apt-cache policy ros-humble-spatio-temporal-voxel-layer 2>/dev/null | head -4 | sed 's/^/  /'
echo ""
echo "=== 등록된 코스트맵 레이어 플러그인 목록 ==="
grep -rhoE "nav2_costmap_2d::[A-Za-z]+Layer" /opt/ros/humble/share/nav2_costmap_2d/*.xml 2>/dev/null | sort -u | sed 's/^/  /'
echo ""
echo "=== nav2 코스트맵이 제공하는 소거 관련 서비스 ==="
ros2 service list 2>/dev/null | grep -aiE "clear" | sed 's/^/  /'
