#!/bin/bash
# 장착 yaw 측정 실행 (정지, 모터 경로 없음): 라이다 노드 단독 + 카메라(IMU·컬러 끔) → 측정 → 두 노드 종료
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash; source /home/jetson/ros2_ws/install/setup.bash
echo "에이전트/주행 스택 실행 여부: $(pgrep -fc '[m]icro_ros_agent|[c]ontroller_server') 개 (0 이어야 모터 명령 경로 없음)"
pgrep -f "[r]obot_state_publisher" >/dev/null || { setsid nohup ros2 launch rover_description description.launch.py > /tmp/wall_rsp.log 2>&1 & RSP=1; }
pgrep -f '[r]plidar_node|[r]ealsense2_camera_node' >/dev/null && { echo "센서가 이미 떠 있음 — 그대로 측정"; STARTED=0; } || {
  setsid nohup ros2 run rplidar_ros rplidar_node --ros-args -p channel_type:=serial -p serial_port:=/dev/rplidar -p serial_baudrate:=1000000 \
     -p frame_id:=lidar_link -p inverted:=false -p angle_compensate:=true -p scan_mode:=Standard > /tmp/wall_lidar.log 2>&1 &
  setsid nohup ros2 launch rover_bringup camera.launch.py enable_imu:=false enable_color:=false > /tmp/wall_cam.log 2>&1 &
  STARTED=1; sleep 14; }
echo -n "/scan: "; timeout 6 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
python3 /tmp/job432c_wallyaw_tf.py 2>&1 | grep -avE '^\[(INFO|WARN)'
if [ "$STARTED" = 1 ]; then
  pkill -INT -f '[r]plidar_node'; pkill -INT -f 'ros2 launch rover_bringup [c]amera'; sleep 3
  pkill -9 -f '[r]plidar_node|[r]ealsense2_camera_node|[d]epth_relay'
  [ "$RSP" = 1 ] && pkill -INT -f "ros2 launch rover_description [d]escription"
  echo "센서 종료: 남은 $(pgrep -fc '[r]plidar_node|[r]ealsense2_camera_node') 개"
fi
