#!/usr/bin/env python3
"""포인트클라우드에서 base_link 기준 낮은 물체 탐색: z 0.06~0.40, |y|<0.6, x 0.2~2.0 의 점을 x 10cm 구간별로 집계."""
import rclpy, time, math, struct, numpy as np, tf2_ros
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
rclpy.init(); n=Node('pcbox'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); got={}
n.create_subscription(PointCloud2,'/camera/camera/depth/color/points',lambda m: got.__setitem__('pc',m),qos_profile_sensor_data)
t=time.time(); tr=None
while time.time()-t<10 and ('pc' not in got or tr is None):
    rclpy.spin_once(n,timeout_sec=0.1)
    if 'pc' in got and tr is None:
        try: tr=buf.lookup_transform('base_link',got['pc'].header.frame_id,rclpy.time.Time()).transform
        except Exception: pass
if 'pc' not in got or tr is None: print("수신/TF 실패"); raise SystemExit
m=got['pc']; off={f.name:f.offset for f in m.fields}; step=m.point_step
buf_=np.frombuffer(m.data,dtype=np.uint8); N=m.width*m.height
xyz=np.stack([np.frombuffer(m.data,dtype=np.float32,count=N,offset=off[k]) if step==12 else
              np.array([struct.unpack_from('f',m.data,i*step+off[k])[0] for i in range(N)]) for k in ('x','y','z')],axis=1)
q=tr.rotation; tx,ty,tz=tr.translation.x,tr.translation.y,tr.translation.z
# 쿼터니언 → 회전행렬
w,x,y,z=q.w,q.x,q.y,q.z
R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
P=xyz[np.isfinite(xyz).all(axis=1)]@R.T+np.array([tx,ty,tz])
print(f"점 {len(P)}  base_link 기준 z 범위 {P[:,2].min():.2f}~{P[:,2].max():.2f}")
sel=P[(P[:,0]>0.2)&(P[:,0]<2.0)&(np.abs(P[:,1])<0.6)]
print("x구간(m)  전체점  z<0.06(바닥)  0.06~0.40(장애물층)  장애물층 z중앙값  y중앙값")
for x0 in np.arange(0.2,2.0,0.1):
    s=sel[(sel[:,0]>=x0)&(sel[:,0]<x0+0.1)]
    if len(s)==0: continue
    ob=s[(s[:,2]>=0.06)&(s[:,2]<0.40)]; fl=s[s[:,2]<0.06]
    print(f"{x0:4.1f}-{x0+0.1:3.1f}  {len(s):5d}  {len(fl):6d}  {len(ob):8d}  {np.median(ob[:,2]) if len(ob) else float('nan'):8.3f}  {np.median(ob[:,1]) if len(ob) else float('nan'):+.2f}")
