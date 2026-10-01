#!/usr/bin/env python3
"""10-01 §9: 위치 추정 모드 부하 재현 — 09-30 매핑 bag 을 도메인 42·sim time 으로 재생해 localization_slam_toolbox_node(office_v2)에 먹이고,
   주행 구간에서 map→odom 이 얼마나 늦는지 잰다(f2a1 과 같은 지표).
   - 재생: /clock·/scan·/tf(기록 당시 map→odom 은 뺌)·/tf_static. 정지 구간(10~250 s)은 10 배속으로 압축, 나머지 1 배속.
   - 지표(재생 bag 시각 250 s 이후 = 주행 구간): odom→base 를 낼 때마다 (그 스탬프 − 그때까지 받은 map→odom 최신 스탬프),
     map→odom 고유 스탬프 간격, 노드 CPU(/proc, SLAM_PID).
   인자: BAG END_S   (slam 노드는 래퍼가 먼저 띄움)"""
import sys, os, time
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

BAG, END = sys.argv[1], float(sys.argv[2]); FAST_A, FAST_B, K = 10.0, 250.0, 10.0
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
msgs = []; t0b = None
while r.has_next():
    tp, data, ts = r.read_next()
    if t0b is None: t0b = ts
    if (ts - t0b) * 1e-9 > END: break
    if tp not in ('/scan', '/tf', '/tf_static'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        keep = [x for x in m.transforms if not (x.header.frame_id == 'map' and x.child_frame_id == 'odom')]
        if not keep: continue
        m.transforms = keep
    msgs.append((ts, tp, m))
print('재생 0~%.0f s(10~250 s 는 %g 배속), 메시지 %d' % (END, K, len(msgs)), flush=True)


def wall_of(s):  # bag 시각(s) → 재생 벽시계 오프셋
    if s <= FAST_A: return s
    if s <= FAST_B: return FAST_A + (s - FAST_A) / K
    return FAST_A + (FAST_B - FAST_A) / K + (s - FAST_B)


rclpy.init()
n = Node('loc_replay', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, False)])
pc = n.create_publisher(Clock, '/clock', 10); ps = n.create_publisher(LaserScan, '/scan', 10); pt = n.create_publisher(TFMessage, '/tf', 100)
pst = n.create_publisher(TFMessage, '/tf_static', QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST))
latest = [-1.0]; mo_st = []
def cb(m):
    for x in m.transforms:
        if x.header.frame_id == 'map' and x.child_frame_id == 'odom':
            s = x.header.stamp.sec + x.header.stamp.nanosec * 1e-9; mo_st.append(s); latest[0] = max(latest[0], s)
n.create_subscription(TFMessage, '/tf', cb, 100)
SP = os.environ.get('SLAM_PID')
def cpu():
    try: f = open('/proc/%s/stat' % SP).read().split(); return (int(f[13]) + int(f[14])) / os.sysconf('SC_CLK_TCK')
    except Exception: return float('nan')
for ts, tp, m in msgs:
    if tp == '/tf_static': pst.publish(m)
time.sleep(2.0)
w0 = time.time(); last_clock = 0; deficit = []; c_a = w_a = None; nextp = 60
for ts, tp, m in msgs:
    s = (ts - t0b) * 1e-9; target = w0 + wall_of(s)
    while True:
        d = target - time.time()
        if d <= 0: break
        rclpy.spin_once(n, timeout_sec=min(d, 0.005))
    if ts - last_clock > 5e6:
        c = Clock(); c.clock.sec = ts // 1000000000; c.clock.nanosec = ts % 1000000000; pc.publish(c); last_clock = ts
    if tp == '/scan': ps.publish(m)
    elif tp == '/tf':
        pt.publish(m)
        if s >= FAST_B:
            if c_a is None: c_a, w_a = cpu(), time.time()
            for x in m.transforms:
                if x.header.frame_id == 'odom' and x.child_frame_id == 'base_link' and latest[0] > 0:
                    deficit.append(x.header.stamp.sec + x.header.stamp.nanosec * 1e-9 - latest[0])
    if s > nextp: print('  재생 %3.0f s / %.0f' % (s, END), flush=True); nextp += 60
c_b, w_b = cpu(), time.time()
d = np.array(deficit); u = np.unique(np.array(mo_st)); u = u[u >= (t0b * 1e-9 + FAST_B)]; du = np.diff(u)
print('주행 구간 %.0f~%.0f s: (EKF 스탬프 − map→odom 최신 스탬프) 중앙 %+.3f · 95%% %+.3f · 최대 %+.3f s, >0.2 s 비율 %.2f %%' % (
    FAST_B, END, np.median(d), np.percentile(d, 95), d.max(), (d > 0.2).mean() * 100))
print('map→odom 고유 스탬프 간격 중앙 %.3f · 95%% %.3f · 최대 %.3f s (%d 개)' % (np.median(du), np.percentile(du, 95), du.max(), len(u)))
print('노드 CPU 평균 %.0f %% (주행 구간 %.0f s)' % ((c_b - c_a) / (w_b - w_a) * 100, w_b - w_a))
rclpy.shutdown()
