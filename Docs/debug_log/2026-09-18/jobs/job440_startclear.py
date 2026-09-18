#!/usr/bin/env python3
"""출발 자세 여유 게이트 (2026-09-18 dy3 교훈): 로버 뒤 ≈5 cm 의 물체(관찰자 발 추정)로 출발 자세가 내접 셀 안에 들어가
   스무더 충돌·Optimizer fail 이 났다. 로컬 코스트맵 99/100 셀과 /scan 점의 차체 외곽(반길이 0.25·반폭 0.165) 거리 최소를 본다.
   마지막 줄 = 둘 중 작은 값(m). 러너가 ≥ 0.10 을 요구.
"""
import time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
import tf2_ros
HL, HW = 0.25, 0.165


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wait_tf(target, source, sec=10.0):
    """09-18 dy4: 새 노드가 /tf 를 받기 전에 조회해 예외로 죽었다(코스트맵은 transient_local 로 즉시 와서 순서가 뒤바뀜) → 준비될 때까지 기다린다."""
    t0 = time.time()
    while time.time() - t0 < sec:
        if buf.can_transform(target, source, rclpy.time.Time()):
            return buf.lookup_transform(target, source, rclpy.time.Time()).transform
        rclpy.spin_once(n, timeout_sec=0.1)
    print('출발 자세: TF %s←%s %.0f s 안에 없음' % (target, source, sec)); return None


def fp_dist(rx, ry):
    return np.hypot(np.maximum(np.abs(rx) - HL, 0), np.maximum(np.abs(ry) - HW, 0))


rclpy.init(); n = Node('startclear440'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = {'cm': None, 'scan': None}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('cm', m), qos)
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('scan', m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 12.0 and (S['cm'] is None or S['scan'] is None):   # 09-18 dy4: 6 s 안에 못 받아 nan → 12 s
    rclpy.spin_once(n, timeout_sec=0.1)
dc = ds = float('nan')
if S['cm'] is None: print('출발 자세: 로컬 코스트맵 수신 없음(12 s)')
if S['scan'] is None: print('출발 자세: /scan 수신 없음(12 s)')
if S['cm'] is not None:
    m = S['cm']
    T = wait_tf(m.header.frame_id, 'base_link')
if S['cm'] is not None and T is not None:
    px, py, pth = T.translation.x, T.translation.y, yaw_of(T.rotation)
    # 09-18 dy5: 99(내접)는 '로버 중심이 여기면 충돌' 이라 차체 외곽과 재면 반경을 두 번 센다(09-11 같은 실수) → LETHAL(100)만
    d = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width); jj, ii = np.where(d >= 100)
    X = m.info.origin.position.x + (ii + 0.5) * m.info.resolution - px; Y = m.info.origin.position.y + (jj + 0.5) * m.info.resolution - py
    c, s = math.cos(-pth), math.sin(-pth); rx, ry = X * c - Y * s, X * s + Y * c
    dd = fp_dist(rx, ry); k = int(np.argmin(dd)) if dd.size else -1
    dc = float(dd.min()) if dd.size else 9.9
    print('출발 자세: 로컬 코스트맵 LETHAL(100) 셀 ↔ 차체 외곽 최소 %.3f m%s' % (dc, (' @ 차체 (%+.2f, %+.2f)' % (rx[k], ry[k])) if k >= 0 else ''))
if S['scan'] is not None:
    sc = S['scan']
    T = wait_tf('base_link', sc.header.frame_id)
if S['scan'] is not None and T is not None:
    ly = yaw_of(T.rotation); lx, lyy = T.translation.x, T.translation.y
    r = np.asarray(sc.ranges, dtype=np.float64); a = sc.angle_min + np.arange(r.size) * sc.angle_increment
    ok = np.isfinite(r) & (r > sc.range_min) & (r < 2.0)
    bx = lx + r[ok] * np.cos(a[ok] + ly); by = lyy + r[ok] * np.sin(a[ok] + ly)
    dd = fp_dist(bx, by); k = int(np.argmin(dd)) if dd.size else -1
    ds = float(dd.min()) if dd.size else 9.9
    print('출발 자세: 라이다 점 ↔ 차체 외곽 최소 %.3f m%s' % (ds, (' @ 차체 (%+.2f, %+.2f)' % (bx[k], by[k])) if k >= 0 else ''))
rclpy.shutdown()
print('%.3f' % np.nanmin([dc, ds]) if not (math.isnan(dc) and math.isnan(ds)) else 'nan')
