#!/bin/bash
cat /tmp/j539.txt
echo "==== 트레이스(상태 변화만)"
awk '{k=$2" "$5; if (k!=p) {print; p=k}}' /tmp/j540_trace.txt | tail -15
echo "줄 수 $(wc -l < /tmp/j540_trace.txt), gw=X 횟수 $(grep -c 'gw=X' /tmp/j540_trace.txt)"
