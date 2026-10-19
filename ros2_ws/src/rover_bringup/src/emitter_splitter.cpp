// 프로젝터 번갈이 분리 노드 (C++) — D455f 의 emitter_on_off(프레임마다 프로젝터 켬/끔 교대) 출력을 소비자별로 나눈다 (2026-10-19 §15).
//   왜: cuVSLAM 은 프로젝터 점 무늬가 없는 IR 스테레오가, nvblox · 점군은 프로젝터를 켠 깊이가 필요하다(09-29 §10, O1 채택).
//       Isaac 의 realsense_splitter(nvblox::RealsenseSplitterNode)는 컨테이너 · apt 에 없어 소스 빌드가 필요하고, 카메라는 호스트에 있다
//       → 호스트에서 같은 일을 하는 작은 노드. 판정 근거는 같다: 프레임별 메타데이터 json 의 "frame_emitter_mode".
//   입력(드라이버 4.58.3): <stream>/image_rect_raw(또는 points) + 같은 stamp 의 <stream>/metadata(json_data)
//   출력: 켬 프레임만 → depth 이미지 · 점군, 끔 프레임만 → infra1 · infra2 이미지. camera_info 는 나누지 않는다(Isaac 과 같음 —
//         소비자는 stamp 로 짝을 맞춘다).
//   ⚠ 켬 판정값(10-19 §15 S1 실측): 이 드라이버(4.58.3) · D455f 에서 frame_emitter_mode == 1 인 프레임이 오히려 프로젝터 **꺼진** 영상이었다
//     (깊이 유효 비율 0.32 vs 0.77, IR 점 무늬 |라플라시안| 0.6 vs 5.8, 두 무리 겹침 없음). 값 반전인지 한 프레임 밀림인지는 교대에선 구분 불가
//     → 파라미터 on_mode(기본 0 = 실측)로 두고, 내보낸 깊이의 유효 비율을 통계에 찍어 운용 중에도 확인한다.
//   짝 맞추기: 이미지와 메타데이터 중 먼저 온 쪽을 stamp(ns) 로 잠시 보관, 다른 쪽이 오면 판정. max_wait_s 넘게 짝이 없으면 버림(통계에 셈).
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <deque>
#include <map>
#include <memory>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "realsense2_camera_msgs/msg/metadata.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"

namespace rover_bringup
{

using Metadata = realsense2_camera_msgs::msg::Metadata;

// json_data 에서 정수 키 값을 꺼낸다(드라이버가 만드는 평평한 json — 전체 파서는 필요 없음). 없으면 -1.
inline int64_t jsonInt(const std::string & js, const std::string & key)
{
  const std::string pat = "\"" + key + "\":";
  const auto p = js.find(pat);
  if (p == std::string::npos) {return -1;}
  try {
    return std::stoll(js.substr(p + pat.size(), 24));
  } catch (...) {
    return -1;
  }
}

inline int64_t stampNs(const builtin_interfaces::msg::Time & t)
{
  return static_cast<int64_t>(t.sec) * 1000000000LL + t.nanosec;
}

// 한 스트림(이미지 또는 점군): 메타데이터 판정값을 기다리는 보관함 + 통계
template<typename MsgT>
class SplitStream
{
public:
  SplitStream(
    rclcpp::Node * node, const std::string & name, const std::string & in_topic, const std::string & meta_topic,
    const std::string & out_topic, bool keep_on, int64_t on_mode, const rclcpp::QoS & in_qos, const rclcpp::QoS & out_qos,
    double max_wait_s)
  : name_(name), keep_on_(keep_on), on_mode_(on_mode), max_wait_ns_(static_cast<int64_t>(max_wait_s * 1e9))
  {
    pub_ = node->create_publisher<MsgT>(out_topic, out_qos);
    sub_ = node->create_subscription<MsgT>(
      in_topic, in_qos, [this](typename MsgT::ConstSharedPtr m) {onMsg(std::move(m));});
    meta_sub_ = node->create_subscription<Metadata>(
      meta_topic, in_qos, [this](Metadata::ConstSharedPtr m) {onMeta(std::move(m));});
  }

  // 10 s 마다 한 줄: 들어온 수 · 켬 · 끔 · 짝 없음 버림 · 같은 상태 연속(교대가 깨진 횟수) · 판정 불가(키 없음)
  std::string statsLine()
  {
    char buf[256];
    std::snprintf(
      buf, sizeof(buf), "%s 입력 %lu · 켬 %lu · 끔 %lu · 내보냄 %lu · 짝없음 %lu · 교대깨짐 %lu · 키없음 %lu%s",
      name_.c_str(), n_in_, n_on_, n_off_, n_out_, n_expired_, n_repeat_, n_nokey_, validText().c_str());
    n_in_ = n_on_ = n_off_ = n_out_ = n_expired_ = n_repeat_ = n_nokey_ = 0;
    valid_sum_ = 0.0;
    return buf;
  }

private:
  std::string validText() const
  {
    if (valid_sum_ <= 0.0 || n_out_ == 0) {return "";}
    char b[48];
    std::snprintf(b, sizeof(b), " · 내보낸 깊이 유효 %.2f", valid_sum_ / n_out_);
    return b;
  }

  void onMsg(typename MsgT::ConstSharedPtr m)
  {
    ++n_in_;
    const int64_t t = stampNs(m->header.stamp);
    auto it = modes_.find(t);
    if (it != modes_.end()) {
      decide(m, it->second);
      modes_.erase(it);
    } else {
      pending_.emplace_back(t, std::move(m));
    }
    prune(t);
  }

  void onMeta(Metadata::ConstSharedPtr m)
  {
    const int64_t t = stampNs(m->header.stamp);
    int64_t mode = jsonInt(m->json_data, "frame_emitter_mode");
    if (mode < 0) {   // 판이 다른 드라이버 대비: 레이저 출력으로 대신 판정
      const int64_t lp = jsonInt(m->json_data, "frame_laser_power");
      mode = lp < 0 ? -1 : (lp > 0 ? 1 : 0);
    }
    if (mode < 0) {++n_nokey_; return;}
    if (mode == last_mode_) {++n_repeat_;}
    last_mode_ = mode;
    for (auto p = pending_.begin(); p != pending_.end(); ++p) {
      if (p->first == t) {
        decide(p->second, mode);
        pending_.erase(p);
        prune(t);
        return;
      }
    }
    modes_[t] = mode;
    prune(t);
  }

  void decide(const typename MsgT::ConstSharedPtr & m, int64_t mode)
  {
    const bool on = mode == on_mode_;
    on ? ++n_on_ : ++n_off_;
    if (on == keep_on_) {
      pub_->publish(*m);
      ++n_out_;
      if constexpr (std::is_same_v<MsgT, sensor_msgs::msg::Image>) {
        // 내보낸 깊이의 유효(0 아님) 화소 비율 — 켬 판정이 맞는지 운용 중 확인(S1: 켬 ≈ 0.77, 끔 ≈ 0.32, 160×120)
        if (m->encoding == "16UC1" && m->width * m->height > 0) {
          const auto * d = reinterpret_cast<const uint16_t *>(m->data.data());
          const std::size_t n = static_cast<std::size_t>(m->width) * m->height;
          std::size_t nz = 0;
          for (std::size_t i = 0; i < n; ++i) {nz += d[i] != 0;}
          valid_sum_ += static_cast<double>(nz) / n;
        }
      }
    }
  }

  // 오래된 보관분 정리 — 이미지 · 메타데이터 어느 쪽이든 max_wait 넘게 짝이 없으면 버린다
  void prune(int64_t now)
  {
    while (!pending_.empty() && now - pending_.front().first > max_wait_ns_) {
      pending_.pop_front();
      ++n_expired_;
    }
    while (!modes_.empty() && now - modes_.begin()->first > max_wait_ns_) {
      modes_.erase(modes_.begin());
    }
  }

  std::string name_;
  bool keep_on_;
  int64_t on_mode_;
  int64_t max_wait_ns_;
  typename rclcpp::Publisher<MsgT>::SharedPtr pub_;
  typename rclcpp::Subscription<MsgT>::SharedPtr sub_;
  rclcpp::Subscription<Metadata>::SharedPtr meta_sub_;
  std::deque<std::pair<int64_t, typename MsgT::ConstSharedPtr>> pending_;
  std::map<int64_t, int64_t> modes_;
  int64_t last_mode_{-1};
  double valid_sum_{0.0};
  unsigned long n_in_{0}, n_on_{0}, n_off_{0}, n_out_{0}, n_expired_{0}, n_repeat_{0}, n_nokey_{0};
};

class EmitterSplitter : public rclcpp::Node
{
public:
  EmitterSplitter()
  : rclcpp::Node("emitter_splitter")
  {
    const std::string in_ns = declare_parameter("in_ns", std::string("/camera/camera"));
    const std::string out_ns = declare_parameter("out_ns", std::string("/camera/split"));
    const double max_wait_s = declare_parameter("max_wait_s", 0.5);
    const bool split_points = declare_parameter("split_points", true);
    const int64_t on_mode = declare_parameter("on_mode", static_cast<int64_t>(0));   // 위 ⚠ — S1 실측
    // 입력은 best effort 로 받는다(reliable 발행자와도 맞음). 출력은 reliable — nvblox 의 깊이 구독(기본 QoS)이 reliable 이라
    //   best effort 로 내보내면 짝이 안 맞아 아무것도 못 받는다.
    const auto in_qos = rclcpp::SensorDataQoS();
    const auto out_qos = rclcpp::QoS(rclcpp::KeepLast(2)).reliable();
    depth_ = std::make_unique<SplitStream<sensor_msgs::msg::Image>>(
      this, "깊이(켬)", in_ns + "/depth/image_rect_raw", in_ns + "/depth/metadata", out_ns + "/depth/image_rect_raw", true, on_mode,
      in_qos, out_qos, max_wait_s);
    ir1_ = std::make_unique<SplitStream<sensor_msgs::msg::Image>>(
      this, "IR1(끔)", in_ns + "/infra1/image_rect_raw", in_ns + "/infra1/metadata", out_ns + "/infra1/image_rect_raw", false, on_mode,
      in_qos, out_qos, max_wait_s);
    ir2_ = std::make_unique<SplitStream<sensor_msgs::msg::Image>>(
      this, "IR2(끔)", in_ns + "/infra2/image_rect_raw", in_ns + "/infra2/metadata", out_ns + "/infra2/image_rect_raw", false, on_mode,
      in_qos, out_qos, max_wait_s);
    if (split_points) {
      // 점군은 깊이 프레임에서 만들어지므로 깊이 메타데이터로 판정(Isaac 판과 같은 짝)
      pts_ = std::make_unique<SplitStream<sensor_msgs::msg::PointCloud2>>(
        this, "점군(켬)", in_ns + "/depth/color/points", in_ns + "/depth/metadata", out_ns + "/depth/color/points", true, on_mode,
        in_qos, out_qos, max_wait_s);
    }
    timer_ = create_wall_timer(std::chrono::seconds(10), [this]() {
        RCLCPP_INFO(get_logger(), "10 s: %s | %s | %s%s%s", depth_->statsLine().c_str(), ir1_->statsLine().c_str(),
          ir2_->statsLine().c_str(), pts_ ? " | " : "", pts_ ? pts_->statsLine().c_str() : "");
      });
  }

private:
  std::unique_ptr<SplitStream<sensor_msgs::msg::Image>> depth_, ir1_, ir2_;
  std::unique_ptr<SplitStream<sensor_msgs::msg::PointCloud2>> pts_;
  rclcpp::TimerBase::SharedPtr timer_;
};

}  // namespace rover_bringup

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<rover_bringup::EmitterSplitter>());
  rclcpp::shutdown();
  return 0;
}
