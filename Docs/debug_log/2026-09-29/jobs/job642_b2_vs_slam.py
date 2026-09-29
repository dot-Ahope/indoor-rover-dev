#!/usr/bin/env python3
"""09-29 §5: f0a7 에서 map→odom 누적 보정이 f0a6 의 2.2 배가 된 원인 — B2 가 odom 에 더한 이동과 SLAM 보정(map→odom 변화)을 구간별로 대조.
   B2 추가량 재구성(F0 bag 에 /wheel_odom/conditioned 가 없음): 컨디셔너와 같은 조건·식 —
     순수 회전 = |휠 vx| < 0.02 m/s 그리고 |ω| > 0.10 rad/s (ω = EKF twist.angular.z ≈ 자이로),
     더하는 속도 (vx, vy) = (ω·py, −ω·px), p = 시계(ω<0) (−0.029, +0.052) / 반시계(ω>0) (−0.029, −0.095) m.
   odom 좌표로 적분(EKF yaw). f0a6(끔)은 "켰다면 더했을 양", f0a7(켬)은 실제 더한 양(EKF vy 로 교차 확인).
   SLAM 보정: 구간 [시작 −0.3 s, 끝 +2.0 s] 의 map→odom 이동 변화 M (map≈odom 방향, mo yaw ≤ 2°).
   해석: 로봇이 실제로 D 만큼 밀렸고 odom 이 그중 A 를 반영하면 SLAM 은 M ≈ D − A 를 더한다.
         f0a6(A=0 실제): M ≈ D → M 이 가상 A 와 같은 방향·크기면 모델이 맞다.  f0a7: M ≈ D − A → A 가 과하면 M 이 −A 방향.
   인자: BAG [BAG ...]"""
import sys, math, bisect
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

PCW, PCCW = (-0.029, 0.052), (-0.029, -0.095)
VMAX, WMIN = 0.02, 0.10


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def load(bag):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    W, E, MO = [], [], []
    while r.has_next():
        tp, data, ts = r.read_next()
        if tp not in ('/wheel_odom', '/odometry/filtered', '/tf'): continue
        m = deserialize_message(data, get_message(types[tp]))
        if tp == '/wheel_odom': W.append((ts * 1e-9, m.twist.twist.linear.x))
        elif tp == '/odometry/filtered':
            p = m.pose.pose; tw = m.twist.twist
            E.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, p.position.x, p.position.y, yaw(p.orientation), tw.linear.x, tw.linear.y, tw.angular.z))
        else:
            for tr in m.transforms:
                if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':
                    q = tr.transform
                    MO.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, q.translation.x, q.translation.y, yaw(q.rotation)))
    MO.sort()
    return W, E, MO


def near(lst, t):
    k = bisect.bisect_left([x[0] for x in lst], t); return lst[min(max(k, 0), len(lst) - 1)]


def analyze(bag):
    W, E, MO = load(bag)
    wt = [w[0] for w in W]; mt = [m[0] for m in MO]
    print('== %s: EKF %d, 휠 %d, map→odom %d' % (bag, len(E), len(W), len(MO)))
    segs, cur = [], None
    for i in range(1, len(E)):
        t, x, y, th, vx, vy, wz = E[i]; dt = t - E[i - 1][0]
        if dt <= 0 or dt > 0.2: continue
        wvx = W[min(max(bisect.bisect_left(wt, t), 0), len(W) - 1)][1]
        on = abs(wvx) < VMAX and abs(wz) > WMIN
        if on:
            px, py = PCW if wz < 0 else PCCW
            ax, ay = wz * py, -wz * px
            c, s = math.cos(th), math.sin(th)
            if cur is None or t - cur['t1'] > 0.5:
                cur = {'t0': t, 't1': t, 'A': [0.0, 0.0], 'rot': 0.0, 'vy': [], 'y0': th}; segs.append(cur)
            cur['t1'] = t; cur['A'][0] += (c * ax - s * ay) * dt; cur['A'][1] += (s * ax + c * ay) * dt
            cur['rot'] += wz * dt; cur['vy'].append(vy)
    segs = [g for g in segs if g['t1'] - g['t0'] > 0.3]
    t00 = E[0][0]
    SA, SM, SMin = [0.0, 0.0], [0.0, 0.0], 0.0
    print('  구간  시각(s)  길이  회전°   B2 A(odom, cm)      |A|   SLAM M(cm)          |M|   M·Â(cm)  EKF vy 평균(m/s)')
    for k, g in enumerate(segs):
        a = near(MO, g['t0'] - 0.3); b = near(MO, g['t1'] + 2.0)
        M = (b[1] - a[1], b[2] - a[2]); A = g['A']
        nA = math.hypot(*A); proj = (M[0] * A[0] + M[1] * A[1]) / nA if nA > 1e-6 else 0.0
        SA[0] += A[0]; SA[1] += A[1]; SM[0] += M[0]; SM[1] += M[1]; SMin += math.hypot(*M)
        vy = sum(g['vy']) / len(g['vy'])
        print('  %3d  %6.1f  %4.1f  %+6.1f  (%+5.1f, %+5.1f)  %4.1f  (%+5.1f, %+5.1f)  %4.1f  %+5.1f    %+.3f'
              % (k + 1, g['t0'] - t00, g['t1'] - g['t0'], math.degrees(g['rot']), 100 * A[0], 100 * A[1], 100 * nA, 100 * M[0], 100 * M[1], 100 * math.hypot(*M), 100 * proj, vy))
    tot = (MO[-1][1] - MO[0][1], MO[-1][2] - MO[0][2])
    print('  합: B2 A (%+.1f, %+.1f) cm | 구간 SLAM M 합 (%+.1f, %+.1f) cm | map→odom 전체 변화 (%+.1f, %+.1f) cm = %.1f cm'
          % (100 * SA[0], 100 * SA[1], 100 * SM[0], 100 * SM[1], 100 * tot[0], 100 * tot[1], 100 * math.hypot(*tot)))
    print('      구간 밖 map→odom 변화 (%+.1f, %+.1f) cm' % (100 * (tot[0] - SM[0]), 100 * (tot[1] - SM[1])))
    # 전체 경로를 1 s 창으로 나눠 map→odom 변화가 어디서 크게 생겼나(상위 5)
    win = []
    t = MO[0][0]
    while t < MO[-1][0]:
        a = near(MO, t); b = near(MO, t + 1.0); win.append((math.hypot(b[1] - a[1], b[2] - a[2]), t - t00, b[1] - a[1], b[2] - a[2])); t += 1.0
    print('  map→odom 경로 길이(1 s 창 크기 합, 상쇄 없음) %.1f cm — 순 변화 %.1f cm' % (100 * sum(w[0] for w in win), 100 * math.hypot(*tot)))
    win.sort(reverse=True)
    print('  map→odom 변화 큰 1 s 창 상위 6: ' + ' | '.join('%.1f s (%+.1f, %+.1f)' % (w[1], 100 * w[2], 100 * w[3]) for w in win[:6]))


for b in sys.argv[1:]: analyze(b)
