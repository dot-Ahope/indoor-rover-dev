#!/bin/bash
# nv1 실패 판별: (1) 시험 컨테이너 쓰기 층(apt 설치)을 이미지로 보존 (2) /dev 전체 마운트 빼고 옛 컨테이너와 같은 옵션으로 재생성
#   (3) NV_MODE=off 로 기동 → cuVSLAM 적재 여부 · NitrosContext 오류 · 토픽 주기(같은 컨테이너 ros2 topic hz)
N=isaac_rs_test; IMG=isaac_ros_dev-aarch64-rs:apt; WS=/home/jetson/workspaces/isaac_ros-dev
docker commit $N $IMG >/dev/null && docker image inspect $IMG -f 'commit {{.Id}} {{.Size}}'
docker rm -f $N >/dev/null
docker run -d --name $N --privileged --network host --ipc host --pid host --runtime nvidia \
  -e ISAAC_ROS_WS=/workspaces/isaac_ros-dev -e HOST_USER_UID=1000 -e HOST_USER_GID=1000 -e USER=jetson -e ROS_DOMAIN_ID \
  -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all \
  -v /tmp/:/tmp/ -v /dev/input:/dev/input -v $WS:/workspaces/isaac_ros-dev -v /usr/bin/tegrastats:/usr/bin/tegrastats \
  -v /usr/lib/aarch64-linux-gnu/tegra:/usr/lib/aarch64-linux-gnu/tegra -v /usr/src/jetson_multimedia_api:/usr/src/jetson_multimedia_api \
  -v /usr/share/vpi3:/usr/share/vpi3 -v /etc/localtime:/etc/localtime:ro --workdir /workspaces/isaac_ros-dev \
  --entrypoint /usr/local/bin/scripts/workspace-entrypoint.sh $IMG sleep infinity >/dev/null || exit 2
sleep 15; docker exec $N id admin
SRC='source /opt/ros/humble/setup.bash; source /workspaces/isaac_ros-dev/install_rs/setup.bash'
: > /tmp/nv_probe.log
docker exec -d -u admin $N bash -c "$SRC; export NV_MODE=off; exec ros2 launch /tmp/nv_static.launch.py > /tmp/nv_probe.log 2>&1"
sleep 25
grep -aE "NitrosContext\]: (cuda|\[NitrosContext\] set)|Loaded node|Failed to load|Open profile|process has died|emitter" /tmp/nv_probe.log | sed 's/\x1b\[[0-9;]*m//g' | cut -c1-200
docker exec -u admin $N bash -c "$SRC; ros2 topic list | grep -E 'camera|visual_slam' | head -30; for t in /camera/camera/depth/image_rect_raw /camera/camera/infra1/image_rect_raw /visual_slam/tracking/odometry; do echo \"\$t\"; timeout 8 ros2 topic hz \$t 2>&1 | grep average | tail -1; done"
docker exec $N bash -c "pkill -INT -f 'nv_static.launch.py|__node:=nv_static_container'; sleep 3; pkill -9 -f 'nv_static.launch.py|__node:=nv_static_container'" 2>/dev/null; sleep 2
echo "남은 $(pgrep -fc '__node:=nv_static_container')"
