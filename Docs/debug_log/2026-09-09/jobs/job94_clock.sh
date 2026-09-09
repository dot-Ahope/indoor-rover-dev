#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 시스템 시계 ==="
timedatectl 2>/dev/null | sed 's/^/  /'
echo "--- 부팅 이후 시각 동기/스텝 이벤트 ---"
journalctl -b --no-pager 2>/dev/null | grep -aiE "time ?sync|systemd-timesyncd|chronyd|clock step|adjusting system clock|System clock|RTC" | tail -20
echo ""
echo "=== 토픽 발행률 (개별, 10초) ==="
printf "  %-22s " /wheel_odom;        timeout 12 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
printf "  %-22s " /odometry/filtered; timeout 12 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
echo ""
echo "=== 정지 상태 10초 동안 위치 변화 (모터 무지령) ==="
python3 - <<'PY'
import rclpy, time, math
from rclpy.node import Node
from nav_msgs.msg import Odometry
rclpy.init(); n = Node('drift')
S = {}
def mk(k):
    def cb(m):
        st = m.header.stamp.sec + m.header.stamp.nanosec*1e-9
        S.setdefault(k, []).append((time.time(), st, m.pose.pose.position.x, m.pose.pose.position.y,
                                   m.twist.twist.linear.x, m.twist.twist.angular.z))
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('w'), 20)
n.create_subscription(Odometry, '/odometry/filtered', mk('f'), 20)
t0 = time.time()
while time.time()-t0 < 10: rclpy.spin_once(n, timeout_sec=0.1)
now = time.time()
print("  ROS 시각(host time.time()) = %.3f" % now)
for k, name in (('w','/wheel_odom'), ('f','/odometry/filtered')):
    d = S.get(k, [])
    if not d:
        print("  %-20s 수신 0" % name); continue
    a, b = d[0], d[-1]
    print("  %-20s 수신 %d, x %.3f->%.3f (dx %+.3f), y %.3f->%.3f, |v| max %.3f, |w| max %.3f"
          % (name, len(d), a[2], b[2], b[2]-a[2], a[3], b[3],
             max(abs(r[4]) for r in d), max(abs(r[5]) for r in d)))
    print("       헤더 stamp 첫 %.3f 끝 %.3f (경과 %.3f s, 실제 %.3f s), host 대비 오프셋 %+.3f s"
          % (a[1], b[1], b[1]-a[1], b[0]-a[0], b[1]-b[0]))
rclpy.shutdown()
PY
