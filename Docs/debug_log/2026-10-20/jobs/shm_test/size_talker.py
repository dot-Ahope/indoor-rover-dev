#!/usr/bin/env python3
# (10-20 §7.5) 크기 바꿔 가며 발행 — 인자: 이름 폭 높이 화소바이트(1|2) 줄수(1|2). 15 Hz, 토픽 /shmt/ir1 [/shmt/ir2]
import sys, rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
name, W, H, B, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
rclpy.init(); n = Node(name)
pubs = [n.create_publisher(Image, '/shmt/ir%d' % i, 5) for i in range(1, N + 1)]
m = Image(); m.height, m.width, m.encoding, m.step = H, W, ('mono8' if B == 1 else '16UC1'), W * B; m.data = bytes(W * H * B)
def tick():
    m.header.stamp = n.get_clock().now().to_msg()
    for p in pubs: p.publish(m)
n.create_timer(1 / 15.0, tick); rclpy.spin(n)
