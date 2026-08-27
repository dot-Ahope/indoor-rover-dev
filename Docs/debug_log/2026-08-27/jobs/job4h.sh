#!/bin/bash
# ws 배포: rover_description(xacro+mesh+launch) + rover_bringup(lidar/camera/slam/foxglove launch, slam.yaml) → colcon → xacro 검증
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_description /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
cd ~/ros2_ws && colcon build --symlink-install 2>&1 | tail -3
source ~/ros2_ws/install/setup.bash
echo "===XACRO_CHECK==="
xacro ~/ros2_ws/install/rover_description/share/rover_description/urdf/rover.urdf.xacro lidar_mount_h:=0.29 deck_x:=0.0 deck_y:=0.0 lidar_yaw:=3.14159265 > /tmp/rover_rendered.urdf && echo "xacro OK ($(wc -c < /tmp/rover_rendered.urdf) bytes)"
grep -A2 'name="lidar_joint"' /tmp/rover_rendered.urdf | grep origin
grep -A2 'name="camera_joint"' /tmp/rover_rendered.urdf | grep origin
python3 -c "import xml.dom.minidom as m; m.parse('/tmp/rover_rendered.urdf'); print('XML valid')"
echo "===LAUNCH_FILES==="
ls ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/ ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/
echo "===BUILD_LOG_TAIL==="
tail -4 /tmp/hid_build.log
