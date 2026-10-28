#!/bin/bash
# §16 place_web 확인(dry_run place_server 와 함께 — 목표를 Nav2 에 보내지 않음, 로버 안 움직임). 키는 출력하지 않는다
SRC=~/ros2_ws/src/rover_navigation
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
chmod +x $SRC/scripts/place_web.py
setsid nohup python3 $SRC/scripts/place_server.py --ros-args -p places_file:=$SRC/config/places.yaml -p dry_run:=true > /tmp/place_server_web.log 2>&1 &
PS=$!
setsid nohup python3 $SRC/scripts/place_web.py --ros-args -p places_file:=$SRC/config/places.yaml > /tmp/place_web.log 2>&1 &
PW_=$!; sleep 12
K=$(cat ~/.config/rover_web/key); echo "키 파일 권한 $(stat -c %a ~/.config/rover_web/key) · 길이 ${#K}"
U=http://127.0.0.1:8080
echo "키 없이 / → $(curl -s -o /dev/null -w %{http_code} $U/)"
echo "키 있음 / → $(curl -s -o /tmp/pw_page.html -w %{http_code} "$U/?k=$K") · $(wc -c < /tmp/pw_page.html) B · title $(grep -o '<title>[^<]*' /tmp/pw_page.html)"
echo "places → $(curl -s -H "X-Rover-Key: $K" $U/api/places)"
for c in "where" "go_to W3" "go_to 위 복도" "go_to 없는곳" "stop"; do
  echo "POST '$c' → $(curl -s -H "X-Rover-Key: $K" -H 'Content-Type: application/json' -d "{\"text\":\"$c\"}" $U/api/cmd)"; sleep 2.5; done
echo "== state"; curl -s -H "X-Rover-Key: $K" "$U/api/state?after=0" | python3 -c "import json,sys; s=json.load(sys.stdin); print('batt', s['batt'], 'subs', s['subs']); [print(' ', e['seq'], e['state'], e.get('place'), (e.get('detail') or '')[:110]) for e in s['log']]"
echo "== 외부 주소 열림"; ss -ltn | grep -c ":8080 "
echo "PC 시험용 대기 60 s"; sleep 60
kill -INT $PW_ $PS; sleep 2; kill -9 $PW_ $PS 2>/dev/null; pkill -f "path_end_yaw.py --serve" 2>/dev/null
echo "== place_web 로그"; grep -av "^\s*$" /tmp/place_web.log | sed 's/k=[A-Za-z0-9_-]*/k=<KEY>/g' | tail -8 | cut -c1-200
