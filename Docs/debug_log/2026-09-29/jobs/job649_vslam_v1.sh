#!/bin/bash
# 09-29 §9 V1: 컨테이너에서 job647 측정(DUR·LABEL) + 같은 시간 부하(top·tegrastats) 기록
DUR=${1:-60}; LAB=${2:-V1}
CN=isaac_ros_dev-aarch64-container
(timeout $((DUR+2)) tegrastats --interval 1000 > /tmp/vslam_tegra_$LAB.log 2>&1 &)
(for i in $(seq 1 $((DUR/5))); do top -b -n1 -w 200 | head -25; sleep 5; done > /tmp/vslam_top_$LAB.log 2>&1 &)
docker exec -u admin $CN bash -lc "export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; python3 /tmp/job647_vslam_measure.py $DUR $LAB" 2>&1 | grep -av "^\["
sleep 3
echo "== 부하(top 평균 %CPU, 코어 1 = 100)"
awk '/component_con|realsense2_c|rplidar|python3|ekf_node/ {c[$NF]+=$9; n[$NF]++} END {for (k in c) printf "  %-22s %.1f\n", k, c[k]/n[k]}' /tmp/vslam_top_$LAB.log | sort -k2 -nr | head -8
echo "  전체 CPU 사용(top idle 기준 평균): $(awk '/^%Cpu/ {s+=100-$8; n++} END {printf "%.0f %% (6 코어 합 기준 %.0f %%)", s/n, 6*s/n}' /tmp/vslam_top_$LAB.log)"
echo "  GPU GR3D 평균: $(grep -aoE 'GR3D_FREQ [0-9]+%' /tmp/vslam_tegra_$LAB.log | grep -oE '[0-9]+' | awk '{s+=$1;n++} END {if(n) printf "%.0f %% (n=%d)", s/n, n}')"
