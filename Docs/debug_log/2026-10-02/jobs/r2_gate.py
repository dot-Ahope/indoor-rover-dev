#!/usr/bin/env python3
"""10-02 §14 R2(오프라인 원형): 휠 공분산 중계 + rf2o 게이트 — bag 재생에서 EKF A/B 를 같은 입력으로 돌리기 위한 노드.
   /wheel_odom → /r2/wheel_A (지금 컨디셔너와 같은 공분산: vx 0.02², vy 0.01², vyaw 0.1²)
               → /r2/wheel_B (B3: 휠 |vx| < 0.02 이고 |ω| > 0.10 이면 vx·vy 0.03² — 휠의 '옆 이동 0' 주장을 회전 중 약하게)
   /odom_rf2o  → /r2/rf2o_gated (차체 속도 vx·vy 만, 아래 게이트·가변 σ)
     좌표: 차체 속도 = R(π − 0.04677)·v_rf2o (라이다가 뒤집혀 달림, 10-02 §13.2 줄자 검증)
     G1 자이로 일치: |ω_rf2o − ω_자이로| > max(0.05, 0.3·|ω_자이로|) 이면 버림(사람 등으로 흐름이 오염되면 회전도 같이 틀어진다는 가정 — 09-29 §6.1)
     G2 정지 검사: 휠 |vx| < 0.005·|ω_자이로| < 0.02 인데 rf2o |v| > 0.02 면 버림(정지 중 가짜 이동)
     σ: 회전 중(|ω_자이로| > 0.15) vx·vy 0.03 / 그 밖: vx 0.10(직진은 휠 우선 — rf2o 축척 0.93, §13.2)·vy 0.03
   자이로 = /imu/data(컨디셔너 출력, 광학 프레임) 의 −ω_y (컨디셔너 gyro_yaw_axis 1·sign −1 과 같은 약속)"""
import math, collections, rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from rclpy.qos import qos_profile_sensor_data   # 10-02 §14.1: bag 재생 /wheel_odom 은 micro-ROS 원래대로 best-effort → reliable 구독은 아무것도 못 받음(1·2 차 재생 무효 원인)
LY = math.pi - 0.04677


class Gate(Node):
    def __init__(self):
        super().__init__('r2_gate')
        self.pa = self.create_publisher(Odometry, '/r2/wheel_A', 20); self.pb = self.create_publisher(Odometry, '/r2/wheel_B', 20)
        self.pr = self.create_publisher(Odometry, '/r2/rf2o_gated', 20)
        self.create_subscription(Odometry, '/wheel_odom', self.on_wheel, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odom_rf2o', self.on_rf2o, qos_profile_sensor_data)
        self.create_subscription(Imu, '/imu/data', self.on_imu, qos_profile_sensor_data)
        # 10-02 §14.1: 회전 시험 bag(rot2·rot3)엔 /imu/data 가 없음 → 자이로 대신 라이브 EKF 회전 속도(자이로 지배)를 씀
        self.create_subscription(Odometry, '/odometry/filtered', self.on_live, qos_profile_sensor_data)
        self.pl = self.create_publisher(Odometry, '/r2/live_w', 20)
        # 10-02 §14.2: 순수 회전 중 휠 병진 σ(B3). 0.03 이면 휠(25 Hz)이 rf2o(10 Hz)를 눌러 rot3 미끄러짐 37 cm 중 7 cm 만 잡음 → 0.3(사실상 무시)
        self.rot_sd = float(self.declare_parameter('rot_sd', 0.3).value)   # EKF 의 '자이로 대용' 입력(회전 속도만) — EKF 출력 이름 바꿈과 겹치지 않게 다른 이름으로
        self.wg = 0.0; self.wv = 0.0; self.ww = 0.0; self.n = {'pass': 0, 'g1': 0, 'g2': 0}; self.t_imu = -1.0
        # 10-02 §14.2: G1 은 rf2o 가 추정한 구간(직전 스캔 → 이번 스캔, 0.1 s)의 자이로 평균과 비교. 3 차 재생에서 최신 자이로 한 표본과 비교했더니
        #   사람 없는 f2b3 에서도 움직이는 중 34~37 % 거부(|Δω| 90 % 값 0.09~0.12) — 시각 어긋남·잡음이 문턱 0.05 를 넘음 → 바닥값 0.12
        self.gh = collections.deque(maxlen=400); self.g1_floor = float(self.declare_parameter('g1_floor', 0.12).value)
        self.csv = open(self.declare_parameter('csv', '/tmp/r2_gate.csv').value, 'w'); self.csv.write('t,w_rf2o,w_gyro,v_wheel,w_wheel,bx,by,res' + chr(10))
        self.create_timer(10.0, lambda: self.get_logger().info('rf2o 게이트 통과 %(pass)d · G1 거부 %(g1)d · G2 거부 %(g2)d' % self.n))

    def on_imu(self, m):
        self.wg = -m.angular_velocity.y; self.t_imu = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9; self.gh.append((self.t_imu, self.wg))

    def on_live(self, m):
        t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        if t - self.t_imu > 1.0:
            self.wg = m.twist.twist.angular.z; self.gh.append((t, self.wg))
            o = Odometry(); o.header = m.header; o.child_frame_id = 'base_link'; o.twist.twist.angular.z = self.wg
            c = [0.0] * 36; c[35] = 0.02 ** 2; o.twist.covariance = c; self.pl.publish(o)

    def on_wheel(self, m):
        self.wv, self.ww = m.twist.twist.linear.x, m.twist.twist.angular.z
        for pub, b3 in ((self.pa, False), (self.pb, True)):
            o = Odometry(); o.header = m.header; o.child_frame_id = m.child_frame_id; o.twist.twist = m.twist.twist
            rot = b3 and abs(self.wv) < 0.02 and abs(self.ww) > 0.10
            rv = self.rot_sd ** 2; c = [0.0] * 36; c[0] = rv if rot else 0.02 ** 2; c[7] = rv if rot else 0.01 ** 2; c[35] = 0.1 ** 2
            o.twist.covariance = c; pub.publish(o)

    def on_rf2o(self, m):
        vx, vy, w = m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z
        c, s = math.cos(LY), math.sin(LY); bx, by = c * vx - s * vy, s * vx + c * vy
        t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9; res = 'pass'
        win = [g for tt, g in self.gh if t - 0.1 <= tt <= t]; wgm = sum(win) / len(win) if win else self.wg
        if abs(w - wgm) > max(self.g1_floor, 0.3 * abs(wgm)): res = 'g1'
        elif abs(self.wv) < 0.005 and abs(self.wg) < 0.02 and math.hypot(bx, by) > 0.02: res = 'g2'
        self.csv.write('%.3f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%s' % (t, w, self.wg, self.wv, self.ww, bx, by, res) + chr(10)); self.csv.flush()
        self.n[res] += 1
        if res != 'pass': return
        o = Odometry(); o.header = m.header; o.header.frame_id = 'odom'; o.child_frame_id = 'base_link'
        o.twist.twist.linear.x, o.twist.twist.linear.y = bx, by
        rot = abs(self.wg) > 0.15; cv = [0.0] * 36; cv[0] = (0.03 if rot else 0.10) ** 2; cv[7] = 0.03 ** 2; cv[35] = 1e3
        o.twist.covariance = cv; self.pr.publish(o)


def main():
    rclpy.init(); rclpy.spin(Gate())


if __name__ == '__main__':
    main()
