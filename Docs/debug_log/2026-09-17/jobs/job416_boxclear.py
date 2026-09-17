#!/usr/bin/env python3
"""주행 스크립트 '실여유 0' 검증 (2026-09-17 mp12): bag 의 로컬 코스트맵 LETHAL 셀 ↔ 차체 외곽 사각형 거리. 로버는 움직이지 않는다.
   - 로컬 코스트맵(odom 프레임) 매 메시지: odom→base_link 자세(가장 가까운 /tf)로 LETHAL(=100) 셀 중심을 차체 좌표로 → 외곽(반길이 0.25, 반폭 0.165) 거리 − 반셀(0.025)
   - 상자 영역(odom x 0.9~1.6, y −0.3~+0.2) 셀만 따로 → 상자 LETHAL 범위(x/y)와 차체 오른쪽 변까지 거리
   - 비교: 주행 스크립트 상자 모델(게이트 검출 1.173/−0.052, 폭 0.18·깊이 0.11)
   인자: BAG GOAL_EPOCH
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid
HL, HW, HC = 0.25, 0.165, 0.025
BAG, G = sys.argv[1], float(sys.argv[2])


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
ob, cms = [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9 - G
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/local_costmap/costmap' and -2 < t < 40:
        cms.append((t, deserialize_message(data, OccupancyGrid)))
ob.sort(); obt = [o[0] for o in ob]
print('odom->base %d, 로컬 코스트맵 %d (t −2~40)' % (len(ob), len(cms)))
print('   t   | 로버 odom x     y    yaw  | 상자영역 LETHAL 셀 x범위        y범위        셀수 | 차체↔상자 LETHAL | 차체↔전체 LETHAL (위치)')
res = []
for t, m in cms:
    st = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9 - G
    k = bisect.bisect_left(obt, st); k = min(max(k, 0), len(ob) - 1)
    if k > 0 and abs(obt[k - 1] - st) < abs(obt[k] - st): k -= 1
    _, px, py, pth = ob[k]
    d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width); jj, ii = np.where(d >= 100)
    X = m.info.origin.position.x + (ii + 0.5) * m.info.resolution; Y = m.info.origin.position.y + (jj + 0.5) * m.info.resolution
    c, s = math.cos(-pth), math.sin(-pth); dx, dy = X - px, Y - py
    rx, ry = dx * c - dy * s, dx * s + dy * c
    dist = np.hypot(np.maximum(np.abs(rx) - HL, 0), np.maximum(np.abs(ry) - HW, 0)) - HC
    boxsel = (X > 0.9) & (X < 1.6) & (Y > -0.3) & (Y < 0.2)
    db = float(dist[boxsel].min()) if boxsel.any() else float('nan')
    da = float(dist.min()) if dist.size else float('nan'); ka = int(np.argmin(dist)) if dist.size else 0
    res.append((st, db))
    if 12 <= st <= 30:
        print(' %5.1f | %6.3f %+6.3f %+5.1f° | %s | %+.3f | %+.3f (%.2f,%+.2f)' % (st, px, py, math.degrees(pth),
              ('x %.3f~%.3f y %+.3f~%+.3f %3d' % (X[boxsel].min(), X[boxsel].max(), Y[boxsel].min(), Y[boxsel].max(), boxsel.sum())) if boxsel.any() else '없음' + ' ' * 36,
              db, da, X[ka] if dist.size else 0, Y[ka] if dist.size else 0))
v = [(t, d) for t, d in res if not math.isnan(d)]
tm, dm = min(v, key=lambda z: z[1])
print('상자 LETHAL ↔ 차체 최소: %.3f m @ t=%.1f (셀 중심 거리 − 반셀 0.025, 셀 양자화 ±2.5 cm)' % (dm, tm))
print('주행 스크립트 상자 모델(게이트 1.173/−0.052, 폭 0.18): y %+.3f~%+.3f, x %.3f~%.3f' % (-0.052 - 0.09, -0.052 + 0.09, 1.173, 1.173 + 0.11))
