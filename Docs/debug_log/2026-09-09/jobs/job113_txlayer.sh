#!/bin/bash
# 전송 계층 계측: wc=write 호출, wb=gState busy 로 버림, wh=HAL 오류, wt=세마포어 타임아웃, wl=최대 len
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
python3 - <<'PY'
import rclpy, time, re
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
from diagnostic_msgs.msg import DiagnosticArray
rclpy.init(); n = Node('txl'); C = {'odom': 0}; TX = {}
n.create_subscription(Odometry, '/wheel_odom', lambda m: C.__setitem__('odom', C['odom']+1), qos_profile_sensor_data)
def cb(m):
    for st in m.status:
        for kv in st.values:
            if kv.key == 'TX':
                TX.update({k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', kv.value)})
n.create_subscription(DiagnosticArray, '/rover/status', cb, qos_profile_sensor_data)
t0 = time.time()
while time.time()-t0 < 15 and 'wc' not in TX: rclpy.spin_once(n, timeout_sec=0.1)
if 'wc' not in TX: print("TX 필드 없음:", TX); raise SystemExit(1)
print("초기:", TX); print("")
print("   구간 | odom시도  write호출  busy버림  HAL오류  세마포타임아웃 | odom수신Hz | 최대len")
prev = dict(TX); pc = C['odom']
for b in range(14):
    tb = time.time()
    while time.time()-tb < 5.0: rclpy.spin_once(n, timeout_sec=0.02)
    el = time.time()-tb
    d = {k: (TX.get(k,0)-prev.get(k,0))/el for k in ('ot','wc','wb','wh','wt')}
    r = (C['odom']-pc)/el
    prev = dict(TX); pc = C['odom']
    print("  %3.0fs | %8.1f %10.1f %9.1f %8.1f %14.1f | %10.1f | %d"
          % (b*5+5, d['ot'], d['wc'], d['wb'], d['wh'], d['wt'], r, TX.get('wl',0)), flush=True)
rclpy.shutdown()
PY
