#!/bin/bash
# 2번(컨테이너 RealSense 층 + realsense_splitter) 사전 조사 — 읽기만 (10-21 §17)
echo "== docker images"; docker images --format '{{.Repository}}:{{.Tag}} {{.Size}} {{.CreatedSince}}' | head -20
echo "== containers"; docker ps -a --format '{{.Names}} {{.Image}} {{.Status}}'
echo "== isaac ws"; ls ~/workspaces/isaac_ros-dev/ 2>&1; ls ~/workspaces/isaac_ros-dev/src 2>&1
echo "== isaac_ros_common"; ls ~/workspaces/isaac_ros-dev/src/isaac_ros_common/docker 2>&1 | head -40
echo "== .isaac_ros_common-config"; cat ~/.isaac_ros_common-config 2>&1; cat ~/workspaces/isaac_ros-dev/src/isaac_ros_common/scripts/.isaac_ros_common-config 2>&1
echo "== nvblox container inspect"; for c in $(docker ps -a --format '{{.Names}}'); do echo "-- $c"; docker inspect -f '{{.Config.Image}} net={{.HostConfig.NetworkMode}} ipc={{.HostConfig.IpcMode}} priv={{.HostConfig.Privileged}} binds={{.HostConfig.Binds}} devs={{.HostConfig.Devices}}' $c; done
echo "== in container pkgs"; C=$(docker ps --format '{{.Names}}' | grep -i isaac | head -1); echo "C=$C"; [ -n "$C" ] && docker exec $C bash -c 'source /opt/ros/humble/setup.bash; ros2 pkg list 2>/dev/null | grep -i -E "realsense|nvblox|visual_slam|splitter"; dpkg -l | grep -i realsense | head; ls /workspaces/isaac_ros-dev/src 2>&1; ls /workspaces/isaac_ros-dev/install 2>&1 | head -30'
echo "== disk"; df -h / /home | tail -2
echo "== internet"; timeout 6 curl -sI https://github.com | head -1
echo "== host realsense"; dpkg -l | grep -i -E "librealsense|realsense2" | awk '{print $2,$3}'
