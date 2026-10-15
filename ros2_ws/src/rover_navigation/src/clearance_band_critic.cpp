// ClearanceBandCritic — MPPI 크리틱: 차체(패딩 포함 풋프린트) ↔ 치명 칸 중심의 정확 거리가 band 보다 작은 궤적 점에 벌점.
// (2026-10-15 §29, 근거 Docs/debug_log/2026-10-15/SUMMARY.md §28)
//
// 왜: 오늘 실패 3 건은 MPPI 가 상자 옆 정확 여유 2.7~4.4 cm 까지 서서히 붙은 뒤, Nav2 칸 검사(꼭짓점 칸 내림 + Bresenham)가
//     같은 여유에서도 위상에 따라 치명 칸을 '밟음'으로 뒤집혀 서 있는 자세부터 충돌 → 모든 궤적 · 후진 실패였다.
//     CostCritic 은 중심 비용으로만 점수를 매기고 풋프린트 비용은 충돌(LETHAL) 판정에만 쓴다 — 풋프린트 253(내접)은 치명 칸 17.5 cm 안이면
//     늘 나오므로 '99 에 벌점'은 띠가 너무 넓다(f2v4 여유 17.4 cm 에서 이미 99). 그래서 정확 거리로 띠(기본 6 cm)만 벌한다.
// 동작: 각 궤적의 점(trajectory_point_step 간격)에서 중심 비용이 0 이면 건너뜀(로컬 팽창 0.40 m ≥ 외접 0.32 + 띠 0.06),
//       아니면 (외접 반지름 + 띠) 안의 치명 칸(254)까지 직사각 풋프린트 정확 거리 d 의 최소를 구함(치명 칸 목록은 주기마다 한 번, §29.3).
//       d < band 면 (band − d)/band 를 더함(겹침 d = 0 은 1 — 충돌 자체는 CostCritic 이 처리). 점수 = weight × 합 / 평가 점 수 상한(traj_len/step).
// 치명 칸은 벌만 받고 막지 않는다 — 좁은 곳에서 모든 궤적이 띠 안이면 벌점이 비슷해져 경로 추종이 결정(지나감).
#include <algorithm>
#include <chrono>
#include <cmath>
#include <string>
#include <vector>

#include "nav2_costmap_2d/cost_values.hpp"
#include "nav2_mppi_controller/critic_function.hpp"

namespace rover_navigation
{

class ClearanceBandCritic : public mppi::critics::CriticFunction
{
public:
  void initialize() override
  {
    auto getParam = parameters_handler_->getParamGetter(name_);
    getParam(weight_, "cost_weight", 20.0f);
    getParam(power_, "cost_power", 1);
    getParam(band_, "band", 0.06f);
    getParam(step_, "trajectory_point_step", 2);
    if (step_ < 1) {step_ = 1;}
    RCLCPP_INFO(
      logger_, "ClearanceBandCritic: 띠 %.3f m · 가중 %.1f · 점 간격 %d", band_, weight_, step_);
  }

  void score(mppi::CriticData & data) override
  {
    if (!enabled_) {return;}
    // 풋프린트(패딩 포함, 몸체 좌표) → 축 정렬 직사각형으로 본다(우리 풋프린트는 직사각형)
    const auto fp = costmap_ros_->getRobotFootprint();
    if (fp.empty()) {return;}
    float xmin = 1e9f, xmax = -1e9f, ymin = 1e9f, ymax = -1e9f, rmax = 0.0f;
    for (const auto & p : fp) {
      xmin = std::min(xmin, static_cast<float>(p.x)); xmax = std::max(xmax, static_cast<float>(p.x));
      ymin = std::min(ymin, static_cast<float>(p.y)); ymax = std::max(ymax, static_cast<float>(p.y));
      rmax = std::max(rmax, static_cast<float>(std::hypot(p.x, p.y)));
    }
    const auto t0 = std::chrono::steady_clock::now();
    const float res = static_cast<float>(costmap_->getResolution());
    const float ox = static_cast<float>(costmap_->getOriginX()), oy = static_cast<float>(costmap_->getOriginY());
    const int sx = static_cast<int>(costmap_->getSizeInCellsX()), sy = static_cast<int>(costmap_->getSizeInCellsY());
    const unsigned char * grid = costmap_->getCharMap();
    const float reach = rmax + band_, reach2 = reach * reach;

    const auto & tr = data.trajectories;
    const size_t n = tr.x.shape(0), len = tr.x.shape(1);
    // §29.3: 주기마다 한 번, 모든 궤적 점의 범위 + reach 안의 치명 칸 중심만 목록으로(칸 289 개를 점마다 훑던 첫 판이 제어 주기 놓침 167 회/206 s)
    float txmin = 1e9f, txmax = -1e9f, tymin = 1e9f, tymax = -1e9f;
    for (size_t i = 0; i < n; ++i) {
      for (size_t j = 0; j < len; j += step_) {
        txmin = std::min(txmin, tr.x(i, j)); txmax = std::max(txmax, tr.x(i, j));
        tymin = std::min(tymin, tr.y(i, j)); tymax = std::max(tymax, tr.y(i, j));
      }
    }
    const int mx0 = std::max(0, static_cast<int>(std::floor((txmin - reach - ox) / res)));
    const int mx1 = std::min(sx - 1, static_cast<int>(std::floor((txmax + reach - ox) / res)));
    const int my0 = std::max(0, static_cast<int>(std::floor((tymin - reach - oy) / res)));
    const int my1 = std::min(sy - 1, static_cast<int>(std::floor((tymax + reach - oy) / res)));
    // 치명 칸을 한 변 reach 인 통에 나눠 담음 → 점마다 이웃 3×3 통만 봄(벽이 많으면 목록이 수백 칸)
    const float bx0 = ox + mx0 * res, by0 = oy + my0 * res;
    const int nbx = std::max(1, static_cast<int>(std::ceil((mx1 - mx0 + 1) * res / reach)));
    const int nby = std::max(1, static_cast<int>(std::ceil((my1 - my0 + 1) * res / reach)));
    if (static_cast<int>(bins_.size()) < nbx * nby) {bins_.resize(nbx * nby);}
    for (int b = 0; b < nbx * nby; ++b) {bins_[b].clear();}
    lx_.clear(); ly_.clear();
    for (int my = my0; my <= my1; ++my) {
      for (int mx = mx0; mx <= mx1; ++mx) {
        if (grid[my * sx + mx] == nav2_costmap_2d::LETHAL_OBSTACLE) {
          const float wx = ox + (mx + 0.5f) * res, wy = oy + (my + 0.5f) * res;
          const int ix = std::min(nbx - 1, static_cast<int>((wx - bx0) / reach)), iy = std::min(nby - 1, static_cast<int>((wy - by0) / reach));
          bins_[iy * nbx + ix].push_back(static_cast<int>(lx_.size()));
          lx_.push_back(wx); ly_.push_back(wy);
        }
      }
    }
    const size_t nl = lx_.size();
    size_t evaluated = 0;
    if (nl > 0) {
      const float npts = static_cast<float>((len + step_ - 1) / step_);
      for (size_t i = 0; i < n; ++i) {
        float acc = 0.0f;
        for (size_t j = 0; j < len; j += step_) {
          const float x = tr.x(i, j), y = tr.y(i, j);
          const int cx = static_cast<int>(std::floor((x - ox) / res)), cy = static_cast<int>(std::floor((y - oy) / res));
          if (cx < 0 || cy < 0 || cx >= sx || cy >= sy) {continue;}
          if (grid[cy * sx + cx] == nav2_costmap_2d::FREE_SPACE) {continue;}   // 팽창 0.40 ≥ reach 0.38 → 띠 안 치명 칸 없음
          ++evaluated;
          const float c = std::cos(tr.yaws(i, j)), s = std::sin(tr.yaws(i, j));
          float dmin = band_;
          const int pbx = static_cast<int>(std::floor((x - bx0) / reach)), pby = static_cast<int>(std::floor((y - by0) / reach));
          for (int qy = std::max(0, pby - 1); qy <= std::min(nby - 1, pby + 1) && dmin > 0.0f; ++qy) {
            for (int qx = std::max(0, pbx - 1); qx <= std::min(nbx - 1, pbx + 1) && dmin > 0.0f; ++qx) {
              for (const int k : bins_[qy * nbx + qx]) {
                const float wx = lx_[k] - x, wy = ly_[k] - y;
                if (wx * wx + wy * wy > reach2) {continue;}
                const float bx = c * wx + s * wy, by = -s * wx + c * wy;   // 몸체 좌표
                const float ddx = std::max(std::max(xmin - bx, bx - xmax), 0.0f);
                const float ddy = std::max(std::max(ymin - by, by - ymax), 0.0f);
                const float d = std::sqrt(ddx * ddx + ddy * ddy);
                if (d < dmin) {dmin = d; if (dmin <= 0.0f) {break;}}
              }
            }
          }
          if (dmin < band_) {acc += (band_ - dmin) / band_;}
        }
        if (acc > 0.0f) {data.costs(i) += std::pow(weight_ * acc / npts, power_);}
      }
    }
    // 계산 시간 기록(§29.3 근거용): 100 주기마다 평균 · 최대 ms, 치명 칸 수, 평가한 점 수
    const double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
    t_sum_ += ms; t_max_ = std::max(t_max_, ms); l_max_ = std::max(l_max_, nl); e_max_ = std::max(e_max_, evaluated);
    if (++calls_ % 100 == 0) {
      RCLCPP_INFO(
        logger_, "ClearanceBandCritic 시간: 평균 %.2f ms · 최대 %.2f ms · 치명 칸 최대 %zu · 평가 점 최대 %zu (100 주기)",
        t_sum_ / 100.0, t_max_, l_max_, e_max_);
      t_sum_ = 0.0; t_max_ = 0.0; l_max_ = 0; e_max_ = 0;
    }
  }

protected:
  float weight_{20.0f};
  int power_{1};
  float band_{0.06f};
  int step_{2};
  std::vector<float> lx_, ly_;
  std::vector<std::vector<int>> bins_;
  double t_sum_{0.0}, t_max_{0.0};
  size_t l_max_{0}, e_max_{0}, calls_{0};
};

}  // namespace rover_navigation

#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(rover_navigation::ClearanceBandCritic, mppi::critics::CriticFunction)
