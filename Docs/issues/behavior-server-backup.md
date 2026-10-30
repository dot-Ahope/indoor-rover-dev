# behavior_server BackUp — map 프레임 버그와 첫 1 s 의 엇갈린 지령

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결**(두 원인 확인 + 조치 + 실주행 확인: 09-11 §5.15 ret1 BackUp 2/2 성공, §5.16 `backup failed` 0) — 근본 구조(behavior 가 smoother 를 거치지 않음)는 남음 | 09-11 §5.12 ~ §5.15 (이 카드), 앞선 증상 09-03 · 09-10 · 09-11 낮 | [09-11 §5.12](../debug_log/2026-09-11/SUMMARY.md)(사용자 질문 "서로 다른 명령을 내리는 부분이 있는가") | `ros2_ws/src/rover_navigation/config/nav2_params.yaml` — `behavior_server.global_frame: map → odom`, `velocity_smoother.velocity_timeout: 1.0 → 0.3` | [RPP vs MPPI](controller-rpp-vs-mppi.md)(컨트롤러 중단 → BackUp 전환) · [stuck_monitor](stuck-monitor.md)(세 번째 `/cmd_vel` 발행자) · [코스트맵 클리어](costmap-clear-recovery.md)(BackUp 은 클리어 다음 복구) · [회피 계측 실수 ⑥](avoid-run-metrics.md)(같은 종류의 프레임 오류) · [라이다 근접 사각](near-wall-blindspot.md)(09-03 BackUp 거부) |

**한 줄**: BT 복구의 BackUp 이 두 가지로 망가져 있었다. ① **품질** — 컨트롤러가 멈춘 뒤 `velocity_smoother` 가 `velocity_timeout`(1.0 s) 동안 0 을 계속 내보내, BackUp 첫 1 s 에 smoother 의 0(20 Hz)과 behavior_server 의 −0.05(10 Hz)가 번갈아 나갔다(사용자가 본 "멈춤과 진행이 동시"). `velocity_timeout` 0.3 으로 겹침 제거(합성 A/B 확정). ② **작동 자체** — `behavior_server.global_frame: map` 이라 behavior 가 map 자세로 footprint 를 만들어 **odom 프레임** `costmap_raw` 위에서 검사했다. map→odom 보정만큼(그때 29 cm) 어긋난 자리를 보니 이동량과 무관하게 모든 위치가 LETHAL → BackUp 이 양방향 모두 0.0 s 에 "Collision Ahead" 로 실패. `odom` 으로 바꾸자 즉시 성공. 재기동 직후(보정 ≈ 0)엔 되고 드리프트가 쌓이면 `backup failed → Wait 5 s` 가 되던 이날의 패턴이 이것으로 설명된다.

---

## 1. 증상
- 사용자(09-11 §5.12): BackUp 때 로버가 멈춤과 진행을 동시에 하는 듯 더듬거림 → "서로 다른 명령을 내리는 부분이 있는가".
- 이날 회차들에 `backup failed` 가 일상: job222 4 건(09-11 §3 표), s4r3 · job224/227 · 복귀 실패(§5.14 '오늘 마지막에 남는 것'). 반면 s4r2(재기동 직후) BackUp 2 회 성공.
- 합성 시험(§5.14): BackUp 액션이 **0.0 s 에 "Collision Ahead"** 로 실패 — 앞 · 뒤 양방향 모두. 그런데 `costmap_raw` 미지(255) 0 %, footprint 둘레 최대 253(LETHAL 아님).
- 앞선 같은 증상: 09-03 RPP Run 2 에서 BackUp 이 `Collision Ahead` 로 거부됨(원인 미확인으로 남음 — [라이다 근접 사각 §4](near-wall-blindspot.md)).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-03 | RPP Run 2 | BackUp 이 `Collision Ahead` 로 거부 | 원인 미확인 | 09-03 SUMMARY, [Nav2 카드](nav2-first-setup.md) |
| 09-10 §3 | job184 | `behavior_server: Running backup → backup completed successfully` | (BackUp 은 됐다 — 그날 map→odom 크기는 기록 없음) | 원천 소실 |
| 09-11 §3 | job222 → job231(BT 수정 · 재기동 뒤) | `backup failed` 4 → 0 건 | BT 수정의 효과로 표에 함께 적힘 — **실제로는 재기동으로 map→odom 이 작아진 효과일 수 있음**(§6 모순 ①) | 원천 소실 |
| 09-11 §5.12 | `job277_cmdvel.py` · `job278_pubs_jp.py` · `job279_interleave.py` — 발행자 · bag_s4r2 시계열 | `/cmd_vel` 발행자 셋: `velocity_smoother`(컨트롤러 → `/cmd_vel_nav` → smoother), `behavior_server`(spin · backup · drive_on_heading · wait), `stuck_monitor`(취소 때 0 × 10, 주기 발행 아님). bag_s4r2 `/cmd_vel` 849 개 · 52.9 s | — | bag_s4r2 **소실**(09-14 재부팅) |
| §5.12 | 첫 판정 | '10 ms 미만 간격 0 개 → 충돌 없음' | **틀림**(실수 ①) | 원천 소실 |
| §5.12 | 100 ms 창당 메시지 수로 다시 봄 | 9.20 +0.03 · 9.25 +0.01 · 9.30~9.75 0.00(smoother 감속 램프, 단일) → **9.76 −0.05 · 9.80 0 · 9.85 0 · 9.86 −0.05 · 9.90 0 … 10.66 −0.05**(창당 3 개: 0 @ 20 Hz + −0.05 @ 10 Hz) → 10.77~ 깨끗한 후진(창당 1) → 13.96 0.00 · 14.05 +0.01 … 14.55 +0.08(전진 재개 단일). 두 번째 BackUp(22.76)도 동일 | BackUp 첫 1.0 s = smoother 의 `velocity_timeout` 동안의 0 스트림과 behavior 의 후진이 맞물림 → 보드는 마지막 지령을 따르므로 1/3 듀티 더듬 후진 | SUMMARY 원문 표 |
| §5.12 | `velocity_timeout` 1.0 → **0.3**(BT 전환 0.45 s 보다 짧게) | 적용, 미검증 | 근본 해결은 twist_mux(Humble behavior 는 smoother 를 안 거침)지만 한 줄로 되는지 먼저 | `nav2_params.yaml` 주석 |
| §5.12 | 통로 정지 자체의 원인 | 정정된 로컬 LETHAL 센서 근거 100 % | 멈춤은 유령 띠(도구 오류) 때문이 아니라 RPP 충돌 검사가 실제 장애물 셀에 닿은 것. 정지 → 후진은 설계된 BT 순서, 맞물림은 그 후진의 *품질* 문제 | — |
| §5.14 | `job282_ab_timeout.py` 합성 재현 시도 | BackUp 이 양방향 0.0 s 실패 | 비용이 아니라 다른 경로 → 조사 | 원천 소실 |
| §5.14 | `job284_raw.py` — `costmap_raw` 둘레 raw 값 | 255 **0 %**, 둘레 최대 253 | 미지 셀 가설 기각 | 원천 소실 |
| §5.14 | `job285_behavior.py` — 같은 footprint 를 odom 자세 vs map 자세로 Bresenham 순회 | odom 자세: 이동 0 · +0.05 · +0.10 · +0.15 · −0.05 · −0.10 · −0.15 둘레 최대 **253 253 253 253 253 253 246**. map 자세(behavior 현재): **254 × 7 전부**. 그때 map→odom (−0.107, +0.275) = 29 cm | 프레임 버그 확정. Nav2 bringup 예제도 behavior_server 는 `odom`. 내 진단 도구가 저녁에 범한 것과 같은 종류의 오류가 설정에 있었음 | 원천 소실(값은 `nav2_params.yaml` 주석에도 기록) |
| §5.14 | `global_frame: odom` 배포 | BackUp **SUCCEEDED 3.3 s / 4.3 s** | 고쳐짐 | — |
| §5.14 | `job282` A/B(BackUp 이 살아난 뒤) | A(0.3): `0.00:−0.05 0.00:+0.00 \| 0.10:−0.05 0.20:−0.05 0.30:−0.05 …` — 첫 100 ms 경계에 0 하나, 이후 10 Hz 후진만. B(1.0): `0.00:−0.05 0.00:+0.05 0.05:+0.05 0.10:−0.05 0.10:+0.05 …` — 1 s 내내 ±0.05 교대(100 ms 당 4 개). BT 전환 0.41~0.45 s | **0.3 은 겹침이 사라지고 1.0 은 재현 → 확정.** smoother 는 입력이 끊기면 *마지막 명령*을 timeout 동안 반복(합성은 마지막이 +0.05 라 B 는 ±0.05 교대, 실주행은 컨트롤러가 중단 때 0 을 내므로 0/−0.05 교대 — bag_s4r2 와 일치). 자동 판정은 '0 이 정확히 0 개' 기준이라 경계 메시지 하나에 '보류' — 기준이 과했음(실수 ②) | 원천 소실 |
| §5.15 | 복구가 살아난 뒤 코스 + 복귀 | ret1: 충돌 10 · **backup 2/2 성공** · wait 2(ABORTED 는 목표 기하) | `global_frame: odom` 이 실주행에서 작동(그 전엔 `backup failed` 가 일상) | [통과 폭 카드 §2](passage-width-analysis.md) |
| §5.16 | v1 · v2 | `backup failed` 0 | 복구 작동 | `outputs/v1.csv` · `v2.csv`(러너 CSV — BackUp 집계는 nav2.log, 원천 소실) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| BackUp 때 두 발행자가 엇갈린 지령을 낸다 | bag_s4r2 100 ms 창당 메시지 수 | BackUp 첫 1 s 창당 3 개(0 과 −0.05), 그 뒤 1 개 | **지지(측정)** |
| 엇갈림은 smoother 의 `velocity_timeout` 동안의 출력 | `job282` A(0.3) / B(1.0) 합성 | A 겹침 없음 · B 재현 | **지지(측정)** |
| BackUp 즉시 실패는 footprint 둘레의 미지(255) 셀 | `job284` raw 둘레 | 255 0 %, 최대 253 | **기각** |
| BackUp 즉시 실패는 behavior 의 자세 프레임(map) | `job285` odom vs map 자세 순회 | odom 253(통과) · map 254 × 7(전부 충돌) | **지지(측정)** + 수정 뒤 성공 |
| 이날의 `backup failed` 회차는 진짜 막힘이었다 | 위 버그의 시간 의존성(재기동 직후 성공 · 드리프트 뒤 실패) | s4r2(재기동 직후) 성공, 드리프트 쌓인 회차 실패 | **재해석 필요**(§5.14) — s4r3 · job224/227 · 복귀 실패의 '복구 불능' 판정은 이 버그 위에서 난 것. 복구가 작동했다면 결과가 달랐을 수 있음(**미확인**) |
| 09-03 RPP Run 2 의 BackUp 거부도 같은 버그 | 09-03 의 map→odom · 설정 기록 | 그날 `global_frame` 값 · 보정량 기록 없음 | **미확인**(서명은 같음: 'Collision Ahead' 즉시 거부) |

## 4. 조치와 효과
| 바꾼 것 | 전 → 후 | 효과 | 한계 |
|---|---|---|---|
| `behavior_server.global_frame` | map → **odom** | BackUp 3.3 · 4.3 s 성공, ret1 2/2, v1 · v2 `backup failed` 0. 지금도 odom(`nav2_params.yaml` L819 부근 주석에 job285 수치) | behavior 의 이동 판정이 odom 기준 — 미끄러짐은 못 봄(회전 미끄러짐 줄기와 같은 한계) |
| `velocity_smoother.velocity_timeout` | 1.0 → **0.3** | BackUp 첫 1 s 겹침 사라짐(A/B). 지금도 0.3 | 근본 구조는 그대로 — Humble behavior 는 smoother 를 거치지 않고 `/cmd_vel` 에 직접 씀. 경계에 0 하나는 남음. twist_mux 는 미도입 |

## 5. 내 실수
### 실수 ① '10 ms 미만 간격 0 개' 로 충돌 없음을 판정 (09-11 §5.12)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 두 발행자가 같은 순간에 `/cmd_vel` 을 내는지 bag 으로 확인(`job277`) |
| 본 것 | 연속 메시지 간격 10 ms 미만 0 개 |
| 처음 추론 | 두 스트림이 겹치지 않는다 → 충돌 없음 |
| 의심한 이유 | 사용자가 육안으로 더듬거림을 봄. 두 스트림이 50 ms 어긋나 맞물리면 최소 간격은 10 ms 밑으로 내려가지 않는다 |
| 판별 | 100 ms 창당 메시지 수(`job279`): 정상 1 개 vs BackUp 첫 1 s 3 개 |
| 결론 | 충돌 있음(0 과 −0.05 교대). `velocity_timeout` 0.3 |
| 다음에 알아보는 법 | 발행자가 여럿인 토픽의 엇갈림은 '간격 최소값' 이 아니라 **고정 창당 메시지 수**와 **값의 교대**로 본다. 발행 주기가 서로 배수(20 Hz · 10 Hz)면 간격은 늘 일정해 보인다 |
| 데이터 | bag_s4r2 **소실**, 도구 [`jobs/job277_cmdvel.py`](../debug_log/2026-09-11/jobs/job277_cmdvel.py)(간격 판정판) · [`job279_interleave.py`](../debug_log/2026-09-11/jobs/job279_interleave.py)(창당 개수판), 출력 원천 소실 — SUMMARY §5.12 표가 유일 |

### 실수 ② A/B 자동 판정 기준이 과함 (09-11 §5.14)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `job282` 가 스스로 '원인 · 수정 확정' 을 찍게 |
| 본 것 | A(0.3) 에 첫 100 ms 경계 0 메시지 하나 → 판정 '보류' |
| 처음 추론 | (도구 설계) A 는 '0 이 정확히 0 개 · 창당 최대 1' 이어야 한다 |
| 의심한 이유 | 시계열을 직접 보니 0 은 후진 시작 경계의 한 개뿐이고 이후 10 Hz 후진만 |
| 판별 | A · B 의 처음 14 개 메시지를 나란히 봄 |
| 결론 | 확정으로 기록(SUMMARY 가 '기준이 과했다' 를 남김) |
| 다음에 알아보는 법 | 자동 판정 문턱은 '경계 효과 1 개' 같은 정상 잡음을 허용하게 잡고, 판정과 함께 원시 시계열을 같이 찍는다 |
| 데이터 | 원천 소실, 도구 [`jobs/job282_ab_timeout.py`](../debug_log/2026-09-11/jobs/job282_ab_timeout.py) 판정 줄 `ok = ra['zeros'] == 0 and ra['mx'] == 1 …` |

### 실수 ③ (설정) behavior_server 를 map 프레임으로 둠 — 언제 · 왜 그렇게 됐는지 기록 없음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | (Nav2 첫 구축 때) behavior_server 설정 |
| 본 것 | BackUp 이 드리프트가 쌓이면 실패, 재기동 직후엔 성공 |
| 처음 추론 | 이날 낮엔 '복구 불능' · '진짜 막힘' 으로 읽음 |
| 의심한 이유 | 합성 시험에서 둘레 최대 253(충돌 아님)인데 0.0 s 실패 |
| 판별 | `job285` 프레임별 순회 · 수정 뒤 성공 |
| 결론 | 코스트맵(odom)과 자세(map)의 프레임 불일치 — 진단 도구의 실수 ⑥([계측 카드](avoid-run-metrics.md))과 같은 종류 |
| 다음에 알아보는 법 | 서명: **재기동 직후엔 되고 시간이 갈수록 안 됨** + 비용은 정상인데 충돌 판정. 코스트맵을 읽는 모든 노드 · 도구의 자세 프레임이 그 코스트맵의 `global_frame` 과 같은지 본다 |
| 데이터 | `nav2_params.yaml` behavior_server 블록 주석, 도구 [`job285_behavior.py`](../debug_log/2026-09-11/jobs/job285_behavior.py) |

## 6. SUMMARY ↔ 원문 모순
1. **09-11 §3 검증 표의 'backup failed 4 → 0'** 은 BT 수정 효과처럼 적혔지만, 같은 날 §5.14 에서 BackUp 실패의 원인이 map 프레임 버그(시간에 따라 map→odom 이 커지면 실패)로 밝혀졌다. job231 은 재기동 뒤라 보정이 작았을 가능성이 있다 — 0 건이 BT 수정 덕인지는 **미확인**.
2. **§5.14 표 머리 '이동 0 / ±0.05 / ±0.10 / ±0.15'** 와 값 7 개의 순서: 도구 출력 순서는 `0, +0.05, +0.10, +0.15, −0.05, −0.10, −0.15`(`job285` 코드). 246 은 −0.15(후진 0.15 m) 위치 값.
3. **§5.12 의 smoother 동작 설명**('0 을 계속 내보낸다')과 **§5.14**('마지막 명령을 timeout 동안 반복')는 같은 동작이다 — 실주행에서는 컨트롤러가 중단 때 마지막으로 0 을 냈기 때문에 0 이 반복된 것. 모순은 아니지만 §5.12 만 읽으면 기전을 오해할 수 있다.

## 7. 남은 것 (09-11 시점)
- twist_mux(또는 behavior 출력을 smoother 앞으로) — 미도입.
- 이날 `backup failed` 회차들(s4r3 · job224/227 · §5.11 복귀 실패)의 재해석 — 하지 않음.
- **이후(09-15 ~)**: 컨트롤러가 RPP → MPPI(09-15), BT 의 BackUp 자리는 10-15 우리 `MonotoneEscape` 플러그인(behavior_server 플러그인, BackUp 액션 형식, `backup_dist 0.30 · speed 0.03`)으로 바뀜(BT L122~126). 다음 시기 카드에서 채움.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| bag_s4r2 `/cmd_vel` | BackUp 첫 1 s 맞물림 | 09-11 §5.12, bag 소실 |
| 합성 BackUp · A/B | 프레임 버그 발견 · timeout 확정 | §5.14 |
| ret1 | 실주행 BackUp 2/2 | §5.15 |
| 도구 | `job277` · `job278` · `job279` · `job282` · `job284` · `job285` | 아래 §9 |

---

## 9. 도구 해설
공통 사항은 [계측 카드 §9.0](avoid-run-metrics.md). 모두 Jetson `/tmp`, 출력은 **원천 소실**(SUMMARY 수치만).

### 9.1 `job277_cmdvel.py` — 발행자 · 파라미터 · bag 시계열 (첫 판정판)
- [`jobs/job277_cmdvel.py`](../debug_log/2026-09-11/jobs/job277_cmdvel.py), 인자 없음. ① `/cmd_vel` · `/cmd_vel_nav` · `/cmd_vel_smoothed` 의 `ros2 topic info --verbose` 에서 발행자 노드(이 판은 `Publishers:` 줄을 찾음 — Humble 형식은 `Publisher count:` 라 비었을 수 있음, 그래서 job278 이 고침) ② smoother `velocity_timeout · max_decel · max_accel · smoothing_frequency · feedback · deadband_velocity`, controller 충돌 지평 ③ `rosbag2_py` 로 `/tmp/bag_s4r2` 의 `/cmd_vel` → 개수 · 평균 간격 · 간격 중앙 · **10 ms 미만 개수** · 1 s 초과 개수, 0.3 s 창 안에 +v 와 −v 가 같이 있는 구간, 후진 시작마다 직전 · 직후 값.
- 결함: 실수 ① 의 판정 방식. 계보: → job278 → job279.

### 9.2 `job278_pubs_jp.py` — Humble 형식 발행자 · 더듬거림 · N1 사실
- [`jobs/job278_pubs_jp.py`](../debug_log/2026-09-11/jobs/job278_pubs_jp.py). ① `Publisher count` / `Subscription count` 구간으로 발행자 · 구독자, `stuck_monitor` 발행 토픽 ② bag_s4r2 linear.x 부호를 구간(run)으로 묶어 1 s 미만 정지 중 앞뒤가 전진인 것(더듬거림) 개수 ③ **N1 사실 수집**: `/etc/nv_tegra_release`(L4T), `nvidia-jetpack` 버전, `/usr/local/cuda-*`, isaac apt 소스 · 패키지 수, 워크스페이스 nvblox 흔적, `tegrastats` GR3D, `free -m`. ③ 의 출력이 09-11 §5.13 '사실'(L4T R36.5.0 · Isaac 없음 · GPU 0 % · RAM 7.6 GB 중 5.9 GB 가용)의 출처로 보임(**추정** — SUMMARY 에 도구 이름 없음) → [클리어 카드 §2 §5.13 행](costmap-clear-recovery.md).

### 9.3 `job279_interleave.py` — 100 ms 창당 메시지 수
- [`jobs/job279_interleave.py`](../debug_log/2026-09-11/jobs/job279_interleave.py). bag_s4r2 `/cmd_vel` 의 세 창(9.2~11.2 · 22.2~24.2 · 13.8~14.6 s)을 `시각:값` 으로 8 개씩 찍고, `int(t·10)` 으로 묶은 100 ms 창당 메시지 수의 분포. 2 이상이면 두 스트림 맞물림. §5.12 표의 원천.

### 9.4 `job282_ab_timeout.py` — velocity_timeout 합성 A/B
- [`jobs/job282_ab_timeout.py`](../debug_log/2026-09-11/jobs/job282_ab_timeout.py) `[backup|drive]`. 실제 충돌을 기다리지 않고 같은 기전을 재현: ① 컨트롤러 흉내로 `/cmd_vel_nav` 에 +0.05 를 20 Hz 로 2.0 s → 끊음 ② 0.4 s 뒤(실측 BT 전환 0.45 s) `/backup`(또는 `/drive_on_heading`) 액션 0.15 m · 0.05 m/s · 허용 15 s ③ `/cmd_vel` 을 수신 시각으로 기록 → 중단 후 첫 행동 지령 시각 · smoother 마지막 0 시각 · 후진 첫 1 s 의 메시지 수 · 0 개수 · 100 ms 창당 최대 · 처음 14 개. A = 현재값, B = `ros2 param set … velocity_timeout 1.0`, 끝나면 0.3 복원 + readback. 판정 `A 0 개 · 창당 1 && B 0 > 0 · 창당 ≥ 2`.
- 쓰인 곳: §5.14 — 첫 실행에서 BackUp 이 0.0 s 실패해 프레임 버그를 끌어냄, 수정 뒤 A/B 확정.
- 결함: 판정 기준(실수 ②), 실행 중 파라미터를 바꿨다 되돌림(smoother 파라미터라 10-14 의 '패딩 토글 → MPPI 멈칫' 과는 다른 대상이지만 같은 방식). 지금 다시 쓰기: 기전 확인용으로 유효, 시험 뒤 재기동 권장.

### 9.5 `job284_raw.py` — costmap_raw 둘레 값
- [`jobs/job284_raw.py`](../debug_log/2026-09-11/jobs/job284_raw.py). `/local_costmap/costmap_raw`(`nav2_msgs/Costmap`, raw 0~255 — behavior 의 충돌 검사와 같은 데이터)를 TRANSIENT_LOCAL 로 받아, 그 격자 frame 의 로버 자세에서 footprint(+0.05) 네 변 13 점씩의 raw 값을 이동 0 · −0.05 · −0.10 · −0.15 · +0.10 · +0.20 마다 → 최대 · 변별 최대 · 255 개수, 전체 셀 중 255 비율. 이 도구는 **올바른 프레임**(격자 frame)으로 읽어서 '둘레 최대 253 인데 실패' 라는 모순을 드러냈다.

### 9.6 `job285_behavior.py` — 프레임 버그 판별
- [`jobs/job285_behavior.py`](../debug_log/2026-09-11/jobs/job285_behavior.py). ① nav2.log 의 behavior · collision · footprint · costmap 관련 ERROR/예외 마지막 8 줄 ② behavior_server `global_frame · robot_base_frame · transform_tolerance · local_costmap_topic · local_footprint_topic · simulate_ahead_time · cycle_frequency`, `published_footprint` 발행 · `costmap_raw` QoS ③ `costmap_raw` 위에서 footprint 폴리곤(반길이 0.30 · 반폭 0.215 네 꼭짓점)을 **Bresenham 으로 변을 따라 모든 셀** 순회(= Nav2 `FootprintCollisionChecker::footprintCost`), 꼭짓점이 격자 밖이면 254 'OFF-GRID'. (a) odom→base 자세, (b) map→base 자세(= behavior 가 실제로 하던 것) 각각 이동 7 개 위치. map→odom 현재값도 출력.
- 결과: §2 표의 253 × 6 · 246 vs 254 × 7. 계보: 이 순회 방식이 이후 코스트맵 판정 도구들의 기준.

## 10. 용어
- **behavior_server**: Nav2 복구 동작(Spin · BackUp · DriveOnHeading · Wait) 서버. 동작 중 직접 `/cmd_vel` 에 쓴다(Humble 에선 velocity_smoother 를 거치지 않음).
- **BackUp**: 지정 거리 · 속도로 직선 후진하는 복구. 매 주기 `simulate_ahead_time`(여기 2.0 s) 앞까지 footprint 를 투영해 충돌이면 "Collision Ahead" 로 중단.
- **global_frame(behavior_server)**: behavior 가 로봇 자세를 구하는 프레임. 충돌 검사 격자(`local_costmap/costmap_raw`)는 odom 이므로 둘이 같아야 한다.
- **costmap_raw**: 코스트맵의 raw 0~255 값을 그대로 담은 `nav2_msgs/Costmap` 토픽(발행용 OccupancyGrid 0~100 과 다름). 값 의미는 [통과 폭 카드 §10](passage-width-analysis.md).
- **velocity_smoother · velocity_timeout**: 컨트롤러 지령(`/cmd_vel_nav`)의 가감속을 제한해 `/cmd_vel` 로 내는 노드. 입력이 끊기면 마지막 지령을 `velocity_timeout` 동안 유지하다 감속 · 정지.
- **twist_mux**: 여러 지령원에 우선순위를 둬 하나만 내보내는 다중화 노드. 이 프로젝트엔 아직 없음.
- **BT 전환 시간**: FollowPath 실패 → BackUp 시작까지 0.41~0.45 s(실측, §5.14).
- **Bresenham 순회**: 두 격자 점 사이 직선이 지나는 셀을 빠짐없이 고르는 정수 알고리즘 — footprint 변 위의 모든 셀 비용을 본다.
