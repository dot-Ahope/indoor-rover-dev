#!/bin/bash
sleep 60; top -b -n2 -d10 | awk '/PID +USER/{f++} f==2 && $9+0>0 {s+=$9; if ($9>8) printf "%s=%s ", $12, $9} END {printf "\n정지 CPU 합 %.0f %%\n", s}'
