#!/bin/bash
# Phase N0 3단계 (2026-09-21): 호스트 센서 스택(카메라·라이다·EKF·SLAM, Nav2 없음) 위에서 컨테이너의 nvblox_node 를 깊이 전용으로 띄운다. 인자: start|stop|status|log
#   입력 리매핑: camera_0/depth/image ← /camera/camera/depth/image_rect_raw, camera_0/depth/camera_info ← /camera/camera/depth/camera_info (예제 get_realsense_remappings 와 같음, splitter 없음)
#   DDS: 호스트와 같은 UDP 전용 프로파일(/tmp/fastdds_udp_only.xml, /tmp 는 컨테이너에 마운트). 로그 /tmp/nvblox_n0.log (통계 출력 포함)
set +u
CN=isaac_ros_dev-aarch64-container; CMD=${1:-status}
X() { docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "$1"; }
case "$CMD" in
  start)
    X 'pkill -f nvblox_node 2>/dev/null; true'
    docker exec -d -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; exec ros2 run nvblox_ros nvblox_node --ros-args --params-file /tmp/nvblox_n0.yaml -r camera_0/depth/image:=/camera/camera/depth/image_rect_raw -r camera_0/depth/camera_info:=/camera/camera/depth/camera_info > /tmp/nvblox_n0.log 2>&1'
    sleep 12; echo "nvblox_node: $(X 'pgrep -fc nvblox_node')"; tail -8 /tmp/nvblox_n0.log | cut -c1-160 ;;
  stop)  X 'pkill -INT -f nvblox_node; sleep 2; pkill -9 -f nvblox_node 2>/dev/null; true'; echo "stopped" ;;
  log)   grep -aE "rate|Hz|ms|delay|drop|Error|error|WARN" /tmp/nvblox_n0.log | tail -${2:-25} | cut -c1-170 ;;
  *)     echo "nvblox_node: $(X 'pgrep -fc nvblox_node') | 토픽: $(X 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 8 ros2 topic list 2>/dev/null | grep -E "nvblox|map_slice|esdf" | tr "\n" " "')"; tail -3 /tmp/nvblox_n0.log | cut -c1-160 ;;
esac
