#!/bin/bash
# 사용자 승인(09-17): 정지한 slam_toolbox 의 전 스레드 역추적 (읽기 전용 attach, 끝나면 detach)
P=$(pgrep -f async_slam_toolbox_node | head -1)
echo "slam pid $P  stat $(ps -o stat=,pcpu=,etime= -p $P)"
echo "__PW__" | sudo -S -p "" gdb -p $P -batch -nx -ex "set pagination off" -ex "set print thread-events off" -ex "info threads" -ex "thread apply all bt 25" > /tmp/slam_bt.txt 2>&1
echo "gdb 종료코드 $?  출력 $(wc -l < /tmp/slam_bt.txt) 줄"
echo "detach 후 상태: $(ps -o stat=,pcpu= -p $P)"
