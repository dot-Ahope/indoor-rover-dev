#!/usr/bin/env python3
import rclpy, time, math, numpy as np, tf2_ros
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
rclpy.init(); n=Node('zchk'); buf=tf2_ros.Buffer(); tl=tf2_ros.TransformListener(buf,n); got={}
n.create_subscription(PointCloud2,'/camera/camera/depth/color/points',lambda m: got.__setitem__('pc',m),qos_profile_sensor_data)
n.create_subscription(Odometry,'/odometry/filtered',lambda m: got.__setitem__('od',m),10)
t=time.time(); trs={}
while time.time()-t<10 and (len(got)<2 or len(trs)<2):
    rclpy.spin_once(n,timeout_sec=0.1)
    if 'pc' in got:
        for f in ('base_link','odom'):
            if f not in trs:
                try: trs[f]=buf.lookup_transform(f,got['pc'].header.frame_id,rclpy.time.Time()).transform
                except Exception: pass
od=got.get('od'); print(f"EKF pose z = {od.pose.pose.position.z:.4f}  (roll/pitch 유무 확인용 q={od.pose.pose.orientation.x:.3f},{od.pose.pose.orientation.y:.3f})" if od else "odom 없음")
m=got['pc']; off={f.name:f.offset for f in m.fields}; N=m.width*m.height
xyz=np.stack([np.frombuffer(m.data,dtype=np.float32,count=N,offset=off[k]) for k in ('x','y','z')],axis=1); xyz=xyz[np.isfinite(xyz).all(axis=1)]
def R(q):
    w,x,y,z=q.w,q.x,q.y,q.z
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
for f,tr in trs.items():
    P=xyz@R(tr.rotation).T+np.array([tr.translation.x,tr.translation.y,tr.translation.z])
    near=P[(P[:,0]>0.5)&(P[:,0]<1.4)&(np.abs(P[:,1])<0.3)] if f=='base_link' else P
    fl=near[near[:,2]<0.06]; ob=near[(near[:,2]>=0.06)&(near[:,2]<0.40)]
    print(f"[{f}] 변환 t=({tr.translation.x:.3f},{tr.translation.y:.3f},{tr.translation.z:.3f})  근접 0.5~1.4m 점 {len(near)}: z<0.06 {len(fl)}개(z중앙값 {np.median(fl[:,2]) if len(fl) else float('nan'):+.3f})  0.06~0.40 {len(ob)}개(z중앙값 {np.median(ob[:,2]) if len(ob) else float('nan'):+.3f})")
    if f=='odom':
        near=P[(np.hypot(P[:,0]-trs['odom'].translation.x, P[:,1]-trs['odom'].translation.y)<1.6)]
        print(f"[odom] 반경1.6m 점 z 분포: 5% {np.percentile(near[:,2],5):+.3f} 50% {np.percentile(near[:,2],50):+.3f} 95% {np.percentile(near[:,2],95):+.3f}")
