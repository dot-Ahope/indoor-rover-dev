#!/bin/bash
# 09-29 §10: M1(프로젝터 켬/끔 깊이) → M2(번갈이 60 fps 실현성). cuVSLAM·전용 카메라를 먼저 내린다.
set +u
bash /tmp/job648_vslam_down.sh
CAM() { : > /tmp/emit_cam.log; setsid nohup ros2 run realsense2_camera realsense2_camera_node --ros-args -r __node:=camera -r __ns:=/camera "$@" > /tmp/emit_cam.log 2>&1 < /dev/null & sleep 12; }
echo "########## M1: 깊이 640x480x15, IR·컬러·점군·IMU 끔 ##########"
CAM -p enable_depth:=true -p enable_color:=false -p enable_infra1:=false -p enable_infra2:=false -p enable_gyro:=false -p enable_accel:=false \
    -p depth_module.depth_profile:=640x480x15 -p depth_module.profile:=640x480x15 -p depth_module.emitter_enabled:=1 -p initial_reset:=true -p publish_tf:=true
for E in 1 0 1 0; do python3 /tmp/job653_depth_emit.py $E 30 2>&1 | grep -a "M1\|없음"; done
pkill -INT -f realsense2_camera_node; sleep 3; pkill -9 -f realsense2_camera_node 2>/dev/null
echo "########## M2: 번갈이(emitter_on_off) 640x480x60, 깊이+IR ##########"
CAM -p enable_depth:=true -p enable_color:=false -p enable_infra1:=true -p enable_infra2:=true -p enable_gyro:=true -p enable_accel:=true -p gyro_fps:=200 -p accel_fps:=200 -p unite_imu_method:=2 \
    -p depth_module.depth_profile:=640x480x60 -p depth_module.infra_profile:=640x480x60 -p depth_module.profile:=640x480x60 \
    -p depth_module.emitter_enabled:=1 -p depth_module.emitter_on_off:=true -p initial_reset:=true -p publish_tf:=true
grep -aoE "Open profile: stream_type: (Depth|Infra)[^;]*FPS: [0-9]+" /tmp/emit_cam.log | sort -u
echo -n "  emitter_on_off 적용값: "; timeout 6 ros2 param get /camera/camera depth_module.emitter_on_off 2>&1 | tail -1
for t in /camera/camera/depth/image_rect_raw /camera/camera/infra1/image_rect_raw /camera/camera/infra2/image_rect_raw; do printf "  %-40s %s\n" $t "$(timeout 8 ros2 topic hz $t 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"; done
echo "  메타데이터(연속 8 개, 프로젝터 관련 키):"
timeout 8 ros2 topic echo /camera/camera/depth/metadata --field json_data 2>/dev/null | grep -aoiE '"(frame_emitter_mode|frame_laser_power_mode|frame_laser_power|emitter[a-z_]*)":[^,}]*' | head -16 | paste -sd' '
echo "  카메라 노드 CPU(top 5 회 평균): $(for i in 1 2 3 4 5; do top -b -n1 -w 200 | awk '/realsense2_c/ {print $9}'; sleep 1; done | awk '{s+=$1;n++} END {if(n) printf "%.1f %%", s/n}')"
