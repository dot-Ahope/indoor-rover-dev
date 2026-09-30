#!/bin/bash
# 09-30 §14: slam.yaml(loop_search_space_dimension 8→3) 를 src·install 양쪽에 배포 — 지금 도는 SLAM 은 건드리지 않음(다음 prep 에서 반영)
for d in /home/jetson/ros2_ws/src/rover_bringup/config /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config; do
  cp /tmp/slam.yaml $d/slam.yaml && echo "배포: $d/slam.yaml"
done
grep -n "loop_search_space_dimension" /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/slam.yaml
python3 -c "import yaml;yaml.safe_load(open('/tmp/slam.yaml'));print('YAML OK')"
bash -n /tmp/job240_clean.sh && echo "job240 문법 OK"
