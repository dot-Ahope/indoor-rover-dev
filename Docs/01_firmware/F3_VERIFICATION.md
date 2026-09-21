# F3 — 엔코더 속도 산출 검증

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-005 |
| 단계 | F3 (펌웨어 개발 4단계) |
| 대상 | STM32F405RGTx + JGB37-520 + 직교 엔코더 (TIM2/TIM5) |
| 목적 | 카운트 → m/s 속도 변환 + EMA 저역통과 필터 정상 동작 확인, CPR 실측 검증 |
| 전제 | 휠 받침대 상태 (F2와 동일) |

---

## 1. F3 단계 추가/변경 사항

### 1.1 파일
- **신규** [`App/app/rover_platform.h`](../../firmware/rover_jupiter_fw/App/app/rover_platform.h)
  - 휠 반경·둘레·트랙 폭·엔코더 CPR·m/count 상수 격리
  - 양산기 이식 시 본 헤더만 교체
- **추가** `encoder_update_velocity()`, `encoder_read_velocity_mps()` —
  [`App/hal/i_encoder.h`](../../firmware/rover_jupiter_fw/App/hal/i_encoder.h),
  [`App/drivers/stm32_encoder_driver.c`](../../firmware/rover_jupiter_fw/App/drivers/stm32_encoder_driver.c)
- **추가** `tEncSample` FreeRTOS task (100Hz, AboveNormal 우선순위) —
  [`Core/Src/freertos.c`](../../firmware/rover_jupiter_fw/Core/Src/freertos.c)
- **수정** [`App/app/f1_sanity_task.c`](../../firmware/rover_jupiter_fw/App/app/f1_sanity_task.c) —
  1Hz dump 에 `v L= R= mm/s` 추가

### 1.2 속도 산출 알고리즘
```
ΔCNT = CNT_now − CNT_prev    (int32_t, modulo-2^32 wrap 안전)
v_raw = ΔCNT × METERS_PER_COUNT / Δt        [m/s]
v_filt = α × v_raw + (1−α) × v_filt_prev    (EMA 1차)
```
- 샘플 주기 Δt = 10 ms (100 Hz)
- α = 0.2 → 시정수 ≈ 40 ms (디지털 IIR)
- METERS_PER_COUNT = 0.1571 / 1320 ≈ 0.119 mm/cnt

콘솔에서 mm/s 정수로 표시 (newlib-nano `%f` 미지원 회피).

---

## 2. 사용자 검증 절차

### 2.1 자동 시퀀스 관찰
F1 sanity 1Hz dump 가 다음 형식으로 출력:
```
[F1   NN] enc L=±XX R=±XX  v L=±NNNmm/s R=±NNNmm/s  adc=XXXX  freeHeap=XXXX
```

F2 자동 시퀀스가 도는 동안 다음 값들이 보여야 함 (이전 F2 실측 기반 예상):

| F2 phase | 예상 v_L (mm/s) | 예상 v_R (mm/s) | 비고 |
|---|---|---|---|
| L fwd 50% | **+200 ~ +260** | 0 | ≈ 1800 cnt/s × 0.131 mm |
| L rev 50% | -150 ~ -200 | 0 | 비대칭은 F2 에서도 관찰됨 |
| R fwd 50% | 0 | 0 ~ +10 | 정지마찰 미통과 |
| R fwd 70% | 0 | **+300 ~ +380** | ≈ 2680 cnt/s × 0.131 mm |
| fwd 50% 양쪽 | +200 ~ +260 | ≈ 0 | RIGHT 50% 안 돔 |
| rev 50% 양쪽 | -150 ~ -200 | ≈ 0 | |

### 2.2 체크 항목

| # | 항목 | 통과 조건 | 실패 시 |
|---|---|---|---|
| 1 | 정지 시 v = 0 | 모터 stop 후 ≤ 200ms 안에 ±10 mm/s 이하 수렴 | EMA α 조정 / 샘플 주기 확인 |
| 2 | 듀티 ↗ 시 v ↗ | 50% → 70% 로 갈 때 v 도 증가 | 속도 산출 부호·매핑 확인 |
| 3 | 부호 일관 | 전진 시 v > 0, 후진 시 v < 0 (양 휠 모두) | 엔코더 driver 부호 보정 |
| 4 | 좌·우 분리 | L 만 회전 시 v_R ≈ 0, R 만 회전 시 v_L ≈ 0 | encoder 채널 매핑 검토 |
| 5 | 필터 노이즈 | 정상 회전 중 v 가 ±5% 이내로 안정 | α 너무 크면 노이즈, 작으면 lag |

### 2.3 CPR 실측 검증 (수동 — 선택)

dev plan §2.2 의 1320 CPR (출력축, ×4 quadrature 포함 가정) 이 맞는지 확인:

1. 모든 모터 정지 상태 (시퀀스 종료 후 또는 리셋 직후)
2. 휠 한쪽을 손으로 **정확히 1바퀴** 회전
3. 콘솔 `enc L=` 또는 `enc R=` 값 확인

- ≈ **±1320** → 가정 정확. `rover_platform.h` 수정 불필요.
- ≈ **±5280** → 4× 차이. `ENCODER_CPR` 을 5280 으로 수정 후 재빌드.
- 그 외 값 → 다른 CPR. 실측 값으로 `ENCODER_CPR` 갱신.

> 회전 정확도는 휠의 시작/끝 인덱스 마크로 ±5% 가능. 100 카운트 단위 차이는 ×4 quadrature 여부로 거의 결정됨.

---

## 3. F3 완료 기준 (Definition of Done)

- [ ] F2 시퀀스 도는 동안 `v L=` `v R=` 값이 카운트 변화와 일관되게 표시
- [ ] 정지 후 속도가 200ms 안에 0 근방 수렴
- [ ] 정·역회전에 따른 부호 반전 확인
- [ ] CPR 실측 (위 2.3) — 값에 따라 `ENCODER_CPR` 조정
- [ ] 100Hz sampler task 가 디버그 콘솔에서 stack overflow 등 이상 없이 동작 (freeHeap 안정)

→ 통과하면 **F3 완료**, F4(폐루프 속도 PID + 스톨 감지) 진행.

---

## 4. 알려진 한계 / 의도된 미구현

- **저속 양자화**: 100Hz 샘플 + 0.131mm/cnt → 1cnt/sample = 13 mm/s. 매우 저속(<13 mm/s)에서 양자화 노이즈 큼. F4 PID 또는 odometry 적분(F6)에서 누적으로 완화.
- **CPR 가정**: 1320 (출력축, ×4 quadrature 포함). 위 2.3에서 실측 검증 필요.
- **단순 EMA**: 변속 시 lag 약 40ms. 필요 시 F4에서 가중치 조정 또는 더 복잡한 필터(Kalman 등) 검토.
- **물리 단위 검증 없음**: 휠 둘레·반경은 `Docs/02_hardware/rover.urdf` 신뢰. 실제 휠 측정으로 보정은 차후.

---

*문서 끝.*
