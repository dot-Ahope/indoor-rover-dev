#!/bin/bash
# run_goal_yaw_1026 — (PC) §20 목표 방향 시험: 실주행 SmacHybrid 값(시간 상한 2.0 s) 하나 + NavFn 을 오프라인 planner_server(도메인 42)에 올려 장면 78 개 질의. 로버 안 움직임.
#   입력 outputs/planner_offline/goal_yaw/scenes_goal_yaw.npz(prep_scenes + jobs/scenes_goal_yaw_1026.json). 출력 같은 폴더 run_goal_yaw.txt · result_goal_yaw.npz
D=/f/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-26; T=/f/6_Indoor_Rover/Rover/Docs/tools/plan_offline; O=$D/outputs/planner_offline/goal_yaw
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
V=Smac_R10_C30_A10_RS
SMAC_MAXT=2.0 python -X utf8 $T/gen_yaml.py $O/planner_goal_yaw.yaml 0.01 $V > /dev/null
grep -n "max_planning_time\|motion_model\|cost_penalty\|analytic_expansion_max_length\|cache_obstacle" $O/planner_goal_yaw.yaml
bash $T/up_bundle.sh $O/planner_goal_yaw.yaml $O/scenes_goal_yaw.npz $S/up_planoff_gy.sh
MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=1800 JX_WHY='§20 목표 방향 시험: Smac 실주행 값 + NavFn, 장면 78(도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_gy.sh GridBased,$V" > $O/run_goal_yaw.txt 2>&1
sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' $O/run_goal_yaw.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/result_goal_yaw.npz
echo "끝: 재구성 일치 1.0000 $(grep -ac '재구성 일치 1.0000' $O/run_goal_yaw.txt)/78 · Smac 성공 $(grep -a "$V" $O/run_goal_yaw.txt | grep -c '성공')"
