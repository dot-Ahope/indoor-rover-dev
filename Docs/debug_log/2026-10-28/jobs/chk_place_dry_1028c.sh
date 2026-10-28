#!/bin/bash
# §8 f2pl1 통로 북쪽 거절 재현(dry_run(dry_run — 목표를 Nav2 에 보내지 않음, 로버 안 움직임): src 에 올린 place_server 를 띄우고 명령 창구로 검사
SRC=~/ros2_ws/src/rover_navigation
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 -c "import yaml" 2>&1 | head -1
setsid nohup python3 $SRC/scripts/place_server.py --ros-args -p places_file:=$SRC/config/places.yaml -p dry_run:=true > /tmp/place_server_dry_c.log 2>&1 &
PS=$!; sleep 12
C="python3 $SRC/scripts/place_cmd.py"
for c in "where" "go_to 통로 북쪽" "go_to 통로 북쪽" "go_to 통로 북쪽" "go_to 남서" "go_to B" "go_to W3" "return"; do echo "## $c"; $C $c --wait 25; echo "  rc $?"; done
kill -INT $PS; sleep 2; kill -9 $PS 2>/dev/null; pkill -f "path_end_yaw.py --serve" 2>/dev/null
echo "== 서버 로그"; grep -av "^\s*$" /tmp/place_server_dry_c.log | tail -25 | cut -c1-220
