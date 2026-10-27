#!/bin/bash
# run_tt1_exp_1027 — (PC) §27 f2tt1 통로 세 순간(남행 15:57:41 · 북행 15:58:05.80 · 북행 재계획 15:58:11.40)을 진단 빌드(~/smac_dbg_ws, 탐색 기록)로 재질의.
#   설정 = §7 V1(tol 0.35 · cp 3.0 · 시간 상한 2.0 s = 실주행 값). 로버 안 움직임(도메인 42).
D=/f/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-27; T=/f/6_Indoor_Rover/Rover/Docs/tools/plan_offline; O=$D/outputs/tt1_exp
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
n=V1; P=Smac_R10_C30_A10_RS
cp $D/outputs/tolcp/planner_V1.yaml $O/planner_$n.yaml
bash $T/up_bundle.sh $O/planner_$n.yaml $O/scenes_tt1.npz $S/up_planoff_tt1.sh
MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=600 JX_WHY='10-27 §27 f2tt1 통로 탐색 기록(진단 빌드, 도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_tt1.sh GridBased,$P /home/jetson/smac_dbg_ws 1" > $O/run_$n.txt 2>&1
sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' $O/run_$n.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/result_$n.npz
sed -n '/EXP_B64_BEGIN/,/EXP_B64_END/p' $O/run_$n.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/exp_$n.tgz
sed -i '/_B64_BEGIN/,/_B64_END/c\(base64 묶음 생략 — result_'$n'.npz · exp_'$n'.tgz)' $O/run_$n.txt
grep -a "Smac\|GridBased\|탐색 기록\|적재" $O/run_$n.txt | grep -av WARN | head -12 | cut -c1-150
