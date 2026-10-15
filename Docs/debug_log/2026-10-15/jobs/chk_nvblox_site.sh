#!/bin/bash
# (10-15 §13) nvblox 컨테이너 안에서 ESDF 'site' 판정 소스·기본값 찾기 — 읽기만, 로버 안 움직임
C=$(docker ps --format '{{.Names}}' | grep -m1 isaac_ros_dev)
echo "컨테이너: ${C:-없음}"
[ -z "$C" ] && exit 0
docker exec "$C" bash -c 'for d in /workspaces /opt/ros /usr/local/include /usr/include; do grep -rIl --include=*.h --include=*.hpp --include=*.cu --include=*.cpp --include=*.yaml "max_site_distance" $d 2>/dev/null; done | head -20' > /tmp/site_files.txt
cat /tmp/site_files.txt
for f in $(cat /tmp/site_files.txt | head -8); do echo "=== $f"; docker exec "$C" grep -n -B3 -A6 "max_site_distance" "$f" | head -60; done
