#!/bin/bash
# 벽 마주보기 검증: 정지 스캔, base_link 프레임 최근접 방향 = 벽 = 정면이어야 함
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
import tf2_ros
class A(Node):
    def __init__(s):
        super().__init__('a'); s.acc=[]; s.m=None
        s.buf=tf2_ros.Buffer(); tf2_ros.TransformListener(s.buf,s)
        s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment,msg.header.frame_id)
rclpy.init(); n=A(); t0=time.time()
while time.time()<t0+4: rclpy.spin_once(n,timeout_sec=0.2)
if not n.acc: print("NO_SCAN"); raise SystemExit
M=np.nanmedian(np.vstack([r for r in n.acc if len(r)==len(n.acc[0])]),axis=0)
a0,ai,fid=n.m; ang=a0+ai*np.arange(len(M))
tf=n.buf.lookup_transform('base_link',fid,rclpy.time.Time()); q=tf.transform.rotation
yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
bang=(np.degrees(ang+yaw)+180)%360-180
print(f"lidar→base_link yaw={math.degrees(yaw):.0f}deg. base_link 30deg bin 중앙거리(가까울수록 벽):")
best=(None,99)
for c in range(-180,180,30):
    m=(bang>=c)&(bang<c+30)&np.isfinite(M)
    if m.sum()<3: continue
    v=np.nanmedian(M[m])
    if v<best[1]: best=(c+15,v)
    print(f"  [{c:+4d}..{c+30:+4d}]  {v:5.2f} m  {'#'*int(min(v,4)*8)}")
b=best[0]; d='전방✓(정렬 정상)' if abs(b)<45 else('후방✗(yaw 반대 → 되돌려야)' if abs(b)>135 else('좌✗' if b>0 else '우✗'))
print(f"\n=> 최근접(벽) 방향 = {best[0]:+d} deg ({best[1]:.2f}m) → 로버 기준 {d}")
print("   (벽을 정면에 뒀는데 후방으로 나오면 yaw 되돌림, 좌/우로 나오면 ±90 보정 필요)")
n.destroy_node(); rclpy.shutdown()
PY
