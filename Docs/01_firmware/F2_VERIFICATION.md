# F2 — 모터 개방루프 PWM 검증

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-004 |
| 단계 | F2 (펌웨어 개발 3단계) |
| 대상 | STM32F405RGTx + AM2861 H-브리지 × 2 |
| 목적 | 양쪽 모터의 정·역회전 동작과 PWM 클램프(80%)·주파수(20kHz) 확인 |
| 전제 | **휠 받침대(공중)** 상태. 모터·드라이버 전원(12V) 인가 |

---

## 1. F2 단계 추가/변경 사항

### 1.1 PWM 주파수 — 20 kHz 재튜닝
[`App/drivers/am2861_driver.c`](../../firmware/rover_jupiter_fw/App/drivers/am2861_driver.c):
- `motor_driver_init()` 에서 `__HAL_TIM_SET_AUTORELOAD` 로 ARR 런타임 override.
  - TIM1 (168 MHz) ARR=8399 → 20 kHz, 8400 step 듀티 해상도
  - TIM3 ( 84 MHz) ARR=4199 → 20 kHz, 4200 step 듀티 해상도
- 듀티 → CCR 변환에 채널별 ARR 사용 (`duty_to_ccr(abs, arr)`)
- CubeMX 생성 `tim.c` 는 건드리지 않음 (재생성에도 안전)

### 1.2 안전 클램프 (F1 시점 이미 driver에 포함)
- `MOTOR_DUTY_MAX = 0.80` — 절댓값 초과 듀티는 0.80 으로 캡

### 1.3 자동 시퀀스 태스크
[`App/app/f2_motor_test.c`](../../firmware/rover_jupiter_fw/App/app/f2_motor_test.c):

| 단계 | L 듀티 | R 듀티 | 시간 |
|---|---|---|---|
| start in 3s | 0 | 0 | 3000 ms |
| fwd 10% | +0.10 | +0.10 | 2000 ms |
| stop    | 0    | 0    | 1000 ms |
| rev 10% | -0.10 | -0.10 | 2000 ms |
| stop    | 0    | 0    | 1000 ms |
| fwd 20% | +0.20 | +0.20 | 2000 ms |
| stop    | 0    | 0    | 1000 ms |
| rev 20% | -0.20 | -0.20 | 2000 ms |
| stop (영구) | 0 | 0 | ∞ |

총 시퀀스 길이 ≈ 15초. 종료 후 모터 영구 정지.

f1SanityTask 와 병렬 동작 → 1Hz 로 엔코더 카운트 계속 dump.

---

## 2. 검증 절차 (사용자 실측)

### 2.1 안전 확인
- [ ] 휠이 바닥에 닿지 않는 받침대 위
- [ ] 양쪽 휠 회전 경로에 손/케이블/장애물 없음
- [ ] 비상시 전원 차단 스위치 손 닿는 위치
- [ ] UART5 콘솔 띄움 (115200, 8N1)

### 2.2 플래시 후 콘솔 관찰

기대 출력 (대략, 타이밍 순서):
```
========================================= (부팅 배너)
[F1-i2c1 scan] (none)
[F1-i2c2 scan] (none)
[F1-init] motor=OK enc=OK imu=OK(whoami=0xEA) mag=SKIP(...) adc=OK(...)
[F2] start in 3s — 휠 받침대 상태 확인
[F1    1] enc L=+0 R=+0  ...
[F1    2] enc L=+0 R=+0  ...
[F1    3] enc L=+0 R=+0  ...
[F2] fwd 10%  L=+0.10 R=+0.10
[F1    4] enc L=+XXX R=+XXX  ...     ← 카운트 증가
[F1    5] enc L=+XXXX R=+XXXX  ...
[F2] stop
[F1    6] enc L=+XXXX R=+XXXX  ...   ← 정지 후 같은 값 유지
[F2] rev 10%  L=-0.10 R=-0.10
[F1    7] enc L=+XXX R=+XXX  ...     ← 카운트 감소 (음수 방향)
...
[F2] sequence done — motors stopped, monitor encoder counts
```

### 2.3 체크 항목

| # | 항목 | 통과 조건 | 실패 시 |
|---|---|---|---|
| 1 | PWM 주파수 | 휘파람 소리(가청대) 없거나 매우 작음 | TIM ARR 설정 확인 |
| 2 | `fwd 10%` 시 회전 방향 | **두 휠 같은 방향** (전진) | 한쪽 반대면 → driver의 LEFT/RIGHT 또는 IA/IB 매핑 반전 |
| 3 | `fwd 10%` 시 엔코더 부호 | **L·R 둘 다 같은 부호로 증가** | 한쪽 반대 부호면 → encoder IC1/IC2 polarity 반전 (F3에서) |
| 4 | `rev 10%` 동작 | 두 휠 반대로 회전, 엔코더 부호 반대 | 동일 검토 |
| 5 | `fwd 20%` vs `fwd 10%` | 회전 속도 약 2배 (선형) | PWM duty → 속도 변환 비례 |
| 6 | 시퀀스 종료 후 | 모터 완전 정지, 콘솔 `sequence done` | E-stop 없이도 정지 유지 |
| 7 | F1SanityTask 1Hz dump | 끊김 없음, freeHeap 안정 | 스택/heap 검토 |

### 2.4 매핑·극성 이슈 정리 (있는 경우)
실측 결과 다음 중 하나가 발견되면 driver 또는 encoder 설정 보정 필요:

- **두 휠이 반대 방향으로 회전** (전진 시 한쪽만 전진, 다른쪽 후진)
  → `am2861_driver.c` 의 한쪽 모터 IA/IB 스왑. 또는 LEFT/RIGHT 잠정 매핑(M1↔M3) 반전.
- **한쪽 엔코더 카운트만 반대 부호**
  → F3 단계 작업이지만, 메모해두고 F3에서 한쪽만 `IC1Polarity = Falling` 변경.
- **양쪽 다 회전했는데 엔코더 카운트 변화 없음**
  → 엔코더 라인 결선·풀업 점검.

→ 이슈가 있으면 콘솔 출력 그대로 알려줘.

---

## 3. F2 완료 기준 (Definition of Done)

- [ ] 시퀀스 4단계(±10%, ±20%) 모두 동작
- [ ] 두 휠 전진 시 같은 방향, 후진 시 반대 방향 (= 양쪽 같이 후진)
- [ ] 양쪽 엔코더 카운트 부호가 회전 방향과 일관
- [ ] 시퀀스 후 모터 완전 정지
- [ ] LEFT/RIGHT ↔ M1/M3 매핑 확정 (필요 시 반전 적용)

→ 통과하면 **F2 완료**, F3(엔코더 속도 산출) 진행.

---

## 4. 알려진 한계 / 의도된 미구현

- **속도 제어 없음** — 듀티만 인가. 부하/배터리 전압에 따라 회전 속도 가변. 속도 PID 는 F4.
- **스톨 감지 없음** — 받침대 상태라 무부하 가정. 스톨 감지는 F4.
- **Watchdog 없음** — F2 코드가 정지 후 영구 대기. `/cmd_vel` 500ms watchdog 은 F5(micro-ROS 통합) 이후 F8.
- **방향 매핑** — 잠정값 (M1=LEFT, M3=RIGHT). F2 실측 결과로 확정.

---

*문서 끝.*
