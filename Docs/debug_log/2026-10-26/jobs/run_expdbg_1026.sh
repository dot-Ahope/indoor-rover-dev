#!/bin/bash
# run_expdbg_1026 — (PC) §22 Smac 탐색 기록: 진단 빌드(~/smac_dbg_ws) 오버레이로 f2sa3 통로 6 순간(목표 방향 원래 그대로)을 재질의하고 방문 노드 기록을 받아 옴. 로버 안 움직임(도메인 42).
D=/f/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-26; T=/f/6_Indoor_Rover/Rover/Docs/tools/plan_offline; O=$D/outputs/planner_offline/goal_yaw
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
V=Smac_R10_C30_A10_RS
bash $T/up_bundle.sh $O/planner_goal_yaw.yaml $O/scenes_expdbg.npz $S/up_planoff_exp.sh
MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=600 JX_WHY='§22 Smac 탐색 기록 재질의 6 순간(진단 빌드, 도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_exp.sh GridBased,$V /home/jetson/smac_dbg_ws 1" > $O/run_expdbg.txt 2>&1
sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' $O/run_expdbg.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/result_expdbg.npz
rm -rf $O/exp; sed -n '/EXP_B64_BEGIN/,/EXP_B64_END/p' $O/run_expdbg.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d | tar xzf - -C $O
echo "끝: $(grep -a '적재된\|오버레이\|탐색 기록' $O/run_expdbg.txt | tr '\n' ' ') · exp $(ls $O/exp | wc -l) 개"
