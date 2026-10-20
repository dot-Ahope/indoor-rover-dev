#!/usr/bin/env python3
# (10-20 §7.3) 빈 노드 — 참가자 수 · 재기동 소란 역
import sys, rclpy
from rclpy.node import Node
rclpy.init(); rclpy.spin(Node(sys.argv[1]))
