#!/bin/bash
# agent -v6 로그에서 '수신된 프레임 길이' 분포를 낸다.
#   odom(~740B) 길이대가 아예 없으면 → 큰 프레임이 구조적으로 못 들어옴
#   있는데 드물면 → 확률적 손실
CLEAN=/tmp/v6_clean2.log
sed -E 's/\x1b\[[0-9;]*m//g' /tmp/agent_v6.log > $CLEAN
echo "총 줄수: $(wc -l < $CLEAN)"
echo ""
echo "=== recv_message (보드->agent) 길이 분포 ==="
grep -a "recv_message" $CLEAN | grep -aoE "len: [0-9]+" | awk '{print $2}' | sort -n | uniq -c | sort -rn | head -20 | sed 's/^/  건수 길이: /'
echo ""
echo "=== DataWriter write (agent->DDS) 길이 분포 ==="
grep -a "DataWriter.cpp" $CLEAN | grep -aoE "len: [0-9]+" | awk '{print $2}' | sort -n | uniq -c | sort -rn | head -20 | sed 's/^/  건수 길이: /'
echo ""
echo "=== 최대 수신 길이 ==="
grep -a "recv_message" $CLEAN | grep -aoE "len: [0-9]+" | awk '{print $2}' | sort -n | tail -3 | sed 's/^/  /'
echo ""
echo "=== send_message (agent->보드) 길이 분포 ==="
grep -a "send_message" $CLEAN | grep -aoE "len: [0-9]+" | awk '{print $2}' | sort -n | uniq -c | sort -rn | head -5 | sed 's/^/  건수 길이: /'
echo ""
echo "=== 로그에 등장하는 모든 함수명 ==="
grep -aoE "\| [a-z_]+ +\|" $CLEAN | tr -d '| ' | sort | uniq -c | sort -rn | head -12 | sed 's/^/  /'
