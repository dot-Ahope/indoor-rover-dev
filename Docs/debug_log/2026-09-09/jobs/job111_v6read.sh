#!/bin/bash
# -v6 로그 60초 수집 후 집계: 보드가 어떤 datawriter 로 몇 프레임 보냈는가 / agent 가 뭘 버렸는가
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 60초 수집 중 (동시에 토픽 수신량도 기록) ==="
S=$(wc -l < /tmp/agent_v6.log)
python3 - <<'PY' &
import rclpy, time
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, BatteryState
from diagnostic_msgs.msg import DiagnosticArray
rclpy.init(); n = Node('v6obs'); C = {'odom':0,'imu':0,'stat':0,'bat':0}
def mk(k):
    def cb(m): C[k] += 1
    return cb
n.create_subscription(Odometry, '/wheel_odom', mk('odom'), qos_profile_sensor_data)
n.create_subscription(Imu, '/imu/data_raw', mk('imu'), qos_profile_sensor_data)
n.create_subscription(DiagnosticArray, '/rover/status', mk('stat'), qos_profile_sensor_data)
n.create_subscription(BatteryState, '/battery', mk('bat'), qos_profile_sensor_data)
print("   구간     odom   imu  stat  bat", flush=True)
for b in range(12):
    base = dict(C); tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    print("  %3.0f-%3.0fs %6.2f %5.2f %5.2f %5.2f"
          % (b*5, b*5+5, (C['odom']-base['odom'])/el, (C['imu']-base['imu'])/el,
             (C['stat']-base['stat'])/el, (C['bat']-base['bat'])/el), flush=True)
rclpy.shutdown()
PY
wait
E=$(wc -l < /tmp/agent_v6.log)
echo ""
echo "=== 로그 증가: $((E-S)) 줄 ==="
CLEAN=/tmp/v6_clean.log
sed -E 's/\x1b\[[0-9;]*m//g' /tmp/agent_v6.log | tail -n +$((S+1)) > $CLEAN
echo ""
echo "=== 로그 종류별 건수 (상위 15) ==="
grep -aoE '\| [a-z_]+ +\|' $CLEAN | tr -d '| ' | sort | uniq -c | sort -rn | head -15 | sed 's/^/  /'
echo ""
echo "=== datawriter 별 전송 건수 ==="
grep -a "write_data\|user_write\|SEND\|RECV" $CLEAN | grep -aoE "datawriter_id: 0x[0-9A-Fa-f]{3}" | sort | uniq -c | sed 's/^/  /'
echo ""
echo "=== 오류/버림 흔적 ==="
grep -aiE "error|wrong|invalid|discard|drop|bad|crc|out of|full|overflow|unknown|not found" $CLEAN | sed -E 's/^(.{0,150}).*/\1/' | sort | uniq -c | sort -rn | head -15 | sed 's/^/  /'
echo ""
echo "=== 세션/스트림 관련 ==="
grep -aiE "session|stream|heartbeat|acknack|fragment" $CLEAN | sed -E 's/^(.{0,140}).*/\1/' | sort | uniq -c | sort -rn | head -12 | sed 's/^/  /'
echo ""
echo "=== 원시 라인 샘플 (10줄) ==="
tail -400 $CLEAN | head -10 | sed -E 's/^(.{0,170}).*/\1/' | sed 's/^/  /'
