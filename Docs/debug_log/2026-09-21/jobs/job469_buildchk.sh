#!/bin/bash
echo "빌드 프로세스: $(pgrep -fc build_image_layers) | docker pull/build: $(pgrep -fa 'docker (pull|build|buildx)' | wc -l)"
echo "로그 $(wc -l < /tmp/isaac_build.log) 줄, 마지막 6줄:"; tail -6 /tmp/isaac_build.log | cut -c1-170
echo "images: $(docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}' | grep -E 'isaac|nvcr' | tr '\n' ';')"
echo "docker 진행 중 컨테이너: $(docker ps --format '{{.Names}} {{.Image}}' | tr '\n' ';') | 디스크 $(df -h / | tail -1 | awk '{print $4}') | load $(cut -d' ' -f1-3 /proc/loadavg) | net rx MB: $(awk '/wlP1p1s0/{printf "%.0f", $2/1e6}' /proc/net/dev)"
