#!/bin/bash
# 세션 초기화(손 이동 후): EKF+slam 재시작(base/agent 유지) + 회전공간 판정. 로버 정지!
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
docker ps --format '{{.Names}}' | grep -q microros && echo "agent 유지됨(보드 RESET 불필요)" || echo "!! agent 없음"
pkill -f sensor_conditioner; pkill -f ekf_node; pkill -f slam_toolbox; pkill -f "slam.launch"; sleep 3
echo "=== EKF 재시작 (자이로 캘리브 ~10s, 정지!) ==="
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 16
grep -a "gyro bias\|not stationary" /tmp/ekf.log | tail -1
echo "=== slam 재시작 ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
echo "=== 검증 ==="
echo -n "  /odometry/filtered: "; timeout 5 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1
echo -n "  odom 원점: "; timeout 4 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aoE "x: [-0-9.e]+" | head -1
echo -n "  map->odom: "; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE "Translation" | head -1 || echo "미확보"
echo -n "  map->base_link: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE "Translation" | head -1 || echo "미확보"
echo "=== 공간 판정 (회전 스윕 반경 기준) ==="
python3 - << 'PY'
import math, numpy as np, rclpy, time
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMIN,XMAX,YMIN,YMAX=-0.25,0.25,-0.165,0.165
SWEEP=math.hypot(XMAX,YMAX)   # 중심~풋프린트 모서리 = 제자리회전 스윕 반경
rclpy.init(); n=rclpy.create_node('sp'); m=[None]
n.create_subscription(LaserScan,'/scan',lambda x:m.__setitem__(0,x),qos_profile_sensor_data)
t0=time.time()
while m[0] is None and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
r=np.array(m[0].ranges,np.float32); a=m[0].angle_min+m[0].angle_increment*np.arange(len(r))
ok=np.isfinite(r)&(r>0.05)&(r<12); th=a[ok]+LYAW
px=LX+r[ok]*np.cos(th); py=r[ok]*np.sin(th)
dc=np.hypot(px,py)                     # 로버 중심으로부터의 거리
mind=float(np.min(dc))
print(f"  스윕 반경(필요) = {SWEEP*100:.1f}cm, 가장 가까운 장애물(중심기준) = {mind*100:.0f}cm")
print(f"  회전 여유 = {(mind-SWEEP)*100:+.0f}cm → {'OK 회전 가능' if mind>SWEEP+0.05 else 'X 회전 불가(공간 부족)'}")
# 직진 경로여유(전/후)
band=np.abs(py)<=(YMAX+0.03)
f=px[band & (px>XMAX)]; b=px[band & (px<XMIN)]
F=(float(np.min(f))-XMAX)*100 if f.size else 999
B=(XMIN-float(np.max(b)))*100 if b.size else 999
print(f"  직진 경로여유: 전방 {F:.0f}cm / 후방 {B:.0f}cm")
side=float(np.min(np.abs(py)[np.abs(px)<=XMAX])) if (np.abs(px)<=XMAX).any() else 9
print(f"  최근접 측면 = {side*100:.0f}cm (참고)")
rclpy.shutdown()
PY
