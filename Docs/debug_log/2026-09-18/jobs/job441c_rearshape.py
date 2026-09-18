#!/usr/bin/env python3
"""dy3 출발 때 로버 뒤 물체 추적 (2026-09-18). 인자: BAG GOAL_EPOCH
  map 프레임(= map->odom ∘ odom->base_link ∘ 보정 라이다 TF)에서 출발 자세 뒤쪽 창(map x −0.45~−0.15, y −0.20~+0.50)의 점 수를
  0.5 s 간격으로 — 고정 물체면 로버가 떠나도 같은 map 자리에 계속 보이고(가려지지 않는 한), 사람이면 움직이거나 사라진다.
  로버 odom 전진량도 같이.
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from sensor_msgs.msg import LaserScan
LYAW, LX = math.pi - 0.04677, 0.152


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


bag, G = sys.argv[1], float(sys.argv[2])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
ob, mo, scans = [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9 - G
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9 - G
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((st, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/scan' and -2 < t < 12:
        scans.append((t, deserialize_message(data, LaserScan)))
ob.sort(); mo.sort(); obt = [o[0] for o in ob]; mot = [m[0] for m in mo]
# 모양: t −2~0 s 스캔을 모아 창 안 점의 y(2 cm 칸) 분포와 칸별 x 최소 — 두 덩어리면 다리 두 개 의심
Y, X = [], []
for t, sc in scans:
    if not (-2 < t < 0):
        continue
    rr = np.asarray(sc.ranges, dtype=np.float64); aa = sc.angle_min + np.arange(rr.size) * sc.angle_increment
    ok = np.isfinite(rr) & (rr > sc.range_min) & (rr < 3.0)
    lx = LX + rr[ok] * np.cos(aa[ok] + LYAW); ly = rr[ok] * np.sin(aa[ok] + LYAW)
    w = (lx > -0.45) & (lx < -0.15) & (ly > -0.20) & (ly < 0.55)
    Y += list(ly[w]); X += list(lx[w])
Y, X = np.array(Y), np.array(X)
print('  출발 전 2 s 창 안 점 %d 개. y 2 cm 칸별 점 수 / 그 칸의 가장 가까운 x(뒷면 −0.25 기준 간격):' % len(Y))
for lo in np.arange(-0.20, 0.55, 0.02):
    s_ = (Y >= lo) & (Y < lo + 0.02)
    print('   y %+.2f | %4d %s | %s' % (lo, s_.sum(), '#' * min(60, s_.sum() // 5), ('x %+.3f (간격 %.3f)' % (X[s_].max(), -0.25 - X[s_].max())) if s_.any() else ''))
