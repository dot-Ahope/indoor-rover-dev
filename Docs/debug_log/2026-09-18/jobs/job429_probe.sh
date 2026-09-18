#!/bin/bash
# A안 사전 점검 (2026-09-18): 디스크, wpa_supplicant 실행 인자, wpa_cli 모니터가 debug 메시지를 받는지 20 s 시험, 단일 채널 스캔 가능 여부.
# sudo 사용(사용자 A안 승인). 설정 변경 없음. 인자: 없음. 비밀번호는 환경변수 SPW 로 받는다.
S() { echo "$SPW" | sudo -S -p '' "$@"; }
echo "== 디스크"; df -h / /var/log | sed 's/^/  /'
echo "== syslog 크기 $(ls -la /var/log/syslog | awk '{print $5}') / logrotate: $(ls /etc/logrotate.d/ 2>/dev/null | tr '\n' ' ')"
systemctl is-active logrotate.timer cron 2>&1 | tr '\n' ' ' | sed 's/^/  logrotate.timer, cron: /'; echo
echo "== wpa_supplicant 실행 인자"; ps -o pid,args -C wpa_supplicant | sed 's/^/  /'
echo "== sudo 확인"; S true && echo "  sudo OK"
echo "== wpa_cli 상태(root)"; S wpa_cli -i wlP1p1s0 status 2>&1 | grep -avE 'passphrase|psk|pmk' | sed 's/^/  /'
echo "== 모니터 시험 20 s (level 2 = debug), 5 s 뒤 wpa_cli scan 1 회"
( (echo "level 2"; sleep 20) | S timeout 22 wpa_cli -i wlP1p1s0 2>&1 ) > /tmp/wpamon_test.txt &
sleep 5; S wpa_cli -i wlP1p1s0 scan >/dev/null 2>&1; wait
echo "  받은 줄 $(wc -l < /tmp/wpamon_test.txt), 앞 25 줄:"; grep -avE 'passphrase|psk=' /tmp/wpamon_test.txt | head -25 | cut -c1-160 | sed 's/^/    /'
echo "  <수준> 분포: $(grep -aoE '^<[0-9]>' /tmp/wpamon_test.txt | sort | uniq -c | tr '\n' ' ')"
echo "== 단일 채널 스캔(5180) 소요 시간·AP 폭"
t0=$(date +%s%N); S iw dev wlP1p1s0 scan freq 5180 > /tmp/scan5180.txt 2>&1; t1=$(date +%s%N)
echo "  $(( (t1-t0)/1000000 )) ms, 결과 BSS $(grep -c '^BSS ' /tmp/scan5180.txt) 개"
awk '/^BSS b0:38:6c:37:1b:4c/{p=1} /^BSS / && !/b0:38:6c:37:1b:4c/{p=0} p' /tmp/scan5180.txt | grep -aE 'BSS |signal|last seen|channel width|center freq|secondary channel offset|Channel Switch|Country' | sed 's/^/    /'
rm -f /tmp/wpamon_test.txt /tmp/scan5180.txt
