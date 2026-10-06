#!/usr/bin/env python3
"""rf2o 게이트 — 라이다 스캔 정합 속도(rf2o)를 걸러 EKF 의 병진 입력으로 넘긴다 (2026-10-02 R2 → 10-06 R3 라이브).

왜: 제자리 회전 중 트랙이 실제로 미끄러지는데(±90°×3 에 36.8 cm, 줄자) 휠·자이로 EKF 는 0.3 cm 로 본다 →
    odom 좌표 로컬 코스트맵에 옛 표시가 어긋나 쌓여 벽이 두꺼워진다(f2b3 구석 12 cm → MPPI 실패).
    rf2o 를 이 게이트로 넣은 EKF 는 오프라인 재생에서 줄자 대비 4.3 cm, 직진 축척 0.998(Docs/debug_log/2026-10-02 §13~§16).

입력: /odom_rf2o(rf2o_laser_odometry, 10 Hz) · /imu/data(컨디셔너 출력, 광학 프레임 → 로봇 yaw = −ω_y) · /wheel_odom(정지 판정)
출력: /odom_rf2o/gated — 차체 속도 vx·vy 만(회전은 자이로가 담당), 아래 가변 σ
  좌표: 차체 속도 = R(π − 0.04677)·v_rf2o — 라이다가 yaw π−2.68° 로 뒤집혀 달려 rf2o 병진이 라이다 좌표로 나온다(10-02 §13.2 줄자 검증)
  G1 자이로 일치: rf2o ω 와 직전 0.1 s 자이로 평균의 차가 max(g1_floor, 0.3·|ω|) 넘으면 버림
       — 사람 등 움직이는 물체가 스캔 흐름을 오염시키면 회전 추정도 같이 틀어진다는 가정(09-29 §6.1, 사람 시험 T1~T3 로 검증 예정)
       — 최신 자이로 한 표본과 비교하면 사람 없이도 34~37 % 오거부(시각 어긋남) → 0.1 s 평균·바닥 0.12 로 1~2 ‰(§14.2)
  G2 정지 검사: 휠 |vx| < 0.005 이고 |ω| < 0.02 인데 rf2o |v| > 0.02 면 버림(정지 중 가짜 이동)
  σ: 회전 중(|ω| > 0.15) vx·vy 0.03 / 그 밖 vx 0.10(직진은 휠 우선 — rf2o 축척 0.93)·vy 0.03
짝 설정: 컨디셔너 rot_cov(B3)를 켜고 순수 회전 중 휠 병진 σ 를 0.3 으로(0.03 이면 25 Hz 휠이 10 Hz rf2o 를 눌러 미끄러짐을 지움 — §14.1)
TODO(improve): 200 Hz 자이로 구독을 Python 으로 받는다 — CPU 가 문제가 되면 컨디셔너(C++)에 합친다."""
import collections
import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu


class Rf2oGate(Node):
    def __init__(self):
        super().__init__('rf2o_gate')
        self.lidar_yaw = float(self.declare_parameter('lidar_yaw', math.pi - 0.04677).value)
        self.g1_floor = float(self.declare_parameter('g1_floor', 0.12).value)
        self.rot_w = float(self.declare_parameter('rot_w', 0.15).value)
        self.sd_rot = float(self.declare_parameter('sd_rot', 0.03).value)
        self.sd_vx = float(self.declare_parameter('sd_vx', 0.10).value)
        self.sd_vy = float(self.declare_parameter('sd_vy', 0.03).value)
        # 비교용 그림자 EKF(A, 지금 구성)에 줄 휠 중계 — 컨디셔너 기본 공분산과 같게(rot_cov 끈 것과 같음). ekf.launch shadow:=true 일 때만
        self.relay = bool(self.declare_parameter('relay_plain', False).value)
        self.pplain = self.create_publisher(Odometry, '/wheel_odom/plain', 20) if self.relay else None
        csv = str(self.declare_parameter('csv', '').value)   # 비우면 기록 안 함
        self.csv = open(csv, 'w') if csv else None
        if self.csv: self.csv.write('t,w_rf2o,w_gyro,v_wheel,bx,by,res\n')
        self.pub = self.create_publisher(Odometry, '/odom_rf2o/gated', 20)
        self.create_subscription(Odometry, '/odom_rf2o', self.on_rf2o, qos_profile_sensor_data)
        self.create_subscription(Imu, '/imu/data', self.on_imu, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/wheel_odom', self.on_wheel, qos_profile_sensor_data)   # micro-ROS 는 best-effort
        self.gh = collections.deque(maxlen=400); self.wg = 0.0; self.wv = 0.0
        self.n = {'pass': 0, 'g1': 0, 'g2': 0}
        self.create_timer(30.0, lambda: self.get_logger().info('rf2o 게이트 통과 %(pass)d · G1 거부 %(g1)d · G2 거부 %(g2)d' % self.n))

    @staticmethod
    def stamp(h): return h.stamp.sec + h.stamp.nanosec * 1e-9

    def on_imu(self, m):
        self.wg = -m.angular_velocity.y; self.gh.append((self.stamp(m.header), self.wg))

    def on_wheel(self, m):
        self.wv = m.twist.twist.linear.x
        if self.pplain:
            o = Odometry(); o.header = m.header; o.child_frame_id = m.child_frame_id; o.twist.twist = m.twist.twist
            c = [0.0] * 36; c[0] = 0.02 ** 2; c[7] = 0.01 ** 2; c[35] = 0.1 ** 2; o.twist.covariance = c; self.pplain.publish(o)

    def on_rf2o(self, m):
        vx, vy, w = m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z
        c, s = math.cos(self.lidar_yaw), math.sin(self.lidar_yaw); bx, by = c * vx - s * vy, s * vx + c * vy
        t = self.stamp(m.header)
        win = [g for tt, g in self.gh if t - 0.1 <= tt <= t]; wgm = sum(win) / len(win) if win else self.wg
        res = 'pass'
        if abs(w - wgm) > max(self.g1_floor, 0.3 * abs(wgm)): res = 'g1'
        elif abs(self.wv) < 0.005 and abs(wgm) < 0.02 and math.hypot(bx, by) > 0.02: res = 'g2'
        self.n[res] += 1
        if self.csv: self.csv.write('%.3f,%.4f,%.4f,%.4f,%.4f,%.4f,%s\n' % (t, w, wgm, self.wv, bx, by, res)); self.csv.flush()
        if res != 'pass': return
        o = Odometry(); o.header = m.header; o.header.frame_id = 'odom'; o.child_frame_id = 'base_link'
        o.twist.twist.linear.x, o.twist.twist.linear.y = bx, by
        rot = abs(wgm) > self.rot_w; cv = [0.0] * 36
        cv[0] = (self.sd_rot if rot else self.sd_vx) ** 2; cv[7] = (self.sd_rot if rot else self.sd_vy) ** 2; cv[35] = 1e3
        o.twist.covariance = cv; self.pub.publish(o)


def main():
    rclpy.init(); rclpy.spin(Rf2oGate())


if __name__ == '__main__':
    main()
