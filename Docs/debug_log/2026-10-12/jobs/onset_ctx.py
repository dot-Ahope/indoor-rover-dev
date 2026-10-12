# 10-12 §8: (1) 포화 시작 직전 20 s 의 주행 상태 (2) 포화 없는 구간에서 '도는 정도'와 프로세스 부하의 관계
#   러너 csv(10 Hz: t, goal, 자세, 지령 v·w) + proc 기록(2 s, 전 프로세스 틱). csv 의 t 는 러너 시작 기준 → proc 의 epoch 와 맞추려고 주행 시작 시각을 인자로 줌.
import csv, sys, time, math, collections, numpy as np
def ep(s): return time.mktime(time.strptime('2026-10-12 ' + s, '%Y-%m-%d %H:%M:%S'))
RUNS = [('f2f1', 15, '10:31:56', '10:35:04'), ('f2f3', 15, '11:30:03', '11:30:53'), ('f2g2', 15, '12:16:03', '12:17:24'), ('f2i1', 15, '13:52:44', '13:53:24'),
        ('f2g1', 5, '11:55:39', None), ('f2h1', 15, '13:32:39', None)]
def load_proc(f):
    snap = collections.defaultdict(dict)
    for l in open(f, errors='replace'):
        p = l.split(None, 3)
        if len(p) < 4 or p[1] == 'ALL': continue
        try: snap[int(p[0])][(p[1], p[3].strip())] = int(p[2])
        except ValueError: pass
    return snap
KEYS = ['(ekf_node)', '(localization_sl)', '(rf2o_laser_odom)', '(nvblox_node)', '(controller_serv)', '(planner_server)', '(ros2)']
print('(1) 포화 시작 직전 20 s (지령 기준)')
for nm, pf, st, on in RUNS:
    R = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(open('f0_%s/%s.csv' % (nm, nm)))]
    T0 = ep(st) - R[0]['t'] + 0.0   # csv 첫 표본 ≈ 주행 시작 직후
    for r in R: r['e'] = T0 + r['t']
    if on:
        W = [r for r in R if ep(on) - 20 <= r['e'] < ep(on)]
        v = np.array([r['v'] for r in W]); w = np.array([r['w'] for r in W])
        print('  %s(벌점 %d) 시작 %s: 목표 %d · 평균 v %+.3f · |w| 평균 %.2f rad/s · |w|>0.2 인 시간 %.0f %% · 후진 시간 %.0f %% · 위치 (%.2f, %.2f)' % (
            nm, pf, on, W[-1]['goal'], v.mean(), np.abs(w).mean(), (np.abs(w) > 0.2).mean() * 100, (v < -0.005).mean() * 100, W[-1]['map_x'], W[-1]['map_y']))
    # (2) 포화 전 구간: 2 s 칸마다 |w| 평균과 프로세스 CPU
    snap = load_proc('f0_%s/proc_%s.log' % (nm, nm)); ts = sorted(snap); end = ep(on) - 4 if on else R[-1]['e']
    rows = []
    for a, b in zip(ts[:-1], ts[1:]):
        if a < ep(st) + 5 or b > end: continue
        seg = [r for r in R if a <= r['e'] < b]
        if len(seg) < 5: continue
        cpu = [sum((snap[b][k] - snap[a][k]) for k in snap[b] if k[1] == key and k in snap[a]) / (b - a) for key in KEYS]
        rows.append([np.mean([abs(r['w']) for r in seg]), np.mean([r['v'] for r in seg])] + cpu + [sum((snap[b][k] - snap[a].get(k, snap[b][k])) for k in snap[b]) / (b - a)])
    A = np.array(rows)
    if len(A) < 8: print('  %s: 포화 전 표본 부족' % nm); continue
    hi = A[:, 0] > 0.2; lo = A[:, 0] < 0.08
    print('  %s 포화 전 %d 칸 | 도는 칸(|w|>0.2) %d · 직진 칸(|w|<0.08) %d | ' % (nm, len(A), hi.sum(), lo.sum()) +
          ' '.join('%s %.0f→%.0f' % (k.strip('()')[:8], A[lo, 2 + i].mean() if lo.any() else 0, A[hi, 2 + i].mean() if hi.any() else 0) for i, k in enumerate(KEYS)) +
          ' | 합계 %.0f→%.0f (직진→도는 칸)' % (A[lo, -1].mean() if lo.any() else 0, A[hi, -1].mean() if hi.any() else 0))
    np.save('onset_%s.npy' % nm, A)
