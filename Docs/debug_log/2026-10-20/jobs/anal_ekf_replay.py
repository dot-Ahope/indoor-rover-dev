#!/usr/bin/env python3
"""anal_ekf_replay — EKF 오프라인 재실행 변형(V0~V3)을 주행 때 EKF · cuVSLAM 과 함께 SLAM 기준으로 비교. (2026-10-20 §5, PC)
  지표(§4 와 같음): 10 s 창 상대 오차(1 s 간격) — 전 구간 위치 95 % · 최대 · yaw 95 %, W3 회전 t105~125 위치 최대,
  상자 옆 출발 t18~36 · 복귀 t180~200 위치 95 %; t=20 s 정렬 절대 위치 95 % · yaw |95 %| · 끝 위치.
  모두 camera_link 의 지도 평면 자세. 인자: 주행bag 재실행출력bag cuVSLAM_csv [그림.png]
  §6.4 실시간 그림자 주행: 재실행출력bag 자리에 주행bag 을 주고 환경 RTOPICS='/odometry/ekf_vslam' 로 그 토픽만, cuVSLAM_csv 를 '-' 로 주면
  주행bag 의 /visual_slam/tracking/odometry(camera_link 자세)를 cuVSLAM 으로 쓴다."""
import sys, math, bisect, csv, os
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
TS = get_typestore(Stores.ROS2_HUMBLE)
bag, rbag, vcsv = sys.argv[1:4]; fig = sys.argv[4] if len(sys.argv) > 4 else None
D = 10.0; T_AL = 20.0


def qm(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def M4(p, q):
    M = np.eye(4); M[:3, :3] = qm(q.x, q.y, q.z, q.w); M[:3, 3] = [p.x, p.y, p.z]; return M


static = {}; MO, OB = [], []; src = {}
with AnyReader([Path(bag)], default_typestore=TS) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static', '/odometry/filtered')]):
        m = rd.deserialize(raw, c.msgtype)
        if c.topic == '/odometry/filtered':
            src.setdefault('EKF(주행 기록)', []).append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, M4(m.pose.pose.position, m.pose.pose.orientation))); continue
        for tr in m.transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9; A = M4(tr.transform.translation, tr.transform.rotation)
            if c.topic == '/tf_static': static[tr.child_frame_id] = (tr.header.frame_id, A)
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, A))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, A))
RT = [x for x in os.environ.get('RTOPICS', '').split(',') if x]
with AnyReader([Path(rbag)], default_typestore=TS) as rd:
    CS = [c for c in rd.connections if not RT or c.topic in RT]
    if RT and not CS: sys.exit('RTOPICS %s 가 bag 에 없음' % RT)   # 빈 목록이면 rosbags 는 전부 읽는다
    for c, t, raw in rd.messages(connections=CS):
        m = rd.deserialize(raw, c.msgtype)
        src.setdefault('재실행 ' + c.topic.split('/')[-1].upper(), []).append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, M4(m.pose.pose.position, m.pose.pose.orientation)))
B2C = np.eye(4); f = 'camera_link'
while f != 'base_link':
    p, A = static[f]; B2C = A @ B2C; f = p
if vcsv == '-':
    R = []
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic == '/visual_slam/tracking/odometry']):
            m = rd.deserialize(raw, c.msgtype); p_, q_ = m.pose.pose.position, m.pose.pose.orientation
            R.append([m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, p_.x, p_.y, p_.z, q_.x, q_.y, q_.z, q_.w])
    R = np.array(R)
else:
    R = np.array([[float(v) for v in r] for r in list(csv.reader(open(vcsv)))[1:]])
src['cuVSLAM(IMU 끔)'] = []
for r in R:
    V = np.eye(4); V[:3, :3] = qm(*r[4:8]); V[:3, 3] = r[1:4]; src['cuVSLAM(IMU 끔)'].append((r[0], V @ np.linalg.inv(B2C)))   # camera_link → base_link 로 맞춰 둠
for L in (MO, OB): L.sort(key=lambda q: q[0])
MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; t0 = MOt[0]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
slam = lambda t: at(MO, MOt, t) @ at(OB, OBt, t) @ B2C
pl = lambda M: (M[0, 3], M[1, 3], math.atan2(M[1, 0], M[0, 0]))
SEG = (('W3 회전 t105~125', 105, 125, 'max'), ('상자 옆 출발 t18~36', 18, 36, 95), ('상자 옆 복귀 t180~200', 180, 200, 95))
print('기준 = SLAM camera_link · 창 %.0f s · 정렬 t=%.0f s' % (D, T_AL))
curves = {}
for nm, L in src.items():
    L.sort(key=lambda q: q[0]); Lt = [q[0] for q in L]
    est = lambda t, L=L, Lt=Lt: at(L, Lt, t) @ B2C
    tend = min(Lt[-1], OBt[-1]); ws = np.arange(t0 + 20, tend - D, 1.0); O = []
    for a in ws:
        G = np.linalg.inv(slam(a)) @ slam(a + D); E = np.linalg.inv(est(a)) @ est(a + D); X = np.linalg.inv(G) @ E
        O.append((a - t0, 100 * math.hypot(X[0, 3], X[1, 3]), abs(math.degrees(math.atan2(X[1, 0], X[0, 0])))))
    O = np.array(O); seg = []
    for sn, s0, s1, q in SEG:
        k = (O[:, 0] + D > s0) & (O[:, 0] < s1); v = O[k, 1].max() if q == 'max' else np.percentile(O[k, 1], q); seg.append('%s %s %.1f' % (sn, '최대' if q == 'max' else '95%', v))
    ta = t0 + T_AL; A0 = slam(ta) @ np.linalg.inv(est(ta)); ts = np.arange(ta, tend, 0.2)
    E = np.array([pl(A0 @ est(t)) for t in ts]); G = np.array([pl(slam(t)) for t in ts])
    err = 100 * np.hypot(E[:, 0] - G[:, 0], E[:, 1] - G[:, 1]); ye = np.degrees(np.angle(np.exp(1j * (E[:, 2] - G[:, 2]))))
    curves[nm] = (ts - t0, err, O)
    print('  %-16s 10 s 창: 전 구간 위치 95%% %4.1f · 최대 %4.1f cm · yaw 95%% %.2f° | %s cm | 절대: 위치 95%% %4.1f · 끝 %4.1f cm · yaw |95%%| %.1f°'
          % (nm, np.percentile(O[:, 1], 95), O[:, 1].max(), np.percentile(O[:, 2], 95), ' · '.join(seg), np.percentile(err, 95), err[-1], np.percentile(np.abs(ye), 95)))
if fig:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
    fg, ax = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    for nm, (tt, err, O) in curves.items():
        ls = '--' if '주행' in nm else '-'; ax[0].plot(O[:, 0], O[:, 1], ls, lw=1, label=nm); ax[1].plot(tt, err, ls, lw=1, label=nm)
    for a in ax:
        for s0, s1, c in ((18, 36, '#d9ead3'), (105, 125, '#f4cccc'), (180, 200, '#d9ead3')): a.axvspan(s0, s1, color=c, alpha=0.6)
        a.grid(alpha=0.3)
    ax[0].set_ylabel('10 s 창 위치 오차 (cm)'); ax[1].set_ylabel('절대 위치 오차 (cm, t=20 s 정렬)'); ax[1].set_xlabel('t (s, 주행 bag)')
    ax[0].legend(fontsize=8, ncol=3); ax[0].set_title('EKF 재실행 — 초록 = 상자 옆, 빨강 = W3 되돌아 회전')
    fg.tight_layout(); fg.savefig(fig, dpi=110); print('그림', fig)
