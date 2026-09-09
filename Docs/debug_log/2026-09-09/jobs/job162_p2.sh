#!/bin/bash
LIB=/opt/ros/humble/lib/libspatio_temporal_voxel_layer_core.so
for w in clearing clear_after_reading voxel_filter filter data_type origin_z voxel_min_points enabled decay_acceleration model_type track_unknown_space restore_cleared_footprint; do
  n=$(strings $LIB 2>/dev/null | grep -acE "(^|\.)$w$")
  printf "  %-28s %s\n" "$w" "$([ "$n" != "0" ] && echo 존재 || echo '없음(정확일치)')"
done
echo ""
echo "=== 예제 파라미터 파일이 함께 설치됐는지 ==="
find /opt/ros/humble/share/spatio_temporal_voxel_layer -type f 2>/dev/null | sed 's/^/  /'
