// PathBlockedAhead — 전역 경로의 "앞 구간" 이 일정 시간 이상 막혀 있으면 SUCCESS 를 돌려주는 BT 조건 노드
//
// 2026-10-01 §8.39 (사용자 승인 (a)): f2a12 목표 7 에서 의자가 통로를 0.39 m 로 좁혔는데(§8.37~8.38)
//   경로를 목표당 1 회만 계획(RateController 0.01 Hz, §8.24)하므로 막힌 경로를 그대로 붙잡고
//   MPPI 가 0 근처 지령으로 떨다가(±0.015 m/s·±0.2 rad/s) nav_guard 가 45 s 에 취소했다.
//   진행 검사기(0.25 m/25 s) → FollowPath 재시도(같은 경로) → 재계획까지 50 s 이상 걸려 nav_guard(45 s)가 먼저 끊었다.
//
// 동작: 로버에서 가장 가까운 경로 점부터 앞으로 lookahead(1.5 m) 안의 경로 점을 전역 코스트맵에서 본다.
//   skip_near(0.30 m) 안은 보지 않는다 — 로버가 벽 가까이(inflation 띠) 서 있을 때 출발점 비용으로 오판하지 않기 위해.
//   한 점이라도 cost ≥ min_cost(OccupancyGrid 99 = 원래 253 = 내접, 로버 중심이 거기 가면 차체가 닿음)이고
//   그 상태가 hold_time(2.0 s) 이상 이어지면 SUCCESS(막힘). 경로가 바뀌면(재계획) 타이머를 다시 시작한다.
//
// 기각한 대안:
//   · Nav2 IsPathValid(§8.17): 경로 전체를 1 Hz 로 보고 한 번만 걸려도 무효 → 병목(여유 7~12 cm)에서 센서 표시가
//     흔들릴 때마다 재계획, f2a8 에서 200 s 에 170 회(§8.21). 여기서는 앞 1.5 m 만, 2 s 지속일 때만 본다.
//   · RateController 주기를 다시 올림: 막히지 않았는데도 경로가 통로 사이를 오가는 문제(§8.22~8.24)가 돌아온다.
//   · 진행 검사기 시간 단축: 좁은 통로에서 천천히 정렬하는 정상 주행까지 실패로 만든다.
#include <cmath>
#include <limits>
#include <memory>
#include <string>

#include "behaviortree_cpp_v3/condition_node.h"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_util/robot_utils.hpp"
#include "nav_msgs/msg/occupancy_grid.hpp"
#include "nav_msgs/msg/path.hpp"
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/buffer.h"

namespace rover_navigation
{

class PathBlockedAhead : public BT::ConditionNode
{
public:
  PathBlockedAhead(const std::string & name, const BT::NodeConfiguration & conf)
  : BT::ConditionNode(name, conf)
  {
    node_ = config().blackboard->get<rclcpp::Node::SharedPtr>("node");
    tf_ = config().blackboard->get<std::shared_ptr<tf2_ros::Buffer>>("tf_buffer");
    std::string topic = "/global_costmap/costmap";
    getInput("costmap_topic", topic);
    // BT 틱 안에서만 콜백을 돌리기 위해 별도 콜백 그룹·실행기(Nav2 IsBatteryLow 와 같은 방식)
    cb_group_ = node_->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive, false);
    executor_.add_callback_group(cb_group_, node_->get_node_base_interface());
    rclcpp::SubscriptionOptions opt;
    opt.callback_group = cb_group_;
    // 코스트맵 발행 QoS = transient_local·reliable(마지막 판을 늦게 붙은 구독자도 받음)
    sub_ = node_->create_subscription<nav_msgs::msg::OccupancyGrid>(
      topic, rclcpp::QoS(1).transient_local().reliable(),
      [this](nav_msgs::msg::OccupancyGrid::SharedPtr m) {grid_ = m;}, opt);
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<nav_msgs::msg::Path>("path", "따라가는 전역 경로"),
      BT::InputPort<double>("lookahead", 1.5, "로버 앞 검사 길이(m)"),
      BT::InputPort<double>("skip_near", 0.30, "로버 가까이 보지 않는 길이(m)"),
      BT::InputPort<double>("hold_time", 2.0, "막힘이 이만큼 이어져야 SUCCESS(s)"),
      BT::InputPort<int>("min_cost", 99, "막힘 판정 OccupancyGrid 값(99=내접 253, 100=치명 254)"),
      BT::InputPort<std::string>("costmap_topic", "/global_costmap/costmap", "전역 코스트맵 토픽"),
      BT::InputPort<std::string>("global_frame", "map", "경로·코스트맵 좌표계"),
      BT::InputPort<std::string>("robot_base_frame", "base_link", "로버 좌표계"),
    };
  }

  BT::NodeStatus tick() override
  {
    executor_.spin_some();
    nav_msgs::msg::Path path;
    if (!getInput("path", path) || path.poses.empty() || !grid_) {
      reset();
      return BT::NodeStatus::FAILURE;
    }
    // 경로가 바뀌었으면(재계획) 타이머를 처음부터. 계획 시각 + 점 수로 구분한다.
    const rclcpp::Time stamp(path.header.stamp);
    if (stamp != path_stamp_ || path.poses.size() != path_size_) {
      path_stamp_ = stamp;
      path_size_ = path.poses.size();
      reset();
    }
    double lookahead = 1.5, skip_near = 0.30, hold_time = 2.0;
    int min_cost = 99;
    std::string global_frame = "map", base_frame = "base_link";
    getInput("lookahead", lookahead);
    getInput("skip_near", skip_near);
    getInput("hold_time", hold_time);
    getInput("min_cost", min_cost);
    getInput("global_frame", global_frame);
    getInput("robot_base_frame", base_frame);

    geometry_msgs::msg::PoseStamped robot;
    if (!nav2_util::getCurrentPose(robot, *tf_, global_frame, base_frame, 0.2)) {
      return BT::NodeStatus::FAILURE;
    }
    const double rx = robot.pose.position.x, ry = robot.pose.position.y;

    // 로버에서 가장 가까운 경로 점
    size_t start = 0;
    double best = std::numeric_limits<double>::max();
    for (size_t i = 0; i < path.poses.size(); ++i) {
      const double d = std::hypot(path.poses[i].pose.position.x - rx, path.poses[i].pose.position.y - ry);
      if (d < best) {best = d; start = i;}
    }

    // 앞으로 경로 길이를 누적하며 skip_near~lookahead 구간의 칸 값을 본다
    const auto & g = *grid_;
    const double res = g.info.resolution, ox = g.info.origin.position.x, oy = g.info.origin.position.y;
    double along = 0.0;
    bool blocked = false;
    double bx = 0.0, by = 0.0;
    int bcost = 0;
    for (size_t i = start; i < path.poses.size(); ++i) {
      if (i > start) {
        along += std::hypot(path.poses[i].pose.position.x - path.poses[i - 1].pose.position.x,
                            path.poses[i].pose.position.y - path.poses[i - 1].pose.position.y);
      }
      if (along > lookahead) {break;}
      if (along < skip_near) {continue;}
      const double px = path.poses[i].pose.position.x, py = path.poses[i].pose.position.y;
      const int mx = static_cast<int>(std::floor((px - ox) / res));
      const int my = static_cast<int>(std::floor((py - oy) / res));
      if (mx < 0 || my < 0 || mx >= static_cast<int>(g.info.width) || my >= static_cast<int>(g.info.height)) {continue;}
      const int c = g.data[my * g.info.width + mx];
      if (c >= min_cost) {blocked = true; bx = px; by = py; bcost = c; break;}
    }

    const rclcpp::Time now = node_->now();
    if (!blocked) {
      reset();
      return BT::NodeStatus::FAILURE;
    }
    if (!blocked_since_) {
      blocked_since_ = std::make_unique<rclcpp::Time>(now);
      RCLCPP_INFO(node_->get_logger(), "PathBlockedAhead: 앞 경로 (%.2f, %.2f) 비용 %d — %.1f s 지속되면 재계획", bx, by, bcost, hold_time);
    }
    if ((now - *blocked_since_).seconds() >= hold_time) {
      RCLCPP_WARN(node_->get_logger(), "PathBlockedAhead: 앞 경로 (%.2f, %.2f) 비용 %d 가 %.1f s 지속 → 주행 중단·재계획", bx, by, bcost, hold_time);
      return BT::NodeStatus::SUCCESS;
    }
    return BT::NodeStatus::FAILURE;
  }

private:
  void reset() {blocked_since_.reset();}

  rclcpp::Node::SharedPtr node_;
  std::shared_ptr<tf2_ros::Buffer> tf_;
  rclcpp::CallbackGroup::SharedPtr cb_group_;
  rclcpp::executors::SingleThreadedExecutor executor_;
  rclcpp::Subscription<nav_msgs::msg::OccupancyGrid>::SharedPtr sub_;
  nav_msgs::msg::OccupancyGrid::SharedPtr grid_;
  rclcpp::Time path_stamp_{0, 0, RCL_ROS_TIME};
  size_t path_size_{0};
  std::unique_ptr<rclcpp::Time> blocked_since_;
};

}  // namespace rover_navigation

#include "behaviortree_cpp_v3/bt_factory.h"
BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<rover_navigation::PathBlockedAhead>("PathBlockedAhead");
}
