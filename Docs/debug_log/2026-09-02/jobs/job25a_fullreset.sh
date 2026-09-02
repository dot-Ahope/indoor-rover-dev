#!/bin/bash
# 손 이동 후 전체 재초기화: Nav2 종료 → EKF → slam → Nav2 순. base/agent 유지.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== Nav2 종료 (프레임 재설정 전) ==="
pkill -f "navigation_launch|controller_server|planner_server|bt_navigator|behavior_server|velocity_smoother|smoother_server|waypoint_follower|lifecycle_manager_navigation" 2>/dev/null; sleep 3
echo "=== EKF 재시작 (자이로 캘리브 ~10s, 정지!) ==="
pkill -f sensor_conditioner; pkill -f ekf_node; pkill -f slam_toolbox; pkill -f "slam.launch"; sleep 3
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 16
grep -a "gyro bias\|not stationary" /tmp/ekf.log | tail -1
echo "=== slam 재시작 ==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
echo -n "  map->base_link: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -aE "Translation" | head -1 || echo "미확보"
echo "=== Nav2 재기동 ==="
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 25
echo "  lifecycle:"
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother; do
  printf "    %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo -n "  local_costmap: "; timeout 6 ros2 topic hz /local_costmap/costmap 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1 || echo "무발행"
echo ""
echo "=== 공간 판정 (회전 목표용) ==="
python3 - << 'PY'
import math, numpy as np, rclpy, time
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
LX,LYAW=0.152,math.pi; XMAX,YMAX=0.25,0.165; SWEEP=math.hypot(XMAX,YMAX)
rclpy.init(); n=rclpy.create_node('sp'); acc=[]
n.create_subscription(LaserScan,'/scan',lambda x: acc.append(x) if len(acc)<5 else None,qos_profile_sensor_data)
t0=time.time()
while len(acc)<5 and time.time()<t0+6: rclpy.spin_once(n,timeout_sec=0.1)
PX=[];PY=[]
for m in acc:
    r=np.array(m.ranges,np.float32); a=m.angle_min+m.angle_increment*np.arange(len(r))
    ok=np.isfinite(r)&(r>0.05)&(r<12); th=a[ok]+LYAW
    PX.append(LX+r[ok]*np.cos(th)); PY.append(r[ok]*np.sin(th))
px=np.concatenate(PX); py=np.concatenate(PY); dc=np.hypot(px,py); ang=np.degrees(np.arctan2(py,px))
print(f"  회전 스윕반경 {SWEEP*100:.0f}cm / 최근접 {np.min(dc)*100:.0f}cm → {'회전 OK' if np.min(dc)>SWEEP+0.05 else '회전 불가'}")
for nm,c in [('정면',0),('좌(90)',90),('후면',180),('우(-90)',-90)]:
    d=np.abs(((ang-c+180)%360)-180); mk=d<20
    if mk.any(): print(f"  {nm:>8s} 방향 여유: {np.min(dc[mk])*100:5.0f}cm")
rclpy.shutdown()
PY
