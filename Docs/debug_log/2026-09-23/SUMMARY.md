# 2026-09-23 — N6-2: CPU 회수(점군 끄기)·러너 수정·게이트 보강·슬라이스 높이 재검토 → N6 최종 판정

## 0. 시작 상태 (`outputs/j498_state.txt`)
- Jetson 08:56 재부팅됨, **ALOPS_ROBOTICS_5G 172.30.1.8** 에 붙음(WEB_DEV_5G 192.168.0.101 응답 없음 — 09-16 과 같은 양상). 러너는 `JETSON_HOST=172.30.1.8` 로(옛 alt 러너 + 새 러너의 `JETSON_HOST` 변수). `run_xfer_all.sh` 는 IP 가 박혀 있어 호스트 변수판 `run_xfer_all_h.sh` 로 대체(없는 파일은 건너뜀).
- 스택·컨테이너·`/tmp` 전부 없음, 포크 diff 보존. → **실제 재부팅 복구 시험(09-22 §4 남은 항목)**: 스크립트 재전송 → 컨테이너 `docker start` → prep(base → 보드 리셋 → 센서·SLAM·Nav2+nvblox 자동) 한 번으로 모드 N 게이트 J·K·L 통과하는지.

## 1. N6-2 계획·판정 기준(실행 전 선언)
1. **러너 재고정 수정**: `job125_avoid3.py` `REFIX_MAX` 0.30 → 0.06(게이트 D 허용과 동일). 기준 R1: 이후 회차에서 t≈1 s 의 '점프' 채택 0, ① 이 bag 횡변위 기반 여유(lat−0.165−0.01)와 ±2 cm 안.
2. **CPU 회수**: 모드 N 에서 realsense 점군 생성 끄기(`pointcloud.enable`/`pointcloud__neon_.enable` 런타임 false; 모드 S 는 true) → 릴레이 입력 0. 기준 C1: 정지 realsense CPU 14.6 → ≤ 10 %, 릴레이 ≤ 1 %, 깊이 15 Hz·nvblox 게이트 J 유지. C2: 주행 3 회 **CPU 합 < 320 %**(recorder 포함 문자 기준) 및 recorder 제외값 기록. 다른 지표는 BASELINE §4 유지.
3. **게이트 보강**(job505): M = 목표 부근(x 1.5~2.3, |y|<0.45) 전역 LETHAL 중 라이다·카메라 근거 없는 셀 0; N = 코스트맵 상자 셀 최대 y − 카메라 점군 상자 왼쪽 가장자리 ≥ −0.025(과소 마킹 ≤ 2.5 cm).
4. **슬라이스 최소 높이 0.03 vs 0.06 정지 측정**(통합 1.4 고정): 목표 부근 유령 셀 수·게이트 L 상자 셀 수·상자 왼쪽 가장자리 차. 기준 H1: 0.03 에서 유령 0(3 표본)이고 가장자리 차 ≤ 2.5 cm 면 0.03 채택, 아니면 0.06 유지.
5. **재부팅 복구**(§0): 기준 B1: 추가 손작업 없이(보드 리셋 제외) prep 뒤 J·K·L 통과.

### 0.1 Wi-Fi 끊김 4 번째 — 오늘은 다른 양상 (사용자 요청 "백그라운드 로그 확인"; `jobs/job529_wifi_collect.sh`·`job530_wifi_boot.sh` → `outputs/j529_wifi.txt`·`j530_wifi_boot.txt`, 원본 `/var/log/wifi_mon` 전체는 로컬 scratchpad `wifi_mon_0923/` 에 복사, git 제외)
- 어제 저녁까지 WEB_DEV_5G 정상(DHCP 갱신 16:37·17:37, 192.168.0.101). 오늘 08:56 부팅(NTP 전이라 로그 시각은 1970-01-01 09:00 = 부팅 기준).
- 부팅 후 3 분 동안 WEB_DEV_5G(b0:38:6c:37:1b:4c, 5180 MHz, −50~−54 dBm, PMF on)에 **연결 자체는 3 번 성공**(9:00:50, 9:01:41, 9:03:21 — 4-way 완료, NM "Connected") 했으나 **매번 DHCP 응답이 없어 45 s 뒤 `ip-config-unavailable` 로 실패** → 9:03:53 NM 이 스스로 끊고(reason 3 locally_generated) 다음 우선순위 ALOPS_ROBOTICS_5G(우선순위 5) 로 자동 전환 → 즉시 DHCP 성공 172.30.1.8. 이후 ALOPS 에서 안정(−52~−55 dBm, 9:45 까지 끊김 0).
- **이전 3 회(09-15·16·17)와 다르다**: 그때는 AP 가 먼저 deauth(reason 2)하고 PSK 재인증을 reason 23 으로 거부했다. 오늘은 인증은 되는데 **데이터 경로(DHCP)가 안 됐다** — AP 의 DHCP 서버/키 설치 문제 또는 공유기 측 일시 장애 후보. AP 비콘은 지금도 보이나(wifi-mon BEACON 5180 −51 dBm) NM 재스캔 목록엔 WEB_DEV_5G 가 안 보인다(숨김 SSID 이거나 NM 이 실패 AP 를 잠시 뺀 것 — 미확정). 공유기 로그는 무선 이벤트를 안 남기므로(09-18) DHCP 임대 표를 사용자가 UI 에서 확인하는 것이 유일한 공유기 측 근거.
- 오늘 영향: 재부팅 직후라 DDS 참가자 분리 문제는 없음(스택이 뜨기 전). 러너는 `JETSON_HOST=172.30.1.8` 로 진행. 옛 `run_xfer_all.sh` 는 IP 고정 → 호스트 변수판으로 대체.
- 판단·제안(사용자 결정): ① 4 번 중 4 번 모두 WEB_DEV_5G 쪽 원인(AP deauth 3, DHCP 무응답 1)이고 ALOPS 는 한 번도 끊긴 적 없음 → **기본을 ALOPS 로**(우선순위 교체, WEB_DEV 는 예비) 하면 IP 가 172.30.1.8 로 고정돼 운용이 단순해진다(PC 와 같은 서브넷). ② 그대로 두려면 러너에 "두 IP 핑 → 응답하는 쪽 자동 선택" 을 넣어 손작업을 없앤다(오늘 적용 가능). ③ 공유기 DHCP 임대 표에서 08:57~09:03 의 58:02:05:bd:d5:35 요청 흔적 확인.

## 2. 재부팅 복구 B1 (`outputs/j510_prep_a.txt`·`j531_b1_c1.txt`)
- 스크립트 재전송(`run_xfer_all_h.sh` 24 개 + 09-21 세트 13 개) → 컨테이너 `docker start`(nvblox 패키지 8 보존) → `run_mp9prep.sh`(base 기동 → 사용자 보드 리셋 → 센서·SLAM·Nav2+nvblox) 한 번으로: 게이트 A~D 통과(상자 1.147/−0.051, 창 0.235, 목표 여유 0.324, 배터리 **12.35 V**), **J·K·L·M 통과**(nvblox 15.1/9.5 Hz·0.103 s, plugins nvblox, 상자 셀 10, 목표 부근 유령 0). → **B1 통과**: 재부팅 뒤 손작업은 보드 리셋뿐(IP 변경은 별건).
- 새 게이트 N 은 파서 결함으로 판정 불가("코스트맵 상자 최대 y ?" — job315 표준 출력 형식이 prep 의 파서와 달라 값이 비었음) → 수정 뒤 재검사(§2.1). M 은 정상 동작.
- C1 첫 시도: `pointcloud.enable` 은 이 realsense-ros(neon 필터)에 선언돼 있지 않음 → 실제 파라미터 `pointcloud__neon_.enable`(True) 로 재시험(§3).

## 3. C1 점군 생성 끄기 정지 A/B (`jobs/job531_pcl_toggle.sh` → `outputs/j531c_pcl.txt`; 1·2 차 시도 `j531b` 는 파라미터 이름 오류)
- realsense-ros(neon 필터판)의 실제 파라미터는 `pointcloud__neon_.enable`(`pointcloud.enable` 은 미선언). 런타임 false → 점군 토픽·릴레이 출력 0 Hz, 깊이 15 Hz·nvblox 깊이 콜백 15.1 Hz 유지(파이프라인 재시작 없음) → true 로 즉시 복구.
- 정지 CPU(top 20 s): realsense **15.3 → 13.9 %**(−1.4), depth_relay **3.7 → 0**(구독자 없어도 수신·역직렬화하던 몫 소멸), 전체 합 201 → 195 %(−6 %p). 기대(−10 %p)보다 작다 — realsense 노드의 비용은 점군보다 USB 수신·복호가 대부분(추정). 주행 CPU 320~325 → **≈315~319 로 <320 경계에 걸릴 것**(측정 전).
- 적용 방식: 모드 N 이면 launch 뒤 `pointcloud__neon_.enable false`, 모드 S 면 true — `navigation.launch.py` 의 camera_layer 에 연동(ExecuteProcess 로 param set). 주행 3 회로 C2 판정.

## 4. H1 슬라이스 최소 높이 0.03 vs 0.06 정지 측정 (`jobs/job532_slice_h.sh` → `outputs/j532_slice_h.txt`, 통합 1.4 고정, 배치 1.147/−0.051)
| | 0.06(현재) 3 표본 | 0.03 3 표본 |
|---|---|---|
| 게이트 L 상자 셀/프레임 | 10·11·11 | 11·10·10 |
| 목표 부근 슬라이스 ≤0 / 전역 LETHAL | 0/0 · 0/0 · 0/0 | 0/2 · 1/3 · 1/3 |
| 카메라 상자 y 구간 | −0.14~+0.04 | −0.12~+0.06 |
- **판정: 0.06 유지**(H1 불합격 — 0.03 은 통합 1.4 m 안에서도 목표 부근 유령 셀이 돌아옴(2~3 셀), 상자 커버는 두 값이 같음). 09-22 의 "0.03 복귀 가능" 추정은 기각. 코스트맵 상자 최대 y 는 job315 호출 방식 문제로 이번에도 비어 있음 → §2.1 에서 게이트 N 과 함께 정리.

## 5. 네트워크: 고정 IP(공유기 DHCP 예약) 방식으로 WEB_DEV_5G 복귀 + IP 충돌 감지 (사용자 지시 10:1x; `jobs/job535_net_fixed.sh`·`run_j535.sh` → `outputs/j535_net.txt`, 사전 확인 `j534_netprep.txt`)
- 사용자 답변에 대한 판단(§0.1 보강): "다른 IP 의 대량 트래픽이 내 IP 를 끊는다" 는 기전은 오늘 로그(인증 성공·DHCP 무응답)와 이전 3 회(AP deauth·PSK 거부)에 맞지 않는다. "IP 가 끊긴다" 에 가장 가까운 실제 기전은 **IP 충돌**(같은 IP 가 다른 기기에 할당·사용)이며 09-03 의 "링크 유지·핑 100 % 손실" 과는 맞을 수 있다 — 가설, 미측정. 사용자 결정: 공유기에서 Jetson MAC 에 고정 할당(예약)하고 DHCP 를 그대로 쓴다.
- 적용(sudo, 사용자 지시): ① `iputils-arping`·`tcpdump` 설치, ② NM 두 프로파일 `ipv4.dad-timeout 3000`(주소 설정 전 3 s ARP 중복 검사 — 충돌이면 활성화 실패 + "duplicate address" 로그), ③ `wifi_mon.sh` 15 s 루프에 `arping -D`(중복 주소 탐지) 추가 → 다른 MAC 이 응답하면 `mon.log` 에 `ARP_DUP ip=… <MAC>` + 5 분당 1 회 스냅샷(`outputs/../jobs/job535_net_fixed.sh` 의 패치 본문), ④ `nmcli con up WEB_DEV_5G`.
- 결과: 10:14:33 연결 → **10:14:35 DHCP 임대 192.168.0.101(2 s)** → 활성. 아침(08:57~09:03)의 DHCP 무응답 3 회는 재현되지 않음(원인 미확정 — 부팅 직후 공유기/AP 측 일시 상태로 추정). PC 핑 4 s 만에 응답.
- 후속: IP 변경으로 이미 뜬 DDS 참가자가 갈리므로 전체 정지(에이전트 포함) → prep → **보드 리셋** 필요(§6). 러너 `run_jx.sh` 는 두 IP 를 핑해 자동 선택.
