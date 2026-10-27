#!/bin/bash
# run_swap_1027 — (PC) §1 ③ 출발 ↔ 지도 바꿔 끼우기: 진단 빌드(~/smac_dbg_ws, 설치판과 같은 동작 · 탐색 기록)로 장면 16 개 질의. 로버 안 움직임(도메인 42).
#   입력 outputs/swap/scenes_swap.npz(prep_scenes + jobs/scenes_swap_1027.json), 설정 = 10-26 planner_goal_yaw.yaml(실주행 Smac 값, 시간 상한 2.0 s)
D=/f/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-27; T=/f/6_Indoor_Rover/Rover/Docs/tools/plan_offline; O=$D/outputs/swap
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
V=Smac_R10_C30_A10_RS
cp $D/../2026-10-26/outputs/planner_offline/goal_yaw/planner_goal_yaw.yaml $O/planner_swap.yaml
bash $T/up_bundle.sh $O/planner_swap.yaml $O/scenes_swap.npz $S/up_planoff_swap.sh
MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=900 JX_WHY='10-27 §1 출발 ↔ 지도 바꿔 끼우기 16 장면(진단 빌드, 도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_swap.sh GridBased,$V /home/jetson/smac_dbg_ws 1" > $O/run_swap.txt 2>&1
sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' $O/run_swap.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/result_swap.npz
sed -n '/EXP_B64_BEGIN/,/EXP_B64_END/p' $O/run_swap.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/exp_swap.tgz
sed -i '/_B64_BEGIN/,/_B64_END/c\(base64 묶음 생략 — result_swap.npz · exp_swap.tgz 로 따로 저장)' $O/run_swap.txt
echo "끝: $(grep -a '적재된\|탐색 기록' $O/run_swap.txt | tr '\n' ' ') · 재구성 1.0000 $(grep -ac '재구성 일치 1.0000' $O/run_swap.txt)/16"
