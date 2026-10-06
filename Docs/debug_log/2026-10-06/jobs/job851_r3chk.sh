#!/bin/bash
# 10-06 R3 정지 기동 확인: rf2o·게이트·그림자 EKF 동작, 발행률, 게이트 판정, CPU(10 s)
source ~/rf2o_ws/install/setup.bash 2>/dev/null
echo "  프로세스: rf2o $(pgrep -fc rf2o_laser_odometry_node) · 게이트 $(pgrep -fc rf2o_gate.py) · ekf $(pgrep -fc 'ekf_node') · 컨디셔너 $(pgrep -fc sensor_conditioner)"
for tp in /odom_rf2o /odom_rf2o/gated /odometry/filtered /odometry/ekf_a /wheel_odom/plain; do printf "  %-20s %s\n" $tp "$(timeout 6 ros2 topic hz $tp 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"; done
echo "  B3 rot_cov: $(timeout 10 ros2 param get /sensor_conditioner rot_cov_enable 2>&1 | tail -1) · rot_vx_var $(timeout 10 ros2 param get /sensor_conditioner rot_vx_var 2>&1 | tail -1)"
echo "  EKF odom1: $(timeout 10 ros2 param get /ekf_filter_node odom1 2>&1 | tail -1)"
grep -a "게이트 통과" /tmp/sensors.log | tail -1
for p in rf2o_laser_odometry_node rf2o_gate.py ekf_shadow_a; do P=$(pgrep -f "$p" | head -1); [ -n "$P" ] && a=$(awk '{print $14+$15}' /proc/$P/stat); declare "c_$P=$a"; done
sleep 10
for p in rf2o_laser_odometry_node rf2o_gate.py ekf_shadow_a; do P=$(pgrep -f "$p" | head -1); [ -z "$P" ] && continue; b=$(awk '{print $14+$15}' /proc/$P/stat); v=c_$P; echo "  CPU $p: $(( (b - ${!v}) * 100 / 1000 )) %"; done
echo "  위치: $(timeout 8 ros2 run tf2_ros tf2_echo map base_link 2>/dev/null | grep -a Translation | head -1)"
echo "  load $(cut -d' ' -f1-3 /proc/loadavg)"
