#!/usr/bin/env python3
# cuVSLAM 자세 → 차체(base_link) 몸 기준 속도 /vslam/odom (2026-10-20 §6) — EKF 에 vx · vy 로만 넣는다.
# 왜 속도만: 오프라인 재실행(Docs/debug_log/2026-10-20/SUMMARY.md §5.3)에서 cuVSLAM 병진 속도 융합이 회전 미끄러짐 창을
#   12~29 % 줄였고, yaw 속도는 자이로(200 Hz)가 이미 같거나 나아 효과가 없었다. 자세(위치) 자체는 SLAM 이 맡는다.
# 계산은 재실행 입력(jobs/mk_ekf_replay_bag.py)과 같게: camera_link 자세에 base_link→camera_link 의 역을 곱해 차체 자세로,
#   앞뒤 프레임 중앙 차분(k−1 → k+1)을 반 회전 돌려 k 몸 기준 속도, stamp = 프레임 k. 그래서 출력은 한 프레임(≈ 67 ms) 늦다.
# 이상값 거름: 프레임 간격 > 0.3 s(빠짐)이면 건너뛰고, 로버가 낼 수 없는 속도(|v| > 0.5 m/s 또는 |ω| > 1.5 rad/s — 지령 상한
#   0.10~0.15 m/s · 0.40 rad/s)는 버린다(추적 재시작 · 재국소화 때 자세가 튀는 것).  // TODO(improve): 추적 상태(/visual_slam/status) 연동
# base_link→camera_link 는 URDF 고정이라 /tf_static 을 한 번 받아 사슬을 만들고 구독을 끊는다.
#   (10-20 §6.1: tf2 TransformListener 를 쓰니 /tf 30 Hz+ 를 계속 받으며 이 노드가 코어 1.9 개를 먹었다)
import math
import os

# 10-20 §6.1: numpy(OpenBLAS)가 작은 4×4 연산마다 일꾼 스레드를 깨워 바쁜 대기 — 이 노드가 스레드 14 개 · 코어 2 개를 먹었다(top 213 %).
#   numpy 를 부르기 전에 1 스레드로 묶는다.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1'); os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np  # noqa: E402
import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.qos import DurabilityPolicy, QoSProfile
from tf2_msgs.msg import TFMessage

VXY_VAR = 0.005 ** 2   # (m/s)^2 — 재실행 §5 선언값: 회전 중 휠 'vy = 0'(σ 0.01, B3 때 0.3)보다 믿게
VYAW_VAR = 0.02 ** 2   # (rad/s)^2 — EKF 설정이 yaw 를 안 쓰면 무시됨
V_MAX, W_MAX, DT_MAX = 0.5, 1.5, 0.3


def qm(x, y, z, w):
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


class VslamTwist(Node):
    def __init__(self):
        super().__init__('vslam_twist')
        self.static = {}; self.c2b = None
        self.st_sub = self.create_subscription(TFMessage, '/tf_static', self.on_static,
                                               QoSProfile(depth=100, durability=DurabilityPolicy.TRANSIENT_LOCAL)); self.hist = []; self.n_out = 0; self.n_drop = 0
        self.pub = self.create_publisher(Odometry, '/vslam/odom', 10)
        self.create_subscription(Odometry, '/visual_slam/tracking/odometry', self.cb, qos_profile_sensor_data)
        self.create_timer(10.0, self.stat)

    def stat(self):
        self.get_logger().info('출력 %d · 버림 %d (최근 10 s)' % (self.n_out, self.n_drop)); self.n_out = self.n_drop = 0

    def on_static(self, msg):
        for tr in msg.transforms:
            t = tr.transform; A = np.eye(4); A[:3, :3] = qm(t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w)
            A[:3, 3] = [t.translation.x, t.translation.y, t.translation.z]; self.static[tr.child_frame_id] = (tr.header.frame_id, A)
        B = np.eye(4); f = 'camera_link'
        while f != 'base_link':
            if f not in self.static:
                return   # 사슬이 아직 다 안 옴 — 다음 메시지(정적 발행자 여럿)를 기다림
            p, A = self.static[f]; B = A @ B; f = p
        self.c2b = np.linalg.inv(B); self.destroy_subscription(self.st_sub)
        self.get_logger().info('base_link→camera_link 받음(%.3f, %.3f, %.3f) — 변환 시작' % tuple(B[:3, 3]))

    def cb(self, m):
        if self.c2b is None:
            return
        p, q = m.pose.pose.position, m.pose.pose.orientation
        V = np.eye(4); V[:3, :3] = qm(q.x, q.y, q.z, q.w); V[:3, 3] = [p.x, p.y, p.z]
        self.hist.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.header.stamp, V @ self.c2b))
        if len(self.hist) < 3:
            return
        self.hist = self.hist[-3:]
        (ta, _, Pa), (_, stk, _), (tc, _, Pc) = self.hist
        dt = tc - ta
        if dt <= 0 or dt > DT_MAX:
            self.n_drop += 1; return
        D = np.linalg.inv(Pa) @ Pc
        th = math.atan2(D[1, 0], D[0, 0]); c, s = math.cos(th / 2), math.sin(th / 2)
        vx = (c * D[0, 3] + s * D[1, 3]) / dt; vy = (-s * D[0, 3] + c * D[1, 3]) / dt; w = th / dt
        if math.hypot(vx, vy) > V_MAX or abs(w) > W_MAX:
            self.n_drop += 1; return
        o = Odometry(); o.header.stamp = stk; o.header.frame_id = 'odom'; o.child_frame_id = 'base_link'
        o.pose.covariance = [1e3 if i % 7 == 0 else 0.0 for i in range(36)]
        o.twist.twist.linear.x = vx; o.twist.twist.linear.y = vy; o.twist.twist.angular.z = w
        cov = [0.0] * 36; cov[0] = cov[7] = VXY_VAR; cov[14] = cov[21] = cov[28] = 1e3; cov[35] = VYAW_VAR
        o.twist.covariance = cov
        self.pub.publish(o); self.n_out += 1


def main():
    rclpy.init(); rclpy.spin(VslamTwist())


if __name__ == '__main__':
    main()
