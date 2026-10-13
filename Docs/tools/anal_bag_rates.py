#!/usr/bin/env python3
"""anal_bag_rates — bag 여러 개의 토픽별 '기록기가 받은' 메시지 수·주기·크기를 나란히 비교한다. (2026-10-13)
  왜: PreferForward 5 와 15 에서 발행되는 데이터의 양(개수·바이트)이 다른지 확인(포화가 15 에서만 생긴 이유 후보 가리기).
  주의: bag 의 수는 '발행된 수'가 아니라 '기록기가 받은 수'다. 포화 구간이 섞이면 받은 수가 줄므로 --t0/--dur 로 포화 전 구간만 볼 수 있다.
  출력: 토픽마다 bag 별 Hz · 평균 크기(B) · kB/s, 끝에 합계.
  사용: anal_bag_rates.py 이름=bag폴더[@시작초,길이초] ...   (시작초 = bag 첫 메시지 기준)"""
import sys, collections
from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
TS = get_typestore(Stores.ROS2_HUMBLE)
runs = []
for a in sys.argv[1:]:
    name, rest = a.split('=', 1); win = None
    if '@' in rest: rest, w = rest.rsplit('@', 1); win = tuple(float(x) for x in w.split(','))
    runs.append((name, rest, win))
R = {}; allt = set()
for name, path, win in runs:
    n = collections.Counter(); by = collections.Counter(); t0 = None; t1 = None
    with AnyReader([Path(path)], default_typestore=TS) as rd:
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
