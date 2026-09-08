#!/usr/bin/env python3
"""상자를 검출해 map 좌표로 바꾸고 로컬·전역 코스트맵 비용과 깊이점 z 분포를 한 번 출력(주행 없음)."""
import math, sys, time, rclpy, tf2_ros
import numpy as np
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n=Node('probe'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); S={}
qos=QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
n.create_subscription(PointCloud2,'/camera/camera/depth/color/points',lambda m:S.__setitem__('pc',m),qos_profile_sensor_data)
n.create_subscription(OccupancyGrid,'/local_costmap/costmap',lambda m:S.__setitem__('lc',m),qos)
n.create_subscription(OccupancyGrid,'/global_costmap/costmap',lambda m:S.__setitem__('gc',m),qos)
def Rq(q):
    w,x,y,z=q.w,q.x,q.y,q.z
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def cloud(fr):
    m=S['pc']
    try: tr=buf.lookup_transform(fr,m.header.frame_id,rclpy.time.Time()).transform
    except Exception: return None
    off={f.name:f.offset for f in m.fields}; step=m.point_step
    raw=np.frombuffer(m.data,dtype=np.uint8).reshape(-1,step)
    xyz=np.stack([raw[:,off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x','y','z')],axis=1)
    xyz=xyz[np.isfinite(xyz).all(axis=1)]
    return xyz@Rq(tr.rotation).T+np.array([tr.translation.x,tr.translation.y,tr.translation.z])
def cost(k,x,y):
    if k not in S: return 'NA'
    g=S[k]; i=g.info
    cx=int((x-i.origin.position.x)/i.resolution); cy=int((y-i.origin.position.y)/i.resolution)
    return g.data[cy*i.width+cx] if 0<=cx<i.width and 0<=cy<i.height else 'OOB'
def tf_ready():
    if 'pc' not in S: return False
    try:
        buf.lookup_transform('base_link', S['pc'].header.frame_id, rclpy.time.Time())
        buf.lookup_transform('map', S['pc'].header.frame_id, rclpy.time.Time())
        return True
    except Exception: return False
# ⚠ 메시지 수신만 기다리면 TF 버퍼가 비어 lookup 이 실패한다(09-08 실수) → TF 준비까지 대기
t=time.time()
while time.time()-t<15 and not (len(S)>=3 and tf_ready()): rclpy.spin_once(n,timeout_sec=0.1)
if 'pc' not in S: print("포인트클라우드 없음"); raise SystemExit(1)
if not tf_ready(): print("TF 준비 실패(15s)"); raise SystemExit(1)
B=cloud('base_link'); M=cloud('map')
if B is None or M is None: print("TF 실패"); raise SystemExit(1)
sel=(B[:,2]>=0.04)&(B[:,2]<0.35)&(B[:,0]>0.4)&(B[:,0]<1.3)&(np.abs(B[:,1])<0.4)
if sel.sum()<30: print(f"상자 후보 부족 {sel.sum()}"); raise SystemExit(1)
bxl=B[sel]; bxm=M[sel]
BX,BY=float(np.median(bxm[:,0])),float(np.median(bxm[:,1]))
print(f"상자: base_link ({np.median(bxl[:,0]):.2f},{np.median(bxl[:,1]):+.2f}) / map ({BX:.2f},{BY:+.2f})  점 {sel.sum()}")
print(f"  base_link z: 5% {np.percentile(bxl[:,2],5):.3f} 50% {np.percentile(bxl[:,2],50):.3f} 95% {np.percentile(bxl[:,2],95):.3f}")
print(f"  map       z: 5% {np.percentile(bxm[:,2],5):.3f} 50% {np.percentile(bxm[:,2],50):.3f} 95% {np.percentile(bxm[:,2],95):.3f}")
print(f"  비용  로컬={cost('lc',BX,BY)}  전역={cost('gc',BX,BY)}")
