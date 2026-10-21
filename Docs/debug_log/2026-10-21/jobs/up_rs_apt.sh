#!/bin/bash
# 10-21 §17.1 2번 마무리(재): 시험 컨테이너에만 옛 컨테이너와 같은 판 nvblox 3.2.5 · cuVSLAM 3.2.6 · bringup 3.2.13 apt 설치(모의 결과 Inst 46 · Remv 0 · realsense 변경 없음)
#   → realsense_splitter 는 원본(COLCON_IGNORE 붙어 배포)을 건드리지 않고 src_rs/ 로 복사해 빌드 → 기준 (a)(b)(c)(d) 재확인
N=isaac_rs_test; W=/workspaces/isaac_ros-dev
docker exec -u root $N bash -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y -q --no-install-recommends ros-humble-isaac-ros-nvblox=3.2.5-0jammy ros-humble-isaac-ros-visual-slam=3.2.6-0jammy ros-humble-nvblox-examples-bringup=3.2.13-0jammy 2>&1 | tail -3'
echo "== (a) 버전"
docker exec -u admin $N bash -c 'source /opt/ros/humble/setup.bash; rs-enumerate-devices --version 2>&1 | grep version; echo "realsense2_camera $(ros2 pkg xml realsense2_camera -t version)"; dpkg -l | awk "/realsense/ {print \$2, \$3}"'
echo "== (b) realsense_splitter 빌드(src_rs 복사본)"
docker exec -u admin $N bash -c "cd $W && mkdir -p src_rs && rm -rf src_rs/realsense_splitter && cp -r src/isaac_ros_nvblox/nvblox_examples/realsense_splitter src_rs/ && rm src_rs/realsense_splitter/COLCON_IGNORE && source /opt/ros/humble/setup.bash && colcon build --base-paths src_rs --packages-select realsense_splitter --build-base build_rs --install-base install_rs --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF 2>&1 | tail -5; source install_rs/setup.bash; ros2 component types | grep -A2 realsense_splitter; ls install_rs/realsense_splitter/lib"
echo "== (c) 기존 패키지"
docker exec -u admin $N bash -c 'source /opt/ros/humble/setup.bash; ros2 pkg list | grep -E "^(nvblox_ros|isaac_ros_visual_slam|nvblox_nav2|nvblox_examples_bringup)$"; ls /opt/ros/humble/share/nvblox_examples_bringup/config/sensors/realsense_emitter_flashing.yaml; ls /workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_examples/nvblox_examples_bringup/config/sensors/realsense_emitter_flashing.yaml'
echo "== (d) 지금 스택"; pgrep -fc realsense2_camera; docker ps --format '{{.Names}} {{.Status}}'
