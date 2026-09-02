#!/bin/bash
# VX_SCALE 0.783 반영: 재빌드 → conditioner/EKF/slam 재시작 → 검증. 로버 정지!
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
cp /tmp/sensor_conditioner.py ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
echo "=== 재빌드 ==="
cd ~/ros2_ws && colcon build --packages-select rover_bringup 2>&1 | tail -2
source ~/ros2_ws/install/setup.bash
echo "=== EKF/slam 재시작 (자이로 캘리브 ~10s, 정지 유지!) ==="
pkill -f sensor_conditioner; pkill -f ekf_node; pkill -f slam_toolbox; pkill -f "slam.launch"; sleep 3
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf3.log 2>&1 &
sleep 15
grep -a "gyro bias\|not stationary" /tmp/ekf3.log | tail -1
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 10
echo "=== 검증 ==="
echo "  VX_SCALE: $(grep -a '^VX_SCALE' ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py)"
echo "  노드: $(ros2 node list 2>/dev/null | grep -E 'ekf|conditioner|slam' | tr '\n' ' ')"
echo -n "  /odometry/filtered: "; timeout 4 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo -n "  odom 원점: "; timeout 4 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aA2 "position:" | grep -aoE "x: [-0-9.e]+" | head -1
echo -n "  map->odom: "; timeout 5 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1
echo "=== 방향별 여유 ==="
python3 - << 'PY'
import math, numpy as np, rclpy, time
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
rclpy.init(); n=rclpy.create_node('cl'); m=[None]
n.create_subscription(LaserScan,'/scan',lambda x:m.__setitem__(0,x),qos_profile_sensor_data)
t0=time.time()
while m[0] is None and time.time()<t0+5: rclpy.spin_once(n,timeout_sec=0.1)
r=np.array(m[0].ranges,np.float32); a=m[0].angle_min+m[0].angle_increment*np.arange(len(r))
ok=np.isfinite(r)&(r>0.05)&(r<12); th=a[ok]+LYAW
px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
dx=np.maximum.reduce([XMIN-px,np.zeros_like(px),px-XMAX]); dy=np.maximum.reduce([YMIN-py,np.zeros_like(py),py-YMAX])
c=np.sqrt(dx*dx+dy*dy); ang=np.degrees(np.arctan2(py,px))
F=np.min(c[(ang>=-30)&(ang<30)])*100; B=np.min(c[(ang>=150)|(ang<-150)])*100
print(f"  전방 {F:.0f}cm / 후방 {B:.0f}cm → 추천 {'F(전진)' if F>B else 'B(후진)'}")
rclpy.shutdown()
PY
