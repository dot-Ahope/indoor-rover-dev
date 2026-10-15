#!/usr/bin/env python3
"""chk_box_dump — 정지 상태에서 시험 상자 둘레의 세 층을 지도 좌표로 저장(Jetson 에서 실행, 로버 안 움직임). (2026-10-15 §23)
  왜: 사용자 "시각화해서 두 경우(site 2.0 · 1.0)의 데이터를 비교" — 요약값만 남긴 chk_box_face 대신 원자료를 같은 그림에.
  층: ① 카메라 깊이 점군 /camera/camera/depth/color/points(원시, TSDF 전) ② nvblox 거리 지도 조각 /nvblox_node/static_map_slice(카메라 지도)
      ③ 로컬 코스트맵 /local_costmap/costmap(최종 장애물). 좌표 변환은 tf2(지도 ← 각 프레임).
  저장: /tmp/box_dump_<라벨>.npz — pts(x, y, z, 지도 · 구역 안 · 프레임 합침, 최대 20 만 점), slice(x, y, 거리), lc(x, y, 값), robot(x, y, yaw), 원점·해상도.
  구역(지도): x 0.6~1.6, y −0.40~0.30.  인자: 라벨 [초=12]"""
import sys, time, math, struct
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import PointCloud2
from nvblox_msgs.msg import DistanceMapSlice
import tf2_ros
LAB = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
BX = (0.6, 1.6, -0.40, 0.30)
def qmat(q):
    x, y, z, w = q.x, q.y, q.z, q.w
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
class N(Node):
    def __init__(s):
        super().__init__('chk_box_dump'); s.buf = tf2_ros.Buffer(); s.tl = tf2_ros.TransformListener(s.buf, s)
        s.P = []; s.S = None; s.L = None; s.npts = 0
        s.create_subscription(PointCloud2, '/camera/camera/depth/color/points', s.cb_pc, qos_profile_sensor_data)
        s.create_subscription(DistanceMapSlice, '/nvblox_node/static_map_slice', s.cb_sl, 5)
        s.create_subscription(OccupancyGrid, '/local_costmap/costmap', s.cb_lc, QoSProfile(depth=2, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    def tf(s, frame):
        t = s.buf.lookup_transform('map', frame, rclpy.time.Time()); tr = t.transform
        return np.array([tr.translation.x, tr.translation.y, tr.translation.z]), qmat(tr.rotation)
    def cb_pc(s, m):
        if s.npts > 200000: return
        try: T, R = s.tf(m.header.frame_id)
        except Exception: return
        off = {f.name: f.offset for f in m.fields}
        a = np.frombuffer(m.data, np.uint8).reshape(-1, m.point_step)
        xyz = np.stack([a[:, off[k]:off[k] + 4].copy().view(np.float32).ravel() for k in ('x', 'y', 'z')], 1)
        xyz = xyz[np.isfinite(xyz).all(1)]; w = xyz @ R.T + T
        k = (w[:, 0] > BX[0]) & (w[:, 0] < BX[1]) & (w[:, 1] > BX[2]) & (w[:, 1] < BX[3]) & (w[:, 2] > -0.10) & (w[:, 2] < 0.40)
        s.P.append(w[k]); s.npts += int(k.sum())
    def cb_sl(s, m):
        try: T, R = s.tf(m.header.frame_id)
        except Exception: return
        d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.indices(d.shape)
        lx = m.origin.x + (ix + 0.5) * m.resolution; ly = m.origin.y + (iy + 0.5) * m.resolution
        wx = T[0] + R[0, 0] * lx + R[0, 1] * ly; wy = T[1] + R[1, 0] * lx + R[1, 1] * ly
        k = (wx > BX[0]) & (wx < BX[1]) & (wy > BX[2]) & (wy < BX[3]) & (d != m.unknown_value)
        s.S = np.stack([wx[k], wy[k], d[k]], 1)
    def cb_lc(s, m):
        try: T, R = s.tf(m.header.frame_id)
        except Exception: return
        a = np.array(m.data, np.int16).reshape(m.info.height, m.info.width); iy, ix = np.indices(a.shape)
        lx = m.info.origin.position.x + (ix + 0.5) * m.info.resolution; ly = m.info.origin.position.y + (iy + 0.5) * m.info.resolution
        wx = T[0] + R[0, 0] * lx + R[0, 1] * ly; wy = T[1] + R[1, 0] * lx + R[1, 1] * ly
        k = (wx > BX[0]) & (wx < BX[1]) & (wy > BX[2]) & (wy < BX[3]) & (a > 0)
        s.L = np.stack([wx[k], wy[k], a[k]], 1)
rclpy.init(); n = N(); t0 = time.time()
while time.time() - t0 < DUR: rclpy.spin_once(n, timeout_sec=0.2)
T, R = n.tf('base_link'); yaw = math.atan2(R[1, 0], R[0, 0])
P = np.concatenate(n.P) if n.P else np.zeros((0, 3))
np.savez_compressed('/tmp/box_dump_%s.npz' % LAB, pts=P.astype(np.float32), slice=n.S, lc=n.L, robot=np.array([T[0], T[1], yaw]))
print('[%s] 점군 %d 점 · 조각 칸 %d(≤0: %d) · 코스트맵 칸 %d(치명 %d) · 로버 (%.3f, %.3f, %+.1f°) → /tmp/box_dump_%s.npz' % (
    LAB, len(P), 0 if n.S is None else len(n.S), 0 if n.S is None else int((n.S[:, 2] <= 0).sum()), 0 if n.L is None else len(n.L), 0 if n.L is None else int((n.L[:, 2] >= 100).sum()), T[0], T[1], math.degrees(yaw), LAB))
n.destroy_node(); rclpy.shutdown()
