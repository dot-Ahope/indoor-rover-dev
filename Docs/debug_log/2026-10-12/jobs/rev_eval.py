# 10-12 §1.2: 러너 csv 로 목표별 후진·제자리 회전 집계. 후진 거리 = 지령 v < −0.005 인 표본 사이 odom 이동 길이(EKF, 미끄러짐은 못 봄).
#   인자: 이름=csv ...
import csv, sys, math
for a in sys.argv[1:]:
    nm, f = a.split('='); R = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(open(f))]
    print('== %s' % nm)
    for g in sorted({r['goal'] for r in R}):
        G = [r for r in R if r['goal'] == g]; rev = revt = spin = fwd = 0.0; run = best = 0.0
        for p, q in zip(G[:-1], G[1:]):
            dt = q['t'] - p['t']; d = math.hypot(q['odom_x'] - p['odom_x'], q['odom_y'] - p['odom_y'])
            if p['v'] < -0.005: rev += d; revt += dt; run += dt; best = max(best, run)
            else:
                run = 0.0
                if p['v'] > 0.005: fwd += d
            if abs(p['v']) <= 0.01 and abs(p['w']) >= 0.15: spin += dt
        print('  목표 %d: %5.1f s | 후진 %.2f m · %.1f s(가장 긴 연속 %.1f s) | 전진 %.2f m | 제자리 회전 %.1f s' % (g, G[-1]['t'] - G[0]['t'], rev, revt, best, fwd, spin))
