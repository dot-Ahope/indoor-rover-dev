#!/usr/bin/env python3
"""근거리 아티팩트 재확인 (2026-09-21 §5, 09-14 job311/312 의 '0.36~0.38 m 에 17 % 프레임' 근거를 데크 보정 뒤 다시 본다). 인자: [SEC=30] [DEC]
  앞 0.45 m 안에 물체가 없는 상태에서 원시 점군의 카메라 거리 0.25~0.45 m 껍질 안, base z 0.03~0.30, |y|<0.5, x<0.70 인 점을 프레임별로 센다.
  이 값이 릴레이 min_range 를 얼마까지 내릴 수 있는지의 근거(아티팩트가 남는 거리 아래로는 못 내림).
"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
import tf2_ros
SEC = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
CAM = np.array([0.234, 0.044, 0.143])


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


rclpy.init(); n = Node('artifact460'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
FR = []; TFC = {}; SEEN = [0]


def cb(m):
    SEEN[0] += 1
    if SEEN[0] % 2: return
    fid = m.header.frame_id
    if fid not in TFC:
        try:
            t = buf.lookup_transform('base_link', fid, rclpy.time.Time()).transform
            TFC[fid] = (Rq(t.rotation), np.array([t.translation.x, t.translation.y, t.translation.z]))
        except Exception:
            return
    R, T = TFC[fid]
    off = {f.name: f.offset for f in m.fields}
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
    xyz = np.stack([raw[:, off[k]:off[k] + 4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)] @ R.T + T
    r = np.linalg.norm(xyz - CAM, axis=1)
    s = (r > 0.25) & (r < 0.45) & (xyz[:, 2] > 0.03) & (xyz[:, 2] < 0.30) & (np.abs(xyz[:, 1]) < 0.5) & (xyz[:, 0] < 0.70)
    FR.append((int(s.sum()), r[s].copy(), xyz[s].copy()))


n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', cb, qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < SEC + 2.0:
    rclpy.spin_once(n, timeout_sec=0.05)
rclpy.shutdown()
cnt = np.array([f[0] for f in FR])
print('아티팩트 껍질(카메라 0.25~0.45 m, z 0.03~0.30): 프레임 %d, 점 있는 프레임 %d (%.0f%%), ≥3 점 %d (%.0f%%), 프레임당 중앙 %.0f 최대 %d' % (
    len(cnt), (cnt > 0).sum(), 100 * (cnt > 0).mean() if len(cnt) else 0, (cnt >= 3).sum(), 100 * (cnt >= 3).mean() if len(cnt) else 0, np.median(cnt) if len(cnt) else 0, cnt.max() if len(cnt) else 0))
allr = np.concatenate([f[1] for f in FR]) if FR else np.array([])
if allr.size:
    h, e = np.histogram(allr, bins=np.arange(0.25, 0.451, 0.02))
    print('  거리 분포(2 cm 칸, 점 수): ' + ' '.join('%.2f:%d' % (e[i], h[i]) for i in range(len(h))))
    P = np.concatenate([f[2] for f in FR]); print('  점 위치 중앙 base (x %.2f y %+.2f z %.2f), z 범위 %.2f~%.2f' % (np.median(P[:, 0]), np.median(P[:, 1]), np.median(P[:, 2]), P[:, 2].min(), P[:, 2].max()))
