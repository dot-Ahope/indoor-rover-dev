#!/bin/bash
source /opt/ros/humble/setup.bash
cp /tmp/rover_src/rover_description/urdf/rover.urdf ~/ros2_ws/src/rover_description/urdf/rover.urdf
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_description 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
pkill -f robot_state_publisher 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_description description.launch.py > /tmp/rsp.log 2>&1 &
sleep 6
echo "===lidar_link TF yaw (0 기대)==="; timeout 5 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -aE "RPY \(degree\)" | head -1
echo "===참고: base_link 프레임 근거리 방향 (코너 정면+좌측 벽이면 근거리가 0°~+90° 아크여야 정상)==="
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
yaw=math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z)); bang=(np.degrees(ang+yaw)+180)%360-180
for c in range(-180,180,45):
    m=(bang>=c)&(bang<c+45)&np.isfinite(M)
    if m.sum()>=3:
        v=np.nanmedian(M[m]); t='벽' if v<1.0 else('트임' if v>2 else '')
        print(f"  base [{c:+4d}..{c+45:+4d}] {v:.2f}m {t}")
n.destroy_node(); rclpy.shutdown()
PY
echo "VERIFY_IN_FOXGLOVE"
