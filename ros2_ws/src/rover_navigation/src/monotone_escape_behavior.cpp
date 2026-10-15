// MonotoneEscape — Nav2 behavior_server 플러그인: '여유가 줄지 않는 이동'으로 교착(서 있는 자세부터 닿음 판정)에서 빠져나온다.
//
// 2026-10-15 (Docs/debug_log/2026-10-15/SUMMARY.md §25~§26):
//   라이다 아래 낮은 물체(카메라만 봄) 옆에서 지도상 여유가 칸 검사 기준(약 4.4 cm) 아래로 내려가면 MPPI 의 모든 후보와 Nav2 BackUp 이
//   첫 점부터 '충돌'로 거부되어 약 12 s 만에 Nav2 가 포기했다(f2v1 · f2v3 · f2v4, 10-14 f2t1 · f2u2). 실측 여유는 8~9 cm 였다(§18.2).
//   카메라의 몇 cm 과장은 안전한 쪽 오차라 그대로 둔다(사용자: 카메라 회피가 중요). 대신 이 동작은 앞 · 뒤 직진과 제자리 좌 · 우 회전 중
//   '차체 다각형 ↔ 모든 치명 칸(라이다 · 카메라 구분 없음) 정확한 거리가 한 걸음도 줄지 않는' 움직임만 골라 천천히 실행한다.
//   → 어떤 물체에도 지금보다 가까워지지 않는다(지도가 맞든 틀리든 지금보다 위험해지지 않음). 실행 중 파라미터 변경 없음(10-14 pad_relief 의 멈칫 부작용 없음).
//   오프라인 검증: 실패 5 건 모두 0.02~0.30 m 직진으로 최근접 5 cm 도달(§25.1). 회전은 f2v3 자세에서 우 15° 로 2.7 → 8.7 cm(§18.1 탐색).
//
// 동작: 시작 때 지금 코스트맵으로 네 가지 움직임(앞 · 뒤 최대 max_travel, 좌 · 우 최대 max_rotation)을 작은 걸음으로 모의해
//   '거리가 줄지 않은 채 target_clearance 에 닿는' 것 중 가장 짧은(정규화) 것을 고른다. 실행 중에는 매 주기 코스트맵을 다시 보고
//   거리가 decrease_tolerance 넘게 줄면 즉시 멈추고 실패한다(움직이는 동안 새로 찍힌 칸 대비). target 에 닿으면 성공 → BT 가 경로를 다시 계획.
//   어떤 움직임도 target 에 못 닿으면 움직이지 않고 실패(→ BT 의 Wait 로 넘어감 — 기존과 같음).
// 액션 형식: nav2_msgs/action/BackUp 재사용(BT 의 BackUp 노드를 server_name 으로 이 서버에 연결; backup_dist · backup_speed 는 쓰지 않음, time_allowance 만 씀).
// 기각한 대안: pad_relief(실행 중 footprint_padding 변경 — 멈칫 · 잔떨림 부작용, 10-14 §21) · 대기 연장(시야 밖 카메라 칸이 감쇠하면 실제 상자도 지도에서 사라짐, §18.3)
//   · 카메라 칸 일괄/깜빡임 기준 낮추기(§9 · §12) · nvblox site 거리(§22~§23 효과 없음).
#include <algorithm>
#include <cmath>
#include <limits>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

#include "nav2_behaviors/timed_behavior.hpp"
#include "nav2_msgs/action/back_up.hpp"
#include "nav2_msgs/msg/costmap.hpp"
#include "nav2_util/node_utils.hpp"
#include "nav2_util/robot_utils.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace rover_navigation
{
using nav2_behaviors::Status;
using BackUpAction = nav2_msgs::action::BackUp;

class MonotoneEscape : public nav2_behaviors::TimedBehavior<BackUpAction>
{
public:
  MonotoneEscape() = default;

  void onConfigure() override
  {
    auto node = node_.lock();
    if (!node) {throw std::runtime_error{"MonotoneEscape: node lock 실패"};}
    const std::string p = behavior_name_ + ".";
    auto decl = [&](const std::string & n, double v) {
        nav2_util::declare_parameter_if_not_declared(node, p + n, rclcpp::ParameterValue(v));
        double out; node->get_parameter(p + n, out); return out;
      };
    max_travel_ = decl("max_travel", 0.30);             // 직진 최대(m) — 오프라인 검증 범위
    max_rotation_ = decl("max_rotation", 0.52);         // 회전 최대(rad, 약 30°)
    target_clearance_ = decl("target_clearance", 0.05); // 이만큼 여유가 생기면 성공(m) — 칸 검사 막힘 약 4.4 cm(09-23) 위
    lin_speed_ = decl("linear_speed", 0.03);            // m/s — 천천히
    ang_speed_ = decl("angular_speed", 0.15);           // rad/s
    decrease_tol_ = decl("decrease_tolerance", 0.003);  // 실행 중 거리 감소 허용(m) — 코스트맵 갱신 · 자세 잡음
    x_front_ = decl("footprint_front", 0.272);          // 차체 직사각형(패딩 포함, 발행 풋프린트 0.53 × 0.35 와 같음)
    x_rear_ = decl("footprint_rear", -0.258);
    half_width_ = decl("footprint_half_width", 0.175);
    search_radius_ = decl("search_radius", 1.0);        // 이 반경 안의 치명 칸만 계산
    nav2_util::declare_parameter_if_not_declared(node, p + "costmap_topic", rclcpp::ParameterValue(std::string("local_costmap/costmap_raw")));
    std::string topic; node->get_parameter(p + "costmap_topic", topic);
    costmap_sub_ = node->create_subscription<nav2_msgs::msg::Costmap>(
      topic, rclcpp::QoS(1).transient_local().reliable(),
      [this](nav2_msgs::msg::Costmap::SharedPtr m) {std::lock_guard<std::mutex> g(mu_); costmap_ = m;});
  }

  Status onRun(const std::shared_ptr<const BackUpAction::Goal> command) override
  {
    time_allowance_ = command->time_allowance;
    end_time_ = clock_->now() + time_allowance_;
    double x, y, th;
    if (!pose(x, y, th)) {RCLCPP_ERROR(logger_, "[monotone_escape] 자세 없음"); return Status::FAILED;}
    std::vector<std::pair<double, double>> cells;
    if (!obstacles(x, y, cells)) {RCLCPP_ERROR(logger_, "[monotone_escape] 코스트맵 없음"); return Status::FAILED;}
    start_x_ = x; start_y_ = y; start_th_ = th;
    const double c0 = clearance(x, y, th, cells);
    // 네 가지 움직임 모의: 0 앞 · 1 뒤 · 2 좌회전 · 3 우회전
    static const char * names[4] = {"앞", "뒤", "좌회전", "우회전"};
    int best = -1; double best_cost = std::numeric_limits<double>::max(), best_amt = 0.0;
    std::string report;
    for (int k = 0; k < 4; ++k) {
      const bool lin = k < 2; const double sign = (k == 0 || k == 2) ? 1.0 : -1.0;
      const double step = lin ? 0.01 : 0.0175, limit = lin ? max_travel_ : max_rotation_;
      double prev = c0, reached = -1.0, last = c0;
      for (double a = step; a <= limit + 1e-9; a += step) {
        const double px = lin ? x + sign * a * std::cos(th) : x, py = lin ? y + sign * a * std::sin(th) : y;
        const double pt = lin ? th : th + sign * a;
        const double c = clearance(px, py, pt, cells);
        if (c < prev - 2e-4) {break;}  // 모의에선 한 걸음도 줄면 안 됨
        prev = c; last = c;
        if (c >= target_clearance_) {reached = a; break;}
      }
      char buf[96];
      if (reached > 0) {std::snprintf(buf, sizeof(buf), " %s:%.3f", names[k], reached);}
      else {std::snprintf(buf, sizeof(buf), " %s:없음(끝 %.1f cm)", names[k], last * 100);}
      report += buf;
      if (reached > 0) {
        const double cost = reached / limit;
        if (cost < best_cost) {best_cost = cost; best = k; best_amt = reached;}
      }
    }
    RCLCPP_INFO(logger_, "[monotone_escape] 시작 최근접 %.1f cm · 목표 %.1f cm · 모의 결과(닿는 양 m/rad):%s",
      c0 * 100, target_clearance_ * 100, report.c_str());
    if (c0 >= target_clearance_) {mode_ = -1; prev_clear_ = c0; return Status::SUCCEEDED;}  // 이미 여유 있음 → 첫 주기에 성공
    if (best < 0) {RCLCPP_WARN(logger_, "[monotone_escape] 거리가 줄지 않고 목표에 닿는 움직임 없음 → 움직이지 않음"); return Status::FAILED;}
    mode_ = best; amount_ = best_amt + (best < 2 ? 0.01 : 0.0175); prev_clear_ = c0;
    RCLCPP_INFO(logger_, "[monotone_escape] 선택: %s %.3f", names[best], best_amt);
    return Status::SUCCEEDED;
  }

  Status onCycleUpdate() override
  {
    if (time_allowance_.seconds() > 0.0 && clock_->now() > end_time_) {
      stopRobot(); RCLCPP_WARN(logger_, "[monotone_escape] 시간 초과"); return Status::FAILED;
    }
    double x, y, th;
    std::vector<std::pair<double, double>> cells;
    if (!pose(x, y, th) || !obstacles(x, y, cells)) {stopRobot(); return Status::FAILED;}
    const double c = clearance(x, y, th, cells);
    if (c >= target_clearance_) {
      stopRobot(); RCLCPP_INFO(logger_, "[monotone_escape] 성공: 최근접 %.1f cm", c * 100); return Status::SUCCEEDED;
    }
    if (mode_ < 0) {stopRobot(); return Status::SUCCEEDED;}
    if (c < prev_clear_ - decrease_tol_) {
      stopRobot(); RCLCPP_WARN(logger_, "[monotone_escape] 거리 감소 %.1f → %.1f cm — 멈춤", prev_clear_ * 100, c * 100); return Status::FAILED;
    }
    prev_clear_ = std::max(prev_clear_, c);
    const double moved = mode_ < 2 ? std::hypot(x - start_x_, y - start_y_) : std::fabs(angdiff(th, start_th_));
    if (moved >= amount_) {
      stopRobot(); RCLCPP_WARN(logger_, "[monotone_escape] 계획한 양을 다 갔는데 목표 미달(최근접 %.1f cm)", c * 100); return Status::FAILED;
    }
    auto cmd = std::make_unique<geometry_msgs::msg::Twist>();
    if (mode_ == 0) {cmd->linear.x = lin_speed_;} else if (mode_ == 1) {cmd->linear.x = -lin_speed_;}
    else if (mode_ == 2) {cmd->angular.z = ang_speed_;} else {cmd->angular.z = -ang_speed_;}
    vel_pub_->publish(std::move(cmd));
    return Status::RUNNING;
  }

private:
  static double angdiff(double a, double b) {return std::atan2(std::sin(a - b), std::cos(a - b));}

  bool pose(double & x, double & y, double & th)
  {
    geometry_msgs::msg::PoseStamped p;
    if (!nav2_util::getCurrentPose(p, *tf_, global_frame_, robot_base_frame_, transform_tolerance_)) {return false;}
    x = p.pose.position.x; y = p.pose.position.y; th = tf2::getYaw(p.pose.orientation); return true;
  }

  // 코스트맵(odom, behavior global_frame 과 같아야 함)의 치명 칸(254) 중심 — 로버 둘레 search_radius 안만
  bool obstacles(double x, double y, std::vector<std::pair<double, double>> & out)
  {
    nav2_msgs::msg::Costmap::SharedPtr m;
    {std::lock_guard<std::mutex> g(mu_); m = costmap_;}
    if (!m) {return false;}
    const auto & md = m->metadata; const double r = md.resolution;
    const double ox = md.origin.position.x, oy = md.origin.position.y;
    out.clear();
    for (unsigned int j = 0; j < md.size_y; ++j) {
      for (unsigned int i = 0; i < md.size_x; ++i) {
        if (m->data[j * md.size_x + i] != 254) {continue;}
        const double cx = ox + (i + 0.5) * r, cy = oy + (j + 0.5) * r;
        if (std::hypot(cx - x, cy - y) <= search_radius_) {out.emplace_back(cx, cy);}
      }
    }
    return true;
  }

  // 차체 직사각형(몸체 좌표) ↔ 칸 중심 최소 거리. 칸이 차체 안이면 0.
  double clearance(double x, double y, double th, const std::vector<std::pair<double, double>> & cells) const
  {
    const double c = std::cos(th), s = std::sin(th); double best = std::numeric_limits<double>::max();
    for (const auto & p : cells) {
      const double dx = p.first - x, dy = p.second - y, bx = c * dx + s * dy, by = -s * dx + c * dy;
      const double ex = std::max({x_rear_ - bx, bx - x_front_, 0.0}), ey = std::max(std::fabs(by) - half_width_, 0.0);
      best = std::min(best, std::hypot(ex, ey));
    }
    return best;
  }

  rclcpp::Subscription<nav2_msgs::msg::Costmap>::SharedPtr costmap_sub_;
  nav2_msgs::msg::Costmap::SharedPtr costmap_;
  std::mutex mu_;
  double max_travel_{0.30}, max_rotation_{0.52}, target_clearance_{0.05}, lin_speed_{0.03}, ang_speed_{0.15};
  double decrease_tol_{0.003}, x_front_{0.272}, x_rear_{-0.258}, half_width_{0.175}, search_radius_{1.0};
  double start_x_{0}, start_y_{0}, start_th_{0}, amount_{0}, prev_clear_{0};
  int mode_{-1};
  rclcpp::Duration time_allowance_{0, 0};
  rclcpp::Time end_time_;
};

}  // namespace rover_navigation

PLUGINLIB_EXPORT_CLASS(rover_navigation::MonotoneEscape, nav2_core::Behavior)
