#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== /dev/shm 내용 ==="
ls -l /dev/shm 2>/dev/null | head -5
echo "  총 $(ls /dev/shm 2>/dev/null | wc -l)개"
echo "  fastrtps_port*: $(ls /dev/shm 2>/dev/null | grep -c fastrtps_port)"
echo "  fastrtps_ (그 외): $(ls /dev/shm 2>/dev/null | grep -c '^fastrtps' )"
echo "  sem.fastrtps*: $(ls /dev/shm 2>/dev/null | grep -c '^sem.fastrtps')"
echo ""
echo "=== 문제 포트 파일의 소유·잠금 ==="
for f in fastrtps_port7423 fastrtps_port7427; do
  ls -l /dev/shm/$f* 2>/dev/null | sed 's/^/  /'
  fuser -v /dev/shm/$f 2>&1 | tail -2 | sed 's/^/    /'
done
echo ""
echo "=== 죽은 프로세스가 남긴 것인지: 현재 열려있는 참조 ==="
echo "  /dev/shm 을 여는 프로세스 수: $(fuser /dev/shm/* 2>/dev/null | tr ' ' '\n' | sort -u | grep -c '[0-9]')"
echo ""
echo "=== /odometry/filtered, /tf 퍼블리셔 ==="
timeout 8 ros2 topic info /odometry/filtered --verbose 2>/dev/null | grep -aE "Publisher count|Node name|Reliability" | head -6 | sed 's/^/  /'
timeout 8 ros2 topic info /tf 2>/dev/null | sed 's/^/  /'
