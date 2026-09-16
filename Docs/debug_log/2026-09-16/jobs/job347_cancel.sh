#!/bin/bash
echo "=== nav2.log 1789541800~1812 (취소 출처) ==="
grep -aE "\[17895418(0[0-9]|1[0-2])\." /tmp/nav2.log | grep -avE "Passing new path|Aborting handle" | head -12 | cut -c1-190
echo "=== bt_navigator 전체(goal 이후) ==="; grep -a "bt_navigator\]" /tmp/nav2.log | awk -F'[][]' '{split($4,a,"."); if (a[1]+0>=1789541789) print}' | head -6 | cut -c1-190
