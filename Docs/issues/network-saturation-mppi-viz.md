# 통신 포화 — MPPI 궤적 발행(206 kB) + reliable `/tf` 기록기 → `/tf` HEARTBEAT 폭주 · Nav2 중단

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회** — 정체는 캡처 1 회(f2m1)로 **측정**: 포화 = UDP 통신량 약 10 배, 그 79 % 가 `/tf` 쓰는 쪽 2 곳(SLAM · EKF)의 HEARTBEAT. 시작점은 'bag 기록기가 reliable `/tf` 의 읽는 쪽으로 가장 먼저 뒤처짐' 으로 **지지**(캡처 순서 + 개입 시험 f2n1 1 회, 기전의 Fast DDS 동작은 소스 미확인 — 추정). 대책 두 겹이 운용 기본: `mppi_viz:=lite`(28 kB, 10-12 0/2) · 기록기 `/tf` best effort(10-13 0/1, 러너 기본 켬). **미확정**: PreferForward 5 에서는 0/3 인 이유(10-13 §3.3 사용자 결정으로 닫음), 폭주가 시작되는 그 순간의 계기. 커널 수신 버퍼 208 kB 는 그대로 | 10-12 ~ 10-13 (7 기) · 이후(10-19 ~) | [10-12 §1.3](../debug_log/2026-10-12/SUMMARY.md) 사용자 "상자 주변에서 행동이 매끄럽지 못했다"(f2f1) → §2 CPU 69 → 92 % · odom→base_link TF 수신 끊김 30 군데 | `ros2_ws/src/rover_navigation/launch/navigation.launch.py`(`mppi_viz:=lite`, 10-12 §7.3, 커밋 `cd6313ba`) · 러너 `job551_f0drive.sh`(top 루프 pid 고침 §3.4 `f7e0e62a` · UDP 손실 2 s 기록 §8.2 `8e71fe93` · 기록기 `/trajectories` best effort §11 `888860ce` · 캡처 `CAP_PCAP` 10-13 §0 `03008a09` · 기록기 `/tf` best effort `BAG_BE_TF` 10-13 §2 → 기본 1 §4.1 `2ea17ea7`) · `job550_f0run.py` + `job613_pathyaw.py --serve`(상주 경로 조회기, 10-13 §4.2 `2ea17ea7`) · prep 의 그림자 EKF 끔(`job966_prep_lean.sh` → `Docs/tools/prep_patrol.sh`) · `CLAUDE.md` §6(10-12 §14 `08faa968`) | [W3 떨림 · TF 지연](tf-lag-w3-wobble.md)(같은 '미래 시각 TF' 오류의 다른 기전 — §7.1) · [SLAM map→odom 시각 정체](slam-stamp-freeze.md) · [DDS 공유메모리 사고](dds-shm-incident.md)(UDP 전용 결정이 이 경로의 배경, 10-12 §8.3 ~ §8.6 · §17 공유메모리 검토) · [주행 직전 DDS 참여자 금지](pre-drive-dds-participants.md)(참여자 생성 = 탐색 폭주 계열) · [Foxglove 4 초 스냅](foxglove-snap-cpu.md)(느린 구독자 계열의 앞 사례) · ['후진하고 멈췄다'](cpu-load-stalls.md)(같은 TF 조회 실패 서명의 09-09 판) · [회전 방식 · 앞 회전 우선](rotation-method-track-ratio.md)(PreferForward 15 의 출처) · [micro-ROS 보드율 회귀](microros-baud-regression.md)(다른 통신 손실 — 보드 UART) · [빠른 prep](prep-fast-startup.md)(같은 날 §10 · §13, 조회 묶기 = 참여자 줄이기) · [상자 옆 정지 — 원인](box-side-stall-cause.md)(f2f1 멈칫 · f2o1 중단의 통신 아닌 몫) |

**한 줄**: 10-12 PreferForward 15 검증 주행에서 로버가 상자 옆에서 멈칫하고(f2f1) 다음 주행들은 목표 도중 중단됐다. bag 의 `/tf` 수신이 주행 도중 어느 순간 **50 → 5~20 Hz** 로 무너지고 끝까지 안 돌아오며, 그동안 TF 를 듣는 노드(EKF · 위치 추정 · rf2o 등)만 1.5~3.5 배 무거워졌다. 하루 10 회 주행 A/B 로 '**MPPI 궤적 발행 206 kB × 10 Hz + PreferForward 15**' 일 때만 생긴다(6/6)는 대응을 찾았고, 발행을 1/7(`lite`, 28 kB)로 줄이자 사라졌다(0/2). 계측(f2j1)으로 포화 = UDP 통신량 10 배 · 수신 버퍼 손실 수천 /s 임을 쟀고, 10-13 루프백 캡처(f2m1)로 늘어난 패킷의 79 % 가 `/tf` 쓰는 쪽 2 곳의 **HEARTBEAT**, 가장 먼저 뒤처진 읽는 쪽이 **bag 기록기** 임을 봤다. 기록기만 `/tf` 를 best effort 로 받게 하자 206 kB 발행 그대로도 포화가 없었다(f2n1). 즉 포화는 주행 스택보다 **계측(기록기)이 시작한 것**일 가능성이 높다(추정). PreferForward 5 에서 왜 안 생기는지는 발행량 · 간격 · 기록기 CPU 어디서도 차이를 못 찾아 미확정으로 닫았다.

## 1. 증상
- **f2f1(10-12 §1.2 · §2)** — 3/3 성공했지만 복귀 상자 구간(map x 2.6 → 0.4)이 **67 s**(10-08 f2e2 44 s), 느린 시간 11 s, 정지 2 회 · 후진 3.5 s · 지령 없음 5.1 s(펌웨어 워치독 정지). 사용자: "상자 주변에서 행동이 매끄럽지 못했다."
  - 부하(`jobs/top_eval.py`): 전체 69 → 92 %, EKF 21 → 53 · 위치 추정 31 → 47(코어 1 개 = 100). 집계 줄 원문은 원천 소실(10-12 정리 페이지가 표시, `outputs/f2f1_cpu.txt` 는 출력 형식이 다름).
  - TF 끊김(`jobs/gap_eval.py` → [`f2f1_gaps.txt`](../debug_log/2026-10-12/outputs/f2f1_gaps.txt)):
    ```
    tf odom→base_link        n   5631 수신 끊김 30: 10:32:40.1(1.8 s) 10:33:42.1(2.8 s) 10:34:15.2(2.6 s) 10:35:04.1(3.5 s) 10:35:07.8(2.0 s) …
    tf odom→base_link        n   6658 수신 끊김 0:                     ← f2e2(10-08)
    ```
  - Nav2(`outputs/f2f1_navlog.txt`): 10:35:07 컨트롤러 "미래 시각 TF" → follow_path 중단, 10:35:09 `PathBlockedAhead`, 10:35:14 계획 서버 응답 시간 초과, 10:35:28 · 29 중단 2 회. 그날 해석은 '연산 부하 → 중단 반복 → 멈춤이 멈춤을 부름'(§2, 계기 미확정).
- **f2f3(§3.3)** — 목표 1 도중(출발 50 s 뒤)부터 끝까지, 목표 3 ABORTED. 컨트롤러 "미래 시각 TF" 22 회 · follow_path 중단 24 · 서버 응답 시간 초과 15 · BT 틱 초과 767. `/cmd_vel` 0.5 s 넘는 끊김 9 회(최대 9.9 s). `/tf` 수신 50 → 약 10 Hz([`f2f3_tf.txt`](../debug_log/2026-10-12/outputs/f2f3_tf.txt) 첫 줄 `f2f3 컨트롤러 TF 미래 오류 odom→map n 22: 요청−최신 중앙 0.071 s [0.013~0.829]`).
- **'포화' 의 정의(10-12 §4 에서 주행 전 선언, 이후 모든 판정에 씀)**: bag `/tf` 수신 10 s 평균이 25 Hz 아래인 칸 ≥ 3 **그리고** follow_path 중단 ≥ 1.
- 그림: [`2026-10-12_tf_rate_runs.png`](../04_navigation/figures/2026-10-12_tf_rate_runs.png)(10 회의 `/tf` 수신) · [`2026-10-12_udp_storm.png`](../04_navigation/figures/2026-10-12_udp_storm.png)(계측 4 회 UDP) · [`2026-10-12_cpu_saturation.png`](../04_navigation/figures/2026-10-12_cpu_saturation.png)(f2f3 포화 전후 부하) · [`2026-10-13_bag_reception_f2m1_f2n1.png`](../04_navigation/figures/2026-10-13_bag_reception_f2m1_f2n1.png)(기록기 수신 부족률).

## 2. 흐름 (시간순)
jobs · outputs 는 [2026-10-12](../debug_log/2026-10-12/) · [2026-10-13](../debug_log/2026-10-13/) 아래. 같은 부팅(10-12 09:42), 코스 b910(B → W3 동쪽 → 출발), 상자 ①·② 제자리. 10-12 구성 = B 구성(전역 nvblox map 프레임 + 재계획 0.5 Hz + rf2o · G4 잔차) — 아래 표의 '그림자' = 비교용 그림자 EKF A, 'viz' = `mppi_viz`.

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-12 §1 · §2 | f2f1(PF 15 · 그림자 켬 · viz true) + 상자 구간 분석 | 위 §1. 부하 상승(10:35:04)이 첫 중단(10:35:07)보다 먼저 | 직접 원인 = 연산 부하로 Nav2 중단 · 재시작 반복(측정). 계기 미확정, 후보 'EKF 2 개 · 재부팅 뒤 경과' — ❌ 'EKF 2 개' 는 §7.3 에서 기각(실수 ①) | `f2f1_box_smooth.txt` · `f2f1_gaps.txt` · `f2f1_navlog.txt` · bag `bags/bag_f2f1.tgz` |
| 10-12 §3.3 | f2f3 재현(같은 구성) | `/tf` 50 → 10 Hz, 프로세스 부하가 f2f1 과 **같은 모양**(EKF 22 → 54 · 위치 추정 21 → 51 · rf2o 4 → 13, 합계 416 → 498). f2e2 대비 실행 중 파라미터 차이 = PreferForward 5 → 15 하나 | 정해진 '포화 상태' 로 넘어가는 현상(측정). /tf 재전송 폭주(추정), 방아쇠 미확정 | [`f2f1_f2f3_proc.txt`](../debug_log/2026-10-12/outputs/f2f1_f2f3_proc.txt) · `f2f3_navlog.txt` · `nav2_f2f3.log.gz` |
| 10-12 §3.4 | 사용자 "중복 실행인지 확인"(`job961_dup.sh` · `job962_dup2.sh`) | 스택 중복 0. `/rf2o_laser_odometry` 노드 이름 2 개(프로세스 1). **러너 top 루프가 주행 뒤 약 15 분 남음**(f2f2 잔류가 f2f3 시작 1.5 분과 겹침) | 중복은 원인 아님. 잔류 루프는 내 결함 → pid 고침(실수 ⑥) | [`j961_dup.txt`](../debug_log/2026-10-12/outputs/j961_dup.txt) |
| 10-12 §4 | f2g1 — **PF 5** 로만 되돌림(같은 부팅) | `/tf` 내내 50 Hz, 3/3, 후진 2.93 m 재현. 순간 중단 6 회(정상 주행에도 있음) | 포화 없음. 사용자 "후진 벌점이 문제라고 판단되지 않는다" 에 동의했으나 데이터는 반대(5 에서 0/2, 15 에서 2/2) | [`f2g1_tf.txt`](../debug_log/2026-10-12/outputs/f2g1_tf.txt) · `f2g1_navlog.txt` |
| 10-12 §5 | f2g2 — PF 15 교차 확인(첫 prep 값 지정 누락 → 재실행, 실수 ⑤) | 출발 81 s 뒤 50 → 6~17 Hz, 목표 3 ABORTED. 주행 중단 뒤 정지 상태 `/tf` 45 Hz · CPU 평상 | **15 에서 3/3, 5 에서 0/1(10-08 포함 0/2)** — 상관은 측정, 기전 미확정. '15 는 회전이 늘어 부하 문턱' 가설 ❌(§8.1 기각, 실수 ②). 포화는 주행 중에만 유지 | `f2g2_tf_cpu.txt` · [`j965_state.txt`](../debug_log/2026-10-12/outputs/j965_state.txt) |
| 10-12 §6 | f2h1 — 그림자 EKF 끔 + **궤적 발행 끔** + PF 15 | 3/3, 포화 없음, 미래 시각 TF 0 회, 후진 0.24 m | '여유를 만들면 사라진다' 와 맞음. 둘 중 어느 쪽이 결정적인지 미분리 | `f2h1_tf_cpu_box.txt` · `f2h1_navlog.txt` |
| 10-12 §7.2 · §7.3 | 사용자 "MPPI 는 기록하는 게 좋지 않을까?" → f2i1 = 그림자만 끔 · **궤적 발행 켬** | 40 s 뒤 포화, 목표 3 ABORTED. **EKF 1 개인데 11.8 → 38.6**. `/trajectories` 1 개 **206 kB**(마커 832) | **결정적인 것은 궤적 발행**(15 + 발행 켬 4/4 · 끔 0/1 · 5 + 켬 0/3). `lite` 추가(계산 28 kB) | `f2i1_tf_cpu_traj.txt`(`traj_size.py`), 커밋 `cd6313ba` |
| 10-12 §8.1 | 사용자 "왜 5 는 되고 15 는 안 되나"(`onset_ctx.py`) | 포화 직전 20 s 는 4 회 모두 **거의 직진 0.075 m/s**. 도는 칸 vs 직진 칸 부하 합계 358 → 382 · 373 → 363 · 368 → 377 | '회전 부하' 가설 기각. 5/15 차이 **설명 못 함**, 확률적 현상 가능성 | [`onset_ctx.txt`](../debug_log/2026-10-12/outputs/onset_ctx.txt) |
| 10-12 §8.2 | 사용자 "다른 프로세스와 충돌인가"(`job967_net.sh`) | `/trajectories` 발행자 1 · 구독자 = 주행 중 기록기뿐. **rmem_default = rmem_max = 212,992 B**(206 kB 메시지와 거의 같음). 부팅 뒤 누적 `RcvbufErrors` 8,592,442 / 133,271,653(6.4 %) | 논리적 충돌 없음, 공유 자원(UDP 수신 버퍼) 경합 정황(추정). 누적값이라 포화 순간은 못 봄 → 러너에 2 s 손실 기록 추가 | [`j967_net.txt`](../debug_log/2026-10-12/outputs/j967_net.txt) |
| 10-12 §8.3 ~ §8.6 | 공유메모리 질문들(검토만) | 호스트 Fast DDS 2.6.12, nvblox 컨테이너 `ipc host`, 에이전트 SHM 끔 | 지금은 안 바꿈(§8.3) → 사용자 방향은 SHM(§8.6 · §17). §8.3 은 질문 오독(실수 ⑦) | [`j968_shm.txt`](../debug_log/2026-10-12/outputs/j968_shm.txt) — 상세는 [DDS 공유메모리 카드](dds-shm-incident.md) |
| 10-12 §9 | f2j1 계측 재현(f2i1 구성 + 2 s UDP 기록) | 평상 수신 약 5,300 /s · 손실 0~2(**기록기 소켓만**). 15:05:13 수신 7,224 → :15 19,626 → :17 **52,608 · 손실 2,913**. 통신량이 손실보다 먼저 | 포화 = 통신량 10 배 폭증(측정). 버퍼 넘침은 결과 · 유지 요인. 선언 창으로는 2.6 배 = '부분' — 창 설계 결함(실수 ④) | [`f2j1_net_anal.txt`](../debug_log/2026-10-12/outputs/f2j1_net_anal.txt) · `net_f2j1.log.gz` |
| 10-12 §11 | f2k1 — 기록기가 `/trajectories` 만 best effort | 포화 전 손실 0~2 /s, 기록 9.5~10.1 Hz. **목표 1 도착 순간(15:25:19)** 45,279 /s · 손실 1,492, 목표 2 ABORTED | 대책 1 효과 없음 → '기록기 재전송 씨앗' 기각 — ⚠ 10-13 에 절반 뒤집힘(씨앗은 기록기가 맞고 대상 토픽이 `/tf`, 실수 ③) | [`f2k1_net_anal.txt`](../debug_log/2026-10-12/outputs/f2k1_net_anal.txt) |
| 10-12 §12 | f2l1 — `mppi_viz:=lite` | 메시지 **28 kB**(마커 112), 0.26 MB/s, `/tf` 내내 50 Hz, 3/3. 2 만 /s 넘는 칸 3 개는 모두 **목표 전환 직후**(탐색 폭주, 2~4 s 회복) | 효과 있음 — 포화를 부르는 것은 궤적 발행의 양(측정된 대응) | [`f2l1_net_anal.txt`](../debug_log/2026-10-12/outputs/f2l1_net_anal.txt) |
| 10-12 §13 · §14 | f2l2(lite 반복, 빠른 prep) · 마무리 | 3/3, 포화 없음 → lite 2/2 | **운용 구성 확정**: 그림자 EKF 끔 + lite + PF 15(`CLAUDE.md` §6). 미해결: 최초 계기 · 5/15 차이 · 전환 탐색 폭주 | [`f2l2_net_anal.txt`](../debug_log/2026-10-12/outputs/f2l2_net_anal.txt), 커밋 `08faa968` |
| 10-12 §17 | 사용자 "UDP 버퍼는 늘렸나? CPU 문제?" | **늘리지 않음**(208 kB 그대로) | 해결은 발행량을 줄여 피한 것. 버퍼 키우기 = 지연 증가 · 소켓 약 180 개 × 상한(지식 기반 설명) | 측정 없음 |
| 10-12 §20 · §21 | "버퍼에 쌓여 생기나, 수신 쪽은 무엇인가" · "BT 요청 폭주라면?" | f2g2 Nav2 로그 분당: smoother 27.6 → 17.6 · "Passing new path" 25.1 → 14.1 · 응답 시간 초과 0 → 7.5 | 늘어난 5 만여 개/s 의 종류 · 송신자는 **모름**. (나) 'BT 요청 폭주' 는 요청 수(분당 수십)로 설명 불가 → 약함. §20 에서 (나)를 (가)와 같은 무게로 쓴 것 정정(실수 ⑧) | 분석 출력은 §5.2 Nav2 로그 집계(원문 `nav2_f2g2.log.gz`) |
| 10-12 §22 | 사용자 "캡처 한 번 하고 넘어가자" | — | 판정 초안을 주행 전에 선언 | — |
| 10-13 §0 · §1.1 | 캡처 준비: `anal_rtps_pcap.py`(합성 pcap 검증), 러너 `CAP_PCAP=1`, 사용자 `sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump` | prep 64 s, viz true(20/2), PF 15 | 주행 가능 | `outputs/prep_f2m1.txt` |
| 10-13 §1.2 | **f2m1** 포화 재현 + 루프백 캡처(1.24 GB) | RTPS 4,794 → **56,350 /s**, HEARTBEAT 450 → **44,739 /s(79 %)** = SLAM 23,283 + EKF 20,780(모두 `rt/tf`). NACK_FRAG 0. 0.2 s 한 칸에 평상 → 폭주. 10:19:40.91 `ros2`(pid 65844) 혼자 70 → 92 개 뒤처짐 | **H-재전송 성립**(85 %), H-데이터 · H-탐색 기각. 가장 먼저 뒤처진 읽는 쪽 = 기록기(pid 로 판단, 명령줄 미확인) | [`cap_f2m1_anal2.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_anal2.txt) · [`cap_f2m1_onset.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_onset.txt) · [`cap_f2m1_acklag.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_acklag.txt) · [`net_f2m1.log`](../debug_log/2026-10-13/outputs/net_f2m1.log) |
| 10-13 §2 · §2.1 | **f2n1** — 한 가지만: 기록기 `/tf` best effort(`BAG_BE_TF=1`), viz true 그대로 | 3/3, 전체 약 4,810 /s 일정, `/tf` HEARTBEAT **6~7 /s**, bag `/tf` 49.3~50.1 Hz | **추정 지지**(viz true + 15 는 그때까지 7/7 포화, 이번 0/1). 포화는 계측이 만든 것일 가능성. 선언문이 탐색 급증을 미리 구분하지 못한 흠(실수 ⑨) | [`cap_f2n1_anal.txt`](../debug_log/2026-10-13/outputs/cap_f2n1_anal.txt) · [`net_f2n1.log`](../debug_log/2026-10-13/outputs/net_f2n1.log) · `run_f2n1.txt` |
| 10-13 §3.1 | bag 수신 시각화(`fig_bag_reception.py`) | 받은 비율 `/tf` f2m1 **23 %** · f2n1 100 %, `/tf` 최대 간격 4,417 ms · 152 ms | f2n1 수신 정상. 발행 멈춤과 미수신은 그림만으론 구분 못 함 | [`bag_reception.txt`](../debug_log/2026-10-13/outputs/bag_reception.txt) |
| 10-13 §3.2 · §3.3 | PF 5 vs 15: 발행 데이터 양 · 간격(`anal_bag_rates.py`), 포화 전 기록기 CPU(`anal_recorder_cpu.py`) | `/trajectories` 206,341 B 동일, 8.4 vs 8.9 Hz, 합계 2,453 vs 2,526 kB/s. 기록기 CPU 20.2 vs 19.8 · 20.3 % | 차이 없음 → **5 대 15 기전 미확정으로 닫음**(사용자 "닫고 넘어가자"). 재개 조건 = lite 또는 BE `/tf` 에서도 포화 재발 | [`bag_rates_pf.txt`](../debug_log/2026-10-13/outputs/bag_rates_pf.txt) · [`recorder_cpu.txt`](../debug_log/2026-10-13/outputs/recorder_cpu.txt) |
| 10-13 §4.1 · §4.2 | 러너 수정 2 건(사용자 "5번, 6번 먼저") | `BAG_BE_TF` 기본 0 → 1. `job613 --serve` 상주(정지 시험 3 건 연속 YAW, 잔류 0) | — | 커밋 `2ea17ea7` · `jobs/chk_pathyaw_serve.sh` |
| 10-13 §4.4 | f2o1 검증(lite + BE `/tf` + 상주 조회기) | 소켓 손실 **주행 전 구간 0 /s**(전환 칸 포함), `/tf` 49~51 Hz. lite 수정 전 f2l1 · f2l2 의 전환 칸(10 s 평균) 1,208 · 1,564 · 2,278 · 2,510 /s | 전환 급증 = 목표마다 띄우던 조회기 탓(수정 전 2 회 vs 뒤 1 회). 목표 3 중단은 통신 아닌 상자 옆 정지(→ [상자 옆 정지 — 원인](box-side-stall-cause.md)) | [`net_f2o1.log`](../debug_log/2026-10-13/outputs/net_f2o1.log) · `run_f2o1.txt` |
| 10-13 §10 | 사용자 "포화가 오히려 상자를 피하게 했나" | 상자 옆 통과 6 회 중 포화는 f2f1 1 회, 포화 4 회 중 3 회는 상자 전에 중단 | 아니다 — 상자 옆은 원래 2.8~4.7 cm 로 아슬아슬([상자 옆 정지 — 원인](box-side-stall-cause.md)) | `outputs/box_pass.txt` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| EKF 2 개(본체 + 그림자 A)라 무겁다(10-12 §2) | f2i1: 그림자 끔 | EKF **1 개** 11.8 → 38.6(3.3 배), 포화 그대로 | **기각**(측정) |
| PF 15 는 회전이 늘어 부하 문턱을 넘긴다(§5.2 · §6.2) | `onset_ctx.py`: 포화 직전 지령 · 도는 칸 vs 직진 칸 부하 | 4 회 모두 직진 0.075 m/s, 부하 차 −10 ~ +24(합계 약 370 중) | **기각**(측정) |
| 중복 · 잔류 프로세스(§3.4) | `job961` · `job962` | 스택 중복 0, 잔류 top 루프는 f2f1 에는 없었음 | **기각**(f2f1 이 설명 안 됨) |
| MPPI 궤적 발행량이 결정적(§7.3 · §12) | 같은 PF 15 로 발행 원래대로 / lite / 끔 | **6/6 · 0/2 · 0/1** | **지지**(측정된 대응) |
| 기록기가 궤적 메시지 **조각**을 잃어 재전송이 폭주의 씨앗(§9.2) | f2k1(기록기 `/trajectories` BE) + f2m1 NACK_FRAG | f2k1 포화 그대로. f2m1 포화 창 NACK_FRAG **0**, DATA_FRAG 103 → 101 | **기각**(조각 재전송으로서) |
| BT 액션 · 서비스 요청 폭주(§20 (나)) | f2g2 Nav2 로그 분당 횟수 | 수십 회/분, 일부는 감소 | **약함 → 기각에 가까움**(5 만 /s 를 설명 못 함) |
| **H-재전송**: 신뢰성 확인 신호(HEARTBEAT · ACKNACK)가 과반 · 평상 10 배(10-13 §1 선언) | `anal_rtps_pcap.py` 평상 4 s vs 포화 20 s | HEARTBEAT + ACKNACK **85 %**, HEARTBEAT 99 배 | **성립**(측정) |
| H-데이터(특정 토픽 DATA 과반) · H-탐색(탐색 포트 과반) | 같은 출력 | DATA 14 %, 탐색 포트 증가 없음 | **기각** |
| 가장 먼저 뒤처진 읽는 쪽 = bag 기록기 | `anal_rtps_acklag.py` + 소켓 첫 손실 순서(`anal_udp_drops.py`) | 10:19:40.91 `ros2`(65844) 혼자 −70, 다른 11 곳 0. 소켓 첫 손실 기록기 10:19:42 → 나머지 :44 ~ :48 | **지지**(측정) — `ros2` = 기록기는 pid · 수신량으로 판단(명령줄 미확인) |
| 기록기를 `/tf` best effort 로 바꾸면 포화가 사라진다(개입) | f2n1 | 0/1(그 전 viz true + 15 는 7/7) | **지지(1 회)** — 우연 확률은 낮으나 확정 아님 |
| 기록기 소켓이 206 kB 궤적으로 넘쳐 `/tf` 가 함께 버려진다(10-13 §1.2 해석 1) | 소켓이 하나라는 구조 · 버퍼 크기 · f2j1 평상 손실 | 평상에도 기록기 소켓만 1~2 /s 손실(f2j1) | **추정**(구조 정황, 순간 관측 없음) |
| Fast DDS 는 보관함이 안 비면 발행마다 모든 읽는 쪽에 HEARTBEAT(해석 2) | 소스 · 문서 | 확인 안 함. 캡처의 HEARTBEAT 목적지는 '(모두)' | **미확인** |
| PF 5 vs 15 의 발행량 · 간격 · 기록기 CPU 차이 | `anal_bag_rates.py` · `anal_recorder_cpu.py` | 크기 동일, 주기 3 % · CPU 0.5 %p 안 | **기각** — 5 에서 0/3 인 이유는 **미확정(닫음)** |
| 러너 `netmap`(/proc/*/fd 훑기, 시작 15 s 뒤)이 f2m1 방아쇠(§1.2 해석 5) | 시각 대조 | f2m1 은 포화 시작과 1 s 안 겹침. 10-12 포화 6 회 중 f2f1 · f2f3 · f2g2 · f2i1 은 손실 기록(netmap) 도입 전 | 10-12 의 원인일 수 없음, f2m1 방아쇠였는지는 **구분 못 함** |
| 목표 전환 때 탐색 폭주 = 목표마다 띄우던 조회기 프로세스 | 상주화 전후(lite 끼리) | 전환 칸 1,208 ~ 2,510 /s(f2l1 · f2l2) → 0 /s(f2o1) | **지지**(수정 전 2 · 뒤 1 회) — 포화와는 별개 문제 |

판별에 쓴 핵심 줄과 결과(§2.3):
- 포화 창 집계 — `Docs/tools/anal_rtps_pcap.py` 135 · 137~139 행:
  ```python
  for k, body, fl, src, dst in sm:
      A['kind'][k] += 1
      ...
      if k in WRITER_SIDE:
          off = 4 if k in ('DATA', 'DATA_FRAG') else 0; wid = body[off + 4:off + 8]; A['wr'][(k, src + wid)] += 1
  ```
  결과([`cap_f2m1_anal2.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_anal2.txt), 부른 형태 `jobs/anal_cap_f2m1b.sh`: `--onset 10:19:40 --win 20 --base 10:19:36,4`):
  ```
  == 평상(10:19:36 부터 4 s): RTPS 패킷 4794 개/s · 8870 kB/s (RTPS 아닌 UDP 0 개/s)
    하위 메시지 종류(개/s · 비율): DATA 3745 (77 %) · ACKNACK 594 (12 %) · HEARTBEAT 450 (9 %) · DATA_FRAG 103 (2 %)
  == 포화(시작 뒤 20 s): RTPS 패킷 56350 개/s · 14400 kB/s (RTPS 아닌 UDP 0 개/s)
    하위 메시지 종류(개/s · 비율): HEARTBEAT 44739 (79 %) · DATA 8024 (14 %) · ACKNACK 3588 (6 %) · DATA_FRAG 101 (0 %) · NACK_FRAG 0 (0 %)
        23283  HEARTBEAT      localization_sl[0254862100000100] rt/tf
        20780  HEARTBEAT      ekf_node[69536c1a00000000] rt/tf
  ```
- 시작 순간 — `Docs/tools/anal_rtps_onset.py` 39~40 행(`/tf` 쓰는 쪽의 DATA · HEARTBEAT 를 0.2 s 칸으로) → [`cap_f2m1_onset.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_onset.txt):
  ```
  10:19:40.5   1001 | ekf_no 60 locali 40 | 0 | - | -
  10:19:40.7   5342 | ekf_no 451 locali 40 | 3920 | planner_server[3c540722] 24 controller_serv[385497c9] 22 localization_sl[02548621] 12 | (모두) 3920
  10:19:41.0  14056 | ekf_no 748 locali 487 | 11355 | controller_serv[385497c9] 106 planner_server[3c540722] 98 nvblox_node[c6558318] 55 | (모두) 11355
  ```
  이번 카드 작성 때 남아 있던 발췌 캡처 `2026-10-13/bags/cap_f2m1_onset.pcap.gz`(16 MB)로 같은 명령(`10:19:40 1.2`)을 다시 돌려 위 세 줄이 **그대로** 나왔다(11-03, PC).
- 뒤처진 읽는 쪽 — `Docs/tools/anal_rtps_acklag.py` 51~52 행:
  ```python
  if t <= ta < t + 1.0: got[rd] = (base - 1, nb, ta - t)   # base = 아직 못 받은 첫 번호 → base−1 까지 받음
  lag = sorted(((l1 - v[0], rd, v) for rd, v in got.items()), key=lambda x: -x[0])
  ```
  결과([`cap_f2m1_acklag.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_acklag.txt) 20~23 행, ekf `/tf`):
  ```
  10:19:40.91 HB first 23685 ~ last 23774 (보관 90 개) | 1 s 안 확인 12 곳 | 가장 뒤처진 곳: ros2[340166cc] −70(누락 표시 100, +1.00 s) · bt_navigator[4054da27] −-21(…)
  10:19:41.68 HB first 23699 ~ last 23797 (보관 99 개) | 1 s 안 확인 12 곳 | 가장 뒤처진 곳: ros2[340166cc] −92(누락 표시 100, +0.32 s) · …
  ```
  (발췌 캡처로 11-03 재실행 — 10:19:40.91 · 41.16 두 줄 동일)
- f2j1 통신량이 손실보다 먼저 — [`f2j1_net_anal.txt`](../debug_log/2026-10-12/outputs/f2j1_net_anal.txt) 2 s 표(이 표를 낸 스크립트는 `jobs/` 에 없음 — **스크립트 원천 소실**, `net_anal.py` 는 창 평균 · 소켓 표만 낸다):
  ```
  15:05:11    5286      0 |          0 …
  15:05:13    7224      2 |          2 …
  15:05:15   19626      2 |          2 …
  15:05:17   52608   2913 |       1020        990         75        191        308 …
  ```
- PF 5 vs 15 발행량 — `Docs/tools/anal_bag_rates.py` 25 · 37 행(토픽별 `n[t] / d` · `by[t] / max(n[t], 1)`) → [`bag_rates_pf.txt`](../debug_log/2026-10-13/outputs/bag_rates_pf.txt):
  ```
  /trajectories                                    8.4 · 206341 · 1742.9     8.9 · 206341 · 1830.9
  /tf                                                    49.7 · 96 · 4.8           49.7 · 96 · 4.8
  합계(메시지/s · kB/s)                                            412 · 2453                385 · 2526
  ```

## 4. 조치와 효과
| 조치 | 언제 · 근거 | 효과(측정) | 한계 |
|---|---|---|---|
| 그림자 EKF A 끔(`shadow:=false`) | 10-12 §6 · §14 | 단독으로는 효과 없음(f2i1 포화) — 부하 −10 정도 | 비교용 `/odometry/ekf_a` 를 잃음(영상 손실 없음, §6.3) |
| `mppi_viz:=lite`(후보 10 × 8 + 최적 32 = 마커 112, 28 kB) | 10-12 §7.3 신설, §12 · §13.1 검증 | PF 15 에서 0/2(f2l1 · f2l2), 이후 운용 기본 | 영상에 후보 퍼짐만 남음. 기전을 고친 것이 아니라 소켓에 들어가는 양을 줄인 것 |
| 기록기 `/trajectories` best effort(`BAG_BE_TRAJ`, 기본 켬) | 10-12 §11 | **효과 없음**(f2k1) — '해도 없음' 으로 남김(§14) | 근거 주석이 지금도 '재전송 씨앗' 을 말함(§6-7) |
| 기록기 `/tf` best effort(`BAG_BE_TF`, 기본 켬) | 10-13 §2 시험 → §4.1 기본 | viz true(206 kB) 그대로 0/1(f2n1), bag `/tf` 손실 없음. f2o1 이후 lite 와 함께 | 1 회. '느린 reliable 구독자 하나가 `/tf` 쓰는 쪽을 붙잡는' 약점 자체는 스택에 남음(rviz · foxglove 등, 10-13 §2.1) |
| 경로 조회기 상주(`job613 --serve`) | 10-13 §4.2 | 목표 전환 칸 손실 1,208 ~ 2,510 → 0 /s(f2o1) | 조회기가 죽으면 예전 방식으로 되돌아감(로그 남김) |
| 러너 top 루프 pid 고침 · UDP 손실 2 s 기록 · 캡처 옵션 | 10-12 §3.4 · §8.2, 10-13 §0 | 잔류 0, 포화 순간 계측 가능 | 손실 기록은 10-27 에 `NET_LOG=1` 일 때만으로 바뀜(§4.1) |
| 수신 버퍼 키우기 · DDS 공유메모리 | 10-12 §8.3 · §17 결정 | 이 시기 미실행 | rmem 208 kB 그대로(10-13 §0 `rmem_max 212,992`). 공유메모리는 이후(10-20) |

### 4.1 지금 코드에서 이 문제와 닿는 곳 (11-03 확인, 바꾸지 않음)
| 항목 | 지금 값 · 위치 | 이 카드와의 관계 |
|---|---|---|
| 러너 기록기 QoS 재정의 | 저장소 최신 사본 `Docs/debug_log/2026-10-27/jobs/job551_f0drive.sh`(PC 러너 `run_f0.sh` 가 올리는 스크래치패드 원본과 11-03 대조 결과 동일) — `:46` `QOSOPT=""; if [ "${BAG_BE_TRAJ:-1}" = 1 ]; then printf '/trajectories: …` · `:54` `[ "${BAG_BE_TF:-1}" = 1 ] && printf '/tf: reliability: best_effort … depth: 100` · `:67` `QOSOPT="--qos-profile-overrides-path /tmp/bag_qos_$NAME.yaml"; fi` · `:71` `ros2 bag record -o $BAG $QOSOPT $TOPICS` | 10-13 §4.1 그대로 기본 켬. ⚠ **`/tf` 재정의가 `BAG_BE_TRAJ` 의 `if … fi` 안에 들어 있다** — `BAG_BE_TRAJ=0` 을 주면 `/tf` 도 reliable 로 돌아간다(코드 읽기, 실행 확인 안 함). `run_f0.sh:10` 은 `BAG_BE_TF` 만 넘기고 `BAG_BE_TRAJ` 는 넘기지 않아 지금은 늘 1 |
| 궤적 기록 여부 | 같은 파일 `:43` `[ "${LONG_REC:-0}" = 1 ] && TOPICS="$TOPICS /trajectories /transformed_global_plan"`, 순회 러너 `Docs/debug_log/2026-10-22/jobs/run_f2c.sh:12` `LONG_REC=${LONG_REC:-1}` | 순회만 궤적을 기록(그 외 주행은 기록기가 `/trajectories` 를 안 받음) |
| 손실 기록 | 같은 파일 `:81` `[ "${NET_LOG:-0}" = 1 ] && (sleep 15; netmap; …)` · `:83` · `:96`(끝에 `netmap` 한 번) | 10-27 §24 에 기본 끔 — 포화가 재발해도 2 s 손실 자료는 `NET_LOG=1` 로 다시 켜야 남는다 |
| 상주 경로 조회기 | `Docs/debug_log/2026-10-21/jobs/job550_f0run.py:69~82`(상주 → 실패 시 한 번 실행) · `:101 ~ :114`(주행 시작 때 `job613_pathyaw.py --serve` 기동) | 10-13 §4.2 그대로 |
| `mppi_viz` 처리 | `ros2_ws/src/rover_navigation/launch/navigation.launch.py:205`(기본 `'false'`) · `:136~140`(`'1','true','yes','lite'` → `visualize = True`, `lite` 면 `trajectory_step 100 · time_step 4`, 아니면 `20 · 2`) · 주석 `:130~135` | 주석의 '4/4 주행' 은 10-12 §7.3 시점 숫자(최종 6/6, 10-13 7/7 — §6-5) |
| prep 기본 | `Docs/tools/prep_patrol.sh:8` `VIZ=${1:-lite}` · `:9` `lite|true) V="mppi_viz:=$VIZ"` · `:11`(`vslam` 기본: `emitter_off:=true vslam:=on dds_shm:=true`) · `:12`(`rf2o` 일 때만 `shadow:=false` 명시) · `:17` `EXTRA_NAV="global_camera:=nvblox replan_hz:=… $V …"` | 순회 prep 기본 = lite. 그림자 EKF A 는 `ekf.launch.py:23`(`shadow = _truthy(…) and rf2o`) · `:100`(기본 `'false'`)이라 지금 기본(cuVSLAM)에서는 애초에 안 뜬다 |
| nav2_params | `ros2_ws/src/rover_navigation/config/nav2_params.yaml:249` `visualize: false`(주석 246~248: 09-17 mp7 ≈ 5 MB/s), `TrajectoryVisualizer` 키는 yaml 에 없음(launch 가 넣음) · `:264` `PreferForwardCritic … cost_weight: 15.0` | 발행 설정의 원본은 launch. prep 확인은 `Docs/tools/chk_prep.py:31~32`(visualize · trajectory_step · time_step) |
| DDS 전송 | `navigation.launch.py:193` `SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', _FASTDDS_XML)`(`:32` `fastdds_udp_only.xml`) | Nav2 · 기록기 경로는 지금도 UDP 루프백 — 포화가 지나간 길은 구조로 남아 있다. 카메라 ↔ cuVSLAM 만 공유메모리(`dds_shm:=true`, 10-20 ~ 10-23) |

## 5. 내 실수
### 실수 ① 'EKF 2 개라서 무겁다' (10-12 §2 → §7.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2f1 상자 옆 멈칫의 부하 상승 계기를 찾음(`jobs/top_eval.py`) |
| 본 것 | EKF 21 → 53 이 가장 큰 증가, 그날 EKF 는 본체 + 그림자 A 2 개 |
| 처음 추론 | EKF 2 개 + rf2o 가 늦은 측정을 되감아 다시 계산하며 무거워짐 → 후보 ① |
| 의심한 이유 | f2f3 에서 TF 를 듣는 노드만 한꺼번에 1.5~3.5 배(§3.3) — EKF 만의 문제가 아님 |
| 판별 시험 | f2i1: 그림자 EKF 만 끄고 같은 구성 |
| 결론 | EKF **1 개** 로도 11.8 → 38.6(3.3 배), 포화 그대로 — EKF 수는 원인 아님. 부하 증가는 포화의 결과 |
| 다음에 알아보는 법 | 한꺼번에 무거워지는 노드들의 공통점(같은 토픽 구독)부터 본다. 결과 지표(CPU)를 원인 후보로 올리기 전에 그것이 먼저 올랐는지 시각을 대조 |
| 스크립트 핵심 | `2026-10-12/jobs/proc_cmp2.py` 13~14 행 `d[k[1][:22]] += (v - snap[a0][k]) / (b0 - a0)`(구간 양끝 틱 차 / 초) |
| 나온 결과 | `(ekf_node)  21.1  21.3  53.3  21.7  54.1` · `합계  352  372  508  416  498`([`f2f1_f2f3_proc.txt`](../debug_log/2026-10-12/outputs/f2f1_f2f3_proc.txt) 3 · 28 행), f2i1 은 `f2i1_tf_cpu_traj.txt` |

### 실수 ② 'PF 15 는 회전이 늘어 부하 문턱을 넘는다' (10-12 §5.2 · §6.2 → §8.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 15 에서 3/3, 5 에서 0/1 인 대응의 기전 |
| 본 것 | 15 에서는 후진 대신 돌아서 전진(f2f1 §1.2), f2h1(부하를 줄임)에서 포화 없음 |
| 처음 추론 | 회전 중 스캔 처리(위치 추정 포크 · rf2o · EKF)가 무거워져 유휴가 바닥 → TF 지연 → 중단 고리 |
| 의심한 이유 | 사용자 질문 "왜 5 는 되고 15 는 안 되나" — 포화 시작 순간의 동작을 안 봤다 |
| 판별 시험 | `jobs/onset_ctx.py`: 포화 직전 20 s 지령 + 포화 전 '도는 2 s 칸' vs '직진 칸' 부하 |
| 결론 | 4 회 모두 직진 0.075 m/s 중 시작, 도는 칸 부하가 눈에 띄게 늘지 않음 → 기각. f2h1 이 산 이유는 궤적 발행을 함께 꺼서였음(§7.3) |
| 다음에 알아보는 법 | '두 가지를 함께 끈' 시험의 성공을 한 가설의 증거로 쓰지 않는다 — 한 번에 하나(§7.2 에서 사용자가 바로잡음) |
| 스크립트 핵심 | `2026-10-12/jobs/onset_ctx.py` 22 · 37 행 `W = [r for r in R if ep(on) - 20 <= r['e'] < ep(on)]` · `hi = A[:, 0] > 0.2; lo = A[:, 0] < 0.08` |
| 나온 결과 | `f2f1(벌점 15) 시작 10:35:04: 목표 3 · 평균 v +0.074 · … |w|>0.2 인 시간 22 %` · `f2g2 포화 전 33 칸 | … | 합계 373→363 (직진→도는 칸)`([`onset_ctx.txt`](../debug_log/2026-10-12/outputs/onset_ctx.txt)) |

### 실수 ③ '기록기 재전송 씨앗' 기각을 너무 넓게 적음 (10-12 §11.2 · §14 → 10-13 §1.2 · §2.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2j1 의 '평상시 손실은 기록기 소켓뿐' 에서 세운 대책 1(기록기 `/trajectories` best effort) 판정 |
| 본 것 | f2k1 포화 그대로, 포화 전 기록기 손실 0~2 /s |
| 처음 추론 | "평상시 기록기 손실은 원래 미미했고 '재전송 씨앗' 추정은 맞지 않는다"(§11.2) → §14 '기각한 내 판단' 목록, TOOLS.md ✔ |
| 의심한 이유 | 10-13 캡처: 늘어난 것은 궤적 조각이 아니라 `/tf` HEARTBEAT, 처음 뒤처진 읽는 쪽은 기록기 |
| 판별 시험 | f2n1: 기록기 `/tf` 만 best effort |
| 결론 | 씨앗은 **기록기가 맞고**, 붙잡힌 것은 궤적이 아니라 **reliable `/tf`**. f2k1 은 엉뚱한 토픽의 QoS 를 바꾼 시험이었다(소켓으로 들어오는 양은 그대로) — 기각할 수 있었던 것은 '궤적 조각 재전송' 까지 |
| 다음에 알아보는 법 | QoS 를 바꾼 토픽과 '재전송이 일어난 토픽' 을 따로 확인하기 전에는 '읽는 쪽 X 가 씨앗' 을 기각하지 않는다. 패킷 종류(NACK_FRAG · HEARTBEAT)를 먼저 센다 |
| 스크립트 핵심 | 러너 `2026-10-12/jobs/job551_f0drive.sh` 38 행 `QOSOPT=""; if [ "${BAG_BE_TRAJ:-1}" = 1 ]; then printf '/trajectories: …`(`/tf` 재정의 없음) |
| 나온 결과 | `ros2  사용자 데이터  42.5 →  1412.6`([`f2k1_net_anal.txt`](../debug_log/2026-10-12/outputs/f2k1_net_anal.txt)) · f2m1 `NACK_FRAG 0 (0 %)`([`cap_f2m1_anal2.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_anal2.txt)) |

### 실수 ④ §9 판정 창이 사건의 시간 구조와 안 맞음 (10-12 §9.2, 같은 § 에서 인정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | H1(수신 버퍼 손실이 포화 순간 5 배 이상) 판정 |
| 본 것 | 선언 계산식(T = `/tf` 10 s 칸 시작 15:05:10 기준 앞 · 뒤 30 s)으로 726 → 1,859 /s = 2.6 배 = '부분' |
| 처음 추론 | — (선언대로 계산) |
| 의심한 이유 | 앞 30 s 창에 15:04:46 탐색 폭주(2 s 에 손실 10,142)가 들어 있고, T 가 실제 급증(15:05:16)보다 6 s 이름 |
| 판별 시험 | 2 s 자료로 다시 봄 |
| 결론 | 평상 0~2 /s → 1,000 ~ 3,400 /s. 선언 판정은 '부분' 으로 남기고 해석은 2 s 자료로 — 결론(통신량 10 배가 먼저)은 2 s 표 기준 |
| 다음에 알아보는 법 | 판정 창을 선언할 때 '목표 전환 직후 n s 제외' 처럼 알려진 다른 급증을 미리 뺀다. 10 s 칸 기준 시각과 2 s 사건 시각을 섞지 않는다 |
| 스크립트 핵심 | `Docs/tools/anal_udp_drops.py` 18 · 20 행 `for nm, a, b in (('시작~T−30 s', …), ('T−30~T', T - 30, T), ('T~T+30', T, T + 30), …)` · `pre, post = rate(T - 30, T, 2), rate(T, T + 30, 2)` |
| 나온 결과 | `T−30~T  9936 / 726 / 6.8 %` · `T~T+30  58355 / 1859 / 3.1 %` · `→ 손실률 T 뒤 30 s / 앞 30 s = 2.6 배`([`f2j1_net_anal.txt`](../debug_log/2026-10-12/outputs/f2j1_net_anal.txt)) |

### 작은 실수들
- ⑤ **prep 값 지정 누락**(10-12 §5.1): f2g2 첫 prep 을 `W` 없이 돌려 기본 5 로 기동 → 실행 중 5.0 확인으로 발견, 재실행. f2g1(prep 1 번)과 절차가 달라짐을 기록. 데이터 [`j964_prep15.txt`](../debug_log/2026-10-12/outputs/j964_prep15.txt).
- ⑥ **러너 top 루프 pid**(10-12 §3.4): `TOPPID=$!` 를 proc 루프 뒤에서 잡아 top 루프가 주행 뒤 약 15 분 남음 → f2f3 시작과 1.5 분 겹침. 고친 줄 `2026-10-12/jobs/job551_f0drive.sh:48` `TOPPID=$!   # 10-12 §3.4: 여기서 잡아야 함 …`(10-27 판에서 top 루프 자체를 뺌, `:74` `TOPPID=""`).
- ⑦ **공유메모리 질문 오독**(10-12 §8.3 → §8.4): 사용자는 Jetson 통합 메모리를 물었는데 DDS 공유메모리로 답함. §8.3 내용 자체는 유효.
- ⑧ **(나) 가설 무게**(10-12 §20 → §21): 'BT 요청 폭주' 를 재전송 되먹임과 같은 무게로 적었으나 이미 가진 Nav2 로그 수치와 대조하지 않음.
- ⑨ **f2n1 선언문**(10-13 §2.1): "2 배를 넘는 2 s 칸이 없고" 로만 써서 목표 전환 탐색 급증(이미 아는 별개 문제)을 미리 빼지 못함 — 엄격히 읽으면 '중간'. `/tf` 지표 두 개(HEARTBEAT · DATA)는 전 구간 평상.
- ⑩ **그림 어림값**(10-12 §15): 부하 그림 첫 판에 f2g2 의 behavior · smoother · rf2o '포화 전' 값을 어림으로 넣음 → f2f3 한 주행 측정값으로 다시 그림(`jobs/fig_1012.py`).

## 6. 기록 사이 어긋남 (원문 대조, 11-03)
1. **10-12 `TOOLS.md` 'f2k1 … 포화 전 기록기 손실은 원래 0~2'** vs [`f2k1_net_anal.txt`](../debug_log/2026-10-12/outputs/f2k1_net_anal.txt) `ros2 사용자 데이터 42.5 → 1412.6`: 창이 다르다. 42.5 는 `anal_udp_drops.py`(= `net_anal.py`) 의 `srate(v, T - 60, T)`(T = 15:25:20) 창이 15:25:19 표본(기록기 922 /s)을 포함한 값이고, 같은 파일 2 s 표의 15:25:01 ~ :17 은 `2 · 0 · 0 · … · 2` — 둘 다 맞다. 다만 그 줄의 ✔ 표시('기록기 재전송은 씨앗이 아니다')는 10-13 에 절반 뒤집혔다(실수 ③) — `TOOLS.md` 는 고치지 않음.
2. **10-12 §12.2 '전환 직후 손실 4,800 ~ 8,000 /s'** vs **10-13 §4.4 'f2l1 · f2l2 전환 칸 1,208 · 1,564 · 2,278 · 2,510 /s'**: 앞은 2 s 칸 최대(f2l1 요약 줄 `손실/s 중앙 0 · 최대 7986`), 뒤는 `anal_udp_drops.py` 10 s 칸 평균. 11-03 재실행으로 10 s 값 확인: `42:57 1208 … 43:47 1564`(f2l1) · `55:22 2278 … 56:12 2510`(f2l2) · f2o1 전 칸 0. 10-13 정리 페이지는 이 값을 '원천 소실' 로 적었으나 입력(`net_f2l1.log.gz` · `net_f2l2.log.gz` · `net_f2o1.log`)이 남아 있어 **다시 낼 수 있다**.
3. **f2l1 · f2l2 의 'UDP 2 s 칸 98 개 · 수신/s 중앙 5389 …' 요약 줄**과 **f2j1 · f2k1 의 2 s 표**: `net_anal.py` 가 내는 줄이 아니다(그 스크립트는 창 평균 · 10 s 칸 · 소켓 표만). 낸 스크립트가 `jobs/` 에 없음 — **스크립트 원천 소실**(출력은 남음).
4. **10-12 §7.3 '206 kB × 10 Hz → 약 2 MB/s'**: 계산값. `traj_size.py` 출력(`f2i1_tf_cpu_traj.txt` 42 · 45 행)은 기록기가 **받은** 평균 `1.76 MB/s`(f2g1) · `1.35 MB/s`(f2i1, 포화로 덜 받음).
5. **`navigation.launch.py:133~134` 주석 'PreferForward 15 와 함께 쓰면 4/4 주행에서 부하 포화'**: §7.3 시점 숫자. 10-12 최종 6/6(§11.2), 10-13 f2m1 까지 7/7.
6. **10-13 §1.2 '캡처 발췌는 Jetson `/tmp/cap_f2m1_onset.pcap.gz` 에만(재부팅하면 사라짐)'**: 같은 파일이 저장소 폴더 `2026-10-13/bags/cap_f2m1_onset.pcap.gz`(15.7 MB, git 제외 — `.gitignore:50` `Docs/debug_log/*/bags/`)로 PC 에 있다. 이 카드의 재실행은 그 파일로 했다(첫 패킷 10:19:27).
7. **러너 주석 `job551_f0drive.sh:44~45`(10-27 판) '신뢰성 재전송이 통신 폭주(10 배)의 씨앗으로 추정됨'**: 10-12 §11.2 에서 효과 없음으로 판정된 근거가 기본 켬 이유로 그대로 남아 있다(§14 '해도 없음' 이 실제 이유).
8. **10-12 §8.1 '도는 동안 부하가 눈에 띄게 늘지 않는다(f2g1 만 위치 추정 21 → 75)'**: 같은 출력에서 f2g1 합계는 `363→422`(+16 %). f2g1 은 포화가 없던 주행이라 결론(회전 가설 기각)은 그대로지만 합계 증가가 본문에 없다.
9. **도구 머리 주석**: `job965_state.sh` 는 '10-12 §5.3' 이라 적었으나 쓰인 곳은 §5.2(§5.3 없음). `anal_tf_rate.py` 머리 '10-12 §3.3' 은 맞음.
10. **10-13 §1.2 평상 창 4 s**: 캡처가 10:19:24(파일 첫 줄 기준; 발췌 첫 패킷 10:19:27)에 시작돼 포화(10:19:40) 앞에 쓸 수 있는 구간이 짧았고, 10:19:28 ~ 31 기록 시작 직후의 일시 뒤처짐(ros2 −47, 3 s 회복)을 피해 `--base 10:19:36,4` 로 잡았다. 평상 기준이 4 s 표본이라는 점은 본문 표('평상(10:19:36 부터 4 s)')에만 있다.

## 7. 남은 것
- **PF 5 대 15**: viz true 에서 5 는 0/3(f2e1 · f2e2 · f2g1), 15 는 7/7. 발행량 · 간격 · 평균 부하 차이 없음까지 확인하고 **미확정으로 닫음**(10-13 §3.3). 재개 조건 = lite 또는 기록기 BE `/tf` 에서도 포화 재발. 더 파려면 스케줄러 추적(perf sched) 또는 5 로 반복 주행.
- **폭주 순간의 계기**: 평상에도 궤적은 발행 중(DATA_FRAG 103 /s)이었는데 왜 10:19:40.7 인가. f2m1 은 러너 `netmap` 과 1 s 안 겹침 — 구분 못 함.
- **Fast DDS 동작**(보관함이 안 비면 발행마다 전 읽는 쪽에 HEARTBEAT) — 소스 · 문서 확인 안 함. `/tf` DATA 가 5 배 → 8~12 배 는 것이 재전송인지 읽는 쪽별 개별 전송인지도 미구분.
- **스택의 약점**: 느린 reliable 구독자 하나가 `/tf` 를 흔드는 구조는 그대로(rviz · foxglove · 다른 기록기). 기록 없는 주행에서 같은 포화가 생기는지는 확인한 적 없음.
- **러너 결함**: `/tf` best effort 가 `BAG_BE_TRAJ` 조건 안에 묶여 있음(§4.1, 코드 읽기).
- 수신 버퍼(rmem 208 kB) 미변경 — 10-20 §7.1 에서 IR 영상(307 kB)으로 같은 '소켓 버퍼보다 큰 메시지' 문제가 다시 나옴(→ 이후).
- **이후(10-19 ~): 다음 시기에서 채움** — 알려진 포인터만: 10-19 §3 깊이도 기록기 best effort(`job551` 10-27 판 `:60~66`) · 10-20 §7.1 빠짐 원인 = UDP 소켓 수신 버퍼 넘침(IR) · §7.2 ~ §9 공유메모리(N-SHM, 카메라 ↔ cuVSLAM) 도입 · 10-27 §22 SLAM stamp 정체는 통신 탓 아님 · 10-27 §24 러너 손실 기록 `NET_LOG` 기본 끔.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2f1 · f2f3 · f2g2 | PF 15 · 그림자 켬 · viz true — 포화 3/3 | 10-12 §1 · §3.3 · §5.2, `outputs/f0_f2f1_runner.log` 등, bag `2026-10-12/bags/bag_f2f1.tgz` · `bag_f2f3.tgz` · `bag_f2g2.tgz`(로컬), Nav2 로그 `nav2_f2f3.log.gz` · `nav2_f2g2.log.gz` |
| f2f2 | 무효(지도 서버 unconfigured, 주행 안 함) | 10-12 §3.2 — `navmap_ensure` 는 [빠른 prep 카드](prep-fast-startup.md) 몫 |
| f2g1 | PF 5 · 나머지 같음 — 포화 없음 | 10-12 §4.2, `f2g1_tf.txt` · `nav2_f2g1.log.gz` · bag `bag_f2g1.tgz` |
| f2h1 | 그림자 끔 · 궤적 발행 끔 · PF 15 — 포화 없음 | 10-12 §6.2, `f2h1_tf_cpu_box.txt` · bag `bag_f2h1.tgz` |
| f2i1 · f2j1 · f2k1 | 그림자 끔 · viz true · PF 15 — 포화(f2j1 UDP 계측, f2k1 기록기 궤적 BE) | 10-12 §7.3 · §9.2 · §11.2, `f2i1_tf_cpu_traj.txt` · `f2j1_net_anal.txt` · `f2k1_net_anal.txt` · `net_f2j1.log.gz` · `net_f2k1.log.gz` |
| f2l1 · f2l2 | lite · PF 15 — 포화 없음 2/2 | 10-12 §12.2 · §13.1, `f2l1_net_anal.txt` · `f2l2_net_anal.txt` · `net_f2l{1,2}.log.gz` |
| f2m1 | viz true · PF 15 · 기록기 `/tf` reliable + 캡처 — 포화 | 10-13 §1.2, `cap_f2m1_*.txt` · `net_f2m1.log` · `run_f2m1.txt`, 캡처 원본 1.24 GB 삭제(원천 소실) · 발췌 `2026-10-13/bags/cap_f2m1_onset.pcap.gz` · bag `bag_f2m1.tgz` |
| f2n1 | 같고 기록기 `/tf` best effort — 포화 없음 | 10-13 §2.1, `cap_f2n1_anal.txt` · `net_f2n1.log` · `run_f2n1.txt`, 캡처 362 MB 삭제(원천 소실) · bag `bag_f2n1.tgz` |
| f2o1 | lite · BE `/tf` · 상주 조회기 — 러너 수정 검증(통신 부분) | 10-13 §4.4, `net_f2o1.log` · `run_f2o1.txt` |
| 도구(10-12, `2026-10-12/jobs/`) | `gap_eval.py` · `top_eval.py` · `proc_cmp2.py` · `navlog_pc.py` · `tf_rate.py` · `job961_dup.sh` · `job962_dup2.sh` · `job965_state.sh` · `onset_ctx.py` · `job967_net.sh` · `job968_shm.sh` · `net_anal.py` · `traj_size.py` · `job551_f0drive.sh` · `fig_1012.py` · prep 변형 `job963` · `job964` · `job966` · `job969` · `job970` | §9.1 ~ §9.9 |
| 도구(10-13, `Docs/tools/` · `2026-10-13/jobs/`) | `anal_rtps_pcap.py` · `anal_rtps_onset.py` · `anal_rtps_acklag.py` · `anal_cap_f2m1{,b,c,d}.sh` · `anal_cap_f2n1.sh` · `anal_udp_drops.py` · `anal_tf_rate.py` · `anal_traj_size.py` · `fig_bag_reception.py` · `anal_bag_rates.py` · `anal_recorder_cpu.py` · `job613_pathyaw.py --serve` · `job550_f0run.py` · `chk_pathyaw_serve.sh` · `chk_jetson_state.sh` | §9.10 ~ §9.17 |

## 9. 도구 해설
**공통**: 10-12 도구는 번호 이름(규약 전)이라 `2026-10-12/TOOLS.md` 가 사후 색인이다. 10-13 부터 상시 도구는 `Docs/tools/` 에 용도 이름(대응표 `Docs/tools/README.md` 26 · 30 · 49 행: `tf_rate.py` → `anal_tf_rate.py`, `net_anal.py` → `anal_udp_drops.py`, `traj_size.py` → `anal_traj_size.py`). 이 카드의 `Docs/tools/` 도구는 모두 10-13 커밋(`03008a09` · `94b494cd` · `c3977906` · `c30ee747`) 판에서 **그 뒤 변경 없음**(11-03 `git log`). bag 분석은 PC 에서 `rosbags`(AnyReader, Humble 타입) — bag 은 `bags/*.tgz` 를 풀어서. 'bag 의 시각' 은 **기록기가 받은 시각**이다(발행 멈춤과 미수신을 구분 못 함 — 포화 판정 지표 자체가 기록기 쪽 관찰이라는 점이 10-13 에 중요해짐).

### 9.1 `gap_eval.py` — 토픽 · TF 끊김 (10-12 §2, PC)
- **형태**: `python gap_eval.py BAG [0.5]`.
- **하는 일**: 정해 둔 토픽(`/wheel_odom` · `/odometry/filtered` · `/scan` · `/cmd_vel` · `/tf` 등)의 기록 시각 간격 중 `max(TH, 5 × 중앙값)` 넘는 곳, `/tf` 는 odom→base_link · map→odom 의 **수신 간격 > TH** 와 **stamp 간격 > TH** 를 따로, 그리고 수신 − stamp 지연 중앙 · 최대(22~25 행).
- **출력**: [`f2f1_gaps.txt`](../debug_log/2026-10-12/outputs/f2f1_gaps.txt)(f2f1 · f2e2), `f2f3_tf.txt` 의 토픽 줄. **쓰인 곳**: §2 '끊김 30 군데 vs 0', §3.3 `/cmd_vel` 끊김 9.
- **결함 · 지금**: 수신 간격은 기록기 기준. 상시 도구로 옮겨지지 않음 — `anal_tf_rate.py` 가 주기만 대신함.

### 9.2 `top_eval.py` · `proc_cmp2.py` — 부하 (10-12 §2 · §3.3, PC)
- **형태**: `top_eval.py top.log HH:MM:SS HH:MM:SS …`(러너 top 2 s 기록에서 구간별 load · 유휴 · 프로세스 평균), `proc_cmp2.py 이름=proc.log@시작epoch@끝epoch …`(러너 `/proc` 틱 기록, 코어 1 개 = 100).
- **하는 일(`proc_cmp2`)**: 구간 양끝에 가장 가까운 표본의 프로세스별 누적 틱 차 ÷ 초(11~14 행), 이름 앞 22 자로 합침.
- **출력**: [`f2f1_f2f3_proc.txt`](../debug_log/2026-10-12/outputs/f2f1_f2f3_proc.txt), `f2g2_tf_cpu.txt` · `f2h1_tf_cpu_box.txt` · `f2i1_tf_cpu_traj.txt` 의 부하 표. `top_eval` 의 f2f1 집계 줄은 원천 소실.
- **계보 · 지금**: `Docs/tools/anal_proc_cpu.py` · `anal_top.py`(README 대응표). 10-27 에 러너 top 루프는 빠짐.

### 9.3 `navlog_pc.py` — Nav2 로그 사건 집계 (10-12 §3.3 ~, PC)
- **형태**: `navlog_pc.py nav2.log HH:MM:SS HH:MM:SS [N]`. ⚠ 날짜 `'2026-10-12 '` 하드코딩(3 행).
- **하는 일**: WARN · ERROR 줄만, 문구로 종류 분류 — `'transformPose'` · `'Unable to transform robot pose'` → 'TF 미래(컨트롤러)', `'follow_path' + 'Abort'` → 중단, `'Timed out'` → 응답 시간 초과, `'missed its desired rate'` → 루프 미달, `'tick rate'` → BT 틱 초과(6~10 행). 10 s 칸 분포 + 반복 아닌 원문.
- **출력**: `f2f1_navlog.txt` · `f2f3_navlog.txt` · … · `f2i1_navlog.txt`. **쓰인 곳**: §3.3 ~ §7.3 의 중단 · 시간 초과 · 틱 초과 횟수.
- **결함**: 'TF 미래' 에 `Unable to transform robot pose` 까지 묶음 — 미래 외삽과 다른 TF 실패가 섞일 수 있다. **계보**: `Docs/tools/anal_navlog.py`.

### 9.4 `tf_rate.py` = `Docs/tools/anal_tf_rate.py` — `/tf` 수신 주기 ★ 포화 판정 지표 (PC)
- **형태**: `python anal_tf_rate.py BAG`(두 파일 내용 동일, 11-03 `diff`).
- **하는 일**: bag `/tf` 의 각 메시지를 기록 시각으로 10 s 칸에 넣고 칸마다 메시지 수와 프레임 쌍별 변환 수 ÷ 10(13~14 행) — 정상 50 Hz(odom→base_link 30 + map→odom 20).
- **출력 예**(`f2j1_net_anal.txt` 앞부분): `15:05:00  50.0  30.0  20.0` → `15:05:10  8.9  6.0  2.9`. **쓰인 곳**: 모든 주행의 포화 판정(25 Hz 아래 칸 ≥ 3).
- **결함**: 기록기 수신 기준(§9 공통). 첫 · 끝 칸은 기록 시작 · 종료라 반쪽. **지금**: 그대로 쓸 수 있음.

### 9.5 `job961_dup.sh` · `job962_dup2.sh` · `job965_state.sh` — 프로세스 · 정지 상태 (10-12 §3.4 · §5.2, Jetson, 로버 안 움직임)
- `job961`: 실행 파일별 개수 · 시작 시각 · pid, 노드 이름 중복, 러너 잔류물. `job962` 는 데몬 없이 그래프 재탐색. 출력 [`j961_dup.txt`](../debug_log/2026-10-12/outputs/j961_dup.txt)(잔류 top 루프 발견 → 실수 ⑥).
- `job965`: 주행 중단 뒤 `/tf` 주기 · CPU · 루프백 패킷 → [`j965_state.txt`](../debug_log/2026-10-12/outputs/j965_state.txt) — '포화는 주행 중에만 유지' 의 근거. 머리 주석 § 표기 어긋남(§6-9).
- ⚠ 둘 다 `ros2` 명령(DDS 참여자)을 만든다 — 주행 직전 금지 규칙 대상.

### 9.6 `onset_ctx.py` — 포화 직전 동작 · 회전 칸 부하 (10-12 §8.1, PC)
- **형태**: 인자 없음. `RUNS` 표에 주행 · PF 값 · 출발 시각 · 포화 시작 시각 하드코딩(5~6 행), `f0_<이름>/<이름>.csv`(러너 10 Hz) + `proc_<이름>.log` 를 읽음. 날짜 하드코딩.
- **하는 일**: (1) 포화 시작 전 20 s 지령의 평균 v · |w| · |w| > 0.2 비율 · 후진 비율 · 위치. (2) 포화 전 구간(출발 + 5 s ~ 포화 − 4 s)의 2 s 칸마다 |w| 평균과 프로세스 CPU → 도는 칸(|w| > 0.2) vs 직진 칸(|w| < 0.08) 평균(37~40 행).
- **출력**: [`onset_ctx.txt`](../debug_log/2026-10-12/outputs/onset_ctx.txt). 도는 칸이 0 개인 주행(f2f3 · f2i1)은 `→0` 으로 찍힌다(평균할 표본 없음 — 0 부하가 아님).
- **쓰인 곳**: 실수 ② 기각. **지금**: 상시 도구로 안 옮김.

### 9.7 `job967_net.sh` · `job968_shm.sh` — UDP 버퍼 · 공유메모리 사실 (10-12 §8.2 · §8.3, Jetson)
- `job967`: `/proc/sys/net/core/rmem_*` · `/proc/net/snmp` 의 `Udp:` 누적(`RcvbufErrors`) · DDS 프로파일 앞 40 줄 · `ros2 topic info -v /trajectories` · foxglove 접속 · 살아 있는 UDP 소켓 중 drops > 0(inode → 프로세스, 10~11 행). 출력 [`j967_net.txt`](../debug_log/2026-10-12/outputs/j967_net.txt) 첫 두 줄:
  ```
  == 커널 소켓 버퍼: rmem_default 212992 rmem_max 212992 wmem_default 212992 wmem_max 212992 · lo MTU 65536
  == UDP 누적 통계(부팅 뒤): InDatagrams=133271653 NoPorts=159351 InErrors=8592442 OutDatagrams=133537934 RcvbufErrors=8592442 SndbufErrors=0 …
  ```
- **결함**: 누적값이라 포화 순간과 재기동 · `ros2` 조회의 탐색 폭주를 못 가름(§8.2 한계) → 러너 2 s 기록으로 이어짐.
- `job968`: 컨테이너 ipc · 네트워크 · Fast DDS 판 · `/dev/shm` — [`j968_shm.txt`](../debug_log/2026-10-12/outputs/j968_shm.txt), 해설은 [DDS 공유메모리 카드](dds-shm-incident.md).

### 9.8 러너 `job551_f0drive.sh` 의 계측 · QoS 부분 (10-12 · 10-13, Jetson) ★
- **UDP 손실 기록**(10-12 §8.2 추가): 주행 시작 15 s 뒤 `netmap`(모든 jetson 프로세스의 `/proc/<pid>/fd` 소켓 inode → `MAP inode pid comm`), 이후 2 s 마다 `SNMP` 줄(`/proc/net/snmp` 의 `Udp:` 값)과 drops > 0 인 소켓의 `SOCK 포트 drops inode`(`2026-10-12/jobs/job551_f0drive.sh:54~55`). 주행 끝에 `netmap` 한 번 더. → `/tmp/net_<이름>.log` → `outputs/net_*.log(.gz)`.
- **기록 QoS 재정의**(10-12 §11): `/trajectories` best effort · keep_last 5 를 `/tmp/bag_qos_<이름>.yaml` 로 쓰고 `ros2 bag record --qos-profile-overrides-path`(38~45 행). 10-13 §2 에 `/tf` best effort · depth 100 을 같은 파일에 덧붙임(`BAG_BE_TF`), §4.1 기본 1.
- **캡처**(10-13 §0): `CAP_PCAP=1` 이고 `getcap tcpdump` 에 `cap_net_raw` 가 있으면 `tcpdump -i lo -s 512 -w /tmp/cap_<이름>.pcap udp`(10-27 판 `:87~90`).
- **결함 · 지금**: §4.1 의 `/tf` 재정의가 `BAG_BE_TRAJ` 조건 안 · 근거 주석 낡음(§6-7). 손실 기록은 10-27 부터 `NET_LOG=1` 일 때만.

### 9.9 `net_anal.py` = `Docs/tools/anal_udp_drops.py` — UDP 손실 시간순 ★ (PC)
- **형태**: `python anal_udp_drops.py net_<이름>.log HH:MM:SS(포화 시작)`. 10-13 판은 날짜를 기록 첫 줄에서 읽음(4 행, 10-12 판은 `'2026-10-12 '` 고정 — 유일한 차이, 11-03 `diff`). Windows 콘솔에서는 `PYTHONIOENCODING=utf-8` 이 필요(`−` 문자, 11-03 재실행 때 확인).
- **하는 일**: `SNMP` 줄의 `InDatagrams`(4 번째 값) · `RcvbufErrors`(8 번째)를 누적 → 구간 양끝 차 ÷ 초(14~16 행). 창 4 개(시작 ~ T−30 · T−30 ~ T · T ~ T+30 · T+30 ~ 끝), 뒤/앞 30 s 손실 배수, 10 s 칸 초당 손실, 소켓별 T 앞 60 s → 뒤 60 s 초당 손실(포트 짝수 = 탐색 · 생존, 홀수 = 사용자 데이터, 7400 · 7401 = 멀티캐스트 — 27 행), 프로세스 이름으로 합침.
- **출력**: `f2j1_net_anal.txt` · `f2k1_net_anal.txt` 의 창 · 소켓 부분(2 s 표 · 요약 줄은 다른 스크립트 — §6-3). 10-13 §1.2 의 '첫 손실 시각' 은 이 도구 + 임시 집계(원천 소실).
- **결함**: 소켓 누적값이 재시작으로 줄면 음수(`f2k1` 표의 `?(메타) -2214`). T ± 60 s 창이 사건을 포함하면 '앞' 값이 부풀음(§6-1).

### 9.10 `traj_size.py` = `Docs/tools/anal_traj_size.py` — 궤적 메시지 크기 (PC)
- **하는 일**: bag `/trajectories` 의 직렬화 크기를 10 s 칸으로, 첫 메시지의 마커 수 · ns 별 개수(12~13 행), 평균 MB/s = 총 바이트 ÷ (10 s × 칸 수).
- **출력**: `== bag_f2i1  메시지 1575 · 첫 메시지 마커 (832, Counter({'Candidate Trajectories': 800, 'Optimal Trajectory': 32}))` · `크기 kB 중앙 206 … → 평균 1.35 MB/s`(`f2i1_tf_cpu_traj.txt`), lite `(112, … 80 … 32)` · `28 kB … 0.26 MB/s`(`f2l1_net_anal.txt`). '받은' 양이라 포화 주행은 작게 나온다(§6-4).

### 9.11 `Docs/tools/anal_rtps_pcap.py` — 루프백 캡처를 종류 · 쓰는 쪽 · 받는 쪽으로 ★ (Jetson · PC, 표준 라이브러리만)
- **형태**: `anal_rtps_pcap.py CAP.pcap [--netlog net.log] [--onset HH:MM:SS] [--win 20] [--base HH:MM:SS,길이]`. f2m1 은 `jobs/anal_cap_f2m1.sh`(자동) → `anal_cap_f2m1b.sh`(평상 창 직접 지정).
- **왜**: 10-12 §20 '늘어난 5 만여 개/s 가 무엇이고 누가 보내나'.
- **하는 일**: pcap(링크 종류별 L2 길이) → IPv4 UDP 페이로드 → `RTPS` 머리 뒤 하위 메시지(`0x07` HEARTBEAT · `0x06` ACKNACK · `0x15` DATA · `0x16` DATA_FRAG · `0x12` NACK_FRAG …, 15~16 행)를 순서대로 읽음. 1 차: 2 s 칸 패킷 수, 포화 시작 = 중앙값 4 배를 넘는 칸이 3 칸 연속인 첫 칸(96~97 행, `--onset` 우선). 2 차: 평상 창(시작 전 `win` s, `--base` 로 대체) · 포화 창(시작 + 2 s 부터 `win` s)에서 종류별 수, 쓰는 쪽 = 보낸 참여자 GUID 앞 12 B + writer id(137~139 행), 읽는 쪽 ACKNACK = 보낸 참여자 → INFO_DST 참여자 + writer id. 토픽 이름은 캡처 전체의 탐색 DATA(`000003c2` · `000004c2`)에서 `PID_TOPIC_NAME`(0x0005) · `PID_ENDPOINT_GUID`(0x005a)를 꺼내 붙임(61~78 행). 프로세스 이름 = GUID 안 pid 하위 16 bit ↔ `--netlog` 의 `MAP` 줄 pid(112 · 117 행).
- **출력**: [`cap_f2m1_anal2.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_anal2.txt)(첫판 자동 창 `cap_f2m1_anal.txt`). **쓰인 곳**: H-재전송 판정(§3).
- **결함**: pid → 프로세스는 Fast DDS GUID 의 pid 추정(컨테이너 안은 '?'). `-s 512` 로 잘린 탐색 정보는 토픽 이름을 놓칠 수 있음. 합성 pcap 검증만 하고 실제 GUID 형식 검증은 이 캡처가 처음(10-13 TOOLS.md '？'). **지금**: 그대로 쓸 수 있음(캡처 권한 setcap 은 tcpdump 패키지 갱신 때 사라짐 — 10-13 §1.1).

### 9.12 `Docs/tools/anal_rtps_onset.py` — 포화 시작을 0.2 s 칸으로 ★
- **형태**: `anal_rtps_onset.py CAP.pcap HH:MM:SS 길이 [--step 0.2] [--netlog] [--topic rt/tf]` — f2m1 `anal_cap_f2m1c.sh`(10:19:38, 4 s), f2n1 `anal_cap_f2n1.sh`(`--step 10`, 250 s).
- **하는 일**: 탐색 정보로 `rt/tf` 의 쓰는 쪽 끝점(entity kind 0x02 · 0x03)을 모으고(29 행), 칸마다 그 끝점의 DATA · DATA_FRAG 수(보낸 참여자별), HEARTBEAT 수와 목적지, 그 끝점으로 간 ACKNACK 의 보낸 쪽 상위 3(39~41 행).
- **출력**: [`cap_f2m1_onset.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_onset.txt) · [`cap_f2n1_anal.txt`](../debug_log/2026-10-13/outputs/cap_f2n1_anal.txt). 11-03 발췌 캡처로 재현(§3).
- **결함**: HEARTBEAT 목적지가 '(모두)'(INFO_DST 없음)라 누가 방아쇠인지는 이것만으로 못 가림 → acklag 로 이어짐(10-13 TOOLS.md).

### 9.13 `Docs/tools/anal_rtps_acklag.py` — 뒤처진 읽는 쪽 ★ 기록기를 지목한 도구
- **형태**: `anal_rtps_acklag.py CAP.pcap HH:MM:SS 길이 [--netlog] [--topic rt/tf]` — f2m1 `anal_cap_f2m1d.sh`(10:19:27, 15 s).
- **하는 일**: 쓰는 쪽 HEARTBEAT 의 firstSN ~ lastSN(보관 범위, 37 행)과, 그 뒤 1 s 안 각 읽는 쪽 ACKNACK 의 bitmapBase(아직 못 받은 첫 번호, 39 행)를 맞춰 '뒤처짐 = lastSN − (bitmapBase − 1)' 을 큰 순으로(51~52 행). 0.25 s 안 HEARTBEAT 은 한 묶음, 14 묶음까지.
- **출력**: [`cap_f2m1_acklag.txt`](../debug_log/2026-10-13/outputs/cap_f2m1_acklag.txt).
- **결함**: ACKNACK 이 HEARTBEAT 보다 뒤 번호를 확인하면 음수가 `−-21` 처럼 찍힘(표시 결함, 판정엔 영향 없음). 14 묶음 뒤 생략이라 폭주 구간의 뒤처짐 추이는 잘림. 읽는 쪽 이름 'ros2' = 기록기는 pid · 수신량 정황.

### 9.14 `Docs/tools/fig_bag_reception.py` — 토픽 × 시간 수신 부족률 (10-13 §3.1, PC)
- **형태**: `fig_bag_reception.py 출력.png 기준이름 이름=bag폴더[|HH:MM:SS|설명] …`(기준 = f2n1).
- **하는 일**: 토픽마다 2 s 칸 수신 수 ÷ 기준 주행의 칸 중앙값 → 1 − 비율(34 행), 기준 1 Hz 미만 토픽은 뺌(30 행). `/tf` 메시지 간격의 칸별 최대(39~41 행). 끝에 주행 전체 '받은 비율'(54 행).
- **출력**: 그림 [`2026-10-13_bag_reception_f2m1_f2n1.png`](../04_navigation/figures/2026-10-13_bag_reception_f2m1_f2n1.png) + [`bag_reception.txt`](../debug_log/2026-10-13/outputs/bag_reception.txt)(`f2m1 … tf 23% … trajectories 41%` · `f2n1 … tf 100% … costmap 110%`).
- **결함**: 기준 주행의 중앙값보다 많이 받으면 100 % 를 넘음(`costmap 110%`). 발행 멈춤과 미수신 구분 불가(머리 주석).

### 9.15 `Docs/tools/anal_bag_rates.py` · `anal_recorder_cpu.py` — PF 5 대 15 (10-13 §3.2 · §3.3, PC)
- `anal_bag_rates.py 이름=bag[@시작초,길이초] …`: 토픽별 받은 수 ÷ 구간, 평균 크기, kB/s, 합계(25 · 37 · 40 행). 출력 [`bag_rates_pf.txt`](../debug_log/2026-10-13/outputs/bag_rates_pf.txt), 도착 간격 분포(`bag_gaps_pf.txt`)는 임시 집계.
- `anal_recorder_cpu.py [--bin 10] 이름=proc.log …`: `comm == ros2` 중 로그 전체에서 틱이 가장 많이 는 pid = 기록기(24 행), 10 s 칸 기록기 CPU · 전체 사용률(`ALL` 줄 idle + iowait) · 주요 노드(controller · ekf · 위치 추정 · nvblox · planner · bt). 출력 [`recorder_cpu.txt`](../debug_log/2026-10-13/outputs/recorder_cpu.txt).
- **결함**: `ncpu = round(dt / 초 / 100)` 이 표본 간격 흔들림으로 '코어 5 · 7 개' 를 찍음(6 코어). 평균이라 0.1 s 단위 순간 사건은 못 봄(10-13 §3.3 스스로 적음).

### 9.16 `job613_pathyaw.py --serve` · `job550_f0run.py` · `chk_pathyaw_serve.sh` — 상주 경로 조회기 (10-13 §4.2, Jetson)
- **왜**: 목표마다 `python3 job613` = 새 DDS 참여자 → 전환마다 탐색 급증(f2n1 2~14 s, 손실 177 ~ 1,004 /s). 별도 프로세스로 두는 이유(09-28 §20: 러너 노드 안에서 경로 조회 시 뒤이은 주행 요청 응답 없음)는 유지.
- **하는 일**: `--serve` 면 `READY` 뒤 표준입력 한 줄(`GX GY FALLBACK_RAD`)마다 경로 끝 방향 한 줄(`YAW …` / `FAIL …`). 러너는 주행 시작 때 1 번 띄우고(10-21 판 `:109`), 응답 20 s 없거나 죽으면 한 번 실행으로 되돌아감(`:74 ~ :82`).
- **검증**: `chk_pathyaw_serve.sh` 3 건 연속(`YAW −1.652505 151 0.315` …), 잔류 0. 주행 효과는 f2o1(§2).

### 9.17 prep 변형 · `fig_1012.py` · `chk_jetson_state.sh` (짧게)
- `job963_prep5.sh` · `job964_prep15.sh`(PF 값 지정) · `job966_prep_lean.sh`(그림자 · 궤적 끔) · `job969_prep_j.sh`(궤적 원래대로) · `job970_prep_lite.sh`(lite, launch 배포 · 빌드 포함) — 옛 방식 prep(약 5 분)에 구성만 바꾼 것. 빠른 prep(`job972` → `Docs/tools/prep_fast.sh` · `prep_patrol.sh`)과 지도 서버 `navmap_ensure` 는 [빠른 prep 카드](prep-fast-startup.md) 몫.
- `fig_1012.py`: 10-12 그림 4 장(§1 의 링크). 첫 판 부하 그림 어림값 정정(실수 ⑩).
- `Docs/tools/chk_jetson_state.sh`: 10-13 §0 가동 시간 · /tmp 스크립트 · `rmem_max 212,992` · 캡처 권한 확인.

## 10. 용어
- **포화(이 카드)**: 주행 도중 `/tf` 기록 수신이 10 s 평균 25 Hz 아래로 3 칸 이상 + follow_path 중단 ≥ 1(10-12 §4 선언). 그때 UDP 수신은 평상 약 5,300 → 6~8 만 datagram/s.
- **RTPS 하위 메시지**: DDS 의 전송 단위. DATA(표본) · DATA_FRAG(64 kB 넘는 표본 조각) · HEARTBEAT(쓰는 쪽: "내 보관함에 n ~ m 번이 있다, 확인하라") · ACKNACK(읽는 쪽: "k 번 앞까지 받았고 이것들이 빠졌다") · NACK_FRAG(조각 재요청) · GAP(더는 없는 번호).
- **reliable / best effort**: reliable 은 읽는 쪽이 확인할 때까지 쓰는 쪽이 보관 · 재전송한다. best effort 는 잃으면 그만. 한 토픽에서 읽는 쪽마다 따로 정해지고, 기록기는 `--qos-profile-overrides-path` 로 바꿀 수 있다.
- **보관함(history depth)**: 쓰는 쪽이 들고 있는 표본 수. `/tf` 는 100. 느린 reliable 읽는 쪽이 있으면 비워지지 않는다(10-13 §1.2 해석 — Fast DDS 의 정확한 동작은 미확인).
- **수신 버퍼(rmem) · `RcvbufErrors`**: 커널이 UDP 소켓마다 두는 받기 버퍼(여기 208 kB). 넘치면 버리고 `/proc/net/snmp` 의 `RcvbufErrors` · `/proc/net/udp` 의 drops 가 는다. DDS(UDP 전용)에서는 한 프로세스가 구독하는 모든 토픽이 소켓 한두 개로 들어온다.
- **탐색 폭주**: 새 DDS 참여자(프로세스 · `ros2` 명령)가 뜰 때 모든 참여자가 끝점 목록을 주고받아 짝수 포트(탐색 · 생존) 통신이 2~14 s 급증하는 것.
- **`mppi_viz`**: MPPI 후보 · 최적 궤적 `MarkerArray`(`/trajectories`) 발행. true = 후보 1000 중 20 개마다(50 궤적) × 시간 2 스텝마다(16 점) + 최적 32 = 마커 832(206 kB), lite = 100 개마다(10) × 4 스텝(8 점) + 32 = 112(28 kB).
- **그림자 EKF A**: rf2o 를 뺀 옛 구성(휠 + 자이로)을 같은 주행에서 나란히 계산해 `/odometry/ekf_a` 로만 내는 비교용 EKF(TF 안 냄).
