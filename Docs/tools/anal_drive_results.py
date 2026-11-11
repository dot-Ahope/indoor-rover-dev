#!/usr/bin/env python3
"""anal_drive_results — F0 러너 로그에서 목표별 결과 · 소요 시간 · 도착 오차를 모아 성공률 · 사이클타임 표를 만든다 (2026-11-10, PC, 로버 안 움직임).
  왜: 주행 결과가 날짜별 run_*.txt · f0_*.log · bags/ 사본에 흩어져 있어 '구성별 성공률 · 같은 구간 소요 시간' 을 한눈에 못 봄(11-10 SUMMARY §4).
  읽는 것: Docs/debug_log/<날짜>/ 아래 .log · .txt 중 '########## F0 주행' 머리줄이 있는 것(09-23 이후 러너 형식). 머리줄 · '목표 N 출발' · '목표 N <상태>' · '결과:' 줄만 본다.
  중복: 날짜 · 머리줄 시각 · 목표 문자열이 같으면 한 주행(outputs/ 를 bags/ 보다 우선).
  판정: 목표 성공 = SUCCEEDED 또는 SUCCEEDED_XY(위치만 목표 'f' — 러너가 xy 도달 뒤 일부러 취소, job550 169 행), 주행 성공 = 계획 목표 전부 성공,
        실패 뒤 출발 안 한 목표 = '시도 안 함'. CANCELED 는 러너 한도 초과(로그 '★ 목표 N 한도 초과')와 그 밖(nav_guard · 사람 등)으로 나눈다.
        사이클타임 구간 = (이전 목표 → 이 목표) 좌표 쌍, 목표 1 의 이전은 '출발'.
  접촉: <폴더>/anal_drive_contacts.csv(date,run,class,touched,source,evidence — 그날 SUMMARY 결과 서술에서 사람이 · 에이전트가 분류, 11-10 §5)가 있으면
        주행마다 붙이고 기간 표에 '접촉 있음 / 없음 확인 / 기록 없음' 을 더한다. 없으면 접촉 열은 비운다.
  인자: [--out <폴더>] (기본 Docs/debug_log/2026-11-10/outputs). 출력: <폴더>/anal_drive_results_runs.csv · _goals.csv, 표준 출력에 요약 표(마크다운)."""
import csv, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DL = ROOT / 'Docs/debug_log'
OUT = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else DL / '2026-11-10/outputs'
sys.stdout.reconfigure(encoding='utf-8')

HEAD = re.compile(r'#+ F0 주행 (\d\d:\d\d:\d\d) — 목표 (\S+)')
START = re.compile(r'^목표 (\d+) 출발: map \(([-\d.]+), ([-\d.]+), ([-\d.]+)°\), 거리 ([\d.]+) m, 한도 (\d+) s')
END = re.compile(r'^\s*목표 (\d+) ([A-Z_]+) ([\d.]+) s \| 도착 map \(([-\d.]+), ([-\d.]+), ([-\d.]+)°\) 목표 대비 ([\d.]+) m, ([-\d.]+)°')
TOTAL = re.compile(r'^결과: .*\| 총 ([\d.]+) s')
LIMIT = re.compile(r'★ 목표 (\d+) 한도 초과')
OK = ('SUCCEEDED', 'SUCCEEDED_XY')


def run_name(p):
    """파일 이름에서 주행 이름: run_f2m1.txt · f0_f2a1_runner.log · f0_f2v1_1020.log · j555_f0a1.txt → f2m1 · f2a1 · f2v1 · f0a1"""
    s = p.stem
    s = re.sub(r'^(run_|f0_|j\d+[a-z]?_)', '', s)
    s = re.sub(r'_(runner|\d{4})$', '', s)
    return s


def parse(p, date):
    runs, cur = [], None
    for ln in p.read_text(encoding='utf-8', errors='replace').splitlines():
        m = HEAD.search(ln)
        if m:
            cur = {'date': date, 'time': m.group(1), 'spec': m.group(2), 'name': run_name(p),
                   'n_plan': len(m.group(2).split(';')), 'goals': {}, 'total': None,
                   'src': p.relative_to(ROOT).as_posix(), 'in_bags': '/bags/' in p.as_posix()}
            runs.append(cur); continue
        if not cur: continue
        if (m := START.match(ln)):
            cur['goals'].setdefault(int(m.group(1)), {}).update(
                gx=float(m.group(2)), gy=float(m.group(3)), dist=float(m.group(5)), limit=int(m.group(6)))
        elif (m := END.match(ln)):
            cur['goals'].setdefault(int(m.group(1)), {}).update(
                status=m.group(2), t=float(m.group(3)), err_m=float(m.group(7)), err_deg=float(m.group(8)))
        elif (m := TOTAL.match(ln)):
            cur['total'] = float(m.group(1))
        elif (m := LIMIT.search(ln)):
            cur['goals'].setdefault(int(m.group(1)), {})['limit_hit'] = True
    return runs


runs = {}
for d in sorted(x for x in DL.iterdir() if x.is_dir() and re.match(r'\d{4}-\d\d-\d\d$', x.name) and x.name >= '2026-09-23'):
    for p in sorted(d.rglob('*')):
        if p.suffix not in ('.log', '.txt') or not p.is_file(): continue
        try:
            if 'F0 주행' not in p.read_text(encoding='utf-8', errors='replace'): continue
        except OSError:
            continue
        for r in parse(p, d.name):
            k = (r['date'], r['time'], r['spec'])
            if k not in runs or (runs[k]['in_bags'] and not r['in_bags']):
                runs[k] = r

OUT.mkdir(parents=True, exist_ok=True)
CONTACT = {}
if (OUT / 'anal_drive_contacts.csv').exists():
    with open(OUT / 'anal_drive_contacts.csv', encoding='utf-8') as f:
        for c in csv.DictReader(f): CONTACT[(c['date'], c['run'])] = c
rows_run, rows_goal = [], []
for (date, tm, spec), r in sorted(runs.items()):
    g = r['goals']
    done = [i for i in g if 'status' in g[i]]
    for i in done:   # 취소 원인 구분
        if g[i]['status'] == 'CANCELED':
            g[i]['status'] = 'CANCELED_LIMIT' if g[i].get('limit_hit') else 'CANCELED_OTHER'
    ok = [i for i in done if g[i]['status'] in OK]
    if r['total'] is None and not done:
        verdict = '결과 줄 없음'
    else:
        verdict = '성공' if len(ok) == r['n_plan'] else '실패'
    first_fail = next((f"{i}:{g[i]['status']}" for i in sorted(done) if g[i]['status'] not in OK), '')
    rows_run.append({'date': date, 'time': tm, 'name': r['name'], 'plan': r['n_plan'], 'tried': len(done), 'succeeded': len(ok),
                     'not_tried': r['n_plan'] - len(done), 'verdict': verdict, 'first_fail': first_fail,
                     'total_s': r['total'] if r['total'] is not None else '',
                     'contact': CONTACT.get((date, r['name']), {}).get('class', ''),
                     'touched': CONTACT.get((date, r['name']), {}).get('touched', ''), 'src': r['src']})
    prev = '출발'
    for i in sorted(g):
        x = g[i]
        if 'status' not in x: continue
        here = '(%.1f, %.1f)' % (x['gx'], x['gy']) if 'gx' in x else '?'
        seg_key, prev = '%s → %s' % (prev, here), here
        rows_goal.append({'date': date, 'name': r['name'], 'goal': i, 'segment': seg_key, 'gx': x.get('gx', ''), 'gy': x.get('gy', ''),
                          'dist_m': x.get('dist', ''), 'limit_s': x.get('limit', ''), 'status': x['status'], 't_s': x['t'],
                          'v_mps': round(x['dist'] / x['t'], 3) if x.get('dist') and x['t'] > 0 else '',
                          'err_m': x['err_m'], 'err_deg': x['err_deg']})

for fn, rows in (('anal_drive_results_runs.csv', rows_run), ('anal_drive_results_goals.csv', rows_goal)):
    with open(OUT / fn, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def med(v):
    v = sorted(v); n = len(v)
    return (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2) if n else float('nan')


print('## 날짜별 성공률')
print('| 날짜 | 주행 | 주행 성공 | 목표 시도 | 목표 성공 | 시도 안 함 | 결과 줄 없음 | 실패 상태 |')
print('|---|---|---|---|---|---|---|---|')
by = defaultdict(list)
for r in rows_run: by[r['date']].append(r)
tot = defaultdict(int)
for date in sorted(by):
    rs = by[date]; full = [r for r in rs if r['verdict'] != '결과 줄 없음']
    st = defaultdict(int)
    for x in rows_goal:
        if x['date'] == date and x['status'] not in OK: st[x['status']] += 1
    vals = (len(full), sum(r['verdict'] == '성공' for r in full), sum(r['tried'] for r in rs), sum(r['succeeded'] for r in rs),
            sum(r['not_tried'] for r in full), len(rs) - len(full))
    for k, v in zip(('runs', 'ok', 'tried', 'gok', 'nt', 'nores'), vals): tot[k] += v
    print('| %s | %d | %d | %d | %d | %d | %d | %s |' % ((date,) + vals + (' · '.join('%s %d' % kv for kv in sorted(st.items())) or '-',)))
print('| **합계** | %(runs)d | %(ok)d | %(tried)d | %(gok)d | %(nt)d | %(nores)d | |' % tot)

print('\n## 구간(이전 목표 → 목표)별 사이클타임 — 성공만, 시도 5 회 이상')
print('| 구간 | 시도 | 성공 | 성공률 | 소요 중앙값 s | 최소~최대 s | 직선 거리 m | 진행 속도 중앙값 m/s | 도착 오차 중앙값 m | 방향 오차 중앙값 ° |')
print('|---|---|---|---|---|---|---|---|---|---|')
seg = defaultdict(list)
for x in rows_goal: seg[x['segment']].append(x)
for k, xs in sorted(seg.items(), key=lambda kv: -len(kv[1])):
    if len(xs) < 5: continue
    s = [x for x in xs if x['status'] in OK]
    t = [x['t_s'] for x in s]
    print('| %s | %d | %d | %.0f %% | %.1f | %.1f~%.1f | %.2f | %.3f | %.3f | %.1f |' % (
        k, len(xs), len(s), 100 * len(s) / len(xs), med(t), min(t, default=0), max(t, default=0),
        med([x['dist_m'] for x in xs if x['dist_m'] != '']),
        med([x['v_mps'] for x in s if x['v_mps'] != '']), med([x['err_m'] for x in s]), med([abs(x['err_deg']) for x in s])))
# 기간 = 구성이 크게 바뀐 날(CURRENT_STACK · CLAUDE.md 기준). 날짜 경계만 쓰므로 같은 기간 안의 A/B 시험 구성 차이는 섞인다.
PERIODS = [('09-23', '09-29', 'F0 코스(왕복 · 문 통과), nvblox 채택 직후'),
           ('10-01', '10-08', 'F2 첫 순회(지도 v2 → v3), 계획기 · 지도 불일치 시기'),
           ('10-12', '10-15', 'PreferForward 15 · 궤적 lite · CopyPath · MonotoneEscape'),
           ('10-19', '10-22', '프로젝터 끔 · 깊이 프리셋 3 · cuVSLAM 시험'),
           ('10-23', '10-28', 'cuVSLAM 기본 + Smac 시험 · SLAM timeout 1.5')]
print('\n## 기간별(구성 변경 날짜 기준)')
print('| 기간 | 주요 구성 | 주행 성공 / 주행 | 목표 성공 / 시도 | 접촉(장애물) · 바닥 전선 · 없음 확인 · 기록 없음 | 성공 + 접촉 없음 확인 | 출발 → (2.2, -1.6) 중앙값 s (n) | (5.5, -2.2) → (0.0, 0.0) 중앙값 s (n) |')
print('|---|---|---|---|---|---|---|---|')
for a, b, desc in PERIODS:
    inp = lambda d: a <= d[5:] <= b
    rs = [r for r in rows_run if inp(r['date']) and r['verdict'] != '결과 줄 없음']
    gs = [x for x in rows_goal if inp(x['date'])]
    def seg_med(k):
        t = [x['t_s'] for x in gs if x['segment'] == k and x['status'] in OK]
        return '%.1f (%d)' % (med(t), len(t)) if t else '-'
    cc = lambda k: sum(r['contact'] == k for r in rs)
    clean = sum(r['verdict'] == '성공' and r['contact'] == 'NO_CONTACT' for r in rs)
    print('| %s ~ %s | %s | %d / %d | %d / %d | %d · %d · %d · %d | %d / %d | %s | %s |' % (
        a, b, desc, sum(r['verdict'] == '성공' for r in rs), len(rs), sum(x['status'] in OK for x in gs), len(gs),
        cc('CONTACT'), cc('FLOOR'), cc('NO_CONTACT'), cc('UNKNOWN') + cc('') + cc('AMBIGUOUS'), clean, len(rs),
        seg_med('출발 → (2.2, -1.6)'), seg_med('(5.5, -2.2) → (0.0, 0.0)')))
print('\n주행 %d · 목표 결과 %d 줄 → %s' % (len(rows_run), len(rows_goal), OUT.relative_to(ROOT).as_posix()))
