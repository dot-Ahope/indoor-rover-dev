# F5c — /cmd_vel subscriber + 차동구동 역기구학

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-009 |
| 단계 | F5c (펌웨어 개발 8단계 — F5 완성) |
| 목적 | ROS2 측 `/cmd_vel` 명령 → F405 모터 회전. 차동구동 역기구학·saturation 검증 |
| 전제 | F5b 완료 (agent 연결·heartbeat 발행), F4 PID 동작 |

---

## 1. F5c 추가/변경 사항

### 1.1 [`microros_task.c`](../../firmware/rover_jupiter_fw/App/microros/microros_task.c)
- `geometry_msgs/Twist` subscriber (`/cmd_vel`) 추가
- `rclc_executor` 1개 slot 으로 spin
- 콜백 `cmdvel_callback`:
  ```
  v_lin = Twist.linear.x   (m/s, X 전방)
  ω     = Twist.angular.z  (rad/s, Z 위방향 = 시계반대 +)
  v_l   = v_lin − ω·B/2
  v_r   = v_lin + ω·B/2    (B = 0.190 m)
  ```
  + 입력 saturation: |v_lin| ≤ MAX_LINEAR_SPEED_MPS (0.654)
  + 회전 명령으로 한쪽이 최대 초과 시 양쪽 비례 스케일 다운 (방향 보존)
- 그 다음 `speed_controller_set_target(MOTOR_LEFT/RIGHT, v_l/v_r)` 호출
- Heartbeat publisher (`/rover/f5b_heartbeat`) 는 F5b 그대로 유지

### 1.2 [`freertos.c`](../../firmware/rover_jupiter_fw/Core/Src/freertos.c)
- **F4 자동 시퀀스 task 비활성** — `/cmd_vel` 이 target 을 설정하므로 두 source 충돌 방지
- 회귀 테스트 필요 시 주석 한 줄 해제

### 1.3 RAM·Flash
| 영역 | F5b | F5c | 증가 |
|---|---|---|---|
| Flash | 76 KB | 93 KB | +17 KB (Twist 타입 지원) |
| RAM   | 94 KB | 94 KB | ≈ 0 |

여유 RAM ≈ 34 KB.

---

## 2. 검증 절차

### 2.1 준비
- F5c 펌웨어 플래시
- F405 ↔ Jetson USB 케이블 연결 (CH340N)
- Jetson 에서 micro_ros_agent 실행 중 (F5b 셋업 그대로):
  ```bash
  sudo docker run -d --rm --name microros_agent \
    -v /dev:/dev --privileged --net=host \
    microros/micro-ros-agent:humble \
    serial --dev /dev/myserial -b 921600
  ```
- **휠 받침대 상태 유지** — cmd_vel 명령 시 모터 회전

### 2.2 F405 콘솔 (UART5, COM9) 기대
```
[uROS] waiting for agent...
[uROS] agent OK
[uROS] ready — pub /rover/f5b_heartbeat, sub /cmd_vel
```

### 2.3 ROS2 측 확인 + 명령

```bash
# 1. 토픽 확인
ros2 topic list
# 기대: /cmd_vel, /rover/f5b_heartbeat 모두 보임

ros2 topic info /cmd_vel
# 기대: Subscription count: 1  ← F405

# 2. 전진 0.2 m/s (양쪽 휠 같은 속도)
ros2 topic pub --once /cmd_vel geometry_msgs/Twist "{linear: {x: 0.2}, angular: {z: 0.0}}"
# 기대: F1 콘솔에 tgt L=+200 R=+200, 모터 회전

# 3. 제자리 회전 (좌회전 — 좌측 휠 후진, 우측 전진)
ros2 topic pub --once /cmd_vel geometry_msgs/Twist "{linear: {x: 0.0}, angular: {z: 1.0}}"
# 기대: tgt L=-95 R=+95 (= ω·B/2 = 1.0 × 0.095)

# 4. 정지
ros2 topic pub --once /cmd_vel geometry_msgs/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
# 기대: tgt L=0 R=0, 모터 정지

# 5. 연속 명령 (예: 전진 0.15 m/s for 5초)
ros2 topic pub -r 10 /cmd_vel geometry_msgs/Twist "{linear: {x: 0.15}}"
# Ctrl+C 로 종료 — 그러나 펌웨어는 마지막 명령 유지 (watchdog F8)
```

### 2.4 체크 항목

| # | 검증 | 통과 조건 |
|---|---|---|
| 1 | subscribe 등록 | `ros2 topic info /cmd_vel` 에서 Subscription count: 1 |
| 2 | 직진 추종 | linear.x=0.2 → 두 휠 v ≈ ±10% 이내 (F4 PID 추종) |
| 3 | 회전 역기구학 | angular.z=1.0 → L=−95 mm/s, R=+95 mm/s (부호 반대) |
| 4 | Saturation | linear.x=2.0 (최대 초과) → 양쪽 654 mm/s 으로 제한 |
| 5 | 스케일 다운 | linear.x=0.5, angular.z=10 → L=±650, R=±650 비율 유지 |
| 6 | 정지 명령 | linear.x=0, angular.z=0 → tgt=0, 모터 정지 |
| 7 | Heartbeat 그대로 | `/rover/f5b_heartbeat` 1Hz 발행 유지 |
| 8 | F4 PID 동작 | tgt 변경 시 dead-zone 보상 포함 PID 추종 |

---

## 3. 알려진 한계 / 다음 단계 (F6~F8)

- **cmd_vel watchdog 미구현**: 명령 끊겨도 모터가 마지막 target 유지 → 위험. **휠 받침대 위에서만 테스트.** F8 에서 500ms 미수신 시 정지 추가.
- **/wheel_odom 발행 없음**: F6 작업.
- **/imu/data_raw, /imu/mag 발행 없음**: F7 작업.
- **/rover/status, /battery 발행 없음**: F8 작업.
- **STALL fault 시 latching**: cmd_vel 들어와도 무시. 펌웨어 reset 필요. F8 에서 reset 명령 또는 자동 복귀 검토.

---

## 4. F5c 완료 기준 (DoD)

- [ ] `ros2 topic pub /cmd_vel` → F405 모터 회전 (검증 §2.4 #2~#6)
- [ ] 역기구학 부호 정확 (전진·후진·좌회전·우회전)
- [ ] Saturation 동작 (V_MAX_MPS 초과 시 비례 스케일)
- [ ] Heartbeat 그대로 발행 (F5b 호환)
- [ ] F1 콘솔에서 tgt 변화 관찰 가능

→ 통과하면 **F5 전체 완료**, F6 (오도메트리 + `/wheel_odom` 발행) 진행.

---

*문서 끝.*
