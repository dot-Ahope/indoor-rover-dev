#!/usr/bin/env python3
"""slam_replay_feed — 주행 bag 의 /scan · /tf(map→odom 뺌) · /tf_static 을 실시간 1 배로 다시 내보내고(/clock 포함),
  재생 중 SLAM(localization_slam_toolbox_node, use_sim_time)이 내는 map→odom 을 기록한다 (2026-10-27 §26, Jetson, 로버 안 움직임).
  왜: SLAM map→odom stamp 정체(스캔 정합 처리 지연, §21~§23 · §26)를 파라미터별로 A/B 하려면 같은 입력을 되풀이해야 한다.
  ROS_DOMAIN_ID 를 바꿔(러너 run_slam_replay.sh 가 42) 떠 있는 스택과 섞이지 않게 한다.
  출력(out.txt): 'MO <sim 수신 s> <stamp s> <x> <y> <yaw>' 줄(SLAM 이 낸 map→odom 전부) + 'CPU <sim s> <SLAM 틱 누적>'(SLAM_PID 주면 1 s 마다).
  인자: bag폴더 out.txt [시작 오프셋 s=0] [길이 s=전체]"""
import sys, os, time, math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from rosgraph_msgs.msg import Clock
from builtin_interfaces.msg import Time
import rosbag2_py
BAG, OUT = sys.argv[1], sys.argv[2]; OFF = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0; DUR = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
PID = os.environ.get('SLAM_PID')
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
r.set_filter(rosbag2_py.StorageFilter(topics=['/scan', '/tf', '/tf_static']))
rclpy.init(); n = Node('slam_replay_feed')
pc = n.create_publisher(Clock, '/clock', 10)
ps = n.create_publisher(get_message(types['/scan']), '/scan', QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))
pt = n.create_publisher(get_message(types['/tf']), '/tf', 100)
pts = n.create_publisher(get_message(types['/tf_static']), '/tf_static', QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
out = open(OUT, 'w'); sim = [0.0]
def cb(m):
    for tr in m.transforms:
        if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
            q = tr.transform.rotation; y = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
            out.write('MO %.4f %.4f %.4f %.4f %.5f\n' % (sim[0], tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, y))
n.create_subscription(get_message(types['/tf']), '/tf', cb, 200)
def stamp(t):
    s = Time(); s.sec = int(t); s.nanosec = int((t - int(t)) * 1e9); return s
t_bag0 = None; t_wall0 = None; last_clock = 0.0; last_cpu = 0.0; nmsg = 0
while r.has_next():
    topic, data, tns = r.read_next(); tb = tns * 1e-9
    if t_bag0 is None: t_bag0 = tb
    if tb - t_bag0 < OFF:
        if topic == '/tf_static': pts.publish(deserialize_message(data, get_message(types[topic])))
        continue
    if tb - t_bag0 > OFF + DUR: break
    if t_wall0 is None: t_wall0 = time.time() - (tb - t_bag0 - OFF)
    while True:   # 실시간 1 배 맞추기 — 기다리는 동안 /clock 과 콜백 처리
        now_sim = t_bag0 + OFF + (time.time() - t_wall0)
        if now_sim - last_clock >= 0.01:
            c = Clock(); c.clock = stamp(now_sim); pc.publish(c); last_clock = now_sim; sim[0] = now_sim
        if PID and now_sim - last_cpu >= 1.0:
            try:
                f = open('/proc/%s/stat' % PID).read().split(); out.write('CPU %.3f %d\n' % (now_sim, int(f[13]) + int(f[14]))); last_cpu = now_sim
            except OSError: pass
        if now_sim >= tb: break
        rclpy.spin_once(n, timeout_sec=min(0.005, tb - now_sim))
    m = deserialize_message(data, get_message(types[topic]))
    if topic == '/tf':
        keep = [tr for tr in m.transforms if not (tr.header.frame_id == 'map' and tr.child_frame_id == 'odom')]   # 원래 SLAM 출력은 빼고
        if not keep: continue
        m.transforms = keep; pt.publish(m)
    elif topic == '/tf_static': pts.publish(m)
    else: ps.publish(m)
    nmsg += 1
t_end = time.time() + 3.0
while time.time() < t_end: rclpy.spin_once(n, timeout_sec=0.05)
out.close(); print('재생 끝: 메시지 %d · 길이 %.1f s' % (nmsg, sim[0] - t_bag0 - OFF if t_bag0 else 0))
