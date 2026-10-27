#!/bin/bash
# 10-27 §10 f2st1 prep(10-26 prep_smac_1026.sh + tolerance 확인) — 운용 기본(prep_patrol: vslam on · 프로젝터 끔 · SHM) + 재계획 0.01 + planner:=smac(Smac Hybrid RS → 실패 시 NavFn). 로버 안 움직임
NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "prep_patrol:\|PREP_OK\|PREP_FAIL\|불합격\|★\|위치 추정 검사\|wheel_odom\|nvblox_up" | tail -8
source /opt/ros/humble/setup.bash
echo "BT 사본: PlanSmacOrNavFn $(grep -c 'PlanSmacOrNavFn' /tmp/nav_to_pose_active.xml 2>/dev/null) · RateController $(grep -ao 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml) · step $(grep -c 'step="0.03"' /tmp/nav_to_pose_active.xml)"
echo "bt_navigator xml = $(timeout 8 ros2 param get /bt_navigator default_nav_to_pose_bt_xml 2>&1 | tail -1)"
for p in tolerance motion_model_for_search cost_penalty analytic_expansion_max_length max_planning_time cache_obstacle_heuristic; do echo "SmacHybrid.$p = $(timeout 8 ros2 param get /planner_server SmacHybrid.$p 2>&1 | tail -1)"; done
echo "visual_preset = $(timeout 8 ros2 param get /camera/camera depth_module.visual_preset 2>&1 | tail -1) · odom1 = $(timeout 8 ros2 param get /ekf_filter_node odom1 2>&1 | tail -1)"
echo "MPPI PathAlign = $(timeout 8 ros2 param get /controller_server FollowPathMPPI.PathAlignCritic.cost_weight 2>&1 | tail -1) · PathFollow = $(timeout 8 ros2 param get /controller_server FollowPathMPPI.PathFollowCritic.cost_weight 2>&1 | tail -1)"
