#!/usr/bin/env python3
"""컨디셔너 V1 결정적 대조 (2026-09-28 §11): Python 판 노드를 **DDS 없이** 콜백 직접 호출로 bag 전체(누락 0)에 돌려 출력을 만들고,
  C++ 판이 재생에서 낸 출력(/tmp/cond_cpp_out.pkl, job594 가 저장)과 header.stamp 로 비교한다.
  C++ 판이 받지 못한 입력이 있으면 그 뒤로는 ZUPT 창이 어긋나므로, 'C++ 누락 이전 구간' 과 '전체' 를 나눠 본다. 인자: BAG"""
import sys, pickle, importlib.util
import rclpy, rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG = sys.argv[1]
spec = importlib.util.spec_from_file_location('sc', '/home/jetson/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py')
sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
rclpy.init(); node = sc.SensorConditioner()
cap_i, cap_o = {}, {}
def key(m): return m.header.stamp.sec * 1000000000 + m.header.stamp.nanosec
node.imu_pub.publish = lambda m: cap_i.__setitem__(key(m), (m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z))
node.odom_pub.publish = lambda m: cap_o.__setitem__(key(m), (m.twist.twist.linear.x, m.twist.twist.angular.z, tuple(m.twist.covariance)))
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
inkeys = []
while r.has_next():
    tp, data, ts = r.read_next()
    if tp == '/camera/camera/imu': m = deserialize_message(data, get_message(types[tp])); inkeys.append(key(m)); node.imu_cb(m)
    elif tp == '/wheel_odom': node.odom_cb(deserialize_message(data, get_message(types[tp])))
C = pickle.load(open('/tmp/cond_cpp_out.pkl', 'rb'))
print('Python(결정적) 출력 IMU %d, 휠 %d | C++(재생) IMU %d, 휠 %d' % (len(cap_i), len(cap_o), len(C['imu']), len(C['odo'])))
# C++ 가 받지 못한 첫 입력(캘리브 이후) 시점
after = inkeys[2000:]
miss = [k for k in after if k not in C['imu']]
first_miss = miss[0] if miss else None
ks = sorted(set(cap_i) & set(C['imu']))
pre = [k for k in ks if first_miss is None or k < first_miss]
def mx(keys): return max((max(abs(a - b) for a, b in zip(cap_i[k], C['imu'][k])) for k in keys), default=0.0)
print('C++ 누락 입력 %d 개(캘리브 이후), 첫 누락 %s' % (len(miss), 'index %d / %d' % (after.index(first_miss), len(after)) if first_miss else '없음'))
print('IMU 각속도 최대 차: C++ 누락 이전 %d 개 → %.3g | 전체 %d 개 → %.3g | 완전히 같은 비율(이전 구간) %.1f %%'
      % (len(pre), mx(pre), len(ks), mx(ks), 100.0 * sum(1 for k in pre if cap_i[k] == C['imu'][k]) / max(len(pre), 1)))
ko = sorted(set(cap_o) & set(C['odo']))
print('휠 짝 %d 개, 완전히 같은 비율 %.1f %%' % (len(ko), 100.0 * sum(1 for k in ko if cap_o[k] == C['odo'][k]) / max(len(ko), 1)))
rclpy.shutdown()
