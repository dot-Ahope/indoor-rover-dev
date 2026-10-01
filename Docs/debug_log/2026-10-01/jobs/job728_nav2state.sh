#!/bin/bash
# 10-01 §6: Nav2 lifecycle 상태·부하·EKF 확인(prep 에서 controller_server "?" — 조회 시간 초과인지 기동 실패인지)
for nd in /controller_server /planner_server /bt_navigator /behavior_server /velocity_smoother /smoother_server; do printf "  %-20s " $nd; timeout 8 ros2 lifecycle get $nd 2>&1 | tail -1; done
echo "  lifecycle_manager 로그: $(grep -a 'lifecycle_manager' /tmp/nav2.log | grep -aiE 'fail|active|Managed nodes' | tail -3)"
echo "  load $(cut -d' ' -f1-3 /proc/loadavg) | EKF 위반 $(grep -ac 'Failed to meet' /tmp/sensors.log) | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)"
