#!/usr/bin/env python3
"""컬러 카메라 한 프레임을 /tmp/snap.jpg 로 저장 (현장 확인용). 로버는 움직이지 않는다."""
import sys, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
import cv2
rclpy.init(); n = Node('snap322'); S = {}
def cb(m):
    if 'img' in S: return
    a = np.frombuffer(m.data, dtype=np.uint8).reshape(m.height, m.width, -1)
    if m.encoding in ('rgb8',): a = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
    S['img'] = a; S['enc'] = m.encoding
n.create_subscription(Image, sys.argv[1] if len(sys.argv) > 1 else '/camera/camera/color/image_raw', cb, qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < 8 and 'img' not in S: rclpy.spin_once(n, timeout_sec=0.1)
if 'img' in S:
    cv2.imwrite('/tmp/snap.jpg', S['img'], [cv2.IMWRITE_JPEG_QUALITY, 80]); print('saved', S['img'].shape, S['enc'])
else: print('no image')
