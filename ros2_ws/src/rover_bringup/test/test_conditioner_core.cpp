// conditioner_core 단위 테스트 — Python 판(scripts/sensor_conditioner.py) 동작과 같은지 핵심 경로만 확인.
#include <gtest/gtest.h>

#include "rover_bringup/conditioner_core.hpp"

using rover_bringup::ConditionerParams;
using rover_bringup::GyroBias;
using rover_bringup::Vec3;

TEST(GyroBias, CalibratesMeanWhenStationary)
{
  ConditionerParams p; p.calib_samples = 4;
  GyroBias g(p);
  EXPECT_EQ(g.addCalibSample({0.01, -0.02, 0.0}), GyroBias::CalibResult::kCollecting);
  g.addCalibSample({0.01, -0.02, 0.0});
  g.addCalibSample({0.01, -0.02, 0.0});
  EXPECT_EQ(g.addCalibSample({0.01, -0.02, 0.0}), GyroBias::CalibResult::kCalibrated);   // 4 번째가 완료시킴
  EXPECT_TRUE(g.ready());
  EXPECT_DOUBLE_EQ(g.bias()[0], 0.01);
  EXPECT_DOUBLE_EQ(g.bias()[1], -0.02);
}

TEST(GyroBias, ZeroBiasWhenNotStationary)
{
  ConditionerParams p; p.calib_samples = 2;
  GyroBias g(p);
  g.addCalibSample({0.0, 0.0, 0.0});
  EXPECT_EQ(g.addCalibSample({0.1, 0.0, 0.0}), GyroBias::CalibResult::kNotStationary);   // std 0.05 > 0.015
  EXPECT_DOUBLE_EQ(g.bias()[0], 0.0);
}

TEST(GyroBias, ZuptStepIsClampedAndNeedsStationary)
{
  ConditionerParams p; p.calib_samples = 1; p.zupt_win = 3;
  GyroBias g(p);
  g.addCalibSample({0.0, 0.0, 0.0});
  double oy; Vec3 obs;
  // 정지 아님 → 갱신 없음
  for (int i = 0; i < 5; ++i) {EXPECT_FALSE(g.zuptUpdate({0.0, 0.01, 0.0}, oy, obs));}
  g.setStationary(true);
  EXPECT_FALSE(g.zuptUpdate({0.0, 0.01, 0.0}, oy, obs));
  EXPECT_FALSE(g.zuptUpdate({0.0, 0.01, 0.0}, oy, obs));
  EXPECT_TRUE(g.zuptUpdate({0.0, 0.01, 0.0}, oy, obs));
  // (0.01 − 0) × 0.1 = 0.001 → 상한 0.0005 로 클램프
  EXPECT_DOUBLE_EQ(g.bias()[1], 0.0005);
  EXPECT_EQ(g.zuptCount(), 1);
}

TEST(GyroBias, ZuptRejectsShaking)
{
  ConditionerParams p; p.calib_samples = 1; p.zupt_win = 2;
  GyroBias g(p);
  g.addCalibSample({0.0, 0.0, 0.0});
  g.setStationary(true);
  double oy; Vec3 obs;
  g.zuptUpdate({0.0, 0.0, 0.0}, oy, obs);
  EXPECT_FALSE(g.zuptUpdate({0.0, 0.05, 0.0}, oy, obs));   // std 0.025 ≥ 0.010
  EXPECT_DOUBLE_EQ(g.bias()[1], 0.0);
}

TEST(Wheel, StationaryAndSlipFactor)
{
  ConditionerParams p;
  EXPECT_TRUE(rover_bringup::wheelStationary(p, 0.004, -0.004));
  EXPECT_FALSE(rover_bringup::wheelStationary(p, 0.005, 0.0));
  EXPECT_DOUBLE_EQ(rover_bringup::yawSlipFactor(p, 0.3), 1.0);
  const auto c = rover_bringup::wheelTwistCov(p, 0.0, 0.3);
  EXPECT_DOUBLE_EQ(c.vy, 0.01 * 0.01);
}
