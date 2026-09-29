#!/bin/bash
# rover-base 사용자 서비스 설치 (2026-09-29, Jetson 에서 한 번). systemd/rover-base.service 참고.
#   linger 켜기(로그인 없이 부팅 때 사용자 서비스 기동)에만 sudo 가 한 번 필요하다.
set -e
SRC=$(ros2 pkg prefix rover_bringup 2>/dev/null)/share/rover_bringup/systemd/rover-base.service
[ -f "$SRC" ] || SRC=$(dirname "$0")/../systemd/rover-base.service
mkdir -p ~/.config/systemd/user
cp "$SRC" ~/.config/systemd/user/rover-base.service
if ! loginctl show-user "$USER" -p Linger | grep -q yes; then sudo loginctl enable-linger "$USER"; fi
systemctl --user daemon-reload
systemctl --user enable rover-base.service
echo "linger: $(loginctl show-user "$USER" -p Linger) | enabled: $(systemctl --user is-enabled rover-base)"
