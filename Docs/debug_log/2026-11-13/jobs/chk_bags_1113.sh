#!/bin/bash
# chk_bags_1113 — 11-13 §10: Jetson 의 오늘 bag 위치 · 크기 · 토픽별 크기 비중(읽기만, 로버 안 움직임 · 지우지 않음). 인자 없음.
echo "== 디스크"; df -h / | tail -1
echo "== 오늘 bag"; du -sh /tmp/bag_f2rd1 /tmp/bag_f2rd2 /tmp/bag_rab_A /tmp/bag_rab_B /tmp/bag_rab_A2 /home/jetson/bags/bag_f2rd1 /home/jetson/bags/bag_f2rd2 2>/dev/null
echo "== 홈 bags 전체"; du -sh /home/jetson/bags 2>/dev/null; ls /home/jetson/bags | head -30
echo "== f2rd1 토픽별 바이트(상위 6)"
python3 - /home/jetson/bags/bag_f2rd1 <<'PY'
import sqlite3, glob, sys
db = sqlite3.connect(glob.glob(sys.argv[1] + '/*.db3')[0])
for n, c, b in db.execute('select t.name, count(*), sum(length(m.data)) from messages m join topics t on t.id=m.topic_id group by t.name order by 3 desc limit 6'):
    print(f'  {n:40s} {c:7d} 개 {b/1e6:8.1f} MB')
PY
