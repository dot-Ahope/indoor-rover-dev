#!/bin/bash
# 10-07 §6: 어느 컨트롤러 플러그인이 FollowPath 인가(읽기만)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for p in controller_plugins FollowPath.plugin FollowPathMPPI.plugin FollowPath.transform_tolerance FollowPathMPPI.transform_tolerance; do echo "$p: $(timeout 8 ros2 param get /controller_server $p 2>&1 | tail -1)"; done
