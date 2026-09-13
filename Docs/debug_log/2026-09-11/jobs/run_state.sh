#!/bin/bash
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
ping -w 20 -c 1 192.168.0.101 >/dev/null 2>&1 && echo "핑 OK" || { echo "핑 실패 (Jetson 꺼짐/미연결)"; exit 1; }
sshpass -p <PW> ssh $OPT $J "echo ssh OK; uptime -p; echo '--- /tmp 잔존 ---'; ls /tmp | grep -cE '^job[0-9]+'; ls -d /tmp/bag_v5 /tmp/bag_v4 2>/dev/null; echo '--- 프로세스 ---'; docker ps --format '{{.Names}}' | grep -c microros_agent; for p in controller_server planner_server slam_toolbox ekf_node realsense2_camera_node rplidar sensor_conditioner robot_state_publisher bt_navigator behavior_server velocity_smoother; do printf '%-24s %s\n' \$p \$(pgrep -fc \$p); done"
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; echo '--- 토픽 ---'; for t in /wheel_odom /scan /camera/camera/depth/color/points /odometry/filtered /global_costmap/costmap; do printf '%-40s ' \$t; timeout 6 ros2 topic hz \$t 2>&1 | grep -aoE 'average rate: [0-9.]+' | head -1 || echo; echo; done; echo '--- 자세 ---'; timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE 'Translation|RPY' | head -2"
