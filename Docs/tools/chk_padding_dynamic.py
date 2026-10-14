#!/usr/bin/env python3
"""chk_padding_dynamic — 실행 중에 코스트맵 footprint_padding 을 바꾸면 실제로 반영되는지 본다. 로버는 움직이지 않는다(명령을 내지 않음). (2026-10-14)
  왜: '갇혔을 때만 패딩 0'(10-13 §14.2, 10-14 §2)을 하려면 주행 중에 패딩을 내렸다 올릴 수 있어야 한다. 이 로버의 Nav2(Humble)에서 해 본 적이 없다.
  보는 것(단계마다): ① 설정 요청이 받아들여졌나·걸린 시간 ② 발행 풋프린트(published_footprint)의 앞·옆 치수 — 패딩만큼 줄어야 한다
                    ③ 코스트맵(costmap_raw)의 내접(253)·치명(254) 칸 수 — 내접 반경이 다시 계산되면 253 칸 수가 달라진다 ④ 실행 중 파라미터 값.
  순서: 처음 값 → 0.0 → 처음 값으로 복귀. 끝날 때 반드시 처음 값으로 되돌린다(중간에 실패해도).
  사용: chk_padding_dynamic.py [local|global|both] (기본 local)"""
import sys, time, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rcl_interfaces.srv import SetParameters, GetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from geometry_msgs.msg import PolygonStamped
from nav2_msgs.msg import Costmap
which = sys.argv[1] if len(sys.argv) > 1 else 'local'
NODES = {'local': '/local_costmap/local_costmap', 'global': '/global_costmap/global_costmap'}
names = ['local', 'global'] if which == 'both' else [which]
rclpy.init(); n = Node('chk_padding_dynamic'); S = {}
for k in names:
    S[k] = dict(fp=None, cm=None, tfp=0.0, tcm=0.0)
    n.create_subscription(PolygonStamped, '/%s_costmap/published_footprint' % k, lambda m, k=k: S[k].update(fp=m, tfp=time.time()), 10)
    n.create_subscription(Costmap, '/%s_costmap/costmap_raw' % k, lambda m, k=k: S[k].update(cm=m, tcm=time.time()), QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE, durability=DurabilityPolicy.TRANSIENT_LOCAL))
    S[k]['set'] = n.create_client(SetParameters, NODES[k] + '/set_parameters'); S[k]['get'] = n.create_client(GetParameters, NODES[k] + '/get_parameters')
def spin(sec):
    t = time.time()
    while time.time() - t < sec: rclpy.spin_once(n, timeout_sec=0.05)
def call(cli, req, to=5.0):
    if not cli.wait_for_service(timeout_sec=5.0): return None
    f = cli.call_async(req); t = time.time()
    while not f.done() and time.time() - t < to: rclpy.spin_once(n, timeout_sec=0.02)
    return f.result() if f.done() else None
def getpad(k):
    r = call(S[k]['get'], GetParameters.Request(names=['footprint_padding'])); return None if r is None or not r.values else r.values[0].double_value
def setpad(k, v):
    t = time.time(); r = call(S[k]['set'], SetParameters.Request(parameters=[Parameter(name='footprint_padding', value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=float(v)))]))
    return (None if r is None else (r.results[0].successful, r.results[0].reason)), time.time() - t
def snap(k, since):
    """since 뒤에 새로 온 풋프린트·코스트맵으로 치수와 칸 수를 낸다(최대 6 s 기다림)."""
    t = time.time()
    while time.time() - t < 6 and (S[k]['tfp'] <= since or S[k]['tcm'] <= since): rclpy.spin_once(n, timeout_sec=0.05)
    fp = S[k]['fp']; cm = S[k]['cm']; o = {'fresh_fp': S[k]['tfp'] > since, 'fresh_cm': S[k]['tcm'] > since}
    if fp is not None:
        xs = [p.x for p in fp.polygon.points]; ys = [p.y for p in fp.polygon.points]; o['len'] = max(xs) - min(xs); o['wid'] = max(ys) - min(ys)   # 좌표계가 odom/map 이라 로버가 비스듬하면 축 치수가 커진다 → 변 길이로 본다
        P = list(zip(xs, ys)); e = sorted(((P[i][0] - P[(i + 1) % len(P)][0]) ** 2 + (P[i][1] - P[(i + 1) % len(P)][1]) ** 2) ** 0.5 for i in range(len(P))); o['short'] = e[0]; o['long'] = e[-1]
    if cm is not None:
        d = bytes(cm.data); o['n253'] = d.count(253); o['n254'] = d.count(254); o['cells'] = len(d)
    return o
def show(tag, k, o): print('  %-22s %s: 풋프린트 긴 변 %.3f · 짧은 변 %.3f m%s | 코스트맵 내접(253) %d 칸 · 치명(254) %d 칸%s' % (tag, k, o.get('long', float('nan')), o.get('short', float('nan')), '' if o['fresh_fp'] else ' (새 메시지 없음)', o.get('n253', -1), o.get('n254', -1), '' if o['fresh_cm'] else ' (새 메시지 없음)'), flush=True)
spin(3.0); ORIG = {}
try:
    for k in names:
        ORIG[k] = getpad(k); print('%s 코스트맵: 처음 footprint_padding = %s' % (k, ORIG[k]), flush=True)
        if ORIG[k] is None: print('  파라미터를 읽지 못함 — 건너뜀'); continue
        b = snap(k, 0.0); show('처음(%.3f)' % ORIG[k], k, b)
        for v, tag in ((0.0, '0.0 으로'), (ORIG[k], '처음 값으로 복귀')):
            t0 = time.time(); r, dt = setpad(k, v); print('  설정 요청 → %s: %s (%.2f s)' % (tag, '응답 없음' if r is None else ('받아들임' if r[0] else '거부: ' + r[1]), dt), flush=True)
            spin(1.5); a = snap(k, t0); show('%s 뒤' % tag, k, a); print('    실행 중 값 %s | 긴 변 변화 %+.1f mm · 짧은 변 변화 %+.1f mm · 내접 칸 %+d' % (getpad(k), (a.get('long', 0) - b.get('long', 0)) * 1000, (a.get('short', 0) - b.get('short', 0)) * 1000, a.get('n253', 0) - b.get('n253', 0)), flush=True)
finally:
    for k, v in ORIG.items():
        if v is not None and getpad(k) != v: print('  되돌림 재시도 %s → %s: %s' % (k, v, setpad(k, v)[0]), flush=True)
    print('끝: ' + ' · '.join('%s footprint_padding = %s' % (k, getpad(k)) for k in ORIG), flush=True)
    rclpy.shutdown()
