#!/bin/bash
# N2~N3 1단계 2차 (2026-09-21): isaac_ros_common 의 cmake extras 가 CUDA 를 강제(FindCUDA REQUIRED)해 호스트 빌드 실패 →
#   nvblox_nav2 는 ament_auto_find_build_dependencies() 로 존재만 확인하고 nvblox_msgs 는 CMake 에서 아예 안 씀 → **빈 스텁 패키지** isaac_ros_common(ament_cmake) 로 대체(호스트 전용, 컨테이너와 무관).
#   C++17 은 nvblox_nav2 CMake 가 스스로 설정. 되돌리기: rm -rf ~/ros2_ws/src/isaac_ros_common_stub ~/ros2_ws/src/{nvblox_msgs,nvblox_nav2} ~/ros2_ws/{build,install}/{isaac_ros_common,nvblox_msgs,nvblox_nav2}
set +u
source /opt/ros/humble/setup.bash
cd ~/ros2_ws/src; rm -f isaac_ros_common; rm -rf ~/ros2_ws/build/isaac_ros_common ~/ros2_ws/install/isaac_ros_common
mkdir -p isaac_ros_common_stub; cd isaac_ros_common_stub
cat > package.xml <<'PX'
<?xml version="1.0"?>
<package format="3">
  <name>isaac_ros_common</name>
  <version>3.2.5</version>
  <description>Host-side stub (2026-09-21): satisfies nvblox_nav2/nvblox_msgs dependency without CUDA. Real package lives in the Isaac ROS container.</description>
  <maintainer email="none@example.com">rover</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <export><build_type>ament_cmake</build_type></export>
</package>
PX
cat > CMakeLists.txt <<'CM'
cmake_minimum_required(VERSION 3.5)
project(isaac_ros_common)
find_package(ament_cmake REQUIRED)
ament_package()
CM
cd ~/ros2_ws
T0=$(date +%s); colcon build --symlink-install --packages-select isaac_ros_common nvblox_msgs nvblox_nav2 --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | grep -aE "Starting|Finished|Failed|error:|Error|Summary|warning: unused" | tail -14 | cut -c1-160; echo "빌드 소요 $(( $(date +%s) - T0 )) s"
source ~/ros2_ws/install/setup.bash
echo "pkg: $(ros2 pkg list 2>/dev/null | grep -E 'nvblox|isaac_ros_common' | tr '\n' ' ')"
echo ".so: $(ls ~/ros2_ws/install/nvblox_nav2/lib/ 2>/dev/null | grep -E '\.so' | tr '\n' ' ') | 플러그인 xml: $(ls ~/ros2_ws/install/nvblox_nav2/share/nvblox_nav2/*.xml 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"
echo "pluginlib 등록: $(ros2 run nav2_costmap_2d --help >/dev/null 2>&1; python3 - <<'PY'
from ament_index_python.packages import get_packages_with_prefixes
import subprocess
out = subprocess.run(['bash','-lc','source ~/ros2_ws/install/setup.bash; ros2 pkg xml nvblox_nav2 | grep -o "nav2_costmap_2d plugin=\"[^\"]*\""'], capture_output=True, text=True).stdout.strip()
print(out or '(package.xml export 없음)')
PY
)"
echo "msg: $(ros2 interface list 2>/dev/null | grep -c nvblox_msgs) 개 | DistanceMapSlice 필드 $(ros2 interface show nvblox_msgs/msg/DistanceMapSlice 2>/dev/null | grep -cvE '^\s*#|^\s*$') 줄"
echo "install 목록: $(ls ~/ros2_ws/install | grep -vE 'setup|local_' | tr '\n' ' ')"
