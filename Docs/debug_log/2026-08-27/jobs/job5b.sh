#!/bin/bash
# W4 슬립 재캘리브레이션 (자이로 기준, WT-600 게이지 0.245 반영 펌웨어). 접지 상태·사용자 입회.
# 각 회전: 정지1.5s → 회전 T초 → 정지2s. 자이로(광학 -y) 적분 vs /wheel_odom(원본) 적분 → factor.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
run_one() {  # $1=speed $2=dur $3=label
python3 - "$1" "$2" "$3" << 'PY'
import sys, time, math, subprocess, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
W=float(sys.argv[1]); T=float(sys.argv[2]); LBL=sys.argv[3]
class C(Node):
    def __init__(s):
        super().__init__('slip_cal'); s.g=[]; s.w=[]
        s.create_subscription(Imu,'/imu/data',lambda m:s.g.append((m.header.stamp.sec+m.header.stamp.nanosec*1e-9,-m.angular_velocity.y)),qos_profile_sensor_data)
        s.create_subscription(Odometry,'/wheel_odom',lambda m:s.w.append((m.header.stamp.sec+m.header.stamp.nanosec*1e-9,m.twist.twist.angular.z)),qos_profile_sensor_data)
def integ(v): return sum((v[i][0]-v[i-1][0])*0.5*(v[i][1]+v[i-1][1]) for i in range(1,len(v)))
rclpy.init(); n=C(); t0=time.time()
while time.time()<t0+1.5: rclpy.spin_once(n,timeout_sec=0.05)
pub=subprocess.Popen(['ros2','topic','pub','-r','10','-t',str(int(T*10)),'-w','1','/cmd_vel','geometry_msgs/msg/Twist','{angular: {z: %s}}'%W],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
while pub.poll() is None: rclpy.spin_once(n,timeout_sec=0.02)
subprocess.run(['ros2','topic','pub','-t','5','-r','10','-w','1','/cmd_vel','geometry_msgs/msg/Twist','{}'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
t1=time.time()
while time.time()<t1+2.0: rclpy.spin_once(n,timeout_sec=0.05)
gy=integ(n.g); wh=integ(n.w); wmax=max((abs(v) for _,v in n.w),default=0)
f=gy/wh if abs(wh)>1e-3 else float('nan')
print(f"[{LBL}] cmd={W:+.2f} x{T}s | gyro={math.degrees(gy):+7.2f}deg wheel={math.degrees(wh):+7.2f}deg | factor={f:.3f} @wheel|vyaw|~{wmax:.2f}")
n.destroy_node(); rclpy.shutdown()
PY
sleep 2
}
echo "=== W4 SLIP RECALIB (WT-600, gyro reference) ==="
run_one  0.3 4 "L-slow"
run_one  0.5 3 "L-fast"
run_one -0.3 4 "R-slow"
run_one -0.5 3 "R-fast"
echo "=== 종료 (모터 정지 확인) ==="
ros2 topic pub -t 5 -r 10 -w 1 /cmd_vel geometry_msgs/msg/Twist '{}' >/dev/null 2>&1
timeout 4 ros2 topic echo /odometry/filtered --once --field twist.twist.angular.z 2>/dev/null
