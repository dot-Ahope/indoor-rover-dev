#!/usr/bin/env python3
"""mk_ekf_replay_params — ekf.yaml(주행 구성)에서 재실행 변형 V0~V3 파라미터 파일을 만든다. (2026-10-20 §5)
  모두 publish_tf false · use_sim_time true. odom1 = /vslam/odom(base_link 몸 기준 속도) — 쓰는 축만 다름. 인자: ekf.yaml 출력.yaml"""
import sys, yaml, copy
base = yaml.safe_load(open(sys.argv[1], encoding='utf-8'))['ekf_filter_node']['ros__parameters']
F = [False] * 15
def cfg(vx=False, vy=False, vyaw=False):
    c = list(F); c[6], c[7], c[11] = vx, vy, vyaw; return c
V = {'v0': None, 'v1': cfg(vyaw=True), 'v2': cfg(True, True, True), 'v3': cfg(True, True, False)}
out = {}
for nm, c in V.items():
    p = copy.deepcopy(base); p.update({'publish_tf': False, 'use_sim_time': True})
    if c: p.update({'odom1': '/vslam/odom', 'odom1_config': c, 'odom1_queue_size': 10, 'odom1_nodelay': True, 'odom1_differential': False, 'odom1_relative': False})
    out['ekf_' + nm] = {'ros__parameters': p}
yaml.safe_dump(out, open(sys.argv[2], 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False)
print('변형', list(out))
