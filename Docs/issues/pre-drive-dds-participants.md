# 주행 직전 DDS 참여자 금지 — cc1 루프 미달 18 에서 나온 '30 s 규칙'

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **절차 규칙(우회)** — 원인 판정은 n = 1(cc1) 대 4(cc2~cc5)의 정황이고 기전은 **미확인**. 규칙 문구('30 s')의 수치 근거는 측정이 아니다(§5). 이후 러너 `sleep 30`(09-23) · 게이트 한 노드(10-27) · 상주 창구(10-28)로 이어짐 | 09-21 §1 · §2 · §4 (이 카드), 이후 09-22 · 09-23 · 10-27 §24 · 10-28 §16 | [09-21 §1 cc1 '루프 미달 18 · EKF 위반 61'](../debug_log/2026-09-21/SUMMARY.md) | `Docs/debug_log/2026-09-21/jobs/job231_drive.sh`(메타 스냅숏 `job453_runmeta.sh` 호출을 bag 시작 **앞** → bag 종료 **뒤**) · `Docs/04_navigation/TEST_COURSE_AND_GATES.md` v1.0(09-21, 절차 5 단계 · 운영 규칙 4) · `BASELINE_STVL.md` §3-5 | [CostCritic 교체](obstacles-to-costcritic.md)(cc1 이 판정 주행이었음) · [Phase S 기준선](phase-s-baseline.md)(cc1 제외 사유) · [SLAM Fast DDS 데드락](slam-dds-deadlock.md)(09-17 `job393` 참여자 생성 · 소멸 스트레스) · [DDS 공유메모리 사고](dds-shm-incident.md) · [CPU 부하 · 정지](cpu-load-stalls.md)(EKF 위반 서명) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md)(10-27, 같은 날 게이트 정리) |

**한 줄**: 09-21 CostCritic 첫 판정 주행 cc1 은 성공했지만 상자 옆 구간에서 컨트롤러가 10 Hz 주기를 18 번 놓쳤다. 컨트롤러 CPU 증가는 +4 %p 뿐인데 EKF · planner · BT · SLAM 등 크리틱과 무관한 노드가 함께 2~4 배로 올라, 그날 처음 주행 직전에 넣은 **메타 스냅숏**(파라미터 조회 노드 + `ros2 topic list/echo` = DDS 참여자 3 개 생성 · 소멸)을 의심했다. 스냅숏을 bag 종료 뒤로 옮긴 cc2~cc5 4 회에서 미달 0 · CPU 정상이어서 '주행 30 s 전엔 DDS 참여자를 만들거나 없애지 않는다' 를 절차 규칙으로 정했다. 다만 (a) 바꾼 것이 스냅숏 위치만이 아니고(회차마다 prep 재기동), (b) cc1 은 스냅숏 **전**의 게이트에서 이미 SLAM map→odom 이 절반이었고, (c) 같은 시기 러너 게이트 자신이 주행 수 초 전에 참여자를 여럿 만들고 있었다 — 그래서 '스냅숏이 원인' 은 지지(약함), '30 s' 는 측정에서 나온 값이 아니다. 규칙은 09-23 러너 `sleep 30` 으로 처음 실제 대기가 됐다.

## 1. 증상
- cc1(09-21 09:38:15 목표 수신 → 09:38:46 성공, Jetson 시계 — nav2 로그 epoch 1789951095.6 · 1789951126.8): **SUCCEEDED 31.1 s · 2.20 m**, 1 s 정지 0. 그러나 `Control loop missed its desired rate of 10.0000Hz` **18 회**, 목표 수신 뒤 12.5~21.3 s(상자 옆 구간), BT `compute_path` 응답 대기 초과 1 · `follow_path` 응답 대기 초과 3 → 대기 목표 3 개 `Aborting handle`. 로버는 멈추지 않았다(csv |v| < 0.01 구간 없음). [nav2_cc1.log](../debug_log/2026-09-21/outputs/nav2_cc1.log)(grep 수 18, cc2~cc5 는 0) · [drive_cc1_runner.txt](../debug_log/2026-09-21/outputs/drive_cc1_runner.txt).
- 판정 기준(09-18 §16 사전 선언) '루프 미달 ≤ 1' 불합격 — CostCritic 판정 6 줄 중 유일한 불합격.
- 프로세스별 CPU(top 2 s, [j379_cc1.txt](../debug_log/2026-09-21/outputs/j379_cc1.txt) top 절): controller 43.1/82.4 · **ekf 42.0 · slam 43.2 · bt 28.5 · planner 23.6 · behavior 19.8 · smoother 18.3** · load 평균 8.6 최대 9.3. cc2 는 controller 35.5 · bt 15.1 이고 slam · ekf · planner 는 상위 6 줄에 안 듦([j379_cc2.txt](../debug_log/2026-09-21/outputs/j379_cc2.txt)).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-17 §6.3 | SLAM 데드락 수정판(Fast DDS 2.6.12) 검증에 참여자 생성 · 소멸 스트레스 `job393_churn.sh` | 3 라운드 정지 0 | '참여자 churn 이 SLAM 을 멈출 수 있다' 는 경계가 생김 | [SLAM 데드락 카드](slam-dds-deadlock.md) |
| 09-18 §17.3 | 주행 재현 규칙 구현: `job231_drive.sh` 가 `export TOPICS` 직후 **bag 시작 전에** `job453_runmeta.sh`(run_meta + job451 파라미터 스냅숏) 실행 | 시험 9.1 s, run_meta 25 줄 · params 598 줄 · 무응답 0 | 재현 정보 확보. 주행 부하는 따지지 않음 | [j453_metatest.txt](../debug_log/2026-09-18/outputs/j453_metatest.txt), `2026-09-18/jobs/job231_drive.sh` 9 행 |
| 09-21 §1 cc1 | 이 판으로 첫 주행. 순서(Jetson 시계): job254 게이트 → **09:38:01 메타 시작**(약 9 s) → bag · top 시작 · `sleep 4` → 09:38:15 목표 → 09:38:28~36 미달 18 → 09:38:46 성공 | 위 §1. top 합계 433 %(아래 §5 계산) | '크리틱 CPU +4 %p 로는 18 회를 설명 못 함, 무관한 노드가 함께 올랐다 → **메타 스냅숏의 디스커버리 후폭풍** 의심(09-17 churn 계열)' | [meta_cc1.txt](../debug_log/2026-09-21/outputs/meta_cc1.txt)(date 09:38:01) · nav2_cc1.log · `bags/top_cc1.log`(로컬) |
| 09-21 §1 직후 | 열 · 클럭 배제(`run_j457.sh` → `job457_cpustate.sh`) | 15 W · 1497 MHz × 6 · 49 °C · dmesg 이상 없음, idle top 에 lifecycle_manager 13.7 % | 하드웨어 원인 아님 | [j457_cpustate.txt](../debug_log/2026-09-21/outputs/j457_cpustate.txt) |
| 09-21 §1 → §2 | `job231_drive.sh` 에서 job453 호출을 **bag 종료 · sync 뒤**로 옮김(주석 '파라미터는 주행 중 안 바뀌므로 재현성 동일'). 그리고 prep(`run_mp9prep.sh`) 다시 | — | cc2 에서 미달 횟수로 가린다, 그대로면 크리틱을 다시 본다(판별을 주행 전에 선언) | `2026-09-21/jobs/job231_drive.sh` 11 · 30 행 |
| 09-21 §2 cc2 | 같은 코스(상자 y −0.050) | 미달 **0**, BT 응답 초과 0, controller 34/68 · ekf 12 · planner 11 · bt 15(dy6 수준), top 합계 316 % | **cc1 미달 원인 = 메타 스냅숏으로 판정.** 절차 규칙 '주행 30 s 전 참여자 생성 금지' 신설 | [drive_cc2_runner.txt](../debug_log/2026-09-21/outputs/drive_cc2_runner.txt) · [j379_cc2.txt](../debug_log/2026-09-21/outputs/j379_cc2.txt) |
| 09-21 §3 · §7 | cc3 · cc4 · cc5 | 미달 0 · 0 · 0, top 합계 321 · 323 · 317 % | 규칙 유지. 기준선에서 cc1 제외 | [BASELINE_STVL.md](../debug_log/2026-09-21/BASELINE_STVL.md) §2 |
| 09-21 §4 · §6 | 판정표에 '루프 미달: cc1 불합격 — 원인은 절차' · S5 계측(코스트맵 주기)은 '주행 전 `ros2 topic hz` 금지 규칙' 때문에 bag 에서 사후 계산 | — | 규칙이 계측 설계에도 쓰임 | [09-21 SUMMARY §4 · §6](../debug_log/2026-09-21/SUMMARY.md) |
| 09-21 오후 | `TEST_COURSE_AND_GATES.md` v1.0: 절차 5 단계 '주행 30 s 전부터 DDS 참여자를 만들거나 없애는 명령 금지(`ros2 param/topic list·echo`, 임시 노드, 스냅샷)' · 운영 규칙 4 | 그런데 같은 문서 절차 6 단계는 '`run_drive_nohup.sh` — **게이트 A~G 재검사** → bag … → 주행' | 규칙과 러너가 어긋난 채 문서화(§5 ②) | 커밋 `35308b81` |
| 이후 09-22 | 절차 v2.0: 게이트 K(`ros2 param get`) · L(슬라이스 구독)도 '주행 30 s 전에 끝낸다', `job505_modeN_gate.sh` 머리 주석 | — | 규칙이 nvblox 게이트로 확장 | [nvblox N0~N4 카드](nvblox-migration-n0-n4.md) · `2026-09-22/jobs/job505_modeN_gate.sh` |
| 이후 09-23 | F0 러너 `job551_f0drive.sh`: 게이트 B · C · G2 뒤 **`sleep 30   # DDS 참여자 생성 뒤 30 s (09-21 cc1 규칙)`** → bag 시작 | — | 규칙이 처음 러너 안의 실제 대기가 됨 | `2026-09-23/jobs/job551_f0drive.sh` 21 행 |
| 이후 10-27 §24 | 사용자 "주행 전 여러 검사 중 중복 · 불필요한 것 없애자" — B(`ros2 topic hz` 12 s) · C(job386 5 s) · G2(job440) **참여자 3 개 · 약 24 s → 한 노드** `Docs/tools/chk_drive_gate.py`, prep 래퍼의 `ros2 param get` 약 11 번 → `chk_prep.py` 한 노드, 대화 쪽 30 s 대기 없앰(러너가 함) | 러너 30 s 유지, 그 마지막 10 s 로 P 측정 | 참여자 수 자체를 줄이는 쪽으로 | [10-27 SUMMARY §24](../debug_log/2026-10-27/SUMMARY.md) · [SLAM stamp 정체 카드](slam-stamp-freeze.md) |
| 이후 10-28 §10 · §16 | 장소 이름 이동 러너 `run_place_s1_1028.sh`: 게이트(chk_drive_gate) → 서버 · bag 기동 → `sleep 30   # DDS 참여자(서버 · 경로 조회기 · 기록기) 생성 뒤 30 s(09-21 규칙)`. 휴대폰 창구 `place_web.py` = 참여자 1 개 → 'prep 뒤 상주, 주행 30 s 전 새로 띄우지 않음'. f2pl3 에서 새로 뜬 참여자의 첫 명령이 빠짐(§10) | — | 같은 규칙이 운용 구성 요소의 기동 방식까지 정함. §10 은 다른 증상(새 참여자 첫 메시지 유실) | [10-28 SUMMARY §10 · §16](../debug_log/2026-10-28/SUMMARY.md) · `2026-10-28/jobs/run_place_s1_1028.sh` 18 행 |
- 별개 기전(같은 '통신 부하' 계열, 이 카드 범위 밖): 10-12 · 10-13 bag 기록기가 reliable `/tf` 를 못 따라가 생긴 HEARTBEAT 폭주(CLAUDE.md §6). 이 카드의 규칙과 직접 관계는 확인된 적 없다.

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| CostCritic 이 CPU 를 더 써서 주기를 놓쳤다 | 같은 크리틱으로 cc2~cc5 | controller 평균 34~37 %(cc1 43), 미달 0 × 4 | **기각**(n = 4) — [CostCritic 카드](obstacles-to-costcritic.md) §3 |
| 열 · 클럭 · 전력 모드 | job457 | 15 W · 1497 MHz · 49 °C · dmesg 깨끗 | **기각**(주행 직후 1 회 측정) |
| 주행 직전 메타 스냅숏(참여자 3 개 생성 · 소멸)이 원인 | 스냅숏 위치만 옮겨 cc2 → 미달 0, cc3~cc5 도 0 | 18 → 0, CPU 합 433 → 316~323 % | **지지(약함)**. 바뀐 것이 스냅숏 위치 하나가 아님(회차마다 `run_mp9prep.sh` 로 스택 재기동 · 상자 y −0.097 → −0.050 · 시간 경과) — 재현 시험(스냅숏을 다시 앞에 넣기)은 안 했다 |
| cc1 상태가 스냅숏 **전**부터 달랐다 | 러너 게이트 C(job386, 스냅숏보다 앞에서 실행)의 map→odom 개수 | cc1 **43 개/5 s**(최대 간격 0.11 s), cc2 · cc3 100 · cc4 96 · cc5 85 | **미확인** — 이 차이는 이번 카드에서 처음 짚음. SUMMARY 는 언급 없음. 스냅숏 앞에서 이미 SLAM 발행이 절반이었다면 '스냅숏 단독 원인' 이 약해진다 |
| 부하가 스냅숏 직후의 짧은 폭발이었다 | `bags/top_cc1.log` 2 s 스냅숏별 합계 · ekf 시계열(아래 §5 계산) | 합계 398~473 % 가 09:38:10 부터 09:38:49 까지 **40 s 내내** 유지, ekf 는 5.9 → 15.8 → 18.8 → 32.5 → 45 %(09:38:16 부터 고원) | 스냅숏이 끝난 뒤(≈ 09:38:10) 30 s 넘게 지속 — '디스커버리 후폭풍' 으로 부르기엔 길다. **기전 미확인** |
| 러너 게이트의 참여자도 같은 부하를 낸다 | cc2~cc5 에도 job254 게이트(`ros2 topic hz` · job386 · `ros2 service call` × 2 · `tf2_echo` · job248)가 주행 수~수십 초 전에 돎 | 미달 0 × 4 | 게이트 참여자로는 재현 안 됨 → 차이는 job453 의 내용(12 노드에 파라미터 서비스 호출 + `topic list` · `topic echo`)일 수 있다(추정) |

## 4. 조치와 효과
| 조치 | 전 | 후 | 한계 |
|---|---|---|---|
| 메타 스냅숏을 bag 종료 뒤로(`job231_drive.sh`, 09-21) | cc1 미달 18 · CPU 합 433 % · EKF 위반 주행 창 +19 | cc2~cc5 미달 0 · 합 316~323 % · EKF 창 +1 · +1 · 0 · 0 | 재현성: 파라미터는 주행 중 안 바뀐다는 전제(이 시기엔 사실 — 10-14 pad_relief 같은 실행 중 변경은 없음). n = 1 대 4 |
| 절차 규칙(09-21 문서화) | — | TEST_COURSE v1.0 절차 5 · 운영 규칙 4, BASELINE §3-5 | 러너 게이트 자신이 규칙을 어김(§5 ②), 09-23 까지 실제 대기 없음 |
| 러너 `sleep 30`(09-23 job551) | 게이트 → 수 초 뒤 bag · 주행 | 게이트 → 30 s → bag · 주행 | 30 s 는 측정값이 아님. 대기 효과를 따로 잰 기록 없음 |
| 게이트 한 노드(10-27 `chk_drive_gate.py`) · prep 확인 한 노드(`chk_prep.py`) | 참여자 3 개 · 약 24 s / `ros2 param get` 약 11 번 | 참여자 1 개 | 효과(미달 · CPU) 비교 기록은 이 카드에서 확인 안 함 |
- 지금 저장소(11-02 확인): `Docs/tools/chk_drive_gate.py` 머리 주석에 '한 노드(DDS 참여자 1 개)', `2026-10-28/jobs/run_place_s1_1028.sh` 18 행 `sleep 30`, `TEST_COURSE_AND_GATES.md` 현판 42 · 72 행에 규칙 유지.

## 5. 한계 · 모순 기록(원문 대조)
- ① **EKF 위반 61 은 주행 중 횟수가 아니다.** `sensors.log` 누적이며, 러너가 주행 전 게이트 · 주행 뒤에 찍은 두 줄의 차가 주행 창 증분: cc1 42 → 61(**+19**), cc2 19 → 20, cc3 22 → 23, cc4 39 → 39, cc5 19 → 19([drive_ccN_runner.txt](../debug_log/2026-09-21/outputs/drive_cc1_runner.txt) 'EKF 위반' 두 줄). SUMMARY §1 제목 · §2 표의 '61 / 20' 은 누적값이다. 방향(cc1 만 튐)은 같다.
- ② **규칙과 러너의 어긋남(09-21 ~ 09-22).** 규칙은 '주행 30 s 전 참여자 금지' 인데 그날 러너 `run_drive_nohup.sh` → `job254_s4run.sh` 는 주행 직전에 `ros2 topic hz /wheel_odom`(6 s) · `job386_slamalive.py` · `ros2 service call` × 2 · `sleep 15` · `ros2 run tf2_ros tf2_echo` · `job248_audit.py` 를 돌리고, `job231_drive.sh` 는 `sleep 4` 뒤 주행한다. PC 쪽 감싸개도 그 앞에 job248 · job315 × 3 · job377 · job440 을 ssh 로 띄운다. 즉 cc2~cc5 도 '30 s 규칙' 을 지키지 않았고, 그래도 미달 0 이었다. 같은 날 BASELINE · SUMMARY §6 의 '주행 전 `ros2 topic hz` 금지' 도 게이트 B 가 스스로 어긴다. 실제 30 s 대기는 09-23 job551 부터.
- ③ **'30 s' 의 출처.** 09-21 SUMMARY §2 · §4 에 수치 근거 없음(측정 · 문서 인용 없음). Fast DDS 의 참여자 정리 시간 등과 맞춘 값인지 기록 없음 — 출처 미확인 숫자로 다룬다.
- ④ **'lifecycle_manager 13.7 %' 는 cc1 특이값이 아니다.** SUMMARY §1 은 '주행 뒤 idle 에서도 lifecycle_manager 13.7 %' 를 이상 징후처럼 적었지만, 같은 계산으로 cc1 주행 중 평균 10.2 %, cc2 11.8 %, cc4 ps 13.1 %([rss_cc4.txt](../debug_log/2026-09-21/outputs/rss_cc4.txt))라 평소 값이다.
- ⑤ SUMMARY §1 의 'controller 41 · ekf 40' 과 j379 의 '43.1 · 42.0' 은 2 %p 다르다(같은 top 기록, 집계 창 차이로 보임 — 미확인).
- ⑥ 기존 카드 문구 '09:37:22 출발'([CostCritic 카드](obstacles-to-costcritic.md) §2)은 PC 감싸개의 '주행 시작'(nohup 기동 = 게이트 시작) 시각이다. 목표 수신은 Jetson 09:38:15.
- 이 카드 작성 때(11-02) 계산한 값 — 원문 출력 파일 없음, 원천 = `Docs/debug_log/2026-09-21/bags/top_ccN.log`(git 제외 로컬 보관):
  - 스냅숏별 합계(%CPU 열 합, 6 코어 = 600 %): `awk '/^top -/{if(n)print s; s=0; n++} /^ *[0-9]+ /{s+=$9} END{print s}' top_ccN.log` 의 평균 · 최대 = cc1 **433 / 473**, cc2 316 / 405, cc3 321 / 454, cc4 323 / 426, cc5 317 / 434. cc2~cc5 의 316~323 은 BASELINE '전체 CPU %' 와 일치(같은 방법으로 보임).
  - cc1 스냅숏 시각 · 합계: 09:38:08 265(top 첫 장 — 누적 평균이라 버림) · 09:38:10 398 · 09:38:12 358 · 이후 09:38:49 까지 433~472.
  - 한계: 합계에는 계측 자신(top · `ros2 bag record` = 'ros2' 약 20~32 % · 러너 python3)이 들어 있다.

## 6. 내 실수
### M1. 메타 스냅숏을 주행 직전에 넣어 판정 주행 1 회를 흐림 (09-18 §17.3 → 09-21 §1 · §2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 주행 재현 규칙(09-18): 주행마다 `run_meta.txt` · `params.txt` 를 bag 폴더에. `job231_drive.sh` 에 `job453_runmeta.sh` 호출을 넣음 — **bag 시작 전**(토픽 목록 `TOPICS` 를 export 한 바로 다음 줄) |
| 본 것 | cc1: 미달 18(12.5~21.3 s), BT 응답 초과 4, controller +4 %p 인데 ekf 42 · slam 43 · bt 28.5 · planner 23.6 % (j379_cc1 top 절), load 최대 9.3 |
| 처음 추론 | 그날 바꾼 것은 크리틱(CostCritic)이므로 크리틱 계산량 의심 — 판정 기준 '루프 미달 ≤ 1' 이 바로 그 위험을 보려고 둔 것 |
| 의심한 이유 | 같은 창의 다른 지표와 모순: 크리틱이 원인이면 controller 만 올라야 하는데 컨트롤러와 무관한 EKF · SLAM · planner · BT 가 함께 2~4 배. 열 · 클럭은 정상(j457). 그날 처음 들어간 절차 변경 = 주행 직전 스냅숏(참여자 3 개 생성 · 소멸) |
| 판별 시험 | 스냅숏을 bag 종료 뒤로 옮기고 같은 코스 cc2 — 판정 기준을 주행 전에 적음('미달이 그대로면 크리틱을 다시 본다') |
| 결론 | cc2 미달 0 · CPU dy6 수준, cc3~cc5 도 0 → 스냅숏 위치를 원인으로 판정. 단 prep 재기동 · 상자 배치도 함께 바뀌었고(§3), cc1 은 스냅숏 전 게이트에서 이미 SLAM 발행이 절반이었다(§3, 11-02 원문 대조에서 발견) — 판정은 '지지(약함)', 기전 미확인 |
| 다음에 알아보는 법 | 서명: **컨트롤러와 무관한 노드(ekf · slam · planner · bt)가 함께 오르고 CPU 합이 평소(≈ 320 %)보다 100 %p 이상 큼** → 크리틱 · 계획기가 아니라 통신 · 참여자 쪽부터. 규칙: 계측을 추가할 땐 주행 창 밖(bag 종료 뒤)에 두고, 새 단계는 판정 주행 전에 빈 주행 1 회로 부하를 본다. 게이트 C 의 map→odom 개수(정상 85~100 개/5 s)가 절반이면 출발 전부터 이상이다 |
| 데이터 | [nav2_cc1.log](../debug_log/2026-09-21/outputs/nav2_cc1.log) · [j379_cc1.txt](../debug_log/2026-09-21/outputs/j379_cc1.txt) · [j379_cc2.txt](../debug_log/2026-09-21/outputs/j379_cc2.txt) · [drive_cc1_runner.txt](../debug_log/2026-09-21/outputs/drive_cc1_runner.txt)(게이트 C 43 개/5 s) · [meta_cc1.txt](../debug_log/2026-09-21/outputs/meta_cc1.txt) · [j457_cpustate.txt](../debug_log/2026-09-21/outputs/j457_cpustate.txt) · `bags/top_cc1.log` · `bags/bag_cc1.tgz`(로컬), 도구 `2026-09-18/jobs/job231_drive.sh`(전) · `2026-09-21/jobs/job231_drive.sh`(후) |

## 7. 남은 것
- 기전: 참여자 3 개 생성 · 소멸이 40 s 넘는 전 노드 부하를 내는 경로 — 미확인. 재현 시험(스냅숏을 일부러 주행 앞에 넣기 · 대기 0/10/30 s)은 한 적 없다.
- cc1 게이트 C 의 map→odom 43 개/5 s(다른 회차 85~100) — 스냅숏 전 상태 이상인지 미확인. 그날 prep 뒤 cc1 전에 돈 참여자(`run_j451b.sh` 파라미터 조회 · 게이트만 시험 `gate_cc1`)와의 관계도 미확인.
- '30 s' 의 근거 수치. 지금 러너는 30 s 를 기다리지만 그 값을 줄이거나 늘린 비교 기록은 없다.
- 이후(10-12 ~ 10-13 통신 포화, 10-27 게이트 정리의 효과 수치): 그 시기 카드에서 채움.

## 8. 실험 · 도구 색인
- 주행: 09-21 cc1(문제) · cc2(판별) · cc3~cc5(반복). 결과 파일은 `2026-09-21/outputs/`(drive_ccN · drive_ccN_runner · j379_ccN · nav2_ccN.log · meta_ccN · params_ccN), top 원본은 `bags/top_ccN.log`(로컬).
- 도구: `job231_drive.sh`(09-18 판 → 09-21 판) · `job453_runmeta.sh` · `job451_paramsnap.py`(09-18 폴더) · `job254_s4run.sh`(09-18 폴더) · `run_drive_nohup.sh`(09-21 폴더) · `job379_navevents.sh`(회수 · top 집계) · `job457_cpustate.sh` + `run_j457.sh`.
- 이후 도구: `2026-09-22/jobs/job505_modeN_gate.sh` · `2026-09-23/jobs/job551_f0drive.sh` · `Docs/tools/chk_drive_gate.py` · `Docs/tools/chk_prep.py` · `2026-10-28/jobs/run_place_s1_1028.sh`.

## 9. 도구 해설
공통: Jetson 쪽 스크립트는 PC WSL 감싸개(`run_*.sh`)가 스크래치패드에서 CR 을 지우고 `sshpass -p <PW> scp` 로 Jetson `/tmp` 에 올려 실행한다. 09-21 주행 감싸개가 가리키는 옛 스크래치패드(`82ce61d4…`)는 09-28 자동 소실 → 저장소 `jobs/` 판을 올려야 다시 쓴다. Jetson 주소는 당시 192.168.0.101(지금 192.168.0.110, `JETSON_HOST` 로 덮음).

### job231_drive.sh — 주행 묶음(bag · top · 러너 · 메타) · 09-21 수정판
- 실행 위치 · 부른 형태: Jetson, `job254_s4run.sh` 가 게이트 통과 뒤 `bash /tmp/job231_drive.sh NAME D TMO` 로 부름. 환경 `TOPICS`(자기가 만듦) · `BAG_EXTRA` · `BAG_PROFILE` · `STAGE` · `NOTE` · `GIT_HEAD`(job453 에 넘김).
- 왜: 09-1x 부터 '한 번의 원격 실행으로 bag 기록 + 주행 + nav2 로그 분석' (머리 주석: BT 수정 · 감쇠 복원 검증 주행용으로 시작).
- 하는 일(09-21 판, 순서대로): ① Fast DDS UDP 전용 프로파일 · ROS 환경 ② 기록 토픽 = `/tf /tf_static /map /scan /plan /plan_smoothed /unsmoothed_plan /local_plan /transformed_global_plan` 두 코스트맵 · `/odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck` + `BAG_EXTRA`, `BAG_PROFILE=nvblox` 면 nvblox 슬라이스 · 점유격자 · 깊이 이미지 · camera_info 추가(09-21 Phase N) ③ `ros2 bag record` · `top -b -d 2 -w 180 -o %CPU` · `tegrastats --interval 1000`(09-21 S5) 백그라운드, `ps` 로 노드 16 종 RSS 스냅숏 ④ `sleep 4` → nav2.log 줄 수 표시 → `python3 /tmp/job125_avoid3.py D TMO NAME | tail -40` ⑤ 2 s 뒤 bag SIGINT · top · tegrastats 종료, 주행 뒤 RSS · `free -m` 추가, bag 종료를 최대 10 s 기다리고 sync ⑥ **`bash /tmp/job453_runmeta.sh NAME D TMO`(09-21 에 여기로 옮김)** → 메타를 bag 폴더로 ⑦ nav2.log 신규분에서 `detected collision` · `clear except` · `clear entirely` · `backup failed` · `Goal succeeded` · `aborted` 개수, bag 크기, `sensors.log` 의 `Failed to meet update rate` 누적 · `slam.log` 의 `Message Filter dropping` 누적 · loadavg.
- 09-18 판과의 차(diff): 9 행 `export TOPICS; bash /tmp/job453_runmeta.sh $NAME $D $TMO`(bag 전) → 삭제, 30 행 같은 호출(bag 뒤) 추가, tegrastats · RSS 줄 추가, BAG_PROFILE 줄 추가.
- 출력: 화면(→ 감싸개가 `drive_NAME.log` 로) — 'EKF 위반 N회' 는 **누적값**(§5 ①). 파일 `/tmp/bag_NAME/`(+ run_meta.txt · params.txt) · `/tmp/top_NAME.log` · `/tmp/tegra_NAME.log` · `/tmp/rss_NAME.txt` · `/tmp/nav2_new.log` → `run_post3.sh` 가 회수. 09-21 원문 [drive_ccN_runner.txt](../debug_log/2026-09-21/outputs/drive_cc2_runner.txt).
- 쓰인 곳: 09-21 cc1~cc5 전부, 09-22 N4 주행. 판정 영향: cc1 판(전) · cc2~ 판(후)의 차이가 이 카드의 판별 변수.
- 계보 · 결함 · 지금: → 09-23 `job551_f0drive.sh`(F0 러너, 게이트를 안으로 넣고 `sleep 30`, top 은 루프 방식) → 10-27 판(게이트 `chk_drive_gate.py`, top 루프 제거 · /proc 틱 기록). 결함: 'EKF 위반' 줄이 누적이라 오독 쉬움, top 합계에 기록기 자신이 들어감. 지금 다시 쓰기: 상자 코스(job125) 전용이라 그대로는 안 씀 — 저장소 사본은 기록으로.

### job453_runmeta.sh · job451_paramsnap.py — 주행 메타 · 실행 중 파라미터
- 해설 본문은 [CostCritic 카드 §9](obstacles-to-costcritic.md)(09-18). 이 카드에 걸린 점만:
- 참여자 수: `ros2 topic echo /rover/status --once`(timeout 6 s) · `ros2 topic list`(timeout 8 s) · `python3 job451_paramsnap.py`(노드 하나가 12 노드의 `list_parameters` · `get_parameters` 서비스 클라이언트를 만들어 차례로 호출, timeout 45 s) = 참여자 3 개가 차례로 생겼다 사라짐. 시험 소요 9.1 s([j453_metatest.txt](../debug_log/2026-09-18/outputs/j453_metatest.txt)).
- cc1 의 [meta_cc1.txt](../debug_log/2026-09-21/outputs/meta_cc1.txt) `date: 09:38:01` 이 스냅숏 시작 시각 — 목표 수신(09:38:15)보다 14 s 앞. 지금은 주행 뒤 실행(10-27 §24 '유지' 항목: 사후 params 스냅숏).

### job254_s4run.sh — 주행 직전 게이트(09-21 cc 회차가 쓴 판)
- 실행 위치 · 부른 형태: Jetson, PC `run_drive_nohup.sh` 가 `nohup bash /tmp/job254_s4run.sh NAME D BX BY TOL > /tmp/drive_NAME.log` 로. 원본 `2026-09-18/jobs/job254_s4run.sh`.
- 하는 일(참여자 관점): 프로세스 14 종 pgrep(참여자 아님) → **`ros2 topic hz /wheel_odom`(6 s)** → **`job386_slamalive.py`**(map→odom 개수 · 간격 · stamp 지연, 5 s) → 이전 bag 잔존 정리 → **`ros2 service call` 로컬 · 전역 clear** → `sleep 15` → **`ros2 run tf2_ros tf2_echo map base_link`(6 s)** → **`job248_audit.py`**(상자 검출 · 통로 폭) → 상자 dx · dy ±TOL 판정 → `job231_drive.sh`. 굵은 것이 참여자를 만든다 — 마지막 것(job248)과 주행 사이는 job231 의 `sleep 4` 뿐.
- 출력: `drive_NAME.log` 앞 10 줄(게이트) — 'SLAM: map->odom N 개/5 s' 줄이 §3 의 cc1 43 개 근거.
- 결함(이 카드 관점): 규칙 '주행 30 s 전 참여자 금지' 와 맞지 않음(§5 ②). 계보: → job551(09-23, 게이트 뒤 sleep 30) → `chk_drive_gate.py`(10-27, B · C · G2 한 노드). 게이트 각 도구의 해설은 [MPPI 통로 카드](mppi-passage-tuning.md) · [간헐 중단 카드](intermittent-abort-dy.md).

### run_drive_nohup.sh — PC 감싸개(09-21 판)
- 실행 위치 · 부른 형태: PC WSL, `STAGE=… NOTE=… GIT_HEAD=… run_drive_nohup.sh NAME 2.0 BX BY 0.06 0`.
- 하는 일: 러너 파일 8 종(job254 · job231 · job125 · job248 · job315 · job386 · job451 · job453)을 옛 스크래치패드(`SPS=…82ce61d4…`)에서 CR 제거 → scp. 사전 게이트를 **ssh 로 따로**: job248(감사 · 출력이 잘리면 1 회 재시도) → job315 × 3(상자 셀 최대 y 중앙값, 3 s 간격) → 통로 띠 셀 ≤ 1 · 창 ≥ 0.20 → job377(목표 풋프린트 여유 ≥ 0.20) → job440(출발 자세 여유 ≥ 0.10, nan 이면 1 회 재시도) → 원격 nohup 으로 job254 → 5 s 마다 원격 로그 폴링(최대 8 분, '결과 ' · '주행하지 않음' 에서 끝).
- 출력: `drive_NAME.txt`(PC 화면 기록), 첫 줄의 '주행 시작 HH:MM:SS' 는 **PC 시계로 nohup 기동 시각**(게이트 시작, 움직임 시작 아님 — §5 ⑥).
- 참여자: 사전 게이트만으로 참여자 6~8 개(재시도 포함)가 주행 1~2 분 전에 생겼다 사라짐. 계보 · 지금: 위 job254 와 같음. 다시 쓰려면 `SPS` 경로를 저장소 `jobs/` 로 바꿔야 한다.

### job457_cpustate.sh · run_j457.sh — 'CPU 가 왜 높았나' 의 하드웨어 배제
- 해설 본문은 [CostCritic 카드 §9 표](obstacles-to-costcritic.md). 이 카드에서의 쓰임: 열 · 클럭 · 전력 모드 가설 기각(§3). 결함: 주행 **뒤** 1 회라 주행 중 클럭을 본 것이 아님(`jetson_clocks` 상태는 sudo 불가로 못 봄).

### chk_drive_gate.py (10-27, 지금 쓰는 판) — 짧게
- 실행 위치: Jetson, 러너가 `timeout 40 python3 /tmp/chk_drive_gate.py` 로. B(`/wheel_odom` 5 s ≥ 1 Hz) · C(map→odom 수신 간격 최대 < 0.5 s · stamp 지연 < 1.0 s) · G2(출발 자세 여유 m)를 **노드 하나**로, 마지막 줄 `GATE B= C= G2=`. 기준은 옛 도구 그대로(머리 주석). 이 카드의 규칙이 '참여자를 안 만든다' 에서 '하나만 만든다' 로 옮겨 간 자리. 자세한 해설은 10 월 시기 카드에서.

## 10. 용어
- **DDS 참여자(participant)**: ROS 2 노드가 DDS 위에서 갖는 통신 주체. `ros2 topic echo/list/hz` · `ros2 param` · `ros2 service call` · 임시 파이썬 노드는 실행될 때마다 새 참여자를 만들고, 끝날 때 없앤다. 생길 때 다른 모든 참여자와 서로를 알리는 **디스커버리**(UDP 멀티캐스트 · 유니캐스트 교환)가 일어난다.
- **디스커버리 후폭풍**: 09-21 SUMMARY 의 표현. 참여자 생성 · 소멸 직후 기존 노드들이 디스커버리 처리로 CPU 를 더 쓰는 현상을 가리킨 가설 — 이 프로젝트에서 측정으로 확인된 기전은 없다.
- **제어 주기 미달(Control loop missed its desired rate)**: Nav2 controller_server 가 `controller_frequency`(10 Hz) 한 주기 안에 계산 · 발행을 못 끝냈을 때의 경고.
- **EKF 위반(Failed to meet update rate)**: robot_localization ekf_node 가 30 Hz 주기를 못 맞췄을 때의 경고 — `sensors.log` 누적 수로 센다.
- **메타 스냅숏**: 주행 재현 규칙(09-18)의 `run_meta.txt`(파일 해시 · 단계 · 토픽) + `params.txt`(실행 중 노드 파라미터).
- **게이트**: 주행 전에 러너가 자동으로 거는 통과 조건(프로세스 중복 · 보드 · SLAM · 상자 · 통로 · 목표 · 출발 자세 …), 단일 출처는 `TEST_COURSE_AND_GATES.md`.
