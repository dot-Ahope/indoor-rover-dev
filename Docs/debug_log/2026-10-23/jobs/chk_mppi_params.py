#!/usr/bin/env python3
"""chk_mppi_params — nav2_params.yaml 의 controller_server(FollowPathMPPI 포함) 블록을 원문 그대로 남기고, 주행 bag 의 params.txt(실행 중 노드 파라미터)와 값 비교(2026-10-23, PC).
  왜: MPPI 추종 오차(§20.9 · §21)를 파라미터로 설명하려면 '저장소 YAML' 이 아니라 '실행 중 값' 이 근거여야 함.
      prep 이 /tmp/nav2_params_active.yaml 을 sed 로 바꾸고 launch 가 mppi_viz 로 덮으므로 둘이 다를 수 있음.
  출력(표준 출력): ① YAML controller_server 블록 원문(주석 포함, 행 번호) ② 실행 중 controller_server 의 FollowPathMPPI.* · 주기 관련 값 전체
                 ③ 주행별 YAML ↔ 실행 중 차이(YAML 에만 · 실행 중에만 · 값 다름) ④ 주행끼리 실행 중 값 차이.
  인자: nav2_params.yaml name=bag [...]"""
import sys, ast
from pathlib import Path
import yaml


def flat(d, pre=''):
    out = {}
    for k, v in d.items():
        key = pre + str(k)
        if isinstance(v, dict): out.update(flat(v, key + '.'))
        else: out[key] = v
    return out


def parse_params(txt, node='/controller_server'):
    """params.txt 의 한 노드 구간 → {이름: 값}."""
    out, on = {}, False
    for l in txt.splitlines():
        if l.startswith('/'):
            on = l.split(':')[0] == node; continue
        if on and l.startswith('  ') and ': ' in l:
            k, v = l.strip().split(': ', 1)
            try: out[k] = ast.literal_eval(v)
            except Exception: out[k] = {'True': True, 'False': False}.get(v, v)
    return out


def norm(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return round(float(v), 9)
    if isinstance(v, (list, tuple)): return tuple(norm(x) for x in v)
    return v


ypath = Path(sys.argv[1]); lines = ypath.read_text(encoding='utf-8').splitlines()
# ① 원문 블록
s = next(i for i, l in enumerate(lines) if l.startswith('controller_server:'))
e = next(i for i in range(s + 1, len(lines)) if lines[i] and not lines[i].startswith((' ', '#')))
print('### ① %s controller_server 블록 원문 (행 %d~%d) — FollowPath(RPP) 는 BT 가 안 씀(controller_id="FollowPathMPPI"), 참고로 함께 남김' % (ypath.name, s + 1, e))
for i in range(s, e): print('%4d| %s' % (i + 1, lines[i]))
Y = flat(yaml.safe_load('\n'.join(lines))['controller_server']['ros__parameters'])
runs = []
for a in sys.argv[2:]:
    n, b = a.split('=', 1); runs.append((n, parse_params((Path(b) / 'params.txt').read_text(encoding='utf-8'))))
# ② 실행 중 값(첫 주행)
n0, P0 = runs[0]
print('\n### ② 실행 중 controller_server 값(%s params.txt, RPP FollowPath.* 제외)' % n0)
for k in sorted(P0):
    if not k.startswith('FollowPath.'): print('  %s: %r' % (k, P0[k]))
# ③ YAML ↔ 실행 중
print('\n### ③ YAML ↔ 실행 중 차이(RPP FollowPath.* 제외)')
for n, P in runs:
    print('  [%s]' % n)
    for k in sorted(set(Y) | set(P)):
        if k.startswith('FollowPath.') or k.startswith('/'): continue
        if k not in P: print('    YAML 에만(실행 중 노드에 없음 = 안 읽힘): %s = %r' % (k, Y[k]))
        elif k not in Y: print('    실행 중에만(YAML 에 없음 = 기본값 또는 launch/prep 이 넣음): %s = %r' % (k, P[k]))
        elif norm(Y[k]) != norm(P[k]): print('    값 다름: %s  YAML %r → 실행 중 %r' % (k, Y[k], P[k]))
# ④ 주행끼리
print('\n### ④ 주행끼리 실행 중 값 차이(%s 기준)' % n0)
for n, P in runs[1:]:
    d = [k for k in sorted(set(P0) | set(P)) if norm(P0.get(k)) != norm(P.get(k))]
    print('  %s: %s' % (n, '없음' if not d else ', '.join('%s %r→%r' % (k, P0.get(k), P.get(k)) for k in d)))
