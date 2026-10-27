#!/bin/bash
# §17 결함 수정 (2026-10-27 §15~16): nvblox_nav2 층 slice 콜백 — lookupTransform 예외 때 경고만 찍고 계속 진행해
#   기본 생성 Transform(이동 0 · 회전 단위)으로 odom 슬라이스를 map 에 적던 것을, 그 슬라이스를 버리고 return 하도록.
#   return 하면 slice_ · T_G_S_ 둘 다 직전 값 그대로 → 짝이 맞는 직전 슬라이스를 계속 씀(전역 카메라 층이 0.1~0.5 s 늦을 뿐).
#   되돌리기: 아래 줄(// 2026-10-27 수정 표시) 삭제 후 재빌드. 09-21 floor 수정(job493)은 그대로 둔다.
set +u
R=/home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox
F=$R/nvblox_nav2/src/nvblox_costmap_layer.cpp
echo "== 수정 전 catch 부분"; grep -n -A6 'catch (tf2::TransformException' $F | cut -c1-140
python3 - "$F" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
mark = '// 2026-10-27 수정'
if mark in s: print('이미 수정됨'); sys.exit(0)
old = '          << ". Error: " << e.what());\n    }\n'
if s.count(old) != 1: print('패턴 %d 개 — 수정 안 함' % s.count(old)); sys.exit(1)
new = ('          << ". Error: " << e.what());\n'
       '      return;  ' + mark + ': 조회 실패 시 이 슬라이스를 버림(직전 slice_ · T_G_S_ 유지). 원래는 기본 Transform(단위)으로 odom 슬라이스를 map 에 적어 장애물이 0.5 m 틀어짐(rover 10-27 §15)\n'
       '    }\n')
open(p, 'w').write(s.replace(old, new)); print('수정함')
PY
echo "== 수정 후 catch 부분"; grep -n -A7 'catch (tf2::TransformException' $F | cut -c1-140
echo "== git diff ($R) — 09-21 floor + 10-27 return"; git -C $R --no-pager diff -- nvblox_nav2/src/nvblox_costmap_layer.cpp
source /opt/ros/humble/setup.bash; cd ~/ros2_ws
SO=~/ros2_ws/install/nvblox_nav2/lib/libnvblox_costmap_layer.so; B0=$(stat -c %Y $SO 2>/dev/null || echo 0)
T0=$(date +%s); colcon build --symlink-install --packages-select nvblox_nav2 --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | grep -aE "Starting|Finished|Failed|error:|Error|Summary" | tail -6 | cut -c1-160; echo "빌드 rc ${PIPESTATUS[0]} · 소요 $(( $(date +%s) - T0 )) s"
B1=$(stat -c %Y $SO 2>/dev/null || echo 0); echo ".so 갱신: $([ "$B1" -gt "$B0" ] && echo yes || echo NO) ($(date -d @$B1 '+%H:%M:%S' 2>/dev/null)) · sha $(sha256sum $SO | cut -c1-12)"
strings $SO | grep -c "Can't transform" | sed 's/^/경고 문자열 수 /'
echo "== 실행 중 Nav2 는 아직 옛 .so — prep 재기동 때 반영"
