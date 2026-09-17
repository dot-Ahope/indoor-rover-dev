#!/usr/bin/env python3
"""mp8: /rover/status 키-값 전체를 시간순으로(값이 바뀔 때만) + 같은 시각 cmd/wheel 속도"""
import sys, rosbag2_py, bisect
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG = sys.argv[1]; G = float(sys.argv[2])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
st, cmd, wo = [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9 - G
    if topic == '/rover/status': st.append((t, deserialize_message(data, get_message(types[topic]))))
    elif topic == '/cmd_vel': m = deserialize_message(data, get_message(types[topic])); cmd.append((t, m.linear.x, m.angular.z))
    elif topic == '/wheel_odom': m = deserialize_message(data, get_message(types[topic])); wo.append((t, m.twist.twist.linear.x))
ct = [c[0] for c in cmd]; wt = [w[0] for w in wo]
print('status 필드:', [kv.key for s in st[0][1].status for kv in s.values])
prev = None
for t, m in st:
    kv = tuple((k.key, k.value) for s in m.status for k in s.values if k.key not in ('uptime_ms', 'rx_count', 'tx_count', 'cmd_count', 'seq'))
    if kv != prev or int(t) in (36, 38, 45, 70):
        i = bisect.bisect_right(ct, t) - 1; j = bisect.bisect_right(wt, t) - 1
        print('%6.1f  cmd %+.3f/%+.3f wheel %+.4f | %s' % (t, cmd[i][1] if i >= 0 else 0, cmd[i][2] if i >= 0 else 0, wo[j][1] if j >= 0 else 0, ' '.join('%s=%s' % x for x in kv)[:230]))
        prev = kv
