#!/usr/bin/env python3
# 스캔 디스큐(deskew) — 회전 중 스캔 왜곡·끌림 제거.
#
# 문제: RPLidar는 한 스윕(95ms@10Hz) 동안 점들을 순차 취득하는데, slam/뷰어는 스캔을 한 순간으로 취급한다.
#   회전 중엔 각 점이 서로 다른 자세에서 찍혔으므로, 단일 스탬프로 그리면 스캔 전체가 밀리고(끌림) 형태가 전단(shear)된다.
#   scan_restamp(스윕 중앙 앵커)는 평균 지연만 줄일 뿐 이 왜곡은 남는다.
# 해법: 각 빔의 취득 시각 t_i = stamp + i*time_increment 에 대해, EKF 각속도 ω로 회전량을 보정.
#   기준 t_ref = 스윕 끝(최신). 빔 각도 보정: a'_i = a_i - ω*(t_ref - t_i)  (라이다가 +dyaw 회전 시 고정점 방위 -dyaw)
#   보정 각도를 출력 스캔 격자에 재분류(nearest bin, 더 가까운 값 우선). 출력 스탬프 = t_ref.
# 근거: 정적 /scan 지연 52ms(재스탬프) 중 ~47ms가 반스윕 → 디스큐 시 전송지연(~5ms)만 남음 기대.
# 입력 /scan_raw + /odometry/filtered(ω) → 출력 /scan.
# TODO(production): 순수 yaw 회전 가정(2D). 병진 왜곡은 저속에서 무시(0.05m/s×0.095s=5mm). 필요 시 vx도 반영.
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry


class ScanDeskew(Node):
    def __init__(self):
        super().__init__('scan_deskew')
        # ref: 'end'(최신, 끌림 최소) | 'mid' | 'start'
        self.declare_parameter('ref', 'end')
        self.declare_parameter('omega_deadband', 0.02)  # rad/s, 이하이면 정지로 보고 디스큐 생략
        self.ref = str(self.get_parameter('ref').value)
        self.deadband = float(self.get_parameter('omega_deadband').value)
        self.omega = 0.0
        self.pub = self.create_publisher(LaserScan, '/scan', qos_profile_sensor_data)
        self.create_subscription(LaserScan, '/scan_raw', self.scan_cb, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odometry/filtered', self.odom_cb, qos_profile_sensor_data)
        self.get_logger().info('scan_deskew: /scan_raw → /scan (ref=%s, EKF ω 기반 회전 디스큐)' % self.ref)

    def odom_cb(self, msg):
        self.omega = msg.twist.twist.angular.z

    def scan_cb(self, msg: LaserScan):
        n = len(msg.ranges)
        ti = msg.time_increment
        st = msg.scan_time
        w = self.omega
        # 기준 시각 offset (스캔 시작 대비)
        if self.ref == 'end':
            t_ref = (n - 1) * ti if ti > 0 else st
        elif self.ref == 'mid':
            t_ref = st * 0.5
        else:
            t_ref = 0.0
        out = msg
        # 정지 근처면 디스큐 생략(잡음 방지), 스탬프만 t_ref 로
        if abs(w) < self.deadband or ti <= 0.0 or n == 0:
            self._restamp_only(msg, t_ref)
            return
        r = np.array(msg.ranges, dtype=np.float32)
        a0, ai = msg.angle_min, msg.angle_increment
        idx = np.arange(n)
        t_i = idx * ti
        # 보정 각도: a'_i = a_i - ω*(t_ref - t_i)
        a = a0 + ai * idx - w * (t_ref - t_i)
        # 출력 격자 재분류
        newr = np.full(n, float('inf'), dtype=np.float32)
        valid = np.isfinite(r) & (r >= msg.range_min) & (r <= msg.range_max)
        j = np.round((a - a0) / ai).astype(np.int64)
        ok = valid & (j >= 0) & (j < n)
        # 같은 bin 충돌 시 더 가까운 값 우선 — bin별 최소 거리(벡터화).
        # np.minimum.at 은 중복 인덱스를 올바로 축약(unbuffered) → 기존 Python 루프와 결과 동일.
        # (성능: 초당 ~1.6만 Python 반복 제거 → deskew CPU 대폭 절감. 2026-09-01)
        np.minimum.at(newr, j[ok], r[ok])
        out = LaserScan()
        out.header = msg.header
        out.angle_min = msg.angle_min; out.angle_max = msg.angle_max
        out.angle_increment = msg.angle_increment
        out.time_increment = msg.time_increment; out.scan_time = msg.scan_time
        out.range_min = msg.range_min; out.range_max = msg.range_max
        out.ranges = newr.tolist()
        out.intensities = msg.intensities
        self._publish(out, t_ref)

    def _restamp_only(self, msg, t_ref):
        from rclpy.time import Time
        from rclpy.duration import Duration
        t = Time.from_msg(msg.header.stamp) + Duration(seconds=t_ref)
        msg.header.stamp = t.to_msg()
        self.pub.publish(msg)

    def _publish(self, out, t_ref):
        from rclpy.time import Time
        from rclpy.duration import Duration
        t = Time.from_msg(out.header.stamp) + Duration(seconds=t_ref)
        out.header.stamp = t.to_msg()
        self.pub.publish(out)


def main():
    rclpy.init()
    rclpy.spin(ScanDeskew())


if __name__ == '__main__':
    main()
