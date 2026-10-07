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
2026-10-06 §5: 회전 속도 기준을 /imu/data(200 Hz)에서 EKF 출력 /odometry/filtered 의 ω(30 Hz)로 바꿈(gyro_source, 기본 ekf).
  왜: 라이브 정지 기동에서 게이트 CPU 39 %(코어 하나) — Python 200 Hz 콜백 부담. EKF 의 ω 는 자이로(σ 0.02)가 지배하고 rf2o 는
  ω 를 넣지 않으므로(odom1 은 vx·vy 만) 순환 의존이 없다. 되돌리기 = gyro_source:=imu.
2026-10-07 §4: G4(회전 중 병진 타당성)를 휠과의 잔차 |(bx − v_휠, by)| 로(v_ref wheel 기본, abs = 이전 판정)."""
import collections
import math

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu, LaserScan
import numpy as np


class Rf2oGate(Node):
    def __init__(self):
        super().__init__('rf2o_gate')
        self.lidar_yaw = float(self.declare_parameter('lidar_yaw', math.pi - 0.04677).value)
        self.g1_floor = float(self.declare_parameter('g1_floor', 0.12).value)
        self.rot_w = float(self.declare_parameter('rot_w', 0.15).value)
        self.sd_rot = float(self.declare_parameter('sd_rot', 0.03).value)
        self.sd_vx = float(self.declare_parameter('sd_vx', 0.10).value)
        self.sd_vy = float(self.declare_parameter('sd_vy', 0.03).value)
        self.src = str(self.declare_parameter('gyro_source', 'ekf').value)   # ekf(30 Hz, 기본) | imu(200 Hz)
        self.win = 0.1 if self.src == 'imu' else 0.15   # ekf 는 30 Hz 라 0.1 s 에 표본 3 개 → 0.15 s
        # 비교용 그림자 EKF(A, 지금 구성)에 줄 휠 중계 — 컨디셔너 기본 공분산과 같게(rot_cov 끈 것과 같음). ekf.launch shadow:=true 일 때만
        # 2026-10-06 §12 G3 품질 검사: 직전 스캔을 이번 후보 움직임(rf2o 병진 + 자이로 회전)으로 옮겨 이번 스캔과 겹쳐 보고,
        #   어긋난 점 비율 q 가 크면 움직이는 물체가 스캔을 오염시킨 것으로 본다. 근거: §11.1 — 크게 가린 사람이 움직이면 회전 중 병진이
        #   9.5~27.9 cm 틀어졌는데 G1(자이로 일치)은 회전이 맞아 못 거름. q_mode off | log(판정 안 하고 기록만) | on
        self.q_mode = str(self.declare_parameter('q_mode', 'off').value)
        self.q_soft = float(self.declare_parameter('q_soft', 0.15).value); self.q_rej = float(self.declare_parameter('q_rej', 0.30).value)
        self.q_tol = float(self.declare_parameter('q_tol', 0.05).value)   # 어긋남 판정 거리(m)
        self.scans = collections.deque(maxlen=4)
        # 2026-10-06 §12.1 G4 회전 중 병진 타당성: G3(q)는 천천히 움직이는 큰 몸(0.24 m/s → 프레임당 2.4 cm < 허용 5 cm)을 못 가름(보정 재생).
        #   대신 물리 범위로 — 깨끗한 회전 중 실제 미끄러짐 속도는 90 % 0.037·최대 ≈ 0.1 m/s, 오염 C 는 중앙 0.063·90 % 0.168, E 는 0.113·0.401.
        #   회전 중 |v| > v_soft 면 σ 를 1~10 배로, > v_rej 면 버림. v_mode off | on
        self.v_mode = str(self.declare_parameter('v_mode', 'off').value)
        self.v_soft = float(self.declare_parameter('v_soft', 0.05).value); self.v_rej = float(self.declare_parameter('v_rej', 0.10).value)
        # 2026-10-07 §4: G4 를 '휠과의 잔차' 로. 순회(f2c)의 회전은 대부분 0.04~0.08 m/s 로 전진하며 도는 곡선이라 |v| 절댓값 판정이
        #   정상 전진을 오염으로 봄(곡선 회전 표본 σ 키움 43~58 %, §3.2). 잔차 = |(bx − v_휠, by)| — 제자리 회전에선 v_휠 ≈ 0 이라 10-06 보정값 그대로,
        #   곡선에선 휠이 본 전진을 빼고 휠이 못 보는 몫(미끄러짐·오염)만 남음. v_ref wheel(기본) | abs(10-06~07 §1 판정, 되돌리기)
        self.v_ref = str(self.declare_parameter('v_ref', 'wheel').value)
        if self.q_mode != 'off':
            self.create_subscription(LaserScan, '/scan', self.on_scan, qos_profile_sensor_data)
        self.relay = bool(self.declare_parameter('relay_plain', False).value)
        self.pplain = self.create_publisher(Odometry, '/wheel_odom/plain', 20) if self.relay else None
        csv = str(self.declare_parameter('csv', '').value)   # 비우면 기록 안 함
        self.csv = open(csv, 'w') if csv else None
        if self.csv: self.csv.write('t,w_rf2o,w_gyro,v_wheel,bx,by,q,res\n')
        self.pub = self.create_publisher(Odometry, '/odom_rf2o/gated', 20)
        self.create_subscription(Odometry, '/odom_rf2o', self.on_rf2o, qos_profile_sensor_data)
        if self.src == 'imu':
            self.create_subscription(Imu, '/imu/data', self.on_imu, qos_profile_sensor_data)
        else:
            self.create_subscription(Odometry, '/odometry/filtered', self.on_ekf, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/wheel_odom', self.on_wheel, qos_profile_sensor_data)   # micro-ROS 는 best-effort
        self.gh = collections.deque(maxlen=100); self.wg = 0.0; self.wv = 0.0
        self.n = {'pass': 0, 'g1': 0, 'g2': 0, 'g3': 0, 'g4': 0}
        self.create_timer(30.0, lambda: self.get_logger().info('rf2o 게이트 통과 %(pass)d · G1 거부 %(g1)d · G2 거부 %(g2)d · G3 거부 %(g3)d · G4 거부 %(g4)d' % self.n))

    @staticmethod
    def stamp(h): return h.stamp.sec + h.stamp.nanosec * 1e-9

    def on_imu(self, m):
        self.wg = -m.angular_velocity.y; self.gh.append((self.stamp(m.header), self.wg))

    def on_ekf(self, m):
        self.wg = m.twist.twist.angular.z; self.gh.append((self.stamp(m.header), self.wg))

    def on_scan(self, m):
        r = np.asarray(m.ranges, dtype=np.float32)[::2]; a = (m.angle_min + m.angle_increment * 2 * np.arange(len(r))).astype(np.float32)
        self.scans.append((self.stamp(m.header), r, a, m.angle_min, m.angle_increment * 2, len(r)))

    def quality(self, t, bx, by, w):
        """직전 스캔을 차체 움직임(bx, by, w)으로 옮겨 이번 스캔과 비교 — 어긋난 점 비율(0~1), 판단 불가면 None"""
        S = [x for x in self.scans if x[0] <= t + 0.05]
        if len(S) < 2: return None
        (t1, r1, a1, _, _, _), (t2, r2, a2, amin, ainc, n) = S[-2], S[-1]
        dt = t2 - t1
        if not (0.02 < dt < 0.5): return None
        ok = np.isfinite(r1) & (r1 > 0.2) & (r1 < 4.0)
        cl, sl = math.cos(self.lidar_yaw), math.sin(self.lidar_yaw)
        lx, ly = r1[ok] * np.cos(a1[ok]), r1[ok] * np.sin(a1[ok])
        px, py = 0.152 + cl * lx - sl * ly, sl * lx + cl * ly                 # 직전 스캔 점, 직전 차체 좌표
        dth = w * dt; c, s = math.cos(dth), math.sin(dth); qx, qy = px - bx * dt, py - by * dt
        cx, cy = c * qx + s * qy, -s * qx + c * qy                              # 이번 차체 좌표로
        ux, uy = cx - 0.152, cy                                                  # 이번 라이다 좌표로
        rx, ry = cl * ux + sl * uy, -sl * ux + cl * uy
        rp = np.hypot(rx, ry); ap = np.arctan2(ry, rx)
        k = np.round(((ap - amin) % (2 * np.pi)) / ainc).astype(int) % n
        rc = r2[k]; valid = np.isfinite(rc) & (rc > 0.2)
        if valid.sum() < 100: return None
        return float(np.mean(np.abs(rc[valid] - rp[valid]) > self.q_tol))

    def on_wheel(self, m):
        self.wv = m.twist.twist.linear.x
        if self.pplain:
            o = Odometry(); o.header = m.header; o.child_frame_id = m.child_frame_id; o.twist.twist = m.twist.twist
            c = [0.0] * 36; c[0] = 0.02 ** 2; c[7] = 0.01 ** 2; c[35] = 0.1 ** 2; o.twist.covariance = c; self.pplain.publish(o)

    def on_rf2o(self, m):
        vx, vy, w = m.twist.twist.linear.x, m.twist.twist.linear.y, m.twist.twist.angular.z
        c, s = math.cos(self.lidar_yaw), math.sin(self.lidar_yaw); bx, by = c * vx - s * vy, s * vx + c * vy
        t = self.stamp(m.header)
        win = [g for tt, g in self.gh if t - self.win <= tt <= t]; wgm = sum(win) / len(win) if win else self.wg
        q = self.quality(t, bx, by, wgm) if self.q_mode != 'off' else None
        res = 'pass'
        if abs(w - wgm) > max(self.g1_floor, 0.3 * abs(wgm)): res = 'g1'
        elif abs(self.wv) < 0.005 and abs(wgm) < 0.02 and math.hypot(bx, by) > 0.02: res = 'g2'
        elif self.q_mode == 'on' and q is not None and q > self.q_rej: res = 'g3'
        vb = math.hypot(bx - self.wv, by) if self.v_ref == 'wheel' else math.hypot(bx, by)   # G4 판정량(§4)
        if res == 'pass' and self.v_mode == 'on' and abs(wgm) > self.rot_w and vb > self.v_rej: res = 'g4'
        self.n[res] += 1
        if self.csv: self.csv.write('%.3f,%.4f,%.4f,%.4f,%.4f,%.4f,%.3f,%s\n' % (t, w, wgm, self.wv, bx, by, -1 if q is None else q, res)); self.csv.flush()
        if res != 'pass': return
        o = Odometry(); o.header = m.header; o.header.frame_id = 'odom'; o.child_frame_id = 'base_link'
        o.twist.twist.linear.x, o.twist.twist.linear.y = bx, by
        rot = abs(wgm) > self.rot_w; cv = [0.0] * 36
        cv[0] = (self.sd_rot if rot else self.sd_vx) ** 2; cv[7] = (self.sd_rot if rot else self.sd_vy) ** 2; cv[35] = 1e3
        if self.q_mode == 'on' and q is not None and q > self.q_soft:   # q_soft~q_rej 사이는 σ 를 1~10 배로 키움
            f = 1 + 9 * min(1.0, (q - self.q_soft) / max(self.q_rej - self.q_soft, 1e-3)); cv[0] *= f * f; cv[7] *= f * f
        if self.v_mode == 'on' and rot and vb > self.v_soft:
            f = 1 + 9 * min(1.0, (vb - self.v_soft) / max(self.v_rej - self.v_soft, 1e-3)); cv[0] *= f * f; cv[7] *= f * f
        o.twist.covariance = cv; self.pub.publish(o)


def main():
    rclpy.init(); rclpy.spin(Rf2oGate())


if __name__ == '__main__':
    main()
