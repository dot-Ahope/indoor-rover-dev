#!/bin/bash
# 09-29 §9: 주행 스택을 내리고(base 유지) 카메라를 cuVSLAM 설정(IR 스테레오·프로젝터 끔)으로 띄운 뒤 컨테이너에서 cuVSLAM 3.2 기동
set +u
PATS="nvblox_up.sh nvblox_node depth_relay.py navigation.launch slam.launch sensors.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense2_camera foxglove_bridge visual_slam"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 5; for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
CN=isaac_ros_dev-aarch64-container
docker exec $CN bash -lc "pkill -f nvblox_node; pkill -f visual_slam_launch_container" 2>/dev/null
echo "== 정리 뒤 남은 스택 프로세스: $(for p in $PATS; do pgrep -fc "$p"; done | awk '{s+=$1} END {print s}') | base: $(systemctl --user is-active rover-base)"
: > /tmp/vslam_cam.log; : > /tmp/vslam_node.log
setsid nohup ros2 run realsense2_camera realsense2_camera_node --ros-args -r __node:=camera -r __ns:=/camera \
  -p enable_infra1:=true -p enable_infra2:=true -p enable_color:=false -p enable_depth:=false \
  -p depth_module.emitter_enabled:=0 -p depth_module.infra_profile:=640x360x30 -p depth_module.profile:=640x360x30 \
  -p enable_gyro:=true -p enable_accel:=true -p gyro_fps:=200 -p accel_fps:=200 -p unite_imu_method:=2 \
  -p initial_reset:=true -p publish_tf:=true > /tmp/vslam_cam.log 2>&1 < /dev/null &
sleep 12
echo "== 카메라: $(grep -aoE 'RealSense Node Is Up!|Open profile: .*' /tmp/vslam_cam.log | tr '\n' ';' | cut -c1-300)"
for t in /camera/camera/infra1/image_rect_raw /camera/camera/infra2/image_rect_raw /camera/camera/imu; do printf "  %-40s %s\n" $t "$(timeout 6 ros2 topic hz $t 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"; done
echo -n "  프로젝터(emitter_enabled): "; timeout 6 ros2 param get /camera/camera depth_module.emitter_enabled 2>&1 | tail -1
cp -f /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml /tmp/fastdds_udp_only.xml
# 컨테이너가 호스트 /tmp 를 공유하는지 모르므로 파일은 docker cp 로 넣는다
docker cp /tmp/vslam_standalone.launch.py $CN:/tmp/ && docker cp /tmp/job647_vslam_measure.py $CN:/tmp/ && docker cp /tmp/fastdds_udp_only.xml $CN:/tmp/
docker exec -d -u admin $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; ros2 launch /tmp/vslam_standalone.launch.py > /tmp/vslam_node.log 2>&1"
sleep 15
echo "== cuVSLAM 로그(주요):"; docker exec $CN cat /tmp/vslam_node.log | grep -aiE "error|warn|fail|cuvslam|version|tracker|started|imu" | cut -c1-200 | head -20
printf "  %-40s %s\n" /visual_slam/tracking/odometry "$(timeout 8 ros2 topic hz /visual_slam/tracking/odometry 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
