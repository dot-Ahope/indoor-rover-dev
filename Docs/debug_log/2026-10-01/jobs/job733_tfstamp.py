#!/usr/bin/env python3
"""10-01 §8.2: /tf 의 map→odom(slam_toolbox)과 odom→base_link(EKF) 발행 주기·스탬프 지연(수신 시각 − 스탬프) 10 s.
   목적: 위치 추정 모드에서 컨트롤러가 'extrapolation into the future' 로 실패한 원인 — map→odom 스탬프가 늦거나 띄엄띄엄인지."""
import time, rclpy, numpy as np
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
rclpy.init(); n = Node('tf_stamp_chk'); D = {}
def cb(m):
    now = n.get_clock().now().nanoseconds * 1e-9
    for t in m.transforms:
        k = t.header.frame_id + '→' + t.child_frame_id
        D.setdefault(k, []).append((now, t.header.stamp.sec + t.header.stamp.nanosec * 1e-9))
n.create_subscription(TFMessage, '/tf', cb, 100)
t0 = time.time()
while time.time() - t0 < 10: rclpy.spin_once(n, timeout_sec=0.05)
for k, v in D.items():
    a = np.array(v); lag = a[:, 0] - a[:, 1]; st = np.diff(np.unique(a[:, 1]))
    print('%-22s %4d 개 %.1f Hz | 지연(수신−스탬프) 중앙 %+.3f 최소 %+.3f 최대 %+.3f s | 고유 스탬프 간격 중앙 %.3f 최대 %.3f s' % (
        k, len(a), len(a) / 10, np.median(lag), lag.min(), lag.max(), np.median(st) if len(st) else -1, st.max() if len(st) else -1))
