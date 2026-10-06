#!/usr/bin/env python3
"""10-06 §10 T2 합성: bag 스캔(/scan_in)에 '바닥에 고정된 사람 몸'을 그려 /scan 으로 — 회전 중 가림이 rf2o·EKF 를 흔드는가.
   몸 = 로버 시작 자세 기준 고정 위치의 원기둥들(호 모양으로 늘어놓아 가림 비율을 조절). 로버 자세는 bag 의 라이브 EKF B(/truth_odom,
   단계별 실측에서 줄자 대비 1.5 cm)로 — 가림을 그리는 데만 쓰고, 시험받는 EKF 는 새로 띄운 것.
   매개: coverage(시작 자세에서 라이다가 가려지는 각도 비율 0~1), center_deg(호 중심 방향, 차체 기준), rho(로버 중심~몸 거리 m), body_r(원기둥 반경)"""
import math, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
LX, LY = 0.152, math.pi - 0.04677


def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class Occ(Node):
    def __init__(self):
        super().__init__('occ_scan')
        cov = float(self.declare_parameter('coverage', 0.5).value); cdeg = float(self.declare_parameter('center_deg', 20.0).value)
        self.rho = float(self.declare_parameter('rho', 0.6).value); self.br = float(self.declare_parameter('body_r', 0.08).value)
        # 10-06 §11: 움직이는 몸 — 위치 = 기준 + amp·sin(2πt/period) 방향 move_deg(시작 자세 기준). legs 면 다리 두 개(반경 0.06, 간격 0.2 m)
        self.amp = float(self.declare_parameter('amp', 0.0).value); self.per = float(self.declare_parameter('period', 10.0).value)
        md = math.radians(float(self.declare_parameter('move_deg', 90.0).value)); self.legs = bool(self.declare_parameter('legs', False).value)
        self.mv = (math.cos(md), math.sin(md)); self.t0 = None
        span = math.radians(360 * cov); n = max(1, int(span * self.rho / (1.6 * self.br))) if cov > 0 else 0
        if self.legs:
            cx, cy = self.rho * math.cos(math.radians(cdeg)), self.rho * math.sin(math.radians(cdeg)); self.br = 0.06
            self.local = [(cx + 0.1 * self.mv[0], cy + 0.1 * self.mv[1]), (cx - 0.1 * self.mv[0], cy - 0.1 * self.mv[1])]
        else:
            self.local = [(self.rho * math.cos(math.radians(cdeg) - span / 2 + span * (i + .5) / n), self.rho * math.sin(math.radians(cdeg) - span / 2 + span * (i + .5) / n)) for i in range(n)]
        self.p0 = None; self.pose = None; self.cnt = []
        self.pub = self.create_publisher(LaserScan, '/scan', qos_profile_sensor_data)
        self.create_subscription(Odometry, '/truth_odom', self.on_odom, qos_profile_sensor_data)
        self.create_subscription(LaserScan, '/scan_in', self.on_scan, qos_profile_sensor_data)
        self.create_timer(60.0, lambda: self.get_logger().info('가린 빔 비율 중앙 %.0f %%' % (100 * np.median(self.cnt) if self.cnt else -1)))

    def on_odom(self, m):
        p = (m.pose.pose.position.x, m.pose.pose.position.y, yaw(m.pose.pose.orientation))
        if self.p0 is None:
            self.p0 = p; c, s = math.cos(p[2]), math.sin(p[2])
            self.world = [(p[0] + c * x - s * y, p[1] + s * x + c * y) for x, y in self.local]   # 시작 자세 기준 → odom 고정
            self.wmv = (c * self.mv[0] - s * self.mv[1], s * self.mv[0] + c * self.mv[1])
        self.pose = p

    def on_scan(self, m):
        r = np.array(m.ranges, dtype=np.float32)
        if self.pose is not None and self.world:
            X, Y, T = self.pose; ox, oy = X + LX * math.cos(T), Y + LX * math.sin(T)   # 라이다 위치
            ang = T + LY + m.angle_min + m.angle_increment * np.arange(len(r)); dx, dy = np.cos(ang), np.sin(ang)
            hit = np.full(len(r), np.inf)
            ts = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
            if self.t0 is None: self.t0 = ts
            off = self.amp * math.sin(2 * math.pi * (ts - self.t0) / self.per)
            for cx0, cy0 in self.world:
                cx, cy = cx0 + off * self.wmv[0], cy0 + off * self.wmv[1]
                fx, fy = cx - ox, cy - oy; b = dx * fx + dy * fy; d2 = fx * fx + fy * fy - b * b
                ok = (b > 0) & (d2 < self.br ** 2); t = b - np.sqrt(np.maximum(self.br ** 2 - d2, 0)); hit = np.where(ok & (t < hit), t, hit)
            valid = np.isfinite(r) & (r > 0); occl = np.isfinite(hit) & (~valid | (hit < r))
            r = np.where(occl, hit, r).astype(np.float32); self.cnt.append(occl.mean())
        o = m; o.ranges = r.tolist(); self.pub.publish(o)


def main():
    rclpy.init(); rclpy.spin(Occ())


if __name__ == '__main__':
    main()
