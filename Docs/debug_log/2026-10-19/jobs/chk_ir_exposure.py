#!/usr/bin/env python3
"""chk_ir_exposure — 번갈이 카메라에서 IR 노출 · 게인을 실행 중에 바꿔 가며, 끈 IR 의 밝기 · 특징 수와 켠 깊이 유효 비율을 잰다. (2026-10-19 §24, Jetson, 로버 정지)
  설정: (자동) → 수동 (노출 µs, 게인) 목록. 각 설정 뒤 1.5 s 기다리고 4 s 측정.
  분류: 각 프레임 메타데이터 frame_emitter_mode == 0 이면 켬(§15 S1). 실제 노출 · 게인 = 메타데이터 actual_exposure · gain_level."""
import time, re
import numpy as np, cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from sensor_msgs.msg import Image
from realsense2_camera_msgs.msg import Metadata

C = '/camera/camera'; fast = cv2.FastFeatureDetector_create(threshold=20)
SETS = [('auto', None, None), ('e16 g16', 16000, 16), ('e30 g16', 30000, 16), ('e30 g64', 30000, 64), ('e30 g128', 30000, 128), ('e30 g248', 30000, 248), ('e16 g248', 16000, 248)]
ns = lambda h: h.stamp.sec * 1000000000 + h.stamp.nanosec


class M(Node):
    def __init__(self):
        super().__init__('chk_ir_exposure'); self.meta = {}; self.ir = []; self.dp = []; self.on = False
        q = qos_profile_sensor_data
        for s in ('infra1', 'depth'):
            self.create_subscription(Metadata, '%s/%s/metadata' % (C, s), lambda m, s=s: self.on_meta(s, m), q)
        self.create_subscription(Image, C + '/infra1/image_rect_raw', self.on_ir, q)
        self.create_subscription(Image, C + '/depth/image_rect_raw', self.on_depth, q)
        self.cli = self.create_client(SetParameters, C + '/set_parameters')

    def on_meta(self, s, m):
        g = lambda k: (lambda r: int(r.group(1)) if r else -1)(re.search('"%s":(-?\\d+)' % k, m.json_data))
        self.meta[(s, ns(m.header))] = (g('frame_emitter_mode'), g('actual_exposure'), g('gain_level'))

    def on_ir(self, m):
        if self.on: self.ir.append((ns(m.header), np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.step)[:, :m.width].copy()))

    def on_depth(self, m):
        if self.on: self.dp.append((ns(m.header), float(np.count_nonzero(np.frombuffer(bytes(m.data), np.uint16))) / (m.width * m.height)))

    def setp(self, kv):
        req = SetParameters.Request()
        for k, v in kv:
            p = Parameter(); p.name = k
            p.value = ParameterValue(type=ParameterType.PARAMETER_BOOL, bool_value=v) if isinstance(v, bool) else ParameterValue(type=ParameterType.PARAMETER_INTEGER, integer_value=int(v))
            req.parameters.append(p)
        f = self.cli.call_async(req); rclpy.spin_until_future_complete(self, f, timeout_sec=5.0)
        return [r.successful for r in f.result().results] if f.result() else None


rclpy.init(); n = M(); n.cli.wait_for_service(timeout_sec=10)
spin = lambda s: [rclpy.spin_once(n, timeout_sec=0.02) for _ in range(int(s / 0.02))]
print('%-9s %-14s %-24s %-30s %s' % ('설정', '실제 노출·게인', '끈 IR 밝기 · FAST 중앙', '(5~95 %)', '켠 깊이 유효'))
for nm, e, g in SETS:
    ok = n.setp([('depth_module.enable_auto_exposure', True)]) if e is None else n.setp([('depth_module.enable_auto_exposure', False), ('depth_module.exposure', e), ('depth_module.gain', g)])
    spin(1.5); n.ir.clear(); n.dp.clear(); n.on = True; spin(4.0); n.on = False; spin(0.3)
    off = [a for t, a in n.ir if n.meta.get(('infra1', t), (-1,))[0] == 1]
    eg = [n.meta[('infra1', t)][1:] for t, a in n.ir if ('infra1', t) in n.meta]
    don = [v for t, v in n.dp if n.meta.get(('depth', t), (-1,))[0] == 0]
    fc = [len(fast.detect(a, None)) for a in off]; br = [float(a.mean()) for a in off]
    print('%-9s %-14s 밝기 %5.1f · FAST %5.0f       (%4.0f~%4.0f, 끈 %d 장)        %.3f (%d 장)  설정 결과 %s'
          % (nm, '%s·%s' % (int(np.median([x[0] for x in eg])) if eg else '?', int(np.median([x[1] for x in eg])) if eg else '?'),
             np.median(br) if br else -1, np.median(fc) if fc else -1, *(np.percentile(fc, [5, 95]) if fc else (-1, -1)), len(off),
             np.median(don) if don else -1, len(don), ok))
n.setp([('depth_module.enable_auto_exposure', True)]); n.destroy_node(); rclpy.shutdown()
