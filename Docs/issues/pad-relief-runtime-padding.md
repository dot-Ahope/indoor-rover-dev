# 갇힘 해제 pad_relief · 실행 중 패딩 변경의 멈칫 부작용

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **보류 — 쓰지 않음(10-14 A/B, 사용자 결정 유지)**. 갇혔을 때만 로컬 `footprint_padding` 을 0.01 → 0 으로 잠깐 내리는 노드 `pad_relief` 는 시뮬(10-13 §14.2 · 10-14 §2.1) · 정지 시험(§8.6 4/4) · 실제 1 회 탈출(§17)까지 갔으나, **실행 중 패딩을 한 번 바꿨다 되돌리면 그 스택이 끝날 때까지 MPPI 명령 각속도가 좌우로 떠는 상태가 된다**는 것이 A/B 로 재현됐다(§21.4: 좌우 틀기 /분 A 10.0 · 9.1 → 토글 뒤 B 98.4 · 64.1 → 새 스택 A2 14.7 · 19.6). 기전은 모름(§23 — CostCritic 가설은 기각). 이 시기 끝(10-15)에 두 가지가 정정됨: A/B 가 확정한 것은 주로 '안 보이는 잔떨림' 이고, 잔떨림은 패딩 변경 없이도 생긴다(10-15 §15 · §16) — '충분 조건' 이지 유일한 원인이 아님. 갇힘 탈출은 실행 중 파라미터를 바꾸지 않는 MonotoneEscape 로 넘어감(10-15 §25 ~, 다른 카드) | 10-13 §11 ~ §11.1 · §12.2 · §14.2, 10-14 §2 ~ §3 · §7 ~ §9.5 · §15 · §15.1 · §17 · §18 · §19.1 · §21 ~ §23 · §25 · §26, 10-15 §3 · §5 · §15 · §16 · §20.1 · §25 (이 카드), 이후 10-19 ~ | [10-13 §14.2](../debug_log/2026-10-13/SUMMARY.md)(사용자 지시 '§14 … stuck 때 파라미터 동적 조절 평가') · 부작용은 [10-14 §18](../debug_log/2026-10-14/SUMMARY.md)(사용자 휴대폰 영상 "서남부 통로에서 자꾸 상자 쪽으로 방향을 틀고, 넓은 공간에서 멈칫거리며 …") | `ros2_ws/src/rover_bringup/scripts/pad_relief.py`(새 파일 `0f1d99b7` → SIGHUP 복귀 `c08f43c3` → mode 형 수정 `f25e5f68`, 10-14) · `rover_bringup/CMakeLists.txt`(설치 목록) · `rover_navigation/launch/navigation.launch.py`(`pad_relief:=off\|on\|shadow`, 기본 off — `c08f43c3`) · `Docs/tools/chk_padding_dynamic.py`(`164a4c17`) · `Docs/tools/anal_mppi_sim.py`(`pad` `2887e666` · `unstuck` `e392a6fc`) · prep 래퍼 `2026-10-14/jobs/prep_patrol_pad.sh`(`f25e5f68` → 기본 shadow `7d809b9b`) · `CLAUDE.md` §6 줄(`1c207f64`) | [상자 옆 정지 — 원인](box-side-stall-cause.md)(칸 단위 검사 · 기억 밀림 — pad_relief 가 겨눈 정지) · [상자 옆 정지 — 대책](box-side-stall-remedies.md)(10-13 대책 4 건 · 10-15 MonotoneEscape) · [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md)(`fpchk` · `pad` · `unstuck` 인자) · [inflation · padding 역할](inflation-padding-roles.md) · [Jetson Wi-Fi](jetson-wifi-link.md)(10-14 §8.3 ~ §8.6 IP 충돌 — 정지 시험이 막힌 원인) · [BT CopyPath](bt-copypath-end-yaw.md)(§15.1 '이것이 pad_relief 를 불필요하게 하나') · [W3 저속 떨림 · TF 지연](tf-lag-w3-wobble.md)(같은 '좌우 틀기' 계열) · [MPPI 흔들림 · temperature](mppi-wobble-temperature.md) · [F2 기준선 no5](f2-baseline-no5.md)(10-15 기준 ⑥ 재정의) · [정체 감시 stuck_monitor](stuck-monitor.md)(§8.1 별도 노드로 한 이유) · [behavior_server BackUp](behavior-server-backup.md) |

**한 줄**: 출발점 시험 상자 · 서쪽 통로 옆에서 Nav2 가 '후보 전부 충돌' 로 서는 문제(지도상 여유 2~5 cm, 5 cm 칸 검사)에 대해, 10-13 에 패딩을 **늘 0** 으로 하는 안은 사용자가 기각했고("상자를 돌아가야지 더 붙어서 가는 건 문제", §11.1), 대신 **갇혔을 때만** 패딩을 0 으로 내렸다 0.15 m · 15 s 뒤 되돌리는 `pad_relief` 를 만들었다. 시뮬은 정지 자세 2 곳 × 5 씨앗 모두 탈출(10-13 §14.2 · 10-14 §2.1), 실행 중 변경 반영도 확인(§7.1: 풋프린트 −20.0 mm), 정지 시험 4/4(§8.6). f2r1 · f2r2 는 켜질 상황이 안 와 판정 불가(§9.1 · §9.5), f2t1 에서 처음 실제로 켜져 빠져나왔는데(§17), **그 순간부터 주행 끝까지 멈칫 · 좌우 틀기가 이어졌다**(§18: 좌우 틀기 /분 9.8~25.7 → 84.7~137.9). 정지 중 토글만 한 A/B 로 재현돼(§21.4) **'실행 중 패딩 변경 방식은 쓰지 않는다 · 바꿨으면 prep 으로 재기동'** 이 지금 규칙이다(CLAUDE.md §6). 기전은 미확인.

---

## 0. 지금 규칙 (먼저 읽을 것)
- **`pad_relief` 를 켜지 않는다**(`pad_relief:=on` 금지). 10-14 §21.4 판정 · §26 CLAUDE.md 갱신(`1c207f64`), 지금 CLAUDE.md §6 '갇힘 해제 `pad_relief`(10-14)' 줄.
- **실행 중에 코스트맵 풋프린트 · 패딩 값을 바꿨다면(되돌렸어도) 주행 전에 prep 으로 스택을 다시 띄운다.** 겉으로 보이는 값(파라미터 · 발행 풋프린트 · 코스트맵 값 분포)은 원래대로 돌아와도 동작은 안 돌아온다(§18 · §21.3 · §23).
  - 이 규칙에 걸리는 도구가 저장소에 남아 있다: `Docs/tools/chk_padding_dynamic.py` 는 **그 자체가 0.01 → 0 → 0.01 토글을 한다**(55~57 행) — 돌린 뒤에는 그 스택으로 주행하지 않는다(§4.4).
- 지금 표준 prep(`Docs/tools/prep_patrol.sh` → `prep_fast.sh`)은 `pad_relief` 를 아예 띄우지 않는다(launch 기본 off). CLAUDE.md 의 'prep 기본 shadow' 는 10-14 ~ 10-15 의 래퍼 `2026-10-14/jobs/prep_patrol_pad.sh` 이야기다(§4.4 · §6-1).

## 1. 증상
- **문제의 출발(10-13 §10 · §12.2)**: 복귀 길 시험 상자 끝 옆은 코스트맵 여유 2~5 cm 로 지나는 자리이고, 통과 · 정지가 1~2 cm 로 갈렸다. 멈추면 MPPI 후보가 전부 충돌(명령 0), BT 후진도 같은 풋프린트 검사에 막혀(10-13 f2o1 후진 3 회 실패, 10-14 §9.3) 빠져나올 수단이 없었다 → [상자 옆 정지 카드](box-side-stall-cause.md).
- **pad_relief 의 부작용(10-14 §18)**: 사용자 영상 3 개(`2026-10-14/videos/1_3번_지점까지.mp4` · `2_서남부_통로_주행모습.mp4` · `3_넓은_공간_이상_움직임.mp4`, git 제외) — "서남부 통로에서 자꾸 상자 쪽으로 방향을 틀고, 넓은 공간에서 멈칫거리며 움직이며 이것이 출발점까지 이어진다". 수치로는 f2t1 목표 4 에서 `pad_relief` 가 패딩을 내렸다 올린 순간부터([`hesitation.txt`](../debug_log/2026-10-14/outputs/hesitation.txt)):
  ```
  3 서쪽통로                         28 s   0.076 m/s       2 ( 4.3)             12 (25.7)            +0.4°             1.14
  4b 남서(복귀 뒤)                    52 s   0.031 m/s      13 (15.0)             83 (95.8)            -0.3°             1.02
  f2t1 W3남쪽→W3동쪽                181 s   0.042 m/s     121 (40.1)            416 (137.9)            -0.9°             1.16
  ```
  (열 = 구간 · 길이 · 평균 명령 v · 멈칫 횟수(분당) · ω 부호 바뀜(분당) · 지도 보정 각 변화 · EKF/휠 각속도 비. 같은 길 f2s2 는 0.068 m/s · 2.0 · 43.7 /분)

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-13 §11 · §11.1 | 패딩 0.01 → 0 사전 평가(시뮬, 판정 선언 뒤) — 장면 4 × 씨앗 10, `fpchk=1` | 상자 두 장면 멈춘 씨앗 **1/10 → 0/10**, 대신 최악 여유 2.7~2.8 → 1.6~1.7 cm, 통로 입구 0.4 cm · 실제 통과 구간 0.7 cm | '갇히는 문턱을 1 cm 낮추는' 대책(여유를 늘리지 않음). **사용자 기각**: "바뀐 비용이 너무 크다 … 상자를 돌아가야지 더 붙어서 가는 건 문제가 있다" → 방향 = '더 멀리 돌아간다' | [`sim_pad0_summary.txt`](../debug_log/2026-10-13/outputs/sim_pad0_summary.txt) · `jobs/run_sim_pad0.sh` · `anal_pad0_summary.py`(`2887e666`) |
| 10-13 §12.2 | 그날 대책 정리 | 감쇠 3.0 · BT 후진 · 패딩 0 · cost_weight 3 배 모두 기각 또는 되돌림 | 패딩은 0.01 그대로(저장소 · Jetson) | 10-13 §12.2 |
| 10-13 §14.2 | 사용자 지시 'stuck 때 파라미터 동적 조절 평가' → 실제 정지 자세 3 곳에서 pad 0.01 대 0, 씨앗 1~5, 15 s | f2o1 · f2p1: 0.01 은 5 씨앗 모두 150 주기 내내 실패 · 전진 0, **0 은 5/5 가 1.00~1.11 m 전진**, 최악 여유 1.9 · 2.5 cm. f2q1 은 둘 다 통과(대상 아님) | 선언 '쓸 만함' 충족(시뮬). 실제 정지 자세에서 시뮬이 정지를 5/5 재현 — 칸 단위 검사 기전 보강. 구현 전 확인 4 가지(켜고 끄는 주체 · 실행 중 반영 · 안전 · 사람 구분) | [`sim_unstuck_summary.txt`](../debug_log/2026-10-13/outputs/sim_unstuck_summary.txt) · `jobs/run_sim_unstuck.sh`(`4784683f`) · `anal_unstuck_summary.py` |
| 10-14 §2 · §2.1 | 되돌림 시뮬(`unstuck=1`: 후보 전부 충돌 2 s → 패딩 0, `us_d` 이동 또는 10 s 뒤 0.01), 30 s | 두 자세 × `us_d` 0.15 · 0.30 · 0.50 모두 5/5 가 1.21~1.29 m 전진, 재갇힘 0.30 의 한 씨앗 1 회, 패딩 0 시간 0.15 m 에서 2.1~2.4 s | **되돌림 0.15 m 후보**(가장 짧게 패딩 0). 한계: 실행 중 반영 미확인 · 복구 동작과 겹침 안 봄 | [`sim_unstuck2_summary.txt`](../debug_log/2026-10-14/outputs/sim_unstuck2_summary.txt) · `jobs/run_sim_unstuck2.sh` · `anal_unstuck2_summary.py`(`e392a6fc`) |
| 10-14 §3 | 시뮬 2 건 정리(금지 띠 0.30 · 갇혔을 때만 패딩 0) | 둘은 겹치지 않음(갇히지 않게 / 갇힌 뒤) | 결정 대기 | 10-14 §3 |
| 10-14 §7 · §7.1 | 사용자 "갇혔을 때만 패딩 0 확인부터" → 정지 확인(선언: 긴 · 짧은 변 20 ± 2 mm) | 0.01 → 0.0 받아들임(0.00 s), 풋프린트 **0.530 · 0.350 → 0.510 · 0.330 m(−20.0 · −20.0 mm)**, 복귀 뒤 원래대로. 내접 칸 1,241 → 1,235 → 1,238(치명 칸과 같이 흔들림) | **반영됨**. 내접 칸 수는 판별력 없는 지표. 범위 밖으로 둔 것 = 'MPPI 가 바뀐 풋프린트를 바로 쓰는지'(→ 뒤에 문제가 된 쪽은 '되돌린 뒤 무엇이 남는지' — 이 확인은 그것을 볼 설계가 아니었다, §5 실수 ②) | [`chk_pad_local.txt`](../debug_log/2026-10-14/outputs/chk_pad_local.txt) · [`prep_pad.txt`](../debug_log/2026-10-14/outputs/prep_pad.txt) · `Docs/tools/chk_padding_dynamic.py`(`164a4c17`) |
| 10-14 §8.1 · §8.2 | 사용자 "진행하자" → `pad_relief.py` 설계 · 정지 시험 선언 | 켜기 = /rosout 의 controller_server "fail to compute path" 3 s 안 3 회, 끄기 = 0.15 m 또는 15 s, 3 s 재켬 금지 · 60 s 4 회 상한 · 종료 때 복귀 · 기동 때 이미 0 이면 동작 안 함 · shadow | `stuck_monitor` 에 넣으려다 코드를 보고 별도 노드로(갇힘 = 명령 0 이라 '명령 대비 무이동' 판정에 안 걸림). 로그 문구에 묶인 임시방편 `TODO(improve)` | 10-14 §8.1, 커밋 `0f1d99b7` |
| 10-14 §8.3 ~ §8.5 | 정지 시험 시작 → Jetson 연결 끊김(10:27) · IP 충돌(사용자) | 두 주소 ping 무응답 · 그 뒤 "No route to host" | 시험 미실시. 연결 없이: SIGHUP 에도 복귀 · `run_detached.sh` · launch 인자(기본 off) | 10-14 §8.3 ~ §8.5, 커밋 `c08f43c3` · 네트워크 원인은 [Jetson Wi-Fi 카드](jetson-wifi-link.md) |
| 10-14 §8.6 | 네트워크 복구 뒤 정지 시험(가짜 실패 로그) | 2 회 → 안 켜짐 · 4 회 → 0.330 m · 15.3 s 뒤 0.350 m · 종료 때 0.350 m, 남은 프로세스 0 | **4/4 통과** → 주행 시험으로. 진짜 실패 로그의 문구 · 실제 탈출은 미확인 | [`chk_pad_relief.txt`](../debug_log/2026-10-14/outputs/chk_pad_relief.txt) · `jobs/chk_pad_relief.sh` |
| 10-14 §9 · §9.1 | f2r1(b910, pad_relief 켬) — 판정 선언(통과 / 판정 불가 / 실패) | 첫 기동에서 노드 죽음(`mode:=on` 이 bool) → 고쳐 다시 띄움. 3/3 성공 204.0 s, 11:26:39 실패 **2 회**(문턱 미달) 뒤 스스로 풀림, 상자 구역 최소 여유 2.4 cm | **판정 불가**. 진짜 실패 로그가 같은 문구로 옴(확인 1 건). 문턱 3 회는 '스스로 풀리면 안 끼어듦' 으로 동작 | [`prep_f2r1.txt`](../debug_log/2026-10-14/outputs/prep_f2r1.txt) · [`run_f2r1.txt`](../debug_log/2026-10-14/outputs/run_f2r1.txt) · [`after_f2r1.txt`](../debug_log/2026-10-14/outputs/after_f2r1.txt), 커밋 `f25e5f68` |
| 10-14 §9.2 | 사용자 "상자나 벽에 닿지 않았다. 이건 그냥 스스로 나온 건가?" | 실패 2 회(11:26:39.28 · .46) → 비우기 2 번 → 11:26:40.16 재시도부터 실패 없음, 정지 0.6 s, 치명 칸 **중심**까지 4.9 → 5.2 → 6.0 cm, 그 칸은 비우기 뒤에도 남음 | 그렇다 — 재시도가 0.9 s 만에 통함. 어제 14 회 실패와 갈린 것은 mm 단위(추정) | [`navlog_f2r1.txt`](../debug_log/2026-10-14/outputs/navlog_f2r1.txt) · [`f2r1_selfrecover.txt`](../debug_log/2026-10-14/outputs/f2r1_selfrecover.txt) · `Docs/tools/fig_stop_costmap.py` |
| 10-14 §9.3 | 사용자 "BT 를 수정하는 것으로는 해결하기 어려운가" | 표준 BT 노드로는 어려움(후진 · 회전도 같은 검사, 비우기는 2.5 m 남김, 파라미터 바꾸는 표준 노드 없음). 우리 BT 노드가 구조로는 나음 | 사용자 "일단 지금 상태로 진행하자" → 노드로 먼저 | 10-14 §9.3 |
| 10-14 §9.4 · §9.5 | f2r2(같은 구성) | 3/3 성공 224.1 s, 실패 0 회, 최소 여유 4.2 cm, 패딩 전환 없음 | **판정 불가**(다시). '켜 둬도 평소 주행에 안 끼어듦' 2 회. 사용자: 닿지 않음 · 1 번(순회로 넘어가고 켠 채로) | [`prep_f2r2.txt`](../debug_log/2026-10-14/outputs/prep_f2r2.txt) · [`run_f2r2.txt`](../debug_log/2026-10-14/outputs/run_f2r2.txt) · [`after_f2r2.txt`](../debug_log/2026-10-14/outputs/after_f2r2.txt) |
| 10-14 §15 · §15.1 | 구성 재검토 · 사용자 "CopyPath 가 pad_relief 를 필요 없게 만들지 않나" | CopyPath = 도착 뒤 방향 맞추기 정지, pad_relief = 가는 길 중간 정지(상자 옆 세 번은 목표에서 1.37~1.59 m) | **부분적으로만**. 선택지 ① 켬 ② shadow ③ 끔 → 사용자 ① "어차피 80 s 면 충분히 유지 가능하다"(감쇠 동안 실제 물체는 지도에 남음, 내주는 것은 1 cm) | 10-14 §15.1 |
| 10-14 §17 | f2t1(no5 8 목표, CopyPath 검증) — pad_relief **첫 실제 작동** | 목표 4 출발 직후 15:23:23.6~24.2 실패 4 회 · 후진 실패 → 15:23:24 패딩 0 → 대기 뒤 움직여 15:23:33 0.16 m 에서 0.01 복귀, 그 목표에서 재실패 없음. 8/8 성공, 접촉 없음(사용자) | 켜졌고 빠져나왔고 다시 안 갇힘. **대조가 없어 pad_relief 덕인지 못 가름**. 목표 7 · 8 이 느림(180.9 · 148.4 s) — 원인 안 봄 | [`navlog_f2t1.txt`](../debug_log/2026-10-14/outputs/navlog_f2t1.txt) 21~32 · 89~93 행 · [`run_f2t1.txt`](../debug_log/2026-10-14/outputs/run_f2t1.txt) · [`prep_f2t1.txt`](../debug_log/2026-10-14/outputs/prep_f2t1.txt) |
| 10-14 §18 | 사용자 영상 3 개 → `anal_hesitation.py` | 소켓 손실 0 · /tf 45~50 Hz · 지도 보정 · EKF/휠 비 정상. f2t1 목표 1~3 좌우 틀기 9.8~25.7 → **목표 4~8 84.7~137.9 /분**, 멈칫 15.0~40.1. 주행 뒤 패딩 · 풋프린트 · inflation · 발행 풋프린트 0.530 × 0.350 모두 원래대로 | **pad_relief 의 실행 중 패딩 변경이 가장 유력**, 기전 모름. 반례 '실패 · 최적화 초기화만 겪은 f2r1 은 뒤 19 s 멈칫 0' — ⚠ 같은 19 s 좌우 틀기는 10.5 → 44.2 /분(§5 실수 ③). 판단: shadow 로 내리고 다음 주행 전 재기동 | [`hesitation.txt`](../debug_log/2026-10-14/outputs/hesitation.txt) · `jobs/anal_hesitation.py`(`2fa622a2`) · `jobs/chk_after_relief.sh`(출력 원천 소실) |
| 10-14 §19.1 | 사용자 "1번 진행" → pad_relief shadow | 15:45:05 shadow 기동, 원래 패딩 0.010. f2t1 기록은 Jetson `/tmp/pad_relief_f2t1.log`(원천 소실, 핵심 줄은 `navlog_f2t1.txt` 89~93 행에 있음) | 래퍼 기본 shadow. **스택은 f2t1 그대로 → 다음 주행 전 prep** | `jobs/up_pad_shadow.sh` · `prep_patrol_pad.sh`(`7d809b9b`) |
| 10-14 §21 · §21.1 · §21.2 | A/B 설계 · 판정 선언(주행 전) | A `f2u1` = 새 스택 · B `f2u2` = A 끝난 스택에 정지 중 토글(`up_pad_toggle.sh`) · A2 `f2u3` = 다시 새 스택. 코스 b910, 비교 = 목표 2 · 3. 확정 = A · A2 깨끗(좌우 ≤ 45 · 멈칫 ≤ 6) AND B 좌우 ≥ 60 AND ≥ 2 × max(A, A2) | — | 10-14 §21.1 · §21.2, 커밋 `a57707c5` |
| 10-14 §21.3 | A · B | A 3/3 200.8 s, 토글 16:24:25 → 16:24:37(실제 12 s, f2t1 은 9 s), 47 s 뒤 B 3/3 232.0 s. 좌우 틀기 A 10.0 · 9.1 / **B 98.4 · 64.1**. params.txt A · B 같음, 로컬 코스트맵 값 분포 같음(값 23 개 · 팽창 꼬리 같음) | 컨트롤러 실패 · 초기화 없이 정지 중 토글만으로 재현 → 실패와의 조합은 필요 조건 아님. 후보 = CostCritic 외접 비용 저장 경쟁 조건(크기 설명 부족 ？) | [`run_f2u1.txt`](../debug_log/2026-10-14/outputs/run_f2u1.txt) · [`run_f2u2.txt`](../debug_log/2026-10-14/outputs/run_f2u2.txt) · 목표별 좌우 틀기 출력 **원천 소실** · `anal_lc_hist.py` 출력 원천 소실, 커밋 `176bda33` |
| 10-14 §22 · §22.1 | B 복귀 길 상자 옆 5 s 정지 · "오늘 바꾼 것과 관계있나" | 16:30:07 · 08.5 · 14.0 실패, pad_relief(shadow) 기록 없음(간격 1.2 · 5.5 s 로 '3 s 안 3 회' 미충족) | pad_relief 는 관계 없음(아무것도 안 함). 같은 자리는 f2r1 에서도 실패 — 패딩 토글과 무관하게 원래 실패가 나는 곳 | [상자 옆 정지 카드](box-side-stall-cause.md) · `outputs/anal_box_f2u2.txt` |
| 10-14 §21.4 | A2 와 판정 | A2 3/3 201.5 s, 실패 0. 좌우 틀기 14.7 · 19.6, 멈칫 1.2 · 3.0 | **판정: 실행 중 footprint_padding 변경(0.01 → 0 → 0.01)이 멈칫 · 좌우 틀기의 원인으로 확정**. pad_relief 방식 금지, 기본 off · prep shadow 유지, 같은 방식(실행 중 풋프린트 · 패딩 변경) 대책 모두 보류 — ⚠ 10-15 §15 · §16 이 범위를 좁힘(아래) | [`run_f2u3.txt`](../debug_log/2026-10-14/outputs/run_f2u3.txt) · 목표별 수치 원천 소실 |
| 10-14 §23 | 토글 뒤 무엇이 달라졌나 | 제어 주기 /cmd_vel 중앙 50 ms · 궤적 100 ms · 로컬 지도 0.60 s 세 주행 같음. **비용 0 인 '빈 곳'(반경 0.4 m)에서도 B 84.1 /분**(A 5.1 · A2 18.7) | 같은 입력에 MPPI 가 다른 답. **CostCritic 가설 기각**(CostCritic 이 아무 일 안 하는 곳에서도 재현). 남은 곳 = 경로 · 목표 크리틱 · 최적화기 ？. 읽은 코드 안에서는 패딩 → MPPI 상태 경로를 못 찾음 | [`anal_free_wobble_f2u.txt`](../debug_log/2026-10-14/outputs/anal_free_wobble_f2u.txt) · [`anal_ctrl_timing_f2u.txt`](../debug_log/2026-10-14/outputs/anal_ctrl_timing_f2u.txt)(CPU 열 nan — CPU 317 · 303 · 309 % 는 원천 소실), 커밋 `a637877b` |
| 10-14 §25 · §26 | 사용자 결정 · 마무리 | prep_fast 에 직전 nav2 · slam · sensors 기록 보관(§24 에서 B 의 nav2.log 를 잃은 것 때문) | CLAUDE.md §6 pad_relief 줄 '켜지 않는다(A/B 확정)', 상태: shadow 로 떠 있음 · 다음 주행 전 prep | 10-14 §25 · §26, 커밋 `1c207f64` |
| 10-15 §3 · §18.1 · §20.1 | 기준선 f2v1 · f2v3 · f2v4(새 스택마다 `prep_patrol_pad.sh lite 15.0 shadow`) | 세 번 모두 Nav2 중단(후보 전부 충돌 → 후진 실패 → 대기 × 2 → Goal failed 약 12 s), **세 번 모두 shadow 가 '바꿀 상황' 을 기록**(10:15:54 · 13:24:08 · 14:02:04), 패딩은 그대로. 성공한 f2v2 에는 기록 없음 | f2v1 자리는 f2t1 에서 pad_relief 뒤 탈출했던 같은 자리 → '어제 탈출에 기여했을 가능성'(추정, 반사실 확인 안 됨, §5: 패딩 0 이면 3~4 cm 대가 4~5 cm 대) | [`navlog_f2v1.txt`](../debug_log/2026-10-15/outputs/navlog_f2v1.txt) 74~78 행 · [`navlog_f2v3.txt`](../debug_log/2026-10-15/outputs/navlog_f2v3.txt) 65~69 행 · [`navlog_f2v4.txt`](../debug_log/2026-10-15/outputs/navlog_f2v4.txt) |
| 10-15 §15 | f2v2(패딩 변경 없는 새 스택) | 8/8, 좌우 틀기 목표 1~3 11.8 · 10.9 · 21.4 → **목표 4~8 49.3 · 37.5 · 86.4 · 110.1 · 60.6** | **패딩 변경 없이도 잔떨림이 생긴다** → 10-14 §21 은 '충분 조건' 으로는 맞지만 유일한 원인은 아님(정정 필요 ？) | [`anal_hesitation_f2v2.txt`](../debug_log/2026-10-15/outputs/anal_hesitation_f2v2.txt) |
| 10-15 §16 | 사용자 육안 "넓은 통로에서 멈칫 · 좌우 틀기가 보이지 않았다" → `anal_wiggle_amp.py` | f2t1 목표 7 멈칫 40.2 · 평균 v 0.042 / f2v2 목표 7 멈칫 0.6 · v 0.079 / B 목표 2 멈칫 2.4 · 부호 바뀜 96.6 | 두 현상: ① **보이는 멈칫**(f2t1) ② **안 보이는 잔떨림**(f2v2 후반 · B). 기준 ⑥ 과 10-14 A/B 가 확정한 것은 주로 ②. ① 의 원인으로는 f2t1 의 pad_relief 작동이 여전히 가장 유력하나 **A/B 로 직접 확정된 것은 아님** | [`anal_wiggle_amp.txt`](../debug_log/2026-10-15/outputs/anal_wiggle_amp.txt) · `jobs/anal_wiggle_amp.py`(`d4dc24cb`) |
| 10-15 §25 | 갇힘 탈출을 다시 설계 | '여유가 줄지 않는 곧은 이동' — **실행 중 파라미터 변경 없음(pad_relief 의 멈칫 부작용 없음)** 을 설계 조건에 넣음, 실패 5 건 중 5 건 통과(오프라인) | → MonotoneEscape(10-15 §26 ~) | [상자 옆 정지 — 대책 카드](box-side-stall-remedies.md) |
| 이후(10-19 ~) | 다음 시기에서 채움 | — | — | — |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 패딩을 내리면 상자 옆 갇힘이 풀린다 | 시뮬(10-13 §11 · §14.2 · 10-14 §2.1) | 상자 장면 멈춘 씨앗 1/10 → 0/10, 정지 자세 2 곳 × 5 씨앗 모두 탈출 | **지지(시뮬)** — 실주행 대조는 없음(f2t1 1 회, 대조 없음) |
| 되돌린 뒤 다시 갇힌다 | 시뮬 `us_d` 0.15 · 0.30 · 0.50 | 재갇힘 30 회 중 1 회(0.30), 실주행 f2t1 은 그 목표에서 재실패 없음 | **기각(시뮬 · 1 회 주행)** |
| Nav2 Humble 이 실행 중 `footprint_padding` 변경을 반영한다 | `chk_padding_dynamic.py` 정지 확인 | 풋프린트 −20.0 mm · 복귀 | **지지(측정)** — 반영 여부만. 내접 반경 재계산은 칸 수로 못 가름 |
| f2t1 뒤 멈칫 · 좌우 틀기의 원인 = 실행 중 패딩 변경 | A/B(정지 중 토글만) | B 98.4 · 64.1 /분, A · A2 ≤ 19.6 | **지지(측정, 1 회 토글 · 1 회 B)** — 단 측정량은 주로 잔떨림(10-15 §16) |
| 원인 = 컨트롤러 실패 뒤 최적화 초기화(잡음 표본 교체) | f2r1(패딩 변경 없이 실패 2 회) · B(실패 없이 토글) | B 는 실패 없이 재현. f2r1 뒤 19 s 는 멈칫 0 이지만 좌우 틀기 44.2 /분 · 10-15 f2v2 는 실패 1 회 뒤 잔떨림 | **필요 조건 아님(지지)** · '초기화도 잔떨림을 늘린다' 는 **미확인**(짧은 표본, 10-15 §15 '결론 못 냄') |
| 토글 뒤 '오래 돈 스택' 이 원인 | A2(다시 새 스택) | A2 깨끗 | 이 대조로 가른 것은 '스택을 새로 띄우면 사라진다' 까지. B 가 A 뒤 연속 스택이라 '오래 돈 것' 만으로 생기는지는 따로 안 봄(10-15 f2v2 는 새 스택인데 목표 4 부터 잔떨림 — 같은 질문으로 남음) |
| 토글이 겉으로 보이는 값을 바꾼다 | params.txt diff · 로컬 코스트맵 값 분포 · 발행 풋프린트 · `chk_after_relief.sh` | 모두 같음 | **기각(측정)** — 상태는 보이지 않는 곳에 |
| CostCritic 외접 비용 저장 경쟁 조건 | 빈 곳(반경 0.4 m 비용 0)만 골라 좌우 틀기 | B 빈 곳 84.1 /분 | **기각** — CostCritic 이 건너뛰는 곳에서도 재현 |
| 계산 부하 · 입력 주기가 달라졌다 | `anal_ctrl_timing.py` | 주기 · 지도 간격 같음 | **기각(주기)** · CPU 는 원문 소실 |

## 4. 조치와 효과
### 4.1 시뮬 인자 `pad` · `unstuck`(10-13 · 10-14)
- `Docs/tools/anal_mppi_sim.py` 에 `pad`(기본 0.01, `2887e666`)와 `unstuck=1`(`e392a6fc`). 실행 중 변경 흉내는 **충돌 검사 꼭짓점만** 바꾼다(지금 178~181 행, 그날 판 154~157 행 같은 내용):
  ```python
  def set_pad(p_):
      """실행 중 패딩 변경(unstuck 용): fpchk=1 의 꼭짓점만 바꾼다(코스트맵 inflation 은 기록된 것 그대로)."""
  ```
  → 시뮬은 '되돌린 뒤 MPPI 가 계속 떠는' 부작용을 원리상 낼 수 없었다. 시뮬의 '쓸 만함' 은 충돌 판정 쪽만의 결론이다.
- 결과 발췌(`2026-10-14/outputs/sim_unstuck2_summary.txt`): `f2o1     0.15   +1.28 +1.24 +1.29 +1.26 +1.23   5 / 5    1 1 1 1 1         2.1  2.1  2.2  2.1  2.1     0           2.0             0`.

### 4.2 `pad_relief` 노드(10-14 §8, 지금 `ros2_ws/src/rover_bringup/scripts/pad_relief.py`)
- 판정 · 조치 핵심(지금 판 76 · 90 · 98 행, 10-14 마지막 커밋 `f25e5f68` 이후 변경 없음):
  ```python
  if self.fail_node in m.name and self.fail_text in m.msg: self.fails.append(time.time())          # /rosout 의 controller_server 'fail to compute path'
  if len(self.fails) >= self.trig_n and now - self.t_off >= self.cooldown:                          # 3 s 안 3 회 · 되돌린 뒤 3 s
  if moved >= self.restore_dist or now - self.t_on >= self.max_hold:                                 # 0.15 m(/odometry/filtered) 또는 15 s
  ```
  조치는 `/local_costmap/local_costmap/set_parameters` 로 `footprint_padding` 하나만(전역 · 계획기 · 스무더는 그대로 — 2 번째 `TODO(improve)`).
- 실제 작동 1 회(f2t1, `2026-10-14/outputs/navlog_f2t1.txt` 89~93 행):
  ```
  15:19:37 원래 패딩 0.010 확인
  15:23:24 패딩 → 0.000 (후보 전부 충돌 3 회/3 s, 1 번째) 적용
  15:23:33 패딩 → 0.010 (0.16 m 이동) 적용
  ```
- 효과: 그 목표는 탈출(대조 없음), **대가: 주행 끝까지 좌우 틀기 84.7~137.9 /분 · 멈칫 15.0~40.1 /분**, 목표 7 · 8 이 f2s2 의 118 · 104 s → 180.9 · 148.4 s(§17 · §18).

### 4.3 A/B 와 그 뒤 처리(10-14 §21 ~ §26)
- B 조건 도구 `2026-10-14/jobs/up_pad_toggle.sh`(`a57707c5`) — pad_relief 와 같은 서비스 · 값:
  ```bash
  echo "$(date +%T.%N | cut -c1-12) → 0.0 : $(timeout 12 ros2 param set $P footprint_padding 0.0 2>&1 | tail -1)"
  sleep 9
  echo "$(date +%T.%N | cut -c1-12) → 0.01: $(timeout 12 ros2 param set $P footprint_padding 0.01 2>&1 | tail -1)"
  ```
  출력(16:24:25 → 16:24:37, 끝 값 0.01)은 **원천 소실**(SUMMARY §21.3 서술만).
- 판정 수치(SUMMARY §21.4 표): 목표 2 좌우 틀기 A 10.0 · B 98.4 · A2 14.7, 목표 3 9.1 · 64.1 · 19.6 — `anal_hesitation.py` 출력이 파일로 남지 않아 **원천 소실**. 같은 bag 목표 2 를 10-15 `anal_wiggle_amp.py` 가 다시 셌다(문턱 0.05, `2026-10-15/outputs/anal_wiggle_amp.txt`):
  ```
  f2u1_목표2(A깨끗)        0.072     3.7       9.8 ·   7.4 ·   2.5              0.033          0.040          4.69
  f2u2_목표2(B토글)        0.076     2.4      96.6 ·  47.1 ·   7.1              0.070          0.058          3.80
  f2u3_목표2(A2)         0.075     2.4      15.6 ·   6.0 ·   3.6              0.034          0.041          4.35
  ```
  (§21.4 의 10.0 · 98.4 · 14.7 과 0.2~1.8 차 — 구간 경계 차로 추정. 멈칫 열은 3.7 · 2.4 · 2.4 로 §21.4 의 2.5 · 1.2 · 1.2 와 다름 → 이것도 구간 경계로 추정, 미확인)
- 빈 곳 결과(`2026-10-14/outputs/anal_free_wobble_f2u.txt`): `B           41 s        84.1                 122 s             72.6`.
- 처리: pad_relief 기본 off 유지 · 래퍼 shadow(10-14 §19.1 · §21.4), CLAUDE.md 갱신(§26). 그 뒤 shadow 는 10-15 실패 3 건(f2v1 · f2v3 · f2v4)에서 모두 '바꿀 상황' 을 기록했다 — **켰다면 세 번 다 작동했을 자리**(이번 확인, 각 `navlog_f2v*.txt`). 켰을 때 빠져나왔을지는 모름.

### 4.4 지금 저장소 코드(11-03 확인, 고치지 않음)
| 항목 | 지금 | 위치 |
|---|---|---|
| 노드 파라미터 | `mode` 기본 **'on'** · `relief` 0.0 · `trig_n` 3 · `trig_win` 3.0 · `restore_dist` 0.15 · `max_hold` 15.0 · `cooldown` 3.0 · `max_per_min` 4 · `fail_text` 'fail to compute path' · `fail_node` 'controller_server' · `log_path` /tmp/pad_relief.log | `ros2_ws/src/rover_bringup/scripts/pad_relief.py` 35~37 행 |
| ⚠ 노드 설명 | 머리 설명(1~22 행)에 10-14 §21 의 부작용 경고가 없다 — '왜 필요한가' 와 시뮬 근거만. 인자 없이 직접 띄우면 `mode` 기본 on 으로 **실제로 패딩을 바꾼다** | 같은 파일 2~22 · 35 행 |
| bool → 문자열 | `{True: 'on', False: 'off'}` 로 되돌림(10-14 §9.1 수정) | 같은 파일 40~41 행 |
| 안전장치 | 기동 때 이미 0 이면 동작 안 함 · SIGTERM · SIGHUP 에 복귀 | 같은 파일 68~69 · 116~117 행 |
| launch 인자 | `pad_relief` 기본 **'off'**, on · shadow 일 때만 노드 기동 | `ros2_ws/src/rover_navigation/launch/navigation.launch.py` 231~234 행 |
| ⚠ launch 주석 | "기본 off — 정지 시험·주행 검증 전이다" — 지금 off 인 이유(A/B 부작용)와 다름 | 같은 파일 229~230 행 |
| 설치 | `scripts/pad_relief.py` 설치 목록에 있음 | `ros2_ws/src/rover_bringup/CMakeLists.txt` 39 행 |
| 표준 prep | `EXTRA_NAV="global_camera:=nvblox replan_hz:=… $V ${NAV_ADD:-}"` — `pad_relief` 인자 없음 → **launch 기본 off, 노드 안 뜸**. `prep_fast.sh` 에도 pad_relief 없음(grep 0) | `Docs/tools/prep_patrol.sh` 17 행 |
| 10-14 ~ 10-15 래퍼 | `mode:=${3:-shadow}` — CLAUDE.md 'prep 기본 shadow' 의 출처. 10-22 SUMMARY 9 행 "pad_relief.py · prep_patrol_pad.sh 는 지금 구성에서 안 씀" | `Docs/debug_log/2026-10-14/jobs/prep_patrol_pad.sh` 6 행 |
| ⚠ 확인 도구가 토글을 함 | `for v, tag in ((0.0, '0.0 으로'), (ORIG[k], '처음 값으로 복귀')): … setpad(k, v)` — 돌리면 그 스택은 10-14 §21 의 B 와 같은 상태가 된다. 머리 설명 · `Docs/tools/README.md` 25 행 모두 경고 없음 | `Docs/tools/chk_padding_dynamic.py` 55~57 행 |
| 패딩 · 풋프린트 원본 | 로컬 · 전역 `footprint_padding: 0.01`, `footprint` 앞 0.262 · 뒤 0.248 · 반폭 0.165 | `ros2_ws/src/rover_navigation/config/nav2_params.yaml` 321 · 556 행(패딩), 303 · 538 행(풋프린트) |
| 실행 중 변경 여부 자동 검사 | 없음 — `chk_prep.py` · `chk_drive_gate.py` · `prep_fast.sh` 에 padding · footprint 문자열 0 건. '바꿨으면 재기동' 은 사람이 지키는 규칙 | (grep) |
| 후속 대책의 기각 근거 | "실행 중 파라미터 변경 없음(10-14 pad_relief 의 멈칫 부작용 없음)" · "기각한 대안: pad_relief" | `ros2_ws/src/rover_navigation/src/monotone_escape_behavior.cpp` 8 · 16 행 |
| 다른 실행 중 변경 | 코스트맵 · 컨트롤러 파라미터를 바꾸는 코드는 저장소에 위 두 곳(pad_relief · chk_padding_dynamic)뿐(`set_parameters` grep). 10-13 §12.1 의 `ros2 param set … CostCritic.cost_weight` 는 그날 손으로 한 것 | (grep) |

## 5. 내 실수
### 실수 ① `mode:=on` 이 YAML 참(bool)으로 읽혀 노드가 죽음 (10-14 §9.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2r1 전 `prep_patrol_pad.sh lite 15.0 on` 으로 pad_relief 를 켜고 주행 |
| 본 것 | `prep_f2r1.txt` 47 행 `pad_relief: 0 개 실행 · ` |
| 처음 추론 | (없음 — 바로 노드 로그 확인) |
| 의심한 이유 | 정지 시험(§8.6)은 인자 없이(기본 on) 띄워 통과했는데 인자를 주자 죽음 |
| 판별 시험 | `prep_pad_only.sh` 가 이전 실패 원인(`/tmp/pad_relief_node.log` 끝 3 줄)을 출력 → 형 불일치 |
| 결론 | 명령줄 · launch 인자 모두 `on`/`off` 는 bool 로 읽힌다. `dynamic_typing=True` + bool → 문자열 변환으로 고침. 주행 전에 잡힘 |
| 다음에 알아보는 법 | 문자열 파라미터에 on · off · yes · no · true 같은 값을 쓰면 YAML 형 변환을 먼저 의심. prep 출력에 노드 개수 줄을 두는 것(이번에 잡은 장치)을 유지 |
| 스크립트 핵심 | `pad_relief.py` 41 행 `self.mode = {True: 'on', False: 'off'}.get(g('mode'), str(g('mode')))` |
| 나온 결과 | `  pad_relief: 0 개 실행 · ` (`2026-10-14/outputs/prep_f2r1.txt` 47 행) — 노드 오류 원문은 원천 소실 |
| 데이터 | `2026-10-14/outputs/prep_f2r1.txt`, 도구 `2026-10-14/jobs/prep_pad_only.sh` · `prep_patrol_pad.sh`, 커밋 `f25e5f68` |

### 실수 ② 시뮬 · 정지 확인이 '부작용' 을 볼 수 없는 설계인데 그 한계를 다음 단계 판단에 넣지 않음 (10-14 §2.1 · §7.1 → §9)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 실행 중 패딩 변경을 주행에 쓰기 전에 안전성 확인 |
| 본 것 | 시뮬 5/5 탈출 · 재갇힘 0(§2.1), 풋프린트 −20.0 mm 반영(§7.1), 정지 시험 4/4(§8.6) |
| 처음 추론 | 남은 미확인은 'MPPI 가 줄어든 풋프린트를 바로 쓰는지' 뿐 → 주행 시험으로 |
| 의심한 이유 | f2t1 에서 작동 뒤 멈칫이 주행 끝까지(§18), 겉 값은 원래대로 |
| 판별 시험 | A/B(§21) |
| 결론 | 시뮬의 `set_pad` 는 충돌 검사 꼭짓점만 바꾸므로 '되돌린 뒤 남는 상태' 를 낼 수 없고, §7 확인은 '바뀌는가' 만 보도록 선언됐다. 세 단계 모두 '되돌린 뒤 평소 주행이 같은가' 를 보지 않았다. f2r1 · f2r2 는 켜지지 않아 그것도 못 봄 |
| 다음에 알아보는 법 | 실행 중 상태를 바꾸는 대책은 '바꾼 뒤 · 되돌린 뒤 같은 코스 지표(좌우 틀기 · 멈칫)가 새 스택과 같은가' 를 정지 토글 + 짧은 주행으로 먼저 본다(§21 설계가 그 형태) |
| 스크립트 핵심 | `Docs/tools/anal_mppi_sim.py` 178~179 행 `def set_pad(p_): """실행 중 패딩 변경(unstuck 용): fpchk=1 의 꼭짓점만 바꾼다(코스트맵 inflation 은 기록된 것 그대로)."""` |
| 나온 결과 | `    실행 중 값 0.01 | 긴 변 변화 -0.0 mm · 짧은 변 변화 -0.0 mm · 내접 칸 -3` (`2026-10-14/outputs/chk_pad_local.txt` 8 행 — '되돌아왔다' 까지만 보는 출력) |
| 데이터 | `2026-10-14/outputs/sim_unstuck2_summary.txt` · `chk_pad_local.txt` · `hesitation.txt` |

### 실수 ③ (이번 확인) §18 의 반례 'f2r1 은 실패 · 초기화 뒤 19 s 멈칫 0 회' 는 같은 표에서 좌우 틀기가 4 배로 늘어 있었다 (10-14 §18)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | '실패 뒤 최적화 초기화로 잡음이 바뀌어서' 라는 다른 설명을 가르기 |
| 본 것 | f2r1 목표 3 실패 뒤 19 s: 멈칫 0 |
| 처음 추론 | 초기화만으로는 멈칫이 안 생김 → 패딩 변경이 가장 유력 |
| 의심한 이유 | 같은 출력 줄의 부호 바뀜이 실패 전 10.5 → 실패 뒤 44.2 /분. 10-15 §15 도 같은 비교를 '결론 못 냄' 으로 둠(값은 23.7 /분 — 원문 없음) |
| 판별 시험 | 없음(19 s 짧은 표본). A/B 는 이 설명과 무관하게 '토글만으로 재현' 을 보였으므로 판정에는 영향 없음 |
| 결론 | §18 의 반례는 '보이는 멈칫' 에 대해서만 맞고, 잔떨림은 실패 · 초기화 뒤에도 늘었을 수 있다 — 10-15 §15 · §16 의 정정 방향과 같음 |
| 다음에 알아보는 법 | 두 지표(멈칫 · 좌우 틀기)를 함께 낸 표에서 반례를 들 땐 두 열을 모두 읽는다 |
| 스크립트 핵심 | `2026-10-14/jobs/anal_hesitation.py` 32 행 `ws = np.sign(np.where(np.abs(w) > 0.05, w, 0)); ws = ws[ws != 0]; flips = int((ws[1:] != ws[:-1]).sum())` |
| 나온 결과 | `f2r1 목표3 실패 전                  86 s   0.072 m/s       1 ( 0.7)             15 (10.5)` · `f2r1 목표3 실패 뒤                  19 s   0.075 m/s       0 ( 0.0)             14 (44.2)` (`2026-10-14/outputs/hesitation.txt` 17~18 행) |
| 데이터 | `2026-10-14/outputs/hesitation.txt`, bag `2026-10-14/bags/bag_f2r1.tgz`(로컬) |

### 실수 ④ '원인으로 확정' 의 범위 — 측정량이 잔떨림이었고 유일 원인도 아님 (10-14 §21.4 → 10-15 §15 · §16 정정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 영상의 '멈칫거림' 원인을 A/B 로 확정 |
| 본 것 | B 좌우 틀기 98.4 · 64.1 /분, 멈칫은 목표 3 만 12.3(목표 2 1.2) |
| 처음 추론 | "멈칫거림·좌우 틀기의 원인으로 확정" |
| 의심한 이유 | 10-15 f2v2(패딩 변경 없음)가 목표 4 부터 좌우 틀기 49~110 /분, 사용자 육안은 "안 보였다" |
| 판별 시험 | `anal_wiggle_amp.py` — 문턱 3 단 · 명령/실제 ω 고주파 RMS |
| 결론 | 지표 ⑥(|ω| > 0.05 부호 바뀜)은 눈에 안 보이는 잔떨림을 주로 셌다. A/B 가 확정한 것 = '실행 중 패딩 토글은 잔떨림을 만든다(충분 조건)'. 보이는 멈칫(f2t1)의 원인으로는 pad_relief 작동이 가장 유력하나 직접 확정은 아님. CLAUDE.md §6 의 '멈칫·좌우 틀기(A/B 확정)' 도 이 범위로 읽어야 함 |
| 다음에 알아보는 법 | '흔들림' 지표는 크기(RMS)와 보이는 사건(속도 떨어짐)을 따로 낸다 — 10-15 §17 새 ⑥ |
| 스크립트 핵심 | `2026-10-15/jobs/anal_wiggle_amp.py`(머리 설명: 부호 바뀜을 0.05 · 0.10 · 0.20 rad/s 로, ω 는 1 s 이동평균을 뺀 고주파 RMS) |
| 나온 결과 | `f2v2_목표7(오늘)         0.079     0.6     109.1 ·  46.8 ·   4.0              0.066          0.060          2.56` · `f2t1_목표7(어제멈칫)       0.042    40.2     137.2 ·  20.1 ·   1.6              0.056          0.049          1.75` (`2026-10-15/outputs/anal_wiggle_amp.txt`) |
| 데이터 | `2026-10-15/outputs/anal_wiggle_amp.txt` · `anal_hesitation_f2v2.txt` |

### 작은 실수 — A 첫 러너를 Git Bash 에서 불러 '러너 없음' (10-14 §21.3)
로버 안 움직임 · DDS 참여자 없음 → WSL 로 다시. A/B 결과에는 영향 없음.

## 6. SUMMARY · 정리 페이지 ↔ 원문 어긋남 (이번 확인)
| # | 기록 | 원문 | 판정 |
|---|---|---|---|
| 1 | CLAUDE.md §6 "launch `pad_relief:=off\|on\|shadow`(기본 off, **prep 기본 shadow**)" | 지금 표준 prep `Docs/tools/prep_patrol.sh` 17 행에 pad_relief 인자 없음 → 노드 안 뜸. shadow 기본은 `2026-10-14/jobs/prep_patrol_pad.sh` 6 행(10-14 ~ 10-15 사용), 10-22 SUMMARY 9 행 "지금 구성에서 안 씀" | CLAUDE.md 문구가 10-15 까지의 상태 — 지금은 '표준 prep 은 안 띄움' (고치지 않음, 보고만) |
| 2 | 10-14 §9.2 '치명 칸 중심까지 차체 여유 4.9 cm' vs §9.1 '상자 구역 최소 여유 2.4 cm' | `fig_stop_costmap.py` 72 행 "치명 칸 중심까지(칸 반폭 2.5 cm 는 빼지 않음)" · `anal_box_pass.py` 4 행 '치명 칸 가장자리 거리', 계산식 끝 `- res / 2` | **정의 차이 확인(코드)** — 4.9 − 2.5 = 2.4 로 같은 순간의 같은 양으로 맞음. f2o1 4.8 · f2p1 5.4(중심) 와 1.8 · 2.2(가장자리)는 시각이 달라 2.5 차가 아님 |
| 3 | 10-14 §21.3 · §21.4 목표별 좌우 틀기 · 멈칫 표, 10-14 정리 페이지 막대그래프 | `anal_hesitation.py` A · B · A2 출력 파일 없음 | **원천 소실**(정리 페이지도 그렇게 표시). 10-15 `anal_wiggle_amp.txt` 가 목표 2 만 다시 셈(9.8 · 96.6 · 15.6, §4.3) |
| 4 | 10-14 §23 'controller_server CPU 317 · 303 · 309 %' | `anal_ctrl_timing_f2u.txt` CPU 열 `nan /   nan  (0 표본)` | **원천 소실**(이 도구가 낸 값이 아님 — 'proc 기록의 tick' 계산은 파일 없음) |
| 5 | 10-14 §21.3 'params.txt A · B 시각 줄만 빼고 같다' | params.txt 는 bag 묶음 안(`2026-10-21/bags/bag_f2u1.tgz` 에 `bag_f2u1/params.txt` 있음 · `bag_f2u3.tgz` 도 같은 꼴). **B `bag_f2u2` 는 로컬 `Docs/debug_log/*/bags` 에 없음** | B 쪽 원문 원천 소실 · diff 출력도 없음 |
| 6 | 10-14 §18 표 '4 남서(복귀 뒤) 0.031 · 15.0 · 95.8' | `hesitation.txt` 는 4a(패딩 내리기 전 3 s, 20.0 · 20.0) · 4b(52 s) 로 나눔 | 일치(4b). 4a 줄은 SUMMARY 에 없음 |
| 7 | 10-15 §15 "10-14 f2r1 … 실패 앞 11~13 → 뒤 23.7 /분" | `hesitation.txt` 같은 구간 10.5 · 11.5 → **44.2 /분** | 23.7 의 원문 없음(원천 소실) — 원문 기준 44.2. 실수 ③ |
| 8 | 10-14 §17 'pad_relief 기록은 Jetson `/tmp/pad_relief_f2t1.log` 로 보관'(§19.1) | Jetson /tmp(휘발) | 원천 소실 — 단 핵심 3 줄은 `navlog_f2t1.txt` 89~93 행에 남음 |
| 9 | 10-14 §18 `chk_after_relief.sh` "주행 뒤 패딩 0.01 · 풋프린트 · inflation · 발행 풋프린트 0.530 × 0.350 원래대로" | 출력 파일 없음 | 원천 소실(SUMMARY 서술만) |
| 10 | 10-14 §21.3 `up_pad_toggle.sh` '16:24:25 → 16:24:37(실제 12 s)' | 출력 파일 없음 | 원천 소실 |

## 7. 남은 것 (10-15 시점) · 이후
- **기전 미확인**: 실행 중 패딩 토글이 MPPI(또는 controller_server)의 어디에 상태를 남기는지. 10-14 §23 이 제안한 판별 — ⓐ 같은 값(0.01 → 0.01)으로 다시 설정해도 생기는가(값 변화 없이 콜백만) ⓑ 토글 뒤 controller_server 만 lifecycle 재활성하면 사라지는가 ⓒ 설치판 태그의 optimizer · 나머지 크리틱 · nvblox_nav2 층 `onFootprintChanged` 읽기 · ⓓ job419 시뮬로 재현 — **이 시기엔 하나도 안 함**.
- A/B 는 토글 1 회 · B 1 회. '토글 간격 12 s vs 9 s' · '전역 패딩은 안 바꿈' 조건만 봤다.
- 10-15 f2v2 처럼 **패딩 변경 없이도 잔떨림이 생긴다** — 그 원인(실패 · 초기화 뒤인지, 구간 특성인지)은 이 카드 밖으로 남음([W3 저속 떨림 카드](tf-lag-w3-wobble.md) · [MPPI 흔들림 카드](mppi-wobble-temperature.md)와 같은 계열).
- pad_relief 가 실제로 탈출을 도왔는지 반사실 확인 없음 — f2t1 1 회, 10-15 shadow 3 회('켰다면 작동')는 모두 패딩 그대로 Goal failed.
- '바꿨으면 재기동' 을 기계가 지키지 않는다(§4.4 자동 검사 없음) · `chk_padding_dynamic.py` 는 토글을 하는 도구 그대로.
- 노드는 저장소 · 설치 목록에 남음(기본 off). BT 노드화(10-14 §9.3 · §15 미룬 것)는 MonotoneEscape 로 방향이 바뀌어 안 함.
- **이후(10-19 ~): 다음 시기에서 채움** — 알려진 포인터만: 10-19 §… Jetson src 에 `pad_relief.py` 가 없어 첫 빌드 설치 단계 실패 → 저장소 판 보충(기본 off, `2026-10-19/SUMMARY.md` 94 행) · 10-22 prep 재전송에서 'pad_relief.py · prep_patrol_pad.sh 는 지금 구성에서 안 씀'(`2026-10-22/SUMMARY.md` 9 행) · 10-23 구성 정리 'pad_relief(사실상 꺼짐)'(`2026-10-23/SUMMARY.md` 203 행).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| sim pad0 | 패딩 0 상시 — 장면 4 × 씨앗 10 | 10-13 §11.1, `outputs/sim_pad0_summary.txt` |
| sim unstuck · unstuck2 | 정지 자세 3 곳 pad 0.01 대 0 · 되돌림 `us_d` 3 값 | 10-13 §14.2 `sim_unstuck_summary.txt` · 10-14 §2.1 `sim_unstuck2_summary.txt` |
| 정지 확인 · 정지 시험 | 실행 중 패딩 반영 · pad_relief 4 단계 | 10-14 §7.1 `chk_pad_local.txt` · `prep_pad.txt`, §8.6 `chk_pad_relief.txt` |
| f2r1 · f2r2 | b910, pad_relief 켬 — 판정 불가 × 2 | 10-14 §9 ~ §9.5, `prep_f2r{1,2}.txt` · `run_f2r{1,2}.txt` · `after_f2r{1,2}.txt` · `navlog_f2r1.txt` · `f2r1_selfrecover.txt`, bag `2026-10-14/bags/bag_f2r{1,2}.tgz`(로컬), 그림 `Docs/04_navigation/figures/2026-10-14_f2r1_box_selfrecover.png` |
| f2s1 · f2s2 | no5 앞 · 뒤(pad_relief 켬, 전환 없음) | 10-14 §13, `after_f2s{1,2}.txt` — [CopyPath 카드](bt-copypath-end-yaw.md) |
| f2t1 | no5 8/8, pad_relief 첫 작동 → 멈칫 시작 | 10-14 §17 · §18, `run_f2t1.txt` · `navlog_f2t1.txt` · `hesitation.txt`, bag `2026-10-14/bags/bag_f2t1.tgz`(로컬), 영상 `2026-10-14/videos/` 사용자 3 개 · `sync_*_f2t1_*.mp4`(git 제외) |
| f2u1 · f2u2 · f2u3 | A/B/A2(b910) | 10-14 §21 ~ §23, `run_f2u{1,2,3}.txt` · `anal_free_wobble_f2u.txt` · `anal_ctrl_timing_f2u.txt` · `anal_box_f2u*.txt`, bag `2026-10-21/bags/bag_f2u1.tgz` · `bag_f2u3.tgz`(로컬; f2u2 bag 없음) |
| f2v1 · f2v3 · f2v4 | shadow 가 '바꿀 상황' 기록(값 안 바꿈) | 10-15 §3 · §18.1 · §20.1, `navlog_f2v{1,3,4}.txt` |
| f2v2 | 패딩 변경 없는 잔떨림 | 10-15 §15 · §16, `anal_hesitation_f2v2.txt` · `anal_wiggle_amp.txt` |
| 도구(10-13) | `run_sim_pad0.sh` · `anal_pad0_summary.py` · `chk_pad0.sh` · `run_sim_unstuck.sh` · `anal_unstuck_summary.py` | §9.1 |
| 도구(10-14) | `run_sim_unstuck2.sh` · `anal_unstuck2_summary.py` · `chk_padding_dynamic.py` · `pad_relief.py` · `chk_pad_relief.sh` · `run_detached.sh` · `prep_patrol_pad.sh` · `prep_pad_only.sh` · `chk_after_f2r{1,2}.sh` · `chk_navlog_f2r1.sh` · `fig_stop_costmap.py` · `anal_hesitation.py` · `chk_after_relief.sh` · `up_pad_shadow.sh` · `up_pad_toggle.sh` · `anal_lc_hist.py` · `anal_ctrl_timing.py` · `anal_free_wobble.py` | §9.1 ~ §9.7 |
| 도구(10-15) | `anal_wiggle_amp.py` | §9.7 |

## 9. 도구 해설
공통: 시뮬은 Jetson 에서 `Docs/tools/anal_mppi_sim.py` 를 `xargs -P 3` 으로 병렬 실행하고(결과 Jetson `/tmp/sweep_pad0` · `/tmp/unstuck` · `/tmp/unstuck2` — **원천 소실**, 요약표만 `outputs/` 에), bag 분석은 PC 에서 `rosbags`(AnyReader)로 읽었다. 주행 · 정지 시험 도구는 Jetson `/tmp` 에 올려 실행(`run_jn.sh` 또는 연결 불안정 때 `run_detached.sh`). 시뮬 본체 해설은 [오프라인 MPPI 시뮬레이터 카드](mppi-offline-simulator.md) — 여기서는 이 문제에 쓴 인자만.

### 9.1 시뮬 묶음 · 요약기 (10-13 §11 · §14.2, 10-14 §2) — 계산만, 로버 안 움직임
- **형태**: Jetson `bash /tmp/run_sim_pad0.sh` · `run_sim_unstuck.sh` · `run_sim_unstuck2.sh`(인자 없음). 공통 인자 `COM` = `humble=1 temperature=0.15 … fwd_w=15 fpchk=1`(+ `cost_w=3.81`), 장면별 `t_abs`(bag 시각) · `seed`.
  - `run_sim_pad0.sh`: 장면 4(`box_f2o1` 13:32:59 · `box_f2p1` 14:14:22 · `door_f2a10` · `out_f2o1` 13:30:24) × 씨앗 10, `pad=0`. 대조(pad 0.01)는 10-13 §9.1 의 `/tmp/sweep` cost_w 3.81 결과를 그대로 씀.
  - `run_sim_unstuck.sh`: 정지 자세 f2o1 13:33:27 · f2p1 14:14:56 · f2q1 17:51:40 × pad 0.01 · 0 × 씨앗 1~5, 150 주기(15 s).
  - `run_sim_unstuck2.sh`: f2o1 · f2p1 × `us_d` 0.15 · 0.30 · 0.50 × 씨앗 1~5, `unstuck=1 cycles=300`(30 s).
- **하는 일(요약기)**: 각 시뮬 출력에서 정규식으로 `LETHAL 여유 … 최소` · `실패) 주기 N 회` · `후: 전진` · (unstuck2) `패딩 0 전환 N 회 · 패딩 0 이던 시간 · 되돌린 뒤 5 s 안에 다시 갇힘` 을 읽어 장면 × 조건별 표. **멈춘 씨앗 = 실패 ≥ 10 주기**(pad0), **나온 씨앗 = 전진 ≥ 0.30 m**(unstuck), unstuck2 는 ≥ 1.0 m.
- **시뮬 쪽 동작**(`anal_mppi_sim.py`): `fpchk=1` 은 패딩한 풋프린트 꼭짓점 4 개를 칸으로 옮겨 Bresenham 둘레 최대 비용(Nav2 방식). `unstuck=1` 은 후보 전부 충돌이 `us_k`(20 = 2 s) 이어지면 `set_pad(0.0)`, `us_d` 이동 또는 `us_t`(10 s) 뒤 원래 값(350~355 행). **꼭짓점만 바꾸고 코스트맵 inflation 은 기록된 것 그대로**(§4.1).
- **출력**: `2026-10-13/outputs/sim_pad0_summary.txt` · `sim_unstuck_summary.txt` · `2026-10-14/outputs/sim_unstuck2_summary.txt`. PC 쪽 출력이 비어 Jetson 결과를 요약기로 다시 집계했다(10-13 §11.1 · §14.2).
- **결함**: 켜는 조건(후보 전부 충돌 2 s)과 시간 한도(10 s)가 실제 노드(로그 3 s 안 3 회 · 15 s)와 다름. 복구 동작(비우기 · 후진 · 대기)은 모형에 없음. '되돌린 뒤 남는 상태' 는 원리상 못 냄(실수 ②).
- **지금**: `pad` · `unstuck` 인자는 지금 판에도 있음(`anal_mppi_sim.py` 43 · 178 · 350 행). 묶음 스크립트는 그날 커밋 판 그대로(뒤에 바뀐 판 없음).

### 9.2 `chk_padding_dynamic.py` — 실행 중 패딩 반영 확인 (10-14 §7) ★ ⚠ 스스로 토글을 함
- **형태**: Jetson `python3 /tmp/chk_padding_dynamic.py [local|global|both]`(기본 local). 그날은 `local`.
- **하는 일**: 3 s spin 뒤 `GetParameters` 로 처음 값 → `/local_costmap/published_footprint`(PolygonStamped) · `/local_costmap/costmap_raw`(TRANSIENT_LOCAL)를 받아 ① 풋프린트 **변 길이**(축 치수는 로버가 비스듬하면 커져서 변으로 봄) ② 원시 코스트맵 253 · 254 칸 수. `SetParameters` 로 0.0 → 1.5 s → 새 메시지 기다림(≤ 6 s) → 같은 측정 → 처음 값 → 측정. `finally` 에서 처음 값이 아니면 되돌림 재시도.
  ```python
  for v, tag in ((0.0, '0.0 으로'), (ORIG[k], '처음 값으로 복귀')):
      t0 = time.time(); r, dt = setpad(k, v); …
  ```
- **출력**: [`chk_pad_local.txt`](../debug_log/2026-10-14/outputs/chk_pad_local.txt):
  ```
  0.0 으로 뒤               local: 풋프린트 긴 변 0.510 · 짧은 변 0.330 m | 코스트맵 내접(253) 1235 칸 · 치명(254) 241 칸
    실행 중 값 0.0 | 긴 변 변화 -20.0 mm · 짧은 변 변화 -20.0 mm · 내접 칸 -6
  ```
- **쓰인 곳**: §7.1 '반영됨' → pad_relief 구현 결정. **결함**: 내접 칸 수는 센서 흔들림과 섞여 판별력 없음(§7.1 자인). 되돌린 뒤 동작은 보지 않음.
- **계보 · 지금**: 상시 도구(`Docs/tools/`, `164a4c17` 판 그대로). ⚠ 10-14 §21 이후 기준으로 **이 도구를 돌린 스택은 B 와 같은 상태가 될 수 있다** — 돌렸다면 prep 재기동. 머리 설명 · README 에 그 경고가 없음(§4.4).

### 9.3 `pad_relief.py` · `chk_pad_relief.sh` · `run_detached.sh` — 노드와 정지 시험 (10-14 §8) ★
- **노드**: §4.2 · §4.4. 구독 `/rosout`(Log, depth 100) · `/odometry/filtered`, 발행 `/rover/pad_relief`(DiagnosticArray, 내린 상태면 WARN), 0.2 s 틱 · 1 s 마다 원래 패딩 읽기 시도. shadow 는 `set_padding` 에서 값을 안 바꾸고 `[shadow] 패딩 0.000 로 바꿀 상황(…) — 값은 안 바꿈` 을 적되 내부 상태(켜짐 · 15 s 한도)는 그대로 돌림 — 그래서 shadow 의 되돌림 줄은 늘 '시간 한도 15 s(이동 0.00 m)' 로 나온다(10-15 `navlog_f2v1.txt` 78 행).
- **`chk_pad_relief.sh`**(Jetson, `run_detached.sh chk_pad_relief.sh pad_relief.py` 로 실행): 노드를 기본값(mode on)으로 띄우고, 파이썬 시험 노드가 `/rosout` 에 `name='controller_server'`, `msg='Optimizer fail to compute path (시험용 가짜 로그)'`(level 40)를 0.2 s 간격으로 발행 → `/local_costmap/published_footprint` 짧은 변으로 판정(±3 mm): 2 회 → 0.350 유지 · 4 회 → 2 s 안 0.330 · 13~18 s 안 0.350 복귀 · 다시 4 회 뒤 파일 신호로 SIGTERM → 0.350. 끝에 노드 기록 · 남은 프로세스 수 · 실행 중 값.
  - 출력 [`chk_pad_relief.txt`](../debug_log/2026-10-14/outputs/chk_pad_relief.txt): `3) 시간 한도 복귀: 15.3 s 뒤 0.350 m → 통과` · `11:17:52 패딩 → 0.010 (시간 한도 15 s(이동 0.00 m)) 적용`.
  - 결함: 가짜 로그 문구가 진짜와 같은지는 이 시험으로 못 봄(f2r1 에서 확인). ⚠ 이 시험도 실행 중 토글을 2 번 한다 — 그 스택은 f2r1 전 prep 으로 다시 띄웠으므로 주행 결과엔 영향 없음(`prep_f2r1.txt`).
- **`run_detached.sh`**(PC · WSL): 파일 전송 · 기동 · 결과 읽기를 각각 8 회 재시도(4 s 간격), Jetson 에서 `setsid nohup bash -c '… > /tmp/<이름>.out; touch /tmp/<이름>.done'` 로 띄워 접속이 끊겨도 끝까지 돎. 비밀번호는 `run_jn.sh` 에서 읽고 스크립트에 적지 않음. 호스트 키 검사를 끄는 옵션이라 10-14 §8.4 의 '주소를 빼앗긴 상태에서 비밀번호를 다른 컴퓨터에 보낼 위험' 이 그대로 있다 → [Jetson Wi-Fi 카드](jetson-wifi-link.md).

### 9.4 prep 래퍼 · 상태 확인 (10-14 §9 · §19)
| 도구 | 하는 일 | 출력 |
|---|---|---|
| `prep_patrol_pad.sh [VIZ FWD MODE]` | 기존 pad_relief 죽이고 로그 지움 → `prep_patrol.sh` → `setsid nohup python3 -u /tmp/pad_relief.py --ros-args -p mode:=${3:-shadow}` → '원래 패딩' 줄을 8 s 기다림 → 노드 수 · 실행 중 로컬 패딩 · CostCritic · 전역 감쇠 · nvblox 통합 거리 한 줄 | `prep_f2r{1,2}.txt` · `prep_f2s1.txt` · `prep_f2t1.txt` 끝 두 줄 |
| `prep_pad_only.sh` | 이전 실패 원인(노드 로그 끝 3 줄) 출력 → mode on 으로 노드만 다시 | 원천 소실(SUMMARY §9.1) |
| `chk_after_f2r{1,2}.sh` · `chk_after_f2s{1,2}.sh` | pad_relief 기록 · 주행 시작 뒤 Nav2 컨트롤러 실패 로그 · 현재 로컬 패딩 · 노드 수 | `after_f2r1.txt` 19 행 `현재 로컬 패딩: Double value is: 0.01 · pad_relief 1 개` |
| `chk_navlog_f2r1.sh` | 실패 · 비우기 · 재시도 시각을 nav2.log 에서 | `navlog_f2r1.txt` |
| `up_pad_shadow.sh` | 노드 죽이고 기록을 `/tmp/pad_relief_f2t1.log` 로 옮긴 뒤 shadow 로 다시 | 원천 소실(SUMMARY §19.1) |
| `chk_after_relief.sh` | 로컬 · 전역 패딩 · footprint · inflation 반경 · 감쇠, 발행 풋프린트 한 번, nav2.log 의 local_costmap footprint · padding · reset 줄 | 원천 소실(SUMMARY §18 서술만) |
- 지금: 모두 그날 판, 지금 구성에서 안 씀(10-22 SUMMARY 9 행).

### 9.5 `fig_stop_costmap.py` — 멈춘 순간 차체 ↔ 치명 칸 (10-14 §9.2)
- PC, `Docs/tools/` 상시 도구(10-13). 0.6 s 마다 풋프린트 둘레 최대 비용, 라이다 점까지 **패딩 없는 실제 풋프린트** 외곽 최소 거리, 1 m 안 치명 칸 **중심**까지 거리(72 행 주석 "칸 반폭 2.5 cm 는 빼지 않음").
- 출력 [`f2r1_selfrecover.txt`](../debug_log/2026-10-14/outputs/f2r1_selfrecover.txt): `11:26:39.0       99          0.292 (0.27, -0.46)                        0.049 (0.16, 0.21)`, 그림 `Docs/04_navigation/figures/2026-10-14_f2r1_box_selfrecover.png`.
- 같은 날 `anal_box_pass.py`(가장자리 = 중심 − 0.025)의 2.4 cm 와 정의만 다름(§6-2). 상세는 [상자 옆 정지 카드](box-side-stall-cause.md).

### 9.6 `anal_hesitation.py` · `up_pad_toggle.sh` · `anal_lc_hist.py` — 멈칫 · A/B (10-14 §18 · §21) ★ 판정을 낸 도구
- **`anal_hesitation.py`**(PC `python anal_hesitation.py 이름=bag@HH:MM:SS~HH:MM:SS …`): 구간 안 `/cmd_vel` · `/tf`(map→odom yaw) · `/wheel_odom` · `/odometry/filtered`.
  ```python
  for x in v:
      if x >= 0.06: cruise = True
      elif x < 0.03 and cruise: dips += 1; cruise = False
  ws = np.sign(np.where(np.abs(w) > 0.05, w, 0)); ws = ws[ws != 0]; flips = int((ws[1:] != ws[:-1]).sum())
  ```
  멈칫 = 순항(v ≥ 0.06)에서 0.03 아래로, 좌우 틀기 = |ω| > 0.05 표본의 부호 바뀜, 둘 다 구간 길이로 분당. 지도 보정 각 = map→odom yaw 끝 − 처음, EKF/휠 = |ω| 적분 비.
  - 출력 [`hesitation.txt`](../debug_log/2026-10-14/outputs/hesitation.txt)(§18 의 f2s2 · f2t1 · f2r1). **§21 의 A · B · A2 출력은 원천 소실**.
  - 결함: 구간 길이 = 지정 시각 차(정지 시간 포함). 문턱 0.05 rad/s 는 눈에 안 보이는 잔떨림까지 셈(10-15 §16, 실수 ④).
- **`up_pad_toggle.sh`**: §4.3. 정지 중, 같은 서비스(`ros2 param set /local_costmap/local_costmap footprint_padding`)로 0.0 → `sleep 9` → 0.01, 앞뒤 값 출력. 실제 간격은 `ros2 param set` 기동 시간 때문에 12 s. 출력 원천 소실.
- **`anal_lc_hist.py`**(PC): 구간 안 `/local_costmap/costmap` 전 칸 값 히스토그램 — 0 · 1~49 · 50~89 · 90~98 · 99 · 100 · −1 비율, 0 < 값 < 99 중 가장 작은 5 개(팽창 꼬리), 서로 다른 값 수. 출력 원천 소실(SUMMARY §21.3 '값 23 개, 꼬리 55 · 57 · 58 · 61 · 62, 치명 · 내접 차 ≤ 2 %p').
- **계보 · 지금**: `anal_hesitation.py` → 10-15 `anal_wiggle_amp.py`(크기 지표 추가). 상시 도구로는 안 옮겨짐.

### 9.7 `anal_ctrl_timing.py` · `anal_free_wobble.py` · `anal_wiggle_amp.py` — 무엇이 달라졌나 (10-14 §23 · 10-15 §16)
- **`anal_ctrl_timing.py`**(PC, 인자 `이름@bag@HH:MM:SS~HH:MM:SS@top로그`): `/cmd_vel` · `/trajectories` · `/local_costmap/costmap` 간격 중앙 · 95 % · 최대 · > 100 ms 비율, `/transformed_global_plan` 점 수 변화 중앙, top 기록에서 'controll' 줄 9 번째 열(CPU %).
  - 출력 [`anal_ctrl_timing_f2u.txt`](../debug_log/2026-10-14/outputs/anal_ctrl_timing_f2u.txt): `B           50 /    52 /  4951,  0.1%                        100 /   124               0.60                   0.0                   nan /   nan  (0 표본)` — **CPU 는 top 줄을 못 찾아 0 표본**, §23 의 317 · 303 · 309 % 는 다른 계산(원천 소실).
- **`anal_free_wobble.py`**(PC, 인자 `R 이름=bag@…`): 각 `/cmd_vel` 시각에 직전 로컬 코스트맵에서 로버(odom→base_link) 반경 R 안 최대 비용이 0 이면 '빈 곳'. 빈 곳 · 나머지로 나눠 |ω| > 0.05 부호 바뀜을 셈(구간이 끊기면 부호 이력도 끊음). 근거: humble CostCritic 은 궤적 점 중심 칸 비용이 1 미만이면 건너뜀(머리 설명). 기본 R 0.6(지평 0.26 m + 반 대각 0.31 m), SUMMARY 판정은 0.4.
  - 출력 [`anal_free_wobble_f2u.txt`](../debug_log/2026-10-14/outputs/anal_free_wobble_f2u.txt) — §4.3 발췌. 결함: 0.4 m 는 '지평 끝 중심 칸이 모두 0' 의 근사(차체 모서리 칸은 안 봄) — CostCritic 의 `consider_footprint` 검사가 그 점에서 정말 아무 일도 안 하는지는 소스 읽은 범위 안의 판단.
- **`anal_wiggle_amp.py`**(PC, 10-15 `d4dc24cb`): 부호 바뀜을 문턱 0.05 · 0.10 · 0.20 rad/s 로 각각, 명령 ω · EKF ω 의 고주파 RMS(1 s 이동평균 뺀 값), 방향 흔들림 RMS(°). 출력 [`anal_wiggle_amp.txt`](../debug_log/2026-10-15/outputs/anal_wiggle_amp.txt) — §4.3 · 실수 ④ 발췌. 이 카드에서 A/B 목표 2 수치의 유일한 남은 원문.

### 9.8 이 시기에 부른 앞 시기 · 다른 카드 도구
| 도구 | 이 시기에 한 일 | 해설 |
|---|---|---|
| `Docs/tools/anal_mppi_sim.py` | `pad` · `unstuck` 인자 | [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md) |
| `Docs/tools/anal_box_pass.py` | f2r1 · f2r2 상자 구역 최소 여유 | [상자 옆 정지 — 원인](box-side-stall-cause.md) |
| `run_f2c.sh` · `job551_f0drive` | 러너(b910 · no5) | [F2 기준선 no5](f2-baseline-no5.md) |
| `Docs/tools/prep_patrol.sh` · `prep_fast.sh` | 래퍼가 부르는 prep 본체 | [prep 빠른 기동](prep-fast-startup.md) |

## 10. 용어
- **footprint_padding(패딩)**: 코스트맵 풋프린트(0.51 × 0.33 m)를 사방으로 키우는 값. 충돌 검사 기준 · 내접 반경(0.165 + 패딩)이 함께 바뀐다. 지금 0.01(09-14 결정).
- **후보 전부 충돌('Optimizer fail to compute path')**: MPPI 가 뽑은 궤적 후보가 모두 충돌 판정이라 명령을 못 낸 상태. Nav2 Humble 의 controller_server 로그 문구이고 pad_relief 의 켜는 신호였다.
- **Optimizer reset(최적화 초기화)**: 실패 뒤 MPPI 가 제어열 · 잡음 표본을 새로 시작하는 것(f2r1 `navlog_f2r1.txt` 13~14 행).
- **shadow(관찰 모드)**: 판정과 기록만 하고 값은 안 바꾸는 모드. pad_relief · stuck_monitor 가 같은 이름을 씀.
- **멈칫 vs 잔떨림(좌우 틀기)**: 멈칫 = 순항 속도에서 크게 떨어지는 보이는 사건. 잔떨림 = 속도는 그대로인데 명령 ω 가 ±0.07 rad/s 정도로 빠르게 좌우를 오가는 것(10-15 §16). |ω| > 0.05 부호 바뀜 지표는 주로 잔떨림을 센다.
- **빈 곳(free wobble)**: 로버 반경 0.4 m 안 로컬 코스트맵이 전부 0 인 순간 — 장애물 비용 크리틱이 할 일이 없는 곳에서 흔들림을 보려는 구분.
- **토글(패딩 토글)**: 실행 중 0.01 → 0 → 0.01 로 바꿨다 되돌리는 것. 10-14 B 조건 · f2t1 의 pad_relief 작동 · `chk_padding_dynamic.py` 실행 · `chk_pad_relief.sh` 시험이 모두 여기에 해당.
