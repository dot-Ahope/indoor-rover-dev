#!/bin/bash
# 리셋 후 세션 확인 + slam 재시작(깨끗한 맵) + 회전 전 시작 여유(풋프린트 실거리) 측정
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===세션==="
echo -n "wheel_odom: "; timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo -n "battery: "; timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NONE
echo -n "imu_data_raw: "; timeout 5 ros2 topic hz /imu/data_raw 2>&1 | grep -aE "average|does not" | tail -1
echo "===slam 재시작(맵 초기화)==="
pkill -f slam_toolbox 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
ros2 node list | grep -q slam_toolbox && echo "slam OK" || echo NO_SLAM
echo "===시작 여유(로버 외곽↔벽 실거리) 측정==="
python3 - << 'PY'
import math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
class A(Node):
    def __init__(s): super().__init__('a'); s.c=None; s.create_subscription(LaserScan,'/scan',s.cb,qos_profile_sensor_data)
    def cb(s,m):
        r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r)); ok=np.isfinite(r)&(r>0.05)
        if ok.sum():
            th=a[ok]+LYAW; px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
            dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
            d=np.sqrt(dx*dx+dy*dy); i=int(np.argmin(d)); s.c=(float(d[i]*100),math.degrees(a[ok][i]),float(r[ok][i]))
rclpy.init(); n=A(); t0=time.time()
while n.c is None and time.time()<t0+4: rclpy.spin_once(n,timeout_sec=0.2)
if n.c: print(f"  최소 로버-벽 실거리 = {n.c[0]:.1f} cm  (raw θ={n.c[1]:+.0f}deg, 벽거리 {n.c[2]:.2f}m)")
else: print("  NO_SCAN")
# 360도 회전 안전성 예측: 모서리 반경 0.30m, LiDAR 스윙 0.15m 감안 필요 여유 ~35cm
print("  360도 안전 기준: 시작 여유 >= 30cm 권장 (모서리 스윙 여유 포함)")
n.destroy_node(); rclpy.shutdown()
PY
