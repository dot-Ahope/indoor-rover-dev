#!/bin/bash
# robot_state_publisher 중복 정리: base.launch 의 자식이 아닌 것(벽 측정 때 description.launch 로 띄운 것)만 종료
for p in $(pgrep -f '[r]obot_state_publisher'); do
  pp=$(ps -o ppid= -p $p | tr -d ' '); pa=$(ps -o args= -p $pp)
  echo "rsp $p ← 부모 $pp: $(echo $pa | cut -c1-90)"
  if echo "$pa" | grep -q 'rover_description description.launch'; then kill -INT $pp; sleep 2; kill -9 $p 2>/dev/null; echo "  → 종료(벽 측정 잔여)"; fi
done
sleep 1; echo "남은 rsp: $(pgrep -fc '[r]obot_state_publisher')"
