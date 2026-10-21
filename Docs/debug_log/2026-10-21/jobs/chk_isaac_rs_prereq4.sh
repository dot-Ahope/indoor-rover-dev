#!/bin/bash
C=isaac_ros_dev-aarch64-container
docker inspect $C -f 'runtime={{.HostConfig.Runtime}} pid={{.HostConfig.PidMode}} user={{.Config.User}} entry={{json .Config.Entrypoint}} cmd={{json .Config.Cmd}} workdir={{.Config.WorkingDir}}'
docker inspect $C -f '{{range .Config.Env}}{{println .}}{{end}}' | grep -v -E "^PATH=|^LD_LIBRARY|^PYTHONPATH|^AMENT|^CMAKE|^COLCON" | head -40
docker inspect $C -f '{{json .HostConfig.DeviceRequests}} {{json .HostConfig.CapAdd}} {{json .HostConfig.Tmpfs}} restart={{.HostConfig.RestartPolicy.Name}}'
echo "== vslam share"; docker exec $C bash -c 'ls /opt/ros/humble/share/isaac_ros_visual_slam/launch; grep -n -i "qos" /opt/ros/humble/share/isaac_ros_visual_slam/launch/*realsense*.py | head; strings /opt/ros/humble/lib/libvisual_slam_node.so 2>/dev/null | grep -i -E "^[a-z_]*qos[a-z_]*$" | sort -u | head; ls /opt/ros/humble/lib | grep -i visual_slam | head'
echo "== nvblox qos param"; docker exec $C bash -c 'strings /opt/ros/humble/lib/libnvblox_node.so 2>/dev/null | grep -i -E "^[a-z_]*qos[a-z_]*$" | sort -u | head; python3 -c "import cv2; print(cv2.__version__)"'
