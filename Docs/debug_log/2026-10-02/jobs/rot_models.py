# 10-02 §8: 제자리 회전 구간에서 주행계 이동 모델 비교 — 기준 = SLAM(map) 이동 D (09-29 §3.1: 회전 중 SLAM 오차 1~2 cm)
#   모델: cur = 지금 EKF(odom) 이동, zero = 회전 중 병진 0, b2 = 09-28 회전축 고정 모델(시계/반시계 2p 를 각도 비례로)
#   구간: 지령 |w| > 0.15 rad/s 이고 |v| < 0.03 m/s 가 1 s 이상 이어진 곳. 오차 = |모델 이동 − D| (map 좌표, 시작 자세 기준)
import csv, glob, math, os, numpy as np
P2 = {'cw': np.array([-0.059, 0.102]), 'ccw': np.array([-0.062, -0.186])}   # 09-29 §1: 180° 회전 1 회당 2p (로버 시작 자세 기준)
rows = []
for f in sorted(glob.glob('f0_f2*/f2*.csv')):
    R = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(open(f))]
    if len(R) < 50: continue
    rot = np.array([abs(r['w']) > 0.15 and abs(r['v']) < 0.03 for r in R]); t = np.array([r['t'] for r in R])
    i = 0
    while i < len(R):
        if not rot[i]: i += 1; continue
        j = i
        while j + 1 < len(R) and rot[j + 1]: j += 1
        if t[j] - t[i] >= 1.0:
            A, B = R[i], R[j]; dyaw = (B['map_yaw'] - A['map_yaw'] + 180) % 360 - 180
            D = np.array([B['map_x'] - A['map_x'], B['map_y'] - A['map_y']])
            # odom 이동을 map 좌표로(시작 시각 map→odom 회전)
            c, s = math.cos(math.radians(A['mo_yaw'])), math.sin(math.radians(A['mo_yaw']))
            do = np.array([B['odom_x'] - A['odom_x'], B['odom_y'] - A['odom_y']]); cur = np.array([c * do[0] - s * do[1], s * do[0] + c * do[1]])
            th = math.radians(A['map_yaw']); k = abs(dyaw) / 180.0; p = P2['cw' if dyaw < 0 else 'ccw'] * k
            b2 = np.array([math.cos(th) * p[0] - math.sin(th) * p[1], math.sin(th) * p[0] + math.cos(th) * p[1]])
            rows.append((os.path.basename(f), t[i], dyaw, np.linalg.norm(D), np.linalg.norm(cur - D), np.linalg.norm(D), np.linalg.norm(b2 - D)))
        i = j + 1
a = np.array([r[2:] for r in rows])
print('제자리 회전 구간 %d 개 (|회전| 중앙 %.0f°, 최대 %.0f°)' % (len(a), np.median(abs(a[:, 0])), abs(a[:, 0]).max()))
for nm, k in (('지금 EKF', 2), ('병진 0', 3), ('B2', 4)):
    print('  %-8s 오차 중앙 %.3f · 90%% %.3f · 최대 %.3f m' % (nm, np.median(a[:, k]), np.percentile(a[:, k], 90), a[:, k].max()))
for lo, hi in ((0, 60), (60, 120), (120, 400)):
    m = (abs(a[:, 0]) >= lo) & (abs(a[:, 0]) < hi)
    if m.any(): print('  회전 %3d~%3d° (%d 개): 실제 이동 중앙 %.3f | EKF %.3f · 병진0 %.3f · B2 %.3f' % (lo, hi, m.sum(), np.median(a[m, 1]), np.median(a[m, 2]), np.median(a[m, 3]), np.median(a[m, 4])))
