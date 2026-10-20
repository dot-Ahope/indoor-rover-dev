#!/bin/bash
# UDP 수신 버퍼 오류 증가율 — 그림자 구성(정지) 그대로 20 s, cuVSLAM 만 잠시 멈춘 20 s 비교
e() { awk '/^Udp:/{n++} n==2 && /^Udp:/{print $6; exit}' /proc/net/snmp; }
a=$(e); sleep 20; b=$(e); echo "그림자 구성(정지) 20 s: 수신 버퍼 오류 +$((b-a)) (초당 $(( (b-a)/20 )))"
CN=isaac_ros_dev-aarch64-container
P=$(docker exec $CN bash -c "pgrep -f '__node:=cuvslam_[c]ontainer'" | head -1); docker exec $CN kill -STOP $P
a=$(e); sleep 20; b=$(e); echo "cuVSLAM 일시정지(SIGSTOP) 20 s: +$((b-a)) (초당 $(( (b-a)/20 )))"
docker exec $CN kill -CONT $P; echo "cuVSLAM 재개(pid $P)"
grep -A1 '^Udp:' /proc/net/snmp | head -2
