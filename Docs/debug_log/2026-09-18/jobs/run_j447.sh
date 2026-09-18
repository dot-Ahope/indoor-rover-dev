#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'dpkg -l | grep -E "ros-humble-nav2-mppi|ros-humble-nav2-costmap-2d " | awk "{print \$2, \$3}"; echo "== critics.xml"; grep -o "name=\"[^\"]*\"" /opt/ros/humble/share/nav2_mppi_controller/critics.xml; echo "== headers"; ls /opt/ros/humble/include/nav2_mppi_controller/nav2_mppi_controller/critics/ 2>/dev/null || ls /opt/ros/humble/include/nav2_mppi_controller/critics/; echo "== obstacles_critic.hpp"; f=$(find /opt/ros/humble/include -name obstacles_critic.hpp | head -1); grep -nE "float|bool|distanceToObstacle|inCollision|costAtPose|possibly|inflation" $f | head -40'
