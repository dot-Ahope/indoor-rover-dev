// CopyPath — 블랙보드의 경로를 다른 키로 그대로 복사하는 BT 동작 노드(점의 위치·방향을 바꾸지 않음)
//
// 2026-10-14 (Docs/debug_log/2026-10-14/SUMMARY.md §13.1·§14): 경로 다듬기(SmoothPath)가 실패했을 때 원경로를 {path} 로 넘기는 데
//   Nav2 TruncatePath(distance 0)를 쓰고 있었다(09-17 mp6). 그런데 TruncatePath 는 마지막 점 방향을 앞 점과의 방향
//   atan2(0, 0) = 0 으로 덮어써서, 컨트롤러가 받는 목표 방향이 원래 목표(예: −56°)가 아니라 0° 가 됐다.
//   f2s1 목표 3(서쪽 통로): 목표 자세가 좁은 곳이라 스무딩이 매번 실패 → 컨트롤러 끝 방향 +5° → 로버는 −64° 에서
//   64° 를 돌아야 했고, 바로 옆 실제 낮은 물체(라이다 아래 밑동) 때문에 돌지 못해 45 s 뒤 nav_guard 취소.
//   (09-17 BT 주석의 TODO(improve) "전용 복사 노드로 교체할 것" 을 이 노드로 해소한다.)
//
// 동작: input_path 를 output_path 로 그대로 쓴다. 입력이 없거나 점이 0 개면 FAILURE.
//
// 2026-10-26 (Docs/debug_log/2026-10-26/SUMMARY.md §7): step > 0 이면 경로를 호 길이 step 간격으로 다시 찍는다(위치는 선형 보간,
//   방향은 그 구간 시작 점의 방향, 마지막 점은 원래 그대로). 왜: Smac Hybrid 경로 점 간격 ≈ 0.07 m 인데 MPPI 경로 크리틱의
//   offset_from_furthest 는 '점 개수' 라(PathAlign 3 = NavFn 경로에선 ≈ 0.1 m), 간격이 다르면 크리틱이 켜지는 거리가 2~3 배로 바뀜.
//   NavFn(+SimpleSmoother) 경로 간격 0.026~0.047 m 에 맞춰 0.03 m 로 쓴다. step 0(기본) = 예전과 같은 그대로 복사.
//
// 기각한 대안:
//   · BT.CPP SetBlackboard: 값 포트가 문자열이라 nav_msgs::Path 를 그대로 옮길 수 없다(v3).
//   · ComputePathToPose 가 바로 {path} 에 쓰고 SmoothPath 도 {path} 에 덮어쓰기: 한 틱에 {path} 가 두 번 바뀌어
//     FollowPath 가 목표를 두 번 받는다(09-16 mp4, "Aborting handle" 매초).
#include <cmath>
#include <string>

#include "behaviortree_cpp_v3/action_node.h"
#include "nav_msgs/msg/path.hpp"

namespace rover_navigation
{

class CopyPath : public BT::SyncActionNode
{
public:
  CopyPath(const std::string & name, const BT::NodeConfiguration & conf)
  : BT::SyncActionNode(name, conf) {}

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<nav_msgs::msg::Path>("input_path", "복사할 경로"),
      BT::OutputPort<nav_msgs::msg::Path>("output_path", "그대로 복사된 경로(점 위치·방향 유지)"),
      BT::InputPort<double>("step", 0.0, "0 보다 크면 이 호 길이 간격(m)으로 다시 찍음"),
    };
  }

  BT::NodeStatus tick() override
  {
    nav_msgs::msg::Path p;
    if (!getInput("input_path", p) || p.poses.empty()) {
      return BT::NodeStatus::FAILURE;
    }
    double step = 0.0;
    getInput("step", step);
    if (step > 0.0 && p.poses.size() > 1) {
      nav_msgs::msg::Path r;
      r.header = p.header;
      r.poses.push_back(p.poses.front());
      double carry = 0.0;   // 직전에 찍은 점 뒤로 이 구간 시작까지 남은 거리
      for (size_t i = 1; i < p.poses.size(); ++i) {
        const auto & a = p.poses[i - 1].pose.position;
        const auto & b = p.poses[i].pose.position;
        const double seg = std::hypot(b.x - a.x, b.y - a.y);
        double s = step - carry;
        while (s < seg) {
          auto q = p.poses[i - 1];
          q.pose.position.x = a.x + (b.x - a.x) * s / seg;
          q.pose.position.y = a.y + (b.y - a.y) * s / seg;
          r.poses.push_back(q);
          s += step;
        }
        carry = seg - (s - step);
      }
      r.poses.push_back(p.poses.back());   // 끝 점(목표 방향 포함)은 원래 그대로
      setOutput("output_path", r);
      return BT::NodeStatus::SUCCESS;
    }
    setOutput("output_path", p);
    return BT::NodeStatus::SUCCESS;
  }
};

}  // namespace rover_navigation

#include "behaviortree_cpp_v3/bt_factory.h"
BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<rover_navigation::CopyPath>("CopyPath");
}
