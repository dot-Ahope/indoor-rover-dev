# F4 — 폐루프 속도 PID + 스톨 감지 검증

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-006 |
| 단계 | F4 (펌웨어 개발 5단계) |
| 대상 | STM32F405 + AM2861 + JGB37-520 |
| 목적 | 좌·우 휠 속도 PID 추종 + 스톨 감지 동작 확인 |
| 전제 | **휠 받침대 상태** (steady 구간에서 휠 손으로 막는 stall 테스트 포함) |

---

## 1. F4 추가/변경 사항

### 1.1 새 파일
- [`App/app/speed_controller.{h,c}`](../firmware/rover_jupiter_fw/App/app/) — per-wheel PID
- [`App/app/safety_monitor.{h,c}`](../firmware/rover_jupiter_fw/App/app/) — 스톨 감지 + latching fault
- [`App/app/f4_pid_test.{h,c}`](../firmware/rover_jupiter_fw/App/app/) — step response 시퀀스

### 1.2 PID 설계
```
err = target − actual
I  += Ki × err × dt   (clamp ±0.16)
duty = Kp × err + I + Kd × derr/dt
duty = clamp(±0.80)
```
초기 게인 (양쪽 동일):
- Kp = 4.0, Ki = 5.0, Kd = 0.0

특수 처리:
- **정지 명령** (|target| < 10 mm/s): 출력·적분 강제 0 — windup 방지
- **Dead-zone 보상**: target 방향과 일치하는 출력이 채널별 dead-zone 미만이면 dead-zone 으로 끌어올림
  - LEFT  dead-zone = 0.25 (F2 실측 ~30% 정지마찰)
  - RIGHT dead-zone = 0.55 (F2 실측 ~55% 정지마찰)
- **Brake 방향 출력**: dead-zone 미적용 — 적극 감속 허용

### 1.3 스톨 감지
- 조건: `|target| > 50 mm/s` AND `|actual| < 20 mm/s` 가 **200 ms 지속** (20 샘플 × 10 ms)
- 진입 시 동작: 양쪽 target=0, PID reset, motor_driver_stop_all
- Latching: `safety_monitor_clear()` 호출 전까지 fault 유지 (현재는 펌웨어 리셋만 가능)

### 1.4 통합 control 태스크
encSample 폐지. 새 `controlTask` (100 Hz, AboveNormal):
```
encoder_update_velocity → speed_controller_update → safety_monitor_update
```
같은 dt 안에 sequencing → PID 가 항상 최신 actual 사용, phase shift 최소.

### 1.5 F2 비활성
모터 매핑·방향 검증 완료(F2 DoD 통과)되었으므로 task 생성 비활성.
파일은 보존 (regression 필요 시 freertos.c 에서 task 다시 등록).

### 1.6 f1_sanity 출력 확장
```
[F1 NN] tgt L=±NNN R=±NNN  v L=±NNN R=±NNN (mm/s)  duty L=±NN% R=±NN%  dist L=±NNN R=±NNN (mm) [FAULT]
```

---

## 2. 검증 절차

### 2.1 안전 확인
- [ ] 휠 받침대 위, 회전 경로 비어있음
- [ ] 마지막 30 초 steady 구간에서 한쪽 휠 손으로 잡을 준비

### 2.2 시퀀스 구성 (총 약 1분 + 30초 steady)

| 구간 | target L | target R | 시간 | 관찰 포인트 |
|---|---|---|---|---|
| L 0.20 m/s | +200 | 0 | 3s | 200 mm/s 추종, 오버슈트, settling |
| L 0.40 m/s | +400 | 0 | 3s | 0.20 → 0.40 로 step 추종 |
| L stop | 0 | 0 | 1s | duty=0, v→0 |
| L -0.20 m/s | -200 | 0 | 3s | 후진 방향 동일 추종 |
| L stop | 0 | 0 | 1s | |
| R 0.20, 0.40, -0.20 | (R 만) | | 8s | 우측 동일 검증 |
| both ±0.30 m/s | ±300 | ±300 | 8s | 양쪽 균일성 (좌·우 비대칭 보완 확인) |
| both ±0.20 (방향 전환) | | | 5s | PID 안정성 (overshoot/oscillation) |
| **STEADY 0.20** | +200 | +200 | **30s** | **이 구간에서 한쪽 휠 손으로 잡기 → STALL 감지** |

### 2.3 체크 항목

| # | 항목 | 통과 조건 |
|---|---|---|
| 1 | 추종 정확도 | tgt 200 mm/s 명령 시 1초 안에 ±20 mm/s 이내 도달 |
| 2 | 오버슈트 | < 20% (예: tgt 200 → peak ≤ 240) |
| 3 | 정상오차 | 정상상태에서 ±5% 이내 |
| 4 | 부호 | tgt + 시 v +, tgt − 시 v − |
| 5 | 좌·우 균일성 | 동일 tgt 명령 시 v_L ≈ v_R (±10% 이내) |
| 6 | 정지 명령 | tgt=0 시 duty=0 즉시, v→0 1초 안 |
| 7 | Dead-zone | 작은 tgt(예: 100 mm/s) 명령 시 duty 가 dead-zone 위 |
| 8 | **STALL 감지** | steady 0.20 중 휠 잡으면 200~300 ms 안에 `[FAULT]` 표시 + duty=0 |
| 9 | Fault latching | STALL 후 휠 놔도 모터 재가동 안 됨 (펌웨어 리셋 필요) |

### 2.4 게인 튜닝 가이드 (필요 시)

| 증상 | 조정 |
|---|---|
| Settling 느림 | Kp ↑ (4.0 → 6.0) |
| 오버슈트 큼 | Kp ↓ 또는 Kd ↑ (0 → 0.05) |
| 정상오차 큼 | Ki ↑ (5.0 → 8.0) |
| 정상상태 진동 | Ki ↓ |
| 저속 추종 실패 | dead-zone 미세 조정 (`speed_controller.c` DEADZONE) |
| 좌·우 비대칭 | 채널별 Kp, Ki 분리 |

---

## 3. F4 완료 기준 (DoD)

- [ ] step response 추종 ±5% 이내 (정상상태)
- [ ] 양 휠 동시 명령 시 균일 회전
- [ ] STALL 감지 동작 + `[FAULT]` 표시
- [ ] 1분 시퀀스 + 30초 steady 동안 freeHeap 안정, 콘솔 끊김 없음
- [ ] 모터 brake 방향 출력 시 부드러운 감속 (덜컹임 적음)

→ 통과하면 **F4 완료**, F5(micro-ROS 통합 — `/cmd_vel` 구독) 진행.

---

## 4. 알려진 한계

- **게인 튜닝 미완**: 초기 추정값. 실측 후 조정 필요.
- **Kd = 0**: D 항 미사용. 진동 보이면 활성 (노이즈에 민감하므로 EMA 필터 후 derivative 권장).
- **Fault latching 해제 방법 없음**: 펌웨어 리셋만 가능. F8 에서 reset 명령 추가 예정.
- **Cmd_vel watchdog 미구현**: F8에서 추가.
- **Dead-zone 잠정값**: F2 1차 실측 기반. 배터리·온도에 따라 가변. 더 정교한 보상은 향후.

---

*문서 끝.*
