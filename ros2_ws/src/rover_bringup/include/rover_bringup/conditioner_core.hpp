// 센서 컨디셔너 핵심 로직 (ROS 비의존) — scripts/sensor_conditioner.py 의 C++ 이식 (2026-09-28).
//   왜 이식: Python 판이 CPU 42 %(200 Hz IMU + 25 Hz 휠 재발행, rclpy 비용으로 추정) —
//            Docs/debug_log/2026-09-28/SUMMARY.md §10. 대체 패키지는 쓰지 않기로 결정(같은 §10).
//   원칙: 1 단계는 **Python 판과 출력이 같아야 한다**(같은 입력 → 같은 수치). 동작을 바꾸는 개선
//         (가변 공분산·ICR 모델, §7 B2·B3)은 동일성 검증 뒤 CovariancePolicy 자리에 넣는다.
//   ROS 와 분리한 이유: 바이어스·ZUPT·공분산 계산을 gtest 로 따로 검증하기 위해.
#pragma once

#include <array>
#include <cmath>
#include <cstddef>
#include <vector>

namespace rover_bringup
{

struct ConditionerParams
{
  // 공분산 (분산 값) — Python 판 상수와 동일
  double gyro_var = 0.02 * 0.02;    // (rad/s)^2 — 바이어스 제거 후 잔류 노이즈
  double accel_var = 0.5 * 0.5;     // (m/s^2)^2
  double vx_var = 0.02 * 0.02;      // (m/s)^2 — FG 양자화 + 주기 지터
  double vy_var = 0.01 * 0.01;      // 차동구동 측면속도 = 0 측정 (09-28 §7: 회전 중 과신 → B3 에서 가변화 예정)
  double vyaw_var = 0.1 * 0.1;      // (rad/s)^2 — 트랙 스크럽 슬립 반영
  // 휠 보정 계수 — 09-07 펌웨어 교정 뒤 1.0(무동작). 구 펌웨어로 되돌릴 때만 바꾼다(Python 판 주석 참조)
  double vx_scale = 1.0;
  double slip_x0 = 0.15, slip_y0 = 1.0, slip_x1 = 0.60, slip_y1 = 1.0;
  // 부팅 바이어스 캘리브
  std::size_t calib_samples = 2000;  // 200 Hz × 10 s
  double calib_max_std = 0.015;      // rad/s
  // ZUPT (휠 정지 구간 온라인 바이어스 재추정) — 09-10 도입, IMU 단독 정지 판정은 느린 회전을 흡수하므로 쓰지 않는다(§10)
  double zupt_stationary_vx = 0.005;    // m/s
  double zupt_stationary_vyaw = 0.005;  // rad/s
  std::size_t zupt_win = 400;           // 200 Hz × 2 s
  double zupt_max_std = 0.010;          // rad/s
  double zupt_alpha = 0.10;
  double zupt_max_step = 0.0005;        // rad/s
  // ── B2 제자리 회전 ICR 모델 (2026-09-28 §26~27) — 기본 꺼짐. 회전 시험 16 회 스캔 정합으로 식별:
  //   제자리 회전 중 차체는 차체 좌표의 점 p 를 축으로 돈다(시계·반시계 따로). leave-one-out 잔차 중앙값 3.8 cm(보정 전 13.5).
  bool icr_enable = false;
  double icr_cw_px = -0.029, icr_cw_py = 0.052;     // m — 시계(ω<0) 회전축(차체 앞+/왼+)
  double icr_ccw_px = -0.029, icr_ccw_py = -0.095;  // m — 반시계(ω>0)
  double icr_v_max = 0.02;    // m/s — 휠 |vx| 가 이보다 작고
  double icr_w_min = 0.10;    // rad/s — |ω| 가 이보다 크면 '순수 회전' 으로 본다 (호 회전은 미식별이라 적용 안 함, §7.2)
  // ── B3 순수 회전 구간 가변 공분산 — 기본 꺼짐. 휠 vy = 0 ± 0.01 주장이 회전 중 옆 밀림을 부정하지 않도록(§20.5, §26)
  bool rot_cov_enable = false;
  double rot_vx_var = 0.03 * 0.03;   // (m/s)^2
  double rot_vy_var = 0.03 * 0.03;   // (m/s)^2
};

using Vec3 = std::array<double, 3>;

// 표본 평균·모표준편차 (Python 판과 같은 순서로 합산해 수치가 같게)
inline void meanStd(const std::vector<Vec3> & s, Vec3 & mean, Vec3 & stdev)
{
  const double n = static_cast<double>(s.size());
  for (int k = 0; k < 3; ++k) {
    double sum = 0.0;
    for (const auto & v : s) {sum += v[k];}
    mean[k] = sum / n;
  }
  for (int k = 0; k < 3; ++k) {
    double sq = 0.0;
    for (const auto & v : s) {sq += (v[k] - mean[k]) * (v[k] - mean[k]);}
    stdev[k] = std::sqrt(sq / n);
  }
}

inline double maxOf(const Vec3 & v) {return std::fmax(v[0], std::fmax(v[1], v[2]));}

// 부팅 캘리브레이션 + ZUPT 로 자이로 바이어스를 관리한다.
class GyroBias
{
public:
  enum class CalibResult { kCollecting, kCalibrated, kNotStationary };

  explicit GyroBias(const ConditionerParams & p) : p_(p) {}

  bool ready() const {return ready_;}
  const Vec3 & bias() const {return bias_;}
  const Vec3 & calibStd() const {return calib_std_;}

  // 캘리브 표본 추가. 완료 전에는 발행하지 않는다(Python 판과 같음 — 완료시키는 표본도 발행 안 함).
  CalibResult addCalibSample(const Vec3 & raw)
  {
    samples_.push_back(raw);
    if (samples_.size() < p_.calib_samples) {return CalibResult::kCollecting;}
    Vec3 m{}, s{};
    meanStd(samples_, m, s);
    calib_std_ = s;
    samples_.clear();
    samples_.shrink_to_fit();
    ready_ = true;
    if (maxOf(s) < p_.calib_max_std) {
      bias_ = m;
      return CalibResult::kCalibrated;
    }
    bias_ = {0.0, 0.0, 0.0};
    return CalibResult::kNotStationary;
  }

  void setStationary(bool st) {stationary_ = st;}

  // ZUPT: 원시 자이로를 받는다. 갱신했으면 true, old_y 에 갱신 전 y 바이어스, obs 에 관측 평균.
  bool zuptUpdate(const Vec3 & raw, double & old_y, Vec3 & obs)
  {
    if (!stationary_) {
      if (!zbuf_.empty()) {zbuf_.clear();}   // 움직이면 부분 표본은 버린다
      return false;
    }
    zbuf_.push_back(raw);
    if (zbuf_.size() < p_.zupt_win) {return false;}
    Vec3 m{}, s{};
    meanStd(zbuf_, m, s);
    zbuf_.clear();
    if (maxOf(s) >= p_.zupt_max_std) {return false;}   // 휠은 0 인데 흔들림 = 손으로 옮기는 중 등
    old_y = bias_[1];
    for (int k = 0; k < 3; ++k) {
      double step = (m[k] - bias_[k]) * p_.zupt_alpha;
      if (step > p_.zupt_max_step) {step = p_.zupt_max_step;} else if (step < -p_.zupt_max_step) {step = -p_.zupt_max_step;}
      bias_[k] += step;
    }
    obs = m;
    ++count_;
    return true;
  }

  int zuptCount() const {return count_;}

private:
  ConditionerParams p_;
  bool ready_ = false;
  bool stationary_ = false;
  Vec3 bias_{0.0, 0.0, 0.0};
  Vec3 calib_std_{0.0, 0.0, 0.0};
  std::vector<Vec3> samples_;
  std::vector<Vec3> zbuf_;
  int count_ = 0;
};

// 휠 정지 판정 (보정 전 원시값 기준 — Python 판과 같음)
inline bool wheelStationary(const ConditionerParams & p, double vx, double wz)
{
  return std::fabs(vx) < p.zupt_stationary_vx && std::fabs(wz) < p.zupt_stationary_vyaw;
}

// 회전 슬립 계수 — |vyaw| 2 점 선형보간(범위 밖 클램프). 현재 두 점 모두 1.0(무동작).
inline double yawSlipFactor(const ConditionerParams & p, double vyaw)
{
  const double a = std::fabs(vyaw);
  if (a <= p.slip_x0) {return p.slip_y0;}
  if (a >= p.slip_x1) {return p.slip_y1;}
  return p.slip_y0 + (p.slip_y1 - p.slip_y0) * (a - p.slip_x0) / (p.slip_x1 - p.slip_x0);
}

// '순수 회전' 판정 — 휠 vx 는 작고 회전은 크다. ω 는 자이로(휠 ω 는 스크럽으로 최대 +16 % 과대, §6).
inline bool pureRotation(const ConditionerParams & p, double vx, double w)
{
  return std::fabs(vx) < p.icr_v_max && std::fabs(w) > p.icr_w_min;
}

// B2: 회전축 p 로 도는 차체의 순간 속도 = ω ẑ × (−p) = (ω·py, −ω·px). 순수 회전이 아니거나 꺼져 있으면 0.
//   검산(§27): 시계 0.38 rad/s, p (−0.029, +0.052) → 180° 적분 이동 (−0.058, +0.104) m = 2p(측정 평균).
struct TwistAdd
{
  double vx, vy;
  bool active;
};
inline TwistAdd icrTwistAdd(const ConditionerParams & p, double vx, double w)
{
  if (!p.icr_enable || !pureRotation(p, vx, w)) {return {0.0, 0.0, false};}
  const double px = (w < 0.0) ? p.icr_cw_px : p.icr_ccw_px;
  const double py = (w < 0.0) ? p.icr_cw_py : p.icr_ccw_py;
  return {w * py, -w * px, true};
}

// 휠 twist 공분산 정책. 기본 = 고정값(Python 판과 같음). B3: 순수 회전 구간에서 vx·vy 분산을 키운다.
struct WheelTwistCov
{
  double vx, vy, vyaw;
};
inline WheelTwistCov wheelTwistCov(const ConditionerParams & p, double vx, double w)
{
  if (p.rot_cov_enable && pureRotation(p, vx, w)) {return {p.rot_vx_var, p.rot_vy_var, p.vyaw_var};}
  return {p.vx_var, p.vy_var, p.vyaw_var};
}

}  // namespace rover_bringup
