#!/usr/bin/env python3
"""anal_passage_gap — 서쪽 통로(map x ≈ −1.7)를 남북으로 지날 때, y 띠(5 cm)마다 로컬 코스트맵 치명 칸의 왼쪽(서) · 오른쪽(동) 경계와 그 사이 폭. (2026-10-15 §3, 오늘만)
  왜: f2v1 이 (−1.70, −4.12)에서 '후보 전부 충돌'로 Nav2 중단. 어제 f2t1 은 같은 자리를 지났다 → 통로 폭이 코스트맵에서 달랐는지.
  방법: 지정 시각 직전 로컬 코스트맵(odom)의 치명 칸(100)을 그 시각 map→odom 으로 지도 좌표로 옮겨, 통로 중심 x0 기준 서쪽 칸 중 가장 동쪽 · 동쪽 칸 중 가장 서쪽을 띠마다.
        차체 폭(패딩 포함) 0.35 m 를 빼면 차체 중심이 설 수 있는 x 범위 폭(= 여유 합).
  인자: x0 y0 y1 이름=bag@HH:MM:SS.f ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
X0, Y0, Y1 = [float(v) for v in sys.argv[1:4]]; W = 0.35
rows = {}
names = []
for a in sys.argv[4:]:
    nm, rest = a.split('='); bag, hh = rest.split('@'); hms, _, fr = hh.partition('.'); mo = None; lc = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        T = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap')]):
            ts = t / 1e9
            if T is None: T = time.mktime(time.strptime(time.strftime('%Y-%m-%d ', time.localtime(ts)) + hms, '%Y-%m-%d %H:%M:%S')) + (float('0.' + fr) if fr else 0)
            if ts > T: break
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            else: lc = m
    a_ = np.array(lc.data, np.int16).reshape(lc.info.height, lc.info.width); iy, ix = np.nonzero(a_ >= 100)
    ox_ = lc.info.origin.position.x + (ix + 0.5) * lc.info.resolution; oy_ = lc.info.origin.position.y + (iy + 0.5) * lc.info.resolution
    c_, s_ = math.cos(mo[2]), math.sin(mo[2]); mx = mo[0] + c_ * ox_ - s_ * oy_; my = mo[1] + s_ * ox_ + c_ * oy_
    names.append(nm)
    for y in np.arange(Y0, Y1, -0.05):
        k = np.abs(my - y) < 0.025; L = mx[k & (mx < X0)]; R = mx[k & (mx > X0)]
        l = L.max() if len(L) else float('nan'); r = R.min() if len(R) else float('nan')
        rows.setdefault(round(y, 2), []).append((l, r, r - l - W))
print('y 띠   ' + '   '.join('%-30s' % ('%s: 서 경계 · 동 경계 · 여유 합(cm)' % n) for n in names))
for y in sorted(rows, reverse=True):
    print('%+.2f  ' % y + '   '.join('%+.2f · %+.2f · %5.1f              ' % (l, r, 100 * g) for l, r, g in rows[y]))
