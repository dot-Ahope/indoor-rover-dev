#!/bin/bash
# depth_relay CPU 프로파일: 두 번째 인스턴스를 cProfile 로 12 s 돌려 단계별 시간 (원 릴레이는 그대로)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 상위 CPU 프로세스(명령줄) ==="
ps -eo pcpu,pid,args --sort=-pcpu | head -8 | cut -c1-120
R=$(ls ~/ros2_ws/install/rover_bringup/lib/rover_bringup/depth_relay.py 2>/dev/null || find ~/ros2_ws/install -name depth_relay.py | head -1)
echo "relay: $R"
timeout 14 python3 -m cProfile -o /tmp/relay.prof $R --ros-args -r __node:=depth_relay_prof -p out_topic:=/relay_prof -p min_range:=0.45 -p voxel:=0.05 -p min_points_per_voxel:=3 -p persist_frames:=5 -p persist_min:=3 -p process_every:=1 >/dev/null 2>&1
python3 - <<'PY'
import pstats
p = pstats.Stats('/tmp/relay.prof'); p.sort_stats('tottime')
print('=== tottime 상위 14 (12 s 실행) ===')
p.print_stats(14)
PY
echo "=== 원 릴레이 프레임 처리 시간 로그(있으면) ==="; grep -a "ms" /tmp/sensors.log 2>/dev/null | grep -ai relay | tail -3 | cut -c1-160
