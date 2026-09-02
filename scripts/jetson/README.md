# Jetson 운영 스크립트

Claude Code가 Jetson(`jetson@192.168.0.101`)에서 실행하는 스크립트들. PC에서 WSL+sshpass로 전송·실행한다.
**비밀번호는 `<PW>`로 마스킹**되어 있으니 실행 시 실제 값으로 치환. 날짜별 전체 이력은 `Docs/debug_log/<날짜>/jobs/`.

## ⚠ 컨트롤러(보드) RESET 필요 판단표

micro-ROS 세션은 **agent를 재시작하면 끊긴다**(펌웨어가 부팅/연결 시 1회만 세션 수립 — 재연결 로직 부재).
따라서 **agent를 재시작하는 스크립트만 보드 RESET이 필요**하다.

| 스크립트 | 하는 일 | agent 재시작? | **보드 RESET 필요?** |
|---|---|---|---|
| `spin_map_launch.sh` (+`spin_map_core.sh`) | 제자리 360° 회전 맵핑 (detach, 풋프린트 가드) | ❌ | **불필요** |
| `check_spin_log.sh` | 회전 로그·상태 확인 (읽기 전용) | ❌ | 불필요 |
| `safety_stop.sh` | 회전 프로세스 정리 + 정지 지령 | ❌ | 불필요 |
| `check_reboot_or_wifi.sh` | 재부팅 vs WiFi 단절 판별 (읽기 전용) | ❌ | 불필요 |
| `restart_slam.sh` | slam_toolbox만 재시작 (맵 초기화) | ❌ | 불필요 |
| `restart_full_stack.sh` | **base.launch(=agent 포함) + sensors 재시작** | ✅ | **필요** |

**요약**: `restart_full_stack.sh`(agent 재시작 포함)만 실행 후 **보드 RESET 버튼**을 눌러야 `/wheel_odom` 등이 돌아온다.
나머지(회전·SLAM·진단·정지)는 세션을 안 건드리므로 RESET 불필요.

## 세션 살아있는지 빠른 확인
`check_reboot_or_wifi.sh` 또는 `ros2 topic hz /wheel_odom` (50Hz 나오면 세션 정상).

## 제어 경로와 WiFi
로버 제어는 **Jetson→USB→보드(로컬)**. WiFi는 PC 모니터링용일 뿐. 그래서 회전은 detach로 띄우면
**WiFi가 끊겨도 완주**한다(`spin_map_launch.sh`). 회전 중 WiFi 드롭은 강철 섀시 안테나 차폐 추정.
