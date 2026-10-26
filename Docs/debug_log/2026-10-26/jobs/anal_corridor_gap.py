#!/usr/bin/env python3
"""anal_corridor_gap — 서쪽 통로 단면(y −4.4 ~ −5.0, 0.1 m 간격)에서 전역 코스트맵 치명 칸 사이 틈 폭 · 내접(99) 아닌 칸 폭, 주행별 비교 (2026-10-26 §16, PC).
  왜: f2sa3 통로 여유가 10-23 f2rp4 보다 나빴는데, 그날그날 물건 배치(실제 촬영: 빨간 쇼핑백 · 열린 상자 날개)가 다를 수 있음.
  기준 시각: 로버가 통로 남행(목표 4)에 들어가기 직전의 전역 코스트맵. 인자: 이름=bag=HH:MM:SS ..."""
import sys, time, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
for arg in sys.argv[1:]:
    name, bag, hh = arg.split('=')
    GR = []
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/global_costmap/costmap']):
            m = rd.deserialize(raw, c.msgtype); GR.append((t * 1e-9, m.info.origin.position.x, m.info.origin.position.y, m.info.resolution, np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width)))
    d0 = time.strftime('%Y-%m-%d ', time.localtime(GR[0][0])); te = time.mktime(time.strptime(d0 + hh, '%Y-%m-%d %H:%M:%S'))
    g = GR[max(bisect.bisect_right([q[0] for q in GR], te) - 1, 0)]; _, ox, oy, r, G = g
    print('== %s (지도 %s)' % (name, time.strftime('%H:%M:%S', time.localtime(g[0]))))
    for y in np.arange(-4.4, -5.05, -0.1):
        i = int((y - oy) / r); xs = np.arange(-2.4, -0.9, r); js = ((xs - ox) / r).astype(int); row = G[i, js]
        # 통로 가운데(x −1.65) 에서 좌우로 처음 치명 · 처음 내접 칸까지
        c = int(np.argmin(np.abs(xs + 1.65)))
        def edge(th, step):
            k = c
            while 0 <= k < len(row) and row[k] < th: k += step
            return xs[k] if 0 <= k < len(row) else float('nan')
        L, Rr = edge(100, -1), edge(100, +1); L9, R9 = edge(99, -1), edge(99, +1)
        print('  y %.1f: 치명 사이 %.2f m (x %.2f ~ %.2f) · 99 미만 폭 %.2f m · 가운데 칸 값 %d' % (y, Rr - L - r, L, Rr, R9 - L9 - r, row[c]))
