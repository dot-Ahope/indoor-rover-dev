#!/bin/bash
# 데크 yaw 보정 배포 (2026-09-18): rover.urdf·rover.urdf.xacro·stuck_monitor.py 를 src+install 에. 기존본은 ~/ros2_ws/.bak_20260918/ 에 백업.
W=/home/jetson/ros2_ws; B=$W/.bak_20260918; mkdir -p $B
set -e
for pair in "rover.urdf rover_description/urdf rover_description/share/rover_description/urdf" \
            "rover.urdf.xacro rover_description/urdf rover_description/share/rover_description/urdf" \
            "stuck_monitor.py rover_bringup/scripts rover_bringup/lib/rover_bringup"; do
  set -- $pair; f=$1; src=$W/src/$2/$f; ins=$W/install/$3/$f
  [ -e "$src" ] && cp -p "$src" "$B/src_$f" ; [ -e "$ins" ] && cp -pL "$ins" "$B/install_$f"
  echo "  $f: install 은 $( [ -L "$ins" ] && echo "심볼릭 → $(readlink "$ins")" || echo 복사본 )"
  cp /tmp/$f "$src"; [ -L "$ins" ] || cp /tmp/$f "$ins"
  [ "$f" = stuck_monitor.py ] && chmod +x "$src" "$ins"
  cmp -s /tmp/$f "$src" && cmp -s /tmp/$f "$ins" && echo "   배포 확인 OK" || { echo "   ★ 불일치"; exit 1; }
done
set +e
source /opt/ros/humble/setup.bash
python3 - <<'PY'
import xacro, re
for name, xml in (('rover.urdf', open('/home/jetson/ros2_ws/install/rover_description/share/rover_description/urdf/rover.urdf').read()),
                  ('xacro', xacro.process_file('/home/jetson/ros2_ws/install/rover_description/share/rover_description/urdf/rover.urdf.xacro').toxml())):
    for j in ('sensor_deck_joint', 'lidar_joint', 'camera_joint'):
        m = re.search(r'<joint name="%s".*?<origin[^>]*xyz="([^"]+)"[^>]*rpy="([^"]+)"' % j, xml, re.S)
        print('  %-10s %-18s xyz=%s rpy=%s' % (name, j, m.group(1) if m else '-', m.group(2) if m else '-'))
PY
grep -n "^LIDAR_YAW" $W/install/rover_bringup/lib/rover_bringup/stuck_monitor.py
python3 -m py_compile $W/install/rover_bringup/lib/rover_bringup/stuck_monitor.py && echo "  stuck_monitor 문법 OK"
