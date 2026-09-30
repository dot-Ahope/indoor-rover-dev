#!/bin/bash
# 09-30 §17: 사용자 "멈추고 마무리" — 점프 전 재생(job719) 중단, 도메인 42 재생 slam 정리. 라이브 센서·에이전트는 그대로.
pkill -f job719_cut.sh; pkill -f job719_cutreplay.py
pkill -INT -f "async_slam_toolbox_node.*use_sim_time:=true"; sleep 2; pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null
echo "남은: 재생기 $(pgrep -fc job719_cutreplay.py) · 재생 slam $(pgrep -fc 'async_slam_toolbox_node.*use_sim_time:=true') · bag 기록 $(pgrep -fc 'ros2 bag record')"
ls -la /home/jetson/maps/office/ | grep -a cand || echo "후보 지도 파일 없음(저장 전 중단)"
du -sh /home/jetson/bags/map_0930_1724
