#!/bin/bash
# 09-29: 재부팅으로 사라진 회전 bag 을 /tmp 에 다시 풀기. 인자 없음(/tmp/bag_*.tgz 를 푼다)
cd /tmp || exit 1
for f in bag_*.tgz; do tar xzf $f && rm -f $f; done
for d in /tmp/bag_s1 /tmp/bag_r1 /tmp/bag_r1b /tmp/bag_r2 /tmp/bag_r2b /tmp/bag_r3 /tmp/bag_s2; do
  [ -d $d ] || { echo "없음 $d"; continue; }
  source /opt/ros/humble/setup.bash
  echo "$d: $(ros2 bag info $d 2>/dev/null | grep -aE 'Duration' | tr -s ' ') | $(ros2 bag info $d 2>/dev/null | grep -aoE '/odometry/filtered|/wheel_odom|/imu/data |/cmd_vel' | tr '\n' ' ')"
done
