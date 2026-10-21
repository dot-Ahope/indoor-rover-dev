#!/usr/bin/env python3
"""anal_mx1 — 10-21 §19 번갈이 중 수동 노출 · 게인 시험(시험 컨테이너 안, 로버 안 움직임).
  카메라 노드(/camera/camera, 4.51.1 토픽 /camera/...)의 파라미터를 단계별로 바꾸고 2 s 안정 + 6 s 측정.
  프레임을 메타데이터 frame_emitter_mode 로 두 무리로 나눠 깊이 유효 비율이 높은 쪽 = 실제 켬.
  인자: 60|30 (최대 노출: 60 → 16000 µs, 30 → 32000 µs) [이름] — 이름을 주면(§19.2 mx2) 파라미터를 안 바꾸고 기동 상태 그대로 한 번만 잰다"""
import sys, time, re
import numpy as np, cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as Q
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from sensor_msgs.msg import Image
from realsense2_camera_msgs.msg import Metadata
FPS = sys.argv[1] if len(sys.argv) > 1 else '60'
EXP = 16000 if FPS == '60' else 32000
C = '/camera'
ns = lambda h: h.stamp.sec * 1000000000 + h.stamp.nanosec
F20 = cv2.FastFeatureDetector_create(threshold=20); F5 = cv2.FastFeatureDetector_create(threshold=5)
num = lambda key, s: (lambda g: int(g.group(1)) if g else None)(re.search(r'"%s":(\d+)' % key, s))


def lap(a):
    a = a.astype(np.int16); return float(np.abs(4 * a[1:-1, 1:-1] - a[:-2, 1:-1] - a[2:, 1:-1] - a[1:-1, :-2] - a[1:-1, 2:]).mean())


class M(Node):
    def __init__(self):
        super().__init__('anal_mx1')
        self.on = False; self.meta = {'depth': {}, 'infra1': {}}; self.dep = []; self.ir = []
        self.img = {'depth': [], 'infra1': []}   # §19.2 그림용: 최근 프레임 몇 장(시각, 배열)
        for s in ('depth', 'infra1'):
            self.create_subscription(Metadata, f'{C}/{s}/metadata', lambda m, s=s: self.on_meta(s, m), Q)
        self.create_subscription(Image, f'{C}/depth/image_rect_raw', self.on_dep, Q)
        self.create_subscription(Image, f'{C}/infra1/image_rect_raw', self.on_ir, Q)
        self.cli = self.create_client(SetParameters, '/camera/camera/set_parameters')

    def on_meta(self, s, m):
        self.meta[s][ns(m.header)] = (num('frame_emitter_mode', m.json_data), num('actual_exposure', m.json_data), num('gain_level', m.json_data))

    def on_dep(self, m):
        if not self.on: return
        a = np.frombuffer(bytes(m.data), np.uint16).reshape(m.height, m.width)
        self.dep.append((ns(m.header), np.count_nonzero(a) / a.size, np.count_nonzero(a[m.height // 2:]) / (a.size / 2)))
        self.img['depth'] = (self.img['depth'] + [(ns(m.header), a.copy())])[-6:]

    def on_ir(self, m):
        if not self.on: return
        a = np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width]
        self.ir.append((ns(m.header), float(a.mean()), len(F20.detect(a)), len(F5.detect(a)), lap(a)))
        self.img['infra1'] = (self.img['infra1'] + [(ns(m.header), a.copy())])[-6:]

    def setp(self, **kw):
        ps = []
        for k, v in kw.items():
            k = 'depth_module.' + k
            if isinstance(v, bool): pv = ParameterValue(type=ParameterType.PARAMETER_BOOL, bool_value=v)
            else: pv = ParameterValue(type=ParameterType.PARAMETER_INTEGER, integer_value=int(v))
            ps.append(Parameter(name=k, value=pv))
        out = []
        for p in ps:   # 하나씩(순서 보장 · 실패 항목 구분)
            f = self.cli.call_async(SetParameters.Request(parameters=[p])); t = time.time()
            while not f.done() and time.time() - t < 5: rclpy.spin_once(self, timeout_sec=0.05)
            r = f.result().results[0] if f.done() else None
            out.append('%s=%s:%s' % (p.name.split('.')[-1], kw[p.name.split('.', 1)[1]], 'ok' if r and r.successful else ('FAIL ' + (r.reason[:80] if r else 'timeout'))))
        return ' '.join(out)


def spin(n, sec):
    t = time.time()
    while time.time() - t < sec: rclpy.spin_once(n, timeout_sec=0.02)


def save_imgs(n, lab, keys):
    # §19.2: 메타 모드별 IR1 · 깊이 한 장씩 /tmp/mx_img/<이름>_<IR|depth>_m<모드>.png (IR 원본 밝기 그대로, 깊이는 0~4 m 회색, 0 = 검정)
    import os; os.makedirs('/tmp/mx_img', exist_ok=True)
    tag = re.sub(r'[^0-9A-Za-z_]', '', lab) or 'x'
    for s, nm in (('infra1', 'IR'), ('depth', 'depth')):
        for t, a in reversed(n.img[s]):
            md = n.meta[s].get(t)
            if not md: continue
            k = md[0]; f = '/tmp/mx_img/%s_%s_m%s.png' % (tag, nm, k)
            if os.path.exists(f) and os.path.getmtime(f) > time.time() - 10: continue
            if s == 'depth':
                a = np.where(a > 0, 255 - np.clip(a / 4000.0 * 230, 0, 230), 0).astype(np.uint8)
            cv2.imwrite(f, a)


def report(n, lab):
    g = {}
    for t, v, lo in n.dep:
        md = n.meta['depth'].get(t); g.setdefault(md[0] if md else None, {'d': [], 'i': [], 'm': []})['d'].append((v, lo))
    for t, b, f20, f5, lp in n.ir:
        mi = n.meta['infra1'].get(t)
        e = g.setdefault(mi[0] if mi else None, {'d': [], 'i': [], 'm': []}); e['i'].append((b, f20, f5, lp)); e['m'].append(mi)
    keys = [k for k in g if k is not None and g[k]['d']]
    save_imgs(n, lab, keys)
    onk = max(keys, key=lambda k: np.median([x[0] for x in g[k]['d']])) if keys else None
    print('[%s]' % lab)
    for k in sorted(g, key=lambda k: (k is None, k)):
        e = g[k]; tag = '켬' if k == onk else ('끔' if k is not None else '메타없음')
        d = np.array(e['d']) if e['d'] else np.zeros((0, 2)); i = np.array(e['i']) if e['i'] else np.zeros((0, 4))
        ex = [m[1] for m in e['m'] if m and m[1] is not None]; ga = [m[2] for m in e['m'] if m and m[2] is not None]
        print('  모드 %s(%s): 깊이 n %d 유효 %.3f 아래 %.3f · IR n %d 밝기 %.1f FAST20 %.0f FAST5 %.0f |lap| %.2f · 노출 %s 게인 %s' % (
            k, tag, len(d), np.median(d[:, 0]) if len(d) else -1, np.median(d[:, 1]) if len(d) else -1, len(i),
            np.median(i[:, 0]) if len(i) else -1, np.median(i[:, 1]) if len(i) else -1, np.median(i[:, 2]) if len(i) else -1, np.median(i[:, 3]) if len(i) else -1,
            int(np.median(ex)) if ex else '-', int(np.median(ga)) if ga else '-'))


rclpy.init(); n = M()
n.cli.wait_for_service(timeout_sec=10); spin(n, 3)
STEPS = [('①자동', dict(enable_auto_exposure=True)),
         ('②자동끔', dict(enable_auto_exposure=False)),
         ('③%d×16' % EXP, dict(exposure=EXP, gain=16)),
         ('④%d×64' % EXP, dict(gain=64)),
         ('⑤%d×128' % EXP, dict(gain=128)),
         ('⑥%d×248' % EXP, dict(gain=248)),
         ('⑦대조 끔+자동', dict(emitter_on_off=False, emitter_enabled=0, enable_auto_exposure=True))]
if len(sys.argv) > 2: STEPS = [(sys.argv[2], {})]
print('프로필 P%s · 최대 노출 %d µs' % (FPS, EXP))
for lab, kw in STEPS:
    if kw: print('설정 %s → %s' % (lab, n.setp(**kw)))
    spin(n, 2.0); n.dep, n.ir = [], []; n.on = True; spin(n, 6.0); n.on = False
    report(n, lab)
n.destroy_node(); rclpy.shutdown()
