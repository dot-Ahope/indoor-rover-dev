#!/usr/bin/env python3
"""10-02 §2: f2a12 bag 을 도메인 42·sim time·1 배속으로 통째 재생해 localization_slam_toolbox_node 에 먹이고,
   재생 map→odom 에 1.33 m 점프(라이브 +278.4 s)가 다시 생기는지 본다. 라이브 기록 map→odom 도 bag 에서 같이 읽어 비교.
   인자: BAG OUT_NPZ   (slam 노드는 래퍼가 먼저 띄움)"""
import sys, math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg import TFMessage
from rclpy.parameter import Parameter

def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
BAG, OUT = sys.argv[1], sys.argv[2]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
msgs = []; live = []; t0b = None
while r.has_next():
    tp, data, ts = r.read_next()
    if t0b is None: t0b = ts
    if tp not in ('/scan', '/tf', '/tf_static'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        keep = []
        for x in m.transforms:
            if x.header.frame_id == 'map' and x.child_frame_id == 'odom':
                live.append(((ts - t0b) * 1e-9, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation)))
            else: keep.append(x)
        if not keep: continue
        m.transforms = keep
    msgs.append((ts, tp, m))
print('재생 전체 %.0f s(1 배속), 메시지 %d, 라이브 map→odom %d' % ((msgs[-1][0] - t0b) * 1e-9, len(msgs), len(live)), flush=True)
rclpy.init()
n = Node('loc_jump_replay', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, False)])
pc = n.create_publisher(Clock, '/clock', 10); ps = n.create_publisher(LaserScan, '/scan', 10); pt = n.create_publisher(TFMessage, '/tf', 100)
pst = n.create_publisher(TFMessage, '/tf_static', QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST))
rep = []
def cb(m):
    for x in m.transforms:
        if x.header.frame_id == 'map' and x.child_frame_id == 'odom':
            s = (x.header.stamp.sec * 1000000000 + x.header.stamp.nanosec - t0b) * 1e-9
            rep.append((s, x.transform.translation.x, x.transform.translation.y, yaw(x.transform.rotation)))
n.create_subscription(TFMessage, '/tf', cb, 100)
for ts, tp, m in msgs:
    if tp == '/tf_static': pst.publish(m)
time.sleep(2.0)
w0 = time.time(); last_clock = 0; nextp = 60
for ts, tp, m in msgs:
    s = (ts - t0b) * 1e-9; target = w0 + s
    while True:
        d = target - time.time()
        if d <= 0: break
        rclpy.spin_once(n, timeout_sec=min(d, 0.005))
    if ts - last_clock > 5e6:
        c = Clock(); c.clock.sec = ts // 1000000000; c.clock.nanosec = ts % 1000000000; pc.publish(c); last_clock = ts
    if tp == '/scan': ps.publish(m)
    elif tp == '/tf': pt.publish(m)
    if s > nextp: print('  재생 %3.0f s' % s, flush=True); nextp += 60
tE = time.time() + 2
while time.time() < tE: rclpy.spin_once(n, timeout_sec=0.05)
R = np.array(sorted(rep)); L = np.array(live)
def at(A, s): i = max(np.searchsorted(A[:, 0], s) - 1, 0); return A[i, 1:]
print('재생 map→odom %d 개' % len(R))
J = [(b[0], math.hypot(b[1] - a[1], b[2] - a[2]), math.degrees(abs((b[3] - a[3] + math.pi) % (2 * math.pi) - math.pi))) for a, b in zip(R, R[1:])]
big = [j for j in J if j[1] > 0.10 or j[2] > 3.0]
print('한 번에 0.10 m·3° 넘게 바뀐 횟수 %d, 최대 %.2f m' % (len(big), max(j[1] for j in J)))
for j in big[:12]: print('  +%.1f s  %.2f m  %.1f°' % j)
for s in (100, 200, 250, 270, 276, 278, 280, 285, 300, 340):
    a, b = at(R, s), at(L, s)
    print('  +%3d s 재생 (%+.3f, %+.3f, %+.1f°) | 라이브 (%+.3f, %+.3f, %+.1f°) | x 차 %+.3f' % (s, a[0], a[1], math.degrees(a[2]), b[0], b[1], math.degrees(b[2]), a[0] - b[0]))
np.savez(OUT, rep=R, live=L)
rclpy.shutdown()
