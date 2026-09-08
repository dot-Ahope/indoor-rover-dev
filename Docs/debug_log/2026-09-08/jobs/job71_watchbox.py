#!/usr/bin/env python3
"""상자 셀 추적 실험 — 접근하는 동안 코스트맵의 '상자 칸'이 언제·왜 사라지는지 직접 본다.
  사용: python3 job71_watchbox.py [주행거리m=0.45] [속도=0.04]
동작: 시작 시 전방 포인트클라우드로 상자 위치를 자동 검출 → 그 map 좌표를 고정 → 저속 전진하며
      0.25s 마다 (로버x, 카메라~상자 거리, 로컬 비용, 전역 비용, 상자 근방 깊이점 수) 를 기록.
Nav2 를 쓰지 않고 /cmd_vel 직접 발행(전역경로·컨트롤러 영향 배제) → 순수하게 코스트맵 거동만 본다."""
import math, sys, time, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid

DIST = float(sys.argv[1]) if len(sys.argv) > 1 else 0.45
VEL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.04
CAM_X = 0.232

rclpy.init(); n = Node('watchbox')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
pub = n.create_publisher(Twist, '/cmd_vel', 10)
S = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('lc', m), qos)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: S.__setitem__('gc', m), qos)

def R(q):
    w, x, y, z = q.w, q.x, q.y, q.z
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
def cloud(frame):
    """지정 프레임에서의 포인트 (N,3). 실패 시 None."""
    if 'pc' not in S: return None
    m = S['pc']
    try: tr = buf.lookup_transform(frame, m.header.frame_id, rclpy.time.Time()).transform
    except Exception: return None
    off = {f.name: f.offset for f in m.fields}; step = m.point_step
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, step)
    xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x','y','z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    return xyz @ R(tr.rotation).T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])
def pose():
    try:
        t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception: return None
def cost(key, x, y):
    if key not in S: return None
    g = S[key]; i = g.info
    cx = int((x-i.origin.position.x)/i.resolution); cy = int((y-i.origin.position.y)/i.resolution)
    return g.data[cy*i.width+cx] if 0 <= cx < i.width and 0 <= cy < i.height else None

t0 = time.time()
while time.time()-t0 < 12 and (pose() is None or 'pc' not in S or 'lc' not in S): rclpy.spin_once(n, timeout_sec=0.1)
p0 = pose()
if p0 is None or 'pc' not in S: print("TF/포인트클라우드 없음"); raise SystemExit(1)

# 상자 자동 검출: base_link 기준 z 0.06~0.35, x 0.4~1.3, |y|<0.4 점군의 중앙값
P = cloud('base_link')
sel = P[(P[:,2]>=0.06)&(P[:,2]<0.35)&(P[:,0]>0.4)&(P[:,0]<1.3)&(np.abs(P[:,1])<0.4)]
if len(sel) < 30: print(f"상자 후보 점 부족 ({len(sel)}) — 전방 0.4~1.3m 에 낮은 물체를 두세요"); raise SystemExit(1)
bx, by, bz = float(np.median(sel[:,0])), float(np.median(sel[:,1])), float(np.median(sel[:,2]))
ch, sh = math.cos(p0[2]), math.sin(p0[2])
BX = p0[0] + bx*ch - by*sh; BY = p0[1] + bx*sh + by*ch      # map 고정 좌표
print(f"상자 검출: base_link ({bx:.2f},{by:+.2f}) z {bz:.2f}, 점 {len(sel)} → map ({BX:.2f},{BY:+.2f})")
print(f"전진 {DIST}m @ {VEL}m/s. 카메라 실명 예상 거리 ≈0.29m\n")
print("  t   로버x  카메라~상자  로컬  전역  상자근방 깊이점")

cmd = Twist(); cmd.linear.x = VEL
t1 = time.time(); nxt = t1; log = t1; start_x = p0[0]
while time.time()-t1 < DIST/VEL + 2:
    rclpy.spin_once(n, timeout_sec=0.01)
    now = time.time()
    if now >= nxt: pub.publish(cmd); nxt += 0.05
    p = pose()
    if p and math.hypot(p[0]-p0[0], p[1]-p0[1]) >= DIST: break
    if now >= log and p:
        log += 0.25
        camd = math.hypot(BX-(p[0]+CAM_X*math.cos(p[2])), BY-(p[1]+CAM_X*math.sin(p[2])))
        Q = cloud('map'); nb = 0
        if Q is not None:
            nb = int(np.sum((np.abs(Q[:,0]-BX)<0.12)&(np.abs(Q[:,1]-BY)<0.12)&(Q[:,2]>0.06)&(Q[:,2]<0.35)))
        print(f"{now-t1:5.1f} {p[0]-start_x:+.3f}    {camd:.3f}    {str(cost('lc',BX,BY)):>4} {str(cost('gc',BX,BY)):>4}   {nb:5d}", flush=True)
for _ in range(20): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.03)
print("\n정지. 로컬/전역 비용이 언제 0 으로 떨어지는지, 그때 깊이점이 0 인지 보면 원인이 갈린다:")
print("  깊이점 0 + 비용 유지  → 기억 정상 (raytrace_min_range 효과 있음)")
print("  깊이점 0 + 비용 0     → 소거가 일어남 (다른 소스가 지우거나 min_range 미적용)")
print("  깊이점 >0 + 비용 0    → 마킹 자체가 안 됨 (높이/문턱/사거리 문제)")
