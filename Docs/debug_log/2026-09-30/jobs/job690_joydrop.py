#!/usr/bin/env python3
"""09-30 §4 F1-0 무선 끊김 시험: 30 s 동안 /joy 와 /cmd_vel_test(조종 출력, 로버 비구동)를 기록.
   사용자: 스틱 전진 유지 → 약 5 s 뒤 패드 전원 끔 → 10 s 뒤 다시 켬.
   판정: /joy 가 끊기거나(패드 꺼짐) 축 값이 사라진 뒤 1 s 넘게 0 아닌 linear.x 가 이어지면 불합격."""
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

rclpy.init(); n = Node('joy_drop_test')
J, C = [], []
n.create_subscription(Joy, '/joy', lambda m: J.append((time.time(), list(m.axes))), 50)
n.create_subscription(Twist, '/cmd_vel_test', lambda m: C.append((time.time(), m.linear.x, m.angular.z)), 50)
t0 = time.time()
while time.time() - t0 < 30: rclpy.spin_once(n, timeout_sec=0.02)
print('/joy %d 개, /cmd_vel_test %d 개 (30 s)' % (len(J), len(C)))
# 1 s 칸마다 요약: /joy 수·axis1 평균, cmd 수·linear.x 평균
for k in range(30):
    a, b = t0 + k, t0 + k + 1
    jj = [x for x in J if a <= x[0] < b]; cc = [x for x in C if a <= x[0] < b]
    ax1 = sum(x[1][1] for x in jj if len(x[1]) > 1) / len(jj) if jj else float('nan')
    lx = sum(x[1] for x in cc) / len(cc) if cc else float('nan')
    print('  %2d s | /joy %3d (axis1 %+.2f) | cmd %3d (vx %+.3f)' % (k, len(jj), ax1, len(cc), lx))
# /joy 공백 구간과 그 동안의 cmd
gaps = [(J[i][0], J[i + 1][0]) for i in range(len(J) - 1) if J[i + 1][0] - J[i][0] > 0.5]
for g0, g1 in gaps:
    cc = [x for x in C if g0 < x[0] < g1]
    nz = [x for x in cc if abs(x[1]) > 1e-3]
    print('/joy 공백 %.1f~%.1f s (%.1f s) 동안 cmd %d 개, 0 아닌 것 %d 개%s'
          % (g0 - t0, g1 - t0, g1 - g0, len(cc), len(nz), ', 마지막 0 아닌 cmd 공백 시작 뒤 %.2f s' % (nz[-1][0] - g0) if nz else ''))
if not gaps: print('/joy 공백(0.5 s 넘음) 없음 — 패드가 꺼져도 /joy 가 계속 나왔거나 끄지 않음 → 위 표의 axis1 로 판단')
