#!/bin/bash
# 10-08 §5 시험 전 확인(로버 안 움직임): 프로세스·정체 감시 모드·보드·로버 위치(map)·차체 중심 기준 라이다 최근접·방향별 최근접
for p in microros_agent rplidar realsense2_camera sensor_conditioner ekf_node slam_toolbox stuck_monitor controller_server; do printf "  %-20s %s\n" "$p" "$(pgrep -fc "$p")"; done
echo "  stuck shadow: $(timeout 10 ros2 param get /stuck_monitor shadow_mode 2>&1 | tail -1)"
echo "  wheel_odom: $(timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"
python3 - <<'PY'
import math, time, rclpy, tf2_ros
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
def yaw(q): return math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
rclpy.init(); n = Node('chk942'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n); sc = []
n.create_subscription(LaserScan, '/scan', lambda m: sc.append(m), qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 6: rclpy.spin_once(n, timeout_sec=0.1)
try:
    t = buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform; print('  로버 map (%.2f, %.2f) yaw %.0f°' % (t.translation.x, t.translation.y, math.degrees(yaw(t.rotation))))
    l = buf.lookup_transform('base_link', sc[-1].header.frame_id, rclpy.time.Time()).transform
    tx, ty, th = l.translation.x, l.translation.y, yaw(l.rotation); m = sc[-1]; sec = {}
    for i, r in enumerate(m.ranges):
        if not math.isfinite(r) or r < 0.15: continue
        a = m.angle_min + i * m.angle_increment + th; x, y = tx + r * math.cos(a), ty + r * math.sin(a); d = math.hypot(x, y)
        k = int(((math.degrees(math.atan2(y, x)) + 22.5) % 360) // 45); sec[k] = min(sec.get(k, 9), d)
    nm = ['앞', '앞왼', '왼', '뒤왼', '뒤', '뒤오', '오', '앞오']
    print('  차체 중심 기준 최근접(방향별): ' + ' · '.join('%s %.2f' % (nm[k], sec.get(k, 9)) for k in range(8)) + ' | 최소 %.2f m (필요 ≥ 0.85)' % min(sec.values()))
except Exception as e: print('  TF/스캔 실패', e)
rclpy.shutdown()
PY
