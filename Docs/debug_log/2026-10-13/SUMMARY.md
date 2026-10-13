# 2026-10-13 — 포화 패킷 캡처 → DDS 공유메모리 도입

전날 기록: `Docs/debug_log/2026-10-12/SUMMARY.md` §9·§11(포화 = UDP 통신량 10 배), §17·§22(결정: 캡처 1 회 뒤 공유메모리 도입). 도구 색인 `TOOLS.md`(오늘부터 작업하면서 채움), 상시 도구 `Docs/tools/`.

## §0 시작 상태(사용자: "재부팅됐다")
- `Docs/tools/chk_jetson_state.sh`: Jetson 192.168.0.101, 가동 33 분, /tmp 스크립트 0 개(재부팅으로 소실), 에이전트 컨테이너 1 개, 설치본 PreferForward 15.0, rmem_max 212,992.
- tcpdump 는 설치돼 있으나 캡처 권한 없음(setcap 없음, 암호 없는 sudo 불가) → **캡처는 사용자 조치가 필요**(방식 A: 주행 직전 sudo tcpdump 직접 실행 / 방식 B: setcap 한 번).
- 도구 규약 적용: 상시 도구를 용도 이름으로 `Docs/tools/` 에 모음(대응표 `Docs/tools/README.md`). 새 도구 `anal_rtps_pcap.py`(루프백 캡처 분석 — 합성 pcap 으로 동작 확인: 평상 DATA 100 /s → 포화 HEARTBEAT·ACKNACK 각 500 /s 를 종류·토픽·프로세스별로 맞게 집계).
- 주행 래퍼 `job551_f0drive.sh` 에 `CAP_PCAP=1` 추가: tcpdump 에 권한이 있으면 주행 구간을 자동 캡처(`/tmp/cap_<이름>.pcap`, 앞 512 B), 없으면 안내만.

## §1 f2m1 포화 재현 + 패킷 캡처 — 선언(주행 전)
- 목적: 포화 때 늘어나는 초당 5 만여 개 패킷의 **종류와 보낸 쪽**을 확인한다(10-12 §20·§21 의 미확인 부분). 공유메모리 도입 전 마지막 관찰.
- 구성: 10-12 에 6/6 포화한 구성 — 그림자 EKF 끔 + **MPPI 궤적 발행 원래대로(`mppi_viz:=true`, 206 kB × 10 Hz)** + PreferForward 15 + 전역 nvblox + 재계획 0.5 Hz. prep `Docs/tools/prep_patrol.sh true`. 코스 b910, 상자 ①·② 제자리.
- 계측: 루프백 UDP 캡처(앞 512 B) + 기존 UDP 손실 2 s 기록 + bag. 분석 `anal_rtps_pcap.py`(평상 창 = 포화 시작 전 20 s, 포화 창 = 시작 뒤 20 s).
- 판정(포화 창의 하위 메시지 개수 기준):
  - **H-재전송**: HEARTBEAT + ACKNACK + NACK_FRAG + GAP(전송 확인·재전송 요청 계열)가 과반이고 평상 대비 10 배 이상 → 신뢰성 전송의 되먹임.
  - **H-데이터**: DATA + DATA_FRAG 가 과반이고 특정 쓰는 쪽(토픽)이 그 절반 이상 → 그 발행자가 원인(재전송된 데이터인지는 같은 writer 의 평상 대비 증가율로 본다).
  - **H-탐색**: 탐색·생존 신호 끝점이 과반 → 참여자 탐색 폭주.
  - 어느 것도 과반이 아니면 상위 5 개 흐름을 그대로 보고하고 해석은 보류한다.
- 포화가 안 생기면: 캡처는 평상 기준선으로만 쓰고 한 번 더 주행한다.
- 주의: 재현 주행이라 목표 2~3 에서 중단될 가능성이 높다(10-12 에 6 번 중 4 번 중단).

### §1.1 캡처 권한·prep(사용자: 방식 B — `sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump` 실행, 로버 출발 위치) — 로버 안 움직임
- 권한 확인: `/usr/bin/tcpdump cap_net_admin,cap_net_raw=eip`. 되돌리기는 `sudo setcap -r /usr/bin/tcpdump`(tcpdump 는 Ubuntu 패키지 프로그램이다. 이 권한은 그 파일에만 붙고, 패키지가 갱신되면 사라진다).
- prep(`Docs/tools/prep_patrol.sh true 15.0`, 10:06:00~10:07:04 = **64 s**, `outputs/prep_f2m1.txt`): PREP_OK.
  - Nav2 5 개 active, /wheel_odom 24.7 · /odometry/filtered 29.3 · /tf 50.3 Hz, 배터리 12.35 V.
  - 전역 코스트맵 333×242, plugins static · nvblox_layer · obstacle · inflation, nvblox 프레임 map.
  - PreferForward 15.0, **visualize True · trajectory_step 20 · time_step 2**(원래 발행량), 정체 감시 관찰 모드.
  - `navmap_ensure` 는 2 번째 확인에서 active(이번에도 처음엔 미설정이었던 것으로 보임), "no map received" 0, SHM 오류 0.
- 눈에 띄는 점: 시작 위치가 map→base **(0.010, 0.099)** — 옆으로 약 10 cm(10-12 의 prep 들은 1 cm 안). 목표는 지도 절대 좌표라 주행에는 문제없으나 시작 조건 차이로 기록한다(로버가 테이프에서 옆으로 놓였거나 위치 추정이 그만큼 맞춘 것 — 구분 안 함).

### §1.2 f2m1 결과 — 포화 재현됨, 정체는 `/tf` 의 HEARTBEAT 폭주, 가장 먼저 뒤처진 읽는 쪽은 기록기
주행(10:19:26, viz true + PreferForward 15 + 그림자 EKF 끔, `outputs/run_f2m1.txt`): 목표 1 SUCCEEDED 65.0 s, 목표 2 **ABORTED** 80.3 s(도착 (5.345, −2.128), 목표 대비 0.171 m). 목표 3 은 가지 않음. 캡처 `/tmp/cap_f2m1.pcap` 1.24 GB(Jetson 에만 있음, 재부팅하면 사라진다).

**측정 1 — 무엇이 늘었나**(`anal_rtps_pcap.py`, `outputs/cap_f2m1_anal2.txt`)

| | 평상(10:19:36 부터 4 s) | 포화(10:19:40 부터 20 s) |
|---|---|---|
| RTPS 패킷 | 4,794 /s | 56,350 /s (11.8 배) |
| DATA | 3,745 (77 %) | 8,024 (14 %) |
| HEARTBEAT | 450 (9 %) | **44,739 (79 %)** |
| ACKNACK | 594 (12 %) | 3,588 (6 %) |
| DATA_FRAG / NACK_FRAG | 103 / 0 | 101 / 0 |

- HEARTBEAT 의 거의 전부가 `rt/tf` 를 쓰는 두 곳에서 나온다: slam_toolbox 23,283 /s, ekf_node 20,780 /s.
- `/tf` DATA 도 늘었다: ekf 300 → 2,307 /s, slam 200 → 2,514 /s(발행 주기는 그대로이므로 늘어난 것은 재전송 또는 읽는 쪽별 개별 전송 — 둘을 구분하진 못했다).
- 다른 토픽의 DATA 는 그대로이고, 큰 메시지 조각(DATA_FRAG)과 조각 재요청(NACK_FRAG)은 늘지 않았다. 탐색 포트 통신도 늘지 않았다.

**판정(§1 선언 기준)**: HEARTBEAT + ACKNACK = 85 % > 50 % → **H-재전송(신뢰성 프로토콜의 확인 신호) 성립.** H-데이터(DATA 가 과반)·H-탐색(탐색 포트가 과반)은 기각.

**측정 2 — 시작 순간**(`anal_rtps_onset.py`, 0.2 s 칸, `outputs/cap_f2m1_onset.txt`)
- 10:19:40.5 까지: ekf `/tf` DATA 60 /칸, slam 40 /칸, HEARTBEAT 0.
- 10:19:40.7: ekf DATA 451, HEARTBEAT 3,920. 다음 칸(41.0)에 slam 도 따라옴(DATA 487), HEARTBEAT 11,355.
- 한 칸(0.2 s) 안에 평상 → 폭주. 서서히 느는 것이 아니다.

**측정 3 — 누가 뒤처졌나**(`anal_rtps_acklag.py`, `outputs/cap_f2m1_acklag.txt`: 쓰는 쪽의 HEARTBEAT(보관 번호 범위)와 읽는 쪽 ACKNACK(받은 번호)을 맞춤)
- 평상(10:19:31.9~37.9): 읽는 쪽 12 곳 모두 최신 번호까지 확인(뒤처짐 0), HEARTBEAT 은 3 s 에 한 번.
- 10:19:40.91(ekf 의 `/tf`): 프로세스 `ros2`(pid 65844) 혼자 **70 개 뒤처짐**, 이후 0.25 s 마다 77 → 83 → 92 로 벌어짐. 같은 시각 나머지 11 곳은 뒤처짐 없음(bt_navigator 가 1~5 개 누락 범위를 표시한 정도).
- slam 의 `/tf` 도 같다: 10:19:41.00 에 `ros2` 가 53 → 59 → 64 → 68 개 뒤처짐.
- `ros2`(65844)는 주행 시작 때 뜬 유일한 `ros2` 명령 = **bag 기록기**(`ros2 bag record`)로 판단한다. 근거: 스택 프로세스는 pid 21xxx, 이것만 65844, 받는 패킷이 다른 곳의 2 배(9,209 /s). 명령줄을 직접 확인한 것은 아니다.
- 소켓 손실 기록(`outputs/net_f2m1.log`, 2 s 간격, `anal_udp_drops.py`)도 같은 순서다: 기록기 소켓(port 7439)이 10:19:42 에 첫 손실(408), 나머지(behavior·bt·controller·ekf·slam)는 10:19:44, planner·smoother 는 10:19:48. 포화 60 s 평균 손실은 기록기 767 /s 가 1 위(bt_navigator 291, ekf 178).
- 덧붙임: 기록 시작 직후(10:19:28~31)에도 `/tf` 보관함이 100 개(=QoS depth)까지 차고 `ros2` 가 47 개 뒤처진 구간이 있었으나 3 s 만에 풀렸다. 즉 "한 읽는 쪽이 뒤처짐" 자체는 회복될 수 있고, 10:19:40 에는 회복되지 않았다.

**해석(추정 — 측정 아님)**
1. 기록기는 모든 토픽을 소켓 하나(수신 버퍼 208 kB)로 받는다. 여기에 MPPI 궤적 206 kB × 10 Hz 가 들어오면 버퍼가 넘치고, 같은 소켓으로 오던 `/tf` 가 함께 버려진다 → 기록기가 `/tf` 를 못 받았다고 알림 → 쓰는 쪽이 재전송 + HEARTBEAT.
2. `/tf` 는 신뢰성(reliable) + 보관 100 개. 한 읽는 쪽이 확인을 못 하면 보관함이 비워지지 않고, Fast DDS 는 그 상태에서 발행할 때마다 HEARTBEAT 을 읽는 쪽 전부(12 곳)에 보내는 것으로 보인다(50 Hz × 12 곳 × 반복 → 수만 /s). 이 통신량이 다른 프로세스의 소켓도 넘치게 해(2~4 s 뒤 손실 시작) 스스로 유지되는 고리가 된다.
3. 이 해석은 10-12 의 관찰과 맞는다: lite(28 kB)·끔에서는 포화 없음, 기록기의 궤적 구독만 best effort 로 바꾼 f2k1 은 여전히 포화(소켓으로 들어오는 양은 그대로이므로).
4. **설명 못 하는 것**: ① PreferForward 5 + viz true 에서는 왜 안 생기나(0/3). ② 평상 구간에도 궤적은 발행되고 있었는데(DATA_FRAG 103 /s) 왜 10:19:40.7 인가 — 그 순간의 계기는 모른다. ③ 2 번의 Fast DDS 동작은 소스·문서로 확인하지 않았다.
5. 우연일 수 있는 일치: 러너의 소켓 손실 기록 루프가 시작 15 s 뒤(=10:19:40)에 `netmap`(/proc/*/fd 훑기)을 한 번 돌린다. 포화 시작과 1 s 안에서 겹친다. 다만 10-12 의 포화 6 회 중 f2f1~f2g 는 이 기록 루프가 없던 때라 원인일 수는 없고, 이번 주행의 방아쇠였는지는 구분 못 한다.

**공유메모리 도입에 주는 뜻**
- 공유메모리로 가면 같은 기기 안의 통신은 UDP 소켓 버퍼를 지나지 않는다 → 해석 1 의 "소켓 넘침으로 `/tf` 가 버려짐"이 없어진다(추정). 방향은 유지할 근거가 된다.
- 그러나 "느린 읽는 쪽 하나가 신뢰성 토픽의 쓰는 쪽을 붙잡는" 구조는 전송 방식과 무관하다. 공유메모리에서도 기록기가 느리면 `/tf` 쓰는 쪽 보관함은 찬다. 그래서 도입 뒤 검증은 "포화가 안 생겼다"만이 아니라 **`/tf` HEARTBEAT 수와 읽는 쪽 뒤처짐**으로 봐야 한다(공유메모리 구간은 tcpdump 에 안 보이므로 Fast DDS 통계 또는 `/tf` 수신율로 대체 — 방법은 §2 에서 정한다).
- 공유메모리와 별개로 값싼 대책 후보(시험 안 함): 기록기가 `/tf` 를 best effort 로 구독(러너의 QoS override 한 줄) — 느린 읽는 쪽이 쓰는 쪽을 붙잡는 고리를 끊는다.
