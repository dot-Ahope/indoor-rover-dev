#!/bin/bash
# 10-06 R3: rover_bringup(rf2o_gate.py·rf2o.yaml·ekf.launch.py·CMakeLists) 배포·빌드, 재생용 bag 풀기
P=~/ros2_ws/src/rover_bringup; S=/tmp/r3
cp $S/rf2o_gate.py $P/scripts/ && chmod +x $P/scripts/rf2o_gate.py && cp $S/rf2o.yaml $P/config/ && cp $S/ekf.launch.py $P/launch/ && cp $S/CMakeLists.txt $P/
cd ~/ros2_ws && source /opt/ros/humble/setup.bash && colcon build --packages-select rover_bringup 2>&1 | grep -aE "Finished|Failed|rror" | head -3
ls -la ~/ros2_ws/install/rover_bringup/lib/rover_bringup/rf2o_gate.py ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/rf2o.yaml
for b in f2b3 f2b4; do [ -d /tmp/bag_$b ] || tar -xzf $S/bag_$b.tgz -C /tmp; done; ls -d /tmp/bag_f2b*
