#!/usr/bin/env python3
"""anal_ctrl_rate — MPPI 컨트롤러가 10 Hz 를 실제로 내는가: nav2 로그 경고 수 + bag 의 지령 · 컨트롤러 발행 간격(2026-10-23, PC, 로버 안 움직임).
  왜: §21 B0 의 추종 오차(굽은 곳 모서리 깎기 · 상자 옆 기울어짐)를 컨트롤러 튜닝 문제로 보기 전에, 제어 주기 자체가 지켜지는지 확인.
  세는 것(nav2 로그, 노드별): 'Control loop missed its desired rate' · 'Optimizer fail to compute path' · 'extrapolation into the future'(controller_server
        와 그 밖(planner_server 의 전역 코스트맵 등) 나눔) · 'Optimizer reset'.
  간격(bag 기록 시각):
    /cmd_vel           = velocity_smoother 출력(smoothing_frequency 20 Hz, 컨트롤러 마지막 지령 뒤 velocity_timeout 0.3 s 동안 계속 냄)
                         → 컨트롤러 주기를 직접 보여 주지 않음. 요청대로 계산하되 해석 주의.
    /transformed_global_plan = MPPI 가 computeVelocityCommands 마다 1 번 발행 → 컨트롤러 틱 간격의 대리 지표(발행 · 기록 지연 포함).
    둘 다 '주행 중' 만: /transformed_global_plan 연속 구간(1.0 s 넘게 끊기면 구간 나눔 — 목표 사이 · 복구 · BT 재계획) 안의 간격.
  ⚠ bag 기록 시각은 기록기 수신 시각이라 DDS 지연 흔들림이 섞임 — 간격 > 0.2 s 는 '컨트롤러가 늦음' 의 상한 추정.
  인자: name=bag=nav2_log [...]"""
import sys, re
from pathlib import Path
import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore

TS = get_typestore(Stores.ROS2_HUMBLE)
PAT = [('missed_rate', 'Control loop missed its desired rate'), ('opt_fail', 'Optimizer fail to compute path'),
       ('extrap', 'extrapolation into the future'), ('opt_reset', 'Optimizer reset')]


def dist(dt):
    dt = np.asarray(dt)
    if not len(dt): return '없음'
    return 'n %d · 중앙 %.3f · 95 %% %.3f · 99 %% %.3f · 최대 %.3f s · >0.15 s %d · >0.2 s %d · >0.5 s %d' % (
        len(dt), np.median(dt), np.percentile(dt, 95), np.percentile(dt, 99), dt.max(), (dt > 0.15).sum(), (dt > 0.2).sum(), (dt > 0.5).sum())


def run(name, bag, log):
    print('=' * 100); print(name)
    lines = Path(log).read_text(encoding='utf-8', errors='replace').splitlines()
    for key, p in PAT:
        L = [l for l in lines if p in l]
        if key == 'extrap':
            c = sum('[controller_server' in l for l in L)
            print('  로그 %-40s %4d (controller_server %d · 그 밖 %d)' % (p, len(L), c, len(L) - c))
        else:
            print('  로그 %-40s %4d' % (p, len(L)))
    CV, TG = [], []
    with AnyReader([Path(bag)], default_typestore=TS) as rd:
        for c, t, raw in rd.messages(connections=[c for c in rd.connections if c.topic in ('/cmd_vel', '/transformed_global_plan')]):
            (CV if c.topic == '/cmd_vel' else TG).append(t * 1e-9)
    CV, TG = np.array(sorted(CV)), np.array(sorted(TG))
    # 주행 구간 = /transformed_global_plan 연속 구간
    cut = np.nonzero(np.diff(TG) > 1.0)[0]
    starts = np.r_[TG[0], TG[cut + 1]]; ends = np.r_[TG[cut], TG[-1]]
    act = sum(ends - starts)
    print('  주행 구간(컨트롤러 발행 연속) %d 개 · 합 %.1f s · 구간 사이 끊김 %s' % (len(starts), act, ', '.join('%.1f' % g for g in (starts[1:] - ends[:-1]))))
    dtg = np.concatenate([np.diff(TG[(TG >= a) & (TG <= b)]) for a, b in zip(starts, ends)])
    dcv = np.concatenate([np.diff(CV[(CV >= a) & (CV <= b)]) for a, b in zip(starts, ends)])
    print('  /transformed_global_plan 간격(주행 중, 컨트롤러 틱 대리) %s · 실효 %.2f Hz' % (dist(dtg), (len(dtg)) / act if act else 0))
    print('  /cmd_vel 간격(주행 중, smoother 20 Hz 출력)            %s' % dist(dcv))
    print('  /cmd_vel 간격(bag 전체)                                %s' % dist(np.diff(CV)))
    # 놓침 경고 밀도
    mr = sum('Control loop missed its desired rate' in l for l in lines)
    print('  주기 놓침 경고 / 주행 분 = %.1f · 컨트롤러 틱 중 놓침 경고 비율 ≈ %.1f %%' % (mr / (act / 60) if act else 0, 100 * mr / max(len(dtg), 1)))


if __name__ == '__main__':
    for a in sys.argv[1:]:
        n, b, l = a.split('=', 2); run(n, b, l)
