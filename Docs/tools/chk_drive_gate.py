#!/usr/bin/env python3
"""chk_drive_gate — 주행 직전 게이트 B · C · G2 를 한 노드(DDS 참여자 1 개)로 (2026-10-27 §24, Jetson, 로버 안 움직임).
  왜: 러너(job551)가 B = `ros2 topic hz /wheel_odom`(12 s) · C = job386_slamalive.py(5 s) · G2 = job440_startclear.py(최대 60 s)를
      따로 띄워 참여자 3 개 · 약 25 s 가 들었다. 판정 기준은 그대로 옮긴다.
    B  /wheel_odom 수신이 있어야 함(옛 기준: hz 평균이 찍히면 통과) → 5 s 동안 ≥ 1 Hz 면 통과, 값(Hz)도 출력.
    C  map→odom: 5 s 동안 수신 간격 최대 < 0.5 s · stamp 지연(수신 − stamp) 최대 < 1.0 s (job386 그대로).
    G2 출발 자세 여유 = 로컬 코스트맵 LETHAL(100) 칸 · 라이다 점(2 m 안) ↔ 차체 외곽(반길이 0.25 · 반폭 0.165) 최소(m) (job440 그대로).
  출력 마지막 줄: 'GATE B=<OK|FAIL> C=<OK|FAIL> G2=<m|nan>' — 러너가 읽는다(G2 문턱 0.10 은 러너 쪽).
  인자: [관찰 s=5]"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg import TFMessage
import tf2_ros
SEC = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
HL, HW = 0.25, 0.165


def yaw_of(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def fp_dist(rx, ry): return np.hypot(np.maximum(np.abs(rx) - HL, 0), np.maximum(np.abs(ry) - HW, 0))


rclpy.init(); n = Node('drive_gate'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'cm': None, 'scan': None}; wheel = []; mo = []
n.create_subscription(Odometry, '/wheel_odom', lambda m: wheel.append(time.time()), qos_profile_sensor_data)
def cb_tf(m):
    now = n.get_clock().now().nanoseconds * 1e-9
    for tr in m.transforms:
        if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((now, now - (tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9)))
n.create_subscription(TFMessage, '/tf', cb_tf, 100)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('cm', m),
                      QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('scan', m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < SEC or ((S['cm'] is None or S['scan'] is None) and time.time() - t0 < 12.0):
    rclpy.spin_once(n, timeout_sec=0.05)
# B
w = [x for x in wheel if x >= t0]; bhz = (len(w) - 1) / (w[-1] - w[0]) if len(w) > 2 else 0.0
B = 'OK' if bhz >= 1.0 else 'FAIL'; print('  B /wheel_odom %.1f Hz' % bhz)
# C (job386)
if len(mo) < 2: C = 'FAIL'; print('  C map->odom 수신 %d 개 — SLAM 무응답' % len(mo))
else:
    gap = max(mo[i][0] - mo[i - 1][0] for i in range(1, len(mo))); lag = max(r[1] for r in mo)
    C = 'OK' if (gap < 0.5 and lag < 1.0) else 'FAIL'; print('  C map->odom %d 개/%.0f s, 최대 간격 %.2f s, 최대 stamp 지연 %.2f s' % (len(mo), time.time() - t0, gap, lag))
# G2 (job440)
def tf_now(target, source, sec=10.0):
    t1 = time.time()
    while time.time() - t1 < sec:
        if buf.can_transform(target, source, rclpy.time.Time()): return buf.lookup_transform(target, source, rclpy.time.Time()).transform
        rclpy.spin_once(n, timeout_sec=0.1)
    print('  G2 TF %s←%s %.0f s 안에 없음' % (target, source, sec)); return None
dc = ds = float('nan')
if S['cm'] is None: print('  G2 로컬 코스트맵 수신 없음')
else:
    m = S['cm']; T = tf_now(m.header.frame_id, 'base_link')
    if T is not None:
        px, py, pth = T.translation.x, T.translation.y, yaw_of(T.rotation)
        d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width); jj, ii = np.where(d >= 100)   # 99(내접)는 반경을 두 번 셈 → LETHAL 만(09-18 dy5)
        X = m.info.origin.position.x + (ii + 0.5) * m.info.resolution - px; Y = m.info.origin.position.y + (jj + 0.5) * m.info.resolution - py
        c, s = math.cos(-pth), math.sin(-pth); rx, ry = X * c - Y * s, X * s + Y * c
        dd = fp_dist(rx, ry); k = int(np.argmin(dd)) if dd.size else -1; dc = float(dd.min()) if dd.size else 9.9
        print('  G2 로컬 코스트맵 LETHAL ↔ 차체 외곽 최소 %.3f m%s' % (dc, (' @ 차체 (%+.2f, %+.2f)' % (rx[k], ry[k])) if k >= 0 else ''))
if S['scan'] is None: print('  G2 /scan 수신 없음')
else:
    sc = S['scan']; T = tf_now('base_link', sc.header.frame_id)
    if T is not None:
        ly = yaw_of(T.rotation); lx, lyy = T.translation.x, T.translation.y
        r = np.asarray(sc.ranges, dtype=np.float64); a = sc.angle_min + np.arange(r.size) * sc.angle_increment
        ok = np.isfinite(r) & (r > sc.range_min) & (r < 2.0)
        bx = lx + r[ok] * np.cos(a[ok] + ly); by = lyy + r[ok] * np.sin(a[ok] + ly)
        dd = fp_dist(bx, by); k = int(np.argmin(dd)) if dd.size else -1; ds = float(dd.min()) if dd.size else 9.9
        print('  G2 라이다 점 ↔ 차체 외곽 최소 %.3f m%s' % (ds, (' @ 차체 (%+.2f, %+.2f)' % (bx[k], by[k])) if k >= 0 else ''))
g2 = np.nanmin([dc, ds]) if not (math.isnan(dc) and math.isnan(ds)) else float('nan')
print('  게이트 노드 %.1f s' % (time.time() - t0)); rclpy.shutdown()
print('GATE B=%s C=%s G2=%s' % (B, C, ('%.3f' % g2) if not math.isnan(g2) else 'nan'))
