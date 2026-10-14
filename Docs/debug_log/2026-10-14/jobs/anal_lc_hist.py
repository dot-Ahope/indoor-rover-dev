#!/usr/bin/env python3
"""anal_lc_hist — 로컬 코스트맵(/local_costmap/costmap) 값 분포를 구간별로 견준다. (2026-10-14 §21, 오늘만)
  왜: 정지 중 패딩 토글(B) 뒤 멈칫이 재현됐는데 파라미터 스냅샷은 A 와 같다 → 코스트맵 내부(팽창 표 등)가 달라졌는지 값 분포로 본다.
  출력: 구간마다 칸 비율 — 0 · 1~49 · 50~89 · 90~98 · 99(내접) · 100(치명) · 미지(−1), 그리고 0 이 아닌 값 중 가장 작은 값 상위 5 개(팽창 꼬리 모양).
  인자: 이름=bag@HH:MM:SS~HH:MM:SS ..."""
import sys, time
from pathlib import Path
from collections import Counter
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
for a in sys.argv[1:]:
    nm, rest = a.split('='); bag, rng = rest.split('@'); h0, h1 = rng.split('~'); H = Counter(); n = 0
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/local_costmap/costmap']):
            h = time.strftime('%H:%M:%S', time.localtime(t / 1e9))
            if not (h0 <= h <= h1): continue
            H.update(np.array(rd.deserialize(raw, c.msgtype).data, np.int16).tolist()); n += 1
    tot = sum(H.values()); b = lambda lo, hi: 100 * sum(v for k, v in H.items() if lo <= k <= hi) / tot
    small = sorted(k for k in H if 0 < k < 99)[:5]
    print('%-6s %3d 장 | 0 %5.1f%% · 1~49 %5.1f · 50~89 %5.1f · 90~98 %5.1f · 99 %5.1f · 100 %5.1f · 미지 %4.1f | 가장 작은 값 %s · 서로 다른 값 %d 개'
          % (nm, n, b(0, 0), b(1, 49), b(50, 89), b(90, 98), b(99, 99), b(100, 100), b(-1, -1), small, len(H)))
