#!/bin/bash
# mp12(temperature 0.3) vs mp9~11(0.15): 흔들림(job407) + 코스트맵 상자 여유(job416), 같은 지표
source /opt/ros/humble/setup.bash; cd /tmp
echo "######## job407 흔들림"
python3 /tmp/job407_wobble.py /tmp/bag_mp9 1789621954.078 /tmp/bag_mp10 1789622875.413 /tmp/bag_mp11 1789624421.417 /tmp/bag_mp12 1789631920.2186 2>&1 | grep -av 'Opened database'
echo "######## job416 코스트맵 상자 여유"
for a in "mp9 1789621954.078" "mp10 1789622875.413" "mp11 1789624421.417" "mp12 1789631920.2186"; do set -- $a
  echo "== $1"; python3 /tmp/job416_boxclear.py /tmp/bag_$1 $2 2>&1 | grep -av 'Opened database' | grep -aE "^상자 LETHAL|^ +(1[4-9]|2[0-9])\.[0-9] \|" | awk '{print}' | cut -c1-150
done
echo "######## 끝 $(date +%T)"
