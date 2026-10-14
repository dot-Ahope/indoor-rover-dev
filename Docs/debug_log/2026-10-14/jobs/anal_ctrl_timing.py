#!/usr/bin/env python3
"""anal_ctrl_timing — 패딩 토글 뒤 컨트롤러가 '느려졌는지·흔들리는 입력을 받았는지'를 bag · top 기록으로 견준다. (2026-10-14 §23, 오늘만)
  왜: §21 에서 토글 뒤 좌우 틀기가 늘었는데 파라미터·코스트맵 값 분포는 같았다. 계산 시간(주기·CPU)이나 입력(경로·코스트맵 갱신)이 달라졌는지 본다.
  출력(구간별): /cmd_vel 간격 중앙값·95%·최대(ms)와 100 ms 넘는 비율, /trajectories(제어 주기마다 1 번) 간격, 로컬 코스트맵 발행 간격,
               /transformed_global_plan 길이 변화, top 의 controller_server CPU 중앙값.
  인자: 이름=bag@HH:MM:SS~HH:MM:SS@top로그 ..."""
import sys, time, re
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
def gaps(ts): d = np.diff(np.array(ts)) * 1000; return d
print('구간      cmd_vel 간격 ms(중앙/95%/최대, >100ms %)   궤적 간격 ms(중앙/95%)   로컬지도 간격 s(중앙)   경로 점수 변화(중앙)   controller CPU % (중앙/90%)')
for a in sys.argv[1:]:
    nm, bag, rng, top = a.split('@'); h0, h1 = rng.split('~'); T = {'/cmd_vel': [], '/trajectories': [], '/local_costmap/costmap': []}; npts = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in list(T) + ['/transformed_global_plan']]):
            h = time.strftime('%H:%M:%S', time.localtime(t / 1e9))
            if not (h0 <= h <= h1): continue
            if c.topic == '/transformed_global_plan': npts.append(len(rd.deserialize(raw, c.msgtype).poses))
            else: T[c.topic].append(t / 1e9)
    cv = gaps(T['/cmd_vel']); tr = gaps(T['/trajectories']); lc = gaps(T['/local_costmap/costmap']) / 1000
    cpu = []; cur = None
    for line in open(top, encoding='utf-8', errors='ignore'):
        m = re.match(r'top - (\d\d:\d\d:\d\d)', line)
        if m: cur = m.group(1); continue
        if cur and h0 <= cur <= h1 and 'controll' in line:
            try: cpu.append(float(line.split()[8]))
            except Exception: pass
    print('%-8s %5.0f / %5.0f / %5.0f, %4.1f%%                      %5.0f / %5.0f              %5.2f                  %4.1f                 %5.1f / %5.1f  (%d 표본)'
          % (nm, np.median(cv), np.percentile(cv, 95), cv.max(), 100 * (cv > 100).mean(), np.median(tr), np.percentile(tr, 95), np.median(lc),
             np.median(np.abs(np.diff(npts))) if len(npts) > 1 else float('nan'), np.median(cpu) if cpu else float('nan'), np.percentile(cpu, 90) if cpu else float('nan'), len(cpu)))
