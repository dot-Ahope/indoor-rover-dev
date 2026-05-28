# F5b — micro-ROS transport + agent 연결 검증

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-008 |
| 단계 | F5b (펌웨어 개발 7단계 — F5 의 2/3) |
| 목적 | F405 ↔ micro_ros_agent 통신 동작, `/rover/f5b_heartbeat` Int32 1Hz 발행 확인 |
| 전제 | F5a 완료 (libmicroros.a 빌드·링크), F4 까지 동작 |

---

## 1. F5b 추가/변경 사항

### 1.1 새 파일
- [`App/microros/microros_task.{h,c}`](../firmware/rover_jupiter_fw/App/microros/) — 노드 + heartbeat publisher + 1Hz 발행 루프
- [`App/microros/microros_transport.c`](../firmware/rover_jupiter_fw/App/microros/microros_transport.c) — USART1 + DMA custom transport (dma_transport.c 포크, const 시그니처 수정)
- [`App/microros/microros_heap_freertos.c`](../firmware/rover_jupiter_fw/App/microros/microros_heap_freertos.c) — micro-ROS 가 FreeRTOS heap_4 공유 (별도 32KB 힙 미생성)

### 1.2 Makefile
- `App/microros/*.c` 3개 추가
- `Middlewares/.../extra_sources/microros_allocators.c` 추가 (수정 없음 사용)
- `Middlewares/.../extra_sources/microros_time.c` 추가 (수정 없음 사용)
- `custom_memory_manager.c` 는 **사용 안 함** — heap_freertos 어댑터로 대체

### 1.3 freertos.c
- 새 `microrosTask` (priority `osPriorityNormal`, stack 6 KB) 등록

### 1.4 RAM·Flash 변화

| 영역 | F4 | F5b | 증가 |
|---|---|---|---|
| Flash (text) | 32.7 KB | 76.2 KB | +43.5 KB |
| RAM (bss+data) | 72.2 KB | 93.7 KB | +21.5 KB |
| 사용률 | 56% | 73% | +17%p |
| 여유 RAM | ~56 KB | ~35 KB | -21 KB |

---

## 2. 동작 시나리오

### 2.1 부팅 후 microros task 흐름
```
1. RTOS 시작 + microrosTask 진입 (500ms 대기)
2. rmw_uros_set_custom_transport(huart1, dma callbacks)
3. rcl allocator 설정 (FreeRTOS heap 공유)
4. rmw_uros_ping_agent — agent 응답 대기 (1초 timeout 무한 재시도)
5. agent 연결되면: rclc_support_init → node_init → publisher_init
6. 1Hz 로 std_msgs/Int32 발행 (counter 증가)
```

UART5 콘솔 출력 예 (성공 케이스):
```
[uROS] waiting for agent...
[uROS] no agent. retrying...
[uROS] no agent. retrying...
[uROS] agent OK
[uROS] publisher ready — /rover/f5b_heartbeat
```

이후 콘솔 출력 없음 (publish 성공 시 침묵). 실패 시 `[uROS] publish rc=...` 출력.

### 2.2 동시에 도는 다른 태스크
- F1 sanity: 1Hz 진단 dump (그대로)
- controlTask: 100Hz PID (그대로)
- f4PidTask: F4 step response 시퀀스 (그대로 — 모터 자동 회전)

---

## 3. agent 측 설정 (PC/Jetson/WSL)

micro-ROS agent 는 ROS2 측에서 실행. 옵션 3가지:

### 3.1 Jetson (권장 — Ubuntu 22.04 + ROS2 Humble 이미 셋업)
```bash
# Jetson 에서
sudo apt install ros-humble-micro-ros-agent
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyACM0 -b 921600
```
`/dev/ttyACM0` 는 CH340N 인식 디바이스. `dmesg | tail` 로 실제 디바이스명 확인.

### 3.2 WSL2 Ubuntu-22.04 (이미 F5a 셋업됨)
WSL 은 기본적으로 COM port 직접 접근 안 됨. `usbipd-win` 필요:
```powershell
# Windows host
winget install usbipd
usbipd list                                  # CH340N BUSID 확인
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>          # WSL 으로 redirect
```
WSL 안에서:
```bash
source /opt/ros/humble/setup.bash
apt install ros-humble-micro-ros-agent       # 또는 colcon 빌드
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 921600
```

### 3.3 Docker (어디서든)
```bash
docker run -it --rm -v /dev:/dev --device=/dev/myserial --net=host \
  microros/micro-ros-agent:humble \
  serial --dev /dev/myserial -b 921600
```

---

## 4. 검증 절차

### 4.1 준비
1. 펌웨어 플래시
2. USART1 (CH340N) 을 호스트 USB 에 연결 — `/dev/ttyACM0` (또는 ttyUSB0) 인식 확인
3. UART5 (별도 디버그) 콘솔도 띄움 — `[uROS] ...` 메시지 관찰용
4. agent 측 셋업 §3 중 택일

### 4.2 순서
1. **F405 부팅** → UART5 콘솔에 `[uROS] waiting for agent...` 출력
2. **호스트에서 agent 실행** (§3) — agent 콘솔에 `Serial port not found.` 또는 ping 메시지
3. F405 콘솔에 `[uROS] agent OK` + `publisher ready` 출력 확인
4. ROS2 측에서 토픽 확인:
   ```bash
   ros2 topic list
   # 기대: /rover/f5b_heartbeat 보임
   ros2 topic echo /rover/f5b_heartbeat
   # 기대: data: 0, data: 1, data: 2 ... (1초 간격 증가)
   ```

### 4.3 체크 항목

| # | 항목 | 통과 조건 |
|---|---|---|
| 1 | agent 연결 | F405 콘솔 `agent OK` 표시 |
| 2 | publisher 생성 | `ros2 topic list` 에 `/rover/f5b_heartbeat` |
| 3 | 발행 주기 | `ros2 topic hz /rover/f5b_heartbeat` ≈ 1.0 Hz |
| 4 | 데이터 증가 | echo 시 data 가 1씩 monotonic 증가 |
| 5 | F4 PID 그대로 | F4 step response 시퀀스 정상 동작 (모터 + 콘솔) |
| 6 | RAM 안정성 | freeHeap 1분간 같은 값 유지 (leak 없음) |
| 7 | 재연결 | agent 종료·재시작 시 F405 가 재연결 (현재는 미구현 — F5c 에서) |

---

## 5. 디버깅

| 증상 | 원인 후보 | 해결 |
|---|---|---|
| `[uROS] waiting for agent...` 영구 출력 | agent 미실행 / 잘못된 ttyXXX | dmesg 로 디바이스명 확인, agent 재실행 |
| agent 콘솔에 "Stream id 0x80 invalid" | baudrate 불일치 | 양쪽 921600 확인 |
| agent 콘솔에 "Serial port closed" | F405 reset 또는 USB 끊김 | 재연결 |
| `[uROS] support_init rc=...` | RAM 부족 | `xPortGetFreeHeapSize` 출력해 확인. heap 상향 검토 |
| `ros2 topic list` 에 안 보임 | agent 도메인 mismatch | `ROS_DOMAIN_ID` 확인 (양쪽 동일해야) |
| F4 PID 동작 안 함 | microros 가 CPU 점유 | microrosTask priority 재검토 |
| stack overflow hook 발동 | microrosTask 스택 부족 | 6 KB → 8 KB 로 상향 |

---

## 6. F5b 완료 기준 (DoD)

- [ ] agent 연결 후 `[uROS] agent OK` 표시
- [ ] `/rover/f5b_heartbeat` 토픽 1Hz 발행 (echo 확인)
- [ ] F4 PID 시퀀스 그대로 동작 (모터 + 콘솔)
- [ ] 1분간 RAM 안정 (`freeHeap` 변동 없음)
- [ ] 콘솔 메시지 끊김·재시작 없음

→ 통과하면 **F5b 완료**, F5c (`/cmd_vel` subscriber + speed_controller 연결) 진행.

---

## 7. 알려진 한계 / 다음 단계

- **재연결 미구현**: agent 끊기면 publish 가 silent fail. F5c 또는 F8 에서 watchdog 추가.
- **단일 publisher 만**: 본격 토픽 (`/wheel_odom`, `/imu/data_raw`, `/imu/mag`, `/rover/status`, `/battery`) 은 F5c~F8 에서.
- **Subscriber 없음**: `/cmd_vel` 구독은 F5c 의 핵심.
- **micro-ROS 와 FreeRTOS heap 공유**: 한쪽 누수가 다른 쪽 영향. F8 에서 heap 모니터링 강화.
- **USART1 single channel**: 향후 대역 부족 시 USART1 921600 → 2 Mbps 또는 F405 USB CDC 검토.

---

*문서 끝.*
