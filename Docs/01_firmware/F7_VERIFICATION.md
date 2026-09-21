# F7 — ICM-20948 IMU + /imu/data_raw 발행

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-011 |
| 단계 | F7 (펌웨어 개발 10단계) |
| 목적 | ICM-20948 본 init (accel + gyro), `sensor_msgs/Imu` 발행 |
| 전제 | F6 완료 (`/wheel_odom` 정상 발행) |
| **미포함** | AK09916 자기계 (`/imu/mag`) — F7.5 에서 구현 ([F7.5_VERIFICATION.md](F7.5_VERIFICATION.md)) |

---

## 1. 추가/변경 사항

### 1.1 [`App/drivers/icm20948_driver.{h,c}`](../../firmware/rover_jupiter_fw/App/drivers) — 본 init
- `imu_init()`: WHO_AM_I 확인 + PWR_MGMT_1 wake + PWR_MGMT_2 enable + Bank2 gyro/accel config
- `imu_read()`: ACCEL_XOUT_H 부터 14byte burst read (accel 6 + temp 2 + gyro 6)
- Bank switching helper `select_bank(0..3)`
- 기본 측정 범위:
  - Accel **±2g** → 16384 LSB/g → 1 LSB ≈ 0.0006 m/s²
  - Gyro  **±250 dps** → 131 LSB/dps → 1 LSB ≈ 1.33e-4 rad/s
- DLPF: ~196Hz BW (gyro), ~246Hz (accel)

### 1.2 [`App/app/imu_processor.{h,c}`](../../firmware/rover_jupiter_fw/App/app) — raw → SI
- `imu_processor_update()`: SPI burst → raw int16 → m/s², rad/s, °C
- `imu_processor_get()`: 최신 스냅샷 copy out

### 1.3 [`Core/Src/freertos.c`](../../firmware/rover_jupiter_fw/Core/Src/freertos.c)
- controlTask 에 `imu_processor_update()` 추가 (100Hz, encoder/PID/safety/odom 다음)

### 1.4 [`App/microros/microros_task.c`](../../firmware/rover_jupiter_fw/App/microros/microros_task.c)
- `/imu/data_raw` (`sensor_msgs/Imu`) publisher 추가
- frame_id="imu_link", orientation_covariance[0]=-1 (REP-145 "not provided")
- spin loop 매 cycle 마다 publish (odom과 동일 ~29Hz)

### 1.5 RAM·Flash
| 영역 | F6 | F7 | 증가 |
|---|---|---|---|
| Flash | 103 KB | 106 KB | +3 KB |
| RAM   | 97 KB | 98 KB | +1 KB |
| 여유 RAM | 31 KB | 30 KB | -1 KB |

---

## 2. 검증 절차

### 2.1 토픽 확인
```bash
ros2 topic list
# 기대: /imu/data_raw 추가

ros2 topic info /imu/data_raw
# Type: sensor_msgs/msg/Imu
# Publisher count: 1

ros2 topic hz /imu/data_raw
# 기대: ~25~30 Hz (odom 과 같은 spin loop)
```

### 2.2 정지 상태 확인 — 중력 벡터
**보드를 수평으로 놓고**:
```bash
ros2 topic echo --once /imu/data_raw
```
기대:
- `linear_acceleration`: 한 축이 약 **+9.81 또는 -9.81 m/s²**, 나머지 두 축 ≈ 0
  - 보드 mount 방향에 따라 X/Y/Z 어느 축이 중력 받는지 결정
  - ROS REP-103 정합 (X 전방, Y 좌측, Z 위방향) 이면 `z ≈ +9.81`
- `angular_velocity`: x, y, z 모두 ≈ 0 (±0.02 rad/s 정도 bias 있을 수 있음)
- `header.stamp`: 0 아닌 값

### 2.3 동적 검증
- **보드를 손으로 회전시키며** `ros2 topic echo /imu/data_raw` 관찰
  - 회전축 방향 gyro 가 ±값
  - 정지하면 0 으로 돌아옴
- **보드를 기울이며**: 중력 벡터가 다른 축으로 분산

### 2.4 체크 항목

| # | 항목 | 통과 조건 |
|---|---|---|
| 1 | 토픽 발견 | `/imu/data_raw` 보임 |
| 2 | 발행률 | `ros2 topic hz` ≈ 25~30 Hz |
| 3 | 중력 벡터 | 한 축이 ±(9.5~10.0) m/s² 범위 |
| 4 | 다른 가속도 축 | < ±0.5 m/s² (정지 시) |
| 5 | gyro bias | 정지 시 \|x\|, \|y\|, \|z\| < 0.05 rad/s |
| 6 | 회전 응답 | 손으로 회전 시 해당 축 gyro 변화 |
| 7 | F6 기능 유지 | `/wheel_odom` 29Hz, heartbeat 1Hz |
| 8 | freeHeap | 변동 없음 |

### 2.5 (선택) RViz 시각화
- Add → Imu → Topic: `/imu/data_raw`
- 보드 회전 시 화살표/원 움직임 확인

---

## 3. Axis 매핑 — 보드 mount 확인

ICM-20948 칩의 +X, +Y, +Z 가 차체의 어느 방향인지는 PCB 위 칩 mount 결정.
**ROS REP-103**: X 전방, Y 좌측, Z 위방향.

F7 검증 결과로 매핑 결정:
- 보드 수평 정지 시 어느 축이 +9.81 → 그게 차체 Z (위방향)
- 차체 전진 시 어느 축 가속도 증가 → 그게 차체 X
- 좌회전 시 어느 축 gyro + → 그게 차체 Z (정의상)

매핑 안 맞으면 `imu_processor.c` 에서 축 swap·sign flip 추가. 일단 raw 그대로 발행.

---

## 4. 알려진 한계 / 다음 단계

- **자기계 미포함**: AK09916 (ICM-20948 내장) — **F7.5 에서 구현** ([F7.5_VERIFICATION.md](F7.5_VERIFICATION.md)).
- **Calibration 없음**: bias·scale factor 보정 안 함. 정지 시 gyro bias 출력 가능 (dev 단계).
- **Orientation 미제공**: covariance[0]=-1 표식. Fusion (Madgwick/EKF) 은 Jetson 측 또는 양산기 작업.
- **Covariance 0**: ROS EKF 노드가 사용 시 작은 값 (예: 1e-3 등) 설정 필요. F8.
- **시간 동기 안 됨**: header.stamp 가 boot time. F8 에서 `rmw_uros_sync_session()`.
- **CCM RAM 미활용**: imu_msg static (DMA 불가능 영역 OK), 향후 메모리 압박 시 검토.

---

## 5. F7 완료 기준 (DoD)

- [ ] `/imu/data_raw` 토픽 보임
- [ ] 발행률 ≈ 25~30Hz
- [ ] 정지 시 중력 벡터 정상 (±9.81 한 축)
- [ ] 정지 시 gyro 0 근처 (±0.05 rad/s)
- [ ] 회전 시 gyro 응답
- [ ] F6 기능 유지

→ 통과하면 **F7 완료**, [F7.5 (AK09916 mag)](F7.5_VERIFICATION.md) 또는 F8 (통합·watchdog·status·battery) 진행.

---

*문서 끝.*
