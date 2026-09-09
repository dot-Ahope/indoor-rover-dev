#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for f in foxglove.launch.py sensors.launch.py; do
  sed -i 's/\r$//' /tmp/$f
  cp /tmp/$f ~/ros2_ws/src/rover_bringup/launch/
  cp /tmp/$f ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/
done
python3 -c "import ast;[ast.parse(open('/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/launch/'+f).read()) for f in ('foxglove.launch.py','sensors.launch.py')]" && echo "  문법 OK"
echo "  viz 기본값: $(grep -aoE \"'viz', default_value='[a-z]+'\" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/foxglove.launch.py)"
echo "=== foxglove 단독 기동 시험 (파라미터 수용 여부) ==="
setsid nohup ros2 launch rover_bringup foxglove.launch.py > /tmp/fgtest.log 2>&1 &
sleep 10
echo "  프로세스: $(pgrep -fc foxglove_bridge)"
grep -aiE "error|invalid|not declared|exception|Starting|listening" /tmp/fgtest.log | tail -6 | cut -c1-140 | sed 's/^/  /'
echo "  CPU: $(ps -p $(pgrep -f foxglove_bridge | head -1) -o %cpu= 2>/dev/null | tr -d ' ')%"
pkill -TERM -f foxglove_bridge; pkill -TERM -f "foxglove.launch"; sleep 2
echo "  정리 후 프로세스: $(pgrep -fc foxglove_bridge)"
