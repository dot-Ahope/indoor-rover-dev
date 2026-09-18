# 2026-09-18 — Wi-Fi(WEB_DEV_5G) 차단 원인 확인: 공유기 로그·설정 조사

전날 기록: `../2026-09-17/SUMMARY.md` §17(Jetson 쪽 분석). 사용자 결정: **WEB_DEV_5G 유지**, 로그로 차단 원인을 확인한다.

## 0. 상태
- Jetson 은 사용자가 아침에 재부팅(10:15:47 부팅) → **WEB_DEV_5G 192.168.0.101 에 정상 접속**(−50 dBm, RX 702 / TX 526.6 Mbit/s VHT 80 MHz 2×2, power_save off). 09-17 13:38 부터 이어지던 거부는 늦어도 이 시각에는 풀렸다(차단 지속 < ≈20 h).
- 재부팅 직후 syslog 줄은 NTP 전 시각(예: 오늘 부팅이 `Sep 17 16:37:22` 로 찍힘)이라 날짜 필터에 주의.

## 1. 공유기 식별 (로그인 없이)
- BSSID OUI b0:38:6c → **EFM Networks(ipTIME)**. `http://192.168.0.1/` → `login/login.cgi`, 관리 화면 제목 **AX3000R**, 펌웨어 **15.03.0**.
- PC(172.30.1.89)에서 이중 NAT(ALOPS 공유기 172.30.1.254, WAN 192.168.0.6) 너머로 관리 화면에 닿는다.

## 2. 공유기 로그 (사용자가 Chrome 에서 직접 로그인, Claude 는 읽기만)
- 관리 UI 는 Flutter 캔버스라 DOM 텍스트가 없다 → 화면이 쓰는 JSON-RPC `POST /cgi/service.cgi {"method":"syslog/show","params":{"id":N,"lang":"kr"}}` 를 같은 세션으로 조회(id 0 = 전체). 설정 변경 호출 없음.
- **시스템 로그 1,452 건(2025-08-18 ~ 2026-09-17 14:30)의 종류 전부**:
  | 종류 | 건수 |
  |---|---|
  | DHCP 할당 "IP … 을(를) MAC 이(가) 할당 받았습니다" | 1,008 |
  | 유선 LAN 포트 연결 끊김 / 연결됨 | 139 / 150 |
  | DDNS 접속·등록 | 96 |
  | WAN 링크 재연결·DHCP·대여시간 초과·서버 무응답 | 51 |
  | 시스템 재시작 | 4 |
  | 관리자 LOGIN 성공 | 3 |
  | 기타(DDNS 실패, WAN 대역 충돌) | 2 |
- **무선 접속·인증·차단·DFS 이벤트는 이 기종이 기록하지 않는다.** 09-14 이후 기록은 다른 기기(1E:DD:9A:94:E6:AD)의 DHCP 2 건(09-17 09:52, 14:30)뿐 — 세 번의 끊김 시각(09-15 14:03:13, 09-16 15:57:34, 09-17 13:38:42) 근처에 WAN/LAN/재시작 사건도 없다.
- Jetson MAC 58:02:05:BD:D5:35 의 기록은 DHCP 할당 16 건(2025-08-18 ~ 2026-09-02)뿐.
- → **공유기 로그로는 차단 원인을 확정할 수 없다.**

## 3. 공유기 무선 설정 (조회 전용 API: `wireless/info`, `wireless/band/info|show`, `wireless/bss/info|show`, `wireless/mac/show`, `easymesh/info`; 비밀번호 필드는 가림)
| 항목 | 값 | 차단 원인 가능성 |
|---|---|---|
| 시스템 가동 시간 | 254 일 22 시간 (인터넷 연결 33 일) | 공유기 재부팅 아님 |
| 5 GHz BSS `WEB_DEV_5G` | wlan0, WPA2-PSK AES, 접근 all, maxsta 0(무제한) | 접속 수 제한 없음 |
| MAC 필터 (2g.1/2g.2/5g.1) | 모두 off | 필터 차단 아님 |
| Easy Mesh | active false | 메시 스티어링 아님 |
| 5 GHz 채널 | **36, 160 MHz (중심 50 = 채널 36~64, DFS 52~64 포함)**, dfs_status normal, country KR, 11ax, 출력 100 % | **DFS 레이더 감지 시 AP 가 채널/폭을 비워야 함** — 후보 |
| 비콘(Jetson 캐시) | VHT seg1 42 / seg2 50 (=160 MHz), RSN **MFP-capable**(PMF 선택), Country KR | **PMF + 제조사 외부 드라이버(rtl88x2ce)** 재인증 문제 — 후보 |
| 2.4 GHz | WEB_DEV(ch1, 40 MHz), WEB_DEV_2G(VAP) | 무관 |

## 4. Jetson 로그 재확인 (`jobs/job428_wifi_dfs.sh` 등 → `outputs/j428*.txt`)
- **정정**: 09-17 §17 에서 단서로 본 재결합 때의 `CTRL-EVENT-STARTED-CHANNEL-SWITCH … ch_width=80 MHz cf1=5210` 은 **모든 접속마다 드라이버가 내는 줄**(WEB_DEV 42 회, ALOPS 15 회)이다 — AP 가 160→80 으로 내려갔다는 증거가 아니다(Jetson 칩이 80 MHz 까지라 자기 폭을 보고).
- 세 번의 AP 끊김(reason 2) 직전에 채널 전환 알림(CSA)·비콘 손실·규제 변경 줄이 없다.
- PMF 협상 여부·핸드셰이크 세부는 sudo 없이는 볼 수 없다(wpa_cli 제어 소켓 권한 거부, 이 드라이버는 `iw station dump` 미지원). NM 프로파일은 `pmf 0 (default)` = 전역 기본(보통 '선택').

## 5. 판단
- **확정된 것(배제)**: 공유기 재부팅, MAC 필터, 접속 수 제한, Easy Mesh, WAN 장애, Jetson 드라이버 오류·약신호·트래픽·SSH 빈도(09-17 §17.3).
- **남은 후보(미확정)**:
  1. **DFS**: 160 MHz 가 DFS 채널 52~64 를 포함 → 레이더(또는 오감지) 시 AP 가 그 채널을 비워야 하고, 일부 펌웨어는 CSA 없이 무선부를 재구성해 단말을 끊는다 — **끊김(reason 2)** 을 설명할 수 있다. 하지만 이후 수 분~수 시간 이어진 **재인증 거부**는 설명하지 못한다.
  2. **PMF(802.11w) + rtl88x2ce 외부 드라이버**: 끊긴 뒤 AP 가 옛 보안 연관을 쥐고 있거나 드라이버가 보호 관리 프레임을 잘못 처리하면 4-way handshake 가 실패한다 — **재인증 거부**를 설명할 수 있다. 하지만 **첫 끊김**의 원인은 아니다.
  3. AP 펌웨어(15.03.0) 결함.
  → 두 현상(끊김·재인증 거부)이 서로 다른 원인일 수 있다. 세 사건만으로는 가를 수 없다.

## 6. 확정 방법 (모두 설정 변경 또는 sudo — 사용자 결정 필요)
| 안 | 내용 | 가르는 것 | 대가 |
|---|---|---|---|
| A. 다음 발생 계측(권장, 망 변경 없음) | Jetson: wpa_supplicant 로그 수준 debug(sudo) + 10~30 s 마다 AP 비콘 폭(160/80)·신호·링크 기록 백그라운드 | 다음 끊김 때 **폭이 160→80 으로 바뀌었는지(DFS)**, 핸드셰이크 어느 단계에서 **PMF/SA Query** 로 막혔는지 | syslog 증가, 하루 1 회 빈도라 며칠 걸릴 수 있음 |
| B. 공유기 5 GHz 폭 80 MHz(36~48, DFS 없음) | ipTIME 설정 변경 | 며칠간 끊김이 사라지면 DFS | 사무실 공유 공유기 — 다른 사용자 속도 저하, 관리자 동의 필요 |
| C. Jetson WEB_DEV_5G 프로파일 PMF 끄기(`pmf 1`) | NM 설정(sudo) | 끊겨도 즉시 재접속되면 PMF 가 재인증 거부 원인 | 보안 약간 낮아짐(WPA2-PSK 그대로) |
| D. 운영 대책(원인과 별개) | ALOPS 자동 연결 끄기 + WEB_DEV_5G 재시도 감시(root 타이머) | — | 끊김 동안 원격 접속 불가, 대신 **IP 가 바뀌지 않아 DDS 분리 없음**. NM 은 `no-secrets` 로 포기하면 스스로 재시도하지 않으므로 감시가 필요 |

## 7. A안 설치 — 다음 끊김 계측 (사용자 승인, sudo 사용, 네트워크 설정 변경 없음)
### 7.1 사전 점검 (`jobs/job429_probe.sh`, `job429b_montest.sh`, `job429c_dbgrate.sh` → `outputs/j429*.txt`)
- **PMF 협상 확인**: root `wpa_cli status` → `key_mgmt=WPA2-PSK`, **`pmf=1`**, `mgmt_group_cipher=BIP`. 즉 Jetson–WEB_DEV_5G 는 802.11w 보호 관리 프레임 상태(§5 후보 2 의 전제가 성립).
- 디스크 193 GB 여유. `/var/log/syslog` 는 `logrotate.timer` 가 inactive 라 회전되지 않는다(144 MB, 2 월부터) — 별도 과제.
- `wpa_cli` 모니터(level 2)는 파이프 입력에서 메시지를 받지 못함(버퍼 끔도 동일) → 기각. 대신 wpa_supplicant 전역 `log_level DEBUG`: 유휴 60 s 에 79 줄·8 KiB(≈11 MiB/일). 시험 뒤 INFO 로 복귀 확인.
- AP 채널만 스캔(`iw scan freq 5180`) 136 ms. 비콘 = VHT 폭 1, seg1 42, seg2 50(**160 MHz**), CSA 없음. 비콘의 WPS 장치명은 "ipTIME BE3600QCA"(관리 화면은 AX3000R — 내부 칩셋 이름으로 추정).

### 7.2 설치물 (`jobs/wifi_mon.sh`, `jobs/job429d_install.sh`, `jobs/job429h_redeploy.sh`)
| 파일 | 역할 |
|---|---|
| `/etc/rsyslog.d/25-wifi-mon.conf` | wpa_supplicant **severity 7(DEBUG) 줄만** `/var/log/wifi_mon/wpa_debug.log` 로, syslog 에는 넣지 않음. INFO 이상(CTRL-EVENT-*)은 기존대로 syslog. `rsyslogd -N1` 검사 통과 |
| `/usr/local/sbin/wifi_mon.sh` + `wifi-mon.service`(enabled, Restart=always) | 15 s: 링크·신호·비트레이트·IP·`wpa_state/pmf/key_mgmt` → `mon.log` LINK. 60 s(WEB_DEV 연결 중): AP 채널 스캔 → BEACON(폭·seg1/2·CSA·Quiet). ALOPS 등 다른 AP 일 때 10 분마다 전체 스캔 BEACON_ALL(WEB_DEV_5G 보이는지·폭). **BSSID 가 바뀌거나 끊기면** EVENT + `event_*.txt` 스냅샷(iw link, wpa 상태, nmcli, 전체 스캔 AP 블록, 직전 debug 400 줄, syslog 80 줄). wpa_supplicant 재시작·재부팅 뒤 DEBUG 자동 재설정. mon 50 MB·debug 300 MB 넘으면 1 회 회전 |
- 첫 기동 때 첫 비콘 스캔이 98 s 막힘(다른 스캔과 겹침 추정, 이후 매분 1 s 이내) → 스캔에 `timeout`(단일 10 s·전체 20 s) 추가 후 재배포.
- 검증: 서비스 active/enabled, 로그 수준 DEBUG, LINK 15 s·BEACON 60 s 정상(`vht_w=1 seg1=42 seg2=50 csa=0`), syslog 로 DEBUG 줄 새지 않음, 스냅샷 함수 수동 시험(`test_event_20260918_110443.txt`, 41 KB, 전 항목 기록, 비밀 값 없음 — "password" 단어는 WPS `Device Password ID` 뿐).
- **되돌리기**: `sudo systemctl disable --now wifi-mon; sudo rm /etc/rsyslog.d/25-wifi-mon.conf; sudo systemctl restart rsyslog; sudo wpa_cli log_level INFO` (+ `/usr/local/sbin/wifi_mon.sh`, `/etc/systemd/system/wifi-mon.service`, `/var/log/wifi_mon/` 삭제).

### 7.3 다음 끊김 때 판정 기준 (미리 선언)
| 관측 | 판정 |
|---|---|
| 끊김 직전 BEACON 에서 seg2 50 → 0/없음(160→80) 또는 CSA=1, 혹은 끊김 뒤 BEACON_ALL 에서 폭이 줄어 있음 | **DFS**(레이더로 52~64 비움)가 끊김의 원인 |
| 끊김 직전 BEACON 폭 그대로·CSA 0 | DFS 아님 → 공유기 쪽 다른 원인 |
| 재접속 시도의 debug 에 msg 1/4 수신·2/4 송신 후 AP deauth(reason 23), SA Query/"Association comeback" 또는 PMF 관련 줄 | **PMF 상태 불일치**가 재인증 거부의 원인 쪽 |
| msg 1/4 자체가 오지 않음 | AP 가 인증 단계 진입 전에 거부 — 공유기 측 거부 목록/상태 |
- 빈도가 하루 1 회 안팎이라 결과는 며칠 걸릴 수 있다. 끊김이 나면 NM 이 ALOPS(172.30.1.8)로 넘어가므로 그쪽 주소로 접속해 `/var/log/wifi_mon/` 을 회수한다.

## 8. 로그·산출물 누적 조사 (사용자 요청, 읽기 전용 — 삭제 없음)
도구: `jobs/job430_disk.sh`, `job430b_logs.sh`, `job430c_talkers.sh`(Jetson) → `outputs/j430*.txt`, PC 쪽은 Git Bash `du`/`git count-objects`.

### 8.1 Jetson (디스크 233 GB 중 28 GB 사용, 193 GB 여유 — 공간 문제 없음)
| 항목 | 크기 | 상태 |
|---|---|---|
| **`/var/log/syslog`** | 144.6 MB (2 월 20 일부터 한 파일) | **logrotate 패키지 미설치**(`dpkg: un`, 바이너리·cron·timer·status 모두 없음) → `/etc/logrotate.d/rsyslog`(주 1 회·4 개·압축) 설정이 있어도 한 번도 실행 안 됨. kern.log 12.7 MB·auth.log 3.5 MB 도 같음 |
| syslog 증가율 | 09-07~09-15 **7~10 MB/일** → 09-16 2.2 · 09-17 1.2 MB/일 | 감소 = 09-16 mavlink-router(크래시 루프, 3 s 마다 재시작) 비활성화. 현재 주 발생원(09-17): iio-sensor-proxy "iio:device busy" 1,696 줄(카메라 IMU 를 데스크톱 화면회전 서비스가 열려다 실패), SSH 세션 시작/종료 ≈1,600 줄(러너 폴링), 카메라 UVC 조회 실패 ≈550 줄 |
| `/var/log/lastlog` | 겉보기 165 MB, 실제 16 KB | 희소 파일 — 문제 아님 |
| `~/.ros/log` | 47 MB, **파일 9,746 개**(python3_*.log 5,630·launch 디렉터리 660·nav2 노드별 224 …), 30 일 넘은 것 1,952 개 17 MB | 크기는 작고 개수가 많음 |
| `/var/cache/apt` | 193 MB | `apt clean` 대상 |
| `/var/lib/snapd` | 3.0 GB (gnome·mesa·chromium 옛 리비전 포함) | 데스크톱 패키지 — 프로젝트 무관 |
| docker | 이미지 2 개 736 MB(micro-ros-agent 627 MB 사용 중, ubuntu:22.04 108 MB) | 컨테이너 0 |
| `/tmp` | ≈0 | 오늘 재부팅으로 비워짐(→ bag 은 주행 직후 회수 규칙 유지) |
| 기타 대형 | ollama(≈3.7 GB)·antigravity IDE 서버 | 사용자 개인 도구 — 대상 아님 |

### 8.2 PC
| 항목 | 크기 | 상태 |
|---|---|---|
| 저장소 `.git` | pack **7.8 MB** | 가볍다 — bag 제외 규칙(`Docs/debug_log/*/bags/`) 정상 |
| 저장소 작업 트리 | 309 MB 중 **bag 186 MB**(09-10 22·09-14 46·09-15 3·09-16 52·09-17 60 MB, git 제외), 펌웨어 micro-ROS 라이브러리 18 MB(git 제외) | bag 은 이 PC 에만 있고 백업 없음 |
| 작업 폴더 `%TEMP%\claude\…\82ce61d4…\scratchpad` | **283 MB, 810 파일** | bag 37 개 275 MB 중 **27 개 160 MB 는 저장소 bags 와 이름·크기 일치(중복)**, **10 개 114 MB(09-11 v1~v4·*_ret·cr1·ret2 원시 bag)는 저장소에 없음**. 스크립트 job 329·run 239 개 |
| **평문 비밀번호** | 작업 폴더 러너 **241 개**, WSL `/tmp` **16 개** | 저장소 밖이지만 평문 사본이 흩어져 있음(커밋본은 `<PW>` 마스킹, 누출 검사 0) |
| WSL `/tmp` | 12 MB, 1,913 파일(스크립트 사본·launch_params) | |
| 빈 세션 폴더 | 5 개 | |

### 8.3 판단
- **공간은 급하지 않다**(Jetson 193 GB, 로그 증가 1~2 MB/일). 문제는 ① **Jetson 로그가 회전되지 않아 무한히 쌓이는 구조**(분석 때 144 MB 전체를 훑어야 함), ② **PC 작업 폴더에 중복 bag 160 MB 와 저장소에 없는 원본 bag 114 MB 가 섞여 있음**(지우면 원본 손실), ③ **평문 비밀번호 사본 257 개**, ④ 실제 운용 도구(러너·job)가 세션 임시 폴더에 있어 정리하면 도구가 사라지는 구조.
