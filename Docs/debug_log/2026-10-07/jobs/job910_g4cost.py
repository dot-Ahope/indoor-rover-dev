#!/usr/bin/env python3
"""10-07 §2.3: f2c1 목표 4(남서) 정체 — 로컬 코스트맵이 차체를 가뒀나. 1 s 마다:
   차체(odom, EKF B) 외곽 안·주변 치명(≥253)·내접(≥99) 칸, 외곽 ↔ 가장 가까운 치명 칸 거리, 라이다 최근접, cmd_vel 요약, EKF A·B 차이.
   (정정) 코스트맵 메시지는 0~100 척도. 차체 외곽: x −0.248~+0.262, y ±0.165 (step_rot 과 같은 치수). 인자: BAG TA TB (epoch)"""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG, TA, TB = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
XB, XF, HW = -0.248, 0.262, 0.165; LX, LYAW = 0.152, math.pi - 0.04677
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
B, A, C, cm, sc = [], [], [], None, None; out = []; nxt = TA
def gap(px, py):   # 차체 좌표 점 → 외곽까지 거리(안이면 0)
    dx = np.where(px > XF, px - XF, np.where(px < XB, XB - px, 0)); dy = np.maximum(np.abs(py) - HW, 0); return np.hypot(dx, dy)
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if t > TB: break
    if t < TA - 3: continue
    if tp in ('/odometry/filtered', '/odometry/ekf_a'):
        m = deserialize_message(data, get_message(types[tp])); p = m.pose.pose
        (B if tp == '/odometry/filtered' else A).append((t, p.position.x, p.position.y, yaw(p.orientation)))
    elif tp == '/cmd_vel':
        m = deserialize_message(data, get_message(types[tp])); C.append((t, m.linear.x, m.angular.z))
    elif tp == '/local_costmap/costmap': cm = deserialize_message(data, get_message(types[tp]))
    elif tp == '/scan': sc = deserialize_message(data, get_message(types[tp]))
    if t >= nxt and cm is not None and B and sc is not None:
        nxt += 1.0; x, y, th = B[-1][1:]; c, s = math.cos(th), math.sin(th)
        g = np.array(cm.data, dtype=np.int16).reshape(cm.info.height, cm.info.width); res = cm.info.resolution
        iy, ix = np.nonzero(g >= 99); wx = cm.info.origin.position.x + (ix + .5) * res; wy = cm.info.origin.position.y + (iy + .5) * res
        bx = c * (wx - x) + s * (wy - y); by = -s * (wx - x) + c * (wy - y); d = gap(bx, by); leth = g[iy, ix] >= 100   # OccupancyGrid 0~100 척도: 100 = 치명(254), 99 = 내접(253) — 첫 판은 253 으로 잘못 셈
        rr = np.array(sc.ranges); a = sc.angle_min + sc.angle_increment * np.arange(len(rr)) + LYAW; ok = np.isfinite(rr) & (rr > 0.05)
        lg = gap(LX + rr[ok] * np.cos(a[ok]), rr[ok] * np.sin(a[ok])); k = np.argmin(lg) if len(lg) else None
        cc = [v for v in C if t - 1 < v[0] <= t]; ad = ('%.1f' % (100 * math.hypot(A[-1][1] - x, A[-1][2] - y))) if A else '-'
        # 가장 가까운 치명 칸이 차체 어느 쪽인가
        if leth.any():
            j = np.argmin(np.where(leth, d, 9)); side = '%s%s' % ('앞' if bx[j] > XF else '뒤' if bx[j] < XB else '', '왼' if by[j] > HW else '오' if by[j] < -HW else '')
            ld = '%.3f(%s, 차체 %+.2f,%+.2f)' % (d[j], side or '안', bx[j], by[j])
        else: ld = '-'
        out.append('%+6.1f s  odom(%.2f,%.2f,%+4.0f°) | 외곽 안 치명 %d·내접 %d | 치명 최근접 %s | 라이다 최근접 %.3f(차체 %+.2f,%+.2f) | cmd %d개 v %+.3f~%+.3f w %+.2f~%+.2f | B−A %s cm' % (
            t - TA, x, y, math.degrees(th), int(((d == 0) & leth).sum()), int(((d == 0) & ~leth).sum()), ld,
            lg[k] if k is not None else -1, (LX + rr[ok][k] * math.cos(a[ok][k])) if k is not None else 0, (rr[ok][k] * math.sin(a[ok][k])) if k is not None else 0,
            len(cc), min([v[1] for v in cc], default=0), max([v[1] for v in cc], default=0), min([v[2] for v in cc], default=0), max([v[2] for v in cc], default=0), ad))
print('\n'.join(out))
