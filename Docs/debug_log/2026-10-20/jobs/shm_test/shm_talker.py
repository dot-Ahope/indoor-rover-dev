#!/usr/bin/env python3
# (10-20 §7.3) 카메라 역 — 640×480 mono8 두 줄을 15 Hz 로. 인자: 노드 이름
import sys, rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
rclpy.init(); n = Node(sys.argv[1] if len(sys.argv) > 1 else 'shm_talker')
pubs = [n.create_publisher(Image, '/shmt/ir%d' % i, 5) for i in (1, 2)]
m = Image(); m.height, m.width, m.encoding, m.step = 480, 640, 'mono8', 640; m.data = bytes(640 * 480)
def tick():
    m.header.stamp = n.get_clock().now().to_msg()
    for p in pubs: p.publish(m)
n.create_timer(1 / 15.0, tick); rclpy.spin(n)
