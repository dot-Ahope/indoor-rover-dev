#!/usr/bin/env python3
"""anal_rev_sign — 바퀴 지령 방향이 뒤집히는 순간, FG 휠 속도(부호 = 마지막 지령 방향)가 실제 움직임과 어긋나는 시간 · 거리 (2026-10-26 §2, PC, 로버 안 움직임).
  왜: FG 펄스는 방향이 없어 펌웨어가 '0 아닌 마지막 duty 부호' 를 붙임(integrated_bldc_driver.c:153 → fg_encoder_driver.c:151 · 170).
      반전 순간 바퀴가 관성으로 옛 방향으로 더 돌면 그 펄스가 새 방향으로 세어짐(그 거리의 2 배 오차) — 크기를 모름(10-23 §24). D10(전진 · 후진 원호) 판단 전제.
  바퀴별 속도: 펌웨어와 같은 식 v_l = v − ω·B/2, v_r = v + ω·B/2, B = 0.443(유효 게이지, rover_platform.h WHEEL_BASE_M).
    휠  = /wheel_odom twist(v, ω) · 지령 = /cmd_vel(v, ω) · 기준 = /vslam/odom 의 vx(차체 좌표) + /imu/data 각속도를 /tf_static 으로 base_link 에 돌린 z 를 같은 식으로.
    기준은 트랙 미끄러짐 · 지연이 섞임 → 반전 없는 구간의 휠−기준 차를 '평소 차' 로 함께 냄.
  지연: 휠과 기준 시계열의 교차상관으로 기준을 휠에 맞춰 옮김(값을 출력).
  사건: 바퀴 지령이 |v| ≥ 0.01 m/s 에서 반대 부호로 바뀐 순간(사이 0 은 0.6 s 까지 허용). 창 = 사건 −0.2 ~ +1.5 s.
  지표(바퀴 · 사건마다): ① 부호 어긋남 시간 = 휠과 기준이 둘 다 |v| > 0.01 인데 부호가 다른 시간 ② 어긋남 거리 = 그 동안 |휠 − 기준| 적분
     ③ 창 전체 순 거리 차 = ∫(휠 − 기준). 평소 차 = 반전 없는 같은 길이 창들의 ③ 절댓값 중앙.
  인자: bag(압축 푼 폴더)들"""
import sys, math, bisect
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
HB = 0.443 / 2
def R(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def series(bag):
    W, C, V, G = [], [], [], []; ST = {}; fid = None
    with AnyReader([Path(bag)], default_typestore=get_typestore(Stores.ROS2_HUMBLE)) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/wheel_odom', '/cmd_vel', '/vslam/odom', '/imu/data', '/tf_static')]):
            m = rd.deserialize(raw, c.msgtype); ts = t * 1e-9
            if c.topic == '/tf_static':
                for tr in m.transforms:
                    q = tr.transform.rotation; ST[tr.child_frame_id] = (tr.header.frame_id, R(q.x, q.y, q.z, q.w))
                continue
            if c.topic != '/cmd_vel': ts = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9   # 측정 시각(헤더). cmd_vel 은 헤더 없음 → 받은 시각(첫 판은 모두 받은 시각이라 자이로 지연이 +470 ms 로 잡힘)
            if c.topic == '/wheel_odom': W.append((ts, m.twist.twist.linear.x, m.twist.twist.angular.z))
            elif c.topic == '/cmd_vel': C.append((ts, m.linear.x, m.angular.z))
            elif c.topic == '/vslam/odom': V.append((ts, m.twist.twist.linear.x))
            else: fid = m.header.frame_id; G.append((ts, m.angular_velocity.x, m.angular_velocity.y, m.angular_velocity.z))
    # 회전 기준 = 카메라 IMU 각속도를 /tf_static 으로 base_link 에 돌린 z. (v1: IMU z 를 그대로 써 수직축이 아니었음 — 지연이 탐색 끝 +480~500 ms 에 붙음.
    #   v2: /odometry/filtered 각속도는 EKF 가 휠 vyaw 도 융합(ekf.yaml odom0_config)해 휠과 독립이 아님 → 버림)
    M = np.eye(3); f = fid
    while f and f != 'base_link' and f in ST: par, Rm = ST[f]; M = Rm @ M; f = par
    if f != 'base_link': raise SystemExit('IMU 좌표 %s → base_link 사슬 없음' % fid)
    G = np.array(sorted(G)); G = np.c_[G[:, 0], (M @ G[:, 1:4].T).T[:, 2]]
    return [np.array(sorted(L)) for L in (W, C, V)] + [G]


for bag in sys.argv[1:]:
    W, C, V, G = series(bag); name = Path(bag).name.replace('bag_', '')
    if len(V) < 10: print('%s: /vslam/odom 없음 — 건너뜀' % name); continue
    T = np.arange(max(W[0, 0], V[0, 0], G[0, 0]) + 1, min(W[-1, 0], V[-1, 0], G[-1, 0]) - 1, 0.01)
    gz = np.interp(T, G[:, 0], G[:, 1]); vx = np.interp(T, V[:, 0], V[:, 1])
    wv = np.interp(T, W[:, 0], W[:, 1]); ww = np.interp(T, W[:, 0], W[:, 2])
    cv = np.array([C[max(bisect.bisect_right(C[:, 0], t) - 1, 0), 1] for t in T]) if len(C) else np.zeros_like(T)
    cw = np.array([C[max(bisect.bisect_right(C[:, 0], t) - 1, 0), 2] for t in T]) if len(C) else np.zeros_like(T)
    # 지연: 차체 v 의 교차상관(±0.5 s)으로 기준(vslam)을 휠에 맞춤, 자이로는 회전 성분으로 따로
    def lag(a, b):
        best, bl = -1e9, 0
        for k in range(-50, 51):
            x = a[50:-50]; y = b[50 + k:len(b) - 50 + k]; s = float(np.dot(x - x.mean(), y - y.mean()))
            if s > best: best, bl = s, k
        return bl
    lv, lg = lag(wv, vx), lag(ww, gz)
    vx = np.roll(vx, -lv); gz = np.roll(gz, -lg)
    out = ['== %s · 기준 지연 맞춤: vslam %+d ms · 자이로 %+d ms(+ = 기준이 늦음)' % (name, 10 * lv, 10 * lg)]
    rows = []
    for side, s in (('왼', -1), ('오른', +1)):
        whl = wv + s * ww * HB; ref = vx + s * gz * HB; cmd = cv + s * cw * HB
        ev = []; last_sign, last_t = 0, -9
        for i, t in enumerate(T):
            if abs(cmd[i]) >= 0.01:
                sg = 1 if cmd[i] > 0 else -1
                if last_sign and sg != last_sign and t - last_t <= 0.6: ev.append(i)
                last_sign, last_t = sg, t
        evt = set()
        for i in ev:
            a, b = i - 20, min(i + 150, len(T) - 1)
            if a < 0: continue
            evt.update(range(a, b))
            both = (np.abs(whl[a:b]) > 0.01) & (np.abs(ref[a:b]) > 0.01); mis = both & (np.sign(whl[a:b]) != np.sign(ref[a:b]))
            prev = cmd[max(i - 60, 0):i]; prev = prev[np.abs(prev) >= 0.01]
            rows.append((side, T[i], 0.01 * mis.sum(), 0.01 * np.abs(whl[a:b] - ref[a:b])[mis].sum(), 0.01 * (whl[a:b] - ref[a:b]).sum(), prev[-1] if len(prev) else 0.0, cmd[i]))
        # 평소 차: 반전 없는 1.7 s 창(움직이는 중) 의 |∫(휠 − 기준)|
        base = []
        for a in range(0, len(T) - 170, 170):
            if any(j in evt for j in (a, a + 85, a + 169)): continue
            if np.abs(cmd[a:a + 170]).max() < 0.02: continue
            base.append(abs(0.01 * (whl[a:a + 170] - ref[a:a + 170]).sum()))
        out.append('  %s 바퀴: 반전 %d 번 · 평소 창 |∫(휠−기준)| 중앙 %.1f mm (n %d)' % (side, len(ev), 1000 * np.median(base) if base else float('nan'), len(base)))
    for side, t, mt, md, net, c0, c1 in rows:
        out.append('   %s %s  지령 %+.3f → %+.3f m/s · 부호 어긋남 %.2f s · 어긋남 거리 %.1f mm · 창 순 차 %+.1f mm' % (
            side, __import__('time').strftime('%H:%M:%S', __import__('time').localtime(t)) + '.%02d' % int(t % 1 * 100), c0, c1, mt, 1000 * md, 1000 * net))
    if rows:
        R = np.array([(r[2], r[3], abs(r[4])) for r in rows])
        out.append('  요약: 반전 %d 번 · 부호 어긋남 시간 중앙 %.2f s(최대 %.2f) · 어긋남 거리 중앙 %.1f mm(최대 %.1f) · |창 순 차| 중앙 %.1f mm(최대 %.1f)' % (
            len(R), np.median(R[:, 0]), R[:, 0].max(), 1000 * np.median(R[:, 1]), 1000 * R[:, 1].max(), 1000 * np.median(R[:, 2]), 1000 * R[:, 2].max()))
    print('\n'.join(out))
