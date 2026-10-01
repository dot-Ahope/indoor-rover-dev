#!/bin/bash
echo "preempt: $(grep -ac -i preempt /tmp/nav2.log) · is_path_valid 관련: $(grep -aci "path_valid\|isPathValid" /tmp/nav2.log)"
grep -ai "preempt\|path_valid" /tmp/nav2.log | tail -3 | cut -c1-200
grep -n "send_goal\|GoalUpdated\|preempt\|wyaw\|경로 끝" /tmp/job550_f0run.py | head -8
