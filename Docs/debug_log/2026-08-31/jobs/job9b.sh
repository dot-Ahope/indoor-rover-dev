#!/bin/bash
# 조이스틱 장치 인식 + joy_node 패키지 확인
echo "===USB 조이스틱 장치==="
ls -l /dev/input/js* 2>/dev/null || echo "  /dev/input/js* 없음"
ls -l /dev/input/event* 2>/dev/null | tail -5
echo "===USB 목록 (조이스틱 후보)==="
lsusb | grep -viE "hub|root|realsense|8086|1a86|10c4|Realtek|IMC" | sed 's/^/  /'
echo "===입력장치 이름==="
for e in /dev/input/event*; do
  n=$(cat /sys/class/input/$(basename $e)/device/name 2>/dev/null)
  echo "  $e: $n"
done 2>/dev/null | grep -iE "joy|game|pad|xbox|dual|controller|wireless" || echo "  (joystick 이름 매칭 없음 — 전체는 위)"
echo "===joy 패키지 설치 여부==="
for p in joy joy-linux teleop-twist-joy; do dpkg -l 2>/dev/null | grep -qE "ros-humble-$p\b" && echo "  $p: 설치됨" || echo "  $p: 없음"; done
echo "===jstest 가용==="
which jstest 2>/dev/null || echo "  jstest 없음(joystick 패키지)"
