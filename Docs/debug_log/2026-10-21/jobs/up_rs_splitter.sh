#!/bin/bash
# 10-21 §17 2번 마무리 — 새 이미지로 시험 컨테이너 isaac_rs_test 생성(지금 컨테이너와 같은 옵션 + /dev 마운트: 카메라 재열거 대비),
#   그 안에서 realsense_splitter 빌드(작업 공간 build_rs/install_rs — 지금 컨테이너가 보는 install 과 분리), 합격 기준 (a)(b)(c) 확인. 카메라는 열지 않음.
N=isaac_rs_test; IMG=isaac_ros_dev-aarch64-rs:latest; WS=/home/jetson/workspaces/isaac_ros-dev
docker image inspect $IMG -f 'image {{.Id}} {{.Size}}' || exit 1
docker rm -f $N >/dev/null 2>&1
docker run -d --name $N --privileged --network host --ipc host --pid host --runtime nvidia \
  -e ISAAC_ROS_WS=/workspaces/isaac_ros-dev -e HOST_USER_UID=1000 -e HOST_USER_GID=1000 -e USER=jetson \
  -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all \
  -v /tmp/:/tmp/ -v /dev:/dev -v $WS:/workspaces/isaac_ros-dev -v /usr/bin/tegrastats:/usr/bin/tegrastats \
  -v /usr/lib/aarch64-linux-gnu/tegra:/usr/lib/aarch64-linux-gnu/tegra -v /usr/src/jetson_multimedia_api:/usr/src/jetson_multimedia_api \
  -v /usr/share/vpi3:/usr/share/vpi3 -v /etc/localtime:/etc/localtime:ro --workdir /workspaces/isaac_ros-dev --entrypoint /usr/local/bin/scripts/workspace-entrypoint.sh $IMG sleep infinity >/dev/null || exit 2
docker exec $N ls -l /usr/local/bin/scripts/workspace-entrypoint.sh; sleep 15; docker exec $N id admin; docker ps --format '{{.Names}} {{.Status}}' | grep $N
echo "== (a) 버전"
docker exec -u admin $N bash -c 'source /opt/ros/humble/setup.bash; rs-enumerate-devices --version 2>&1 | head -2; echo "realsense2_camera $(ros2 pkg xml realsense2_camera -t version)"; echo "realsense2_camera_msgs $(ros2 pkg xml realsense2_camera_msgs -t version)"'
echo "== (b) realsense_splitter 빌드"
docker exec -u admin $N bash -c 'cd /workspaces/isaac_ros-dev && source /opt/ros/humble/setup.bash && colcon build --packages-select realsense_splitter --build-base build_rs --install-base install_rs --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF 2>&1 | tail -6; source install_rs/setup.bash; ros2 pkg executables realsense_splitter; ls install_rs/realsense_splitter/lib | head'
echo "== (c) 기존 패키지"
docker exec -u admin $N bash -c 'source /opt/ros/humble/setup.bash; ros2 pkg list | grep -E "^(nvblox_ros|isaac_ros_visual_slam|nvblox_nav2)$"; python3 -c "import cv2, numpy; print(\"cv2\", cv2.__version__)"'
echo "== (d) 지금 스택 카메라 영향 — 호스트 카메라 프로세스 · 깊이 주기(sensors 로그 대신 프로세스 존재만, 새 참가자 안 만듦)"
pgrep -fc realsense2_camera; docker ps --format '{{.Names}} {{.Status}}'
