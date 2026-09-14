#!/usr/bin/env python3
"""전역 코스트맵 흔들림 정량 (2026-09-14 §2.19 후속). 로버 정지, 주행 없음.

  DUR 초 동안 10 s 마다:
    - map→odom (x, y, yaw)  — slam_toolbox 보정이 정지 중에 움직이는가
    - 전역 코스트맵 상자 LETHAL 셀: map 좌표 범위(셀 자체가 번지는가) 와 차체좌표 범위(계획기가 보는 상자)
    - 로컬 코스트맵 상자 LETHAL 셀: 차체좌표 범위 (odom 프레임, 대조군)
  끝에: map→odom 이동량(최대-최소), 전역 셀 map 좌표 범위의 팽창량, 전역/로컬 차체 y 범위 비교 → 원인 분리.
  인자: BX BY [DUR=300] [PERIOD=10]
"""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
import tf2_ros

BX, BY = float(sys.argv[1]), float(sys.argv[2])
DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
PER = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
rclpy.init(); n = Node('gwobble318'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
G = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: G.__setitem__('gc', m), qos)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: G.__setitem__('lc', m), qos)


def tf_xyyaw(parent, child):
    t = buf.lookup_transform(parent, child, rclpy.time.Time()).transform
    q = t.rotation
    return (t.translation.x, t.translation.y, math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z)))


def box_cells(g, frame):
    """코스트맵 상자 근방 LETHAL 셀 → (map/odom 좌표 배열, 차체좌표 배열)"""
    px, py, pyaw = tf_xyyaw(frame, 'base_link')
    d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); jj, ii = np.where(d >= 100)
    X = g.info.origin.position.x + (ii + 0.5) * g.info.resolution; Y = g.info.origin.position.y + (jj + 0.5) * g.info.resolution
    dx, dy = X - px, Y - py
    bx = dx * math.cos(pyaw) + dy * math.sin(pyaw); by = -dx * math.sin(pyaw) + dy * math.cos(pyaw)
    sel = (bx > BX - 0.20) & (bx < BX + 0.45) & (by > BY - 0.40) & (by < BY + 0.40)
    return np.column_stack([X[sel], Y[sel]]), np.column_stack([bx[sel], by[sel]])


t0 = time.time()
while time.time() - t0 < 20 and ('gc' not in G or 'lc' not in G or not buf.can_transform('map', 'odom', rclpy.time.Time())):
    rclpy.spin_once(n, timeout_sec=0.1)
rows = []
print('  t(s)   map→odom x      y     yaw°  | 전역 상자: 셀수  map x범위        map y범위        차체 y범위      | 로컬 상자: 셀수 차체 y범위')
t_start = time.time(); next_t = t_start
while time.time() - t_start < DUR:
    while time.time() < next_t:
        rclpy.spin_once(n, timeout_sec=0.05)
    next_t += PER
    try:
        mo = tf_xyyaw('map', 'odom')
        gm, gb = box_cells(G['gc'], 'map')
        lm, lb = box_cells(G['lc'], 'odom')
    except Exception as e:
        print('  TF/코스트맵 오류: %s' % e); continue
    r = dict(t=time.time() - t_start, mo=mo, gn=len(gm), gmx=(gm[:, 0].min(), gm[:, 0].max()) if len(gm) else (np.nan, np.nan),
             gmy=(gm[:, 1].min(), gm[:, 1].max()) if len(gm) else (np.nan, np.nan), gby=(gb[:, 1].min(), gb[:, 1].max()) if len(gb) else (np.nan, np.nan),
             ln=len(lm), lby=(lb[:, 1].min(), lb[:, 1].max()) if len(lb) else (np.nan, np.nan))
    rows.append(r)
    print('  %5.0f   %+.3f  %+.3f  %+6.2f | %3d  %.2f~%.2f  %+.2f~%+.2f  %+.2f~%+.2f | %3d  %+.2f~%+.2f'
          % (r['t'], mo[0], mo[1], math.degrees(mo[2]), r['gn'], r['gmx'][0], r['gmx'][1], r['gmy'][0], r['gmy'][1], r['gby'][0], r['gby'][1], r['ln'], r['lby'][0], r['lby'][1]))
if rows:
    mx = [r['mo'][0] for r in rows]; my = [r['mo'][1] for r in rows]; myaw = [math.degrees(r['mo'][2]) for r in rows]
    print('=== 요약 (%d 표본, %.0f s) ===' % (len(rows), rows[-1]['t']))
    print('  map→odom 흔들림: x %.3f m, y %.3f m, yaw %.2f° (최대−최소)' % (max(mx) - min(mx), max(my) - min(my), max(myaw) - min(myaw)))
    gy_lo = [r['gmy'][0] for r in rows if not np.isnan(r['gmy'][0])]; gy_hi = [r['gmy'][1] for r in rows if not np.isnan(r['gmy'][1])]
    if gy_lo:
        print('  전역 상자 셀 map y 범위: 처음 %+.2f~%+.2f → 끝 %+.2f~%+.2f (폭 %.2f → %.2f), 셀수 %d → %d' % (gy_lo[0], gy_hi[0], gy_lo[-1], gy_hi[-1], gy_hi[0] - gy_lo[0], gy_hi[-1] - gy_lo[-1], rows[0]['gn'], rows[-1]['gn']))
    gb_hi = [r['gby'][1] for r in rows if not np.isnan(r['gby'][1])]; lb_hi = [r['lby'][1] for r in rows if not np.isnan(r['lby'][1])]
    if gb_hi and lb_hi:
        print('  차체좌표 상자 좌측 가장자리(최대 y): 전역 %+.2f~%+.2f (변동 %.2f) | 로컬 %+.2f~%+.2f (변동 %.2f)'
              % (min(gb_hi), max(gb_hi), max(gb_hi) - min(gb_hi), min(lb_hi), max(lb_hi), max(lb_hi) - min(lb_hi)))
    print('  판독: map→odom 이 흔들리고 전역 셀 map 폭이 커지면 "SLAM 보정 × STVL 누적", map→odom 이 고정인데 전역만 넓으면 "감쇠/누적", 둘 다 고정이면 오늘 관측은 재기동 직후 과도 상태였다')
