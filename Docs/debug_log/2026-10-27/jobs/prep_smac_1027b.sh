#!/bin/bash
# 10-27 §24 prep — prep_smac_1027.sh 에서 `ros2 param get` 약 11 번을 뺀 판(같은 값은 chk_prep.py 가 한 노드로 조회해 출력). 구성은 그대로:
#   운용 기본(prep_patrol: vslam on · 프로젝터 끔 · SHM) + 재계획 0.01 + planner:=smac. 로버 안 움직임
NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "prep_patrol:\|PREP_OK\|PREP_FAIL\|불합격\|★\|위치 추정 검사\|wheel_odom\|nvblox_up\|server:\|camera:\|filter_node:\|slam_toolbox:\|navigator:\|costmap:\|monitor:\|⏱" | tail -24
echo "BT 사본: PlanSmacOrNavFn $(grep -c 'PlanSmacOrNavFn' /tmp/nav_to_pose_active.xml 2>/dev/null) · $(grep -ao 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml) · step $(grep -c 'step="0.03"' /tmp/nav_to_pose_active.xml)"
