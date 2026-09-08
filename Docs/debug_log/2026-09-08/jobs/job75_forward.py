#!/usr/bin/env python3
"""전방 장애물 추적 (프레임 정정판) — 접근 중 코스트맵의 '앞쪽 장애물'이 유지되는지 본다.
  사용: python3 job75_forward.py [주행거리m=0.40] [속도=0.04]

이전 job71 의 오류: 로컬 코스트맵은 **odom 프레임**인데 map 좌표로 조회했고, 고정한 상자 map 좌표는
slam 의 map→odom 보정으로 어긋날 수 있었다. 여기서는 매 주기마다
  - 로컬: odom 프레임에서 로버 전방 축을 따라 조회
  - 전역: map 프레임에서 같은 축을 조회
하고, '가장 가까운 점유(≥99) 거리' 를 보고한다. 좌표 고정이 없어 드리프트에 영향받지 않는다.
Nav2 경로·컨트롤러는 쓰지 않고 /cmd_vel 직접 발행."""
import math, sys, time, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid

DIST = float(sys.argv[1]) if len(sys.argv) > 1 else 0.40
VEL = float(sys.argv[2]) if len(sys.argv) > 2 else 0.04
CAM_X = 0.232

rclpy.init(); n = Node('fwdwatch')
buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
pub = n.create_publisher(Twist, '/cmd_vel', 10)
S = {}
qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(PointCloud2, '/camera/camera/depth/color/points', lambda m: S.__setitem__('pc', m), qos_profile_sensor_data)
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: S.__setitem__('lc', m), qos)
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: S.__setitem__('gc', m), qos)

def pose_in(frame):
    try:
        t = buf.lookup_transform(frame, 'base_link', rclpy.time.Time()).transform; q = t.rotation
        return (t.translation.x, t.translation.y, math.atan2(2*(q.w*q.z), 1-2*q.z*q.z))
    except Exception: return None
def nearest_block(key, frame):
    """로버 전방 축 0.30~1.30m 에서 비용 ≥99 인 가장 가까운 거리. 없으면 None."""
    if key not in S: return ('NA', None)
    p = pose_in(frame)
    if p is None: return ('TF', None)
    g = S[key]; i = g.info; ch, sh = math.cos(p[2]), math.sin(p[2])
    worst = 0
    for k in range(0, 51):
        d = 0.30 + 0.02*k
        x = p[0] + d*ch; y = p[1] + d*sh
        cx = int((x-i.origin.position.x)/i.resolution); cy = int((y-i.origin.position.y)/i.resolution)
        if not (0 <= cx < i.width and 0 <= cy < i.height): continue
        c = g.data[cy*i.width+cx]
        worst = max(worst, c)
        if c >= 99: return (round(d, 2), worst)
    return (None, worst)
def npoints():
    """전방 0.3~1.3m, |y|<0.25, z 0.05~0.35 의 깊이점 수 (base_link)."""
    if 'pc' not in S: return -1
    m = S['pc']
    try: tr = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
    except Exception: return -1
    off = {f.name: f.offset for f in m.fields}; step = m.point_step
    raw = np.frombuffer(m.data, dtype=np.uint8).reshape(-1, step)
    xyz = np.stack([raw[:, off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x','y','z')], axis=1)
    xyz = xyz[np.isfinite(xyz).all(axis=1)]
    q = tr.rotation; w, x, y, z = q.w, q.x, q.y, q.z
    R = np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    P = xyz @ R.T + np.array([tr.translation.x, tr.translation.y, tr.translation.z])
    return int(np.sum((P[:,0]>0.3)&(P[:,0]<1.3)&(np.abs(P[:,1])<0.25)&(P[:,2]>0.05)&(P[:,2]<0.35)))

t0 = time.time()
while time.time()-t0 < 15 and (pose_in('odom') is None or pose_in('map') is None or len(S) < 3):
    rclpy.spin_once(n, timeout_sec=0.1)
if pose_in('map') is None: print("TF 준비 실패"); raise SystemExit(1)
p0 = pose_in('odom')
print(f"전진 {DIST}m @ {VEL}m/s.  카메라 실명 예상: 카메라~물체 < 0.29m")
print("  t   이동   로컬 최근접(최대비용)  전역 최근접(최대비용)  깊이점")
cmd = Twist(); cmd.linear.x = VEL
t1 = time.time(); nxt = t1; log = t1
while time.time()-t1 < DIST/VEL + 3:
    rclpy.spin_once(n, timeout_sec=0.01)
    now = time.time()
    if now >= nxt: pub.publish(cmd); nxt += 0.05
    p = pose_in('odom')
    if p and math.hypot(p[0]-p0[0], p[1]-p0[1]) >= DIST: break
    if now >= log and p:
        log += 0.3
        ld, lw = nearest_block('lc', 'odom'); gd, gw = nearest_block('gc', 'map')
        print(f"{now-t1:5.1f} {math.hypot(p[0]-p0[0],p[1]-p0[1]):+.3f}   "
              f"{str(ld):>5} ({str(lw):>3})        {str(gd):>5} ({str(gw):>3})       {npoints():5d}", flush=True)
for _ in range(20): pub.publish(Twist()); rclpy.spin_once(n, timeout_sec=0.03)
print("\n최근접 = 전방 축에서 비용 ≥99 인 가장 가까운 거리(m). None = 1.3m 까지 막힘 없음.")
print("접근하며 이 값이 계속 줄어들면 장애물 유지, 갑자기 None 이 되면 그 시점에 사라진 것.")
