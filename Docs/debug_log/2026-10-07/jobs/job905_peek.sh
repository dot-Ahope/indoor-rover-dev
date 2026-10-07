#!/bin/bash
# 10-07: prep 진행 확인(읽기만)
tail -40 /tmp/live/current.log | cut -c1-200
echo "프로세스: ekf $(pgrep -fc '[e]kf_node') · 게이트 $(pgrep -fc '[r]f2o_gate') · rf2o $(pgrep -fc '[r]f2o_laser') · slam $(pgrep -fc '[s]lam_toolbox') · nav2 $(pgrep -fc '[c]ontroller_server') · prep $(pgrep -fc '[j]ob780')"
echo "uptime: $(uptime -p) · 부팅 $(uptime -s)"
tail -5 /var/log/wifi_mon/*.log 2>/dev/null | tail -8 | cut -c1-160
