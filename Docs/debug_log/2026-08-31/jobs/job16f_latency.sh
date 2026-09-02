#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "use_sim_time 파라미터 확인:"
for nd in /ekf_filter_node /rplidar_node /slam_toolbox /scan_deskew; do
  echo -n "  $nd: "; ros2 param get $nd use_sim_time 2>/dev/null | tr '\n' ' '; echo
done
echo ""
echo "=== 콜백 내 실측 지연 (수신시각 - stamp), 토픽별 평균 ==="
python3 - << 'PY'
import rclpy, time
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, LaserScan
rclpy.init(); n=rclpy.create_node('lat')
acc={}
def mk(topic,typ):
    acc[topic]=[]
    def cb(m):
        now=n.get_clock().now().nanoseconds*1e-9
        st=m.header.stamp.sec+m.header.stamp.nanosec*1e-9
        if len(acc[topic])<40: acc[topic].append(now-st)
    n.create_subscription(typ,topic,cb,qos_profile_sensor_data)
for t,ty in [('/wheel_odom',Odometry),('/camera/camera/imu',Imu),('/odometry/filtered',Odometry),('/scan_raw',LaserScan),('/scan',LaserScan)]:
    mk(t,ty)
t0=time.time()
while time.time()<t0+5: rclpy.spin_once(n,timeout_sec=0.05)
import statistics as st
for k in ['/wheel_odom','/camera/camera/imu','/odometry/filtered','/scan_raw','/scan']:
    v=acc[k]
    if v: print(f"  {k:26s} n={len(v):2d}  지연 평균={st.mean(v)*1000:7.1f}ms  최대={max(v)*1000:7.1f}ms  최소={min(v)*1000:7.1f}ms")
    else: print(f"  {k:26s} (미수신)")
rclpy.shutdown()
PY
