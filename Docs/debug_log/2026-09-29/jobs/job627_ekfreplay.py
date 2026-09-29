#!/usr/bin/env python3
"""B2·B3 오프라인 검증 재생기 (2026-09-28 §27): 회전 시험 bag 의 /wheel_odom·/imu/data·/tf_static 을 **도메인 42** 에서 sim time 으로 재생,
  래퍼(job628)가 띄운 C++ 컨디셔너(icr·rot_cov 설정별) → robot_localization EKF 가 내는 /odometry/filtered 를 받아
  회전 구간(/cmd_vel |ω|>0.01)마다 EKF 가 본 중심 이동(시작 차체 기준)을 계산한다. 정답(스캔 직접 정합)과의 비교는 요약에서.
  주의: bag 의 IMU 는 이미 바이어스를 뺀 /imu/data 라 컨디셔너 입력(/imu/data_raw)으로 다시 넣는다 — 컨디셔너가 처음 10 s 정지로
        바이어스를 다시 재므로(≈ 0) 결과에 영향 없음(bag 은 기록 시작 뒤 ≥ 13 s 정지).
  인자: BAG"""
import sys, math, time, bisect
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy, qos_profile_sensor_data
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from tf2_msgs.msg import TFMessage


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


BAG = sys.argv[1]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
msgs, cmd, live = [], [], []   # live = bag 에 기록된 라이브 EKF(V0 재생 타당성 비교용, 09-29)
while r.has_next():
    tp, data, ts = r.read_next()
    if tp == '/cmd_vel': cmd.append((ts * 1e-9, deserialize_message(data, get_message(types[tp])).angular.z)); continue
    if tp == '/odometry/filtered':
        m = deserialize_message(data, get_message(types[tp])); p = m.pose.pose
        live.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, p.position.x, p.position.y, yaw(p.orientation))); continue
    if tp in ('/wheel_odom', '/imu/data', '/tf_static'): msgs.append((ts, tp, deserialize_message(data, get_message(types[tp]))))
rclpy.init(); n = Node('b2_replay')
pc = n.create_publisher(Clock, '/clock', 10)
pw = n.create_publisher(Odometry, '/wheel_odom', qos_profile_sensor_data)
pi = n.create_publisher(Imu, '/imu/data_raw', qos_profile_sensor_data)
pst = n.create_publisher(TFMessage, '/tf_static', QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST))
ekf = []
n.create_subscription(Odometry, '/odometry/filtered', lambda m: ekf.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation))), 50)
for ts, tp, m in msgs:
    if tp == '/tf_static': pst.publish(m)
time.sleep(2.0)
t0b = msgs[0][0]; w0 = time.time() + 0.5; lc = 0
for ts, tp, m in msgs:
    tgt = w0 + (ts - t0b) * 1e-9
    while True:
        d = tgt - time.time()
        if d <= 0: break
        rclpy.spin_once(n, timeout_sec=min(d, 0.003))
    if ts - lc > 5e6:
        c = Clock(); c.clock.sec = ts // 1000000000; c.clock.nanosec = ts % 1000000000; pc.publish(c); lc = ts
    if tp == '/wheel_odom': pw.publish(m)
    elif tp == '/imu/data': pi.publish(m)
te = time.time()
while time.time() - te < 2: rclpy.spin_once(n, timeout_sec=0.02)
print('EKF 출력 %d 개' % len(ekf), flush=True)


def at(t, src=None):
    src = ekf if src is None else src
    k = bisect.bisect_left([e[0] for e in src], t); return src[min(max(k, 0), len(src) - 1)]


def disp(src, a, b):
    A, B = at(a - 0.8, src), at(b + 2.5, src); c, s = math.cos(A[3]), math.sin(A[3]); dx, dy = B[1] - A[1], B[2] - A[2]
    return c * dx + s * dy, -s * dx + c * dy, math.degrees(uw(B[3] - A[3]))


segs = []
for t, w in cmd:
    if abs(w) > 0.01:
        if segs and t - segs[-1][1] < 0.5: segs[-1][1] = t
        else: segs.append([t, t])
segs = [s for s in segs if s[1] - s[0] > 2.0]
for k, (a, b) in enumerate(segs):
    x, y, th = disp(ekf, a, b)
    lv = ' | 라이브 EKF (%+.3f, %+.3f) m %+.1f°' % disp(live, a, b) if live else ' | 라이브 EKF 없음'
    print('  회전 %d: EKF 중심 이동(앞+/왼+) (%+.3f, %+.3f) m, 회전 %+.1f°%s' % (k + 1, x, y, th, lv), flush=True)
rclpy.shutdown()
