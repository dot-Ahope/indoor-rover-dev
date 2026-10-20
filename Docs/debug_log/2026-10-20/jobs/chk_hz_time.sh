#!/bin/bash
unset FASTRTPS_DEFAULT_PROFILES_FILE
for i in 1 2 3 4 5; do
  T0=$(date +%s.%N); L=$(timeout 15 ros2 topic hz /wheel_odom 2>&1 | grep -am1 "average rate"); T1=$(date +%s.%N)
  echo "  $i: 첫 rate 줄까지 $(echo "$T1 - $T0" | bc | cut -c1-5) s · $L"
done
