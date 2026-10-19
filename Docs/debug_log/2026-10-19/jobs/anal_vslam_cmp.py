#!/usr/bin/env python3
"""anal_vslam_cmp — 오프라인 cuVSLAM(프로젝터 끔 · 켬 × IMU 융합 켬 · 끔)과 EKF 를 SLAM 자세(기준) 대비 비교. (2026-10-19 §23, PC)
  모두 camera_link 의 지도 평면 자세(x, y, yaw)로. 정렬 = 각 추정의 첫 시각에서 SLAM 자세에 맞춤(그 뒤 끼워 맞춤 없음).
  SLAM = map→odom ∘ odom→base_link ∘ base_link→camera_link(정적), EKF = 같은 사슬에서 map→odom 을 첫 시각 값으로 고정한 것.
  출력: 변형별 추적 성공 비율 · 위치 오차(끝 · 95 % · 최대) · 구간 증가량, 그림(궤적 + 오차 시간축). 인자: 주행bag csv폴더 출력.png"""
import sys, math, bisect, csv, glob, os
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
bag, cdir, out = sys.argv[1:4]
SEGS = ((60, 80), (160, 210))


def qm(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def T(tr):
    M = np.eye(4); q = tr.rotation; M[:3, :3] = qm(q.x, q.y, q.z, q.w); M[:3, 3] = [tr.translation.x, tr.translation.y, tr.translation.z]; return M


static = {}; MO, OB = [], []
with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
    for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/tf', '/tf_static')]):
        for tr in rd.deserialize(raw, c.msgtype).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
            if c.topic == '/tf_static': static[tr.child_frame_id] = (tr.header.frame_id, T(tr.transform))
            elif tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': MO.append((st, T(tr.transform)))
            elif tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': OB.append((st, T(tr.transform)))
MO.sort(key=lambda q: q[0]); OB.sort(key=lambda q: q[0]); MOt = [q[0] for q in MO]; OBt = [q[0] for q in OB]; t0 = MOt[0]
at = lambda L, Lt, t: L[max(bisect.bisect_right(Lt, t) - 1, 0)][1]
B2C = np.eye(4); f = 'camera_link'
while f != 'base_link':
    p, A = static[f]; B2C = A @ B2C; f = p
slam = lambda t: at(MO, MOt, t) @ at(OB, OBt, t) @ B2C
ekf_o = lambda t: at(OB, OBt, t) @ B2C
pl = lambda M: (M[0, 3], M[1, 3], math.atan2(M[1, 0], M[0, 0]))

runs = {}
for fn in sorted(glob.glob(os.path.join(cdir, 'vslam_*_vs_*.csv'))):
    if fn.endswith('_state.csv'): continue
    nm = os.path.basename(fn)[6:-4]   # 예: true_vs_off
    R = np.array([[float(v) for v in r] for r in list(csv.reader(open(fn)))[1:]])
    S = np.array([[float(v) for v in r] for r in list(csv.reader(open(fn.replace('.csv', '_state.csv'))))[1:]]) if os.path.exists(fn.replace('.csv', '_state.csv')) else np.zeros((0, 2))
    if len(R) == 0: print('%s: 오도메트리 없음' % nm); continue
    ts = R[:, 0]; A0 = slam(ts[0])
    V0 = np.eye(4); V0[:3, :3] = qm(*R[0, 4:8]); V0[:3, 3] = R[0, 1:4]; Ainv = A0 @ np.linalg.inv(V0)
    est = []
    for r in R:
        V = np.eye(4); V[:3, :3] = qm(*r[4:8]); V[:3, 3] = r[1:4]; est.append(pl(Ainv @ V))
    runs[nm] = (ts, np.array(est), S)
# EKF 를 같은 시각축(첫 cuVSLAM 변형의 시각)에서
tref = next(iter(runs.values()))[0]; A0 = slam(tref[0]); E0 = A0 @ np.linalg.inv(ekf_o(tref[0]))
runs['EKF'] = (tref, np.array([pl(E0 @ ekf_o(t)) for t in tref]), np.zeros((0, 2)))
G = np.array([pl(slam(t)) for t in tref])

print('기준 = SLAM camera_link, 시각 = 주행 bag 첫 map→odom 기준 s, 길이 %.0f s' % (tref[-1] - tref[0]))
res = {}
for nm, (ts, E, S) in runs.items():
    Gi = np.array([pl(slam(t)) for t in ts]); err = np.hypot(E[:, 0] - Gi[:, 0], E[:, 1] - Gi[:, 1]) * 100
    yerr = np.degrees(np.angle(np.exp(1j * (E[:, 2] - Gi[:, 2]))))
    ok = 100.0 * (S[:, 1] == 1).mean() if len(S) else float('nan'); res[nm] = (ts, err)
    seg = []
    for a, b in SEGS:
        i0 = np.searchsorted(ts - t0, a); i1 = min(np.searchsorted(ts - t0, b), len(ts) - 1)
        seg.append('t%d~%d +%.1f cm' % (a, b, err[i1] - err[i0]))
    print('  %-14s 추적 성공 %5.1f %% · 위치 오차 끝 %5.1f · 95 %% %5.1f · 최대 %5.1f cm · yaw 오차 끝 %+5.1f° · 구간 증가 %s · 출력 %d (%.1f Hz)'
          % (nm, ok, err[-1], np.percentile(err, 95), err.max(), yerr[-1], ' · '.join(seg), len(ts), len(ts) / (ts[-1] - ts[0])))
fig, ax = plt.subplots(1, 2, figsize=(14, 6))
col = {'EKF': '#7f7f7f'}; pal = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
for i, (nm, (ts, E, S)) in enumerate(runs.items()):
    c = col.get(nm, pal[i % 4]); ax[0].plot(E[:, 0], E[:, 1], lw=1, color=c, label=nm); ax[1].plot(res[nm][0] - t0, res[nm][1], lw=1, color=c, label=nm)
ax[0].plot(G[:, 0], G[:, 1], 'k--', lw=1.2, label='SLAM(기준)'); ax[0].set_aspect('equal'); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8); ax[0].set_title('camera_link 궤적(지도, 첫 자세 맞춤)')
for a, b in SEGS: ax[1].axvspan(a, b, color='0.9')
ax[1].set_xlabel('t (s, 주행 bag)'); ax[1].set_ylabel('SLAM 대비 위치 오차 (cm)'); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8); ax[1].set_title('위치 오차 — 회색 = SLAM 이 크게 고친 구간 · 복귀 회전')
fig.tight_layout(); fig.savefig(out, dpi=110); print('그림', out)
