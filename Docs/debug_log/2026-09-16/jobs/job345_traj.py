#!/usr/bin/env python3
"""MPPI 후보 궤적(/trajectories, visualize=true) 분석 — 정체 순간 최적화기가 무엇을 보고 있었나 (2026-09-16 mp4).

  /trajectories: MarkerArray. TrajectoryVisualizer 는 batch 를 trajectory_step 마다, 시간축을 time_step 마다 뽑아
  각 점을 marker 하나(SPHERE, scale 이 시간에 따라 커짐)로 발행한다. 여기서는 점들을 (x, y) 로 모아
  로버 좌표계로 옮긴 뒤 "궤적 끝단 분포" 를 본다: 앞으로 가는 후보가 있는가, 우회전 후보가 있는가.
  /transformed_global_plan: 컨트롤러가 보는 경로(잘라낸 것) — 로버 기준 첫 0.3 m 방향.
  인자: BAG [t0,t1,...] (bag 첫 odom 기준 초)
"""
import sys, math, bisect
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
from visualization_msgs.msg import MarkerArray
from nav_msgs.msg import Path
from geometry_msgs.msg import Twist

BAG = sys.argv[1]; TS = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else [10, 14, 17, 20, 23]


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


r = rosbag2_py.SequentialReader()
r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
mo, ob, trajs, tplans, cmds = [], [], [], [], []
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            tt = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                mo.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':
                ob.append((tt, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))
    elif topic == '/trajectories':
        m = deserialize_message(data, MarkerArray)
        pts = [(mk.pose.position.x, mk.pose.position.y, mk.header.frame_id, mk.scale.x) for mk in m.markers if mk.action == 0]
        trajs.append((t, pts))
    elif topic == '/transformed_global_plan':
        tplans.append((t, deserialize_message(data, Path)))
    elif topic == '/cmd_vel':
        m = deserialize_message(data, Twist); cmds.append((t, m.linear.x, m.angular.z))
mo.sort(); ob.sort()
mo_t = [s[0] for s in mo]; ob_t = [s[0] for s in ob]; tr_t = [s[0] for s in trajs]; tp_t = [s[0] for s in tplans]; cm_t = [s[0] for s in cmds]
T0 = ob[0][0]
print('bag %s: T0 %.2f, trajectories %d (점/메시지 중앙값 %d), transformed_global_plan %d, cmd %d' % (BAG, T0, len(trajs), int(np.median([len(p) for _, p in trajs])) if trajs else 0, len(tplans), len(cmds)))
if trajs:
    fr = trajs[0][1][0][2] if trajs[0][1] else '?'
    print('trajectories frame: %s, scale 종류 %d' % (fr, len(set(round(p[3], 3) for p in trajs[0][1]))))


def latest(seq, ts, t):
    i = bisect.bisect_right(ts, t) - 1
    return seq[i] if i >= 0 else None


def pose_in(frame, t):
    b = latest(ob, ob_t, t)
    if frame == 'odom' or not mo:
        return (b[1], b[2], b[3])
    a = latest(mo, mo_t, t)
    return (a[1] + b[1] * math.cos(a[3]) - b[2] * math.sin(a[3]), a[2] + b[1] * math.sin(a[3]) + b[2] * math.cos(a[3]), wrap(a[3] + b[3]))


for at in TS:
    t = T0 + at
    tj = latest(trajs, tr_t, t); tp = latest(tplans, tp_t, t); c = latest(cmds, cm_t, t)
    if tj is None:
        print('t=%.1f: trajectories 없음' % at); continue
    fr = tj[1][0][2] if tj[1] else 'odom'
    px, py, pyaw = pose_in(fr, tj[0])
    P = np.array([(p[0], p[1]) for p in tj[1]]); S = np.array([p[3] for p in tj[1]])
    dx = P[:, 0] - px; dy = P[:, 1] - py
    fx = dx * math.cos(pyaw) + dy * math.sin(pyaw); fy = -dx * math.sin(pyaw) + dy * math.cos(pyaw)
    # scale 이 큰 점 = 시간축 뒤쪽(끝단). 상위 20 % scale 을 끝단으로 본다
    thr = np.quantile(S, 0.8); end = S >= thr
    ex, ey = fx[end], fy[end]
    fwd = ex > 0.05; back = ex < -0.03; right = ey < -0.03; left = ey > 0.03
    dist = np.hypot(ex, ey)
    line = 't=%5.1f (msg %.2f s 전) 로버 (%.3f,%.3f) yaw %+.1f° cmd v %+.3f w %+.3f | 후보 끝단 %d개: 앞>5cm %3.0f%%  뒤 %3.0f%%  우 %3.0f%%  좌 %3.0f%%  | 끝단 거리 중앙 %.3f 최대 %.3f | 전방 중앙 %+.3f 횡 중앙 %+.3f' % (
        at, t - tj[0], px, py, math.degrees(pyaw), c[1] if c else 0, c[2] if c else 0, end.sum(), 100 * fwd.mean(), 100 * back.mean(), 100 * right.mean(), 100 * left.mean(), np.median(dist), dist.max(), np.median(ex), np.median(ey))
    if tp is not None and tp[1].poses:
        pfr = tp[1].header.frame_id
        qx, qy, qyaw = pose_in(pfr, tp[0])
        pts = [(q.pose.position.x, q.pose.position.y) for q in tp[1].poses]
        acc = 0; k = 0
        for i in range(len(pts) - 1):
            acc += math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]); k = i + 1
            if acc >= 0.30:
                break
        bearing = math.degrees(wrap(math.atan2(pts[k][1] - qy, pts[k][0] - qx) - qyaw))
        d0 = math.hypot(pts[0][0] - qx, pts[0][1] - qy)
        line += ' | 변환경로(%s, %d점) 첫점 거리 %.3f, 0.3 m 앞 방위 %+.1f°' % (pfr, len(pts), d0, bearing)
    print(line)
