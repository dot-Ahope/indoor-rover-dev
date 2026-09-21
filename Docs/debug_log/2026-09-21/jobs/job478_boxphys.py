#!/usr/bin/env python3
"""물리 상자 위치(카메라 원시 점군, Nav2 불필요) — job125 detect_box 와 같은 규칙 (2026-09-21 N0 용). 출력 마지막 줄: 'BX BY N'
  base_link 로 변환, z 0.05~0.30·x 0.5~1.5·|y|<0.5 → y 1D 군집(간격 0.08, ≥25 점) 중 z 중앙 <0.20 이고 진행축에 가장 가까운 것 → x 로 정렬해 0.10 m 넘는 틈에서 나눠 가장 큰 조각 → 전면 x = 5 % 분위, 중심 y = 중앙값. 10 프레임 중앙값.
"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
import tf2_ros
NFR = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def Rq(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


rclpy.init(); n = Node('boxphys478'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); R = []; TF = {}


def clusters_y(sel, gap=0.08, minpts=25):
    o = sel[np.argsort(sel[:, 1])]; out, cur = [], [o[0]]
    for q in o[1:]:
        if q[1] - cur[-1][1] > gap:
            out.append(np.array(cur)); cur = [q]
        else:
            cur.append(q)
    out.append(np.array(cur)); return [c for c in out if len(c) >= minpts]


def cb(m):
    if len(R) >= NFR: return
    fid = m.header.frame_id
    if fid not in TF:
        try:
            t = buf.lookup_transform('base_link', fid, rclpy.time.Time()).transform
            TF[fid] = (Rq(t.rotation), np.array([t.translation.x, t.translation.y, t.translation.z]))
        except Exception:
            return
    Rm, T = TF[fid]; off = {f.name: f.offset for f in m.fields}
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, m.point_step)
    P = np.stack([raw[:, off[k]:off[k] + 4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], axis=1)
    P = P[np.isfinite(P).all(axis=1)] @ Rm.T + T
    sel = P[(P[:, 2] > 0.05) & (P[:, 2] < 0.30) & (P[:, 0] > 0.5) & (P[:, 0] < 1.5) & (np.abs(P[:, 1]) < 0.5)]
    if len(sel) < 40: return
    low = [(abs(float(np.median(c[:, 1]))), c) for c in clusters_y(sel) if float(np.median(c[:, 2])) < 0.20]
    if not low: return
    low.sort(key=lambda t: t[0]); sel = low[0][1]
    o = sel[np.argsort(sel[:, 0])]; parts, cur = [], [o[0]]
    for q in o[1:]:
        if q[0] - cur[-1][0] > 0.10: parts.append(np.array(cur)); cur = [q]
        else: cur.append(q)
    parts.append(np.array(cur)); sel = max(parts, key=len)
    if len(sel) < 40: return
    R.append((float(np.percentile(sel[:, 0], 5)), float(np.median(sel[:, 1])), len(sel)))


n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', cb, qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 15 and len(R) < NFR:
    rclpy.spin_once(n, timeout_sec=0.05)
rclpy.shutdown()
if not R:
    print('상자 검출 실패'); print('nan nan 0'); sys.exit(1)
A = np.array(R); print('상자(카메라 점군, base_link): 전면 x %.3f (범위 %.3f~%.3f) 중심 y %+.3f (범위 %+.3f~%+.3f) 점 %.0f, %d 프레임' % (
    np.median(A[:, 0]), A[:, 0].min(), A[:, 0].max(), np.median(A[:, 1]), A[:, 1].min(), A[:, 1].max(), np.median(A[:, 2]), len(A)))
print('%.3f %.3f %d' % (np.median(A[:, 0]), np.median(A[:, 1]), len(A)))
