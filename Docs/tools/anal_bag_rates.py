#!/usr/bin/env python3
"""anal_bag_rates — bag 여러 개의 토픽별 '기록기가 받은' 메시지 수·주기·크기를 나란히 비교한다. (2026-10-13 · 11-19 §3 시간 칸 추가)
  왜: PreferForward 5 와 15 에서 발행되는 데이터의 양(개수·바이트)이 다른지 확인(포화가 15 에서만 생긴 이유 후보 가리기).
      11-19: 같은 일을 시간 칸으로 하던 anal_tf_rate(10-12 §3.3, /tf 프레임 쌍별 Hz) · anal_traj_size(10-12 §7.3, /trajectories 크기)를 --bins 로 합침.
  주의: bag 의 수는 '발행된 수'가 아니라 '기록기가 받은 수'다. 포화 구간이 섞이면 받은 수가 줄므로 @시작초,길이초 로 포화 전 구간만 볼 수 있다.
  로버 움직임: 없음.
  사용: anal_bag_rates.py 이름=bag폴더[@시작초,길이초] ...   (시작초 = bag 첫 메시지 기준) — 토픽마다 bag 별 Hz · 평균 크기(B) · kB/s, 끝에 합계
        anal_bag_rates.py --bins 10 --topic /tf [--tf-pairs] 이름=bag ...        — 옛 anal_tf_rate: 칸마다 /tf 메시지 Hz(+ 프레임 쌍별 변환 Hz 상위 8)
        anal_bag_rates.py --bins 10 --topic /trajectories 이름=bag ...           — 옛 anal_traj_size: 칸마다 Hz · 크기 중앙 kB, 전체 크기 중앙/최소/최대 · MB/s
  출력: 표준 출력."""
import sys, time, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent)); import lib_rover as L
args = sys.argv[1:]; BINS = None; TOPIC = None; PAIRS = False; runs = []
while args:
    a = args.pop(0)
    if a == '--bins': BINS = float(args.pop(0))
    elif a == '--topic': TOPIC = args.pop(0)
    elif a == '--tf-pairs': PAIRS = True
    else:
        name, rest = a.split('=', 1); win = None
        if '@' in rest: rest, w = rest.rsplit('@', 1); win = tuple(float(x) for x in w.split(','))
        runs.append((name, rest, win))

if BINS:   # 시간 칸 모드 — 한 토픽
    for name, path, win in runs:
        H = collections.defaultdict(list); P = collections.defaultdict(collections.Counter); t0 = None; first = None
        with L.open_bag(path) as r:
            con = [c for c in r.connections if c.topic == TOPIC]
            # rosbags 는 빈 목록을 주면 '전부' 를 읽는다 — 토픽이 없으면 멈춤(Git Bash 는 '/tf' 인자를 경로로 바꿈 → MSYS_NO_PATHCONV=1, 11-19 §3)
            if not con: sys.exit('%s: 토픽 %r 없음 — 있는 것: %s' % (name, TOPIC, ' '.join(sorted({c.topic for c in r.connections}))))
            if TOPIC == '/tf': print('== %s  /tf 연결(발행자별 기록) %d 개, 메시지 수 %s' % (name, len(con), sorted((c.msgcount for c in con), reverse=True)[:8]))
            for c, t_ns, raw in r.messages(connections=con):
                t = t_ns * 1e-9; t0 = t0 or t
                if win and not (win[0] <= t - t0 < win[0] + win[1]): continue
                b = int((t - t0) // BINS); H[b].append(len(raw))
                if PAIRS or first is None:
                    m = r.deserialize(raw, c.msgtype)
                    if first is None: first = (len(m.markers), collections.Counter(x.ns for x in m.markers)) if hasattr(m, 'markers') else None
                    if PAIRS:
                        for x in m.transforms: P[b]['%s→%s' % (x.header.frame_id, x.child_frame_id)] += 1
        allb = [x for v in H.values() for x in v]
        if TOPIC != '/tf': print('== %s  %s 메시지 %d%s' % (name, TOPIC, len(allb), ' · 첫 메시지 마커 %s' % (first,) if first else ''))
        if not allb: continue
        print('   크기 kB 중앙 %.0f 최소 %.0f 최대 %.0f → 평균 %.2f MB/s' % (np.median(allb) / 1e3, min(allb) / 1e3, max(allb) / 1e3, sum(allb) / 1e6 / (BINS * len(H))))
        keys = [k for k, _ in sum(P.values(), collections.Counter()).most_common(8)] if PAIRS else []
        print('   시각      Hz     kB(중앙)' + ''.join('%19s' % k[:18] for k in keys))
        for b in sorted(H):
            print('   %s %6.1f %8.1f' % (time.strftime('%H:%M:%S', time.localtime(t0 + BINS * b)), len(H[b]) / BINS, np.median(H[b]) / 1e3) + ''.join('%19.1f' % (P[b][k] / BINS) for k in keys))
    sys.exit()

R = {}; allt = set()
for name, path, win in runs:
    n = collections.Counter(); by = collections.Counter(); t0 = None; t1 = None
    with L.open_bag(path) as rd:
        for c, t, raw in rd.messages():
            if t0 is None: t0 = t
            s = (t - t0) / 1e9
            if win and (s < win[0] or s >= win[0] + win[1]): continue
            n[c.topic] += 1; by[c.topic] += len(raw); t1 = s
    dur = win[1] if win else t1
    R[name] = (n, by, dur); allt |= set(n)
    print('%s: %s, 구간 %.0f s%s' % (name, path, dur, ' (시작 %.0f s 부터)' % win[0] if win else ''))
names = [r[0] for r in runs]
print('\n%-44s' % '토픽' + ''.join('%26s' % ('%s Hz·B·kB/s' % x) for x in names))
tot = collections.Counter(); totn = collections.Counter()
key = lambda t: -max(R[x][1][t] / R[x][2] for x in names)
for t in sorted(allt, key=key):
    row = '%-44s' % t[:44]
    for x in names:
        n, by, d = R[x]
        row += '%26s' % ('%.1f · %d · %.1f' % (n[t] / d, by[t] / max(n[t], 1), by[t] / d / 1e3) if n[t] else '-')
        tot[x] += by[t] / d / 1e3; totn[x] += n[t] / d
    print(row)
print('%-44s' % '합계(메시지/s · kB/s)' + ''.join('%26s' % ('%.0f · %.0f' % (totn[x], tot[x])) for x in names))
