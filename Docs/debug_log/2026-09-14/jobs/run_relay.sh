#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in depth_relay.py CMakeLists.txt camera.launch.py nav2_params.yaml job311_floor_noise.py job312_box_edge.py; do tr -d '\r' < $SPS/$f > /tmp/$f; done
sshpass -p <PW> scp $OPT -q /tmp/depth_relay.py $J:~/ros2_ws/src/rover_bringup/scripts/depth_relay.py || exit 1
sshpass -p <PW> scp $OPT -q /tmp/CMakeLists.txt $J:~/ros2_ws/src/rover_bringup/CMakeLists.txt || exit 1
sshpass -p <PW> scp $OPT -q /tmp/camera.launch.py $J:~/ros2_ws/src/rover_bringup/launch/camera.launch.py || exit 1
sshpass -p <PW> scp $OPT -q /tmp/nav2_params.yaml $J:/tmp/nav2_params.yaml || exit 1
sshpass -p <PW> scp $OPT -q /tmp/job311_floor_noise.py $J:/tmp/job311_floor_noise.py; sshpass -p <PW> scp $OPT -q /tmp/job312_box_edge.py $J:/tmp/job312_box_edge.py
cat > /tmp/relay_remote.sh <<'REMOTE_END'
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
chmod +x ~/ros2_ws/src/rover_bringup/scripts/depth_relay.py
echo "=== 1. colcon build rover_bringup (symlink) ==="
cd ~/ros2_ws && colcon build --packages-select rover_bringup --symlink-install 2>&1 | tail -3
ls -la ~/ros2_ws/install/rover_bringup/lib/rover_bringup/depth_relay.py
source ~/ros2_ws/install/setup.bash
echo "=== 2. 릴레이 기동 (standalone; 다음 부팅부터는 camera.launch 가 띄움) ==="
pkill -TERM -f depth_relay.py 2>/dev/null; sleep 1
setsid nohup ros2 run rover_bringup depth_relay.py --ros-args -p min_range:=0.45 -p voxel:=0.05 -p min_points_per_voxel:=3 > /tmp/relay.log 2>&1 &
sleep 6
printf 'in  '; timeout 6 ros2 topic hz /camera/camera/depth/color/points 2>&1 | grep -aoE 'average rate: [0-9.]+' | head -1
printf 'out '; timeout 6 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -aoE 'average rate: [0-9.]+' | head -1
sleep 5; grep -a '프레임:' /tmp/relay.log | tail -1
echo "=== 3. 정면 바닥 아티팩트 (필터 후, 30 s) ==="
TOPIC=/camera/depth/points_filtered python3 /tmp/job311_floor_noise.py 30 2>&1 | grep -av '^\[INFO\]'
echo "=== 4. 상자 가장자리 (필터 후, 20 s) ==="
TOPIC=/camera/depth/points_filtered python3 /tmp/job312_box_edge.py 1.19 -0.034 20 2>&1 | grep -av '^\[INFO\]' | grep -avE '코스트맵'
echo "=== 5. nav2 재기동 (STVL → 필터 토픽) ==="
bash /tmp/job249_nav2only.sh 2>&1 | grep -aE '검증|중복|적용값|자세|상자:|최소폭|근거 없는 셀 위치' | head -12
echo "=== 6. STVL 구독 확인 + 릴레이 통계 ==="
timeout 8 ros2 topic info /camera/depth/points_filtered --verbose 2>/dev/null | grep -aE 'Node name|Subscription count' | head -6
grep -a '프레임:' /tmp/relay.log | tail -1
REMOTE_END
sshpass -p <PW> scp $OPT -q /tmp/relay_remote.sh $J:/tmp/relay_remote.sh
timeout 560 sshpass -p <PW> ssh $OPT $J "bash /tmp/relay_remote.sh"
