#!/usr/bin/env python3
"""컨디셔너 V1 출력 동일성 (2026-09-28 §11): 원시 입력 bag(/camera/camera/imu, /wheel_odom)을 **도메인 42** 에서 1 배속 재생해
  Python 판(/py/...)과 C++ 판(/cpp/...)에 같은 입력을 주고, 출력 메시지를 header.stamp 로 짝지어 필드별 최대 차이를 본다.
  래퍼(job595)가 두 노드를 출력 remap 해 먼저 띄운다. 인자: BAG"""
import sys, time, math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, QoSProfile, ReliabilityPolicy, HistoryPolicy
# 09-28: 두 노드의 발행은 best effort — 구독도 best effort 여야 받는다(reliable 구독은 호환 안 됨, 첫 실행에서 0 개 수신)
SUB_QOS = QoSProfile(depth=200, reliability=ReliabilityPolicy.BEST_EFFORT, history=HistoryPolicy.KEEP_LAST)
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry

BAG = sys.argv[1]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
msgs = []
while r.has_next():
    tp, data, ts = r.read_next()
    if tp in ('/camera/camera/imu', '/wheel_odom'): msgs.append((ts, tp, deserialize_message(data, get_message(types[tp]))))
nimu = sum(1 for m in msgs if m[1] == '/camera/camera/imu'); nodo = len(msgs) - nimu
print('입력: IMU %d, 휠 %d, 길이 %.1f s' % (nimu, nodo, (msgs[-1][0] - msgs[0][0]) * 1e-9), flush=True)

rclpy.init(); n = Node('cond_ab')
pi = n.create_publisher(Imu, '/camera/camera/imu', qos_profile_sensor_data)
po = n.create_publisher(Odometry, '/wheel_odom', qos_profile_sensor_data)
out = {'py_imu': {}, 'cpp_imu': {}, 'py_odo': {}, 'cpp_odo': {}}
def key(m): return m.header.stamp.sec * 1000000000 + m.header.stamp.nanosec
for k, t, T in (('py_imu', '/py/imu/data', Imu), ('cpp_imu', '/cpp/imu/data', Imu), ('py_odo', '/py/wheel_odom/conditioned', Odometry), ('cpp_odo', '/cpp/wheel_odom/conditioned', Odometry)):
    n.create_subscription(T, t, (lambda kk: (lambda m: out[kk].__setitem__(key(m), m)))(k), SUB_QOS)
time.sleep(3.0)
for _ in range(20): rclpy.spin_once(n, timeout_sec=0.05)
t0b = msgs[0][0]; w0 = time.time() + 0.5
for ts, tp, m in msgs:
    target = w0 + (ts - t0b) * 1e-9
    while True:
        d = target - time.time()
        if d <= 0: break
        rclpy.spin_once(n, timeout_sec=min(d, 0.002))
    (pi if tp == '/camera/camera/imu' else po).publish(m)
    rclpy.spin_once(n, timeout_sec=0)
te = time.time()
while time.time() - te < 2.0: rclpy.spin_once(n, timeout_sec=0.02)

def cmp(a, b, fields):
    ks = sorted(set(a) & set(b)); worst = {f: 0.0 for f in fields}
    for k in ks:
        for f in fields:
            va, vb = fields[f](a[k]), fields[f](b[k])
            for x, y in zip(va, vb): worst[f] = max(worst[f], abs(x - y))
    return len(ks), worst

imu_f = {'angular_velocity': lambda m: (m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z),
         'linear_acceleration': lambda m: (m.linear_acceleration.x, m.linear_acceleration.y, m.linear_acceleration.z),
         'orientation': lambda m: (m.orientation.x, m.orientation.y, m.orientation.z, m.orientation.w),
         'angular_velocity_covariance': lambda m: tuple(m.angular_velocity_covariance),
         'linear_acceleration_covariance': lambda m: tuple(m.linear_acceleration_covariance),
         'orientation_covariance': lambda m: tuple(m.orientation_covariance)}
odo_f = {'twist': lambda m: (m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z),
         'pose': lambda m: (m.pose.pose.position.x, m.pose.pose.position.y, m.pose.pose.orientation.z, m.pose.pose.orientation.w),
         'twist_covariance': lambda m: tuple(m.twist.covariance)}
print('수신: Python IMU %d / C++ IMU %d, Python 휠 %d / C++ 휠 %d' % (len(out['py_imu']), len(out['cpp_imu']), len(out['py_odo']), len(out['cpp_odo'])))
print('  (IMU 기대 = 입력 %d − 캘리브 2000 = %d, 휠 기대 = %d)' % (nimu, nimu - 2000, nodo))
nk, w = cmp(out['py_imu'], out['cpp_imu'], imu_f)
print('IMU 짝 %d 개 — 필드별 최대 차: %s' % (nk, ', '.join('%s %.3g' % kv for kv in w.items())))
only_py = len(set(out['py_imu']) - set(out['cpp_imu'])); only_c = len(set(out['cpp_imu']) - set(out['py_imu']))
print('  한쪽에만 있는 IMU: Python %d, C++ %d' % (only_py, only_c))
nk, w = cmp(out['py_odo'], out['cpp_odo'], odo_f)
print('휠 짝 %d 개 — 필드별 최대 차: %s' % (nk, ', '.join('%s %.3g' % kv for kv in w.items())))
# 바이어스 추이(Python − 입력): 짝지은 IMU 에서 bias_y = raw_y − out_y
raw = {key(m): m for ts, tp, m in msgs if tp == '/camera/camera/imu'}
for nm in ('py_imu', 'cpp_imu'):
    ks = sorted(set(out[nm]) & set(raw))
    if ks:
        b0 = raw[ks[0]].angular_velocity.y - out[nm][ks[0]].angular_velocity.y; b1 = raw[ks[-1]].angular_velocity.y - out[nm][ks[-1]].angular_velocity.y
        print('  %s 바이어스 y: 처음 %.6f → 끝 %.6f (ZUPT 이동 %+.6f)' % (nm, b0, b1, b1 - b0))
# 차이 분포: 각속도 차가 0 인 비율과, 0 이 아닌 첫 시점이 Python 쪽 누락 뒤인지
ks = sorted(set(out['py_imu']) & set(out['cpp_imu']))
d = [abs(out['py_imu'][k].angular_velocity.y - out['cpp_imu'][k].angular_velocity.y) for k in ks]
nz = [i for i, v in enumerate(d) if v > 0]
print('각속도 y 차 = 0 인 짝 %d / %d (%.1f %%)' % (len(d) - len(nz), len(d), 100.0 * (len(d) - len(nz)) / max(len(d), 1)))
if nz:
    k0 = ks[nz[0]]; allraw = sorted(raw)
    miss_py = [k for k in allraw if k < k0 and k in out['cpp_imu'] and k not in out['py_imu']]
    print('  첫 차이 시점까지 Python 쪽에만 빠진 IMU %d 개 (C++ 는 받음) — 0 이면 논리 차이 의심' % len(miss_py))
import pickle
pickle.dump({'imu': {k: (m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z) for k, m in out['cpp_imu'].items()},
             'odo': {k: (m.twist.twist.linear.x, m.twist.twist.angular.z, tuple(m.twist.covariance)) for k, m in out['cpp_odo'].items()}},
            open('/tmp/cond_cpp_out.pkl', 'wb'))
rclpy.shutdown()
