#!/usr/bin/env python3
"""포인트클라우드를 point_step 스트라이드로 정확히 읽어 base_link 기준 장애물 점의 경계상자를 낸다.
(이전 job60f/60i 는 x,y,z 를 연속 배열로 잘못 읽었을 수 있음 → 여기서 재확인)"""
import rclpy, math, time, numpy as np, tf2_ros
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
rclpy.init(); n=Node('boxdim'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); got={}
n.create_subscription(PointCloud2,'/camera/camera/depth/color/points',lambda m: got.__setitem__('pc',m),qos_profile_sensor_data)
t=time.time(); tr=None
while time.time()-t<10 and ('pc' not in got or tr is None):
    rclpy.spin_once(n,timeout_sec=0.1)
    if 'pc' in got and tr is None:
        try: tr=buf.lookup_transform('base_link',got['pc'].header.frame_id,rclpy.time.Time()).transform
        except Exception: pass
if 'pc' not in got or tr is None: print("수신/TF 실패"); raise SystemExit
m=got['pc']; off={f.name:f.offset for f in m.fields}; step=m.point_step; N=m.width*m.height
raw=np.frombuffer(m.data,dtype=np.uint8).reshape(-1,step)
xyz=np.stack([raw[:,off[k]:off[k]+4].copy().view(np.float32).ravel() for k in ('x','y','z')],axis=1)
xyz=xyz[np.isfinite(xyz).all(axis=1)]
q=tr.rotation; w,x,y,z=q.w,q.x,q.y,q.z
R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
P=xyz@R.T+np.array([tr.translation.x,tr.translation.y,tr.translation.z])
print(f"점 {len(P)}  (point_step={step}, fields={list(off)})")
print(f"전체 z 범위 {P[:,2].min():+.2f}~{P[:,2].max():+.2f}, 바닥(z<0.06) {np.sum(P[:,2]<0.06)}개")
ob=P[(P[:,2]>=0.06)&(P[:,2]<0.40)&(P[:,0]>0.3)&(P[:,0]<1.45)&(np.abs(P[:,1])<0.9)]
print(f"\n장애물층(z 0.06~0.40, x 0.3~1.45) 점 {len(ob)}")
if len(ob):
    print(f"  x {ob[:,0].min():.2f}~{ob[:,0].max():.2f}  y {ob[:,1].min():+.2f}~{ob[:,1].max():+.2f}  z {ob[:,2].min():.2f}~{ob[:,2].max():.2f}")
    print("  y 히스토그램(5cm):")
    for y0 in np.arange(-0.9,0.9,0.1):
        c=np.sum((ob[:,1]>=y0)&(ob[:,1]<y0+0.1))
        if c: print(f"    y {y0:+.1f}~{y0+0.1:+.1f}: {c:5d}  x중앙 {np.median(ob[(ob[:,1]>=y0)&(ob[:,1]<y0+0.1)][:,0]):.2f}  z중앙 {np.median(ob[(ob[:,1]>=y0)&(ob[:,1]<y0+0.1)][:,2]):.2f}")
# 바닥이 z 0.06 을 넘는 거리 확인 (피치 오차 점검)
fl=P[(P[:,2]<0.20)&(P[:,0]>0.3)]
print("\n바닥 후보 z 의 거리별 중앙값 (피치 오차 점검):")
for x0 in np.arange(0.4,1.6,0.2):
    s=fl[(fl[:,0]>=x0)&(fl[:,0]<x0+0.2)]
    if len(s): print(f"  x {x0:.1f}~{x0+0.2:.1f}: z 5% {np.percentile(s[:,2],5):+.3f} 50% {np.percentile(s[:,2],50):+.3f} 95% {np.percentile(s[:,2],95):+.3f}  n={len(s)}")
