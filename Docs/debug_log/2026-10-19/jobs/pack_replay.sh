#!/bin/bash
# (10-19 §6) ~/bags 의 재생 출력을 /tmp 에 tgz 로 묶음(PC 회수용) — 인자: 꼬리표 ... 로버 안 움직임
for t in "$@"; do tar czf /tmp/replay_$t.tgz -C /home/jetson/bags replay_$t && echo "묶음 replay_$t.tgz $(stat -c %s /tmp/replay_$t.tgz) B"; done
