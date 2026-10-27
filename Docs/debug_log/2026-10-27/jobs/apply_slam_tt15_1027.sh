#!/bin/bash
# §21 Jetson: slam.launch.py(transform_timeout 1.5) 를 src · 설치본에. 로버 안 움직임. 해시는 git blob(PC HEAD 와 대조)
R=~/ros2_ws/src/rover_bringup/launch/slam.launch.py; I=~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/slam.launch.py
echo "이전 src blob $(git hash-object $R | cut -c1-10) · 설치본 $( [ -L $I ] && echo "링크→$(readlink -f $I)" || echo "일반파일 blob $(git hash-object $I | cut -c1-10)")"
cp /tmp/up_slam.launch.py $R; [ -L $I ] || cp $R $I
echo "새 src blob $(git hash-object $R | cut -c1-10) · 설치본 blob $(git hash-object $(readlink -f $I) | cut -c1-10) · CR $(grep -c $'\r' $R)"
grep -n "'transform_timeout'" $R
