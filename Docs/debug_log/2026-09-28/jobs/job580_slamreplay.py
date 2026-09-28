#!/usr/bin/env python3
"""B1 오프라인 검증 재생기 (2026-09-28 §7): 회전 시험 bag 을 **별도 ROS 도메인**에서 sim time 으로 재생해 새로 띄운 slam_toolbox 에 먹이고,
  그 SLAM 이 순수 회전 밀림을 잡는지 본다(정답 = job567 스캔 직접 정합).
  재생: /clock, /scan, /tf(기록 당시 map→odom 은 **빼고** odom→base 등만), /tf_static(transient_local). 실시간 1 배속.
  기록: 재생 중 새 SLAM 이 내는 map→odom(수신 시 sim 시각). 끝나면 회전 구간(/cmd_vel |ω|>0.01)마다
        회전 직전(시작−0.8 s)·직후(끝+2.5 s) map→base = map→odom ∘ odom→base 로 시작 차체 기준 이동(앞+/왼+).
  인자: BAG   (slam_toolbox 는 래퍼가 같은 도메인·use_sim_time 으로 먼저 띄운다)"""
import sys, math, time, bisect
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
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


BAG = sys.argv[1]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
msgs = []; ob = []; cmd = []
while r.has_next():
    tp, data, ts = r.read_next()
    if tp not in ('/scan', '/tf', '/tf_static', '/cmd_vel'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/cmd_vel': cmd.append((ts * 1e-9, m.angular.z)); continue
    if tp == '/tf':
        keep = [tr for tr in m.transforms if not (tr.header.frame_id == 'map' and tr.child_frame_id == 'odom')]
        for tr in keep:
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((ts * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))
        if not keep: continue
        m.transforms = keep
    msgs.append((ts, tp, m))
print('재생 메시지 %d 개, odom→base %d, 지령 %d' % (len(msgs), len(ob), len(cmd)), flush=True)

rclpy.init()
n = Node('b1_replay', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, False)])
pc = n.create_publisher(Clock, '/clock', 10)
ps = n.create_publisher(LaserScan, '/scan', 10)
pt = n.create_publisher(TFMessage, '/tf', 100)
pst = n.create_publisher(TFMessage, '/tf_static', QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE, history=HistoryPolicy.KEEP_LAST))
mo = []; simnow = [0.0]


def cb_tf(m):
    for tr in m.transforms:
        if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
            mo.append((simnow[0], tr.transform.translation.x, tr.transform.translation.y, yaw(tr.transform.rotation)))


n.create_subscription(TFMessage, '/tf', cb_tf, 100)
# 정적 TF 는 먼저 한 번
statics = [m for ts, tp, m in msgs if tp == '/tf_static']
t0b = msgs[0][0]; w0 = time.time()
for m in statics: pst.publish(m)
time.sleep(2.0)
last_clock = 0
for ts, tp, m in msgs:
    target = w0 + 2.0 + (ts - t0b) * 1e-9
    while True:
        d = target - time.time()
        if d <= 0: break
        rclpy.spin_once(n, timeout_sec=min(d, 0.01))
    c = Clock(); c.clock.sec = ts // 1000000000; c.clock.nanosec = ts % 1000000000
    if ts - last_clock > 5e6: pc.publish(c); last_clock = ts
    simnow[0] = ts * 1e-9
    if tp == '/scan': ps.publish(m)
    elif tp == '/tf': pt.publish(m)
    elif tp == '/tf_static': pst.publish(m)
# 끝에 3 s 더 시계를 흘려 마지막 보정을 받는다
tend = msgs[-1][0]
for k in range(60):
    ts = tend + int((k + 1) * 5e7); c = Clock(); c.clock.sec = ts // 1000000000; c.clock.nanosec = ts % 1000000000; pc.publish(c); simnow[0] = ts * 1e-9
    rclpy.spin_once(n, timeout_sec=0.05)
print('새 SLAM map→odom 수신 %d 개' % len(mo), flush=True)


def at(arr, t):
    k = bisect.bisect_right([a[0] for a in arr], t) - 1; return arr[max(k, 0)]


def mb(t):
    _, mx, my, mth = at(mo, t) if mo else (0, 0.0, 0.0, 0.0); _, ox, oy, oth = at(ob, t)
    c, s = math.cos(mth), math.sin(mth); return (mx + c * ox - s * oy, my + s * ox + c * oy, uw(mth + oth))


def rel(p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; c, s = math.cos(p0[2]), math.sin(p0[2]); return c * dx + s * dy, -s * dx + c * dy


segs = []
for t, w in cmd:
    if abs(w) > 0.01:
        if segs and t - segs[-1][1] < 0.5: segs[-1][1] = t
        else: segs.append([t, t])
segs = [s for s in segs if s[1] - s[0] > 2.0]
for k, (a, b) in enumerate(segs):
    tA, tB = a - 0.8, b + 2.5
    p0, p1 = mb(tA), mb(tB); x, y = rel(p0, p1)
    m0, m1 = at(mo, tA) if mo else (0, 0, 0, 0), at(mo, tB) if mo else (0, 0, 0, 0)
    # 회전 동안 map→odom 갱신 횟수(값이 바뀐 횟수)
    ch = 0; prev = None
    for q in mo:
        if tA <= q[0] <= tB:
            v = (round(q[1], 4), round(q[2], 4), round(q[3], 4))
            if prev is not None and v != prev: ch += 1
            prev = v
    print('  회전 %d: SLAM 중심 이동(앞+/왼+) (%+.3f, %+.3f) = %.3f m | 회전 %+.1f° | map→odom 변화 (%+.3f, %+.3f, %+.2f°), 갱신 %d 회'
          % (k + 1, x, y, math.hypot(x, y), math.degrees(uw(p1[2] - p0[2])), m1[1] - m0[1], m1[2] - m0[2], math.degrees(uw(m1[3] - m0[3])), ch), flush=True)
rclpy.shutdown()
