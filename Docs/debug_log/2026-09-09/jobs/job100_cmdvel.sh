#!/bin/bash
# 가설: 보드로 들어가는 /cmd_vel 수신 트래픽이 스핀 루프를 붕괴시킨다.
#   세션1: Nav2 기동(=cmd_vel 시작) 직후 wheel_odom 사망
#   세션2: job97 이 ①에서 중단 → Nav2 가 계속 살아있음 → 리셋 직후부터 붕괴
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== /cmd_vel 발행 주체와 주기 ==="
ros2 topic info /cmd_vel --verbose 2>/dev/null | grep -aE "Publisher count|Node name" | sed 's/^/  /'
printf "  /cmd_vel 주기: "; timeout 10 ros2 topic hz /cmd_vel 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
echo ""
echo "=== 살아있는 Nav2 노드 ==="
ros2 node list 2>/dev/null | grep -aE "controller_server|planner_server|bt_navigator|velocity_smoother|behavior_server|stuck" | sed 's/^/  /' || echo "  없음"
echo ""
echo "=== Nav2 종료 (cmd_vel 차단) ==="
pkill -f "navigation_launch\|controller_server\|planner_server\|bt_navigator\|behavior_server\|velocity_smoother\|smoother_server\|waypoint_follower\|lifecycle_manager_navigation\|stuck_monitor" 2>/dev/null
sleep 5
printf "  종료 후 /cmd_vel 주기: "; timeout 8 ros2 topic hz /cmd_vel 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행 (차단됨)"
echo ""
echo "=== cmd_vel 차단 상태에서 보드 토픽 주기 (20초) ==="
python3 - <<'PY'
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticArray
rclpy.init(); n = Node('c'); C = {'odom': 0, 'imu': 0, 'stat': 0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
t0 = time.time()
while time.time()-t0 < 20: rclpy.spin_once(n, timeout_sec=0.1)
el = time.time()-t0
for k, exp in (('odom', 29), ('imu', 29), ('stat', 5)):
    print("  %-6s %5.2f Hz  (기대 %d)" % (k, C[k]/el, exp))
rclpy.shutdown()
PY
