#!/bin/bash
D=~/workspaces/isaac_ros-dev/src/isaac_ros_common/docker
echo "== build-librealsense.sh"; cat $D/scripts/build-librealsense.sh
echo "== install-realsense-dependencies.sh"; cat $D/scripts/install-realsense-dependencies.sh
echo "== ROS_ROOT in image"; docker image inspect isaac_ros_dev-aarch64:latest -f '{{range .Config.Env}}{{println .}}{{end}}' | grep -E "ROS_ROOT|ROS_DISTRO|BASE"
echo "== splitter package.xml"; cat ~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_examples/realsense_splitter/package.xml | grep -E "depend|name|version"
echo "== mem"; free -m; nproc
echo "== run_dev.sh docker run args"; grep -n -E "docker run|--privileged|--network|--ipc|-v |DOCKER_ARGS\+=" ~/workspaces/isaac_ros-dev/src/isaac_ros_common/scripts/run_dev.sh | head -40
