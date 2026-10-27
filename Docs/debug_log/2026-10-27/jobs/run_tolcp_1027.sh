#!/bin/bash
# run_tolcp_1027 — (PC) §5 허용치 · cost_penalty 재질의: 변형마다 오프라인 planner_server(설치판 .so, 도메인 42)를 따로 띄워 f2sa3 통로 6 순간 질의. 로버 안 움직임.
#   변형 = 이름:tol:cp — Smac 값은 실주행(RS · 해석 1.0 m · 시간 상한 2.0 s · 캐시 끔)에서 tol · cp 만 바꿈
D=/f/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-27; T=/f/6_Indoor_Rover/Rover/Docs/tools/plan_offline; O=$D/outputs/tolcp
SCN=$D/../2026-10-26/outputs/planner_offline/goal_yaw/scenes_expdbg.npz
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
for v in V0:0.25:30 V1:0.35:30 V2:0.50:30 V3:0.25:15 V4:0.35:15; do
  IFS=: read n tol cp <<< "$v"; P=Smac_R10_C${cp}_A10_RS
  SMAC_TOL=$tol SMAC_MAXT=2.0 python -X utf8 $T/gen_yaml.py $O/planner_$n.yaml 0.01 $P > /dev/null
  bash $T/up_bundle.sh $O/planner_$n.yaml $SCN $S/up_planoff_tolcp.sh
  MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=600 JX_WHY='10-27 §5 $n tol $tol cp $cp(도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_tolcp.sh GridBased,$P" > $O/run_$n.txt 2>&1
  sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' $O/run_$n.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/result_$n.npz
  sed -i '/_B64_BEGIN/,/_B64_END/c\(base64 묶음 생략 — result_'$n'.npz)' $O/run_$n.txt
  echo "== $n tol $tol cp $cp · $(grep -a '적재된' $O/run_$n.txt | grep -o '/opt/ros\|smac_dbg_ws\|smac_ws' | head -1) · 재구성 $(grep -ac '재구성 일치 1.0000' $O/run_$n.txt)/6 · Smac 성공 $(grep -a "$P" $O/run_$n.txt | grep -c '성공')"
done
