#!/bin/bash
# chk_roslog_f2dm2_1111 — 11-11: f2dm2(11-10 17:55:17 출발, 사용자 강제 종료) 를 재부팅에도 남는 ~/.ros/log 로 재구성(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: Jetson 재부팅(11-11 10:51)으로 /tmp 의 bag · 러너 원문이 사라짐(chk_f2dm2_left_1111). ROS 2 launch 는 노드 출력을 ~/.ros/log/<시각>/launch.log 에도 쓴다.
#   보는 것: 11-10 17:40 이후 생긴 launch 로그 폴더 목록, 그중 Nav2(bt_navigator 포함) · slam 로그에서 17:55 ~ 끝 사이 주요 줄:
#     bt_navigator 목표 시작 · 성공 · 실패, planner 실패, controller 도달 · 실패, behavior(복구), nav_guard, stuck_monitor, 마지막 줄 시각(= 강제 종료 무렵).
#   시각: 로그의 유닉스 초를 KST 로 바꿔 앞에 붙임. 인자: 없음. 출력: 표준 출력.
cd ~/.ros/log || exit 1
echo "== 11-10 17:40 이후 launch 폴더"
find . -maxdepth 1 -type d -newermt '2026-11-10 17:40' ! -newermt '2026-11-11 10:00' | sort | while read d; do
  echo "  $d $(head -c 300 $d/launch.log 2>/dev/null | grep -ao 'launch [a-z_]*\.launch\.py\|rover_[a-z]*' | head -1) $(stat -c %s $d/launch.log 2>/dev/null) B"; done
# 1 차 실행 뒤 고침: launch.log 는 17 줄뿐(노드가 output='screen' 이라 출력은 /tmp/nav2.log 로만 갔음) → 노드별 rcl 로그 파일(~/.ros/log/<노드>_<pid>_<ms>.log)을 합쳐 본다
echo "== 노드별 로그 파일(11-10 17:40 ~ 11-11 10:00 수정)"
FILES=$(find . -maxdepth 1 -type f -name '*.log' -newermt '2026-11-10 17:40' ! -newermt '2026-11-11 10:00' | sort)
for f in $FILES; do echo "  $f $(stat -c %s $f) B $(date -d @$(stat -c %Y $f) +%H:%M:%S)"; done | head -40
N=/tmp/roslog_merged_f2dm2.txt; cat $FILES > $N 2>/dev/null
echo "== 합친 줄 수 $(wc -l < $N)"
python3 - "$N" <<'EOF'
import re, sys, datetime
t0 = datetime.datetime(2026,11,10,17,55,0).timestamp()
pat = re.compile(r'Begin navigating|Goal succeeded|Goal failed|Goal canceled|Reached the goal|Failed to make progress|failed to generate|Running |nav_guard\]|STUCK|ABORT|abort|Collision|collision|Aborting handle|Received a goal|preempt|cancel', re.I)
last = None
for line in open(sys.argv[1], errors='replace'):
    m = re.search(r'\[(\d{10}\.\d+)\]', line)
    if not m: continue
    t = float(m.group(1)); last = (t, line)
    if t < t0: continue
    if pat.search(line) and 'tick rate' not in line:
        print(datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S'), line.strip()[:200])
if last: print('== 마지막 줄', datetime.datetime.fromtimestamp(last[0]).strftime('%m-%d %H:%M:%S'), last[1].strip()[:160])
EOF
