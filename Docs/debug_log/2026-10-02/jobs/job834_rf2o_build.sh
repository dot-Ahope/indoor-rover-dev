#!/bin/bash
# 10-02 §13 R0: rf2o(MAPIRlab ros2 브랜치) 별도 작업공간 ~/rf2o_ws 에 소스 빌드(slam_ws 와 같은 방식)
set -e
mkdir -p ~/rf2o_ws/src && cd ~/rf2o_ws/src
[ -d rf2o_laser_odometry ] || git clone -q -b ros2 https://github.com/MAPIRlab/rf2o_laser_odometry.git
cd rf2o_laser_odometry && echo "커밋 $(git rev-parse --short HEAD) $(git log -1 --format=%cd --date=short)"
grep -n "covariance\|odom_topic\|freq\|laser_scan_topic\|base_frame_id\|odom_frame_id\|publish_tf\|init_pose" src/*.cpp include/*/*.h launch/* 2>/dev/null | head -30
cd ~/rf2o_ws && source /opt/ros/humble/setup.bash && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -3
ls ~/rf2o_ws/install/rf2o_laser_odometry/lib/rf2o_laser_odometry/
