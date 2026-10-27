#!/bin/bash
# §26 SLAM 재생 A/B 묶음(Jetson, 도메인 42, 로버 안 움직임): f2tt1 첫 210 s, 변형마다 같은 입력. 본 스택 SLAM 생존을 앞뒤로 확인.
B=/tmp/bag_f2tt1; L="0 210"
echo "본 스택 SLAM 프로세스(앞): $(pgrep -fc 'lib/slam_toolbox/localization_slam_toolbox_node.*launch_params' )"
SLAM_EXTRA="" bash /tmp/run_slam_replay.sh V0a $B $L
SLAM_EXTRA="" bash /tmp/run_slam_replay.sh V0b $B $L
SLAM_EXTRA="-p do_loop_closing:=false" bash /tmp/run_slam_replay.sh V1_noloop $B $L
SLAM_EXTRA="-p correlation_search_space_resolution:=0.02" bash /tmp/run_slam_replay.sh V2_res02 $B $L
SLAM_EXTRA="-p correlation_search_space_dimension:=0.3" bash /tmp/run_slam_replay.sh V3_dim03 $B $L
SLAM_EXTRA="-p scan_buffer_size:=10" bash /tmp/run_slam_replay.sh V4_buf10 $B $L
echo "본 스택 SLAM 프로세스(뒤): $(pgrep -fc 'lib/slam_toolbox/localization_slam_toolbox_node.*launch_params' )"
ls -la /tmp/slamrep/
