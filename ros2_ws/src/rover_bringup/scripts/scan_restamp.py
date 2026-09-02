#!/usr/bin/env python3
# 스캔 재스탬프 — RPLidar가 스윕 '시작'에 스탬프를 찍어 실제 취득중심보다 ~scan_time/2 과거로 앵커됨.
# 회전 중 스캔이 회전방향으로 밀려 보이는(그 뒤 slam 스캔매칭이 스냅백) 문제의 주원인.
# 해법: 입력 스캔 스탬프에 offset(기본 scan_time/2)을 더해 스윕 중앙으로 보정 후 재발행.
# 근거: 정적 측정(2026-08-28) /scan now-stamp +112ms, scan_time 95ms, stamp=스윕시작.
# 입력 /scan_raw → 출력 /scan. TODO(production): 드라이버가 스윕중앙 스탬프 지원하면 본 노드 제거.
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from rclpy.duration import Duration


class ScanRestamp(Node):
    def __init__(self):
        super().__init__('scan_restamp')
        # offset_ratio: scan_time 대비 더할 비율 (0.5=스윕중앙). 음수/0 가능.
        self.declare_parameter('offset_ratio', 0.5)
        self.declare_parameter('offset_fixed_s', 0.0)  # 추가 고정 offset(초), 미세조정용
        self.ratio = float(self.get_parameter('offset_ratio').value)
        self.fixed = float(self.get_parameter('offset_fixed_s').value)
        self.pub = self.create_publisher(LaserScan, '/scan', qos_profile_sensor_data)
        self.create_subscription(LaserScan, '/scan_raw', self.cb, qos_profile_sensor_data)
        self.get_logger().info(
            'scan_restamp: /scan_raw → /scan, offset = scan_time*%.2f + %.3fs' % (self.ratio, self.fixed))

    def cb(self, msg: LaserScan):
        off = msg.scan_time * self.ratio + self.fixed
        t = rclpy.time.Time.from_msg(msg.header.stamp) + Duration(seconds=off)
        msg.header.stamp = t.to_msg()
        self.pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(ScanRestamp())


if __name__ == '__main__':
    main()
