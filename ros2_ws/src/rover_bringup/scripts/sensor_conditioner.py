#!/usr/bin/env python3
# 센서 컨디셔너 — 펌웨어 covariance=0(unknown) 보완 + 부팅 시 자이로 바이어스 제거.
# 근거: 실측(2026-08-26) ICM-20948 정지 자이로 z 바이어스 -0.0072 rad/s → EKF yaw -0.23°/s 드리프트.
# TODO(production): 펌웨어가 부팅 자이로 캘리브레이션 + 실측 covariance를 제공하면 본 노드 제거.
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry

GYRO_VAR = 0.02 ** 2      # (rad/s)^2 — 바이어스 제거 후 잔류 노이즈
ACCEL_VAR = 0.5 ** 2      # (m/s^2)^2
VX_VAR = 0.02 ** 2        # (m/s)^2 — FG 양자화 + 주기 지터
VY_VAR = 0.01 ** 2        # 차동구동 측면속도 = 0 측정
VYAW_VAR = 0.1 ** 2       # (rad/s)^2 — 트랙 스크럽 슬립 반영
# 직진 스케일 보정 — 휠 오도가 실제 이동보다 '과대'보고 (펌웨어 스케일 상수 오류).
#   근거(2026-09-01 재측정, 줄자 2회 + slam 교차검증, 같은 바닥·슬립 육안 없음):
#     0.10 m/s: 휠원시 1.354 m vs 줄자 1.06  m → 1.277배 과대
#     0.06 m/s: 휠원시 1.297 m vs 줄자 1.015 m → 1.278배 과대   (속도 무관 = 슬립 아님, 상수 오류)
#     slam은 두 번 다 줄자와 1% 이내 일치 → slam을 지면검증으로 신뢰 확정.
#   → 보정계수 = 1 / 1.2776 = 0.783
#   ⚠ 이전 값 1.022 폐기: 당시 줄자(205cm)에 로버 길이(~0.5m)가 섞여 잘못 측정된 것으로 판단
#     (27.8% 과대 적용 시 실제 ~1.55m, +0.5m = 2.05m 로 정합). 오차는 처음부터 있었음.
# ✅ 2026-09-07 해결: 위 TODO 대로 **펌웨어 상수를 교정**함.
#   WHEEL_CIRCUMFERENCE_M 0.16130 → 0.12533 (휠반경 25.67 → 19.95mm).
#   근거: 라이다 전방벽 변위 GT 3회 (전진0.06 1.2971 / 후진0.06 1.2754 / 전진0.10 1.2885, 평균 1.2870)
#         — 속도 무관 = 계통 오차. 공칭 Ø40 둘레 0.12566 과 0.3% 일치로 교차확인.
#   따라서 여기서는 **더 이상 보정하지 않음**.
#   ⚠ 이 값(1.0)은 교정 펌웨어와 한 쌍 — 구 펌웨어(0.16130)로 되돌릴 땐 0.783 으로 같이 되돌릴 것.
VX_SCALE = 1.0
# 회전 슬립 보정 — |vyaw_wheel| 2점 선형보간(범위 밖 클램프).
# W4 재캘리브레이션 (2026-08-27, WT-600 게이지 0.245 펌웨어 + D455f 자이로 기준, 접지 좌/우×2속도):
#   자이로/휠 적분비 = L-slow 0.482, L-fast 0.402, R-slow 0.429, R-fast 0.553 → 평균 0.47, ±0.06(13%).
#   속도 의존성 없음(느림 0.456/빠름 0.478, 방향 무의미) → 단일 상수. 변동은 강철 탱크 섀시 스키드의 본질적 특성.
#   ⚠ yaw는 EKF에서 D455f 자이로가 25배 신뢰(GYRO_VAR≪VYAW_VAR)로 주도 → 본 계수는 휠 vyaw가 자이로와
#     다투지 않게 맞추는 보조 역할. 정밀 heading은 자이로·SLAM 스캔매칭이 담당.
# 2026-09-07 재캘리브레이션 (스케일 교정 펌웨어 기준). 기준은 **D455f 자이로 적분**.
#   ⚠ 자이로 축 주의: 카메라 IMU 프레임에서 로버 요 회전은 **y축**(부호 반대). z 는 ~0.
#   ⚠ 라이다 스캔정합 GT 도 병행했으나 자이로 대비 산포 ±10% (잔차 17~22cm) → 보조 지표로만 사용.
#   자이로 기준 실측 (휠 ω rad/s → SLIP = 자이로각/휠적분각):
#     0.146→0.569  0.196→0.627  0.294→0.515  0.295→0.634  0.394→0.612  0.492→0.626  0.593→0.616
#   → ω 의존성 뚜렷하지 않음(같은 0.3 에서 0.515/0.634 로 산포). 평균 0.600, 표준편차 0.043(7%).
#   물리 해석: 트랙 스크럽으로 유효 게이지가 기하 게이지(0.245m)보다 큼 → B_eff ≈ 0.245/0.600 = 0.409 m.
#   TODO(improve): B_eff 를 펌웨어 WHEEL_BASE 에 반영하면 지령 ω 도 실제와 일치하고 이 보정은 1.0 이 됨.
#     (현재는 지령 ω 의 60% 만 실제로 회전함 — Nav2 각속도 파라미터 해석 시 주의)
#   구 0.46 은 직진 스케일 오차 0.777 을 포함한 값이었고, 그마저 과소보정이었음.
SLIP_PTS = ((0.15, 0.600), (0.60, 0.600))


def yaw_slip_factor(vyaw):
    a = abs(vyaw)
    (x0, y0), (x1, y1) = SLIP_PTS
    if a <= x0:
        return y0
    if a >= x1:
        return y1
    return y0 + (y1 - y0) * (a - x0) / (x1 - x0)
CALIB_SAMPLES = 2000      # 200Hz(D455f) × 10s — 바이어스 추정 오차 축소
# 정지 판정: 표준편차 기준. 실측(2026-08-26) 정지 시 원시 자이로 p-p ≈0.032 rad/s(σ≈0.005)라
# p-p 기준은 오판 → σ 기준 사용. 회전 중에는 σ가 훨씬 커지므로 여유 3배.
CALIB_MAX_STD = 0.015     # rad/s


class SensorConditioner(Node):
    def __init__(self):
        super().__init__('sensor_conditioner')
        self.bias = None
        self.samples = []
        self.imu_pub = self.create_publisher(Imu, '/imu/data', qos_profile_sensor_data)
        self.odom_pub = self.create_publisher(
            Odometry, '/wheel_odom/conditioned', qos_profile_sensor_data)
        self.create_subscription(Imu, '/imu/data_raw', self.imu_cb, qos_profile_sensor_data)
        self.create_subscription(Odometry, '/wheel_odom', self.odom_cb, qos_profile_sensor_data)

    def imu_cb(self, msg):
        g = msg.angular_velocity
        if self.bias is None:
            self.samples.append((g.x, g.y, g.z))
            if len(self.samples) >= CALIB_SAMPLES:
                n = len(self.samples)
                means = tuple(sum(c) / n for c in zip(*self.samples))
                stds = tuple(
                    (sum((v - m) ** 2 for v in c) / n) ** 0.5
                    for c, m in zip(zip(*self.samples), means))
                if max(stds) < CALIB_MAX_STD:
                    self.bias = means
                    self.get_logger().info(
                        'gyro bias calibrated: (%.5f, %.5f, %.5f) rad/s, std=(%.4f, %.4f, %.4f)'
                        % (means + stds))
                else:
                    self.bias = (0.0, 0.0, 0.0)
                    self.get_logger().warn(
                        'startup not stationary (max std=%.4f) — bias=0 유지' % max(stds))
            return  # 캘리브레이션 완료 전에는 발행 보류
        g.x -= self.bias[0]
        g.y -= self.bias[1]
        g.z -= self.bias[2]
        msg.angular_velocity_covariance = [
            GYRO_VAR if i in (0, 4, 8) else 0.0 for i in range(9)]
        msg.linear_acceleration_covariance = [
            ACCEL_VAR if i in (0, 4, 8) else 0.0 for i in range(9)]
        # orientation 미제공 표식 강제 (covariance[0] = -1, REP-145) — 소스가 무엇이든 EKF가 자세를 쓰지 않도록
        oc = list(msg.orientation_covariance)
        oc[0] = -1.0
        msg.orientation_covariance = oc
        self.imu_pub.publish(msg)

    def odom_cb(self, msg):
        # 직진 스케일 보정 — 휠 유효 구름둘레 과소 → vx 과소보고 (2026-08-31 줄자 캘리브)
        msg.twist.twist.linear.x *= VX_SCALE
        # 회전 슬립 보정 — 휠 기반 각속도는 실회전보다 과대 (트랙 스크럽, 속도 의존)
        msg.twist.twist.angular.z *= yaw_slip_factor(msg.twist.twist.angular.z)
        cov = list(msg.twist.covariance)
        cov[0] = VX_VAR       # vx
        cov[7] = VY_VAR       # vy
        cov[35] = VYAW_VAR    # vyaw
        msg.twist.covariance = cov
        self.odom_pub.publish(msg)


def main():
    rclpy.init()
    rclpy.spin(SensorConditioner())


if __name__ == '__main__':
    main()
