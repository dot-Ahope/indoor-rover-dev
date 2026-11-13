#!/usr/bin/env python3
# anal_series_bins_1113 — 11-13 §6: anal_series_1113 출력 csv 를 칸(기본 1 s)마다 요약: 지령 v·w, 휠 L/R 목표·측정 mm/s·듀티 %, EKF w·map yaw, 보드 메시지.
#   PC, 로버 안 움직임. 인자: csv 시작HH:MM:SS 끝HH:MM:SS [칸 s] (2026-11-13 KST). 출력: 표준 출력.
import sys, math, datetime, collections, statistics as st
f, S, E = sys.argv[1:4]; dt = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
KST = datetime.timezone(datetime.timedelta(hours=9)); ep = lambda h: datetime.datetime.fromisoformat(f'2026-11-13T{h}').replace(tzinfo=KST).timestamp()
t0, t1 = ep(S), ep(E); B = collections.defaultdict(lambda: collections.defaultdict(list)); mo = 0.0
for ln in open(f, encoding='utf-8'):
    p = ln.rstrip('\n').split(','); k, t = p[0], float(p[1])
    if k == 'tf': mo = float(p[4])
    if not (t0 <= t < t1): continue
    b = int((t - t0) // dt); d = B[b]
    if k == 'cmd': d['v'].append(float(p[2])); d['w'].append(float(p[3]))
    elif k == 'ekf': d['ew'].append(float(p[6])); d['my'].append(math.degrees(float(p[4]) + mo))
    elif k == 'st':
        kv = dict(x.split('=', 1) for x in ','.join(p[2:]).split(';') if '=' in x)
        for side in 'LR':
            q = dict(y.split('=') for y in kv[side].split())
            d[side + 't'].append(int(q['tgt'])); d[side + 'v'].append(int(q['v'])); d[side + 'd'].append(int(q['d']))
        d['msg'].append(kv.get('msg', ''))
m = lambda a: st.mean(a) if a else float('nan')
print(f'시각      지령v   지령w | L목표 L측정 L듀티 | R목표 R측정 R듀티 | EKFw  map yaw | 보드')
for b in sorted(B):
    d = B[b]; ts = datetime.datetime.fromtimestamp(t0 + b * dt, KST).strftime('%H:%M:%S')
    msgs = sorted(set(d['msg']) - {'OK'})
    print(f'{ts}  {m(d["v"]):6.3f} {m(d["w"]):6.3f} | {m(d["Lt"]):5.0f} {m(d["Lv"]):5.0f} {m(d["Ld"]):5.0f} | {m(d["Rt"]):5.0f} {m(d["Rv"]):5.0f} {m(d["Rd"]):5.0f} | {m(d["ew"]):5.2f} {m(d["my"]):7.1f} | {" ".join(msgs)[:40]}')
