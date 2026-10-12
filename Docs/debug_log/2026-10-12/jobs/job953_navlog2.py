# 10-12 §2: f2f1 복귀 상자 구간(10:35:00~10:35:45) Nav2 로그 — 반복 경고는 초당 횟수로, 나머지는 원문. + 주행 전체의 종류별 횟수
import re, time, glob, collections
T0, T1 = 1791768900, 1791768945; A0, A1 = 1791768716, 1791768975
rep = collections.Counter(); allc = collections.Counter(); out = []
for f in ['/tmp/nav2.log']:
    for l in open(f, errors='replace'):
        m = re.search(r'\[(\d{10})\.(\d+)\]', l)
        if not m or not ('WARN' in l or 'ERROR' in l): continue
        t = int(m.group(1))
        if not (A0 <= t <= A1): continue
        kind = ('루프 미달' if 'missed its desired rate' in l else 'BT 틱 초과' if 'tick rate' in l else '전역 nvblox TF 미래' if 'NvbloxCostmapLayer' in l and 'global' in l else
                '로컬 nvblox TF' if 'NvbloxCostmapLayer' in l else 'transformPose 실패' if 'transformPose' in l else '경로 프레임 변환 실패' if 'Unable to transform robot pose' in l else
                'follow_path 중단' if 'follow_path' in l and 'Abort' in l else 'smoother 충돌' if 'Smoothed path leads' in l else 'smooth 중단/시간초과' if 'smooth' in l else
                '서버 응답 시간초과' if 'Timed out' in l else '기타')
        allc[kind] += 1
        if T0 <= t <= T1:
            if kind in ('루프 미달', 'BT 틱 초과'): rep[(t, kind)] += 1
            else: out.append((t, re.sub(r'\[\d{10}\.\d+\] ', '', l.strip())[:200]))
print('주행 전체(10:31:56~10:36:15) 종류별:', dict(allc))
print('-- 10:35:00~10:35:45 원문(반복 경고 제외)')
last = None
for t, l in out:
    if l != last: print(time.strftime('%H:%M:%S', time.localtime(t)), l); last = l
print('-- 초당 반복 경고(루프 미달 / BT 틱 초과)')
for t in range(T0, T1 + 1):
    a, b = rep[(t, '루프 미달')], rep[(t, 'BT 틱 초과')]
    if a or b: print(time.strftime('%H:%M:%S', time.localtime(t)), a, b)
