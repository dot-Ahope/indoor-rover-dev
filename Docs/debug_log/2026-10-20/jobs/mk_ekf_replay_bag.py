#!/usr/bin/env python3
"""mk_ekf_replay_bag — EKF 오프라인 재실행용 입력 bag 을 만든다. (2026-10-20 §5, PC)
  주행 bag 의 /wheel_odom → 컨디셔너와 같은 공분산을 넣은 /wheel_odom/conditioned (배율 1 · B2 · B3 끔 = 주행 때 구성),
  /imu/data(컨디셔너 출력이 기록돼 있음) · /tf_static 그대로,
  cuVSLAM(오프라인 csv, camera_link 자세) → base_link 몸 기준 속도 /vslam/odom (앞뒤 프레임 중앙 차분).
  기록 시각 = 원래 bag 기록 시각(vslam 은 header stamp) — ros2 bag play --clock 으로 재생.
  인자: 주행bag cuVSLAM_csv 출력bag"""
import sys, math, csv, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.rosbag2 import Writer
from rosbags.typesys import Stores, get_typestore

TS = get_typestore(Stores.ROS2_HUMBLE)
Odometry = TS.types['nav_msgs/msg/Odometry']; Header = TS.types['std_msgs/msg/Header']; Time = TS.types['builtin_interfaces/msg/Time']
TwistWC = TS.types['geometry_msgs/msg/TwistWithCovariance']; Twist = TS.types['geometry_msgs/msg/Twist']; Vector3 = TS.types['geometry_msgs/msg/Vector3']
PoseWC = TS.types['geometry_msgs/msg/PoseWithCovariance']; Pose = TS.types['geometry_msgs/msg/Pose']; Point = TS.types['geometry_msgs/msg/Point']
Quat = TS.types['geometry_msgs/msg/Quaternion']
VX_VAR, VY_VAR, VYAW_VAR = 0.02 ** 2, 0.01 ** 2, 0.1 ** 2   # conditioner_core.hpp 기본값
VS_VXY_VAR, VS_VYAW_VAR = 0.005 ** 2, 0.02 ** 2              # cuVSLAM 속도 공분산(§5 선언) — 변형별로 쓰는 축은 EKF 설정이 고른다


def qm(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def T(tr):
    M = np.eye(4); q = tr.rotation; M[:3, :3] = qm(q.x, q.y, q.z, q.w); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


bag, vcsv, out = sys.argv[1:4]
TOP = ('/wheel_odom', '/imu/data', '/tf_static')
msgs = []; static = {}
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    conns = [c for c in rd.connections if c.topic in TOP]
    ctype = {c.topic: c.msgtype for c in conns}
    for c, t, raw in rd.messages(connections=conns):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/tf_static':
            for tr in m.transforms: static[tr.child_frame_id] = (tr.header.frame_id, T(tr.transform))
            msgs.append((t, '/tf_static', m))
        elif c.topic == '/wheel_odom':
            cov = np.array(m.twist.covariance, float); cov[0], cov[7], cov[35] = VX_VAR, VY_VAR, VYAW_VAR
            m.twist.covariance = cov; msgs.append((t, '/wheel_odom/conditioned', m))
        else:
            msgs.append((t, c.topic, m))
B2C = np.eye(4); f = 'camera_link'
while f != 'base_link':
    p, A = static[f]; B2C = A @ B2C; f = p
C2B = np.linalg.inv(B2C)

R = np.array([[float(v) for v in r] for r in list(csv.reader(open(vcsv)))[1:]])
P = []
for r in R:
    V = np.eye(4); V[:3, :3] = qm(*r[4:8]); V[:3, 3] = r[1:4]; P.append(V @ C2B)   # base_link 자세(cuVSLAM odom 틀)
nv = 0
for k in range(1, len(R) - 1):
    dt = R[k + 1, 0] - R[k - 1, 0]
    if dt <= 0 or dt > 0.3: continue   # 프레임 빠짐 — 건너뜀
    D = np.linalg.inv(P[k - 1]) @ P[k + 1]                 # k-1 몸 기준 상대 이동
    th = math.atan2(D[1, 0], D[0, 0]); half = qm(0, 0, math.sin(th / 4), math.cos(th / 4))[:2, :2]   # 중간 자세(반 회전)로 돌려 k 몸 기준에 가깝게
    v = half.T @ D[:2, 3] / dt
    st = R[k, 0]; sec = int(st); ns = int(round((st - sec) * 1e9))
    cov = np.zeros(36); cov[0] = cov[7] = VS_VXY_VAR; cov[14] = cov[21] = cov[28] = 1e3; cov[35] = VS_VYAW_VAR
    m = Odometry(header=Header(stamp=Time(sec=sec, nanosec=ns), frame_id='odom'), child_frame_id='base_link',
                 pose=PoseWC(pose=Pose(position=Point(x=0.0, y=0.0, z=0.0), orientation=Quat(x=0.0, y=0.0, z=0.0, w=1.0)), covariance=np.eye(6).flatten() * 1e3),
                 twist=TwistWC(twist=Twist(linear=Vector3(x=float(v[0]), y=float(v[1]), z=0.0), angular=Vector3(x=0.0, y=0.0, z=th / dt)), covariance=cov))
    msgs.append((sec * 10 ** 9 + ns, '/vslam/odom', m)); nv += 1
msgs.sort(key=lambda q: q[0])
ctype['/wheel_odom/conditioned'] = ctype.pop('/wheel_odom'); ctype['/vslam/odom'] = 'nav_msgs/msg/Odometry'
with Writer(Path(out), version=8) as w:
    cw = {tp: w.add_connection(tp, mt, typestore=TS) for tp, mt in ctype.items()}
    for t, tp, m in msgs: w.write(cw[tp], t, TS.serialize_cdr(m, ctype[tp]))
cnt = {}
for _, tp, _ in msgs: cnt[tp] = cnt.get(tp, 0) + 1
print(out, cnt, 'vslam 속도 %d 개' % nv)
