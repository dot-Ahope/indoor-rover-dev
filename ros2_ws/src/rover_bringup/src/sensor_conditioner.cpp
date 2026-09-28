// 센서 컨디셔너 노드 (C++) — scripts/sensor_conditioner.py 와 같은 토픽·QoS·동작 (2026-09-28 이식).
//   입력: /imu/data_raw (launch 에서 /camera/camera/imu 로 remap, 200 Hz), /wheel_odom (25 Hz)
//   출력: /imu/data (바이어스 제거·covariance·orientation 미제공 표식), /wheel_odom/conditioned (twist covariance)
//   근거·검증: Docs/debug_log/2026-09-28/SUMMARY.md §10~ . 로직은 include/rover_bringup/conditioner_core.hpp
#include <memory>

#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rover_bringup/conditioner_core.hpp"
#include "sensor_msgs/msg/imu.hpp"

namespace rover_bringup
{

class SensorConditioner : public rclcpp::Node
{
public:
  SensorConditioner()
  : rclcpp::Node("sensor_conditioner"), p_(loadParams()), gyro_(p_)
  {
    // 자이로 → 로봇 yaw rate: 카메라 IMU 광학 프레임에서 로봇 yaw = 광학 −y (ekf.yaml imu0_config 인덱스 10 과 같은 근거).
    //   생성자 본문에서 선언 — p_ 초기화(loadParams) 안에서 대입하면 뒤이은 멤버 기본값 초기화가 덮어쓴다.
    gyro_yaw_axis_ = static_cast<int>(declare_parameter("gyro_yaw_axis", static_cast<int64_t>(1)));
    gyro_yaw_sign_ = declare_parameter("gyro_yaw_sign", -1.0);
    const auto qos = rclcpp::SensorDataQoS();   // Python 판 qos_profile_sensor_data 와 같음(best effort, depth 5)
    imu_pub_ = create_publisher<sensor_msgs::msg::Imu>("/imu/data", qos);
    odom_pub_ = create_publisher<nav_msgs::msg::Odometry>("/wheel_odom/conditioned", qos);
    imu_sub_ = create_subscription<sensor_msgs::msg::Imu>(
      "/imu/data_raw", qos, [this](sensor_msgs::msg::Imu::UniquePtr m) {onImu(std::move(m));});
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/wheel_odom", qos, [this](nav_msgs::msg::Odometry::UniquePtr m) {onOdom(std::move(m));});
  }

private:
  ConditionerParams loadParams()
  {
    ConditionerParams d;   // 기본값 = Python 판 상수
    ConditionerParams p;
    p.gyro_var = declare_parameter("gyro_var", d.gyro_var);
    p.accel_var = declare_parameter("accel_var", d.accel_var);
    p.vx_var = declare_parameter("vx_var", d.vx_var);
    p.vy_var = declare_parameter("vy_var", d.vy_var);
    p.vyaw_var = declare_parameter("vyaw_var", d.vyaw_var);
    p.vx_scale = declare_parameter("vx_scale", d.vx_scale);
    p.calib_samples = static_cast<std::size_t>(declare_parameter("calib_samples", static_cast<int64_t>(d.calib_samples)));
    p.calib_max_std = declare_parameter("calib_max_std", d.calib_max_std);
    p.zupt_stationary_vx = declare_parameter("zupt_stationary_vx", d.zupt_stationary_vx);
    p.zupt_stationary_vyaw = declare_parameter("zupt_stationary_vyaw", d.zupt_stationary_vyaw);
    p.zupt_win = static_cast<std::size_t>(declare_parameter("zupt_win", static_cast<int64_t>(d.zupt_win)));
    p.zupt_max_std = declare_parameter("zupt_max_std", d.zupt_max_std);
    p.zupt_alpha = declare_parameter("zupt_alpha", d.zupt_alpha);
    p.zupt_max_step = declare_parameter("zupt_max_step", d.zupt_max_step);
    // B2·B3 (09-28 §27) — 기본 꺼짐
    p.icr_enable = declare_parameter("icr_enable", d.icr_enable);
    p.icr_cw_px = declare_parameter("icr_cw_px", d.icr_cw_px);
    p.icr_cw_py = declare_parameter("icr_cw_py", d.icr_cw_py);
    p.icr_ccw_px = declare_parameter("icr_ccw_px", d.icr_ccw_px);
    p.icr_ccw_py = declare_parameter("icr_ccw_py", d.icr_ccw_py);
    p.icr_v_max = declare_parameter("icr_v_max", d.icr_v_max);
    p.icr_w_min = declare_parameter("icr_w_min", d.icr_w_min);
    p.rot_cov_enable = declare_parameter("rot_cov_enable", d.rot_cov_enable);
    p.rot_vx_var = declare_parameter("rot_vx_var", d.rot_vx_var);
    p.rot_vy_var = declare_parameter("rot_vy_var", d.rot_vy_var);
    return p;
  }

  void onImu(sensor_msgs::msg::Imu::UniquePtr msg)
  {
    const Vec3 raw{msg->angular_velocity.x, msg->angular_velocity.y, msg->angular_velocity.z};
    if (!gyro_.ready()) {
      const auto r = gyro_.addCalibSample(raw);
      const auto & b = gyro_.bias();
      const auto & s = gyro_.calibStd();
      if (r == GyroBias::CalibResult::kCalibrated) {
        RCLCPP_INFO(get_logger(), "gyro bias calibrated: (%.5f, %.5f, %.5f) rad/s, std=(%.4f, %.4f, %.4f)",
          b[0], b[1], b[2], s[0], s[1], s[2]);
      } else if (r == GyroBias::CalibResult::kNotStationary) {
        RCLCPP_WARN(get_logger(), "startup not stationary (max std=%.4f) — bias=0 유지", maxOf(s));
      }
      return;   // 캘리브 완료 전에는 발행 보류
    }
    double old_y = 0.0;
    Vec3 obs{};
    if (gyro_.zuptUpdate(raw, old_y, obs)) {
      const double now = get_clock()->now().seconds();
      if (now - zlast_log_ >= 20.0) {   // Python 판 ZUPT_LOG_PERIOD
        zlast_log_ = now;
        const double resid = -(obs[1] - gyro_.bias()[1]);   // EKF 가 쓰는 로봇 yaw rate = 광학 -y
        RCLCPP_INFO(get_logger(), "ZUPT #%d: bias y %.6f → %.6f (관측 %.6f), 잔차 yaw rate %+.6f rad/s = %+.2f °/분",
          gyro_.zuptCount(), old_y, gyro_.bias()[1], obs[1], resid, resid * 57.29578 * 60.0);
      }
    }
    const auto & b = gyro_.bias();
    msg->angular_velocity.x -= b[0];
    msg->angular_velocity.y -= b[1];
    msg->angular_velocity.z -= b[2];
    for (int i = 0; i < 9; ++i) {
      const bool diag = (i == 0 || i == 4 || i == 8);
      msg->angular_velocity_covariance[i] = diag ? p_.gyro_var : 0.0;
      msg->linear_acceleration_covariance[i] = diag ? p_.accel_var : 0.0;
    }
    msg->orientation_covariance[0] = -1.0;   // orientation 미제공 표식(REP-145) — EKF 가 자세를 쓰지 않도록
    // B2 판정용 로봇 yaw rate(바이어스 제거 뒤) 보관
    const double g[3] = {msg->angular_velocity.x, msg->angular_velocity.y, msg->angular_velocity.z};
    gyro_yaw_ = gyro_yaw_sign_ * g[(gyro_yaw_axis_ >= 0 && gyro_yaw_axis_ < 3) ? gyro_yaw_axis_ : 1];
    gyro_t_ = now().seconds();
    imu_pub_->publish(std::move(msg));
  }

  void onOdom(nav_msgs::msg::Odometry::UniquePtr msg)
  {
    auto & tw = msg->twist.twist;
    const double vx_raw = tw.linear.x;
    gyro_.setStationary(wheelStationary(p_, tw.linear.x, tw.angular.z));
    tw.linear.x *= p_.vx_scale;
    tw.angular.z *= yawSlipFactor(p_, tw.angular.z);
    // 회전 판정 ω: 최근(0.1 s 안) 자이로가 있으면 자이로, 없으면 휠 ω
    const double w = (gyro_t_ > 0.0 && now().seconds() - gyro_t_ < 0.1) ? gyro_yaw_ : tw.angular.z;
    const auto add = icrTwistAdd(p_, vx_raw, w);   // B2 (꺼져 있으면 0)
    tw.linear.x += add.vx;
    tw.linear.y += add.vy;
    const auto c = wheelTwistCov(p_, vx_raw, w);    // B3 (꺼져 있으면 고정값)
    msg->twist.covariance[0] = c.vx;
    msg->twist.covariance[7] = c.vy;
    msg->twist.covariance[35] = c.vyaw;
    odom_pub_->publish(std::move(msg));
  }

  ConditionerParams p_;
  GyroBias gyro_;
  double zlast_log_ = 0.0;
  double gyro_yaw_ = 0.0, gyro_t_ = 0.0, gyro_yaw_sign_ = -1.0;
  int gyro_yaw_axis_ = 1;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
};

}  // namespace rover_bringup

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<rover_bringup::SensorConditioner>());
  rclcpp::shutdown();
  return 0;
}
