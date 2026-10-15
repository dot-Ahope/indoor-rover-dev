#!/usr/bin/env python3
"""chk_box_face — 로버가 서 있는 동안 로컬 코스트맵에 찍힌 출발점 시험 상자의 서쪽 면(로버 쪽 면) x 를 프레임마다 기록. (2026-10-15 §22, Jetson 에서 실행, 로버 안 움직임)
  왜: nvblox esdf_integrator_max_site_distance_vox 2.0 → 1.0 정지 A/B — 카메라만 보는 낮은 상자의 면이 실제 면에 얼마나 가까워지는지(실제 면은 사용자 줄자).
  방법: /local_costmap/costmap(odom) 의 치명 칸(≥ 100)을 map→odom 으로 지도 좌표로 옮겨, 구역(x 0.6~1.6, y −0.30~0.25) 안 칸 중 행(y 5 cm)마다 가장 서쪽 칸의 서쪽 가장자리 x.
        프레임마다 전체 가장 서쪽 가장자리 · 칸 수, 끝에 중앙값과 행별 중앙값. 로버(base_link) 지도 자세도.
  인자: [초=20] [라벨]"""
import sys, time, math
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import OccupancyGrid
from tf2_msgs.msg import TFMessage
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 20.0; LAB = sys.argv[2] if len(sys.argv) > 2 else ''
yq = lambda q: math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
class N(Node):
    def __init__(s):
        super().__init__('chk_box_face'); s.ob = s.mo = None; s.F = []; s.rows = {}
        s.create_subscription(TFMessage, '/tf', s.cb_tf, 50)
        s.create_subscription(OccupancyGrid, '/local_costmap/costmap', s.cb_lc, QoSProfile(depth=2, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    def cb_tf(s, m):
        for tr in m.transforms:
            v = (tr.transform.translation.x, tr.transform.translation.y, yq(tr.transform.rotation))
            if tr.child_frame_id == 'base_link' and tr.header.frame_id == 'odom': s.ob = v
            elif tr.child_frame_id == 'odom' and tr.header.frame_id == 'map': s.mo = v
    def cb_lc(s, m):
        if s.mo is None or s.ob is None: return
        a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.nonzero(a >= 100)
        ox = m.info.origin.position.x + (ix + 0.5) * m.info.resolution; oy = m.info.origin.position.y + (iy + 0.5) * m.info.resolution
        c, sn = math.cos(s.mo[2]), math.sin(s.mo[2]); mx = s.mo[0] + c * ox - sn * oy; my = s.mo[1] + sn * ox + c * oy
        k = (mx > 0.6) & (mx < 1.6) & (my > -0.30) & (my < 0.25)
        if not k.any(): s.F.append((np.nan, 0)); return
        west = mx[k].min() - m.info.resolution / 2; s.F.append((west, int(k.sum())))
        for x, y in zip(mx[k], my[k]):
            r = round(y / 0.05) * 0.05; s.rows.setdefault(r, []).append(x - m.info.resolution / 2)
rclpy.init(); n = N(); t0 = time.time()
while time.time() - t0 < DUR: rclpy.spin_once(n, timeout_sec=0.2)
F = np.array(n.F, dtype=float)
rx = n.mo[0] + math.cos(n.mo[2]) * n.ob[0] - math.sin(n.mo[2]) * n.ob[1]; ry = n.mo[1] + math.sin(n.mo[2]) * n.ob[0] + math.cos(n.mo[2]) * n.ob[1]
print('[%s] %d 프레임 · 로버 지도 (%.3f, %.3f, %+.1f°) · 차체 앞끝 x ≈ %.3f(앞 0.262 m)' % (LAB, len(F), rx, ry, math.degrees(n.ob[2] + n.mo[2]), rx + 0.262 * math.cos(n.ob[2] + n.mo[2])))
ok = ~np.isnan(F[:, 0]) if len(F) else np.array([], bool)
if ok.any():
    print('  상자 서쪽 면 x(가장 서쪽 칸의 서쪽 가장자리): 중앙 %.3f · 최소 %.3f · 최대 %.3f · 칸 수 중앙 %d' % (np.median(F[ok, 0]), F[ok, 0].min(), F[ok, 0].max(), int(np.median(F[ok, 1]))))
    for r in sorted(n.rows): v = n.rows[r]; print('  행 y %+.2f: 그 행 서쪽 가장자리 최소 %.3f (프레임 칸 %d)' % (r, min(v), len(v)))
else: print('  구역 안 치명 칸 없음')
n.destroy_node(); rclpy.shutdown()
