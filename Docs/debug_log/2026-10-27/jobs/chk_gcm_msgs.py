#!/usr/bin/env python3
"""chk_gcm_msgs — 전역 코스트맵 메시지를 하나씩: 연결(발행자) 수 · 수신 시각 · header stamp · 원점 · 크기 · 직전 메시지와 다른 칸 수 ·
  문 · 상자 영역 치명 칸 수 (2026-10-27 §15, PC). 사용자: 상자 멈춤 영상 20 s · 31 s 에 문이 막혔다 풀리고 상자가 벽 쪽으로 갔다 돌아옴 → 코스트맵이 2 개였나?
  인자: bag폴더 시작HH:MM:SS 끝HH:MM:SS [토픽=/global_costmap/costmap]"""
import sys, time
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag = Path(sys.argv[1]); TOP = sys.argv[4] if len(sys.argv) > 4 else '/global_costmap/costmap'
t0 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[2], '%Y-%m-%d %H:%M:%S')); t1 = time.mktime(time.strptime('2026-10-27 ' + sys.argv[3], '%Y-%m-%d %H:%M:%S'))
BOXR = (1.0, 1.4, -0.3, 0.1)
hs = lambda t: time.strftime('%H:%M:%S', time.localtime(t)) + '.%02d' % int((t % 1) * 100)
with AnyReader([bag], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    cons = [c for c in rd.connections if c.topic == TOP]
    print('연결 %d 개:' % len(cons), [(c.id, c.msgtype, getattr(c.ext, 'offered_qos_profiles', '')[:80] if hasattr(c, 'ext') else '') for c in cons])
    prev = None
    for c, t, raw in rd.messages(connections=cons):
        ts = t * 1e-9
        if ts < t0 or ts > t1: continue
        m = rd.deserialize(raw, c.msgtype); i = m.info; g = np.array(m.data, np.int8).reshape(i.height, i.width)
        st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        ox, oy, r = i.origin.position.x, i.origin.position.y, i.resolution
        def cnt(x0, x1, y0, y1):
            a, b = int((x0 - ox) / r), int((x1 - ox) / r); c_, d = int((y0 - oy) / r), int((y1 - oy) / r)
            return int((g[c_:d, a:b] == 100).sum())
        nb = cnt(*BOXR); nl = int((g == 100).sum())
        dif = int((g != prev).sum()) if prev is not None and prev.shape == g.shape else -1
        print('%s 연결 %d stamp %s(수신-stamp %+.2f s) 원점 (%.2f, %.2f) %dx%d 치명 전체 %d · 상자 영역 %d · 직전과 다른 칸 %d' % (
            hs(ts), c.id, hs(st), ts - st, ox, oy, i.width, i.height, nl, nb, dif))
        prev = g
