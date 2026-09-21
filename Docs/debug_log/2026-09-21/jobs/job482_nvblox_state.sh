#!/bin/bash
CN=isaac_ros_dev-aarch64-container
echo "== 컨테이너 안 nvblox 프로세스:"; docker exec $CN bash -c "ps -eo pid,ppid,etimes,pcpu,args | grep -E 'nvblox|ros2 run' | grep -v grep | cut -c1-150"
echo "== 로그 v05_dec4 끝:"; tail -20 /tmp/nvblox_v05_dec4.log | grep -avE "^\s*$" | cut -c1-160 | tail -12
echo "== 로그 v03_dec4 오류/경고:"; grep -aiE "error|warn|except|fatal|cuda|frame" /tmp/nvblox_v03_dec4.log | head -6 | cut -c1-160
echo "== 원래 n0 로그 끝(pid 살아있나):"; tail -2 /tmp/nvblox_n0.log | cut -c1-120
echo "== 슬라이스 hz(컨테이너):"; docker exec -u admin $CN bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 10 ros2 topic hz /nvblox_node/static_map_slice 2>&1 | grep -ao "average rate: [0-9.]*" | head -1; timeout 10 ros2 node list 2>/dev/null | grep -c nvblox'
echo "== 호스트 깊이 이미지 크기 지금: $(export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field width 2>/dev/null | head -1) | dec 파라미터 $(timeout 8 ros2 param get /camera/camera decimation_filter.filter_magnitude 2>&1 | tail -1)"
