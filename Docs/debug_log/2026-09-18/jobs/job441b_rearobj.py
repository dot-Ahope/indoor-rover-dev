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
print('  t     | 로버 odom x   y   yaw | 뒤 창 점 수 | 점 map x 범위 / y 범위 | 로버 뒷면(map)과 점 최소 거리')
last = -9
for t, sc in scans:
    if t - last < 0.5:
        continue
    last = t
    i = min(max(bisect.bisect_left(obt, t), 0), len(ob) - 1); _, ox, oy, oth = ob[i]
    j = min(max(bisect.bisect_left(mot, t), 0), len(mo) - 1); _, ax, ay, ath = mo[j]
    bx0, by0, bth = ax + ox * math.cos(ath) - oy * math.sin(ath), ay + ox * math.sin(ath) + oy * math.cos(ath), ath + oth
    rr = np.asarray(sc.ranges, dtype=np.float64); aa = sc.angle_min + np.arange(rr.size) * sc.angle_increment
    ok = np.isfinite(rr) & (rr > sc.range_min) & (rr < 3.0)
    lx = LX + rr[ok] * np.cos(aa[ok] + LYAW); ly = rr[ok] * np.sin(aa[ok] + LYAW)
    mx = bx0 + lx * math.cos(bth) - ly * math.sin(bth); my = by0 + lx * math.sin(bth) + ly * math.cos(bth)
    w = (mx > -0.45) & (mx < -0.15) & (my > -0.20) & (my < 0.50)
    rear = (bx0 - 0.25 * math.cos(bth), by0 - 0.25 * math.sin(bth))
    dmin = float(np.min(np.hypot(mx[w] - rear[0], my[w] - rear[1]))) if w.any() else float('nan')
    print('  %5.2f | %.3f %+.3f %+5.1f° | %4d | %s | %.3f' % (t, ox, oy, math.degrees(oth), w.sum(),
          ('x %+.2f~%+.2f / y %+.2f~%+.2f' % (mx[w].min(), mx[w].max(), my[w].min(), my[w].max())) if w.any() else '-' * 28, dmin))
