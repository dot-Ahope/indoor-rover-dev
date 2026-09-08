#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo -n "cmd_vel (정지 확인): "; timeout 4 ros2 topic echo --once /cmd_vel 2>/dev/null | grep -E "^  x:" | head -1 || echo "발행 없음(정지)"
echo -n "status: "; timeout 5 ros2 topic echo --once /rover/status 2>/dev/null | grep message | head -1
echo -n "배터리: "; timeout 5 ros2 topic echo --once /battery 2>/dev/null | grep "^voltage"
echo "== 박스 방향 코스트맵 여유 계산 =="
python3 - << 'PY'
box_y=0.13; box_x=0.85; infl=0.35; half=0.215
left_edge=box_y+0.05+infl; right_edge=box_y-0.05-infl
Lwall=0.78; Rwall=-0.59
print(f"박스+인플레이션 점유 y: {right_edge:+.2f} ~ {left_edge:+.2f}")
print(f"좌측 통과 필요 y>{left_edge+half:+.2f}, 좌벽 {Lwall:+.2f} → 슬롯 {Lwall-(left_edge+half):+.2f}m")
print(f"우측 통과 필요 y<{right_edge-half:+.2f}, 우벽 {Rwall:+.2f} → 슬롯 {(right_edge-half)-Rwall:+.2f}m")
PY
