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
#   물리 해석: 트랙 스크럽으로 유효 게이지가 기하 게이지(0.245m)보다 큼 → B_eff = 0.245/0.600 = 0.409 m.
#   ✅ 2026-09-07 해결: B_eff 를 **펌웨어 WHEEL_BASE_M 에 반영**(0.245→0.409).
#      이제 /wheel_odom 의 vyaw 자체가 실제 회전율이므로 여기서는 보정하지 않는다(1.0).
#      지령 ω 도 실제 ω 와 일치하게 되어 Nav2 각속도 파라미터가 실단위가 됨(상한 0.40).
#   ⚠ 이 1.0 은 B_eff 펌웨어와 한 쌍 — 기하 게이지(0.245) 펌웨어로 되돌리면 0.600 으로 복귀할 것.
#   ⚠ 잔여 오차 σ 7% 는 스크럽의 실제 변동 — EKF 가 자이로로 흡수.
#   구 0.46 은 직진 스케일 오차 0.777 을 포함한 값이었고, 그마저 과소보정이었음.
SLIP_PTS = ((0.15, 1.0), (0.60, 1.0))


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

# ── ZUPT (정지 구간 온라인 바이어스 재추정) — 2026-09-10 추가 ────────────────
# 왜: 부팅 직후 10초 캘리브는 **차가운 카메라**의 바이어스를 잰다. D455f 가 켜져 발열하면
#   MEMS 자이로 바이어스가 이동하고, 보정값은 그만큼 낡는다. 실측(job213, 정지 30초):
#     원본 광학 wy      -0.001126 rad/s
#     시작 캘리브 y     -0.00075
#     잔차              -0.000376
#     EKF 가 쓰는 yaw rate = -wy 잔차 = +0.000380 rad/s = 1.31 °/분
#     EKF odom->base 실측 드리프트         = +0.000380 rad/s = 1.31 °/분  ← 설명 비율 100%
#   대가: 주행 40초에 0.87°(1.6m 주행 시 횡오차 2.4cm), 정지 10분에 13°.
#   주행 중에는 slam 스캔매칭이 map->odom 으로 흡수하지만, **정지 중에는 slam 이
#   스캔을 처리하지 않아** 오차가 그대로 map 자세에 쌓인다(오늘 80분 정지 후 약 105° 관측).
#   그 상태로 주행을 시작하면 Nav2 의 초기 계획이 엉뚱한 방향을 기준으로 선다.
# 어떻게: 휠 오도메트리가 완전 정지를 보고하는 구간에서 자이로 평균을 다시 재어
#   바이어스를 **천천히** 끌어당긴다. 표준적인 zero-velocity update 다.
#   급변 방지를 위해 1회 갱신량을 제한하고 지수이동평균으로 섞는다.
# 기각한 대안:
#   - 웜업 후 캘리브: 매 기동마다 수 분 대기 → 개발 반복이 느려지고, 온도는 주행 중에도 변한다.
#   - EKF 상태에 바이어스 추가(15→16 상태): robot_localization 이 지원하지 않는다.
#   - 휠 vyaw 신뢰도 상향: 스키드 스티어 스크럽 산포가 7% 라 정지 판정 외에는 못 믿는다.
ZUPT_STATIONARY_VX = 0.005     # m/s — 이보다 작으면 정지로 본다
ZUPT_STATIONARY_VYAW = 0.005   # rad/s
ZUPT_WIN = 400                 # 200Hz × 2s — 재추정 1회에 쓰는 표본 수
ZUPT_MAX_STD = 0.010           # rad/s — 이보다 흔들리면 정지가 아니다 (정지 실측 σ≈0.0022)
ZUPT_ALPHA = 0.10              # 지수이동평균 계수
ZUPT_MAX_STEP = 0.0005         # rad/s — 1회 갱신 상한 (튐 방지)
ZUPT_LOG_PERIOD = 20.0         # 초 — 로그 주기


class SensorConditioner(Node):
    def __init__(self):
        super().__init__('sensor_conditioner')
        self.bias = None
        self.samples = []
        # ZUPT 상태
        self.stationary = False     # 휠이 완전 정지를 보고하는가
        self.zbuf = []              # 정지 구간 원시 자이로 표본
        self.zlast_log = 0.0
        self.zcount = 0
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
        self.zupt_update((g.x, g.y, g.z))
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

    def zupt_update(self, raw):
        """정지 구간에서 자이로 바이어스를 천천히 재추정한다 (원시값을 받는다)."""
        if not self.stationary:
            if self.zbuf:
                self.zbuf = []      # 움직이면 표본 폐기 — 부분 표본은 섞지 않는다
            return
        self.zbuf.append(raw)
        if len(self.zbuf) < ZUPT_WIN:
            return
        cols = list(zip(*self.zbuf))
        self.zbuf = []
        n = len(cols[0])
        means = tuple(sum(c) / n for c in cols)
        stds = tuple((sum((v - m) ** 2 for v in c) / n) ** 0.5 for c, m in zip(cols, means))
        if max(stds) >= ZUPT_MAX_STD:
            return                  # 휠은 0 인데 흔들린다 = 손으로 옮기는 중 등
        new = []
        for b, m in zip(self.bias, means):
            step = (m - b) * ZUPT_ALPHA
            if step > ZUPT_MAX_STEP:
                step = ZUPT_MAX_STEP
            elif step < -ZUPT_MAX_STEP:
                step = -ZUPT_MAX_STEP
            new.append(b + step)
        old_y = self.bias[1]
        self.bias = tuple(new)
        self.zcount += 1
        now = self.get_clock().now().nanoseconds * 1e-9
        if now - self.zlast_log >= ZUPT_LOG_PERIOD:
            self.zlast_log = now
            # EKF 가 쓰는 로봇 yaw rate 는 광학 -y (ekf.yaml imu0_config 인덱스 10)
            self.get_logger().info(
                'ZUPT #%d: bias y %.6f → %.6f (관측 %.6f), 잔차 yaw rate %+.6f rad/s = %+.2f °/분'
                % (self.zcount, old_y, self.bias[1], means[1],
                   -(means[1] - self.bias[1]), -(means[1] - self.bias[1]) * 57.29578 * 60))

    def odom_cb(self, msg):
        self.stationary = (abs(msg.twist.twist.linear.x) < ZUPT_STATIONARY_VX
                           and abs(msg.twist.twist.angular.z) < ZUPT_STATIONARY_VYAW)
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
