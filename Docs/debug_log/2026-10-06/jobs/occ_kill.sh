#!/bin/bash
# 합성 가림 재생 정리 — PID 로만(이름 pkill 은 자기 자신·라이브 스택을 죽일 수 있음)
P=$(ps -eo pid,args | grep -aE "[o]cc_run.sh|[o]cc_rec.py|[o]cc_scan.py|[b]ag play /tmp/bag_step1|[e]kf.launch.py rf2o:=true use_sim_time:=true" | awk '{print $1}')
for p in $P; do kill -INT -- -$(ps -o pgid= -p $p | tr -d ' ') 2>/dev/null; kill -INT $p 2>/dev/null; done; sleep 4
P=$(ps -eo pid,args | grep -aE "[o]cc_run.sh|[o]cc_rec.py|[o]cc_scan.py|[b]ag play /tmp/bag_step1|[e]kf.launch.py rf2o:=true use_sim_time:=true" | awk '{print $1}'); for p in $P; do kill -9 $p; done
echo "남은 시험 프로세스 $(ps -eo args | grep -acE "[o]cc_|[b]ag play /tmp/bag_step1|[u]se_sim_time:=true") · 라이브 ekf $(ps aux | grep -c "[e]kf_node") · 게이트 $(ps aux | grep -c "[r]f2o_gate")"
