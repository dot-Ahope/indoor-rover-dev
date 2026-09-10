# 2026-09-10 — S1 완주. 관측 도구가 관측 대상을 망가뜨리고 있었다

## 0. 이 날의 결론

**회피 주행 완주 + 마킹 전 구간 유지 + 계획 접촉 0% + 조향 진동 0** 을 동시에 달성했다.
결정적이었던 것은 파라미터가 아니라 **Foxglove Studio 클라이언트 연결을 끊은 것**이다.

## 1. S6 기준선 — 깨끗한 부팅에서는 이미 충족

젯슨 재부팅 직후 Nav2 포함 30초 측정:

```
EKF 주기 위반 : 0 회 / 30초   (종료조건 0)  ✅
slam 스캔 폐기: 0 회 / 30초   (종료조건 0)  ✅
load 2.10                     (종료조건 <6) ✅
CPU: rplidar 19.5 / realsense 15.3 / controller 14.8 / python3 14.7 / ekf 12.7
```

**09-09 의 "CPU 부족이 구조적" 이라는 결론은 틀렸다.** 어제 값(load 8~9, EKF 위반 91회,
python3 44%)은 긴 세션 동안 재기동을 수십 번 반복하며 쌓인 **열화**였다. S6 는 마진 확보
가치는 있으나 최우선은 아니다 — 우선순위를 낮춘다.

## 2. decay_acceleration — 장면 의존성을 없앴다 (job183 → job184)

job183 에서 또 접촉했다. 시계열:

```
t=5 깊이점 174 lc_box 100 → t=6 깊이점 0 lc_box 100 → t=8 lc_box 0 (2~3초 만에)
t=11 깊이점 423 lc_box 100 (다시 보이자 복구) → t=14 lc_box 0
```

`voxel_decay 30` 인데 2~3초 만에 사라진다. t=8 시점 카메라~상자 중심은 **0.580 m** 로
`min_z 0.55` 를 **넘어** 절두체 '안' 이었고, 가속 감쇠가 지웠다.

**핵심: 깊이점이 끊기는 거리가 장면마다 다르다.** 09-09 는 0.45~0.51 m, 오늘은 0.65 m.
심지어 job183 t=10~12 에는 116 → 423 → 44 로 되살아났다 사라졌다 한다.
**`min_z` 를 한 값으로 맞추는 접근 자체가 취약하다** — 09-09 에 0.25→0.55 로 올린 것도
그 장면에서만 맞았던 것이다.

**조치**: `decay_acceleration` 3.0 → **0.0**. 절두체 안팎을 가리지 않고 모두 `voxel_decay`
동안 균일 유지 → '관측이 끊기면 30초 유지' 규칙이 장면에 의존하지 않는다.
대가: 치운 물체도 최대 30초 남는다(0.08 m/s 로 2.4 m 이동분, 로컬 3×3 m 롤링이라 지나가면 소멸).
동적 망각 튜닝은 S3 에서 따로 한다.

**결과(job184)**: 로컬이 상자를 잃은 샘플 147 → **12**, 계획이 접촉 경로였던 비율 48% → **0%**,
실제 최근접 0.0 → **45.6 cm**.

## 3. stuck_monitor — Nav2 액션 상태는 전이 시점에만 발행된다

job184 는 접촉 없이 진행했으나 0.92 m 에서 CANCELED 됐다.

```
RegulatedPurePursuitController detected collision ahead! → follow_path 중단
behavior_server: Running backup → "backup completed successfully"   ← 복구는 성공
stuck_monitor: 지령 11.2cm/9° 인데 관측 1.4cm/6.0° (비율 0.13) → 목표 취소
```

**복구가 성공한 직후 stuck_monitor 가 취소했다.** 09-09 에 넣은 억제 로직이 막았어야 했다.

원인: **Nav2 액션 서버는 상태를 전이 시점에만 발행한다**(연속 발행이 아니다).
`EXECUTING` 을 받을 때마다 `recovery_until = now + W(2.0s)` 로 갱신하는 방식이었는데,
후진 복구가 4.5초 걸려 보류 창이 복구 도중 만료됐다.

```
backup 시작(EXECUTING) 994.3 → recovery_until 996.3
backup 완료            998.8   (그 사이 EXECUTING 재발행 없음)
stuck 발동            1000.17  ← 이미 만료
```

**조치**: `recovery_active` 플래그 도입 — EXECUTING 이면 세우고, 종료 상태(4/5/6)를 받으면
내린 뒤 W 만큼 더 보류한다. 판정은 `recovery_active or now < recovery_until` 일 때 건너뛴다.

> 중간에 `ros2 node info /stuck_monitor` 의 구독 목록에 상태 토픽이 없어 "구독 자체가 안 됐다"
> 고 판단했으나 **오독**이었다. `_` 로 시작하는 숨김 토픽은 기본 출력에서 빠진다.
> `ros2 topic info /backup/_action/status` → `Subscription count: 1` 로 확인.

## 4. ★ 진짜 병목 — Foxglove 클라이언트 연결

stuck_monitor 를 고쳐 재기동했는데 Nav2 가 **기동 실패**했다.

```
planner_server 는 설정 성공(플러그인 전부 초기화, 코스트맵 리사이즈 완료)
lifecycle_manager: Failed to change state for node: planner_server.
                   Exception: planner_server/get_state service client: async_send_request failed.
load 6.35, EKF 위반 86회, slam 폐기 28회
```

설정 오류가 아니라 **부하 상태에서 서비스 응답이 늦어 생긴 타임아웃**이다.
CPU 상위를 보니 `foxglove_bridge` 69.6% — 부팅 직후엔 상위권에 없던 것이다.

```
ss -tn | grep :8765
  ESTAB  192.168.0.101:8765  ←  192.168.0.6:65351     ← 사용자 PC 의 Foxglove Studio

foxglove_bridge 정지 후 30초 재측정:
  EKF 주기 위반 : 0 회  (직전 86회)
  slam 스캔 폐기: 0 회  (직전 28회)
  Nav2 전 노드 active   (직전 기동 실패)
```

`viz:=lean` 으로 토픽을 줄여도 **클라이언트가 붙으면** 브리지가 1코어 가까이 쓴다.
09-09 주행 중 Foxglove 로 경로를 보고 있던 것이 EKF 를 굶겨 TF 를 끊고 주행을 망친
인과에 포함된다 — **관측 도구가 관측 대상을 망가뜨리고 있었다.**

**운용 규칙**: 측정 주행 중에는 Foxglove Studio 창을 닫는다(또는 브리지를 내린다).

## 5. job192 — S1 완주

```
결과 SUCCEEDED   주행 1.92m   소요 38.4s
③ lc_box/gc_box 최소 99 — 깊이점 0 인 채로 전 구간 유지
② 계획이 접촉 경로였던 샘플 0/385 (0%)
④ 경로 좌우 전환 0회
   조향 부호반전 0회/m,  직진 중 |ω| 평균 0.039 최대 0.111 rad/s
① 실제 최근접 3.3 cm — 접촉 없음
```

t=11~14 에 후진 복구가 한 번 들어갔으나 **stuck_monitor 가 취소하지 않고 이어서 완주**했다 —
§3 의 수정이 실주행에서 검증됐다.

### S1 종료 조건 대비

| 조건 | 결과 |
|---|---|
| 상자를 완전히 지날 때까지 `lc_box` 유지 | ✅ 최소 99 |
| 실제 최근접 ≥ 5 cm | ❌ **3.3 cm** |

마킹 유지는 달성했고 여유 기준만 미달이다. 이번 통로가 좁았다(상자 y −0.40~−0.10,
좌측 벽 +0.40). 여유 있는 배치에서 반복 확인이 필요하다.

## 6. 미완 / 다음

- **S1 반복 검증** — 여유 있는 배치에서 최근접 ≥ 5 cm 확인. 3회 연속(S4 와 통합 가능).
- **S2 카메라 사각지대 축소** — `decimation_filter 4` 재검토. 깊이점 끊김 거리를 줄이면
  `min_z` 의존성도 함께 줄어든다.
- **S3 동적 망각** — `decay_acceleration 0` 의 대가를 측정하고 필요하면 되살린다.
- **S6 CPU** — 우선순위 하향. 다만 **세션 열화는 실재**하므로 측정 주행 전에는
  스택을 깨끗이 재기동하고, Foxglove 를 끈다.
