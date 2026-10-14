#!/bin/bash
# (10-14 §18) f2t1 동안 30 s 칸별: 컨트롤러 주기 미달·좌표 변환 미래 요청 경고 수, PathBlocked/follow 중단 — 로버 안 움직임
A=$(date -d '15:20:50' +%s)
grep -a -o '\[[a-z_0-9.-]*\] \[[A-Z]*\] \[[0-9]*\.[0-9]*\] \[[a-z_0-9.]*\]: .*' /tmp/nav2.log | awk -v a=$A '{t=$3; gsub(/[\[\]]/,"",t); if (t+0>=a) {b=int((t-a)/30); if ($0 ~ /missed its desired rate/) m[b]++; if ($0 ~ /extrapolation into the future/) x[b]++; if ($0 ~ /follow_path\] \[ActionServer\] Aborting/) f[b]++; if ($0 ~ /Optimizer reset/) r[b]++; n[b]=1}} END {for (b=0;b<=22;b++) if (n[b]) printf "%s  주기미달 %3d  미래변환 %3d  주행중단 %2d  최적화초기화 %3d\n", strftime("%H:%M:%S", a+b*30), m[b], x[b], f[b], r[b]}'
