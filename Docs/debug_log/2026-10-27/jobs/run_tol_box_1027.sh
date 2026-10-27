#!/bin/bash
# run_tol_box_1027 — (PC) §8 허용 0.25 대 0.35 를 10-23 상자 · 통로 6 장면에서: 변형마다 오프라인 planner_server(설치판, 도메인 42) 따로. 로버 안 움직임.
D=/f/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-27; T=/f/6_Indoor_Rover/Rover/Docs/tools/plan_offline; O=$D/outputs/tol_box
SCN=$D/../2026-10-23/outputs/plan_offline/scenes_1023.npz; P=Smac_R10_C30_A10_RS
S=/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
for v in W0:0.25 W1:0.35; do
  IFS=: read n tol <<< "$v"
  SMAC_TOL=$tol SMAC_MAXT=2.0 python -X utf8 $T/gen_yaml.py $O/planner_$n.yaml 0.01 $P > /dev/null
  bash $T/up_bundle.sh $O/planner_$n.yaml $SCN $S/up_planoff_tolbox.sh
  MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash -c "JX_TIMEOUT=600 JX_WHY='10-27 §8 $n tol $tol 상자 · 통로 6 장면(도메인 42, 로버 안 움직임)' bash /mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad/run_jn.sh up_planoff_tolbox.sh GridBased,$P" > $O/run_$n.txt 2>&1
  sed -n '/RESULT_B64_BEGIN/,/RESULT_B64_END/p' $O/run_$n.txt | sed '1d;$d' | tr -d '\r\n ' | base64 -d > $O/result_$n.npz
  sed -i '/_B64_BEGIN/,/_B64_END/c\(base64 묶음 생략 — result_'$n'.npz)' $O/run_$n.txt
  python -X utf8 -I $T/anal_plan_compare.py $O/result_$n.npz $SCN $O/fig_$n 2>/dev/null > $O/anal_$n.txt
  echo "== $n tol $tol · $(grep -a '적재된' $O/run_$n.txt | grep -o '/opt/ros' | head -1) · 재구성 $(grep -ac '재구성 일치 1.0000' $O/run_$n.txt)/6"
done
