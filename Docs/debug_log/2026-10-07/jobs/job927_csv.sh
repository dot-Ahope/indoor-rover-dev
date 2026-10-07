#!/bin/bash
# 10-07 §8.4: 단계 4 csv 최근 값(읽기만) — 2 s 간격으로 줄임
awk -F, '$2=="watch"{k=int($1/2); if(k!=p){printf "%s %s ②%s ①%s 그밖%s\n", strftime("%T",$1), $2, $6, $7, $8; p=k}}' /tmp/box_step.csv | tail -45
