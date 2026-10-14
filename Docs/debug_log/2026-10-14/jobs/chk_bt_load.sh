#!/bin/bash
# (10-14 §14) 스택 재기동(prep) 뒤 bt_navigator 가 CopyPath 를 읽었는지·BT 오류가 없는지 확인 — 로버 안 움직임
I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config
echo "설치본: $(ls -la $I/nav2_params.yaml | cut -c1-12) $(readlink $I/nav2_params.yaml) · copy 플러그인 줄 $(grep -c rover_copy_path_bt_node $I/nav2_params.yaml) · BT CopyPath $(grep -c '<CopyPath' $I/nav_to_pose_no_spin.xml) · PreferForward $(grep -o 'PreferForwardCritic: {[^}]*cost_weight: [0-9.]*' $I/nav2_params.yaml | grep -o '[0-9.]*$')"
bash /tmp/prep_patrol.sh lite 15.0 > /tmp/prep_bt.txt 2>&1; grep -a "PREP_OK\|PREP_FAIL" /tmp/prep_bt.txt | tail -1
echo "--- nav2.log: bt_navigator 관련 오류·플러그인"
grep -a -i "bt_navigator" /tmp/nav2.log | grep -a -i "error\|fail\|exception\|could not\|copy\|plugin\|Activating\|Configuring" | head -12 | cut -c1-200
grep -a -i "CopyPath\|copy_path" /tmp/nav2.log | head -5 | cut -c1-200
