#!/bin/bash
# 10-21 §17 — 새 이미지 isaac_ros_dev-aarch64-rs 빌드(지금 이미지 + NVIDIA Dockerfile.realsense). 백그라운드, 로그 ~/rs_build/build.log
D=~/workspaces/isaac_ros-dev/src/isaac_ros_common/docker; B=~/rs_build
echo "== buildx"; docker buildx version 2>&1 | head -1
echo "== image shell"; docker image inspect isaac_ros_dev-aarch64:latest -f '{{json .Config.Shell}} user={{.Config.User}}'
docker exec isaac_ros_dev-aarch64-container bash -c 'which sudo nvcc; ls /usr/local/cuda/bin/nvcc' 2>&1
rm -rf $B; mkdir -p $B; cp -r $D/scripts $D/udev_rules $B/; cp $D/Dockerfile.realsense $B/Dockerfile
# 바꾼 것 하나: make 동시 작업 수 3(기본 nproc-1=5) — 스택이 떠 있어 메모리 여유 확보. TODO(improve): 스택 내린 상태면 기본값 가능
sed -i 's|build-librealsense.sh -v ${LIBREALSENSE_SOURCE_VERSION};|build-librealsense.sh -v ${LIBREALSENSE_SOURCE_VERSION} -j 3;|' $B/Dockerfile
grep -n "build-librealsense.sh -v" $B/Dockerfile
cd $B; nohup bash -c "DOCKER_BUILDKIT=1 docker build --progress=plain --build-arg BASE_IMAGE=isaac_ros_dev-aarch64:latest -t isaac_ros_dev-aarch64-rs:latest . ; echo BUILD_EXIT=\$?" > $B/build.log 2>&1 &
sleep 20; echo "== log head"; tail -5 $B/build.log
