#!/bin/bash
# 현재 배포 TF(yaw=π)로 스캔을 base_link 프레임 변환 → 정면벽(800mm) base~0°, 좌측벽(325mm) base~+90° 확인
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 배포 TF ==="; timeout 5 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -aE "RPY \(degree\)" | head -1
echo "=== /tf_static 발행자 수(중복=stale 원인) ==="; ros2 topic info /tf_static 2>/dev/null | grep -E "Publisher count"
python3 - << 'PY'
import numpy as np, time, math, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
import tf2_ros
class A(Node):
    def __init__(s):
        super().__init__('a'); s.acc=[]; s.m=None; s.buf=tf2_ros.Buffer(); tf2_ros.TransformListener(s.buf,s)
        s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,msg): r=np.array(msg.ranges,np.float32); r[~np.isfinite(r)]=np.nan; s.acc.append(r); s.m=(msg.angle_min,msg.angle_increment,msg.header.frame_id)
rclpy.init(); n=A(); t0=time.time()
while time.time()<t0+4: rclpy.spin_once(n,timeout_sec=0.2)
M=np.nanmedian(np.vstack([r for r in n.acc if len(r)==len(n.acc[0])]),axis=0)
a0,ai,fid=n.m; ang=a0+ai*np.arange(len(M))
tf=n.buf.lookup_transform('base_link',fid,rclpy.time.Time()); q=tf.transform.rotation
yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
bang=(np.degrees(ang+yaw)+180)%360-180
def band(lo,hi,label):
    m=np.isfinite(M)&(M>=lo)&(M<hi)
    if m.sum()<3: print(f"  {label}: 검출실패"); return
    a=bang[m]; cx=np.sum(np.cos(np.radians(a))); cy=np.sum(np.sin(np.radians(a)))
    c=math.degrees(math.atan2(cy,cx))
    d={'front':'정면(+x)','left':'좌측(+y)','right':'우측(-y)','rear':'후방(-x)'}
    key='front' if abs(c)<45 else('left' if 45<=c<135 else('rear' if abs(c)>=135 else 'right'))
    print(f"  {label}: base_link θ={c:+.0f}deg → {d[key]}")
print(f"base_link 프레임(yaw={math.degrees(yaw):.0f}°) 벽 위치:")
band(0.25,0.45,"좌측벽(325mm) [정답=좌측+90°]")
band(0.65,0.95,"정면벽(800mm) [정답=정면0°]")
n.destroy_node(); rclpy.shutdown()
PY
