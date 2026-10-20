#!/usr/bin/env python3
"""chk_vslam_live — (10-20 §6.1) 정지 중 cuVSLAM 그림자 구성 측정. 노드 1 개 + /proc. 인자: 초(기본 60)
  토픽 주기, 전체 CPU(6 코어 = 100 %), 프로세스별 CPU(코어 1 = 100 %), /odometry/filtered · /odometry/ekf_vslam 이동량."""
import sys, time, os, math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from nav_msgs.msg import Odometry
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
TOP = ['/visual_slam/tracking/odometry', '/vslam/odom', '/odometry/ekf_vslam', '/odometry/filtered']
PROCS = {'cuVSLAM(컨테이너)': '__node:=cuvslam_container', 'vslam_twist': 'vslam_twist.py', 'ekf_vslam': '__node:=ekf_vslam',
         'ekf 주': '__node:=ekf_filter_node', '카메라': 'realsense2_camera_container', 'nvblox': 'nvblox_node', 'rf2o': 'rf2o_laser_odometry_node',
         '컨디셔너': 'sensor_conditioner_node', 'slam': 'localization_slam', 'controller': 'controller_server'}


def pids(pat):
    out = []
    for p in os.listdir('/proc'):
        if not p.isdigit(): continue
        try:
            cl = open('/proc/%s/cmdline' % p, 'rb').read().replace(b'\0', b' ').decode(errors='ignore')
        except Exception:
            continue
        if pat in cl and 'chk_vslam_live' not in cl and 'bash -c' not in cl: out.append(p)
    return out


def jiff(ps):
    s = 0
    for p in ps:
        try:
            f = open('/proc/%s/stat' % p).read().rsplit(')', 1)[1].split(); s += int(f[11]) + int(f[12])
        except Exception:
            pass
    return s


def tot():
    f = [int(x) for x in open('/proc/stat').readline().split()[1:]]; return sum(f), f[3] + f[4]


class N(Node):
    def __init__(self):
        super().__init__('chk_vslam_live'); self.t = {k: [] for k in TOP}; self.pos = {k: [] for k in TOP}
        for k in TOP: self.create_subscription(Odometry, k, lambda m, k=k: self.cb(k, m), qos_profile_sensor_data)

    def cb(self, k, m):
        self.t[k].append(time.time()); p = m.pose.pose.position; self.pos[k].append((p.x, p.y))


rclpy.init(); n = N()
t_end = time.time() + 3
while time.time() < t_end: rclpy.spin_once(n, timeout_sec=0.1)
for k in TOP: n.t[k].clear(); n.pos[k].clear()
P = {k: pids(v) for k, v in PROCS.items()}; J0 = {k: jiff(v) for k, v in P.items()}; T0 = tot(); w0 = time.time()
t_end = time.time() + DUR
while time.time() < t_end: rclpy.spin_once(n, timeout_sec=0.1)
T1 = tot(); el = time.time() - w0; hz = os.sysconf('SC_CLK_TCK')
busy = 100.0 * (1 - (T1[1] - T0[1]) / max(T1[0] - T0[0], 1))
print('측정 %.0f s · 전체 CPU %.1f %% (6 코어 = 100)' % (el, busy))
for k in TOP:
    c = len(n.t[k]); mv = (100 * math.hypot(n.pos[k][-1][0] - n.pos[k][0][0], n.pos[k][-1][1] - n.pos[k][0][1])) if c > 1 else float('nan')
    print('  %-32s %5.1f Hz · 처음→끝 이동 %.2f cm' % (k, c / el, mv))
print('  프로세스 CPU(코어 1 = 100):', ' · '.join('%s %.1f%s' % (k, 100.0 * (jiff(P[k]) - J0[k]) / hz / el, '' if P[k] else '(없음)') for k in PROCS))
