#!/bin/bash
# Phase N0 2단계 (2026-09-21): Isaac ROS Dev 컨테이너를 **상주형**으로 띄우고(run_dev.sh 의 docker run 인자 그대로, -it 대신 -d + sleep) 안에서 nvblox 를 apt 로 설치.
#   run_dev.sh 는 -it(TTY) 전제라 ssh 비대화식에서 못 쓴다. 엔트리포인트(workspace-entrypoint.sh)가 admin 사용자(NOPASSWD sudo)를 만든다.
#   09-21: 호스트에 CDI 스펙(/etc/cdi)이 없어 run_dev.sh 의 nvidia.com/gpu=all(CDI) 지정이 실패 → 레거시 NVIDIA_VISIBLE_DEVICES=all 로(GPU OK, PVA 불필요). CDI 생성(sudo nvidia-ctk cdi generate)은 필요해질 때만.
#   호스트 변경 없음(컨테이너 내부 apt). 되돌리기: docker rm -f isaac_ros_dev-aarch64-container
set +u
IMG=isaac_ros_dev-aarch64; CN=isaac_ros_dev-aarch64-container; WS=$HOME/workspaces/isaac_ros-dev
echo "== 이미지: $(docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | grep -E "^$IMG" | head -1)"
docker image inspect $IMG >/dev/null 2>&1 || { echo "★ 이미지 없음 — 빌드 미완료"; tail -3 /tmp/isaac_build.log; exit 1; }
if [ -z "$(docker ps -q --filter name=$CN --filter status=running)" ]; then
  docker rm -f $CN >/dev/null 2>&1
  docker run -d --privileged --network host --ipc=host --pid=host --runtime nvidia \
    -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all \
    -e ROS_DOMAIN_ID -e USER -e ISAAC_ROS_WS=/workspaces/isaac_ros-dev -e HOST_USER_UID=$(id -u) -e HOST_USER_GID=$(id -g) \
    -v /usr/bin/tegrastats:/usr/bin/tegrastats -v /tmp/:/tmp/ -v /usr/lib/aarch64-linux-gnu/tegra:/usr/lib/aarch64-linux-gnu/tegra \
    -v /usr/src/jetson_multimedia_api:/usr/src/jetson_multimedia_api -v /usr/share/vpi3:/usr/share/vpi3 -v /dev/input:/dev/input \
    -v $WS:/workspaces/isaac_ros-dev -v /etc/localtime:/etc/localtime:ro --name $CN \
    --entrypoint /usr/local/bin/scripts/workspace-entrypoint.sh --workdir /workspaces/isaac_ros-dev $IMG sleep infinity >/dev/null || exit 1
  sleep 5
fi
echo "== 컨테이너: $(docker ps --format '{{.Names}} {{.Status}}' | grep $CN)"
X() { docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "$1"; }
echo "== 안: $(X 'lsb_release -ds; echo ROS_DISTRO=$ROS_DISTRO; nvcc --version 2>/dev/null | grep -o "release [0-9.]*"; apt-cache policy ros-humble-isaac-ros-nvblox | grep -m1 Candidate' 2>&1 | tr '\n' ' ')"
echo "== nvblox 설치(컨테이너 내부 apt, 수 분)"
X 'sudo apt-get update -qq 2>&1 | tail -1; sudo apt-get install -y -qq ros-humble-isaac-ros-nvblox 2>&1 | tail -2'
echo "== 확인: $(X 'source /opt/ros/humble/setup.bash; ros2 pkg list 2>/dev/null | grep -E "^nvblox" | tr "\n" " "; ros2 pkg prefix nvblox_ros 2>/dev/null')"
echo "== 메시지 정의: $(X 'source /opt/ros/humble/setup.bash; ros2 interface show nvblox_msgs/msg/DistanceMapSlice 2>/dev/null | grep -vE "^\s*#" | tr "\n" " " | cut -c1-300')"
cp -f /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml /tmp/fastdds_udp_only.xml; echo "== DDS 프로파일 /tmp 복사(컨테이너와 공유): $(ls -la /tmp/fastdds_udp_only.xml | awk '{print $5}') B"
echo "== docker 디스크: $(docker system df --format '{{.Type}} {{.Size}}' | tr '\n' ';') | 여유 $(df -h / | tail -1 | awk '{print $4}')"
