#!/usr/bin/env python3
"""10-01 §8.15: f2a6 bag → map 위 로버 궤적(0.5 s), /plan 들(10 s 마다 1 개), 명령·휠 속도 → CSV 3 개(/tmp/f2a6_*.csv)."""
import sys, math, numpy as np, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=sys.argv[1], storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
mo, ob, plans, cmd = [], [], [], []
last_plan_t = 0
while r.has_next():
    tp, data, ts = r.read_next(); t = ts * 1e-9
    if tp == '/tf':
        for x in deserialize_message(data, get_message(types[tp])).transforms:
            k = (x.header.frame_id, x.child_frame_id); v = (t, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation))
            if k == ('map', 'odom'): mo.append(v)
            elif k == ('odom', 'base_link'): ob.append(v)
    elif tp == '/plan' and t - last_plan_t > 5:
        m = deserialize_message(data, get_message(types[tp])); last_plan_t = t
        for i, p in enumerate(m.poses[::3]): plans.append((t, i, p.pose.position.x, p.pose.position.y))
    elif tp == '/cmd_vel':
        m = deserialize_message(data, get_message(types[tp])); cmd.append((t, m.linear.x, m.angular.z))
mo, ob = np.array(mo), np.array(ob)
with open('/tmp/f2a6_traj.csv', 'w') as f:
    for t in np.arange(ob[0, 0], ob[-1, 0], 0.5):
        i = np.searchsorted(ob[:, 0], t) - 1; j = max(np.searchsorted(mo[:, 0], t) - 1, 0)
        ox, oy, oth = ob[i, 1:]; mx, my, mth = mo[j, 1:]; c, s = math.cos(mth), math.sin(mth)
        f.write('%.2f,%.3f,%.3f,%.3f\n' % (t, mx + c * ox - s * oy, my + s * ox + c * oy, mth + oth))
with open('/tmp/f2a6_plans.csv', 'w') as f:
    for p in plans: f.write('%.2f,%d,%.3f,%.3f\n' % p)
with open('/tmp/f2a6_cmd.csv', 'w') as f:
    for c in cmd: f.write('%.2f,%.3f,%.3f\n' % c)
print('궤적 %d, 경로 점 %d, 명령 %d' % (int((ob[-1, 0] - ob[0, 0]) / 0.5), len(plans), len(cmd)))
