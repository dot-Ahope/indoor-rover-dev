#!/usr/bin/env python3
"""mp9: 휠 목표가 1~9 mm/s(옛 펌웨어라면 버려졌을 구간)였던 순간 수와 그때 실제 휠 속도, /cmd_vel 최소 크기"""
import sys, rosbag2_py, re
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG = sys.argv[1]; G = float(sys.argv[2])
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
low = []; n = 0; cmds = []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9 - G
    if topic == '/rover/status':
        m = deserialize_message(data, get_message(types[topic])); n += 1
        kv = {k.key: k.value for s in m.status for k in s.values}
        for side in ('L', 'R'):
            d = dict(re.findall(r'(\w+)=(-?\d+)', kv.get(side, '')))
            tg, v = int(d.get('tgt', 0)), int(d.get('v', 0))
            if 0 < abs(tg) < 10: low.append((round(t, 1), side, tg, v))
    elif topic == '/cmd_vel' and t > 0:
        m = deserialize_message(data, get_message(types[topic])); cmds.append((t, m.linear.x, m.angular.z))
print('status 샘플 %d, 휠 목표 1~9 mm/s 인 샘플 %d' % (n, len(low)))
for x in low[:12]: print('  t=%5.1f %s tgt %+d mm/s  측정 %+d' % x)
act = [c for c in cmds if abs(c[1]) > 1e-4 or abs(c[2]) > 1e-4]
if act:
    mv = min(act, key=lambda c: abs(c[1]) + abs(c[2]) * 0.2215)
    print('비영 /cmd_vel %d 개, 가장 작은 명령 t=%.1f v %+.4f w %+.4f (안쪽 휠 %.1f mm/s)' % (len(act), mv[0], mv[1], mv[2], 1000 * min(abs(mv[1] - mv[2] * 0.2215), abs(mv[1] + mv[2] * 0.2215))))
