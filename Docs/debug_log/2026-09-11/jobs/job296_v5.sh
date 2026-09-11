#!/bin/bash
# v5: 재기동 → 패딩 readback 게이트 → face 0 → 상자 게이트 → 코스 D=1.85 (복귀는 별도 판단)
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "################ 1. 재기동 (base 유지) ################"
bash /tmp/job240_clean.sh 15 2>&1 | grep -aE "정리 후|재기동 생략|wheel_odom|gyro bias|active \[3\]|로버 자세|EKF 위반|^상자:|^   \[" | sed 's/^/  /'
LP=$(timeout 6 ros2 param get /local_costmap/local_costmap footprint_padding 2>/dev/null | sed 's/^.*is: //'); GP=$(timeout 6 ros2 param get /global_costmap/global_costmap footprint_padding 2>/dev/null | sed 's/^.*is: //')
echo "  readback: padding local=$LP global=$GP | timeout=$(timeout 6 ros2 param get /velocity_smoother velocity_timeout 2>/dev/null | sed 's/^.*is: //') | behavior_frame=$(timeout 6 ros2 param get /behavior_server global_frame 2>/dev/null | sed 's/^.*is: //') | horizon=$(timeout 6 ros2 param get /controller_server FollowPath.max_allowed_time_to_collision_up_to_carrot 2>/dev/null | sed 's/^.*is: //') | min_angle=$(timeout 6 ros2 param get /controller_server FollowPath.rotate_to_heading_min_angle 2>/dev/null | sed 's/^.*is: //')"
[ "$LP" = "0.03" ] && [ "$GP" = "0.03" ] || { echo "  ★ 패딩 0.03 미적용 — 중단"; exit 1; }
echo "################ 2. face 0 ################"
python3 /tmp/job225_face.py 0 1.5 2>&1 | tail -1 | sed 's/^/  /'
echo "################ 3. 코스 주행 D=1.85 (패딩 0.03, 상자 기준 1.27/-0.15 ±0.25) ################"
bash /tmp/job254_s4run.sh v5 1.85 1.27 -0.15 0.25 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | grep -aE "상자:|상자 기준선|출발 자세|^결과|^  [①②③④⑤⑥]|조향|detected collision|clear entirely|clear except|Goal succeeded|backup|EKF 위반|게이트 실패|★|bag:"
echo -n "  최종 자세: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "  정면 벽: $(bash /tmp/job21c_where.sh 2>&1 | grep -a 정면 | grep -aoE '[0-9]+cm') | 후면: $(bash /tmp/job21c_where.sh 2>&1 | grep -a 후면 | grep -aoE '[0-9]+cm')"
