#!/bin/bash
echo "=== planner_server 관련 로그 전체 ==="
grep -aiE "planner_server|global_costmap|stvl|spatio|openvdb" /tmp/nav2.log | tail -30 | cut -c1-190
echo ""
echo "=== 마지막 40줄 ==="
tail -40 /tmp/nav2.log | cut -c1-180
