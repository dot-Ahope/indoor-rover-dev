#!/usr/bin/env python3
"""09-29 §13 G3: stuck_monitor 판정 로직을 bag 시간으로 재생하는 오프라인 평가기(기존 OLD / 수정 NEW 비교).
   stuck_monitor.py 의 profile·rot_shift_deg·sector_delta 를 설치본에서 그대로 가져오고, tick() 판정 식을 옮겼다(5 Hz, 창 2 s,
   v_thr 0.015, w_thr 0.10, ratio 0.25, confirm 2, cooldown 5 s — 코드 기본값·launch 값 동일).
   차이: 복구 행동(backup 등) 보류는 bag 에 상태 토픽이 없어 생략(F0·회전·직진 시험엔 복구 행동이 없었음 — 러너 로그 기준).
   OLD: 회전 보정 roll = 스캔 상관, 회전 관측 = max(|스캔|, 자이로)
   NEW: 자이로가 창 안에 있으면 roll = 자이로 누적(부호 있음), 회전 관측 = |자이로|; 없으면 OLD 와 같음
   인자: BAG [BAG ...]"""
import sys, math, importlib.util
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message

sp = importlib.util.spec_from_file_location('sm', '/home/jetson/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py')
sm = importlib.util.module_from_spec(sp); sp.loader.exec_module(sm)
W, VT, WT, RATIO, CONF, COOL, RATE = 2.0, 0.015, 0.10, 0.25, 2, 5.0, 5.0


def integ(seq, now, idx, signed=False):
    pts = [x for x in seq if now - W <= x[0] <= now]
    if len(pts) < 2: return 0.0
    f = (lambda v: v) if signed else abs
    return sum(f(pts[i][idx]) * (pts[i][0] - pts[i - 1][0]) for i in range(1, len(pts)))


def run(bag):
    r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=bag, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
    types = {t.name: t.type for t in r.get_all_topics_and_types()}
    cmds, scans, gyro = [], [], []
    while r.has_next():
        tp, data, ts = r.read_next(); t = ts * 1e-9
        if tp == '/cmd_vel': m = deserialize_message(data, get_message(types[tp])); cmds.append((t, m.linear.x, m.angular.z))
        elif tp == '/scan': scans.append((t, sm.profile(deserialize_message(data, get_message(types[tp])))))
        elif tp == '/imu/data': m = deserialize_message(data, get_message(types[tp])); gyro.append((t, -m.angular_velocity.y))
    out = {}
    st = [s[0] for s in scans]
    for mode in ('OLD', 'NEW'):
        hits, last, ev = 0, -1e9, []
        t = scans[0][0] + W + 0.5; gi = 0
        while t < scans[-1][0]:
            dc, ac = integ(cmds, t, 1), integ(cmds, t, 2)
            if not (dc >= VT * W or ac >= WT * W): hits = 0; t += 1 / RATE; continue
            k1 = np.searchsorted(st, t, 'right') - 1; k0 = np.searchsorted(st, t - W, 'right') - 1
            if k0 < 0 or k1 <= k0: t += 1 / RATE; continue
            A, B = scans[k0][1], scans[k1][1]
            rs = sm.rot_shift_deg(A, B)
            gw = [g for g in gyro if t - W <= g[0] <= t] if gyro else []
            g_abs = math.degrees(integ(gyro, t, 1)); g_sig = math.degrees(integ(gyro, t, 1, signed=True))
            if mode == 'NEW' and len(gw) > 10:
                roll, rot_obs = g_sig, abs(g_sig) if False else g_abs
            else:
                roll, rot_obs = rs, max(abs(rs) if rs is not None else 0.0, g_abs)
            Br = np.roll(B, int(round(roll))) if roll is not None else B
            f, b = sm.sector_delta(A, Br, 0), sm.sector_delta(A, Br, 180)
            tr = max(abs(f) if f is not None else 0.0, abs(b) if b is not None else 0.0)
            ratios = []
            if dc >= VT * W and (f is not None or b is not None): ratios.append(tr / dc)
            if ac >= WT * W: ratios.append(rot_obs / math.degrees(ac))
            if not ratios: hits = 0; t += 1 / RATE; continue
            rr = max(ratios); hits = hits + 1 if rr < RATIO else 0
            if hits >= CONF and t - last > COOL:
                last = t; hits = 0
                ev.append('t %.1f s: 지령 %.1fcm/%.0f° 관측 %.1fcm/%.1f° 비율 %.2f (스캔회전 %s, 자이로 %+.1f°)' % (t - cmds[0][0], 100 * dc, math.degrees(ac), 100 * tr, rot_obs, rr, 'None' if rs is None else '%+.1f' % rs, g_sig))
            t += 1 / RATE
        out[mode] = ev
    return out, len(gyro)


tot = {'OLD': 0, 'NEW': 0}
for b in sys.argv[1:]:
    o, ng = run(b)
    name = b.rstrip('/').split('/')[-1]
    print('%-12s 자이로 %5d | OLD %d 건 | NEW %d 건' % (name, ng, len(o['OLD']), len(o['NEW'])))
    for m in ('OLD', 'NEW'):
        tot[m] += len(o[m])
        for e in o[m]: print('   %s %s' % (m, e))
print('합계 OLD %d 건, NEW %d 건' % (tot['OLD'], tot['NEW']))
