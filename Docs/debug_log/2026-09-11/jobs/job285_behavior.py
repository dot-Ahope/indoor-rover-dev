#!/usr/bin/env python3
"""behavior_server 의 'Collision Ahead' 즉시 실패 원인 (2026-09-11).
   costmap_raw 둘레 최대 253 인데 실패 → 비용이 아니라 예외 경로 의심.
   1) nav2.log 의 ERROR/예외 문구  2) behavior_server 파라미터
   3) /local_costmap/published_footprint 폴리곤을 costmap_raw 위에서 Bresenham 으로 전 셀 순회(= FootprintCollisionChecker 와 동일)"""
import subprocess, math, time, rclpy, tf2_ros
from rclpy.node import Node
from nav2_msgs.msg import Costmap
from geometry_msgs.msg import PolygonStamped
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True, executable='/bin/bash').stdout
SRC="source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; "
print("=== 1) nav2.log 예외/오류 (behavior 관련) ===")
print(sh("grep -aE 'ERROR|Exception|Off Grid|not available|Footprint|footprint' /tmp/nav2.log | grep -aiE 'behavior|collision|footprint|costmap' | tail -8 | cut -c1-170"))
print("=== 2) behavior_server 파라미터 ===")
for p in ('global_frame','robot_base_frame','transform_tolerance','local_costmap_topic','local_footprint_topic','simulate_ahead_time','cycle_frequency'):
    v=sh(SRC+f"timeout 6 ros2 param get /behavior_server {p} 2>/dev/null").strip(); print(f"  {p}: {v.split('is:')[-1].strip() if 'is:' in v else v or '?'}")
print("  published_footprint 발행: "+sh(SRC+"timeout 6 ros2 topic info /local_costmap/published_footprint 2>/dev/null | tr '\n' ' '").strip())
print("  costmap_raw QoS: "+sh(SRC+"timeout 8 ros2 topic info /local_costmap/costmap_raw --verbose 2>/dev/null | grep -aE 'Reliability|Durability' | head -2 | tr '\n' ' '").strip())
print("=== 3) 발행 footprint 폴리곤 × costmap_raw Bresenham 순회 ===")
rclpy.init(); n=Node('bh285'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); S={}
qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(Costmap,'/local_costmap/costmap_raw',lambda m:S.__setitem__('c',m),qos)
n.create_subscription(PolygonStamped,'/local_costmap/published_footprint',lambda m:S.__setitem__('f',m),qos)
n.create_subscription(PolygonStamped,'/local_costmap/published_footprint',lambda m:S.__setitem__('f2',m),10)
t0=time.time()
while time.time()-t0<15 and ('c' not in S or ('f' not in S and 'f2' not in S)): rclpy.spin_once(n,timeout_sec=0.1)
c=S.get('c'); f=S.get('f') or S.get('f2')
print("  costmap_raw 수신:", c is not None, "| published_footprint 수신:", f is not None, "(TL:", 'f' in S, "/ 기본QoS:", 'f2' in S, ")")
if c is None or f is None: raise SystemExit(0)
md=c.metadata; res=md.resolution; ox,oy=md.origin.position.x,md.origin.position.y
pts=[(p.x,p.y) for p in f.polygon.points]; print("  footprint frame %s, 점 %d개: %s"%(f.header.frame_id,len(pts),[(round(x,2),round(y,2)) for x in [0] for x,y in pts]))
def w2m(x,y):
    i=int((x-ox)/res); j=int((y-oy)/res)
    return (i,j) if (0<=i<md.size_x and 0<=j<md.size_y) else None
def line_cells(a,b):
    x0,y0=a; x1,y1=b; dx=abs(x1-x0); dy=-abs(y1-y0); sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1; err=dx+dy; out=[]
    while True:
        out.append((x0,y0))
        if x0==x1 and y0==y1: break
        e2=2*err
        if e2>=dy: err+=dy; x0+=sx
        if e2<=dx: err+=dx; y0+=sy
    return out
def footprint_cost(poly):
    cells=[w2m(x,y) for x,y in poly]
    if any(cc is None for cc in cells): return 254, 'OFF-GRID'
    best=(-1,None)
    for k in range(len(cells)):
        for (i,j) in line_cells(cells[k],cells[(k+1)%len(cells)]):
            v=c.data[j*md.size_x+i]
            if v>best[0]: best=(v,(i,j))
    return best
# TF 대기 (버퍼가 odom->base 를 받을 때까지)
tw=time.time(); T={}
while time.time()-tw<15:
    try:
        for fr in ('odom','map'): T[fr]=buf.lookup_transform(fr,'base_link',rclpy.time.Time()).transform
        break
    except Exception: rclpy.spin_once(n,timeout_sec=0.1)
if len(T)<2: print("  TF 실패"); raise SystemExit(0)
HL,HW,PAD=0.25,0.165,0.05; L,W=HL+PAD,HW+PAD; FP=[(L,W),(L,-W),(-L,-W),(-L,W)]
def pose_of(tr):
    q=tr.rotation; return tr.translation.x,tr.translation.y,math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
print("  map->odom 지금: %s"%sh(SRC+"timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -a Translation | head -1").strip())
print("  ※ behavior_server 는 global_frame(=map) 자세로 footprint 를 만들어 odom 프레임 costmap_raw 위에서 검사한다.")
print("     같은 footprint 를 (a) odom 자세로 놓았을 때 vs (b) map 자세로 놓았을 때(=behavior 가 실제로 하는 것):")
for label,fr in (('(a) odom 자세 — 올바름','odom'),('(b) map 자세 — behavior_server 현재','map')):
    x,y,yaw=pose_of(T[fr]); co,si=math.cos(yaw),math.sin(yaw)
    row=[]
    for d in (0.0,0.05,0.10,0.15,-0.05,-0.10,-0.15):
        poly=[(x+(d+fx)*co-fy*si, y+(d+fx)*si+fy*co) for fx,fy in FP]
        v,where=footprint_cost(poly); row.append("%+.2f:%3d%s"%(d,v,'!' if v>=254 else ''))
    print("  %-30s 로버 (%.3f, %.3f) | 이동별 둘레 최대: %s"%(label,x,y,'  '.join(row)))
