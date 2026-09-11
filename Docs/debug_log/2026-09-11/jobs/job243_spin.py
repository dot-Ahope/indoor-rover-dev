#!/usr/bin/env python3
"""제자리 회전 중 병진 드리프트 실측 (2026-09-11).

  사용자 관찰: "목표 도달 후 자세를 바꾸기 위해 제자리 회전을 하는데, 마찰력과 양쪽 바퀴
  속도 다름 이슈로 **뒤로 밀리면서** 회전했다."

  왜 중요한가: 스키드스티어의 제자리 회전은 양 트랙을 반대로 돌린다. 좌우 모터 특성과
  트랙 마찰이 대칭이 아니면 순수 회전이 아니라 **병진 성분**이 섞인다. 그런데 휠
  오도메트리는 좌우 속도가 대칭이라고 가정하고 vx = (vL+vR)/2 를 낸다 — 제자리 회전이면
  vx = 0 을 보고한다. 실제로 밀리면 **EKF 가 그만큼 놓치고**, odom 프레임이 실제와 어긋난다.
  SLAM 이 주행 중 map->odom 으로 흡수하지만, 목표 자세 정렬처럼 회전만 하는 구간에서는
  slam 이 스캔을 적게 처리해 보정이 늦다.

  방법: 제자리 회전 명령(v=0, w=+-W)만 주고
        - odom->base  (휠+IMU 융합 = 로봇이 '믿는' 위치)
        - map->base   (SLAM 보정 포함 = 실제에 가까운 위치)
        를 함께 기록한다. 두 위치 변화량의 차이가 **휠 오도가 놓친 병진**이다.
        라이다 전방거리 변화도 같이 남겨 독립 확인한다.

  안전: 회전 스윕 반경 0.33m. 시작 전 라이다 최근접이 SAFE_MIN 미만이면 중단한다.
  사용: python3 job243_spin.py [회전각deg=360] [방향 1|-1=1] [W=0.32]
"""
import sys
import time
import math
import csv
import numpy as np
import rclpy
import tf2_ros
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import qos_profile_sensor_data

GOAL_DEG = float(sys.argv[1]) if len(sys.argv) > 1 else 360.0
DIRN = 1.0 if (len(sys.argv) < 3 or float(sys.argv[2]) >= 0) else -1.0
W = (float(sys.argv[3]) if len(sys.argv) > 3 else 0.32) * DIRN
SAFE_MIN = 0.40          # m — 회전 스윕 0.33 + 여유

rclpy.init()
n = Node('spin243')
buf = tf2_ros.Buffer()
tl = tf2_ros.TransformListener(buf, n)
S = {}
n.create_subscription(LaserScan, '/scan', lambda m: S.__setitem__('sc', m),
                      qos_profile_sensor_data)
pub = n.create_publisher(Twist, '/cmd_vel', 10)


def tf(a, b):
    try:
        t = buf.lookup_transform(a, b, rclpy.time.Time()).transform
        q = t.rotation
        return (t.translation.x, t.translation.y,
                math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z)))
    except Exception:
        return None


def lidar_min():
    sc = S.get('sc')
    if sc is None:
        return None
    r = np.array(sc.ranges)
    ok = np.isfinite(r) & (r > sc.range_min) & (r < sc.range_max)
    return float(r[ok].min()) if ok.any() else None


def stop():
    z = Twist()
    for _ in range(6):
        pub.publish(z)
        time.sleep(0.05)


t0 = time.time()
while time.time() - t0 < 20 and (tf('odom', 'base_link') is None
                                 or tf('map', 'base_link') is None or 'sc' not in S):
    rclpy.spin_once(n, timeout_sec=0.1)
o0, m0 = tf('odom', 'base_link'), tf('map', 'base_link')
if o0 is None or m0 is None:
    print('TF 준비 실패 (map 은 로버가 멈춰 있으면 늦게 온다)')
    stop()
    raise SystemExit(1)
lm = lidar_min()
print('시작 odom (%.3f, %.3f) hd=%.2f | map (%.3f, %.3f) hd=%.2f'
      % (o0[0], o0[1], math.degrees(o0[2]), m0[0], m0[1], math.degrees(m0[2])))
print('라이다 최근접 %.3f m (안전 하한 %.2f)' % (lm if lm else -1, SAFE_MIN))
if lm is not None and lm < SAFE_MIN:
    print('주변이 너무 좁다 — 중단')
    stop()
    raise SystemExit(2)
print()
print('   t   회전(deg)   odom 이동   map 이동   차이(휠이 놓친 병진)  라이다최근접')

rows = []
cmd = Twist()
cmd.angular.z = W
t0 = time.time()
nxt = 0.0
TMO = abs(GOAL_DEG) / abs(math.degrees(W)) + 20.0
while time.time() - t0 < TMO:
    rclpy.spin_once(n, timeout_sec=0.02)
    pub.publish(cmd)
    el = time.time() - t0
    if el < nxt:
        continue
    nxt += 0.5
    o, m = tf('odom', 'base_link'), tf('map', 'base_link')
    if o is None or m is None:
        continue
    rot = math.degrees((o[2] - o0[2] + math.pi) % (2*math.pi) - math.pi)
    od = math.hypot(o[0]-o0[0], o[1]-o0[1])
    md = math.hypot(m[0]-m0[0], m[1]-m0[1])
    lmn = lidar_min()
    rows.append((el, rot, od, md, md-od, lmn if lmn else float('nan'),
                 o[0]-o0[0], o[1]-o0[1], m[0]-m0[0], m[1]-m0[1]))
    print('%6.1f   %+7.1f    %6.3f     %6.3f      %+7.3f            %.3f'
          % (el, rot, od, md, md-od, lmn if lmn else -1))
    if abs(rot) >= abs(GOAL_DEG) - 3:
        print('  목표 회전 도달')
        break
    if lmn is not None and lmn < 0.22:
        print('  ** 안전 정지 (라이다 %.3f m)' % lmn)
        break
stop()
time.sleep(0.6)

o, m = tf('odom', 'base_link'), tf('map', 'base_link')
print()
print('=== 결과 ===')
if o and m:
    od = math.hypot(o[0]-o0[0], o[1]-o0[1])
    md = math.hypot(m[0]-m0[0], m[1]-m0[1])
    rot = math.degrees((o[2] - o0[2] + math.pi) % (2*math.pi) - math.pi)
    print('  회전량            %.1f deg' % rot)
    print('  odom 상 병진      %.3f m   (휠+IMU 가 믿는 값 — 제자리 회전이면 0 이어야 한다)')
    print('                    dx %+.3f  dy %+.3f' % (o[0]-o0[0], o[1]-o0[1]))
    print('  map 상 병진       %.3f m   (SLAM 보정 포함)' % md)
    print('                    dx %+.3f  dy %+.3f' % (m[0]-m0[0], m[1]-m0[1]))
    print('  차이              %+.3f m  ← 휠 오도메트리가 놓친 병진' % (md - od))
    if rows:
        print('  회전 1도당 놓친 병진: %.4f m/deg (%.1f cm / 90deg)'
              % (abs(md-od)/max(abs(rot), 1), 100*abs(md-od)/max(abs(rot), 1)*90))
    print()
    print('  해석: odom 병진이 0 에 가깝고 map 병진이 크면, 로버는 실제로 밀렸는데')
    print('        휠 오도메트리가 그것을 보고하지 못한 것이다(사용자 관찰과 일치).')
    print('        둘 다 크면 휠도 밀림을 일부 감지한 것이고,')
    print('        둘 다 0 에 가까우면 이번 조건에서는 밀림이 없었다는 뜻이다.')
with open('/tmp/job243.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['t', 'rot_deg', 'odom_d', 'map_d', 'diff', 'lidar_min',
                'odom_dx', 'odom_dy', 'map_dx', 'map_dy'])
    w.writerows(rows)
print('  CSV: /tmp/job243.csv (%d행)' % len(rows))
