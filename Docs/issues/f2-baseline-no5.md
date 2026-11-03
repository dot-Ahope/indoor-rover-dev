# F2 순회 기준선 — no5 · b910, 6 회 중 3 회 합격 (7 기: 10-14 §12 · §13 · §26 · §27~§27.3, 10-15 §0~§4 · §14~§21 · §29.6)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **완료(기준선 수치 고정: 3/6)** · 기준선 문서(`BASELINE_F2.md`) · git 태그 · `TEST_COURSE_AND_GATES` F2 절은 **만들지 않음**(10-14 §26 계획에 있었음). ⚠ 판정 ⑥ 을 f2v2 결과를 본 **뒤에** 바꿨다(사용자 결정, 10-15 §17) — 옛 ⑥ 이면 2/6 | 10-14 §12(코스 그림) ~ 10-15 §21(정리), §29.6 f2w2 는 기준선 밖 같은 코스 주행 | [10-14 §26](../debug_log/2026-10-14/SUMMARY.md) '다음(추천) F2 순회 기준선 고정 — no5 3 회(매번 새 스택), 판정 기준 주행 전 선언' | 코드 변경 없음(구성 고정이 목적). 러너 목표 문자열 [`2026-10-14/jobs/run_f2c.sh`](../debug_log/2026-10-14/jobs/run_f2c.sh) 8 행 `NO5` → [`2026-10-15/jobs/run_f2c.sh`](../debug_log/2026-10-15/jobs/run_f2c.sh) 10 행 `HOMEW` 추가 · 12 행 기본 주소 192.168.0.110. 이름 되돌림(§27.3): [`fig_patrol_goals.py`](../tools/fig_patrol_goals.py) · [`fig_no5_route.py`](../debug_log/2026-10-14/jobs/fig_no5_route.py) · `run_f2c.sh` 주석 | [상자 옆 정지 원인](box-side-stall-cause.md)(세 실패의 기전 — 10-15 §5~§13 · §18.2 · §20.1 · §28) · [상자 옆 정지 대책](box-side-stall-remedies.md)(§21 다음 · §22~§30 — site 1.0 · MonotoneEscape · ClearanceBandCritic) · [BT 끝 방향 0° 결함 · CopyPath](bt-copypath-end-yaw.md)(no5 의 첫 8/8 = f2t1 · 고정 구성의 일부) · [pad_relief · 실행 중 패딩](pad-relief-runtime-padding.md)(구성 '관찰만' · 판정 ⑥ 의 출발점인 멈칫) · [남서 구석 방향 맞춤 정체](southwest-orient-stall.md)(목표 4 '위치만') · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(b910 코스의 출처 · 출발점 시험 상자) · [F2 순회와 위치 점프](f2-patrol-loc-jump.md)(10 목표 코스의 출처) · [MPPI 궤적 발행 포화](network-saturation-mppi-viz.md)(`mppi_viz lite` 구성) · [MPPI 조향 흔들림](mppi-wobble-temperature.md)(잔떨림) · [Phase S 기준선](phase-s-baseline.md)(앞 기준선의 방법) · [Jetson Wi-Fi](jetson-wifi-link.md)(10-15 재부팅 · 새 주소) · [경로 추종 · B0](path-tracking-replan-b0.md) · [PathBlockedAhead only_new](pathblocked-only-new.md) (8 기) |

**한 줄**: 개선 전 '지금 구성' 의 F2 순회 실력을 숫자로 고정하려고, 8 목표 `no5`(B → C → 서쪽 통로 → 남서(위치만) → 서쪽 통로 → 위 복도 → W3 → 출발) 와 3 목표 `b910`(B → W3 → 출발) 을 매번 새 스택으로 달렸다. 판정 ①~⑥ 은 주행 전에 선언했고, 결과는 **6 회 중 3 회 합격**(no5 f2v1 ✘ · f2v2 ✔ · f2v3 ✘, b910 f2u1 ✔ · f2u3 ✔ · f2v4 ✘). 세 실패는 모두 **라이다 아래 낮은 상자 옆**에서 서 있는 자세부터 '닿음' 판정 → 복구 세 바퀴 뒤 Nav2 중단(같은 기전, [상자 옆 정지 원인](box-side-stall-cause.md)). f2v2 는 선언 기준 ⑥(좌우 틀기)을 넘었지만 사용자 육안 · 분석으로 ⑥ 이 눈에 안 보이는 잔떨림을 센다는 것이 드러나 **결과를 본 뒤 ⑥ 을 '보이는 멈칫' 으로 재정의**하고 합격 처리했다(사후 변경 — 표시해 둠). 코스 이름 'W3' 가 두 자리에 붙어 있던 기록 실수도 여기서 바로잡았다(§27.2).

## 1. 증상 (왜 기준선이 필요했나)
- 10-14 하루에 BT 결함 수정(CopyPath) · pad_relief 켬/끔 · A/B(실행 중 패딩 변경 = 멈칫 원인) 가 겹쳐, '지금 구성이 이 코스를 몇 번에 몇 번 도는가' 가 숫자로 없었다. f2t1 은 8/8 이었지만 pad_relief 작동 뒤 목표 7 · 8 이 180.9 · 148.4 s 로 느렸다([`run_f2t1.txt`](../debug_log/2026-10-14/outputs/run_f2t1.txt)).
- 10-14 §26: "다음(추천, 결정 대기): F2 순회 기준선 고정 — `no5` 3 회(매번 새 스택), 판정 기준 주행 전 선언 → BASELINE_F2.md · 태그 · TEST_COURSE_AND_GATES v2.3."
- 사용자 질문(§27): "8 목표에서 2 번째 목표로 W3 를 가는 건 낭비 아닌가" — 기록의 목표 이름이 틀려 있어 생긴 질문이었다(§27.2).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-14 §12 | 10 목표 순회(10-08 FULLF) 그림 — 사용자가 뺄 곳 고름 | 1 B · 2 'W3' · 3 서쪽 통로 · 4 남서(f) · 5 D · 6 남서(f) · 7 서쪽 통로 · 8 'W3 남쪽' · 9 'W3 동쪽' · 10 출발. 2 와 8 은 0.1 m 차라 한 원 | 사용자 "5 번 빼고" → 6 도 뺌(같은 자리 연속 목표 — 길이 0 경로 끝 방향 조회가 됨, 내 판단 · 알림) = `no5`. ⚠ 이름 'W3' · 'W3 남쪽' · 'W3 동쪽' 은 §27.2 에서 정정 | 그림 [`2026-10-14_patrol_goals.png`](../04_navigation/figures/2026-10-14_patrol_goals.png) · [`fig_patrol_goals.py`](../tools/fig_patrol_goals.py)(커밋 `d6e1de4d`, 이름 되돌림 `75d667f7`) |
| 10-14 §13 · §13.3 · §17 | `no5` 첫 주행들 | f2s1 3 목표에서 취소(BT 결함) → f2s2 이어 가기 5/5 → **f2t1 8/8 605.5 s**(CopyPath 뒤, 서쪽 통로 p) | 코스 자체는 8/8 가능. f2t1 은 pad_relief 첫 작동 뒤 멈칫(목표 7 · 8 느림) | [`run_f2t1.txt`](../debug_log/2026-10-14/outputs/run_f2t1.txt) → [BT 끝 방향 카드](bt-copypath-end-yaw.md) |
| 10-14 §21 · §22.2 | A/B(b910): f2u1(새 스택) · f2u2(정지 중 패딩 토글) · f2u3(새 스택) | f2u1 3/3 200.8 s · f2u3 3/3 201.5 s, 좌우 틀기 10.0 · 9.1 / 14.7 · 19.6 /분(목표 2 · 3), B 98.4 · 64.1 | 실행 중 패딩 변경 = 멈칫 원인 확정 → pad_relief 는 관찰만. f2u1 · f2u3 은 다음 날 기준선에 합침 | [`run_f2u1.txt`](../debug_log/2026-10-14/outputs/run_f2u1.txt) · [`run_f2u3.txt`](../debug_log/2026-10-14/outputs/run_f2u3.txt) → [pad_relief](pad-relief-runtime-padding.md) |
| 10-14 §26 | 하루 마무리 · 다음 추천 | — | 기준선 = no5 3 회 · 판정 주행 전 선언 · BASELINE_F2.md · 태그 · TEST_COURSE v2.3(계획) | SUMMARY §26 |
| 10-14 §27 | 사용자 "2 번째 목표 W3 는 낭비 아닌가" · "no5 경로 시각화" | f2t1 실제 궤적, 구간 시간 1 B 53 · 2 56 · 3 서쪽 통로 28 · 4 남서 65 · 5 서쪽 통로 41 · 6 33 · 7 W3 181 · 8 출발 148 s | 2 번째 목표를 빼도 같은 모퉁이를 돈다(아끼는 것은 한 번 서고 방향 맞추는 시간). 사용자 방향: 기준선 = no5 + b910 | 그림 [`figures/no5_route_f2t1.png`](../debug_log/2026-10-14/figures/no5_route_f2t1.png) · [`fig_no5_route.py`](../debug_log/2026-10-14/jobs/fig_no5_route.py) · 입력 [`outputs/f2t1.csv`](../debug_log/2026-10-14/outputs/f2t1.csv) · bag `bag_f2t1.tgz` |
| 10-14 §27.1 | 사용자 결정 | "W3, W3 남쪽, W3 동쪽을 같은 위치로 판단해서 말한 것" | **no5 그대로 + b910.** 혼동 원인 = 목표 이름(내 판단) | SUMMARY §27.1 |
| 10-14 §27.2 | 'W3' 가 겹친 이유(사용자 질문) | 09-29 F0-b: W1 · W2 · **W3 (5.5, −2.2)**. 10-01 §8.3x 코스: B → **C (−1.6, −2.0)** → … → **위 복도 (−1.6, −2.1)** → **W3 (5.5, −2.2)**. 10-01 f2a12 결과 줄(10-01 SUMMARY 455 행)에서 C 를 'W3' 로 적고, 10-02 §6 이 그것을 옮겨 적음 | **설계 이유 없음 — 내 기록 실수가 이어진 것**. 10-14 §12 이후 'W3 남쪽' · 'W3 동쪽' 을 새로 붙여 혼동을 키움(실수 1) | [10-01 SUMMARY](../debug_log/2026-10-01/SUMMARY.md) · [10-02 SUMMARY §6](../debug_log/2026-10-02/SUMMARY.md) · [09-29 SUMMARY §12](../debug_log/2026-09-29/SUMMARY.md) |
| 10-14 §27.3 | 이름 되돌림(사용자 "우선 되돌리고 마무리") | C (−1.6, −2.0) · 위 복도 (−1.6, −2.1) · W3 (5.5, −2.2). 그림 두 장 재작성(덮어쓰기 Errno 22 → 임시 이름 뒤 복사) | 지난 날짜 본문은 고치지 않고 §27.2 · §27.3 이 정정 | 커밋 `75d667f7` |
| 10-15 §0 · §1 · §1.1 | 재부팅 → 새 주소 192.168.0.110(DHCP 예약), `/tmp` 스크립트 5 개 재전송 | 172.30.1.8 무응답 2 분 → 사용자 "110 으로 접속되도록 DHCP 서버에 기록" → 이 Jetson 확인(jetson-desktop · R36.5.0 · office_v3) | 구성 고정 대상: git `75d667f7` 이후 문서 변경만 · `prep_patrol_pad.sh lite 15.0 shadow` · CopyPath · nvblox 통합 1.4 · PreferForward 15 · mppi_viz lite | [`chk_after_reboot.sh`](../debug_log/2026-10-15/jobs/chk_after_reboot.sh)(출력 **원천 소실**) → [Jetson Wi-Fi §2.3](jetson-wifi-link.md) |
| 10-15 §2 선언 | **판정(주행마다)** ① 목표 전부 SUCCEEDED(남서 위치만) ② 접촉 0(사용자) ③ 사람 개입 0 ④ Nav2 ABORT · nav_guard 취소 0 ⑤ 복구 동작 정지 ≤ 2 ⑥ 목표 구간마다 좌우 틀기(\|ω\| > 0.05 부호 바뀜) ≤ 45 /분. 기록만: 시간 · 상자 옆 최소 여유 · CPU · 전력 · 마지막 위치 오차 | no5 2 회(f2v1 · f2v2) + b910 1 회(f2v3 — 실제로는 f2v4, §17 에서 변경) · 10-14 f2u1 · f2u3 은 params.txt 가 같으면 합침 · STAGE `F2-baseline` · 속도 0.07 | '기준을 넘는 주행은 다시 달려 덮지 않고 그대로 기록' | SUMMARY §2 |
| 10-15 §3 | **f2v1(no5 1)** | 1 B 52.8 · 2 C 53.5 · 3 서쪽 통로 27.1 s 성공, **4 남서 ABORTED 25.8 s** — 로버 (−1.704, −4.118, −85.3°) 서쪽 통로 남쪽. Nav2: 'Optimizer fail' → 후진 즉시 실패 → 대기 5 s 를 **세 바퀴**(10:15:48.0 ~ 10:16:05.7) → Goal failed. pad_relief(관찰) '바꿀 상황' 기록 | **불합격(④)**. 쓸고 갈 영역에 치명 · 미지 칸 0 인데 '후보 전부 충돌' → 원인 모름(그때). 어제 f2t1 은 같은 자리에서 pad_relief 가 패딩 0 으로 바꾼 뒤 빠져나감 → 기여 가능성(추정, 반사실 확인 안 됨). ⚠ SUMMARY '복구 두 바퀴, 약 12 s' 는 로그와 다름(실수 3) | [`run_f2v1.txt`](../debug_log/2026-10-15/outputs/run_f2v1.txt) · [`navlog_f2v1.txt`](../debug_log/2026-10-15/outputs/navlog_f2v1.txt) · 그림 [`figures_stall_f2v1.png`](../debug_log/2026-10-15/figures/figures_stall_f2v1.png) · [`figures_stall_f2v1_vs_f2t1.png`](../debug_log/2026-10-15/figures/figures_stall_f2v1_vs_f2t1.png) · [`anal_ahead_cells_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_ahead_cells_f2v1.txt) · [`anal_passage_gap_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_passage_gap_f2v1.txt) |
| 10-15 §4 | f2v1 멈춘 자리에서 복귀 **f2v1r**(사용자 "빠져나와 출발선으로 올 수 있나" → "시작"). 같은 스택, G2 생략, 코스 `homew` = 서쪽 통로(위치만) → 출발. 기준선 아님(STAGE `F2-baseline-recover`) | **2/2 144.1 s**(11.8 · 132.1 s), Nav2 실패 0. 0~3 s 후진(v −0.02~−0.06) + 왼쪽 회전으로 약 10 cm 북쪽 → 통로 안 제자리 회전 −85° → +66° → 북쪽 | 같은 자리 · 같은 스택에서 **남쪽 궤적은 전부 충돌, 북쪽은 바로 찾음** → 막힘은 자리가 아니라 '남쪽으로 나가는 움직임'(측정). 이유 모름(그때) | [`run_f2v1r.txt`](../debug_log/2026-10-15/outputs/run_f2v1r.txt) · [`navlog_f2v1r.txt`](../debug_log/2026-10-15/outputs/navlog_f2v1r.txt) |
| 10-15 §5~§13 | 멈춘 자리 분석 · 대책 후보 오프라인 검증 · 사용자 실측(상자 앞면 5.8~6.0 cm 앞 → 카메라 과장 약 7 cm) | — | 이 카드 밖 → [상자 옆 정지 원인](box-side-stall-cause.md) · [대책](box-side-stall-remedies.md) | SUMMARY §5~§13 |
| 10-15 §14 · §15 | **f2v2(no5 2)** — 같은 구성 · 새 스택 | **8/8 427.4 s**(51.1 · 54.5 · 27.6 · 28.8 · 31.6 · 24.4 · 103.5 · 105.4 s). 실패 1(12:19:35.9, 복구 없음). ⑥ 좌우 틀기 /분: 목표 1~3 = 11.8 · 10.9 · 21.4, **4~8 = 49.3 · 37.5 · 86.4 · 110.1 · 60.6**. 서쪽 통로 상자 옆 3.2~4.3 cm 를 멈추지 않고 통과 | **선언 기준으로는 불합격(⑥)**. 패딩을 바꾸지 않은 스택에서도 좌우 틀기가 생김 → 10-14 '패딩 토글이 원인' 은 충분 조건까지(정정 필요 ？) | [`run_f2v2.txt`](../debug_log/2026-10-15/outputs/run_f2v2.txt) · [`navlog_f2v2.txt`](../debug_log/2026-10-15/outputs/navlog_f2v2.txt) · [`anal_hesitation_f2v2.txt`](../debug_log/2026-10-15/outputs/anal_hesitation_f2v2.txt) · [`anal_hesitation_f2v2_10s.txt`](../debug_log/2026-10-15/outputs/anal_hesitation_f2v2_10s.txt) · [`passage_pass_f2v2.txt`](../debug_log/2026-10-15/outputs/passage_pass_f2v2.txt) |
| 10-15 §16 | 사용자 육안 "넓은 통로에서 멈칫 · 좌우 틀기가 보이지 않았다(어제보다 빨랐다)" | W3 가는 길: 어제 f2t1 v 0.042 · 멈칫 40.2 /분 · 바뀜(0.05) 137, 오늘 f2v2 **v 0.079 · 멈칫 0.6** · 바뀜 109, 명령 ω 흔들림 0.056 → 0.066 | **지표가 두 현상을 섞었다**: ① 보이는 멈칫(속도가 떨어짐 — f2t1) ② 안 보이는 잔떨림(속도 그대로, ω ±0.07 — f2v2 후반 · 10-14 B). 옛 ⑥ 은 주로 ② 를 셈. 10-14 A/B 가 확정한 것도 주로 ② | [`anal_wiggle_amp.txt`](../debug_log/2026-10-15/outputs/anal_wiggle_amp.txt) · [`anal_wiggle_amp.py`](../debug_log/2026-10-15/jobs/anal_wiggle_amp.py) |
| 10-15 §17 | **⑥ 재정의**(사용자 "동의한다. 기준 ⑥ 바꾸고 진행하자") | 새 ⑥: 목표 구간마다 **멈칫(순항 ≥ 0.06 → < 0.03) ≤ 6 /분** + 직선 위주 구간(no5 목표 1 · 2 · 7 · 8, b910 전부) **평균 명령 v ≥ 0.06**. 잔떨림은 기록만. params.txt: f2u1 · f2u3 · f2v1 = f2v2(다른 줄 0), run_meta 배포 파일 해시 같음 | ⚠ **주행 뒤에 바꾼 기준** — 사용자 결정, 이유와 함께 남김(SUMMARY 가 표시). 새 ⑥ 판정: f2u1 2.5 · 0.069 ✔ · f2u3 3.0 · 0.072 ✔ · f2v2 2.4 · 0.072 ✔(② 확인 뒤). 남은 주행 = no5 1 회(f2v3, 'f2v1 대체') + b910 1 회(f2v4) | SUMMARY §17 표(f2u1 · f2u3 값과 params 비교 출력은 **원천 소실**) · f2v2 값은 `anal_hesitation_f2v2.txt` |
| 10-15 §17.1 | 사용자 "f2v2 주행 중 닿은 경우는 없었다" | — | **f2v2 합격 확정** | — |
| 10-15 §18 · §18.1 | **f2v3(no5 3)** | 1 B 51.7 · 2 C 52.9 · 3 서쪽 통로 30.1 s(도착 (−1.670, −3.646, −65.0°), 보낸 방향 −45°), **4 ABORTED 18.9 s** — 목표 3 자리에서 거의 안 움직임. 복구 세 바퀴(13:24:07.2 ~ 13:24:25.2). 앞 왼쪽 모서리 → 치명 칸 2.7 cm(카메라만, 상자 북쪽 끝) | **불합격(④)**. 원인(추정): 목표 3 p 방향이 이번엔 −45°(f2v1 · f2v2 −55~−56°)라 상자 쪽으로 돌아 서며 모서리가 붙음 → 목표 4(남쪽)로 돌 길 없음. 후보: 서쪽 통로 목표 방향 고정(남행 −90° · 북행 +90°) | [`run_f2v3.txt`](../debug_log/2026-10-15/outputs/run_f2v3.txt) · [`navlog_f2v3.txt`](../debug_log/2026-10-15/outputs/navlog_f2v3.txt) · [`anal_motion_probe_f2v3.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe_f2v3.txt) · [`anal_near_cells_src_f2v3.txt`](../debug_log/2026-10-15/outputs/anal_near_cells_src_f2v3.txt) |
| 10-15 §18.2 | 사용자 실측: 멈춘 자세의 왼쪽 앞끝 ↔ 상자 대각선 **8~9 cm** | 지도상 2.7 cm | 카메라 과장 ≈ 6 cm + 5 cm 칸 검사 → 서 있는 자세부터 '닿음'(추정). 실제로는 우회전 · 후진 뒤 남쪽 회전이 가능 | SUMMARY §18.2 → [상자 옆 정지 원인](box-side-stall-cause.md) |
| 10-15 §18.3 · §19 | **f2v3r** 복귀(homew) · 사용자 "상자 쪽으로 경로를 만들었다가 인식 뒤 수정?" | 2/2 136.5 s. 출발 순간(멈춘 지 약 9 분) 최근접 17.5 cm — 상자 카메라 칸이 감쇠로 사라짐. 출발점행 경로는 처음부터 **모두 북쪽**(+85~+107°), 시계 방향 약 190° 회전 중 상자 칸 2 → 12 | 복귀 성공 = 칸 감쇠 덕(방향 차이 아님). 경로 수정 아님 — 회전 방향 때문에 상자 쪽을 향한 모습. ⚠ 그 순간 지도엔 실제 8~9 cm 앞 상자가 없음('대기 늘리기' 류 대책이 위험한 근거) | [`run_f2v3r.txt`](../debug_log/2026-10-15/outputs/run_f2v3r.txt) · [`anal_motion_probe_f2v3r.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe_f2v3r.txt) · [`anal_replan_trace_f2v3r.txt`](../debug_log/2026-10-15/outputs/anal_replan_trace_f2v3r.txt) |
| 10-15 §20 · §20.1 | **f2v4(b910 3)** | 1 B 51.6 · 2 W3 48.8 s 성공, **3 출발 ABORTED 102.7 s** — (1.275, 0.224, 168.8°) 출발점 시험 상자 끝. 복구 세 바퀴(14:02:04.2 ~ 14:02:21.7). 최근접 4.3 cm(차체 왼쪽 옆), 8 cm 안 칸 2 개 모두 라이다 0 | **불합격(④)**. 서쪽 통로와 같은 기전(추정) — 라이다 아래 낮은 물체가 옆에 오고 지도 여유가 약 4.4 cm 아래면 서 있는 자세부터 '닿음' | [`run_f2v4.txt`](../debug_log/2026-10-15/outputs/run_f2v4.txt) · [`navlog_f2v4.txt`](../debug_log/2026-10-15/outputs/navlog_f2v4.txt) · 그림 [`box_end_f2v4.png`](../debug_log/2026-10-15/figures/box_end_f2v4.png) · [`anal_motion_probe_f2v4.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe_f2v4.txt) · [`anal_near_cells_src_f2v4.txt`](../debug_log/2026-10-15/outputs/anal_near_cells_src_f2v4.txt) |
| 10-15 §21 | **기준선 정리** | no5 f2v1 ✘ · f2v2 ✔ · f2v3 ✘(1/3) · b910 f2u1 ✔ · f2u3 ✔ · f2v4 ✘(2/3) = **3/6**. 성공 자리 도착 오차 0.10~0.15 m, 새 ⑥ 안 | **기준선 = 3/6 그대로 고정.** 세 실패 같은 기전(카메라 과장 6~7 cm + 칸 검사). 다음 = ① nvblox site 2.0 → 1.0 ② 서쪽 통로 목표 방향 고정, 같은 코스로 전후 비교 | SUMMARY §21 · 정리 페이지 [`figures/stall_trace_1015.html`](../debug_log/2026-10-15/figures/stall_trace_1015.html) '기준선 순회 §2 · §21' |
| 10-15 §29.1 · §29.6 | **f2w2** — 같은 no5, 단 ClearanceBandCritic(가볍게 고친 판) + MonotoneEscape(§26) 켬 = **기준선 구성 아님** | 8/8 429.8 s(서쪽 통로 3 · 4 · 5 = 29.2 · 28.8 · 33.0 s). 서쪽 통로 최소 5.1~6.0 cm(f2v2 3.2), 2.7~4.4 cm 띠 0 프레임. 제어 주기 놓침 428 | §29.1 판정 ③(놓침) 불합격 — 운용 불가. 기준선과 같은 코스 · 판정 ①~⑥ 으로 비교한 첫 개선판 | [`run_f2w2.txt`](../debug_log/2026-10-15/outputs/run_f2w2.txt) · [`anal_band_run_no5.txt`](../debug_log/2026-10-15/outputs/anal_band_run_no5.txt) → [상자 옆 정지 대책](box-side-stall-remedies.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| f2u1 · f2u3(10-14) 를 10-15 주행과 합쳐도 된다(같은 구성) | bag `params.txt` 차이 · run_meta 배포 파일 해시 | 다른 줄 0 · 해시 같음(수정 날짜만 다름) — SUMMARY §17 | **지지**(비교 출력은 원천 소실) |
| f2v2 의 ⑥ 위반 = 사용자가 처음 지적한 '보이는 멈칫' | 같은 길 f2t1 vs f2v2 의 평균 v · 멈칫 수 · 문턱별 부호 바뀜 · ω 흔들림 RMS | f2v2 W3 길 v 0.079 · 멈칫 0.6 /분(f2t1 0.042 · 40.2), 바뀜 0.05 문턱 109 vs 0.20 문턱 4.0 | **기각** — ⑥ 은 작은 잔떨림을 셌다. 사용자 육안과 일치 |
| 옛 ⑥ 으로 판정해도 결과가 같다 | 옛 ⑥ 값 | f2u1 목표 1~3 = 13.6 · 10.0 · 9.1, f2u3 = 18.8 · 14.7 · 19.6 /분(10-14 §21.3 · §21.4) → 합격 그대로. **f2v2 만 불합격**(목표 4 · 6 · 7 · 8). f2v1 · f2v3 · f2v4 는 ④ 로 불합격 | **기각** — 재정의는 f2v2 하나의 판정을 바꿨다: 옛 ⑥ 2/6 → 새 ⑥ 3/6 |
| f2v1 실패는 pad_relief(관찰만) 때문 — 어제는 패딩 0 으로 빠져나감 | 같은 자리 · 패딩 변경 없는 주행 | f2v2 는 같은 서쪽 통로를 패딩 변경 없이 3.2~4.3 cm 로 통과, f2v1r 은 같은 스택에서 북쪽으로 바로 빠짐 | **미확인**(반사실 없음). 실패는 '서서 방향을 고쳐야 하는 상황' 에서 생김(추정, §15) |
| 세 실패(f2v1 · f2v3 · f2v4)는 같은 기전 | 최근접 칸의 출처(라이다 점 유무) · 지도 여유 · 실측 | 8 cm 안 칸 모두 라이다 0(카메라만) · 지도 여유 2.7~4.3 cm · 실측 8~9 cm(f2v3) | **지지(측정 + 추정)** — 기전 확정은 [상자 옆 정지 원인](box-side-stall-cause.md)(10-15 §28) |
| f2v3 은 목표 3 의 자동 방향 −45° 때문 | 목표 3 도착 자세 비교 | f2v1 (−1.711, −3.569, −71.9°) 안에서 멈춤 · f2v2 (−1.718, −3.573, −74.5°) 통과 · f2v3 (−1.670, −3.646, −65.0°) 즉시 멈춤. 경로 끝 방향 f2v1 −54.5 · f2v2 −55.9 · f2v3 −45.0° | **추정(정황 지지)** — 방향 고정 시험은 안 함 |
| f2v3r 복귀 때 경로가 상자 쪽으로 났다가 바뀜(사용자) | 경로 방향 · 상자 구역 거리 시간순 | 출발점행 경로 모두 북쪽, 상자 칸 2 → 12 는 회전 중 재관측 | **기각** |

## 4. 조치와 효과
- **고정한 수치(10-15 §21)** — 지금 구성(10-15 §0: CopyPath · pad_relief 관찰 · nvblox 통합 1.4 m · PreferForward 15 · mppi_viz lite · 속도 0.07, NavFn + SimpleSmoother. prep `prep_patrol_pad.sh lite 15.0 shadow` = rf2o + G4 휠 잔차 게이트 · 그림자 EKF 끔 · 전역 nvblox(map) · 재계획 0.5 Hz · stuck 관찰 — [`2026-10-14/jobs/prep_patrol_pad.sh`](../debug_log/2026-10-14/jobs/prep_patrol_pad.sh) 3 · 6 행) 의 F2 순회:

  | 코스 | 주행 | ① 도착 | ④ 중단 | 새 ⑥ 멈칫 /분(최대) · 직선 v(최소) | ② 접촉 | 판정 | 실패 자리 |
  |---|---|---|---|---|---|---|---|
  | b910 | f2u1(10-14) | 3/3 | 0 | 2.5 · 0.069 | 보고 없음 | ✔ | — |
  | b910 | f2u3(10-14) | 3/3 | 0 | 3.0 · 0.072 | 없음(반대쪽으로 꺾어 통과) | ✔ | — |
  | no5 | f2v1 | 3/8 | 1 | — | — | ✘ | 서쪽 통로 남쪽(목표 4 시작) |
  | no5 | f2v2 | 8/8 | 0 | 2.4 · 0.072 | 없음(사용자) | ✔ | — |
  | no5 | f2v3 | 3/8 | 1 | — | — | ✘ | 서쪽 통로 입구(목표 3 자리) |
  | b910 | f2v4 | 2/3 | 1 | — | — | ✘ | 출발점 시험 상자 끝(목표 3) |

  출처: SUMMARY §17 표 · §21 표, 러너 출력 `2026-10-15/outputs/run_f2v*.txt` · `2026-10-14/outputs/run_f2u*.txt`. f2v2 새 ⑥ 값은 [`anal_hesitation_f2v2.txt`](../debug_log/2026-10-15/outputs/anal_hesitation_f2v2.txt)(멈칫 최대 g6 2.4 · 직선 구간 v g1 0.080 · g2 0.081 · g7 0.080 · g8 0.072):
  ```
  구간    길이   평균 명령 v   순항→멈칫 횟수(분당)   ω 부호 바뀜(분당)
  g6     25 s   0.079 m/s       1 ( 2.4)             36 (86.4)
  g7    103 s   0.080 m/s       0 ( 0.0)            189 (110.1)
  g8    105 s   0.072 m/s       4 ( 2.3)            106 (60.6)
  ```
  계산 줄([`2026-10-14/jobs/anal_hesitation.py`](../debug_log/2026-10-14/jobs/anal_hesitation.py) 28~32 행, 커밋 `2fa622a2`):
  ```python
  for x in v:
      if x >= 0.06: cruise = True
      elif x < 0.03 and cruise: dips += 1; cruise = False      # 멈칫(새 ⑥)
  ws = np.sign(np.where(np.abs(w) > 0.05, w, 0)); ws = ws[ws != 0]; flips = int((ws[1:] != ws[:-1]).sum())   # 옛 ⑥
  ```
- 효과 · 쓰임: 다음 개선(10-15 §22 site 1.0 — 효과 없음 · §25~§27 MonotoneEscape · §29 ClearanceBandCritic · §30 통합 거리 1.0)이 이 3/6 · 같은 코스 · 같은 판정으로 비교됐다(f2w1 · f2w2 — [상자 옆 정지 대책](box-side-stall-remedies.md)).
- 한계: ① 표본 6 회 — 3/6 의 흩어짐은 크다(no5 1/3 · b910 2/3). ② ⑥ 은 사후 재정의(§3). ③ ② · ③ 은 사용자 관찰 — f2u1 은 '보고 없음' 으로 접촉 0 처리. ④ 기준선 문서 · 태그 · 시험 코스 문서 판 올림을 안 해, 이 수치의 단일 출처는 10-15 SUMMARY §17 · §21 뿐.
- **지금 코드 · 문서 확인(11-03)**:
  - 시험 코스 문서 [`TEST_COURSE_AND_GATES.md`](../04_navigation/TEST_COURSE_AND_GATES.md) 1 행 'v2.3 (Phase N + F0-a 왕복), 2026-09-28' — F2 · no5 · b910 절 **없음**. `BASELINE_F2.md` 는 저장소에 없음(파일 검색 0, 이름은 10-14 · 10-15 SUMMARY 에만). git 태그는 `stvl-baseline` · `navfn-baseline-20261023`(10-23 §21 'B0: NavFn 결함 기준선' — b910 상자 옆 수치, 이 카드의 3/6 과 다른 기준선).
  - 코스 좌표: 러너 `no5` 는 저장 사본 [`2026-10-15/jobs/run_f2c.sh`](../debug_log/2026-10-15/jobs/run_f2c.sh) 8 행(실행본은 PC 스크래치패드). 장소 등록부 [`places.yaml`](../../ros2_ws/src/rover_navigation/config/places.yaml) 은 no5 자리를 이름으로 담지만 **서쪽 통로('통로 북쪽')가 x −1.65 → −1.78 로 옮겨짐**(37~41 행, 10-28 §9) — place_server 로 도는 순회는 기준선 no5 와 같은 코스가 아니다. 남서 46 행 `yaw_mode: f`(기준선과 같음). 이름 C · 위 복도 · W3 는 3 행 주석대로 10-14 §27.3 이름.
  - 구성: 기준선 뒤 바뀐 것(10-27 계획기 smac · cuVSLAM 오도메트리 등, CLAUDE.md §6)이 많아 **지금 스택은 이 기준선 구성이 아니다** — 같은 비교를 하려면 10-15 §0 구성으로 띄워야 함.

## 5. 내 실수 · 기록 어긋남
1. **목표 이름 'W3' 이중 사용**(10-14 §27.2 — 칸 형식) — 하려 한 것: 10-01 f2a12 결과를 기록 · 본 것: 러너 로그의 목표 번호 · 처음 추론: 목표 2 = 'W3' · 의심한 이유(10-14): 사용자가 'W3 를 두 번 가는 낭비' 로 읽음 · 판별: 09-29 §12 · 10-01 §8.3x 코스 정의 대조 · 결론: 10-01 SUMMARY 455 행에서 C 를 'W3' 로 잘못 적고 10-02 §6 이 옮겨 적음(원인 추정: 번호 ↔ 이름 대응을 로그에서 옮기다 혼동), 10-14 §12 이후 'W3 남쪽 · 동쪽' 을 새로 붙여 키움 · 다음에 알아보는 법: 목표는 이름과 좌표를 함께 적고, 이름은 코스 정의(지금은 `places.yaml`)에서만 가져온다 · 데이터: SUMMARY §27.2 · 커밋 `75d667f7`.
2. **판정 ⑥ 을 지표 검증 없이 선언**(10-15 §2 → §16) — 하려 한 것: 10-14 의 '멈칫' 을 막는 기준 · 본 것: f2v2 ⑥ 위반인데 사용자 육안은 정상 · 처음 추론: f2v2 불합격 · 의심한 이유: 사용자 관찰 · 평균 속도 최고 · 판별: `anal_wiggle_amp.py`(문턱 3 개 · 고주파 RMS) · 결론: \|ω\| > 0.05 부호 바뀜은 표본 MPPI 의 작은 잔떨림까지 센다 · 다음에 알아보는 법: 기준 지표는 선언 전에 '깨끗한 주행' 과 '문제 주행' 기록에 돌려 갈리는지 본다(10-14 A/B 의 f2u1 · f2u3 vs f2t1 로 가능했음) · 데이터: [`anal_wiggle_amp.txt`](../debug_log/2026-10-15/outputs/anal_wiggle_amp.txt). 결과: **주행 뒤 기준 변경**(사용자 결정, §17 에 표시) — 옛 ⑥ 이면 2/6.
3. **'복구 두 바퀴, 약 12 s'**(SUMMARY §3 · §21 '약 12 s 만에 포기') — Nav2 로그는 세 실패 모두 '후진 실패 → 대기 5 s' 가 **세 번**(f2v1 10:15:48.2 · 54.6 · 16:00.5, f2v3 13:24:08.0 · 14.0 · 20.0, f2v4 14:02:04.5 · 10.5 · 16.5), 첫 'Optimizer fail' 부터 'Goal failed' 까지 **17.5~18.0 s**. BT `NavigateRecovery` 재시도 6 회(60 행)가 RoundRobin(117~128 행: 비우기 → 후진 → 대기)을 한 번씩 부르고, 후진이 실패하면 같은 차례에 대기로 넘어가므로 '비우기' 3 회 + '후진 실패 → 대기' 3 회가 된다 — 로그의 세 번과 어긋나지 않는다(RoundRobin 동작은 BT.CPP 에 대한 이해, 소스 대조 안 함. f2v1 은 첫 전역 · 로컬 비우기가 10:15:42.1 로 첫 'Optimizer fail' 앞이라 바퀴 경계는 로그만으로 확정 못 함). SUMMARY §3 의 시각 줄은 10:15:53.3 부터라 첫 바퀴(10:15:48.0)를 빠뜨림. 데이터: [`navlog_f2v1.txt`](../debug_log/2026-10-15/outputs/navlog_f2v1.txt) 34~73 행 · [`navlog_f2v3.txt`](../debug_log/2026-10-15/outputs/navlog_f2v3.txt) · [`navlog_f2v4.txt`](../debug_log/2026-10-15/outputs/navlog_f2v4.txt).
4. **선언한 회차 배정이 바뀜**(§2 'b910 1 회 = f2v3') → §17 끝 '남은 주행: no5 1 회(f2v1 대체, f2v3) + b910 1 회(f2v4)'. '대체' 라 썼지만 §21 은 f2v1 을 빼지 않고 세 번 모두 셈 — 선언의 '다시 달려 덮지 않는다' 는 지켜졌고, 바뀐 것은 no5 가 2 → 3 회로 는 것. 이유는 SUMMARY 에 따로 없음.
5. **출력 원문 없음**: f2u1 · f2u3 의 새 ⑥ 값(2.5 · 0.069 / 3.0 · 0.072) · params.txt 비교 · `chk_after_reboot.sh` 결과 — SUMMARY §17 · §1.1 서술뿐(원천 소실). 10-14 A/B 의 `anal_hesitation.py` 출력도 원천 소실(하루 보고서 표시).
6. 경미: 10-15 러너 출력 6 개(`run_f2v1` ~ `run_f2v4` · `f2v1r` · `f2v3r`) 머리에 `run_f0.sh: line 8: …/rescued_jetson_tmp/job386_slamalive.py: No such file or directory`(job440 · job451 · job453 도) — PC 쪽 보조 사본이 없어 이 판이 전송되지 않았다. 그런데도 게이트 C 통과(6/6, job386 이 Jetson `/tmp` 에 있었다는 뜻)이고 §17 은 params.txt(job451 · job453 산출)를 비교했다 — Jetson 에 있던 판의 출처는 기록 없음(재부팅 뒤 `up_tools.sh` 가 `up950/` 사본을 올렸을 가능성, 추정). 10-14 · 10-15 저녁(f2w1 · f2w2) 출력엔 이 줄이 없다.

## 6. 남은 것 (10-15 시점)
- `BASELINE_F2.md` · 태그 · `TEST_COURSE_AND_GATES` F2 절 — 계획만, 안 함.
- 개선 후보 ② '서쪽 통로 목표 방향 고정' — 시험 안 함. ① site 1.0 은 §22.2 에서 효과 없음.
- 잔떨림(명령 ω 흔들림 0.034 → 0.07 로 바뀌는 사건) — MPPI 과제로 남김(§17).
- 실패 뒤 멈춘 자리에서 '시야 밖 감쇠로 실제 상자를 잊은 지도' 로 출발하는 위험(§18.3) — 이 기준선 구성의 알려진 약점.

## 7. 이후 (10-19 ~): 다음 시기에서 채움
- 포인터만: 10-20 §6.3 · §6.4 이름 **f2v1 재사용**(그림자 주행 — '이름 충돌, 덮어쓴 것 없음' 은 10-20 이 밝힘) · 10-23 §21 B0 태그 `navfn-baseline-20261023` · 10-26 ~ 10-28 no5 반복 8/8(`places.yaml` 4 행 주석) · 10-28 §9 통로 북쪽 좌표 이동.
- **8 기(10-19 ~ 10-23) 채움**:
  - 이 시기 순회 주행은 거의 모두 **b910**(출발점 낮은 상자 복귀가 주제 — 10-22 f2pi1 · f2sm3, 10-23 f2pa1 · 2 · f2von1 · 2 · f2rp1 · 2 · 5). 판정은 이 카드의 ①~⑥ 이 아니라 날마다 선언한 상자 옆 지표(실제 최소 여유 · 경로 선 대비 치우침 · 짧은 멈칫 등) — 3/6 과 직접 비교할 수 없다. 본체 → [경로 추종 · 재계획 → B0](path-tracking-replan-b0.md).
  - **no5 는 10-23 에 두 번**(구성: vslam on · 프리셋 3 · 통합 2.0 · 재계획 0.01 + PathBlockedAhead · PathAlign 14 — 10-15 기준선 구성과 오도메트리 · 깊이 · 재계획이 다름):
    | 주행 | 결과 | 목표별 시간(s) | 서쪽 통로 · 최소 정확 여유 | 막힘 · 복구 | 데이터 |
    |---|---|---|---|---|---|
    | f2rp3(10-23 §20.1) | 8/8 · 접촉 0 | 52.2 · 53.5 · 27.3 · 34.6 · **52.1** · 25.0 · 99.3 · 106.0(총 450) | 최소 4.0 cm(남서 목표 근처), 2.7~4.4 cm 띠 4 프레임 | 서쪽 통로 막힘 오판 5 · **Wait 2** | [`run_f2rp3.txt`](../debug_log/2026-10-23/outputs/run_f2rp3.txt) · [`anal_band_run_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_band_run_f2rp3.txt) |
    | f2rp4(§20.5, only_new) | 8/8 · 접촉 0 | 51.7 · 54.1 · 28.5 · 26.2 · 32.6 · 24.4 · 98.6 · 101.3(총 417.9) | 진입 3.7 · 복귀 4.8 · 최소 2.9 cm(남서 돌아서기, 직전 최적화 실패 2) | 막힘 1(출발 상자, 정상) · Wait 0 | [`run_f2rp4.txt`](../debug_log/2026-10-23/outputs/run_f2rp4.txt) · [`anal_band_run_f2rp4.txt`](../debug_log/2026-10-23/outputs/anal_band_run_f2rp4.txt) |
    10-15 기준선 판정 ①~⑥ 으로 다시 매기지는 않았다(② 접촉 · ④ 중단은 둘 다 0, ⑤ '복구 정지 ≤ 2' 는 f2rp3 Wait 2 로 경계). 10-15 f2v2(427.4 s · 서쪽 통로 3.2 cm)와 같은 코스 · 비슷한 시간. f2rp3 의 막힘 오판은 → [PathBlockedAhead 카드](pathblocked-only-new.md).
  - **B0(10-23 §21) 는 이 카드의 기준선과 다른 기준선** — 같은 코스 이름(no5 · b910)을 쓰지만 구성(위)과 지표(상자 옆 실제 여유 b910 15.2 · 5.5 · 3.1 cm, no5 8/8 2 회)가 다르다. 태그 `navfn-baseline-20261023`(커밋 `9ce20486`)이 B0 이고, 이 카드의 3/6 은 여전히 태그 · 문서가 없다(10-15 SUMMARY §17 · §21 이 단일 출처).
  - 10-23 §20 이 비교 대상으로 f2v2 · f2w2 · f2v1 · f2t1 을 적어, 이 기준선 주행들이 B0 판정의 참조값으로 쓰였다.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2t1(10-14) | no5 첫 8/8 · 코스 궤적 그림의 원본 | `2026-10-14/outputs/run_f2t1.txt` · `f2t1.csv` · bag `bags/bag_f2t1.tgz` |
| f2u1 · f2u3(10-14) | b910 기준선 2 회(A · A2) | `2026-10-14/outputs/run_f2u1.txt` · `run_f2u3.txt` |
| f2v1 · f2v2 · f2v3(10-15) | no5 기준선 3 회 | `2026-10-15/outputs/run_f2v1~3.txt` · `navlog_f2v1~3.txt` |
| f2v4(10-15) | b910 기준선 3 회째 | `outputs/run_f2v4.txt` · `navlog_f2v4.txt` · 그림 `figures/box_end_f2v4.png` |
| f2v1r · f2v3r(10-15) | 멈춘 자리에서 복귀(homew) — 기준선 아님 | `outputs/run_f2v1r.txt` · `run_f2v3r.txt` · `navlog_f2v1r.txt` |
| f2w2(10-15) | 같은 no5, ClearanceBandCritic 판 — 기준선 아님 | `outputs/run_f2w2.txt` · `anal_band_run_no5.txt` |
| `run_f2c.sh` | 목표 문자열 래퍼(NO5 · B910 · HOMEW) | `2026-10-14/jobs/` · `2026-10-15/jobs/` |
| `fig_patrol_goals.py` · `fig_no5_route.py` | 코스 그림 · 실제 궤적 그림 | `Docs/tools/` · `2026-10-14/jobs/` → `04_navigation/figures/2026-10-14_patrol_goals.png` · `2026-10-14/figures/no5_route_f2t1.png` |
| `anal_hesitation.py` · `anal_wiggle_amp.py` | 판정 ⑥(옛 · 새) 계산 | `2026-10-14/jobs/` · `2026-10-15/jobs/` → `outputs/anal_hesitation_f2v2*.txt` · `anal_wiggle_amp.txt` |
| `chk_navlog_f2v1.sh` ~ `chk_navlog_f2v4.sh` · `chk_navlog_f2v1r.sh` | Nav2 · pad_relief 로그 발췌 | `2026-10-15/jobs/` → `outputs/navlog_*.txt` |
| `chk_after_reboot.sh` | 재부팅 뒤 신원 · `/tmp` · 컨테이너 확인 | `2026-10-15/jobs/`(출력 원천 소실) |
| `fig_stall_view.py` · `anal_passage_gap.py` · `anal_ahead_cells.py` · `anal_motion_probe.py` · `anal_near_cells_src.py` · `anal_replan_trace.py` | 실패 자리 분석 | `2026-10-15/jobs/` — 해설은 [상자 옆 정지 원인](box-side-stall-cause.md) |

## 9. 도구 해설
공통: 주행 체인 `run_f2c.sh` → 스크래치패드 `run_f0.sh`(전송 · `setsid nohup` 기동 · 2 s 폴링 · 산출물 회수) → Jetson `job551_f0drive.sh`(게이트 A · B · J · C · G2 · P → bag · tegrastats · top → `job550_f0run.py` → 메타 `job453_runmeta.sh` 가 `run_meta.txt` · `params.txt` 를 bag 에 넣음) — 해설 본체는 [남서 카드 §9](southwest-orient-stall.md) · [F2 순회와 위치 점프 §9](f2-patrol-loc-jump.md). 이 기준선은 그 체인을 그대로 썼다(10-13 판 [`run_f0.sh`](../debug_log/2026-10-13/jobs/run_f0.sh) · [`job551_f0drive.sh`](../debug_log/2026-10-13/jobs/job551_f0drive.sh) 와 같은 구조).

### run_f2c.sh — 목표 문자열 래퍼 (PC/WSL, bash) · 10-15 판
- 부른 형태: `bash run_f2c.sh f2v2 "<NOTE>" <GIT> no5`(STAGE `F2-baseline`, 복귀는 `… homew` · STAGE `F2-baseline-recover`). 인자 4 가 `rest5 · rest5f · fullf · b910 · no5 · s1rest · homew` 중 하나면 그 문자열, 아니면 `FULL`(10 목표).
- 목표 문자열(지도 절대 좌표, `GOAL_FRAME=map`): 6 행 `B910="2.25,-1.6,p;5.5,-2.2,p;0,0,p"` · 8 행 `NO5="2.25,-1.6,p;-1.6,-2.0,p;-1.65,-3.7,p;-1.6,-5.5,f;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"` · 10 행 `HOMEW="-1.65,-3.7,f;0,0,p"`(10-15 §4 추가 — 멈춘 자리에서 서쪽 통로 자리(위치만) → 출발점). 12 행 `LONG_REC=${LONG_REC:-1}`(→ `/trajectories` · `/transformed_global_plan` 기록) · `JETSON_HOST=${JETSON_HOST:-192.168.0.110}`(10-14 판 172.30.1.8) · `G2_SKIP=${G2_SKIP:-0}` · `EXTRA_TOPICS="/odometry/ekf_a /odom_rf2o /odom_rf2o/gated"`(그림자 EKF 는 꺼져 있어 `/odometry/ekf_a` 는 없었을 것 — prep 6 행 `shadow:=false`, bag 확인 안 함). 속도 0.07 고정.
- 왜(10-02 §6.2): 목표 문자열을 wsl 인자로 넘기다 갈라진 실수 재발 방지 — 문자열을 파일 안에 둠.
- 계보: 10-07 판(FULL · REST5 · REST5F) → 10-08(FULLF · B910) → 10-14(NO5 · S1REST) → 10-15(HOMEW, 주소 110). 결함: 실행본이 PC 스크래치패드라 날짜별 사본이 진본. 지금 F2.5 순회는 `place_server`(이름 → `places.yaml` 좌표)로 바뀜.

### fig_patrol_goals.py — 순회 목표 그림 (PC, Python matplotlib, `Docs/tools/`)
- 부른 형태: `python Docs/tools/fig_patrol_goals.py 출력.png`(저장소 뿌리에서 — `Docs/04_navigation/maps/office_v3.yaml · .pgm` 을 상대 경로로 읽음).
- 하는 일: 저장 지도(회색) 위에 10-08 FULLF 목표 10 개(17~18 행 `G` — 좌표 · p/f · 이름)를 번호 원으로(빨강 = f · 파랑 = p), 0.15 m 안 목표는 한 원에 번호를 묶음(2 · 8 은 0.1 m 차), 목표 사이 순서 화살표(직선 — 실제 경로 아님), 출발 초록 삼각형. 끝에 목표 표 출력(`%2d  %-8s (%5.2f, %5.2f)  위치만/방향까지`).
- 출력: [`2026-10-14_patrol_goals.png`](../04_navigation/figures/2026-10-14_patrol_goals.png)(10-14 §27.3 에서 새 이름으로 다시 그림). 화면 표 원문은 없음.
- 쓰인 곳: §12 사용자 선택(5 번 빼기). 결함: 목표 목록이 코드 안 상수(FULLF) — 다른 코스엔 고쳐 써야 함. 지금 쓸 수 있음.

### fig_no5_route.py — no5 실제 궤적 그림 (PC, Python rosbags + matplotlib, 10-14 jobs)
- 부른 형태: `fig_no5_route.py bag 러너csv 출력.png`(f2t1 bag · `outputs/f2t1.csv`).
- 하는 일: bag `/tf` 에서 odom→base_link · map→odom 을 모아 지도 좌표 궤적(3 표본에 하나)을 만들고, 러너 csv 의 `goal` 열이 처음 바뀐 시각을 첫 비영 `/cmd_vel` 시각(T0)에 맞춰 목표 구간 경계로 삼아 구간마다 tab10 색으로 그림. 범례 = '목표 k → 이름(걸린 시간 s)', 목표 원은 `fig_patrol_goals.py` 와 같은 규칙. 끝에 목표별 시작 시각 출력.
- 출력: [`figures/no5_route_f2t1.png`](../debug_log/2026-10-14/figures/no5_route_f2t1.png). 화면 출력 원문은 없음 — 구간 시간(53 · 56 · 28 · 65 · 41 · 33 · 181 · 148 s)은 SUMMARY §27 서술. 쓰인 곳: §27 · §27.1 결정. 결함: 목표 경계는 csv 와 bag 의 시작 맞춤(첫 지령 기준)에 의존.

### anal_hesitation.py — 멈칫 · 좌우 틀기 (PC, Python rosbags, 10-14 jobs, 커밋 `2fa622a2`)
- 부른 형태: `anal_hesitation.py 이름=bag@HH:MM:SS~HH:MM:SS …`(10-15 §15 는 f2v2 목표 1~8 구간 g1~g8 · 10 s 단위).
- 하는 일: 구간 안 `/cmd_vel`(v · ω) · `/tf` map→odom yaw · `/wheel_odom` · `/odometry/filtered` 각속도 → ① 멈칫 = v 가 ≥ 0.06(순항)이 된 뒤 < 0.03 으로 떨어진 횟수 ② 좌우 틀기 = \|ω\| > 0.05 인 표본만 남긴 부호의 바뀜 수 ③ 지도 보정 각 변화(끝 − 처음) ④ Σ\|EKF ω\| / Σ\|휠 ω\| — 모두 분당.
- 출력: [`anal_hesitation_f2v2.txt`](../debug_log/2026-10-15/outputs/anal_hesitation_f2v2.txt) · [`anal_hesitation_f2v2_10s.txt`](../debug_log/2026-10-15/outputs/anal_hesitation_f2v2_10s.txt). 10-14 A/B · f2t1 출력은 원천 소실.
- 쓰인 곳: 옛 ⑥(②) · 새 ⑥(①). 결함: ② 는 진폭을 안 봐 잔떨림과 보이는 흔들림을 구분 못 함(§16 — 이 카드 실수 2). 계보 → `anal_wiggle_amp.py`.

### anal_wiggle_amp.py — 좌우 틀기의 크기 (PC, Python rosbags, 10-15 jobs, 커밋 `d4dc24cb`)
- 부른 형태: `anal_wiggle_amp.py 이름=bag@HH:MM:SS~HH:MM:SS …`(f2v2 · f2t1 · f2u1 · f2u2 · f2u3 의 같은 길).
- 하는 일: 구간의 `/cmd_vel` · `/odometry/filtered` 로 평균 v · 멈칫 /분(위와 같은 식) · 부호 바뀜 /분을 문턱 0.05 · 0.10 · 0.20 rad/s 셋으로, 그리고 고주파 RMS — `hp()` = 0.05 s 격자 보간 뒤 1 s 이동평균을 뺀 값(방향은 2 s) — 를 명령 ω · EKF ω · EKF 방향(°)에 대해:
  ```python
  def hp(t, x, win=1.0):
      g = np.arange(t[0], t[-1], 0.05); y = np.interp(g, t, x); k = max(1, int(win / 0.05)); m = np.convolve(y, np.ones(k) / k, mode='same'); return y - m
  ```
- 출력 [`anal_wiggle_amp.txt`](../debug_log/2026-10-15/outputs/anal_wiggle_amp.txt):
  ```
  구간                 평균v   멈칫/분  부호바뀜/분(0.05·0.10·0.20)   명령ω 흔들림   실제ω 흔들림
  f2v2_목표7(오늘)         0.079     0.6     109.1 ·  46.8 ·   4.0              0.066          0.060
  f2t1_목표7(어제멈칫)       0.042    40.2     137.2 ·  20.1 ·   1.6              0.056          0.049
  f2u1_목표2(A깨끗)        0.072     3.7       9.8 ·   7.4 ·   2.5              0.033          0.040
  ```
- 쓰인 곳: §16 → §17 재정의. 결함: 구간 시각을 문자열 비교(`h0 <= h <= h1`)로 걸러 자정을 넘는 구간엔 못 씀. 이동평균 `mode='same'` 은 구간 양 끝에서 평균이 작아져 RMS 가 조금 커짐(1 s 몫).

### chk_navlog_f2v1.sh ~ f2v4.sh · chk_navlog_f2v1r.sh — Nav2 로그 발췌 (Jetson, bash, 로버 안 움직임)
- 10-14 `chk_navlog_f2t1.sh` 와 같은 본문([BT 끝 방향 카드 §9](bt-copypath-end-yaw.md)) — 시작 시각만 다름(f2v1 판 3 행 `date -d '10:13:17'`). `/tmp/nav2.log` 에서 목표 시작 · 성공 · 실패 · 스무딩 충돌 · 'fail to compute' · 후진 · 대기 · 비우기 줄만 `uniq -c -f2` 로 → `/tmp/f2v1_events.txt`, 끝에 `/tmp/pad_relief.log`.
- 출력 `outputs/navlog_f2v*.txt` — 예(f2v1, 50~53 · 73~77 행):
  ```
  10:15:54.5 [controller_server]: Optimizer fail to compute path
  10:15:54.6 [behavior_server]: Running backup
  10:15:54.6 [behavior_server]: backup failed
  10:15:54.6 [behavior_server]: Running wait
  ...
  10:16:05.7 [bt_navigator]: Goal failed
  --- pad_relief
  10:15:54 [shadow] 패딩 0.000 로 바꿀 상황(후보 전부 충돌 3 회/3 s, 1 번째) — 값은 안 바꿈
  ```
  첫 줄 `cp: '/dev/null' and '/dev/null' are the same file` 은 무해한 잡음(원인 미확인). 쓰인 곳 §3 · §15 · §18.1 · §20.1 판정 ④ · ⑤.

### chk_after_reboot.sh — 재부팅 뒤 확인 (Jetson, bash, 로버 안 움직임)
- 호스트 이름 · `/etc/nv_tegra_release` 첫 줄 · `~/ros2_ws/src/rover_navigation` 유무 · `~/maps/office/office_v3.posegraph` 수 · `uptime` · `/tmp` 기동 스크립트 6 개 유무 · `docker ps -a` 상태 · `wlan0` 주소 · SSID. 출력 원천 소실(SUMMARY §1.1 서술). ⚠ Jetson 위에서 도는 스크립트라 **로그인(비밀번호 전송) 뒤**의 확인이다 — 신원 확인으로서의 한계는 [Jetson Wi-Fi §2.3](jetson-wifi-link.md).

## 10. 용어
- **기준선(baseline)**: 개선을 시작하기 전 '지금 구성' 의 성적을 같은 코스 · 같은 판정 · 매번 새 스택으로 재어 고정한 값. 개선판은 이 값과만 비교한다(Phase S 의 `BASELINE_STVL.md` 와 같은 방법).
- **no5 · b910**: 순회 코스 이름 — no5 = 10-08 FULLF 10 목표에서 5(D)와 6(남서 두 번째)을 뺀 8 목표, b910 = FULLF 의 1 · 9 · 10 번(B → W3 → 출발, 10-08 사용자 지정).
- **C · 위 복도 · W3**: 10-01 §8.3x 코스 정의의 이름 — C (−1.6, −2.0) · 위 복도 (−1.6, −2.1) · W3 (5.5, −2.2, 동쪽 끝). 10-02 ~ 10-14 기록의 'W3 (−1.6, −2.0)' · 'W3 남쪽' · 'W3 동쪽' 은 이 이름의 오기.
- **보이는 멈칫 vs 잔떨림**: 멈칫 = 순항 중 명령 속도가 0.06 → 0.03 아래로 떨어지는 것(눈에 보임, 평균 속도가 준다). 잔떨림 = 속도는 그대로인데 명령 각속도가 ±0.07 rad/s 쯤으로 빠르게 좌우를 오가는 것(눈에 안 보임) — 표본 기반 MPPI 에서 흔하다.
- **homew**: 멈춘 자리에서 서쪽 통로 자리(위치만) → 출발점으로 돌아오는 복귀 코스(10-15 §4).
- **복구 세 바퀴**: BT `NavigateRecovery`(재시도 6 회)가 RoundRobin 으로 '코스트맵 비우기' 와 '후진(10-15 §26 전엔 Nav2 BackUp) → 실패하면 대기 5 s' 를 번갈아 세 번씩 부르는 것. 서 있는 자세부터 '닿음' 이면 후진이 0.0 s 에 실패해 첫 실패 뒤 약 18 s 만에 Goal failed.
