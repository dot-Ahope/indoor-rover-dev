#!/bin/bash
python3 /tmp/job711_rotchk.py 2>&1 | grep -av "^\["
echo "프로세스: 컨디셔너 $(pgrep -fc sensor_conditioner) · ekf $(pgrep -fc ekf_node) · realsense $(pgrep -fc realsense2_camera)"
