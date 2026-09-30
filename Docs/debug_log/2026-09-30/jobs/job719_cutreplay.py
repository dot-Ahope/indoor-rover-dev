#!/usr/bin/env python3
"""09-30 §17: 점프 전까지만 지도 되살리기 — 매핑 bag 을 **도메인 42**·sim time 으로 CUT 초까지만 재생해
   office_v1 에서 이어 그리는 새 slam_toolbox 에 먹이고, 끝나면 시계를 계속 흘리며 포즈 그래프·격자를 후보 이름으로 저장.
   (job580 재생기 기반: 기록 당시 map→odom 은 빼고 odom→base·정적 TF·스캔만 재생)
   검증 출력: 재생 SLAM 의 map→odom 점프(>5 cm 또는 >2°) 목록과 CUT 시점 값(라이브 기록과 비교).
   인자: BAG CUT_S OUT_PATH(확장자 없이)"""
import sys, math, time, subprocess
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


BAG, CUT, OUT = sys.argv[1], float(sys.argv[2]), sys.argv[3]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
msgs = []; t0b = None
while r.has_next():
    tp, data, ts = r.read_next()
    if t0b is None: t0b = ts
    if (ts - t0b) * 1e-9 > CUT: break
    if tp not in ('/scan', '/tf', '/tf_static'): continue
    m = deserialize_message(data, get_message(types[tp]))
    if tp == '/tf':
        keep = [tr for tr in m.transforms if not (tr.header.frame_id == 'map' and tr.child_frame_id == 'odom')]
        if not keep: continue
        m.transforms = keep
    msgs.append((ts, tp, m))
print('재생: 앞 %.0f s, 메시지 %d 개 (스캔 %d)' % (CUT, len(msgs), sum(1 for x in msgs if x[1] == '/scan')), flush=True)

rclpy.init()
n = Node('cut_replay', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, False)])
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


def clk(ts):
    c = Clock(); c.clock.sec = ts // 1000000000; c.clock.nanosec = ts % 1000000000; pc.publish(c)


for ts, tp, m in msgs:
    if tp == '/tf_static': pst.publish(m)
time.sleep(2.0)
w0 = time.time(); last_clock = 0; nextp = 60
for ts, tp, m in msgs:
    target = w0 + (ts - t0b) * 1e-9
    while True:
        d = target - time.time()
        if d <= 0: break
        rclpy.spin_once(n, timeout_sec=min(d, 0.01))
    if ts - last_clock > 5e6: clk(ts); last_clock = ts
    simnow[0] = ts * 1e-9
    if tp == '/scan': ps.publish(m)
    elif tp == '/tf': pt.publish(m)
    if (ts - t0b) * 1e-9 > nextp:
        print('  재생 %3.0f s / %.0f' % ((ts - t0b) * 1e-9, CUT), flush=True); nextp += 60
tend = msgs[-1][0]
# 마지막 스캔 처리·지도 갱신을 위해 시계를 5 s 더(위치 입력 없이), 그다음 저장하는 동안에도 시계 유지
k = 0


def tick(sec):
    global k
    tE = time.time() + sec
    while time.time() < tE:
        k += 1; ts = tend + int(k * 5e7); clk(ts); simnow[0] = ts * 1e-9; rclpy.spin_once(n, timeout_sec=0.05)


tick(5.0)
# 재생 SLAM 의 map→odom 점프
J = []
for a, b in zip(mo, mo[1:]):
    d = math.hypot(b[1] - a[1], b[2] - a[2]); da = math.degrees(abs((b[3] - a[3] + math.pi) % (2 * math.pi) - math.pi))
    if d > 0.05 or da > 2.0: J.append((b[0] - t0b * 1e-9, d, da))
print('재생 SLAM map→odom %d 개, 점프(>5 cm·>2°) %d 건' % (len(mo), len(J)))
for t, d, da in J[:20]: print('  +%.1f s  %.2f m  %.1f°' % (t, d, da))
if mo: print('CUT 시점 재생 map→odom (%+.3f, %+.3f, %+.1f°)' % (mo[-1][1], mo[-1][2], math.degrees(mo[-1][3])), flush=True)
for cmd in (['ros2', 'service', 'call', '/slam_toolbox/serialize_map', 'slam_toolbox/srv/SerializePoseGraph', "{filename: '%s'}" % OUT],
            ['ros2', 'service', 'call', '/slam_toolbox/save_map', 'slam_toolbox/srv/SaveMap', "{name: {data: '%s'}}" % OUT]):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    t1 = time.time()
    while p.poll() is None and time.time() - t1 < 60: tick(0.2)
    out = p.communicate()[0] if p.poll() is not None else '(시간 초과)'
    print('  %s → %s' % (cmd[3], out.strip().splitlines()[-1] if out.strip() else '?'), flush=True)
tick(2.0)
rclpy.shutdown()
