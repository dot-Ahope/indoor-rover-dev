#!/bin/bash
# 회전 슬립 계수 정밀 캘리브레이션 (자이로 기준). 인자: 각속도 지령(기본 0.3), 지속 초(기본 4)
# 결과: factor = 자이로 적분 yaw / 휠(원본) 적분 yaw  → sensor_conditioner SLIP_PTS 갱신에 사용
W=${1:-0.3}; T=${2:-4}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - "$W" "$T" << 'PY'
import sys, time, math, subprocess, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
W=float(sys.argv[1]); T=float(sys.argv[2])
class C(Node):
    def __init__(s):
        super().__init__('slip_cal'); s.g=[]; s.w=[]
        s.create_subscription(Imu,'/imu/data',lambda m: s.g.append((m.header.stamp.sec+m.header.stamp.nanosec*1e-9, -m.angular_velocity.y)),qos_profile_sensor_data)  # 광학 -y = 로봇 yaw
        s.create_subscription(Odometry,'/wheel_odom',lambda m: s.w.append((m.header.stamp.sec+m.header.stamp.nanosec*1e-9, m.twist.twist.angular.z)),qos_profile_sensor_data)
def integ(v):
    return sum((v[i][0]-v[i-1][0])*0.5*(v[i][1]+v[i-1][1]) for i in range(1,len(v)))
rclpy.init(); n=C()
t0=time.time()
while time.time()<t0+1.5: rclpy.spin_once(n,timeout_sec=0.05)   # 정지 기준선
n_msgs=int(T*10)
pub=subprocess.Popen(['ros2','topic','pub','-r','10','-t',str(n_msgs),'-w','1','/cmd_vel','geometry_msgs/msg/Twist','{angular: {z: %s}}'%W],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
while pub.poll() is None: rclpy.spin_once(n,timeout_sec=0.02)
subprocess.run(['ros2','topic','pub','-t','5','-r','10','-w','1','/cmd_vel','geometry_msgs/msg/Twist','{}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
t1=time.time()
while time.time()<t1+2.0: rclpy.spin_once(n,timeout_sec=0.05)   # 감속 구간 포함
gy=integ(n.g); wh=integ(n.w)
wmax=max((abs(v) for _,v in n.w),default=0); gmax=max((abs(v) for _,v in n.g),default=0)
print(f"cmd={W} rad/s x {T}s | gyro samples={len(n.g)} wheel samples={len(n.w)}")
print(f"gyro  yaw integral = {math.degrees(gy):+7.2f} deg  (peak {gmax:.3f} rad/s)")
print(f"wheel yaw integral = {math.degrees(wh):+7.2f} deg  (peak {wmax:.3f} rad/s, 원본·미보정)")
print(f"SLIP FACTOR = {gy/wh:.3f}  @ wheel|vyaw|≈{wmax:.2f} rad/s" if abs(wh)>1e-3 else "wheel integral ~0 — 회전 안 됨")
n.destroy_node(); rclpy.shutdown()
PY
