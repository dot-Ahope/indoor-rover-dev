#!/usr/bin/env python3
# (10-20 §7.3) 구독 역 — 두 줄 수신 수를 매초 파일에 덮어씀("시각 n1 n2"), pid 도 파일로. 인자: 노드 이름 상태파일
import sys, os, time, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
name, out = sys.argv[1], sys.argv[2]
open(out + '.pid', 'w').write(str(os.getpid()))
rclpy.init(); n = Node(name); c = [0, 0]
for i in (0, 1): n.create_subscription(Image, '/shmt/ir%d' % (i + 1), lambda m, i=i: c.__setitem__(i, c[i] + 1), qos_profile_sensor_data)
def dump():
    open(out + '.tmp', 'w').write('%.3f %d %d\n' % (time.time(), c[0], c[1])); os.replace(out + '.tmp', out)
n.create_timer(1.0, dump); rclpy.spin(n)
