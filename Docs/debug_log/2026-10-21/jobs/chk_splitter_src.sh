#!/bin/bash
N=~/workspaces/isaac_ros-dev/src/isaac_ros_nvblox/nvblox_examples
cat $N/realsense_splitter/src/realsense_splitter_node.cpp | grep -v "^//" | grep -v "^ *$" | head -170
echo "==== header"; grep -v "^//" $N/realsense_splitter/include/realsense_splitter/*.hpp | grep -v "^ *$" | head -90
echo "==== launch sensors/realsense.launch.py"; grep -v "^#" $N/nvblox_examples_bringup/launch/sensors/realsense.launch.py | grep -v "^ *$"
echo "==== emitter_on yaml"; grep -v "^#" $N/nvblox_examples_bringup/config/sensors/realsense_emitter_on.yaml | grep -v "^ *$"
