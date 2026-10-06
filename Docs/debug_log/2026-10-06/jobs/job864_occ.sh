#!/bin/bash
# 10-06 §10: 가림 0·0.15·0.3·0.5·0.7 를 도메인 51~55 에서 동시에(각자 /clock), bag_step1(2021 s)
i=51; for c in 0.0 0.15 0.3 0.5 0.7; do bash /tmp/occ_run.sh $i $c /tmp/occ_$c.npz > /tmp/occ_run_$i.txt 2>&1 & i=$((i+1)); done
wait; cat /tmp/occ_run_5*.txt | grep -a "도메인"
