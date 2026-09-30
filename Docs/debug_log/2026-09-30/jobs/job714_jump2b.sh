#!/bin/bash
# 09-30 §13 보충: Ceres 최적화(루프 클로저) 흔적 횟수·시각, slam 시작 시각, 카메라 IMU 실제 수신률(기동 때 Motion Module failure 경고 확인)
echo "slam.log 첫 줄 시각: $(head -3 /tmp/slam.log | grep -aoE '\[[0-9]{10}\.' | head -1 | tr -d '[.' | xargs -I{} date -d @{} '+%T')"
echo "Ceres 경고(최적화 실행 흔적) $(grep -ac 'preprocessor.cc' /tmp/slam.log)건:"; grep -a 'preprocessor.cc' /tmp/slam.log | grep -aoE '[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]+'
echo "slam 버림 전체 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회"
echo "-- /imu/data, /scan, /odometry/filtered 수신률(각 5 s)"
for t in /imu/data /scan /odometry/filtered; do echo "$t $(timeout 6 ros2 topic hz $t 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"; done
