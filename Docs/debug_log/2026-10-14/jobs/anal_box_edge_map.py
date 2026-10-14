#!/usr/bin/env python3
"""anal_box_edge_map — 출발점 근처 상자(복귀 길 상자 끝, 10-13 §12)의 북쪽 가장자리를 지도 좌표로: 로컬 코스트맵(odom)과 전역 코스트맵(map) 각각. (2026-10-14 §22, 오늘만)
  왜: f2u2(B)가 같은 자리에서 A 보다 상자에 2 cm 더 붙어 '후보 전부 충돌'이 났다. 로버 자세는 A 보다 3 cm 바깥 → 상자가 코스트맵에서 밀려 찍혔는지 본다.
  방법: 지정 시각 직전의 로컬 코스트맵 치명 칸(100)을 그 시각 map→odom 으로 지도 좌표로 옮겨, 상자 구역(x 0.9~1.7, y −0.6~0.25) 안 칸들의 x 별 가장 큰 y(북쪽 가장자리)를 낸다.
        전역 코스트맵(map)도 같은 방법. map→odom 의 x · y · yaw 도 함께(odom 드리프트 크기).
  인자: 이름=bag@HH:MM:SS ..."""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
XS = np.arange(0.95, 1.70, 0.1)
def edge(wx, wy):
    k = (wx > 0.9) & (wx < 1.75) & (wy > -0.6) & (wy < 0.25); out = []
    for x0 in XS:
        m = k & (np.abs(wx - x0) < 0.05); out.append('%+.2f' % wy[m].max() if m.any() else '  -  ')
    return ' '.join(out)
print('x 열:', ' '.join('%.2f' % x for x in XS))
for a in sys.argv[1:]:
    nm, rest = a.split('='); bag, hh = rest.split('@'); mo = []; lc = None; gc = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        day = None
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/local_costmap/costmap', '/global_costmap/costmap')]):
            ts = t / 1e9
            if day is None: day = time.strftime('%Y-%m-%d ', time.localtime(ts)); T = time.mktime(time.strptime(day + hh, '%Y-%m-%d %H:%M:%S'))
            if ts > T: break
            m = rd.deserialize(raw, c.msgtype)
            if c.topic == '/tf':
                for tr in m.transforms:
                    if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            elif c.topic == '/local_costmap/costmap': lc = m
            else: gc = m
    def cells(g):
        a = np.array(g.data, np.int16).reshape(g.info.height, g.info.width); iy, ix = np.nonzero(a >= 100)
        return g.info.origin.position.x + (ix + 0.5) * g.info.resolution, g.info.origin.position.y + (iy + 0.5) * g.info.resolution
    ox, oy = cells(lc); c, s = math.cos(mo[2]), math.sin(mo[2]); mx = mo[0] + c * ox - s * oy; my = mo[1] + s * ox + c * oy
    gx, gy = cells(gc)
    print('%-8s map→odom (%+.3f, %+.3f, %+.2f°)' % (nm, mo[0], mo[1], math.degrees(mo[2])))
    print('   로컬→지도 북쪽 가장자리 y:', edge(mx, my))
    print('   전역       북쪽 가장자리 y:', edge(gx, gy))
