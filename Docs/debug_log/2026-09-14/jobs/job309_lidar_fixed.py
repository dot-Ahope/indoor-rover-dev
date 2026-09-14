#!/usr/bin/env python3
"""라이다 '고정점' 판정 (2026-09-14, 사용자 관찰: 우측 전방에 로버 중심에서 항상 같은 거리에 찍히는 점 하나).
  정지 상태에서 /scan 을 6 s 모아 0.6 m 안 반환을 각도 인덱스별로 세고, 80 % 이상 지속되는 것을
  차체좌표·거리 지터·강도와 함께 보고한다. 로버 자체(0.25×0.165 + 데크)를 맞히는 자기반사인지,
  특정 각도 고정 아티팩트인지 구분한다. 로컬 코스트맵에 LETHAL 로 남는지도 본다. 로버는 움직이지 않는다."""
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid
import tf2_ros
rclpy.init(); n = Node('lidar309'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = []; G = {}
n.create_subscription(LaserScan, '/scan', lambda m: S.append(m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('g', m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
t0 = time.time()
while time.time() - t0 < 6.0:
    rclpy.spin_once(n, timeout_sec=0.05)
print('스캔 %d개, range_min %.3f range_max %.1f, 점/스캔 %d, 강도 필드 %s' % (len(S), S[0].range_min, S[0].range_max, len(S[0].ranges), '있음' if len(S[0].intensities) else '없음'))
lt = buf.lookup_transform('base_link', S[0].header.frame_id, rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=3.0)).transform
q = lt.rotation; lyaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
print('lidar->base_link (%.3f, %.3f) yaw %.0f°' % (lt.translation.x, lt.translation.y, math.degrees(lyaw)))
N = len(S[0].ranges); cnt = np.zeros(N, int); rs = [[] for _ in range(N)]; its = [[] for _ in range(N)]
near_total = 0
for m in S:
    r = np.array(m.ranges); ok = np.isfinite(r) & (r > 0.0) & (r < 0.6)
    near_total += int(ok.sum())
    for i in np.where(ok)[0]:
        cnt[i] += 1; rs[i].append(r[i])
        if len(m.intensities): its[i].append(m.intensities[i])
print('0.6 m 안 반환: 스캔당 평균 %.1f개' % (near_total / len(S)))
print('지속률 ≥80 % 의 각도 인덱스 (거리 0.6 m 안):')
print('   idx   각도(lidar)  차체 x     y      거리중앙  거리σ    강도중앙  지속률  자기반사?')
found = 0
for i in np.where(cnt >= 0.8 * len(S))[0]:
    a = S[0].angle_min + i * S[0].angle_increment
    rm = float(np.median(rs[i])); rsd = float(np.std(rs[i]))
    lx, ly = rm * math.cos(a), rm * math.sin(a)
    bx = lt.translation.x + lx * math.cos(lyaw) - ly * math.sin(lyaw); by = lt.translation.y + lx * math.sin(lyaw) + ly * math.cos(lyaw)
    inside = (abs(bx) <= 0.30) and (abs(by) <= 0.20)
    im = float(np.median(its[i])) if its[i] else float('nan')
    print('  %4d   %+7.1f°    %+.3f  %+.3f   %.3f    %.4f   %6.1f    %3.0f%%   %s' % (i, math.degrees(a), bx, by, rm, rsd, im, 100.0 * cnt[i] / len(S), '차체 안(0.30×0.20)' if inside else ''))
    found += 1
if not found:
    print('  없음 — 0.6 m 안에 지속되는 반환이 없다')
# 근접 반환의 각도 이웃 폭: 한 인덱스만 켜지면 아티팩트/얇은 물체, 여러 인덱스면 면
if 'g' in G:
    g = G['g']; res = g.info.resolution
    try:
        t = buf.lookup_transform(g.header.frame_id, 'base_link', rclpy.time.Time()).transform
        qq = t.rotation; yaw = math.atan2(2*(qq.w*qq.z+qq.x*qq.y), 1-2*(qq.y*qq.y+qq.z*qq.z))
        d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width)
        print('로컬 코스트맵(%s) 차체 0.45 m 안 LETHAL 셀:' % g.header.frame_id)
        jj, ii = np.where(d >= 100)
        k = 0
        for i_, j_ in zip(ii, jj):
            X = g.info.origin.position.x + (i_ + 0.5) * res; Y = g.info.origin.position.y + (j_ + 0.5) * res
            dx, dy = X - t.translation.x, Y - t.translation.y
            bx = dx * math.cos(yaw) + dy * math.sin(yaw); by = -dx * math.sin(yaw) + dy * math.cos(yaw)
            if math.hypot(bx, by) < 0.45:
                print('   차체 (%+.2f, %+.2f)' % (bx, by)); k += 1
        if not k: print('   없음')
    except Exception as e:
        print('코스트맵 TF 실패:', e)
