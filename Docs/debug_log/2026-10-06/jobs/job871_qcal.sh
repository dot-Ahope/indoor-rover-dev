#!/bin/bash
# 10-06 §12 G3 보정: q 를 기록만(log) — 깨끗(0 %)·정적 몸 50 %·움직이는 C·E·다리 A, 도메인 71~75
export GQ=log
run() { bash /tmp/occ_run.sh $1 $3 /tmp/qcal_$2.npz $4 $5 "$6" > /tmp/qcal_run_$1.txt 2>&1; }
run 71 clean 0.0 20.0 0.6 "" &
run 72 static50 0.5 20.0 0.6 "" &
run 73 A_walk08 0.0 0.0 0.8 "-p legs:=true -p amp:=1.0 -p period:=12.0 -p move_deg:=90.0" &
run 74 C_sway 0.5 20.0 0.6 "-p amp:=0.15 -p period:=4.0 -p move_deg:=110.0" &
run 75 E_fast 0.5 20.0 0.5 "-p amp:=0.3 -p period:=3.0 -p move_deg:=110.0" &
wait; ls -la /tmp/qcal_*_gate.csv
