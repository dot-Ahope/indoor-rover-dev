#!/bin/bash
# job170 의 TF 정지(t≈4.0, 절대시각 ≈1788943244) 전후 로그 조사
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== nav2 로그: 1788943235~1788943260 ==="
awk -F'[][]' '{for(i=1;i<=NF;i++) if($i ~ /^17889432[3-6][0-9]\./) {print; break}}' /tmp/nav2.log 2>/dev/null | tail -25 | cut -c1-165
echo ""
echo "=== sensors 로그: ekf/conditioner 경고 (전체 중 최근) ==="
grep -aiE "ekf|conditioner" /tmp/sensors.log 2>/dev/null | grep -aiE "warn|error|update rate|died|exception" | tail -10 | cut -c1-150
echo ""
echo "=== slam 로그 최근 ==="
grep -aiE "warn|error" /tmp/slam.log 2>/dev/null | tail -5 | cut -c1-150
echo ""
echo "=== 현재 TF 발행 주체별 ==="
timeout 8 ros2 topic info /tf --verbose 2>/dev/null | grep -aE "Node name|Publisher count" | head -12 | sed 's/^/  /'
echo ""
echo "=== 지금 EKF 주기 안정성 (20초, 1초 버킷) ==="
python3 - <<'PY'
import rclpy, time
from rclpy.node import Node
from nav_msgs.msg import Odometry
rclpy.init(); n=Node('ekfstab'); C=[0]
n.create_subscription(Odometry,'/odometry/filtered',lambda m: C.__setitem__(0,C[0]+1),10)
print("   초  수신")
for b in range(20):
    a=C[0]; t=time.time()
    while time.time()-t<1.0: rclpy.spin_once(n,timeout_sec=0.02)
    d=C[0]-a
    print("  %3d  %3d %s" % (b+1, d, "← 이상" if d<20 else ""))
rclpy.shutdown()
PY
