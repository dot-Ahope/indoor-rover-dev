#!/bin/bash
LIB=/opt/ros/humble/lib/libspatio_temporal_voxel_layer_core.so
echo "=== 레이어 레벨 파라미터 후보 ==="
strings $LIB 2>/dev/null | grep -aoE "^(enabled|voxel_decay|decay_model|voxel_size|track_unknown_space|mark_threshold|update_footprint_enabled|combination_method|origin_z|publish_voxel_map|transform_tolerance|mapping_mode|map_save_duration|observation_sources|unknown_threshold|restore_cleared_footprint)$" | sort -u | sed 's/^/  /'
echo ""
echo "=== 소스 레벨 파라미터 후보 ==="
strings $LIB 2>/dev/null | grep -aoE "^(topic|data_type|marking|clearing|obstacle_range|min_obstacle_height|max_obstacle_height|expected_update_rate|observation_persistence|inf_is_valid|voxel_filter|clear_after_reading|max_z|min_z|vertical_fov_angle|vertical_fov_padding|horizontal_fov_angle|decay_acceleration|model_type|filter|voxel_min_points|enabled|sensor_frame)$" | sort -u | sed 's/^/  /'
echo ""
echo "=== 문자열에 나타나는 '.' 접미 파라미터 (소스 하위) ==="
strings $LIB 2>/dev/null | grep -aoE "^\.[a-z_]+$" | sort -u | head -40 | sed 's/^/  /'
