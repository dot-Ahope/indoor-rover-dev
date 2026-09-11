#!/bin/bash
# 손 이동 후 전체 검증: 재기동 → 코스 주행 → 복귀(출발 pose+180°) → face 0
set +u
NAME=${1:-v1}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "################ 1. 재기동 (base 유지, 원점 재설정) ################"
bash /tmp/job240_clean.sh 15 2>&1 | grep -aE "정리 후|base 계층|재기동 생략|wheel_odom|gyro bias|active \[3\]|decay_model|ExceptRegion|reset_distance|ZUPT|로버 자세|EKF 위반|^상자:|^   \[|최소폭" | sed 's/^/  /'
echo "  velocity_timeout=$(timeout 6 ros2 param get /velocity_smoother velocity_timeout 2>/dev/null | sed 's/^.*is: //') behavior_frame=$(timeout 6 ros2 param get /behavior_server global_frame 2>/dev/null | sed 's/^.*is: //') horizon=$(timeout 6 ros2 param get /controller_server FollowPath.max_allowed_time_to_collision_up_to_carrot 2>/dev/null | sed 's/^.*is: //') min_angle=$(timeout 6 ros2 param get /controller_server FollowPath.rotate_to_heading_min_angle 2>/dev/null | sed 's/^.*is: //')"
echo
echo "################ 2. 코스 주행 ################"
bash /tmp/job268_run3.sh $NAME 2>&1 | sed 's/S4 3\/3/코스 주행/' | grep -avE "^ *[0-9]+\.[0-9] [+-]"
echo
echo "################ 3. 복귀 → (0, 0, 180°) ################"
bash /tmp/job288_return_bag.sh ${NAME}_ret 0.0 0.0 180 2>&1
echo
echo "################ 4. face 0 ################"
python3 /tmp/job225_face.py 0 2.0 2>&1 | tail -1 | sed 's/^/  /'
echo -n "  최종: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
