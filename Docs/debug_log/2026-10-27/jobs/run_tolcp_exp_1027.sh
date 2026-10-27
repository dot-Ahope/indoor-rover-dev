#!/bin/bash
# run_tolcp_exp_1027 — (PC) §7 16:11:56.85 남행 한 순간을 진단 빌드(~/smac_dbg_ws, 탐색 기록)로 V1(tol 0.35 · cp 3.0) · V3(tol 0.25 · cp 1.5) 재질의. 변형마다 프로세스 따로. 로버 안 움직임(도메인 42).
D=/f/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-27; T=/f/6_Indoor_Rover/Rover/Docs/tools/plan_offline; O=$D/outputs/tolcp_exp
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
for v in V1:30 V3:15; do
  IFS=: read n cp <<< "$v"; P=Smac_R10_C${cp}_A10_RS
  cp $D/outputs/tolcp/planner_$n.yaml $O/planner_$n.yaml
  bash $T/up_bundle.sh $O/planner_$n.yaml $O/scenes_115653.npz $S/up_planoff_tcx.sh
  MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=600 JX_WHY='10-27 §7 탐색 기록 $n(진단 빌드, 도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_tcx.sh GridBased,$P /home/jetson/smac_dbg_ws 1" > $O/run_$n.txt 2>&1
  sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' $O/run_$n.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/result_$n.npz
  sed -n '/EXP_B64_BEGIN/,/EXP_B64_END/p' $O/run_$n.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/exp_$n.tgz
  sed -i '/_B64_BEGIN/,/_B64_END/c\(base64 묶음 생략 — result_'$n'.npz · exp_'$n'.tgz)' $O/run_$n.txt
  echo "== $n · $(grep -a '적재된' $O/run_$n.txt | grep -o 'smac_dbg_ws' | head -1) · $(grep -a "$P " $O/run_$n.txt | grep -av WARN | head -1 | cut -c1-90) · $(grep -a '탐색 기록' $O/run_$n.txt)"
done
