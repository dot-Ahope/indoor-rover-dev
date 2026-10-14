#!/usr/bin/env python3
"""anal_blob_src — 지도 좌표의 한 작은 구역에 로컬 코스트맵 치명 칸이 언제부터 있었고, 라이다 점이 그 구역에 있었는지 시간순으로. (2026-10-14 §22, 오늘만)
  왜: f2u2 사건 때 상자 앞(x 1.0~1.2, y −0.25~0.15)에 A 에는 없던 치명 칸 덩어리가 있었다 → 라이다로 보이는 실제 물체인지, 카메라(nvblox) 기억이 밀린 것인지.
  출력: 2 s 마다 — 구역 안 치명 칸 수(로컬, 지도 좌표로 옮김), 같은 구역 라이다 점 수(지도 좌표), 로버 지도 위치, map→odom yaw.
  인자: bag 시작HH:MM:SS 끝HH:MM:SS [x0 x1 y0 y1 = 1.0 1.2 -0.25 0.15]"""
import sys, time, math
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
bag, h0, h1 = sys.argv[1:4]; X0, X1, Y0, Y1 = [float(v) for v in sys.argv[4:8]] if len(sys.argv) > 7 else (1.0, 1.2, -0.25, 0.15)
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo = (0, 0, 0); ob = (0, 0, 0); lidar_tf = None; last = -1; lc_n = 0; sc_n = 0
inb = lambda x, y: (x > X0) & (x < X1) & (y > Y0) & (y < Y1)
def tomap(x, y, T): c, s = math.cos(T[2]), math.sin(T[2]); return T[0] + c * x - s * y, T[1] + s * x + c * y
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/local_costmap/costmap', '/scan')]):
        ts = t / 1e9; h = time.strftime('%H:%M:%S', time.localtime(ts)); m = rd.deserialize(raw, c.msgtype)
        if c.topic in ('/tf', '/tf_static'):
            for tr in m.transforms:
                v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
                if tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': mo = v
                elif tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': ob = v
                elif tr.child_frame_id == 'lidar_link':   # 라이다는 뒤집혀 달림(roll 180°) → yaw 만 쓰면 점이 거울상이 됨 — 쿼터니언 전체 회전으로
                    q = tr.transform.rotation; Rq = np.array([[1-2*(q.y*q.y+q.z*q.z), 2*(q.x*q.y-q.z*q.w), 2*(q.x*q.z+q.y*q.w)], [2*(q.x*q.y+q.z*q.w), 1-2*(q.x*q.x+q.z*q.z), 2*(q.y*q.z-q.x*q.w)]]); lidar_tf = (v[0], v[1], Rq)
            continue
        if h < h0 or h > h1: continue
        if c.topic == '/local_costmap/costmap':
            a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
            x, y = tomap(m.info.origin.position.x + (ix + 0.5) * m.info.resolution, m.info.origin.position.y + (iy + 0.5) * m.info.resolution, mo); lc_n = int(inb(x, y).sum())
        elif lidar_tf is not None:
            r = np.array(m.ranges); an = m.angle_min + np.arange(len(r)) * m.angle_increment; ok = np.isfinite(r) & (r > m.range_min) & (r < m.range_max)
            px_, py_ = r * np.cos(an), r * np.sin(an); Rq = lidar_tf[2]; lx = lidar_tf[0] + Rq[0, 0] * px_ + Rq[0, 1] * py_; ly = lidar_tf[1] + Rq[1, 0] * px_ + Rq[1, 1] * py_
            bx, by = tomap(lx[ok], ly[ok], ob); x, y = tomap(bx, by, mo); sc_n = max(sc_n, int(inb(x, y).sum()))
        if ts - last >= 2:
            px, py = tomap(ob[0], ob[1], mo); print('%s  치명 칸 %3d · 라이다 점(2 s 최대) %3d · 로버 지도 (%.2f, %.2f) · map→odom yaw %+.2f°' % (h, lc_n, sc_n, px, py, math.degrees(mo[2]))); last = ts; sc_n = 0
