#!/bin/bash
# prep_relocalize_1110 — 11-10 §8: 발로 돌린 뒤 틀린 SLAM 자세(yaw 51°, 실제는 통로 방향 ≈ 76~92° — 사용자)를 제자리에서 다시 잡음. 로버 안 움직임.
#   왜: 틀린 map 자세로 실시간 장애물이 돌아간 자리에 찍혀 전역 계획 '경로 없음'(f2dm1h). 손으로 출발점에 옮기지 않고 복귀하라는 사용자 지시.
#   하는 일: ① /initialpose 구독자 확인(slam_toolbox 위치 추정 모드가 받는지) ② map 기준 자세 1 회 발행 ③ 3 · 8 s 뒤 map→base_link 읽기
#            ④ 로컬 · 전역 코스트맵 비우기(틀린 자세로 그린 표시 제거). ⚠ DDS 참여자 생성 — 이 뒤 30 s 는 주행 시작하지 않는다.
#   인자: X Y YAW_DEG (기본 -1.626 -5.206 85). 출력: 표준 출력.
X=${1:--1.626}; Y=${2:--5.206}; YAW=${3:-85}
echo "== ① /initialpose 구독"; timeout 8 ros2 topic info /initialpose 2>&1 | grep -aE 'Type|Subscription count'
echo "== 이전 자세"; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE 'Translation|RPY \(degree\)' | head -2
read QZ QW < <(python3 -c "import math;y=math.radians($YAW);print(math.sin(y/2),math.cos(y/2))")
echo "== ② 발행 x=$X y=$Y yaw=$YAW° (qz=$QZ qw=$QW)"
timeout 10 ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: map}, pose: {pose: {position: {x: $X, y: $Y, z: 0.0}, orientation: {z: $QZ, w: $QW}}, covariance: [0.04,0,0,0,0,0, 0,0.04,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0, 0,0,0,0,0,0.12]}}" 2>&1 | tail -1
for t in 3 8; do sleep $([ $t = 3 ] && echo 3 || echo 5); echo "== ③ ${t} s 뒤 map→base_link"; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE 'Translation|RPY \(degree\)' | head -2; done
echo "== slam 로그(끝 5)"; grep -a slam_toolbox /tmp/slam.log | tail -5 | cut -c1-200
echo "== ④ 코스트맵 비우기"
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" 2>&1 | tail -1 | cut -c1-120
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" 2>&1 | tail -1 | cut -c1-120
echo "== $(date +%T) 끝"
