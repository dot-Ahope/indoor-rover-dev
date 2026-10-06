#!/bin/bash
# 10-06 §11: 움직이는 몸 5 조건(도메인 61~65) — 인자: 이름 coverage center_deg rho '추가 매개'
run() { bash /tmp/occ_run.sh $1 $3 /tmp/occm_$2.npz $4 $5 "$6" > /tmp/occm_run_$1.txt 2>&1; }
run 61 A_walk08 0.0 0.0 0.8 "-p legs:=true -p amp:=1.0 -p period:=12.0 -p move_deg:=90.0" &
run 62 B_walk05 0.0 0.0 0.5 "-p legs:=true -p amp:=0.6 -p period:=8.0 -p move_deg:=90.0" &
run 63 C_arc50_sway 0.5 20.0 0.6 "-p amp:=0.15 -p period:=4.0 -p move_deg:=110.0" &
run 64 D_arc30_inout 0.3 20.0 0.6 "-p amp:=0.2 -p period:=3.0 -p move_deg:=20.0" &
run 65 E_arc50_fast 0.5 20.0 0.5 "-p amp:=0.3 -p period:=3.0 -p move_deg:=110.0" &
wait; for d in 61 62 63 64 65; do echo "$d $(grep -a '게이트 통과' /tmp/occ_launch_$d.log | tail -1 | grep -oE '통과.*') | $(grep -a '가린 빔' /tmp/occ_scan_$d.log | tail -1 | grep -oE '가린.*') | 오류 $(grep -acE 'Traceback|Exception' /tmp/occ_scan_$d.log)"; done
