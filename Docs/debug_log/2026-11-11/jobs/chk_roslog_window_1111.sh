#!/bin/bash
# chk_roslog_window_1111 — 11-11: ~/.ros/log 노드별 로그(11-10 17:51 이후 기동분)에서 지정 시각 창의 줄을 시간순으로 모두(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: f2dm2 목표 2 에서 컨트롤러 취소 2 회(17:56:32 · 17:57:07) · Smac 실패 · 스무더 충돌 · monotone_escape — 앞뒤 BT · nav_guard · stuck 줄로 원인 순서를 본다.
#   인자: $1 시작 HH:MM:SS · $2 끝 HH:MM:SS(11-10 기준, 기본 17:56:20 ~ 17:58:05). 'tick rate' · Message Filter 줄은 뺌. 출력: 표준 출력('시각 [노드] 내용').
S=${1:-17:56:20}; E=${2:-17:58:05}
cd ~/.ros/log || exit 1
find . -maxdepth 1 -type f -name '*.log' -newermt '2026-11-10 17:51' ! -newermt '2026-11-11 10:00' -size +0 | python3 -c "
import sys, re, datetime
d = datetime.date(2026,11,10)
t0 = datetime.datetime.combine(d, datetime.time.fromisoformat('$S')).timestamp(); t1 = datetime.datetime.combine(d, datetime.time.fromisoformat('$E')).timestamp()
rows = []
for f in sys.stdin.read().split():
    for line in open(f, errors='replace'):
        m = re.search(r'\[(\d{10}\.\d+)\]', line)
        if not m: continue
        t = float(m.group(1))
        if t0 <= t <= t1 and 'tick rate' not in line and 'Message Filter' not in line:
            rows.append((t, line.strip()))
for t, l in sorted(rows):
    print(datetime.datetime.fromtimestamp(t).strftime('%H:%M:%S.%f')[:12], l[:230])
print('== 줄 수', len(rows))
"
