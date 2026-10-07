#!/bin/bash
# 10-07 §6: 실행 중 노드가 새 설정을 쓰는가(읽기만)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "게이트 파라미터:"; timeout 10 ros2 param list /rf2o_gate 2>&1 | tr '\n' ' '; echo
timeout 8 ros2 param get /rf2o_gate v_ref 2>&1 | tail -2
pgrep -fa "rf2o_gate" | grep -v pgrep | cut -c1-200
ls -la ~/ros2_ws/install/rover_bringup/lib/rover_bringup/rf2o_gate.py; grep -c v_ref ~/ros2_ws/install/rover_bringup/lib/rover_bringup/rf2o_gate.py
echo "컨트롤러 params 파일:"; pgrep -fa controller_server | grep -v pgrep | grep -o "params-file [^ ]*" | head -3
for f in $(pgrep -fa controller_server | grep -v pgrep | grep -o "params-file [^ ]*" | awk '{print $2}'); do echo "$f: $(grep -n 'transform_tolerance' $f | head -6 | tr '\n' ' ')"; done
timeout 10 ros2 param list /controller_server 2>&1 | grep -i "tolerance" | head
