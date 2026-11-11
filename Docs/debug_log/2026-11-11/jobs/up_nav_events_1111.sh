#!/bin/bash
# up_nav_events_1111 — 11-11 §6: /tmp/nav2.log 를 영상 도구(Docs/tools/fig_drive_video.py)의 사건 파일 형식 'HH:MM:SS.cc 노드 메시지' 로 바꿔 표준 출력으로 보냄(Jetson → PC, 읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: 사용자 "탈출동작 부분 경로 생성 및 확정하는 거, 시각화해줘" — f2rr1 복귀 출발 상자 앞(15:00:21) 막힘 → 탈출 → 재계획 장면을 시간줄에 표시.
#   인자: $1 시작 HH:MM:SS · $2 끝 HH:MM:SS(11-11 KST). 'tick rate' · Message Filter 줄 뺌. 출력: 표준 출력(PC 에서 outputs/nav_events_<이름>.txt 로).
S=${1:-14:53:00}; E=${2:-15:01:30}
python3 - "$S" "$E" <<'PYEOF'
import re, sys, datetime
d = datetime.date(2026, 11, 11)
t0 = datetime.datetime.combine(d, datetime.time.fromisoformat(sys.argv[1])).timestamp()
t1 = datetime.datetime.combine(d, datetime.time.fromisoformat(sys.argv[2])).timestamp()
for line in open('/tmp/nav2.log', errors='replace'):
    m = re.search(r'\[(\d{10}\.\d+)\] \[([^\]]+)\]: (.*)', line)
    if not m or 'tick rate' in line or 'Message Filter' in line: continue
    t = float(m.group(1))
    if t0 <= t <= t1:
        print(datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S.%f')[:11], m.group(2), m.group(3)[:200])
PYEOF
