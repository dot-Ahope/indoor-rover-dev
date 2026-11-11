#!/bin/bash
# chk_pose_1110 — 11-10 §7: 사용자가 멈춘 로버를 발로 돌린 뒤 스택이 지금 자세를 어떻게 보나(읽기만 · 로버 안 움직임).
#   보는 것: map→base_link(SLAM 위치 추정 포함) · odom→base_link(EKF, 자이로) 의 위치 · yaw, SLAM 이 마지막으로 스캔을 처리한 로그.
#   왜 둘 다: odom yaw 가 돌린 만큼 바뀌었으면 자이로가 봤다는 것, map yaw 와 odom yaw 의 차(=map→odom 보정)가 크게 튀었으면 SLAM 이 다시 맞춘 것.
#   ⚠ tf2_echo 는 DDS 참여자를 만든다 — 주행 30 s 전에는 돌리지 않는다. 인자: 없음. 출력: 표준 출력.
for p in "map base_link" "odom base_link" "map odom"; do
  echo "== $p"
  timeout 6 ros2 run tf2_ros tf2_echo $p 2>/dev/null | grep -aE 'Translation|RPY \(degree\)' | head -2
done
echo "== slam 마지막 처리 · 경고(끝 8)"
grep -aE 'slam_toolbox' /tmp/slam.log | tail -8 | cut -c1-200
