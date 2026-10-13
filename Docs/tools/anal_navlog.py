# 10-12 §3.3: Nav2 로그(PC 로 회수한 사본) 요약 — 종류별 횟수(주행 창), 10 s 칸 히스토그램, 반복 아닌 경고·오류 원문. 인자: nav2.log HH:MM:SS HH:MM:SS [원문 최대 줄]
import re, sys, time, collections
def ep(s): return time.mktime(time.strptime('2026-10-12 ' + s, '%Y-%m-%d %H:%M:%S'))
A, B = ep(sys.argv[2]), ep(sys.argv[3]); N = int(sys.argv[4]) if len(sys.argv) > 4 else 60
def kind(l):
    return ('루프 미달' if 'missed its desired rate' in l else 'BT 틱 초과' if 'tick rate' in l else '전역 nvblox TF' if 'NvbloxCostmapLayer' in l else
            'TF 미래(컨트롤러)' if 'transformPose' in l or 'Unable to transform robot pose' in l else 'follow_path 중단' if 'follow_path' in l and 'Abort' in l else
            'smoother 충돌' if 'Smoothed path leads' in l or ('smooth_path' in l and 'Abort' in l) else '서버 응답 시간초과' if 'Timed out' in l else
            'PathBlockedAhead' if 'PathBlockedAhead' in l else '진행 실패' if 'Failed to make progress' in l else '계획 실패' if 'failed to create plan' in l.lower() or 'no valid path' in l.lower() else
            '최적화 실패' if 'Optimizer fail' in l or 'optimiz' in l.lower() else '기타')
cnt = collections.Counter(); hist = collections.defaultdict(collections.Counter); out = []; last = None
for l in open(sys.argv[1], errors='replace'):
    m = re.search(r'\[(\d{10})\.\d+\]', l)
    if not m or not ('WARN' in l or 'ERROR' in l): continue
    t = int(m.group(1))
    if not (A <= t <= B): continue
    k = kind(l); cnt[k] += 1; hist[int((t - A) // 10)][k] += 1
    if k not in ('루프 미달', 'BT 틱 초과', '전역 nvblox TF'):
        s = re.sub(r'\x1b\[[0-9;]*m', '', re.sub(r'\[\d{10}\.\d+\] ', '', l.strip())); key = re.sub(r'[-\d.]+', '#', s)
        if key != last: out.append(time.strftime('%H:%M:%S', time.localtime(t)) + ' ' + s[:190]); last = key
print('종류별:', dict(cnt.most_common()))
print('10 s 칸(시작 시각: 루프 미달 / BT 틱 / 그 밖):')
for b in sorted(hist): print('  %s  %3d / %3d / %s' % (time.strftime('%H:%M:%S', time.localtime(A + 10 * b)), hist[b]['루프 미달'], hist[b]['BT 틱 초과'], {k: v for k, v in hist[b].items() if k not in ('루프 미달', 'BT 틱 초과')}))
print('원문(반복 제외, 최대 %d 줄):' % N); print('\n'.join(out[:N]))
