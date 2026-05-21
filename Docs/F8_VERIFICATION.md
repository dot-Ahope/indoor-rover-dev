# F8 — 통합·안전·진단

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-012 |
| 단계 | F8 (펌웨어 개발 마지막 단계) |
| 목적 | cmd_vel watchdog + time sync + /battery + /rover/status — 안전·운용성 마무리 |
| 전제 | F5~F7 완료 |

---

## 1. 추가/변경 사항

### 1.1 cmd_vel watchdog
[`safety_monitor.{h,c}`](../firmware/rover_jupiter_fw/App/app/) 확장:
- `safety_monitor_cmdvel_received()` — cmd_vel 콜백에서 매번 호출, `HAL_GetTick()` 기록
- `safety_monitor_update()` 가 매 cycle (100Hz) `now − last > 500ms` 체크 → 진입 시 motor stop + speed_controller reset
- `safety_monitor_cmdvel_timeout()` — 외부 조회용
- **Latching 안 함** — cmd_vel 다시 들어오면 자동 해제. Stall fault 는 latching 유지 (수동 reset 필요).

### 1.2 micro-ROS time sync
[`microros_task.c`](../firmware/rover_jupiter_fw/App/microros/microros_task.c):
- 초기화 직후 `rmw_uros_sync_session(1000)` 호출 → agent 와 동기
- `s_time_offset_ns` 캐시 (boot time → wall time 변환 가능 — F8 단계에선 header.stamp 는 boot time 그대로 유지, 차후 변환 사용 가능)
- 콘솔 출력: `[uROS] time sync OK` 또는 FAIL

### 1.3 /battery publisher (sensor_msgs/BatteryState @ 1Hz)
- ADC1 IN8 (PB0) raw 값을 `voltage` 필드에 그대로 (voltage divider ratio 미정 — TODO F8.5)
- 나머지 필드 NaN (sensor_msgs convention "unknown")

### 1.4 /rover/status publisher (diagnostic_msgs/DiagnosticArray @ 5Hz)
- `DiagnosticStatus[1]` array — name="rover_jupiter_fw", hardware_id="F405"
- level / message 가 fault 상태 반영:
  - `STALL fault` (level=2 ERROR) — stall fault latching 활성
  - `cmd_vel timeout` (level=1 WARN) — cmd_vel watchdog 발동
  - `OK` (level=0)

### 1.5 F1 sanity 출력 확장
- 매 줄 끝에 `heap=NNNNN` 추가 (freeHeap 모니터링)
- `[FAULT]` 또는 `[CMDVEL_TO]` flag 표시

### 1.6 RAM·Flash
| 영역 | F7 | F8 | 증가 |
|---|---|---|---|
| Flash | 106 KB | 114 KB | +8 KB (BatteryState + DiagnosticArray msg) |
| RAM   | 98 KB  | 99 KB  | +1 KB |
| 여유 RAM | 30 KB | 29 KB | -1 KB |

---

## 2. 검증 절차

### 2.1 토픽 확인
```bash
ros2 topic list
# 기대: /cmd_vel, /imu/data_raw, /wheel_odom, /rover/f5b_heartbeat, /battery, /rover/status

ros2 topic hz /battery       # 약 1 Hz
ros2 topic hz /rover/status  # 약 5 Hz
```

### 2.2 watchdog 검증 (핵심!)
```bash
# 1) 짧은 명령 1회 → 500ms 후 정지 확인
ros2 topic pub --once /cmd_vel geometry_msgs/Twist '{linear: {x: 0.1}}'
# 모터 회전 시작 → 500ms 후 자동 정지
# F1 콘솔에 [CMDVEL_TO] flag 보임
# /rover/status 가 "cmd_vel timeout — motors stopped" WARN

# 2) 연속 명령 → 정상 작동
ros2 topic pub -r 10 /cmd_vel geometry_msgs/Twist '{linear: {x: 0.1}}'
# 모터 계속 회전 (10Hz 명령 → 100ms 마다 갱신, 500ms 안에 항상 새 명령)
# Ctrl+C 로 멈추면 500ms 후 자동 정지
```

### 2.3 /battery 확인
```bash
ros2 topic echo --once /battery
# voltage 필드에 ADC raw 값 (0~4095). F1 콘솔 adc 값과 일치
```

### 2.4 /rover/status 확인
```bash
ros2 topic echo --once /rover/status
# status[0].name = rover_jupiter_fw
# status[0].level = 0 (OK), 1 (cmd_vel timeout 시), 2 (stall fault 시)
# status[0].message 변화 관찰
```

### 2.5 time sync 확인
```bash
ros2 topic echo --once /wheel_odom
# header.stamp 가 boot time 기준 (sync 했지만 header 변환은 F8 단계 미적용)
# F405 콘솔 [uROS] time sync OK 표시 확인
```

### 2.6 체크 항목

| # | 항목 | 통과 조건 |
|---|---|---|
| 1 | watchdog motor stop | --once cmd_vel 후 500ms 내 모터 정지 |
| 2 | watchdog 해제 | -r 10 cmd_vel 중 [CMDVEL_TO] 안 뜸 |
| 3 | /battery 발행률 | ≈ 1.0 Hz |
| 4 | /battery voltage | ADC raw 값 (F1 콘솔 adc 와 동일) |
| 5 | /rover/status 발행률 | ≈ 5 Hz |
| 6 | status level 변화 | 정상 OK, watchdog 시 WARN, stall 시 ERROR |
| 7 | time sync 콘솔 OK | `[uROS] time sync OK` 표시 |
| 8 | freeHeap 안정 | F1 콘솔 heap 값 1분간 변동 없음 |
| 9 | F5~F7 기능 유지 | odom, imu, cmd_vel 그대로 |

---

## 3. F8 완료 기준 (DoD)

- [ ] cmd_vel watchdog 동작 (500ms 후 motor stop)
- [ ] watchdog flag 표시 (콘솔 + /rover/status)
- [ ] /battery 1Hz, /rover/status 5Hz 발행
- [ ] time sync 성공 콘솔 출력
- [ ] freeHeap 누수 없음
- [ ] F5~F7 기능 유지

→ 통과하면 **F8 완료 = F0~F8 펌웨어 개발 전체 완성**.

---

## 4. 남은 작업 (향후)

- **F8.5 — voltage divider ratio**: 사용자가 multi-meter 로 실제 battery V 측정 → ADC raw 와 비율 산출 → `voltage = raw × ratio` 적용.
- **F8.5 — IMU calibration**: gyro.z bias 0.66 rad/s 자동 차감 (1초 startup 평균).
- **F7.5 — AK09916 mag**: ICM-20948 AUX I2C master + `/imu/mag` 발행.
- **header.stamp time sync 적용**: 모든 토픽 stamp 를 `boot_ms + offset` 으로.
- **Stall fault auto-reset**: 일정 시간 후 자동 복귀 또는 ROS service 통한 reset.
- **rover_localization (EKF)**: Jetson 측에서 odom + imu fusion. 양산기 전 단계.
- **양산 이식**: STM32G4/H7 + 외장 모터 드라이버 + 산업급 IMU. Driver/HAL Layer 만 교체.

---

*문서 끝.*
