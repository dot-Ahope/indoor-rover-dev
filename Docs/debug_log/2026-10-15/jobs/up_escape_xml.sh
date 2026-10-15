#!/bin/bash
# (10-15 §26) 플러그인 xml(name 속성 추가) 배포 — 설치본은 src 링크. 로버 안 움직임
tr -d '\r' < /tmp/behavior_plugins.xml > ~/ros2_ws/src/rover_navigation/behavior_plugins.xml; readlink -f ~/ros2_ws/install/rover_navigation/share/rover_navigation/behavior_plugins.xml; grep -o "name=[^ ]*" ~/ros2_ws/install/rover_navigation/share/rover_navigation/behavior_plugins.xml
