#!/bin/bash
# 09-30 §13: 매핑 중 로버가 지도 위에서 갑자기 점프 — 사후 조사(주행 없음, 읽기만).
#  1) 지금 map→odom / odom→base_link 값(점프가 SLAM 보정 쪽인지 EKF 쪽인지)
#  2) slam/sensors/stuck 로그의 경고·오류·루프 클로저 흔적, EKF 미달 횟수
#  3) 부하·메모리·프로세스 생존
echo "########## 1. 현재 TF (3 회, 1 s 간격) ##########"
python3 - <<'EOF' 2>&1 | grep -av "^\["
import time, math, rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
def yx(t):
    q = t.transform.rotation; tr = t.transform.translation
    return '(%+.3f, %+.3f) yaw %+.1f°' % (tr.x, tr.y, math.degrees(math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))))
rclpy.init(); n = Node('jump_chk2'); b = Buffer(); TransformListener(b, n)
t0 = time.time(); k = 1
while time.time() - t0 < 3.6:
    rclpy.spin_once(n, timeout_sec=0.05)
    if time.time() - t0 >= k:
        out = []
        for a, c in (('map', 'odom'), ('odom', 'base_link'), ('map', 'base_link')):
            try: out.append('%s→%s %s' % (a, c, yx(b.lookup_transform(a, c, rclpy.time.Time()))))
            except Exception as e: out.append('%s→%s 없음' % (a, c))
        print(' | '.join(out)); k += 1
EOF
echo "########## 2. 로그 ##########"
echo "-- slam.log 줄 수 $(wc -l < /tmp/slam.log), 경고/오류/루프 관련 마지막 40 줄:"
grep -aiE "warn|error|loop|clos|jump|fail|drop|reject|interp" /tmp/slam.log | tail -40
echo "-- slam.log 마지막 15 줄:"; tail -15 /tmp/slam.log
echo "-- sensors.log: EKF 미달 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회, ZUPT $(grep -ac ZUPT /tmp/sensors.log)건, 경고/오류 마지막 20 줄:"
grep -aiE "warn|error" /tmp/sensors.log | grep -av "Failed to meet" | tail -20
echo "-- EKF 미달 마지막 5 건:"; grep -a 'Failed to meet update rate' /tmp/sensors.log | tail -5
echo "-- stuck_monitor(nav2.log) 마지막 20 줄:"; tail -20 /tmp/nav2.log
echo "########## 3. 부하·메모리·프로세스 ##########"
echo "load $(cut -d' ' -f1-3 /proc/loadavg) | $(free -m | awk '/Mem/{print "mem used "$3" MB / avail "$7" MB"}')"
for p in slam_toolbox ekf_node sensor_conditioner rplidar realsense2_camera foxglove_bridge stuck_monitor joy_linux_node teleop_node scan_deskew; do printf "%s %s · " $p $(pgrep -fc $p); done; echo
ps -eo pid,etimes,pcpu,rss,comm --sort=-pcpu | head -12
