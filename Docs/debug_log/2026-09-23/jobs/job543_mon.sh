#!/bin/bash
grep -aE "^2026-09-23 (11:5[0-9]|12:0[0-7])" /var/log/wifi_mon/mon.log | grep -av BEACON | cut -c1-175
echo "## tx/rx 통계 줄 수(15 s 간격이면 11:50~12:07 = 68)"
grep -acE "^2026-09-23 (11:5[0-9]|12:0[0-7]).*LINK" /var/log/wifi_mon/mon.log
