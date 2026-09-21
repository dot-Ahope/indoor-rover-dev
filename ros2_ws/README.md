# ros2_ws — Jetson ROS2 워크스페이스 (소스)

이 디렉토리의 `src/`가 **정본**이다. Claude Code는 여기서 편집하고 Jetson(`~/ros2_ws/src`)으로 동기화한다.

## 패키지
- **rover_bringup** — launch(base/sensors/full/camera/lidar/ekf/slam/foxglove) + param(ekf.yaml·slam.yaml) + `scripts/sensor_conditioner.py`
- **rover_description** — `urdf/rover.urdf`(WT-600 확정본, = `Docs/02_hardware/rover.urdf` 사본) + `meshes/sensor_deck.stl` + description.launch.py
  - `urdf/rover.urdf.xacro` : 데크 실측 인자화 실험용(기본 미사용, `use_xacro:=true`)

## Jetson 동기화 (PC→Jetson)
```
# WSL 경유 (지시서 §0 패턴). PC 편집 → Jetson ~/ros2_ws/src → colcon build
wsl -d Ubuntu-22.04 -u root -- bash -c "cp -r /mnt/f/6_Indoor_Rover/Rover/ros2_ws/src /tmp/rover_src && \
  find /tmp/rover_src -type f -not -name '*.stl' -exec sed -i 's/\r$//' {} + && \
  sshpass -p '<PW>' scp -r .../src jetson@<HOST>:~/ros2_ws/ && \
  sshpass -p '<PW>' ssh jetson@<HOST> 'cd ~/ros2_ws && colcon build --symlink-install'"
```
빌드산출물(build/install/log)·__pycache__는 `.gitignore` 처리됨.

## 실행 (Jetson)
- `ros2 launch rover_bringup base.launch.py`  — micro-ros agent(Docker) + robot_state_publisher. ⚠ 재시작 시 보드 RESET.
- `ros2 launch rover_bringup sensors.launch.py` — camera+lidar+foxglove+EKF (agent 무관, 자유 재시작)
- `ros2 launch rover_bringup slam.launch.py`  — slam_toolbox
- 시각화: Foxglove Studio → `ws://<jetson-ip>:8765`
