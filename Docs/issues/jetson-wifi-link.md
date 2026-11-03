# Jetson Wi-Fi 간헐 무응답 (1 시기: 08-28 · 09-03, 3 시기: 09-15 ~ 09-18, 4 시기: 09-23, 7 기: 10-14 · 10-15)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **우회**(실행을 네트워크와 분리 · 절전 끔) · 원인 미확정 · 3 시기: 'AP 가 먼저 끊고 재인증을 거부' 3 회(09-15 · 16 · 17) → 계측 서비스 설치, **원인 미확정**(후보 DFS · PMF) · 이후 양상이 다른 사건이 이어짐 · **7 기(10-14 · 10-15): 원인 하나를 사용자가 찾음 — 다른 서버가 192.168.0.101 을 받아 IP 충돌**(§2.3) → 사용자가 DHCP 서버의 .101 항목 제거 · 10-15 부터 **192.168.0.110 예약**. 09-15~17 형(AP deauth · 재인증 거부)과 같은 원인인지는 미확인 · **8 기(10-21 · 10-22): 새 유형 2 개** — 10-21 AP 의 5 GHz SSID 송출 중단(`ssid-not-found` → ALOPS 자동 전환, 사용자 '분배기 문제') 뒤 살아 있던 스택이 통신을 잃음, 10-22 Jetson 링크는 유지된 채 PC 쪽 경로만 약 2 분 끊김(§2.4) | 08-28 ~ (이 카드는 09-23 · 10-14 · 10-15 · 10-21 · 10-22 까지 채움 — 4 시기 09-23: 결합 · 인증 성공 뒤 DHCP 무응답 · 공유기 DHCP 예약 · 같은 날 끊김 4 번 더, §2.2) | [08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md) "detach 실행 → WiFi 무관" | 저장소 파일 없음(계측 스크립트 사본만 [`2026-09-18/jobs/wifi_mon.sh`](../debug_log/2026-09-18/jobs/wifi_mon.sh)). Jetson 설정: ① 09-03 `wlP1p1s0` power_save off(런타임) + NM `802-11-wireless.powersave 2`(**WEB_DEV_5G 프로파일에만**) ② 09-16 `mavlink-router` disable · NM 자동연결 우선순위 WEB_DEV_5G 20 > ALOPS_ROBOTICS_5G 5 ③ 09-18 `wifi-mon.service`(enabled) + `/usr/local/sbin/wifi_mon.sh` + `/etc/rsyslog.d/25-wifi-mon.conf` + wpa_supplicant 로그 수준 DEBUG 유지 | [첫 SLAM 지도](first-slam-map.md)(detach 실행이 생긴 곳) · [DDS 공유메모리 사고](dds-shm-incident.md)(09-16 IP 변경 뒤 DDS 분리 · 루프백 화이트리스트) · [저장 공간 · 로그 누적](storage-housekeeping.md)(09-18 같은 날 조사, syslog 무회전) · IP 충돌(10-14, §2.3) · [남서 구석 정체](southwest-orient-stall.md) (6 기) · [pad_relief · 실행 중 패딩](pad-relief-runtime-padding.md)(10-14 끊김으로 정지 시험이 밀림) · [F2 기준선 no5](f2-baseline-no5.md)(10-15 재부팅 · 새 주소 뒤 기준선) · [주행 전 검사와 운용 사고](drive-ops-1019-1023.md) · [보드 연결 · 세션](board-link-microros-session.md)(10-21 주소 변경 → 에이전트 재시작 · 보드 리셋) (8 기) |

**한 줄**: PC 에서 Wi-Fi 너머 Jetson 으로 SSH 를 걸어 로버를 움직이는데, 그 연결이 가끔 몇 분씩 끊긴다. 08-28 에는 회전 스크립트가 SSH 와 함께 죽어 '재부팅이 아님' 을 확인(`job7g`)한 뒤 **스크립트를 Jetson 안에서 독립 실행(detach)** 하게 바꿔 우회했다. 09-03 저녁에는 플래시 직후 PC → Jetson ping 100 % 손실이 수 분씩 반복돼 Jetson 쪽을 진단(링크 유지 · 신호 −53 dBm · 끊김 로그 없음 · **절전 켜짐**)하고 절전을 껐다. 그 뒤 60 회 중 57 회 응답(5 % 손실) — 쓸 만하지만 완전하지 않았고, 절전이 원인인지는 확정하지 못했다(끈 직후에도 83 % 손실, 회복은 약 2 분 뒤).

**한 줄(3 시기 09-15 ~ 09-18)**: 사흘 연속 하루 한 번(09-15 14:03:13 · 09-16 15:57:34 · 09-17 13:38:42) **WEB_DEV_5G 공유기(AP)가 Jetson 을 먼저 끊고(deauth reason 2), 같은 비밀번호로 다시 붙으려는 것을 reason 23 으로 거부**했다. NetworkManager 는 비밀번호 문제로 보고 포기한 뒤 다음 저장 망 ALOPS_ROBOTICS_5G 로 넘어가 **IP 가 192.168.0.101 → 172.30.1.8 로 바뀌었고**, 그 전에 뜬 ROS 노드와 새 노드가 DDS 에서 갈려(09-16 · 09-17) 스택 전체를 다시 띄워야 했다. 09-17 에 Jetson syslog 전체(2 월 ~)를 훑어 Jetson 쪽 원인(드라이버 · 신호 · 트래픽 · SSH 폴링) 증거가 없음을, 09-18 에 공유기 로그(무선 이벤트를 아예 안 남김)와 설정(MAC 필터 · 접속 수 제한 · 메시 · 재부팅 배제)을 확인했다. 남은 후보는 **DFS(160 MHz 가 DFS 채널 52~64 포함)** → 끊김, **PMF(802.11w, 협상 확인 pmf=1) + 제조사 드라이버** → 재인증 거부로 둘이고, 가를 계측 서비스(`wifi-mon`)를 Jetson 에 설치하고 다음 끊김 때의 판정 기준을 미리 적었다. 이 시기 안에서는 재발이 없어 원인은 **미확정**.

**한 줄(4 시기 09-23)**: 아침 08:56 부팅 직후 Jetson 은 WEB_DEV_5G 에 **결합 · 4-way 인증까지 세 번 성공**했지만 매번 **DHCP 응답이 없어** 45 s 뒤 포기하고 ALOPS(172.30.1.8)로 넘어갔다 — 09-15~17 의 'AP 가 먼저 끊고 재인증 거부' 와 다른 네 번째 양상. 사용자는 '다른 IP 의 트래픽이 내 IP 를 끊는다' 고 봤고, 나는 그 기전은 로그와 안 맞고 가장 가까운 실제 기전은 **IP 충돌**(가설, 미측정)이라고 답했다. 사용자 결정으로 **공유기에서 Jetson MAC 에 192.168.0.101 을 예약**하고, NM 두 프로파일에 주소 중복 검사(DAD 3 s), `wifi_mon.sh` 에 15 s 마다 `arping -D` 를 넣은 뒤 WEB_DEV 로 돌아왔다(10:14, 임대 2 s). 그러나 같은 날 11:57~12:06(무선 링크는 살아 있는데 PC 와의 트래픽만 8 분 끊긴 뒤 AP deauth + reason 23 + 재결합 뒤 DHCP 45 s 무응답) · 12:19(15 s, Jetson → 공유기 핑은 전부 성공 — PC 쪽 NAT 경로) · 14:13 · 14:25~14:36 에 또 끊겼고, 12:06 재연결 뒤 이미 떠 있던 스택의 CPU 가 422 % 로 뛰어 그 주행(n62b)의 CPU 판정을 무효로 만들었다(재기동한 n62c 는 정상 → 'Wi-Fi 재연결 뒤엔 스택 재기동' 규칙). ⚠ 이 카드를 쓰며 원문을 대조해 보니 **`arping -D` 패치는 파일에만 들어가고 실행 중인 서비스에는 걸리지 않았다**(§5.2 실수 3) — 09-23 의 'ARP_DUP 0 건' 은 측정이 아니다.

> 읽는 법: 08~09 월 초 기록은 § 번호가 없어 '날짜 + 제목 글자' 로 인용. 09-03 Wi-Fi 진단 도구 3 개는 **출력 원문이 없다**(대화에만) — 수치는 SUMMARY 문장이 유일한 출처.

## 1. 증상
- 08-28 오전: 제자리 회전(`job7f`, SSH 전경 실행) 도중 연결이 끊겨 스크립트가 중간에 죽음. 이것은 SUMMARY 에 직접 문장으로는 없고, 다음 세 가지로 **재구성**한 것이다 — `job7g` 의 질문('재부팅 vs WiFi 단절 판별'), `job7h` 의 '잔존 회전 프로세스 정리', detach 실행기 `job7i_launch` 의 주석 'WiFi 끊겨도 Jetson 에서 독립 완주'. 끊긴 시각 · 길이 · 그때 회전량은 기록 없음.
- 09-03 18:30~18:45: 새 펌웨어 플래시 직후 PC(172.30.1.89) → Jetson(192.168.0.101) ping 100 % 손실이 수 분간 반복. 경로상 PC 쪽 공유기(172.30.1.254, WAN 192.168.0.6)가 'host unreachable' 회신 = .6 이 Jetson 의 ARP 응답을 못 받음([09-03 '플래시 + Jetson Wi-Fi 간헐 무응답 (18:30~18:45)'](../debug_log/2026-09-03/SUMMARY.md)).
- 09-15 14:0x(3 시기): mp2 주행(NavFn + MPPI) 게이트가 통과된 직후, 주행 단계 ssh 가 아무것도 출력하지 않다가 "No route to host". Windows 에서 직접 ping: 공유기 · AP 는 응답, Jetson(192.168.0.101)은 실패. 같은 때 PC 의 WSL 네트워크도 죽어 `wsl --shutdown` 으로 살렸고(그래서 첫 폴링 결과는 무효), 20 분 넘게 무응답 — 그때는 'Jetson 이 Wi-Fi 를 잃었거나 꺼졌다' 로 봤다([09-15 §3](../debug_log/2026-09-15/SUMMARY.md)). 실제로는 98 s 뒤 다른 망(172.30.1.8)으로 살아 있었다(§5 실수 1).
- 09-16 15:57 · 09-17 13:38: 같은 끊김이 주행 직후 · 재기동 중에 다시. 이번엔 Jetson 이 새 IP 로 옮겨 간 뒤 **이미 떠 있던 노드의 토픽이 새 셸 · 새 노드에서 안 보임**(`/scan` · `/wheel_odom` 0, controller_server activating 에서 멈춤, 정지 스크립트 `ros2 topic pub -1` 이 8 분 무한 대기)([09-16 §1.13](../debug_log/2026-09-16/SUMMARY.md) · [09-17 §8.7](../debug_log/2026-09-17/SUMMARY.md)).

## 2. 흐름 (시간순)
| 날짜 · 시각 | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 08-28 (11:23 전) | `job7f` 360° 회전을 SSH 로 실행 | 도중 끊김(위 재구성) | — | [`job7f.sh`](../debug_log/2026-08-28/jobs/job7f.sh)(출력 원문 없음) |
| 08-28 11:23 | 재부팅인지 단절인지 | uptime 2:32 · 부팅 08:51:45 · 노드 · agent 생존 · 신호 −44 dBm(Link Quality 66/70) | 재부팅 아님 → 네트워크 단절 | [`job7g.sh`](../debug_log/2026-08-28/jobs/job7g.sh) · [`job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt) |
| 08-28 | 잔존 회전 정리 · 정지 확인 | 잔존 없음 · ω ≈ 0 · `/cmd_vel` 무발행 | 로버는 서 있음 | [`job7h.sh`](../debug_log/2026-08-28/jobs/job7h.sh) · [`job7h_safety_cleanup.txt`](../debug_log/2026-08-28/outputs/job7h_safety_cleanup.txt) |
| 08-28 11:28 | detach v1 | 로그 빈 채 · 회전 안 함 | 실패(원인 미확인) | [`job7i_launch.sh`](../debug_log/2026-08-28/jobs/job7i_launch.sh) · [`job7j_spin_log.txt`](../debug_log/2026-08-28/outputs/job7j_spin_log.txt) |
| 08-28 11:42 | detach v2 | 59 s 완주 · 로그 실시간 | "WiFi 드롭 무관(제어경로 Jetson→USB→보드 로컬)" | [`job7k.sh`](../debug_log/2026-08-28/jobs/job7k.sh) · [`job7k_launch.sh`](../debug_log/2026-08-28/jobs/job7k_launch.sh) · [`job7j3_spin_final.txt`](../debug_log/2026-08-28/outputs/job7j3_spin_final.txt) |
| 09-03 18:30 무렵 | 펌웨어 플래시 · `-rst` 뒤 PC → Jetson ping | 100 % 손실 수 분 반복, .6 이 'host unreachable' | PC 쪽 공유기의 ARP 실패 | SUMMARY 문장만 |
| 09-03 | Jetson 쪽 진단(읽기 전용) | `wlP1p1s0` · WEB_DEV_5G ch36 · −53 dBm · AP 1 개 · NM 끊김 로그 없음 · 커널 로그 없음 · 트래픽 ≈ 0 · **Power save: on** | 링크 자체는 유지 | [`wifi_diag.sh`](../debug_log/2026-09-03/jobs/wifi_diag.sh) · [`wifi_diag2.sh`](../debug_log/2026-09-03/jobs/wifi_diag2.sh)(출력 원문 없음) |
| 09-03 | 절전 끄기(sudo, 사용자 고지) | 직후 30 s ping **83 % 손실** → 약 2 분 뒤 .6 · .1 · .101 각 15 회 0 % → 60 s 샘플 57/60 응답(5 % 손실, 최대 308 ms) | 사용 가능하나 완전하지 않음. 원인 **미확정**(해제와 회복이 시간상 겹치나 즉시 회복 아님) | [`wifi_fix.sh`](../debug_log/2026-09-03/jobs/wifi_fix.sh)(출력 원문 없음) |
| 09-03 '내일 할 일' 4 | 재발 관찰 | — | 재발 시 2.4 GHz SSID 또는 유선 검토 | [09-03 '마무리 (18:48)'](../debug_log/2026-09-03/SUMMARY.md) |

### 2.1 3 시기 (09-15 ~ 09-18) — AP 가 끊고 재인증 거부 · 공유기 조사 · 계측 설치
시각은 Jetson syslog 기준. MAC 주소는 끝 2 바이트만 적는다(WEB_DEV_5G AP `…:1b:4c`, ALOPS AP `…:87:46`, Jetson `…:d5:35`).

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-15 §3 (14:0x) | mp2 게이트 통과 직후 주행 명령(원격 `job254 … \| tail -70`) | ssh 무출력 → "No route to host". Windows ping: 공유기 · AP OK, .101 FAIL. WSL 네트워크 동시 사망(첫 폴링 무효). 20 분+ 무응답 | 'Jetson 측(Wi-Fi 소실 또는 다운)' — **반만 맞음**: Jetson 은 살아 있었고 IP 가 바뀌었을 뿐(§5 실수 1) | SUMMARY 문장만 · [`run_recon.sh`](../debug_log/2026-09-15/jobs/run_recon.sh)(.101 만 5 s 마다 ping, 출력 원문 없음) |
| 09-15 §3 | 주행이 시작됐나 | 원격 `\| tail -70` 이라 끊긴 시점의 출력이 없음 | **미확인**. 교훈: 주행은 원격 nohup + 파일 로그, 현장 정지 수단(조이스틱 · 보드 리셋) 명시 | [`job323_state.sh`](../debug_log/2026-09-15/jobs/job323_state.sh)(복구되면 돌릴 확인, 출력 원문 없음) |
| 09-16 오전 §3.1 | USB 장치 모드 주소 192.168.55.1 로 접속, 진단 · syslog 조회 | syslog **14:03:13 `CTRL-EVENT-DISCONNECTED bssid=…:1b:4c reason=2`** → 14:03:21 `SSID-TEMP-DISABLED … reason=AUTH_FAILED`. 저장 연결 3 개 우선순위 모두 0. 사용자가 본 'Connection reset' = sshd `kex_exchange_identification: Connection reset by peer`(내 쪽 3/3 성공, 재현 안 됨). 부팅 직후 766 MB 사용 · 6.6 GB 가용, journal 비영속이라 전날 OOM 여부 모름. `mavlink-router`(PX4 잔재) 크래시 루프. `/dev/ttyUSB*` 없음(사용자가 확장보드 분리) | 'AP 측 deauth → 재연결 실패 상태로 남음 → 16:55 부터 ALOPS' — **뒷부분 틀림**: ALOPS 전환은 14:04:51(09-17 §17.1 의 원문, §5 실수 1) | [`run_usb.sh`](../debug_log/2026-09-15/jobs/run_usb.sh) · [`job324_diag.sh`](../debug_log/2026-09-15/jobs/job324_diag.sh) · [`job325_post_incident.sh`](../debug_log/2026-09-15/jobs/job325_post_incident.sh)(셋 다 출력 원문 없음) |
| 09-16 오전 | 172.30.1.x 가 PC 와 같은 서브넷 → 러너 156 개 호스트를 172.30.1.8 로 | — | 이중 NAT 경로보다 낫다 | [`run_lan.sh`](../debug_log/2026-09-15/jobs/run_lan.sh)(`JETSON_HOST` 기본 172.30.1.8) |
| 09-16 09:36 §3.1 | (사용자 지시 · sudo 동의) mavlink-router disable+stop, 우선순위 WEB_DEV_5G 20 > ALOPS 5(> PTR 0), `nmcli con up WEB_DEV_5G`(nohup) | 192.168.0.101 복귀 · ssh OK. 러너 호스트 .101 로 복원(157 개) | 규칙: 접속 전 .101 · 172.30.1.8 둘 다 ping | [`job326_net_fix.sh`](../debug_log/2026-09-15/jobs/job326_net_fix.sh)(결과는 Jetson `/tmp/nm_switch.log` — **원천 소실**) |
| 09-16 15:57:34 §1.13 | 그날 주행(15:56 종료) 직후 재발 | reason 2 → 16:00:58 ALOPS 172.30.1.8. 주행은 원격 nohup 이라 영향 없음. 전환 전에 뜬 참가자(rplidar · ekf 15:37, agent 10:42)가 옛 IP 를 광고 → 새 셸에서 `/scan` · `/wheel_odom` 0, nav2 재기동 뒤 controller activating 정지. `job156_stop` 의 `ros2 topic pub -1` 8 분 무한 대기 | 'IP 변경이 DDS 를 가른다' → 루프백 화이트리스트(같은 날 저녁 되돌림 — [DDS 공유메모리 사고](dds-shm-incident.md)). 사용자: 끊기는 이유 · 새 IP 로 붙는 이유는 나중에 분석 | [`2026-09-16/jobs/job350_disc.sh`](../debug_log/2026-09-16/jobs/job350_disc.sh) · [`run_alt3.sh`](../debug_log/2026-09-16/jobs/run_alt3.sh)(syslog 15:55~16:01 Wi-Fi 줄) — 출력 원문 없음 |
| 09-17 §8.7 (13:33) | 저속 실측 준비 중 재기동 → SSH 끊김 | SUMMARY: '13:35:45 WEB_DEV → ALOPS 전환(재부팅 아님, 가동 4 h)'. 새 프로세스에서 `/wheel_odom` · `/scan` · EKF · 깊이 · map 프레임 전부 안 보임 | 09-16 과 같은 IP 변경 분리 → 전체 정지 → 에이전트 재기동 → 보드 리셋 대기 중 **사용자가 Jetson 재부팅**. ⚠ 시각 모순: syslog 는 reason 2 가 **13:38:42**, ALOPS 가 **13:40:20**(§17.1) — 13:35:45 의 출처 출력이 없어 **미확인** | [`2026-09-17/jobs/job402_ddssplit.sh`](../debug_log/2026-09-17/jobs/job402_ddssplit.sh) · [`job401_whydrop.sh`](../debug_log/2026-09-17/jobs/job401_whydrop.sh)(출력 원문 없음) |
| 09-17 §8.7 재부팅 뒤 | 다시 붙은 망 | 우선순위 WEB_DEV 20 인데도 ALOPS(172.30.1.8) | 'WEB_DEV_5G 접속 실패로 추정, 미확인' → §17.1 에서 **확인**: 재부팅(실제 ≈13:45, 로그엔 13:05) 뒤 WEB_DEV 5 회 시도 전부 reason 23 | [`j427b_wifi.txt`](../debug_log/2026-09-17/outputs/j427b_wifi.txt) |
| 09-17 §17.1 | syslog 2 월~ 한 파일(144 MB, 회전 없음)에서 세 사건 줄 세우기 | 세 번 모두 ① reason 2 ② 8 s 뒤부터 결합마다 AP 가 reason 23 으로 끊음(결합 4 s 만에, 사건마다 5 회), `SSID-TEMP-DISABLED` 반복 ③ 94 s(09-15 · 09-17) · 199 s(09-16) 뒤 NM `failed (reason 'no-secrets')` ④ 4 s 뒤 ALOPS · DHCP 172.30.1.8. 09-16 15:58:53 엔 `4-Way Handshake failed - pre-shared key may be incorrect` · `WRONG_KEY` | `locally_generated=1` 이 없으므로 둘 다 **AP 가 보낸 deauth**. 같은 저장 PSK 로 앞뒤엔 접속됨(09-16 09:28 · 09:36, 17:53) → 비밀번호가 아니라 **AP 가 일정 시간(≥ 7 분, ≤ ≈2 h 관측) 이 단말을 거부** | [`j427b_wifi.txt`](../debug_log/2026-09-17/outputs/j427b_wifi.txt) · [`j427c_wifi.txt`](../debug_log/2026-09-17/outputs/j427c_wifi.txt) |
| 09-17 §17.2 | 전체 기간 AP 별 집계 | WEB_DEV(ch36): 연결 성공 Jan 6 · Aug 14 · Sep 10, **AP 끊김 reason 2 = 3 회(세 사건뿐)**, reason 23 = 24(Aug 25 1 · Sep 1 3 · 나머지 20 은 세 사건), reason 6305 1(Aug 25). ALOPS(ch153): 연결 64(Jan 8 · Feb 6 · Mar 32 · Apr 5 · Aug 3 · Sep 10), **AP 끊김 0**. 유지 시간 6 h 21 m(09-16) · 19 h 45 m(09-17) — 일정하지 않음. DHCP 갱신과 어긋남 | AP 가 먼저 끊은 것은 09-15 이전 0 회. 세션 타이머 · DHCP 원인 아님 | [`j427c_wifi.txt`](../debug_log/2026-09-17/outputs/j427c_wifi.txt) · [`j427d_wifi.txt`](../debug_log/2026-09-17/outputs/j427d_wifi.txt) §C |
| 09-17 §17.3 | Jetson 쪽 후보 | 끊김 ±90 s 커널 로그에 드라이버 · PCIe AER 오류 없음(곁에 보이는 건 mavlink-router 재시작 4555~4557 회째) · 스택 가동 중 Wi-Fi TX 2 KiB/s · 6 pkt/s · 10 s 창 오류 · 드롭 +0 · 끊김 전 1 h 10 분당 SSH 세션 09-17 `0 0 1 0 2 2 0` | 드라이버 · 약신호 · 트래픽 · SSH 폴링 모두 **기각**. 트리거는 AP 쪽 — AP 관리 화면 로그가 필요 | [`j427_wifi.txt`](../debug_log/2026-09-17/outputs/j427_wifi.txt) · [`j427c_wifi.txt`](../debug_log/2026-09-17/outputs/j427c_wifi.txt) · [`j427d_wifi.txt`](../debug_log/2026-09-17/outputs/j427d_wifi.txt) |
| 09-17 §17.4~17.5 | '새 IP 로 붙는 이유' · 곁가지 | NM 정상 동작(아래 §9 용어). **지금 ALOPS 연결은 절전 켜짐**: 전역 `wifi.powersave = 3`, ALOPS · PTR 프로파일 `0 (default)`, WEB_DEV 만 `2 (disable)`. 규제 영역 `country 00 … DFS-UNSET`. ALOPS 링크 −57 dBm · RX 702 / TX 175.5 Mbit/s | 제안 4 개(§4), 적용 안 함 | [`j427_wifi.txt`](../debug_log/2026-09-17/outputs/j427_wifi.txt) |
| 09-18 §0 | 사용자 아침 재부팅(10:15:47) | WEB_DEV_5G .101 정상(−50 dBm · RX 702 / TX 526.6 Mbit/s VHT 80 MHz 2×2 · power_save off). 이 부팅의 syslog 첫 줄은 `Sep 17 16:37:22` 로 찍힘 | 09-17 13:38 부터의 거부는 늦어도 이때 풀림(< ≈20 h). 사용자 결정: **WEB_DEV_5G 유지, 로그로 원인 확인** | [`j428_wifi_dfs.txt`](../debug_log/2026-09-18/outputs/j428_wifi_dfs.txt) 머리(job428b) |
| 09-18 §1 | 공유기 식별(로그인 없이) | AP BSSID 앞 3 바이트(OUI, 제조사 번호)가 EFM Networks(ipTIME) 등록값, `http://192.168.0.1/` 제목 **AX3000R**, 펌웨어 **15.03.0**. PC 에서 이중 NAT 너머로 닿음 | — | 출력 원문 없음(브라우저) |
| 09-18 §2 | 공유기 시스템 로그(사용자가 Chrome 로그인, 나는 조회 API 로 읽기만) | 1,452 건(2025-08-18 ~ 2026-09-17 14:30): DHCP 할당 1,008 · 유선 LAN 끊김/연결 139/150 · DDNS 96 · WAN 51 · 재시작 4 · 관리자 로그인 3 · 기타 2. **무선 접속 · 인증 · 차단 · DFS 기록 없음**. 09-14 이후엔 다른 기기(`…:e6:ad`) DHCP 2 건뿐, 세 시각 근처 WAN/LAN/재시작 없음. Jetson MAC 기록은 DHCP 16 건(2025-08-18 ~ 2026-09-02) | **공유기 로그로는 확정 불가** | 출력 원문 없음(원천 = 공유기 · 사용자 브라우저 세션) |
| 09-18 §3 | 공유기 무선 설정(조회 전용 API, 비밀번호 필드 가림) | 가동 254 일 22 시간 · BSS WEB_DEV_5G WPA2-PSK AES · maxsta 0(무제한) · MAC 필터 3 개 off · Easy Mesh off · **5 GHz ch36 160 MHz(중심 50 = 36~64, DFS 52~64 포함)** · dfs_status normal · country KR. 비콘: VHT seg1 42 / seg2 50, RSN **MFP-capable** | 배제: 재부팅 · 접속 수 · MAC 필터 · 메시. 후보: **DFS**, **PMF + rtl88x2ce** | 비콘만 [`j428c_bss.txt`](../debug_log/2026-09-18/outputs/j428c_bss.txt), 공유기 설정 원문 없음 |
| 09-18 §4 | Jetson 로그 재확인 | `CTRL-EVENT-STARTED-CHANNEL-SWITCH … ch_width=80 MHz` 는 접속마다 나오는 줄(WEB_DEV 42 · ALOPS 15 — 옛 호스트명 `alops-desktop` 줄 11 · 5 는 별도). BEACON-LOSS · CSA · DFS 줄은 9 월 전체에 0. `wpa_cli` 소켓 권한 거부, `iw station dump` 빈 출력. NM 프로파일 `pmf 0 (default)` | **정정**: 09-17 에 단서로 본 '재결합 때 80 MHz' 는 단서가 아님(Jetson 칩 최대 폭) | [`j428_wifi_dfs.txt`](../debug_log/2026-09-18/outputs/j428_wifi_dfs.txt) · [`j428d_pmf.txt`](../debug_log/2026-09-18/outputs/j428d_pmf.txt) |
| 09-18 §5~§6 | 판단 · 확정 방법 | 배제 목록(공유기 재부팅 · MAC 필터 · 접속 제한 · 메시 · WAN · Jetson 쪽 4 개) | 후보 ① DFS → 끊김은 설명, 재인증 거부는 못 함 ② PMF + 드라이버 → 재인증 거부는 설명, 첫 끊김은 못 함 ③ AP 펌웨어. 두 현상이 다른 원인일 수 있음. 안 A~D 중 **사용자: A(다음 발생 계측)** | — |
| 09-18 §7.1 | 사전 점검(sudo, 사용자 승인) | root `wpa_cli status`: `key_mgmt=WPA2-PSK` · **`pmf=1`** · `mgmt_group_cipher=BIP`. `wpa_cli` 모니터(level 2)는 파이프에서 10 줄 · 수준 표시 0(줄 버퍼 끔도 같음) → 기각. 전역 `log_level DEBUG` 60 s: syslog +79 줄 · +8 KiB(≈11 MiB/일), 복귀 INFO 확인. `iw scan freq 5180` 136 ms · 결과 BSS 20. 비콘 160 MHz · CSA 없음 · WPS 이름 'ipTIME BE3600QCA' | PMF 후보의 전제 성립 | [`j429_probe.txt`](../debug_log/2026-09-18/outputs/j429_probe.txt) · [`j429b_montest.txt`](../debug_log/2026-09-18/outputs/j429b_montest.txt) · [`j429c_dbgrate.txt`](../debug_log/2026-09-18/outputs/j429c_dbgrate.txt) |
| 09-18 §7.2 | 설치 · 재배포 · 시험 | 10:58:42 서비스 시작 · DEBUG 설정 · LINK 정상. **첫 BEACON 스캔이 98 s 막힘**(프로세스 트리 경과 01:38, 단독 `iw` 127 ms) → 스캔에 `timeout` 단일 10 s · 전체 20 s 추가 · 재배포 → 11:03:09 · 11:04:10 BEACON `vht_w=1 seg1=42 seg2=50 csa=0`. 스냅샷 시험 파일 41,158 B | 설치 완료 · 되돌리기 명령 기록 | [`j429d_install.txt`](../debug_log/2026-09-18/outputs/j429d_install.txt) · [`j429e_check.txt`](../debug_log/2026-09-18/outputs/j429e_check.txt) · [`j429f_trace.txt`](../debug_log/2026-09-18/outputs/j429f_trace.txt) · [`j429h_redeploy.txt`](../debug_log/2026-09-18/outputs/j429h_redeploy.txt) · [`j429i_snaptest.txt`](../debug_log/2026-09-18/outputs/j429i_snaptest.txt) |
| 09-18 §7.3 | 다음 끊김 판정 기준 **미리 선언** | (아래 §4.1 표) | 끊기면 172.30.1.8 로 접속해 `/var/log/wifi_mon/` 회수 | — |

### 2.2 4 시기 (09-23) — DHCP 무응답 · 고정 IP(예약) · 하루 네 번의 끊김
시각은 Jetson 시계(NTP 동기 뒤), 부팅 직후 줄은 `1970-01-01 09:0x`(= 부팅 기준 시계, 아래 모순 1). MAC 은 끝 2 바이트(WEB_DEV AP `…:1b:4c` — 공유기 192.168.0.1 의 ARP 항목도 같은 MAC, ALOPS AP `…:87:46`, Jetson `…:d5:35`).

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-23 §0 (08:56 부팅) | 시작 상태 | Jetson 이 ALOPS 172.30.1.8 에 붙음, .101 무응답. 스택 · 컨테이너 · `/tmp` 전부 없음 | 09-16 과 같은 양상으로 봄 → 러너를 `JETSON_HOST=172.30.1.8` 로, IP 가 박힌 `run_xfer_all.sh` 대신 호스트 변수판 | [`j498_state.txt`](../debug_log/2026-09-23/outputs/j498_state.txt) · [`run_xfer_all_h.sh`](../debug_log/2026-09-23/jobs/run_xfer_all_h.sh) |
| 09-23 §0.1 (09:45) | 사용자 요청 '백그라운드 로그 확인' — wifi-mon 기록 · syslog 회수(읽기 전용) | 전날 DHCP 갱신 16:37:11 · 17:37:11(.101) 정상. 부팅 뒤 mon.log `EVENT none -> …:1b:4c` 1970 09:00:50 · 09:01:41 · 09:03:21, `…:1b:4c -> none` 09:01:26 · 09:03:06, 09:04:01 `…:1b:4c -> …:87:46`. 세 번째 시도 syslog: 09:03:08 결합 → 4way_handshake → completed → `dhcp4 … timeout in 45 seconds` → **09:03:53 `ip-config -> failed (reason 'ip-config-unavailable')`** → `reason=3 locally_generated=1`(Jetson 이 떠남) → 09:03:54 ALOPS 자동 활성화(우선순위 5) → 09:03:58 결합 · DHCP 즉시 | '인증은 되는데 **데이터 경로(DHCP)** 가 안 됨' — 09-15~17 과 다른 양상. 후보: AP 의 DHCP · 키 설치 · 공유기 일시 장애(미확정). ALOPS 는 −52~−55 dBm 으로 09:45 까지 끊김 0 | [`job529_wifi_collect.sh`](../debug_log/2026-09-23/jobs/job529_wifi_collect.sh) · [`j529_wifi.txt`](../debug_log/2026-09-23/outputs/j529_wifi.txt) · [`job530_wifi_boot.sh`](../debug_log/2026-09-23/jobs/job530_wifi_boot.sh) · [`j530_wifi_boot.txt`](../debug_log/2026-09-23/outputs/j530_wifi_boot.txt) · wifi-mon 원본 전체 사본 = 스크래치패드 `wifi_mon_0923/`(git 제외, **지금 없음 — 원천 소실**; Jetson `/var/log/wifi_mon` 에 남았는지 미확인) |
| 09-23 §0.1 | AP 보이는가 | wifi-mon `BEACON_ALL` 09:38:53 WEB_DEV `ap_sig −51 · vht_w 1 · seg2 50 · csa 0`(160 MHz 그대로), 그러나 `nmcli dev wifi rescan` 목록엔 ALOPS 만 | '숨김 SSID 이거나 NM 이 실패 AP 를 잠시 뺀 것 — 미확정' | 같은 출력 |
| 09-23 §0.1 제안 | 사용자 결정 요청 | 4 번 중 4 번 WEB_DEV 쪽(AP deauth 3 · DHCP 무응답 1), ALOPS 0 | ① 기본을 ALOPS 로(IP 172.30.1.8 고정 · PC 와 같은 서브넷) ② 러너가 두 IP 를 핑해 자동 선택 ③ 공유기 DHCP 임대 표에서 08:57~09:03 의 Jetson MAC 요청 흔적 확인 | — |
| 09-23 §5 (10:1x) | 사용자 답 · 결정 | 사용자 '다른 IP 의 대량 트래픽이 내 IP 를 끊는다' | 그 기전은 오늘 로그(인증 성공 · DHCP 무응답) · 이전 3 회(AP deauth · PSK 거부)와 안 맞음. 가장 가까운 실제 기전 = **IP 충돌**(09-03 '링크 유지 · 핑 100 % 손실' 과는 맞을 수 있음 — **가설, 미측정**). **사용자 결정: 공유기에서 Jetson MAC 에 고정 할당(예약), DHCP 는 그대로** | — |
| 09-23 §5 사전 확인 | 설정 바꾸기 전 상태(읽기 전용) | arping · tcpdump **없음**, sudo NOPASSWD 아님, 두 프로파일 `ipv4.method auto` · `dad-timeout −1`(기본) · `autoconnect-retries −1`, `wifi_mon.sh` 89 줄 | — | [`job534_netprep.sh`](../debug_log/2026-09-23/jobs/job534_netprep.sh) · [`j534_netprep.txt`](../debug_log/2026-09-23/outputs/j534_netprep.txt) |
| 09-23 §5 적용 (10:14, sudo · 사용자 지시) | ① `iputils-arping` · `tcpdump` 설치 ② 두 프로파일 `ipv4.dad-timeout 3000` ③ `wifi_mon.sh` 에 `arping -D` 블록 삽입 ④ 3 s 뒤 `nmcli con up WEB_DEV_5G`(백그라운드) | 설치 확인 · dad 3000 × 2 · '패치 생성'. 요청 10:14:30 → PC 핑 **4 s 뒤 .101 응답**. NM 10:14:33 활성화 시작 → **10:14:35 `new lease, address=192.168.0.101`(2 s)** → activated | 아침 DHCP 무응답은 재현 안 됨(원인 미확정 — 부팅 직후 공유기/AP 측 일시 상태로 **추정**). ⚠ ③ 의 서비스 재시작은 **실행되지 않았다**(§5.2 실수 3) | [`job535_net_fixed.sh`](../debug_log/2026-09-23/jobs/job535_net_fixed.sh) · [`run_j535.sh`](../debug_log/2026-09-23/jobs/run_j535.sh) · [`j535_net.txt`](../debug_log/2026-09-23/outputs/j535_net.txt) · 공유기 예약은 사용자가 UI 에서(출력 원문 없음) |
| 09-23 §5 확인 | 패치 적용 여부(미적용이면 적용) | `wifi_mon.sh` 안 ARP_DUP 줄 **2** · 서비스 active · mon.log 10:14:40 SNAPSHOT(망 전환) · 10:14:56 WEB_DEV LINK · ARP_DUP 기록 0 · 수동 `arping -D … 192.168.0.101` 'Received 0 response(s)' · DAD 3000/3000 | '적용됨' — **파일만**(서비스 재시작 안 함) | [`job536_moncheck.sh`](../debug_log/2026-09-23/jobs/job536_moncheck.sh) · [`j536_moncheck.txt`](../debug_log/2026-09-23/outputs/j536_moncheck.txt) |
| 09-23 §5 후속 · §6 | IP 가 바뀌었으니 전체 정지(에이전트 포함) → prep | 1 차 prep: base 단계에서 '보드는 송신 중인데 세션이 없다' 로 중단 → 사용자 보드 리셋 → 2 차 통과 | IP 변경 = DDS 참가자 갈림 → 전체 재기동 + 보드 리셋이 절차 | `j510_prep_0923b.txt` · `j510_prep_0923c.txt` · [보드 연결 카드](board-link-microros-session.md) |
| 09-23 §11 (11:57~12:06) | n62b 출발 시도 중 러너가 **파일 전송 단계**에서 실패(로버는 안 움직임) | PC 쪽: 11:57 부터 .101 · 172.30.1.8 둘 다 무응답, 11:59:29 · 12:01:25 잠깐 응답, 12:06:12 이후 안정, 공유기 .1 은 정상(PC 쪽 원문 없음). Jetson 쪽 mon.log LINK: 11:50~**12:05:08** 내내 WEB_DEV · .101, 신호 −55~−58, rx 비트레이트 390 · 351 → **12:01:37~12:03:22 6.0** → 12:03:37~12:04:53 175.6(MCS 2) → 12:05:08 1.0 Mbit/s. BEACON 11:45~11:59:06 매분 `seg2 50 · csa 0`. 12:05:03 `reason 2 (PREV_AUTH_NOT_VALID)` → 12:05:07 NM `dhcp4 restarting` → 12:05:11 `reason 23 (IEEE_802_1X_AUTH_FAILED)` → 12:05:18 `activated -> failed (reason 'supplicant-timeout')` → 12:05:23 커널 `link becomes ready` · DHCP 시작 → **12:06:09 `ip-config-unavailable`**(45 s) → `reason 3 locally_generated` → 12:06:12 재결합 · **0.13 s 만에 임대 .101**. mon.log `ip=` 빈 칸 12:05:30~12:06:00. EVENT · SNAPSHOT **0 건**. ARP_DUP 0 | '무선 연결은 살아 있는데 PC 와의 트래픽만 ≈ 8 분 끊김 → 끝에 09-15~17 과 같은 서명(AP 가 클라이언트 상태를 잃고 재인증 거부)'. 판단(추정): **AP(ipTIME AX3000R)가 연결을 유지한 채 이 클라이언트의 데이터 전달을 멈췄다가 deauth**. 5 번째 사건, 5/5 WEB_DEV · ALOPS 0. 'ARP_DUP 0 = 충돌 없음(단 AP 가 전달을 멈췄으면 못 봄)' — **근거 없음**(§5.2 실수 3) | [`job539_dropchk.sh`](../debug_log/2026-09-23/jobs/job539_dropchk.sh) · [`j539_drop.txt`](../debug_log/2026-09-23/outputs/j539_drop.txt) · [`job542_dropwin.sh`](../debug_log/2026-09-23/jobs/job542_dropwin.sh) · [`j542_dropwin.txt`](../debug_log/2026-09-23/outputs/j542_dropwin.txt) · [`job543_mon.sh`](../debug_log/2026-09-23/jobs/job543_mon.sh) · [`j543_mon.txt`](../debug_log/2026-09-23/outputs/j543_mon.txt) |
| 09-23 §11 계측 보강 | 12:06 부터 Jetson 온보드 30 분 트레이스(2 s 마다 IP · 링크 · **게이트웨이 핑** · 게이트웨이 ARP 상태) | 시작 12:06:17 `ip .101 · link …:1b:4c −55 · gw=ok · neigh REACHABLE` | 다음 끊김에서 'Jetson → 공유기 핑도 죽는가(AP 전달 정지)' 를 가림. 상시화(wifi-mon 에 게이트웨이 핑)는 sudo · 사용자 결정 — **적용 안 함** | [`job540_trace.sh`](../debug_log/2026-09-23/jobs/job540_trace.sh) · [`run_j540.sh`](../debug_log/2026-09-23/jobs/run_j540.sh) · [`job541_fetch.sh`](../debug_log/2026-09-23/jobs/job541_fetch.sh)(출력은 `j539_drop.txt` 뒷부분) |
| 09-23 §12 (12:19) | n62b 재시도 중 두 번째 끊김 — 러너 파일 전송 중 PC → Jetson ≈ 15 s 무응답 | Jetson 트레이스 12:17:00~12:21:30: 2 s 마다 **gw=ok 133 / 133**, 링크 · IP 그대로, 게이트웨이 neigh REACHABLE/DELAY, 그 창의 wpa · NM · 커널 줄 **없음**, sshd 는 12:21:59 `Accepted password … from 192.168.0.6` 한 건(PC 의 NAT 바깥 주소), ARP_DUP 0 | 끊긴 구간은 Jetson 무선이 아니라 **PC → ALOPS 공유기(WAN 192.168.0.6, NAT) → WEB_DEV → Jetson 경로**. 11:57 사건의 앞 8 분도 같은 양상이었다고 봄 | [`job544_drop2.sh`](../debug_log/2026-09-23/jobs/job544_drop2.sh) · [`j544_drop2.txt`](../debug_log/2026-09-23/outputs/j544_drop2.txt) |
| 09-23 §12 · §13 | 끊김의 뒤탈 — n62b(12:24) CPU | CPU 합 **422 %**(n62a 324): ekf 37.6 · slam 34.8 · bt 25.0 · planner 19.7 · nvblox 28.6(n62a 12 · 11 · 15 · 10 · 17.7). tegra CPU 81 % · 7.73 W. bag 의 /tf 수신이 stamp 보다 2.04 s 늦음. 제어 미달 1 · 조향 반전 9.29 /m | **n62b CPU 무효** — 12:05~12:06 재연결(인터페이스 다운/업) 뒤 이미 떠 있던 Fast DDS 참가자들의 재발견 · 재전송 부하로 **추정**(IP 는 같음). 스택 재기동한 n62c 는 ekf 11.6 · slam 11.6 · 합 321 → 추정을 뒷받침. 규칙 후보: **Wi-Fi 재연결이 있었으면 주행 전 스택 재기동**(게이트에 '직전 30 분 NM 재연결 0' 검토) | [`j507_n62b_drive.txt`](../debug_log/2026-09-23/outputs/j507_n62b_drive.txt) · `top_n62b.log` · `tegra_n62b.log` · [`j553_yawseries.txt`](../debug_log/2026-09-23/outputs/j553_yawseries.txt) 머리줄 |
| 09-23 §14 | PC 를 WEB_DEV_5G 에 직접 붙여 봄(NAT 경로 빼기) | PC 에서 Jetson ARP 불가 | **AP 격리(무선 클라이언트끼리 통신 차단) 추정** → PC 는 ALOPS 로 복귀. 다음: 사용자 결정(AP 격리 해제) | 출력 원문 없음 |
| 09-23 §18 (14:13 · 14:25~14:36) | f0a1 prep 중 끊김 → prep 1 회 재실행 | Jetson 쪽 링크 유지, PC → ALOPS → WEB_DEV 경로만 끊김(SUMMARY 문장) | 12:19 와 같은 양상으로 봄. 주행은 `run_f0.sh`(setsid nohup, 끊겨도 계속) | 출력 원문 없음 · [제자리 회전 중 옆 밀림](f0-rotation-side-slip.md) |

### 2.3 7 기 (10-14 · 10-15) — 주소 192.168.0.101 충돌 · 새 예약 주소 192.168.0.110
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-14 §8.3 (10:27 무렵) | pad_relief 정지 시험을 위해 `pad_relief.py` 전송(`put_one.sh`) | scp "lost connection" → 약 3 분 동안 **192.168.0.101 · 172.30.1.8 둘 다 ping 무응답**. PC 쪽 정상(ALOPS_ROBOTICS_5G 신호 87 % · 공유기 172.30.1.254 · 8.8.8.8 응답). 스택은 10:13 prep 뒤 가동 중, 로버 정지, `pad_relief` 는 실행된 적 없음. 배터리 10:13 12.38 V | 원인 모름. 후보 = Jetson Wi-Fi 끊김(09-15~23 에 4 회 — 보통 예비 망으로 넘어가는데 이번엔 둘 다 무응답) · 전원 · 재부팅. 사용자 확인 대기 | SUMMARY §8.3 · TOOLS 10:27 줄(ping 출력 원문 없음) |
| 10-14 §8.4 (10:5x) | 사용자가 원인을 찾음 | 사용자: "현재 다른 서버 컴퓨터 하나가 101 주소를 요청하고 할당받고, 내 IP 가 끊기는 문제가 발생한 것이다." 10:53: .101 은 ping 응답 · 172.30.1.8 무응답. 그 주소의 SSH 서버 판 · 호스트 키를 인증 없이 읽음 | **지금 .101 에서 답하는 것이 Jetson 인지 가릴 수 없다** — 비교할 Jetson 호스트 키를 저장해 둔 적이 없다. 우리 스크립트는 호스트 키 검사를 끄고 비밀번호를 보내므로, 주소를 빼앗긴 상태에서 실행하면 **Jetson 비밀번호를 다른 컴퓨터로 보내게 된다** → 사용자 확인 전 접속 안 함. 과거 관계(추정): 09-23 · 10-07 의 '결합 OK · DHCP 무응답' 은 주소 충돌로 설명될 수 있음, 09-15~17 은 양상이 달라 모름. `wifi_mon` 의 `ARP_DUP` 기록으로 확인 가능하다고 적음(확인은 안 함) | SUMMARY §8.4(호스트 키 값은 이 카드에 옮기지 않음 — 다른 기기의 식별 정보) |
| 10-14 §8.5 | 사용자 "네트워크 문제는 넘어가고 다음 진행하자" → 자격 정보 없이 신원 확인 → 전송 재시도 | 101 의 8765(foxglove) 포트 연결 4/4, 호스트 키 4 회 중 2 회 응답(같은 키) → Jetson 으로 보고 진행. 그 뒤 전송이 계속 "lost connection"(1 + 재시도 8), 자격 정보 없는 SSH 는 **"No route to host"**. ping 10 회 전부 실패 직후 포트 연결은 성공 | 주소가 수 초~수십 초 단위로 붙었다 떨어짐. TCP 연결이 안 되면 인증 단계에 안 가므로 비밀번호가 다른 컴퓨터로 간 것은 아닌 것으로 봄 — **재시도 사이 잠깐 붙었을 가능성은 배제 못 함**. 8765 성공이 WSL 쪽 착시였을 가능성도(같은 시각 ping 전부 실패). 연결 없이 한 일: `pad_relief.py` SIGHUP 때도 패딩 복귀 · `jobs/run_detached.sh`(재시도 전송 + `setsid nohup`) · launch `pad_relief:=off\|on\|shadow`(기본 off) | [`run_detached.sh`](../debug_log/2026-10-14/jobs/run_detached.sh)(커밋 `c08f43c3`) · TOOLS 11:0x 줄 2 개(출력 원문 없음) |
| 10-14 §8.6 (11:15) | 사용자 조치: ipTIME DHCP 서버에서 192.168.0.101 연결 항목 제거 · Jetson 재부팅 | Jetson 은 **172.30.1.8**(ALOPS)로 붙음. ping 3/3, 도구 재전송(`up_tools.sh`, `JETSON_HOST=172.30.1.8`), prep 57 s PREP_OK. 이어 pad_relief 정지 시험 4/4 통과 | 이후 10-14 작업은 172.30.1.8. §15 구성표 '네트워크' 줄: '101 로 돌아갈지 미정' | [`chk_pad_relief.txt`](../debug_log/2026-10-14/outputs/chk_pad_relief.txt) · [10-14 SUMMARY §15](../debug_log/2026-10-14/SUMMARY.md) |
| 10-15 §1 | 재부팅 뒤(사용자 "재부팅했다") 접속 | PC Wi-Fi 172.30.1.89(ALOPS). Jetson 172.30.1.8 ping 무응답 2 분(13 회), ALOPS ARP 표에도 .8 없음 | 부팅 중이거나 다른 망(WEB_DEV_5G)에 붙었을 가능성(추정). .101 은 충돌이 있던 주소라 **신원 확인 없이 접속 안 함** | SUMMARY §1 · TOOLS 아침 줄(`chk_after_reboot.sh` 는 접속 실패로 미실행) |
| 10-15 §1.1 | 사용자 "Jetson 다시 켰다. 192.168.0.110 으로 접속되도록 DHCP 서버에 기록해뒀다." | .110 ping 응답(PC 는 ALOPS 그대로 — NAT 경로). `chk_after_reboot.sh`: 호스트 jetson-desktop · L4T R36.5.0 · `~/ros2_ws/src/rover_navigation` 있음 · `office_v3.posegraph` 있음 · SSID WEB_DEV_5G · 부팅 09:48:52 | **이 로버의 Jetson 맞음**. `/tmp` 기동 스크립트 6 개 모두 없음 → 5 개 저장소 판으로 재전송. 반영: 러너 `run_f2c.sh` 기본 `JETSON_HOST=192.168.0.110` · CLAUDE.md 네트워크 줄. ⚠ SUMMARY 는 이 확인을 '접속 전 신원 확인' 이라 적었지만 스크립트는 Jetson 위에서 돈다 — **로그인(비밀번호 전송) 뒤의 확인**(§5.3 어긋남 1) | [`chk_after_reboot.sh`](../debug_log/2026-10-15/jobs/chk_after_reboot.sh)(출력 **원천 소실**) · [`2026-10-15/jobs/run_f2c.sh`](../debug_log/2026-10-15/jobs/run_f2c.sh) 12 행 |

가설과 판별(7 기):
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 10-14 끊김 = 192.168.0.101 주소 충돌(다른 서버가 같은 주소를 받음) | 사용자 확인(공유기 쪽) · DHCP 항목 제거 + 재부팅 뒤 회복 | 사용자가 공유기에서 찾음, 항목 제거 뒤 Jetson 172.30.1.8 로 안정(그날 이후 작업 계속) | **지지(사용자 확인 + 조치 효과)**. 공유기 화면 · 임대 표 원문은 기록 없음 |
| 09-23 · 10-07 의 '결합 · 인증 OK → DHCP 45 s 무응답'(ⓒ) 도 같은 충돌 | `wifi_mon` `ARP_DUP` 기록 · 그날 공유기 임대 표 | 확인 안 함. 09-23 엔 ARP 검사가 실제로 안 돌았음(§5.2 실수 3) | **미확인**(10-14 §8.4 의 '설명될 수 있다' 는 추정) |
| 09-15~17 'AP 가 먼저 끊고(reason 2) 재인증 거부(reason 23)' 도 같은 충돌 | 양상 비교 | 충돌은 IP 층(ARP) 문제, 그 사건은 무선 인증 층 — 양상이 다름 | **미확인**(같은 원인이라는 근거 없음) |
| 10-14 §8.5 의 '재시도 중 비밀번호가 다른 컴퓨터로 가지 않았다' | 자격 정보 없는 SSH 시도 결과 · ping | "No route to host"(TCP 불성립 → 인증 단계 전) · 다만 재시도 사이 잠깐 붙었는지는 모름 | **대체로 지지 · 완전 배제 못 함** |

### 2.4 8 기 (10-21 · 10-22) — SSID 송출 중단 · PC 쪽 경로 끊김
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-21 §4 (10:48) | 사용자 알림 '내부망 분배기 문제로 192.168.0.110 핑 무응답, 보드 화면엔 `192.168.0.110?`' | PC: .110 핑 100 % 손실 · 172.30.1.8 응답, ARP 의 MAC = Jetson 무선 MAC(09-17 `j427_wifi.txt` 와 같음 — 값은 여기 옮기지 않음) → 다른 기기 아님. Jetson: 10:48:27 연결 끊김 → 스캔 두 번에 `WEB_DEV_5G` 없음 → `ssid-not-found`(10:48:42) → **10:48:45 `ALOPS_ROBOTICS_5G` 172.30.1.8**. 그때 스캔에도 `WEB_DEV` · `WEB_DEV_2G` 는 보이고 `WEB_DEV_5G` 만 없음 | **AP 쪽 5 GHz 송출이 멈춘 것**(사용자 설명과 맞음). 09-15~17 의 deauth · PSK 거부와는 다른 유형. 우선순위대로 ALOPS 로 넘어간 동작은 09-16 설정(우선순위 20 > 5)대로 | SUMMARY §4 서술(Jetson 쪽 확인 출력 **원문 없음** — 10-21 은 하루 시작 점검 출력도 저장소에 없음) |
| 10-21 §4 | 스택 상태 확인 | 프로세스(agent · display_info_pub · EKF 2 · slam · controller · realsense · cuVSLAM · vslam_twist)는 모두 살아 있는데, 새 참여자로 보면 `/rover/display_info` · `/wheel_odom` · `/vslam/odom` · `/odometry/filtered` 하나도 안 보임. 보드 화면 `?` = 펌웨어가 15 s 넘게 `/rover/display_info` 를 못 받음(`display_info_pub.py` 머리 주석) | Jetson 안 DDS 통신 자체가 끊김 — 주소가 바뀐 뒤 기존 참여자가 옛 주소 기준으로 묶인 것으로 **추정**(기전 미확인). 09-16 'IP 변경이 DDS 를 갈랐다' 와 같은 상황 → 스택 재기동 | [09-16 SUMMARY](../debug_log/2026-09-16/SUMMARY.md) 171 행 · [DDS 공유메모리 사고](dds-shm-incident.md) |
| 10-21 §5 · §6 | prep 만 다시 → 보드 토픽 0 Hz → 에이전트 재시작 → 보드 RESET → PREP_OK | `/wheel_odom 0.0 Hz · 배터리 ? V` → 세션 0 → 11:30:29 세션 1 건 · 24.994 Hz | ✘ '§4 결론(prep 재기동)' 은 부족 — 주소가 바뀌면 에이전트 재시작 + 보드 RESET 까지(09-16 · 09-23 에 이미 기록) | [보드 연결 · 세션 카드](board-link-microros-session.md) · [운용 사고 카드 §5.1](drive-ops-1019-1023.md) |
| 10-21 §6 ~ 10-22 §0 | 그날은 `JETSON_HOST=172.30.1.8` 로 작업 | 10-22 아침(10:30 재부팅 뒤) PC 핑 .110 응답(TTL 63) · 172.30.1.8 무응답 → Jetson 이 WEB_DEV_5G 로 돌아옴, 신원 `jetson-desktop` 확인 | 분배기 복구로 보임(복구 시각 · 원인 기록 없음). 재부팅으로 에이전트 · 보드도 새로 떠 §5 순서는 따로 밟지 않음 | [`chk_day_start_1022.txt`](../debug_log/2026-10-22/outputs/chk_day_start_1022.txt) `yes:WEB_DEV_5G` |
| 10-22 §5.2 (13:39~13:42) | f2dr1 러너 기동 중 전송 실패(로버 안 움직임) | 러너 `lost connection` × 3 → `ssh: connect to host 192.168.0.110 port 22: No route to host`. PC 핑: 13:39:47 두 주소 무응답, 13:40:05 잠깐 응답, 13:40:35~13:41:53 무응답, 13:42 부터 .110 안정. Jetson: 가동 3 h 12 m(재부팅 없음) · `WEB_DEV_5G:wlP1p1s0` 유지 · 13:30~13:45 끊김 사건 없음 · 13:32 DHCP 갱신(같은 주소)만 · 스택 생존(controller 1 · nvblox 4) | Jetson 무선은 유지, **PC↔AP(또는 AP 안) 경로가 끊긴 것**으로 추정(PC 쪽 무선 기록 안 봄 — 미확인). 09-23 §11 · §18 의 'Jetson 쪽 링크 유지, PC 쪽 경로만 끊김' 과 같은 양상 | [`run_f2dr1.txt`](../debug_log/2026-10-22/outputs/run_f2dr1.txt) · [`chk_ping_f2dr1.txt`](../debug_log/2026-10-22/outputs/chk_ping_f2dr1.txt) · [`chk_ping_f2dr1_b.txt`](../debug_log/2026-10-22/outputs/chk_ping_f2dr1_b.txt) · [`chk_wifi_1022.txt`](../debug_log/2026-10-22/outputs/chk_wifi_1022.txt) · `chk_wifi_1022b.txt`, 도구 `2026-10-22/jobs/chk_wifi_1022{,b}.sh` |
| 10-22 §5.3 | 끊김 뒤 prep 3 회째 — Nav2 수명 주기 활성화 멈춤 | `get_state` 응답 시간 초과 | §5.2 와 관계 미확인(Jetson 무선은 유지됐었음 — 스택은 Jetson 안에서만 DDS 를 씀) | [운용 사고 카드](drive-ops-1019-1023.md) §2 · §3 |

가설과 판별(8 기):
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 10-21 끊김 = AP 의 5 GHz SSID 송출 중단 | Jetson 스캔 목록 | `WEB_DEV` · `WEB_DEV_2G` 는 보이고 `WEB_DEV_5G` 만 없음 · `ssid-not-found` | **지지**(측정 + 사용자 '분배기 문제'). 분배기 쪽 원인은 기록 없음 |
| 10-22 끊김 = PC 쪽 경로 | Jetson 링크 · 사건 기록 | Jetson 은 같은 AP · 같은 주소 유지, 끊김 사건 0 | **지지(약함)** — PC 쪽 기록 없음 |

- ⚠ **기록 어긋남 · 관찰(10-22 13:42)**: `chk_ping_f2dr1_b.txt` 에서 Jetson 이 WEB_DEV_5G 에만 붙어 있던 동안 **172.30.1.8 이 2 s 간격으로 번갈아 응답**했다(`13:42:27 110:O 1.8:O` · `13:42:29 110:O 1.8:.` …). 그 주소에서 답한 기기가 무엇인지 기록이 없다(SUMMARY §5.2 는 '13:42 부터 안정' 만 적음). §2.3 의 '빼앗긴 주소로 접속하면 비밀번호를 다른 기기에 보낸다' 와 같은 위험 — 172.30.1.8 로 되돌릴 때는 신원 확인 먼저(해석 없음).
- ⚠ **MAC 표기**: 10-21 §4 SUMMARY 본문과 `chk_wifi_1022.txt` 원문에 MAC(Jetson 무선 · AP BSSID)이 그대로 있다 — README §4 'MAC 은 가린다' 와 어긋남(이 카드는 옮기지 않음).
- 이 시기에 wifi-mon 기록(`/var/log/wifi_mon`)을 판정에 쓴 곳: 10-22 `chk_wifi_1022.sh` 가 끊김 사건 유무를 봄(13:30~13:45 없음). 10-21 송출 중단 때의 wifi-mon 스냅숏은 기록에 없음.

이후(09-21 · 10 월): 다음 시기에서 채움. 기록 위치만 적어 둔다.
- 09-21 §0: wifi-mon 첫 스냅샷 `event_20260918_174003.txt` 는 **부팅 직후 첫 결합**(사건 아님, 시각은 NTP 전 시계) — 주말 사이 끊김 없음: [09-21 §0](../debug_log/2026-09-21/SUMMARY.md).
- 09-23: 위 §2.2 · §3.2 · §4.2 · §5.2 · §8.2 로 채움.
- 10-07 DHCP 무응답 재발 → ALOPS 로 작업: [10-07 §2.1](../debug_log/2026-10-07/SUMMARY.md).
- 10-14 사용자가 찾은 원인 — 다른 서버가 192.168.0.101 을 받아 IP 충돌: [10-14 §8.3~§8.6](../debug_log/2026-10-14/SUMMARY.md) → 위 §2.3 으로 채움.
- 10-15 부터 192.168.0.110(DHCP 예약): [10-15 §1.1](../debug_log/2026-10-15/SUMMARY.md) → 위 §2.3. 8 기(10-19 ~ 10-23): 10-21 SSID 송출 중단 · 10-22 PC 쪽 경로 끊김 → 위 §2.4 로 채움. 이후(10-26 ~): 다음 시기에서 채움.
- **wifi-mon 은 지금도 돈다**: 10-27 · 10-28 주행 기록의 프로세스 목록에 `wifi_mon.sh` 가 있다(예: [`2026-10-28/outputs/drives/f2tt2/f0_f2tt2/proc_f2tt2.log`](../debug_log/2026-10-28/outputs/drives/f2tt2/f0_f2tt2/proc_f2tt2.log)). 10-22 `chk_wifi_1022.sh` 가 `/var/log/wifi_mon/*.log` 를 읽었다. ⚠ 스크립트 안의 감시 대상 AP 는 09-18 의 WEB_DEV_5G BSSID(`…:1b:4c`) · 주파수 5180 으로 **고정**되어 있다 — 공유기 · SSID 가 바뀌었으면(10-21 송출 중단) BEACON 줄 대신 10 분마다 전체 스캔만 남는다(코드 기준 추론, 현재 Jetson 설치본은 09-23 패치판이라 미확인). §7.3 기준으로 09-15~17 형 끊김을 판정한 기록은 이 카드 범위(09-23 까지)에서는 없다 — 09-23 12:05 사건도 DFS · PMF 둘 다 **미판정**(§3.2, 직전 BEACON 6 분 공백 · 4-way 줄 미회수 · 스냅샷 0).

## 3. 가설과 판별 (09-03 까지)
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 08-28 끊김 = Jetson 재부팅(전원 · 과부하) | `job7g` uptime · 부팅 이력 · 노드 생존 | 2:32 가동, 노드 · agent 생존 | **기각** |
| 08-28 끊김 = 약한 신호 | `job7g` iwconfig | −44 dBm, 66/70 | '지금은 좋음' 까지만 — 끊긴 순간 값이 아니라 **미확인** |
| 09-03 = Jetson 무선 링크 자체가 끊김 | `wifi_diag` · `wifi_diag2`(link · station dump · NM 로그 · 커널 로그) | 링크 유지 · NM · 커널 끊김 기록 없음 | **기각**(그 시각 기준) |
| 09-03 = Wi-Fi 절전(power save)으로 Jetson 이 ARP 에 늦게 답함 | 절전 끄고 ping | 직후 83 % 손실 → 약 2 분 뒤 회복 → 5 % 손실 | **미확인** — 끈 효과인지 저절로 회복인지 못 가름(끄기 전 같은 시간 동안의 기준선 없음) |
| 09-03 = PC 쪽 공유기(.6)의 WAN ARP | .6 이 'host unreachable' 을 회신 | 증상 위치는 .6 | 후보로 남김(공유기 쪽 로그 없음) — **미확인** |
| 09-03 = Jetson 무선 칩 드라이버(RTL8822CE 5 GHz) | — | 시험 없음 | 후보로 남김 — **미확인** |
| 플래시(ST-Link `-rst`)가 방아쇠 | 시간상 겹침만 | — | 플래시는 보드(MCU)이고 Jetson 무선과 연결고리 없음 — 우연으로 봄(**추정**, 판별 안 함) |

### 3.1 가설과 판별 (3 시기 09-15 ~ 09-18) — 두 현상을 나눠 본다: ⓐ 첫 끊김(reason 2) ⓑ 그 뒤 재인증 거부(reason 23 반복)
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 09-15 무응답 = Jetson 다운 · OOM | 09-16 부팅 직후 메모리 · journal(`job324`) · syslog 전원/OOM 키워드(`job325`) | 766 MB 사용 · 6.6 GB 가용, 전날 journal 비영속이라 OOM 은 못 봄. 그러나 syslog 에 14:04:51 ALOPS 연결 · 14:34:51 DHCP 갱신이 이어짐 | **기각**(살아서 다른 IP 에 있었음 — 09-17 원문으로 확정) |
| ⓑ 비밀번호(PSK)가 틀림 | 같은 저장 PSK 로 앞뒤 접속 여부 | 09-16 09:28 · 09:36 · 17:53 같은 프로파일로 성공 | **기각**. 'pre-shared key may be incorrect' 는 4-way 실패 때 wpa_supplicant 의 추정 문구 |
| Jetson 드라이버(rtl88x2ce) · PCIe 오류 | 끊김 ±90 s 커널 · syslog(`job427c` B) | 오류 없음 | **기각**(로그에 남는 오류에 한해) |
| 약한 신호 | 09-03 −53 dBm · 재결합 시 '정상 결합 뒤 4 s 만에 거부' | 결합 단계는 매번 성공 | **기각** |
| 과다 Wi-Fi 트래픽(DDS 등) | 스택 가동 중 10 s 송수신(`job427` 4) | TX 2 KiB/s · 6 pkt/s, 창 안 오류 · 드롭 +0 | 정상 상태 **기각**. 스택 재기동 순간 멀티캐스트 버스트는 **미측정** |
| 러너 SSH 폴링 빈도 | 끊김 전 1 h 10 분당 세션 수(`job427d`) | 09-17 `0 0 1 0 2 2 0`, 끊김 없던 09-14 최대 46/10 분 | **기각**(SUMMARY 근거). 단 09-15 `0 23 6 6 35 0 0` · 09-16 `0 0 0 3 24 21 0` 은 바빴다 — §5 모순 2 |
| 세션 타이머 · DHCP 갱신 | 유지 시간 · 갱신 시각 대조 | 6 h 21 m vs 19 h 45 m, 갱신과 90 s · 58 min · 8 min 차이 | **기각** |
| 공유기 재부팅 · MAC 필터 · 접속 수 제한 · Easy Mesh · WAN 장애 | 공유기 로그 · 설정 조회(09-18 §2 · §3) | 가동 254 일, 필터 off, maxsta 0, 메시 off, 세 시각 근처 WAN/LAN 사건 없음 | **기각** |
| ⓐ DFS(160 MHz 폭이 DFS 52~64 포함 → 레이더 · 오감지 때 AP 가 무선부 재구성) | Jetson syslog 의 CSA · 비콘 손실 · 규제 변경 줄(`job428`), 끊김 순간의 비콘 폭(→ wifi-mon) | 9 월 전체에 CSA · BEACON-LOSS 0. 공유기는 DFS 를 기록하지 않음 | **미확인** — CSA 없이 끊는 펌웨어도 있다는 것이 근거(일반론, 이 기종 확인 아님) |
| ⓑ PMF(802.11w) 상태 불일치 + 제조사 드라이버 | `wpa_cli status`(root) · 다음 끊김 때 DEBUG 로그의 4-way 단계 | `pmf=1` · BIP 협상 확인(전제 성립). 단계별 증거는 아직 없음 | **미확인** |
| AP 펌웨어(15.03.0) 결함 | — | 시험 없음 | **미확인** |

### 3.2 가설과 판별 (4 시기 09-23) — 세 양상: ⓒ 결합 · 인증 성공 뒤 DHCP 무응답 ⓓ 링크 유지 중 PC 와의 트래픽만 끊김 ⓔ PC 쪽 NAT 경로 끊김
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 아침 끊김 = 09-15~17 형(AP deauth · 재인증 거부) | 부팅 블록 wpa · NM 줄(`job530`) | 결합 · 4-way 완료 · NM 'Connected', 끊은 쪽은 Jetson(`reason 3 locally_generated`) — DHCP 45 s 무응답 뒤 | **기각** — 양상 ⓒ 는 새것 |
| ⓒ = 공유기/AP 의 일시 장애(부팅 직후) | 같은 프로파일로 다시 붙기(10:14) | 임대 2 s 성공 · 재현 안 됨 | **미확인**(1 회 재현 실패는 근거가 약함) |
| ⓒ = IP 충돌(다른 기기가 .101 사용) | 09-23 에는 판별 없음(ARP 검사가 실제로 안 돌았음 — §5.2 실수 3) | — | 09-23 **미확인**. 이후 10-14 사용자가 '다른 서버가 .101 을 요청해 할당받음' 을 찾음 → 10-14 §8.4 '09-23 · 10-07 의 DHCP 무응답은 주소 충돌로 설명될 수 있다(추정)'. DHCP 서버가 왜 응답을 안 했는지(충돌과의 연결 고리)는 **미확인** |
| 사용자 가설: 다른 IP 의 대량 트래픽이 내 IP 를 끊는다 | 기전 대조 · 11:57 창의 계측 | 끊긴 쪽 단서는 AP 상태(reason 2 · 23) · DHCP. 트래픽 계측은 이 날 없음 | 지지 증거 없음 — **미확인**(기각할 측정도 없음) |
| ⓓ 11:57 = Jetson 무선 끊김 | mon.log LINK 15 s | 12:05:08 까지 연결 · IP 유지 | **기각** |
| ⓓ = AP 가 연결은 유지한 채 이 단말로의 데이터 전달을 멈춤 | rx 비트레이트 · deauth 순서 | 12:01:37~12:03:22 rx 6.0(기본 속도 — 데이터 프레임을 못 받았을 수 있음), 끝에 AP 가 reason 2 | **추정** — 6.0 은 유휴 때도 나오는 값이고(ALOPS 09:35~09:45 내내 6.0), 11:57~12:01 에는 데이터 속도(351~390)였다. Jetson → 공유기 핑은 그 창에 없음(트레이스는 12:06 부터) |
| ⓔ 12:19 = Jetson 무선 | 온보드 트레이스 | 게이트웨이 핑 133/133 · wpa/NM 줄 0 | **기각** → PC → NAT(.6) → WEB_DEV 경로 쪽 **지지**(그 경로의 어느 구간인지는 미확인) |
| DFS(09-18 §7.3 기준 1·2) | 끊김 직전 BEACON 폭 · CSA | 11:59:06 까지 `seg2 50 · csa 0`. 12:00~12:05 BEACON 줄은 회수 출력에 없음(`job543` 이 BEACON 을 뺌) | **미판정**(직전 6 분이 비어 있음) |
| PMF 상태 불일치(기준 3·4) | 12:05:11 재인증의 4-way 단계 debug 줄 | 회수 안 함(`job542` 는 CTRL-EVENT · reason 줄만), 사건 스냅샷도 없음(EVENT 0), 원본 사본 소실 | **미판정** |
| n62b CPU 422 % = 재연결 뒤 DDS 재발견 부하 | 재기동 뒤 같은 구성 n62c | ekf · slam 11.6 · 합 321 로 정상 | **지지**(추정 — 재발견 트래픽 자체는 재지 않음) |

## 4. 조치와 효과
- **08-28 · detach 실행(가장 효과가 큰 조치)**: 로버를 움직이는 스크립트를 Jetson 안에서 SSH 와 무관하게 돌리고(`setsid … </dev/null &` + `disown`, 출력은 `/tmp/spin.log`), PC 는 나중에 로그만 읽는다(`job7k` · `job7k_launch` · `job7j`). 끊겨도 스크립트 자체의 가드 · 목표 · 시간 제한으로 끝난다. 효과: 같은 날 360° 회전 완주(59 s). 제어 경로(Jetson → USB → 보드)는 Wi-Fi 를 안 지나므로 '주행 중 끊김' 이 주행을 멈추지는 않는다 — 반대로 **PC 에서 멈출 수도 없다**(09-03 '벤치마크 중에는 … 사용자가 물리 정지 담당').
- **09-03 · 절전 끄기**: `iw dev wlP1p1s0 set power_save off`(재부팅 때 사라짐) + `nmcli con modify <당시 연결> 802-11-wireless.powersave 2`(그 프로파일에 영구). 효과: 5 % 손실 · 최대 308 ms 까지(위 표). 한계: 다른 프로파일(ALOPS)에는 적용 안 됨(09-17 §17 에서 확인).
- 남은 위험(09-03 판단): 주행 중 끊기면 Nav2 는 Jetson 에서 계속 돈다 → 사람이 물리적으로 정지. 온보드 정지 수단 · 목표 시간 제한은 다음 시기(09-29 '정지 수단', `nav_guard`).

### 4.1 3 시기 조치 (09-15 ~ 09-18)
- **09-15 · 주행 실행 방식**: 주행 명령은 원격 `nohup` + 파일 로그로 띄우고 결과를 파일로 회수(원격 `| tail` 금지), 현장 정지 수단(조이스틱 · 보드 리셋) 명시, 게이트 통과 뒤 목표 전송 직전 링크 재확인. 효과: 09-16 · 09-17 끊김 때 주행은 끝까지 갔다(09-16 15:56 종료, 09-17 §8.8 '약 2 분 끊겼으나 분리 실행이라 완료').
- **09-16 · `mavlink-router` 비활성**(사용자 지시 · sudo): PX4 잔재 서비스가 `/dev/ttyACM0` 없음으로 3 s 마다 재시작(09-15 14:01 무렵 재시작 횟수 4,555 회째) → syslog 를 하루 7~10 MB 채우던 주범. Wi-Fi 와의 인과는 없음(끊김 이후에도 사건은 이어짐) — 효과는 로그 양([저장 공간 카드](storage-housekeeping.md)).
- **09-16 · NM 자동연결 우선순위** WEB_DEV_5G 20 > ALOPS 5(사용자 결정). 한계: AP 가 거부하면 ALOPS 로 넘어가는 것은 그대로이고, 넘어간 뒤엔 높은 쪽으로 돌아오지 않는다(09-17 에 그대로 일어남).
- **09-17 §17.6 제안(적용 안 함, sudo · 사용자 결정 필요)**: ① ALOPS 로 고정(7 개월 AP 끊김 0, PC 와 같은 서브넷) ② ALOPS 프로파일 절전 끔 ③ 172.30.1.8 DHCP 예약 · 국가 코드 KR ④ WEB_DEV 를 쓰려면 AP 로그 먼저 + DDS 를 IP 변화에 면역(루프백 한정 — 09-16 에 에이전트 컨테이너 문제로 보류). **사용자 결정(09-18): WEB_DEV_5G 유지 · 원인 확인 먼저.**
- **09-18 · A 안 계측 설치**(사용자 승인 · sudo, 네트워크 설정 변경 없음): 설치물은 §8 도구 해설 `wifi_mon.sh` · `job429d_install.sh`. 되돌리기: `sudo systemctl disable --now wifi-mon; sudo rm /etc/rsyslog.d/25-wifi-mon.conf; sudo systemctl restart rsyslog; sudo wpa_cli log_level INFO` + `/usr/local/sbin/wifi_mon.sh` · `/etc/systemd/system/wifi-mon.service` · `/var/log/wifi_mon/` 삭제.
- 기각 · 미선택 안(09-18 §6): B 공유기 80 MHz(사무실 공유 공유기, 관리자 동의 필요), C Jetson PMF 끄기(`pmf 1` — 보안 약간 낮아짐), D ALOPS 자동연결 끄기 + root 재시도 감시(끊김 동안 원격 불가 대신 IP 고정).

**09-18 §7.3 판정 기준(다음 끊김 때, 미리 선언)**:
| 관측 | 판정 |
|---|---|
| 끊김 직전 BEACON 에서 seg2 50 → 0/없음(160→80) 또는 CSA=1, 혹은 끊김 뒤 BEACON_ALL 에서 폭이 줄어 있음 | **DFS** 가 끊김의 원인 |
| 끊김 직전 BEACON 폭 그대로 · CSA 0 | DFS 아님 → 공유기 쪽 다른 원인 |
| 재접속 debug 에 msg 1/4 수신 · 2/4 송신 뒤 AP deauth(reason 23), SA Query · 'Association comeback' · PMF 관련 줄 | **PMF 상태 불일치**가 재인증 거부 원인 쪽 |
| msg 1/4 자체가 안 옴 | AP 가 인증 단계 전에 거부 — 공유기 측 거부 목록 · 상태 |

### 4.2 4 시기 조치 (09-23)
- **고정 IP = 공유기 DHCP 예약**(사용자 결정 · 공유기 UI, Jetson MAC → 192.168.0.101). NM 은 그대로 DHCP. 효과: 10:14 임대 2 s, 12:06 재연결 때도 .101 유지(0.13 s). 한계: **끊김 자체는 못 막는다**(같은 날 11:57 · 12:19 · 14:13 · 14:25). 그리고 예약은 '다른 기기가 같은 주소를 쓰는 것' 을 막지 못한다 — 10-14 에 실제로 그렇게 됐다(다른 서버가 .101).
- **NM DAD 3 s**(`ipv4.dad-timeout 3000`, 두 프로파일, sudo): 주소를 쓰기 전 3 s 동안 ARP 로 중복을 묻고, 충돌이면 활성화 실패 + 'duplicate address' 로그. 09-23 에 그 로그는 본 적 없음(찾은 기록도 없음). 실제로 3 s 검사가 돌았는지는 **미확인** — `j535` 에서 DHCP 시작(10:14:33.209) → 임대(10:14:35.352) 2.14 s, 임대 → activated 13 ms 로, 3 s 대기가 눈에 띄지 않는다(NM 내부 DHCP 클라이언트가 임대 보고 전에 검사를 하는지는 확인 안 함).
- **wifi-mon `arping -D` 패치**(`job535` ③): `LINK` 줄 뒤에 IPv4 가 있고 arping 이 있으면 `timeout 5 arping -D -c 2 -w 2 -I wlP1p1s0 <내 IP>` → 'Unicast reply' 가 있으면 `ARP_DUP ip=… <응답 줄>` + 5 분에 1 번 스냅샷. ⚠ 09-23 에는 **실행 중인 서비스에 반영되지 않음**(§5.2 실수 3). 다음 서비스 재시작(재부팅) 뒤부터 돌았을 것으로 **추정**.
- `iputils-arping` · `tcpdump` 설치(apt, sudo).
- **러너 IP 자동 선택**(`run_jx.sh`, 09-23): `JETSON_HOST` 가 없으면 .101 → 172.30.1.8 순서로 핑해 응답하는 쪽. 이후 10-15 고정 주소 192.168.0.110 으로 바뀌면서 `JETSON_HOST=192.168.0.110` 관례(CLAUDE.md 네트워크 줄).
- **주행은 끊김과 분리**: `run_f0.sh`(setsid nohup + 로그 폴링, 전송 재시도 3 회) — [제자리 회전 카드](f0-rotation-side-slip.md) 도구 해설.
- **규칙(절차 v2.2 후보 → 지금 CLAUDE.md §6 '주행 30 s 전 DDS 참여자 생성 금지, Wi-Fi 재연결 뒤엔 스택 재기동')**: n62b → n62c 의 근거.
- 제안만(적용 안 함): ① 기본을 ALOPS 로(§0.1, 사용자는 예약을 택함) ② wifi-mon 에 게이트웨이 핑 상시화(§11) ③ AP 격리 해제(§14, 사무실 공유 공유기).

## 5. 내 실수
- 이 시기에 '틀린 판정을 고친' 기록은 없다. 다만 두 가지는 판별이 비어 있다(다음 칸에 남김).
  - 08-28 끊김의 사실 자체가 SUMMARY 에 문장으로 없다 — 도구 주석으로만 재구성 가능. **다음에 알아보는 법**: 연결 끊김은 그 순간 PC 쪽 시각 · 증상(ssh 오류 문구) · 길이를 SUMMARY 에 한 줄로 남긴다.
  - 09-03 절전 OFF 의 효과를 '전후 같은 길이의 ping 기준선' 없이 판단했다. **다음에 알아보는 법**: 설정을 바꾸기 전에 같은 조건의 기준선(예: 60 s ping 손실률)을 먼저 남기고, 바꾼 뒤 같은 측정 — 그래야 '저절로 회복' 과 구별된다.

### 5.1 3 시기 (09-15 ~ 09-18)
**실수 1 — '20 분 무응답 = Jetson 이 망을 잃었다 · 재연결 실패 상태로 남았다'(09-15 §3 · §3.1). 기록에 정정 문장이 없어 이 카드에서 원문으로 처음 짚는다.**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | mp2 주행 결과 회수, 끊긴 뒤 복구 감시(`run_recon.sh` — 192.168.0.101 만 5 s 마다 ping, 복구되면 `job323_state.sh`) |
| 본 것 | .101 이 20 분 넘게 무응답 · 공유기 · AP 는 응답. 다음 날 syslog: 14:03:13 reason 2 · 14:03:21 AUTH_FAILED(09-16 오전에 본 줄은 여기까지) |
| 처음 추론 | 'Jetson 측 Wi-Fi 소실 또는 다운'(09-15), '그 뒤 재연결 실패 상태로 남음 → 사용자가 14:41 · 16:55 재부팅, 16:55 부터 ALOPS'(09-16) |
| 의심한 이유 | (당시엔 의심 없음) 09-17 `job427b` 의 9 월 타임라인에서 같은 날 **14:04:51 ALOPS 연결 · DHCP 172.30.1.8**, 14:34:51 · 15:08 … 30 분마다 갱신이 보임 |
| 판별 | syslog 원문 줄 대조(`j427b_wifi.txt` 91~128 줄) |
| 결론 | Jetson 은 끊긴 지 98 s 만에 172.30.1.8 로 살아 있었다. '무응답' 은 **우리가 옛 주소만 두드린 것**. 주행 시작 여부를 끝내 모르게 된 것도 이 때문(그때 172.30.1.8 로 붙었으면 `/tmp/nav2.log` · bag 을 재부팅 전에 회수할 수 있었다 — 추정) |
| 다음에 알아보는 법 | 서명: 'Jetson 무응답 + 공유기 · AP 는 응답' → 먼저 **다른 저장 망 주소(172.30.1.8)와 USB 192.168.55.1** 을 ping. 규칙은 09-16 §3.1 에 들어갔다('접속 전 두 주소 다 ping'). 로그를 볼 땐 끊김 줄에서 멈추지 말고 그 뒤 '활성화 · DHCP 주소' 줄까지 읽는다 |
| 데이터 | `2026-09-17/outputs/j427b_wifi.txt` · 원천 Jetson `/var/log/syslog`(09-17 당시 144 MB, 회전 없음) |

**실수 2 — '재결합 때 채널 폭이 80 MHz 로 바뀌었다' 를 DFS 단서로 봄(09-17 §17 → 09-18 §4 에서 정정)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 끊김 순간 AP 쪽 변화(채널 · 폭) 찾기 |
| 본 것 | 재결합 직후 `CTRL-EVENT-STARTED-CHANNEL-SWITCH freq=5180 … ch_width=80 MHz cf1=5210` |
| 처음 추론 | AP 가 160 → 80 MHz 로 내려갔다(DFS 로 52~64 를 비움) |
| 의심한 이유 | 09-18 공유기 설정이 160 MHz 그대로 · Jetson 칩이 80 MHz 까지 |
| 판별 | `job428` C: 정상 접속 때마다 같은 줄이 나오는지 |
| 결론 | 접속마다 나오는 드라이버 줄(WEB_DEV 42 · ALOPS 15) — 단서 아님 |
| 다음에 알아보는 법 | '사건 때 본 줄' 은 먼저 **평소 접속에서도 나오는지** 기준선 개수를 센다. 폭은 Jetson 줄이 아니라 AP 비콘(VHT seg2)으로 본다 → wifi-mon 의 BEACON 줄 |
| 데이터 | `2026-09-18/outputs/j428_wifi_dfs.txt` §A · §C |

**기록 사이 모순 · 도구 결함(원문 대조, 10-30)**
1. **09-17 §8.7 '13:35:45 전환' vs §17.1 syslog 'reason 2 13:38:42 · ALOPS 13:40:20'**. 13:35:45 를 낸 출력(`job401_whydrop.sh` 추정)은 저장 안 됨. SSH 가 13:33 에 끊겼다는 것도 syslog 의 끊김(13:38:42)보다 5 분 앞선다 — PC 시계와 Jetson 시계 차이인지 다른 원인인지 **미확인**.
2. **§17.3 SSH 폴링 기각의 근거가 한 날뿐**: 끊김 전 1 h 10 분당 세션은 09-17 `0 0 1 0 2 2 0` 이지만 09-15 `0 23 6 6 35 0 0`, 09-16 `0 0 0 3 24 21 0` 은 바빴다([`j427d_wifi.txt`](../debug_log/2026-09-17/outputs/j427d_wifi.txt) §B). 09-17 이 거의 0 인데도 끊겼으니 '폴링이 필요조건은 아니다' 까지는 맞고, '바쁜 폴링이 방아쇠를 거들었을 가능성' 은 배제되지 않는다.
3. **NTP 전 시각은 '≈40 분 이르다' 가 일정하지 않다**: 09-17 재부팅은 ≈40 분(13:45 → 13:05)이었지만 09-18 10:15:47 부팅은 `Sep 17 16:37:22` 로 찍혔다(약 17.6 h 차이, [09-18 §0](../debug_log/2026-09-18/SUMMARY.md)). 또 `j427b` 에서 09-16 17:53:58 WEB_DEV 재접속 줄은 18:00:58 DHCP 갱신 줄 **뒤**에 있다 → 이 줄도 NTP 전 시각일 가능성(추정). 그렇다면 '거부 ≤ ≈2 h' · '유지 19 h 45 m' 은 수십 분 틀릴 수 있다. 같은 이유로 09-15 §3.1 의 '16:55 재부팅' 줄도 17:12:43 갱신 줄 뒤에 있고, ALOPS 활성화는 14:41 · 14:50 · 15:07 · 16:55 네 번이라 재부팅 횟수 '2 회' 는 **미확인**.
4. **`job428` B 구간(끊김 −60 ~ +20 s 줄)이 세 사건 모두 빈 출력** — 그 창에 반드시 있어야 할 reason 2 줄 자체도 없다 → 시각 변환(`date -d "2026 Sep 15 …"`)이 실패한 **도구 결함**(추정, 원인 줄 미확인). 09-18 §4 '세 끊김 직전에 CSA · 비콘 손실 · 규제 변경 줄이 없다' 의 유효한 근거는 B 가 아니라 A(9 월 전체 종류별 개수에 BEACON-LOSS · CHANNEL-SWITCH(CSA) · DFS 가 하나도 없음)다.
5. **드라이버 모듈 이름**: `job427b` E · `job428d` 는 `/sys/module/rtl88x2ce/parameters/` 를 읽었는데 실제 모듈은 `rtl8822ce`(`j427_wifi.txt` '펌웨어/모듈: rtl8822ce') → '디렉터리 없음'. **드라이버 절전 파라미터는 한 번도 읽지 못했다**(값이 없는 게 아니라 못 읽음).
6. **'오류 · 드롭 0'**(§17.3): 10 s 창의 증가분이 0 이고, 누적으로는 `rx_dropped 282` 가 있다([`j427_wifi.txt`](../debug_log/2026-09-17/outputs/j427_wifi.txt) 107 줄). 결론엔 영향 없음.
7. **'유휴 60 s 에 79 줄'**(§7.1): `job429c` 는 10 s 뒤 스캔을 일부러 한 번 걸었다(wpa 줄 73 중 스캔 관련 44). 진짜 유휴 양은 이보다 적다(**미측정**). 실제 운용 중에는 wifi-mon 이 매분 스캔하므로 오히려 이 값이 운용에 가깝다(추정).
8. **'0 줄' 출력 두 개는 측정이 아님**: `j429d_install.txt` 'wpa_debug.log: 0 줄'(파일은 1,884 B) · `j429i_snaptest.txt` '0 줄, 크기 41158 B' — `S wc -l < 파일` 에서 리다이렉트는 sudo 밖(일반 사용자)에서 열려 권한 실패 → 0. SUMMARY 는 이 값을 쓰지 않았다.
9. **스냅샷 비밀 검사 '1'**: `j429i` 의 'psk|passphrase|password 값: 1' 을 SUMMARY 는 WPS `Device Password ID` 단어로 판정했다. 그 확인 도구 `job429j_secret.sh` 의 출력은 저장 안 됨 → 판정의 원문 **소실**(SUMMARY 문장만).

### 5.2 4 시기 (09-23)
**실수 3 — 'ARP_DUP 0 건 = 이 창에 IP 충돌 없음'(§11 · §12). 기록에 정정 문장이 없어 이 카드에서 원문으로 처음 짚는다.**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | IP 충돌 가설을 상시 계측으로 가르기 — `job535` ③ 이 `wifi_mon.sh` 에 `arping -D` 를 넣고 서비스를 재시작 |
| 본 것 | `j535` 3 절이 '패치 생성' 한 줄로 끝나고, 사슬 끝의 확인 줄('wifi-mon: … \| ARP_DUP 줄 …')이 **없다**. `j536` 은 '파일에 ARP_DUP 줄 2 · 서비스 active · 기록 0'. §11 · §12 는 'ARP_DUP 0 건(15 s 마다 `arping -D`)' 을 근거로 씀 |
| 처음 추론 | 패치가 걸렸고 15 s 마다 검사 중 → 0 건이면 충돌 없음(단서: AP 가 전달을 멈췄으면 못 봄) |
| 의심한 이유 | (10-30 카드 작성 중) 확인 줄이 빠진 이유를 코드로 따라감: `S() { echo "$PW" \| sudo -S -p '' "$@" 2>&1 \| grep -av '^\[sudo\]'; }` — 파이프의 종료 코드는 마지막 `grep` 의 것. `cp` 는 아무것도 출력하지 않으니 grep 이 한 줄도 못 골라 **종료 코드 1** → `bash -n … && S cp … && S systemctl restart wifi-mon && sleep 2 && echo …` 사슬이 `cp` 뒤에서 끊김(파일은 바뀌고 재시작은 안 됨). `job536` 은 파일에 ARP_DUP 가 있으면 아무것도 안 함. 실행 중인 bash 는 `while true; do … done` 을 시작할 때 통째로 읽어 메모리에서 돌리므로 파일을 바꿔도 새 블록을 실행하지 않는다 |
| 판별 | 루프 간격: `arping -D -c 2 -w 2` 는 응답이 없으면 약 2 s 를 기다리므로(일반 동작 — 이 Jetson 에서 시간을 재지는 않음) 검사가 돌면 15 s 루프가 ≈ 17 s 가 돼야 한다. mon.log LINK 간격 — 패치 전 09:35~09:45 38 간격 평균 **15.29 s**(`j529`), 패치 뒤 11:50~12:07 70 간격 평균 **15.19 s**(`j543`). 늘지 않았다. 11:50~12:07 창에 서비스 시작 줄(`START pid`)도 없다 |
| 결론 | 09-23 의 'ARP_DUP 0' 은 **측정이 아니다**(검사가 돌지 않았다 — 두 증거가 같은 쪽, 서비스 프로세스를 직접 보지는 않아 '추정'). §11 의 'IP 충돌을 완전히 배제하지는 못한다' 는 맞는 방향이었지만 근거는 그보다 약했다 — 09-23 의 충돌 여부는 **미확인** |
| 다음에 알아보는 법 | 상시 서비스 스크립트를 고치면 ① 재시작 흔적(`START pid` 줄 · `systemctl show -p ActiveEnterTimestamp`) ② 새 블록이 실제로 돈다는 흔적(새 줄 · 루프 시간 변화)을 확인한 뒤 그 결과를 근거로 쓴다. 출력 거르개(`\| grep -v`)로 감싼 명령을 `&&` 로 잇지 않는다 — 확인 줄은 사슬 밖에 두거나 `${PIPESTATUS[0]}` 로 원래 종료 코드를 본다. 서명: 사슬 끝의 확인 echo 가 출력에 없음 |
| 데이터 | `jobs/job535_net_fixed.sh`(9 행 S 정의 · 3 절 사슬) · `outputs/j535_net.txt` · `jobs/job536_moncheck.sh` · `outputs/j536_moncheck.txt` · `outputs/j529_wifi.txt` · `outputs/j543_mon.txt`(LINK 시각) |

**기록 사이 모순 · 도구 결함(원문 대조, 10-30)**
10. **부팅 블록 시각은 실제 시각이 아니다**: `1970-01-01 09:0x` 는 epoch 0(KST 09:00) = 부팅 순간에서 센 시계다. NM 줄 `Jan  1 09:03:04 … [184.3686]`(부팅 뒤 184 s)과 mon.log `2026-09-23 09:00:56 SNAPSHOT event_19700101_090401` 로 맞추면 **실제 = 1970 표기 − 3 분 4 초**(부팅 08:56:56). 그래서 §0.1 의 '9:00:50 · 9:01:41 · 9:03:21' 은 실제 ≈ 08:57:46 · 08:58:37 · 09:00:17 이고, ALOPS 전환은 ≈ 09:00:54. §0.1 제안 ③ 의 '08:57~09:03' 은 끝이 3 분 늦다(공유기 임대 표를 볼 때는 08:57~09:01).
11. **'매번 DHCP 응답이 없어 45 s 뒤 실패'**: 45 s 타임아웃 · `ip-config-unavailable` 줄은 **세 번째 시도만** 원문에 있다(`job530` 이 `tail -50`). 앞 두 번은 mon.log EVENT 쌍(09:00:50 → 09:01:26, 09:01:41 → 09:03:06 — 15 s 폴링이라 ±15 s)으로만 보인다.
12. **§11 'rx 390~780 · 신호 −56'**: `j543` 은 11:50~12:05 rx 6.0 · 175.6 · 1.0 을 포함한다(위 표). 신호 −55~−58. 끊김 전 4 분의 rx 변화가 SUMMARY 에 빠졌다.
13. **§11 의 뒤쪽은 '09-15~17 서명' 하나가 아니다**: reason 2 · 23 뒤 12:05:23 링크가 다시 올라왔고(재인증은 그 사이 성공), 이어서 **DHCP 45 s 무응답 → `ip-config-unavailable`** — 아침의 양상 ⓒ 가 같은 사건 안에서 이어졌다(`j542` NM 줄). 09-18 §6 의 'ⓐ 끊김과 ⓑ 재인증 거부는 다른 원인일 수 있다' 에 ⓒ 까지 한 사건에 나온 사례.
14. **`job542` 의 mon.log 절은 날짜를 거르지 않는다**: `awk '$2>="11:55:00" && $2<="12:08:00"'` 가 시각 열만 비교해 09-18 · 09-21 같은 시각 줄이 먼저 나오고 `head -30` 에서 잘렸다 → 09-23 줄이 하나도 없다. 09-23 LINK 는 `job543` 으로 다시 뽑았다.
15. **12:05 사건에 wifi-mon 스냅샷이 없다**: 15 s 폴링 순간(12:05:08 · 12:05:30)마다 bssid 가 AP 로 찍혀 'bssid 변화' 가 한 번도 안 잡혔다 → EVENT · SNAPSHOT 0. 09-18 §7.3 판정 기준이 기대던 '사건 순간 debug 400 줄' 이 없다. `wpa_debug.log` 자체는 있었으나 4-way 단계 줄을 뽑지 않았고, 원본 사본(`wifi_mon_0923/`)은 소실. 설계 결함(끊김이 15 s 보다 짧게 끝나면 안 잡힘).
16. **PC 쪽 수치 원문 없음**: §11 '11:57 부터 무응답 · 11:59:29 · 12:01:25 잠깐 응답 · 12:06:12 안정', §12 '≈ 15 s', §18 '14:13 · 14:25~14:36' 은 PC 쪽 핑 기록이 저장되지 않았다. 또 11:57 에 172.30.1.8 을 같이 핑한 것은 그때 Jetson 이 WEB_DEV(.101)에 있었으므로 판별력이 없다(응답했다면 다른 기기).
17. **§12 의 '같은 시각 Jetson 은 게이트웨이 핑 성공 → PC 쪽 경로'**: 게이트웨이 192.168.0.1 은 WEB_DEV AP 자신(ARP 항목 MAC = AP BSSID)이다. 따라서 이 시험은 'Jetson ↔ AP' 구간만 보증하고, 'AP ↔ PC 쪽 공유기 WAN(.6)' 구간과 'PC 쪽 공유기 내부' 구간은 가르지 못한다.

### 5.3 7 기 (10-14 · 10-15) — 내 실수 · 기록 어긋남
1. **'접속 전 신원 확인' 이라 적은 것은 로그인 뒤 확인**(10-15 §1.1) — 하려 한 것: 새 주소 .110 이 이 Jetson 인지 확인 · 본 것: `chk_after_reboot.sh` 결과(호스트 이름 · L4T · 작업 폴더 · 지도 파일) · 처음 추론(SUMMARY): '접속 전 신원 확인' · 의심한 이유(11-03 카드 작성): 스크립트 본문이 `hostname` · `/etc/nv_tegra_release` · `~/ros2_ws` 를 **원격 쪽에서** 읽는다 — 실행하려면 이미 비밀번호로 로그인해야 한다 · 결론: 10-14 §8.4 가 걱정한 '주소를 빼앗긴 채 비밀번호 전송' 을 이 확인은 막지 못한다. 그날은 사용자가 방금 .110 을 예약했다고 알려 위험이 낮았을 뿐 · 다음에 알아보는 법: 인증 없이 할 수 있는 것은 호스트 키 비교뿐 — Jetson 호스트 키를 한 번 저장해 두고(`ssh-keyscan` 결과) 접속 전에 같은지 본다(10-14 §8.4 '비교할 키를 저장해 둔 적이 없다' — 11-03 까지 저장 기록 없음) · 스크립트 핵심(`2026-10-15/jobs/chk_after_reboot.sh` 3 행): `echo "호스트 $(hostname) · $(head -1 /etc/nv_tegra_release …) · ros2_ws $( [ -d ~/ros2_ws/src/rover_navigation ] && echo 있음 …)"` · 나온 결과: 원천 소실(SUMMARY §1.1 서술뿐) · 데이터: 위 스크립트 · TOOLS 10:1x 줄.
2. **10-14 §8.5 의 신원 판단 근거가 약했다** — 포트 8765 연결 4/4 · 호스트 키 2/4(같은 키)를 'Jetson' 근거로 삼았지만, 비교할 Jetson 키가 없으니 '같은 키' 는 '그 주소에서 같은 기계가 두 번 답했다' 일 뿐이다. 그 직후 ping 은 전부 실패해 포트 성공이 WSL 쪽 착시였을 가능성도 SUMMARY 가 적음. 결과적으로 전송은 TCP 단계에서 실패(No route to host). 데이터: SUMMARY §8.5 · TOOLS 11:0x(출력 원문 없음).
3. **출력 원문 없음** — §8.3 ping · §8.5 포트 · 호스트 키 · SSH 시도 · 10-15 §1 ping/ARP · `chk_after_reboot.sh` 출력이 모두 대화에만 있었다(SUMMARY · TOOLS 서술이 전부). README §2.3 의 `| tee` 규칙 전(11-02) 기록.

## 6. 남은 것 (09-03 시점)
- 원인 — 절전 · 공유기 ARP · 드라이버 중 무엇인지 미확정. 이후 양상이 다른 사건들이 이어짐(§2 이후 목록).
- 절전 설정이 프로파일별이라는 점(다른 SSID 로 붙으면 다시 켜짐).
- 주행 중 원격 정지 수단 없음.

### 6.1 남은 것 (09-18 시점)
- 원인 미확정: ⓐ 끊김(DFS?) ⓑ 재인증 거부(PMF?) — wifi-mon 계측 결과 대기(§4.1 판정 기준).
- 절전: ALOPS 프로파일은 여전히 절전 켜짐(§17.5) — 제안만, 미적용. 국가 코드 00.
- IP 가 바뀌면 DDS 가 갈리는 구조 — 루프백 한정은 보류([DDS 공유메모리 사고](dds-shm-incident.md)). 대응은 '전체 재기동 + 보드 리셋' 운용뿐.
- `/var/log/syslog` 무회전(logrotate 미설치) — 분석 때마다 144 MB 를 훑음([저장 공간 카드](storage-housekeeping.md) 보류 ①).
- 위 §5.1 모순 1 · 3(시각) — NTP 전 시각을 판정에 쓰지 않도록 `uptime` · NTP 동기 줄과 대조하는 절차가 필요(09-21 §0 에서 같은 주의를 다시 적음).

### 6.2 남은 것 (09-23 시점)
- 양상 ⓒ(결합 · 4-way 성공 뒤 DHCP 45 s 무응답)의 원인 — **미확인**. 공유기 DHCP 임대 표 확인(§0.1 제안 ③)은 기록이 없다. 같은 날 12:05 사건 안에서도 ⓒ 가 다시 나왔다(§5.2 모순 13).
- IP 충돌 가설 — 09-23 에는 **판별 안 됨**: `arping -D` 검사가 실행 중 서비스에 걸리지 않았다(§5.2 실수 3). 서비스 재시작 · 새 블록 동작 확인이 남음. (이후 10-14 사용자가 다른 서버의 .101 사용을 찾음 — §2 이후 목록.)
- 양상 ⓓ(링크 유지 중 PC 와의 트래픽만 ≈ 8 분 끊김) — 'AP 가 전달을 멈췄다' 는 **추정**. 그 창의 Jetson → 공유기 핑이 없었다(트레이스는 12:06 부터). wifi-mon 에 게이트웨이 핑 상시화는 제안만(sudo · 사용자 결정).
- 양상 ⓔ(12:19, 14:13, 14:25~14:36) — PC → PC 쪽 공유기(NAT, WAN .6) → WEB_DEV AP → Jetson 경로 중 어느 구간인지 **미확인**. 게이트웨이 핑 대상 192.168.0.1 이 WEB_DEV AP 자신이라 'AP ↔ .6' 구간을 못 가른다(§5.2 모순 17). PC 쪽 핑 기록은 저장 안 됨(모순 16).
- AP 격리 추정(§14, PC 를 WEB_DEV 에 직접 붙이면 Jetson ARP 불가) — 해제는 사무실 공유 공유기라 사용자 결정 대기.
- 끊김 · 재연결 뒤 DDS 부하(n62b CPU 422 %) — 규칙(재연결 뒤 스택 재기동)만 있고, 게이트에 'NM 재연결 0' 검사는 미구현(제안).
- wifi-mon 이 15 s 보다 짧은 bssid 변화를 못 잡는 설계(모순 15) — 그대로.

### 6.3 남은 것 (10-15 시점)
- 09-23 · 10-07 의 'DHCP 무응답'(ⓒ)이 같은 주소 충돌이었는지 — `wifi_mon` `ARP_DUP` 기록 확인 안 함(10-14 §8.4 가 방법만 적음).
- 09-15~17 형(AP deauth · 재인증 거부)의 원인 — 그대로 미확정.
- Jetson 호스트 키 저장 · 접속 전 비교 — 안 함(§5.3 실수 1). 지금 스크립트들은 여전히 `StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null` 로 비밀번호를 보냄(예: [`2026-10-14/jobs/run_detached.sh`](../debug_log/2026-10-14/jobs/run_detached.sh) 6 행).
- 예약 주소(.110)도 다른 기기가 스스로 같은 주소를 쓰면 막지 못한다(§9 'DHCP 예약 vs 정적 IP') — 10-14 와 같은 충돌이 다시 날 수 있음.
- **옛 주소 기본값이 남은 곳(11-03 확인)**: `Docs/tools/` 에는 없음 — [`up_tools.sh`](../tools/up_tools.sh) 3 행 `H=${JETSON_HOST:-192.168.0.110}`(11-02 수정). `ros2_ws/` 는 주석만(`rover_bringup/config/fastdds_udp_only.xml` 37 행 · `rover_bringup/scripts/display_info_pub.py` 4 행 — 예시 문자열). 날짜 사본: `2026-10-14/jobs/run_detached.sh` 4 행 · `2026-10-21/jobs/put_one.sh` · `2026-10-21/jobs/run_f0.sh` · `2026-10-27/jobs/run_f0.sh` 의 `${JETSON_HOST:-192.168.0.101}`. **PC 스크래치패드의 실행본 `run_f0.sh` 4 행도 `192.168.0.101`** — `run_f2c.sh`(12 행 `.110` export)를 거치면 문제없지만, `run_f0.sh` 를 직접 부르면 옛 주소(지금은 다른 기기일 수 있는 주소)로 비밀번호를 보낸다.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job7g` | 재부팅 vs 단절 판별 | 08-28, 해설은 [첫 SLAM 지도 §8](first-slam-map.md#8-도구-해설) |
| `job7h` · `job7i_launch` · `job7j` · `job7k` · `job7k_launch` | 정지 확인 · detach 실행 · 로그 확인 | 08-28, 해설은 [첫 SLAM 지도 §8](first-slam-map.md#8-도구-해설) (아래에 요점만) |
| `wifi_diag.sh` · `wifi_diag2.sh` · `wifi_fix.sh` | 09-03 진단 · 절전 끄기 | `2026-09-03/jobs/` |
| mp2 | 09-15 끊김 때 주행(시작 여부 미확인) | 09-15 §3 |
| `run_recon.sh` · `job323_state.sh` | 끊긴 뒤 복구 감시 · 상태 확인 | `2026-09-15/jobs/` |
| `run_usb.sh` · `job324_diag.sh` · `job325_post_incident.sh` | USB 주소로 접속 · 부팅/로그 진단 · 전날 사건 조회 | `2026-09-15/jobs/`(09-16 오전 실행) |
| `job326_net_fix.sh` · `run_lan.sh` | mavlink-router 끄기 · 우선순위 · WEB_DEV 복귀 / 172.30.1.8 러너 | `2026-09-15/jobs/` |
| `job350_disc.sh` · `run_alt3.sh` | 09-16 DDS 분리 확인 · syslog 15:5x | `2026-09-16/jobs/` |
| `job401_whydrop.sh` · `job402_ddssplit.sh` | 09-17 끊김 직후 상태 · DDS 분리 확인 | `2026-09-17/jobs/` |
| `job427_wifi.sh` · `job427b` · `job427c` · `job427d` (+ `run_j427*.sh`) | 읽기 전용 Wi-Fi 분석 4 종 | `2026-09-17/jobs/` → `outputs/j427*_wifi.txt` |
| `job428_wifi_dfs.sh` · `job428b_now.sh` · `job428c_bss.sh` · `job428d_pmf.sh` (+ `run_j428b/c/d.sh`) | DFS · 비콘 · PMF 확인 | `2026-09-18/jobs/` → `outputs/j428*.txt` |
| `job429_probe.sh` · `job429b` ~ `job429j` (+ `run_j429*.sh`) · `wifi_mon.sh` | A 안 사전 점검 · 설치 · 고장 추적 · 재배포 · 스냅샷 시험 | `2026-09-18/jobs/` → `outputs/j429*.txt` |
| `run_jx.sh` · `run_xfer_all_h.sh` | 09-23 범용 러너(두 IP 자동 선택) · 재부팅 뒤 `/tmp` 재전송(호스트 변수판) | `2026-09-23/jobs/` |
| `job529_wifi_collect.sh` · `job530_wifi_boot.sh` | 09-23 아침 끊김(ⓒ) 회수 — wifi-mon · syslog · 부팅 블록 | `2026-09-23/jobs/` → `outputs/j529_wifi.txt` · `j530_wifi_boot.txt` |
| `job534_netprep.sh` · `job535_net_fixed.sh` + `run_j535.sh` · `job536_moncheck.sh` | 고정 IP(예약) 복귀 사전 확인 · 적용(arping · DAD · wifi-mon 패치 · WEB_DEV 전환) · 적용 확인 | → `j534_netprep.txt` · `j535_net.txt` · `j536_moncheck.txt` |
| `job539_dropchk.sh` · `job540_trace.sh` + `run_j540.sh` · `job541_fetch.sh` | 11:57 끊김 직후 요약 · 온보드 30 분 트레이스 · 회수 | → `j539_drop.txt`(뒷부분이 `job541` 출력) · 트레이스 원본 `/tmp/j540_trace.txt`(원천 소실, 발췌는 `j539` · `j544`) |
| `job542_dropwin.sh` · `job543_mon.sh` · `job544_drop2.sh` | 11:55~12:07 창 전체 · 그 창 mon.log · 12:19 두 번째 끊김 | → `j542_dropwin.txt` · `j543_mon.txt` · `j544_drop2.txt` |
| n62b | 끊김 뒤 이미 떠 있던 스택으로 돈 주행(CPU 422 %) | `outputs/j507_n62b_drive.txt` · `bags/bag_n62b.tgz` |
| `put_one.sh` · `run_detached.sh`(10-14) | 끊기는 동안 한 파일 전송 · 재시도 전송 + `setsid nohup` 실행 + 재시도 회수 | PC 스크래치패드(저장 사본 `2026-10-21/jobs/put_one.sh` · `2026-10-14/jobs/run_detached.sh`) |
| 포트 8765 연결 · `ssh-keyscan`(10-14 §8.5) | 자격 정보 없는 신원 확인 | 명령만(스크립트 · 출력 원문 없음) |
| `up_tools.sh`(10-14 §8.6) | 재부팅 · 복구 뒤 도구 일괄 전송 | `Docs/tools/up_tools.sh` |
| `chk_after_reboot.sh`(10-15 §1.1) | 재부팅 뒤 신원 · `/tmp` · 컨테이너 · 망 확인 | `2026-10-15/jobs/`(출력 원천 소실) |

## 8. 도구 해설
공통: Jetson 에서 실행, PC → WSL → sshpass 러너(원본 소실, 후손 [`2026-10-08/jobs/run_jn.sh`](../debug_log/2026-10-08/jobs/run_jn.sh)). 09-03 도구는 이름이 번호(job)가 아닌 용도 이름인 첫 예(도구 이름 규약이 정식으로 생긴 것은 10-12).

### job7g · job7h — 단절 판별 · 정지 확인 (08-28) — 요점
- `job7g`: uptime · 부팅 시각 · `last -x` · ROS 프로세스 수 · agent Up 시간 · 보드 토픽 · HID 모듈 · `iwconfig` 신호. 재부팅이면 uptime 이 짧고 노드 · agent 가 사라진다는 논리. 출력 [`job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt). 한계: 신호는 '지금' 값.
- `job7h`: 회전 프로세스 패턴 `pkill` → 빈 `/cmd_vel` 8 회 → 실제 속도 → `/cmd_vel` 무발행 확인. 끊긴 뒤 '로버가 정말 서 있나' 를 원격으로 확인하는 첫 도구.

### job7i_launch → job7k_launch + job7k — detach 실행 (08-28) — 요점
- v1(`job7i_launch`): `setsid nohup bash /tmp/job7f.sh > /tmp/spin.log 2>&1 &`. 결과: 로그 빈 채 · 회전 안 함(원인 미확인). python 출력 버퍼링(`-u` 없음), stdin 미분리, `disown` 없음이 차이.
- v2(`job7k_launch` → `job7k`): 실행기는 `setsid bash /tmp/job7k.sh </dev/null >/dev/null 2>&1 &` + `disown` + 6 s 뒤 프로세스 수 · 로그 5 줄. 코어는 `exec >>/tmp/spin.log 2>&1` 로 자기 출력을 로그에, `python3 -u` · `flush=True`, 2 s 마다 진행 줄, 시작 · 끝 시각.
- 확인: `job7j`(로그 · 프로세스 · ω · 지도 · uptime · 세션)를 끊김과 무관하게 아무 때나 실행.
- 계보: 이 형태가 이후 모든 주행 러너의 뼈대(09 월 `run_detached` · 10 월 `run_jn.sh` · `/tmp/live/current.log` 실시간 로그 — 다음 시기).

### wifi_diag.sh — 무선 상태 진단 (09-03, 읽기 전용)
- 왜: ping 이 수 분씩 죽는데 Jetson 은 살아 있는지, 링크가 끊긴 건지.
- 하는 일: ① `iw dev` 에서 첫 인터페이스 이름(`wlP1p1s0`) · `uptime -p` ② `iw dev <IF> link` 의 SSID · signal · freq · rx/tx bitrate ③ `iw dev <IF> get power_save` ④ `nmcli -t -f DEVICE,STATE,CONNECTION dev status` 에서 그 장치 줄, 그 연결의 `802-11-wireless.powersave` · `connection.autoconnect-retries` ⑤ `journalctl -u NetworkManager --since "20 min ago"` 에서 disconnect · deactivat · activated · roam · auth · dhcp4 주소/임대 줄 마지막 12 ⑥ `dmesg` 에서 wlan · rtw · rtl88 · iwlwifi · brcm · wlP 마지막 8 ⑦ `ip -4 -br addr show <IF>`.
- 출력: 원문 없음(대화에만). SUMMARY 에 옮긴 것: WEB_DEV_5G · ch36 · −53 dBm · NM 끊김 로그 없음 · 커널 로그 없음 · **Power save: on**.
- 쓰인 곳: '링크는 유지 · 절전 켜짐' → `wifi_fix.sh`.
- 결함: NM 로그 20 분 창은 사건 시각을 정확히 덮는지 확인 안 함. `dmesg` 는 sudo 없이 실행 — 커널 설정에 따라 일반 사용자에게 막힐 수 있다(그 경우 '로그 없음' 과 '못 읽음' 이 같은 빈 출력, **추정**).
- 계보: → 09-17 `job427*_wifi.sh`(syslog 전체에서 deauth · reason 코드) → 09-18 `job428_wifi_dfs.sh` → 09-23 `job529_wifi_collect.sh`(다음 시기).
- 지금 다시: 그대로 쓸 수 있음. 지금은 `/var/log/wifi_mon/` 계측 기록이 더 낫다.

### wifi_diag2.sh — 연결 세부 · 트래픽 (09-03, 읽기 전용)
- 하는 일: ① `iw dev wlP1p1s0 station dump` 의 inactive · rx/tx packets · tx retries · tx failed · beacon loss · rx drop · signal · bitrate · connected time ② `nmcli dev wifi list --rescan no` 에서 같은 SSID(WEB_DEV) 의 AP 목록(로밍 후보 — BSSID · 채널 · 신호) ③ `journalctl -k --since "30 min ago"` 에서 무선 · deauth · disassoc · beacon 줄 ④ `ip neigh show dev wlP1p1s0`(게이트웨이 ARP 상태) ⑤ `/proc/net/dev` 를 5 s 간격 두 번 읽어 rx/tx kB/s ⑥ 실행 중 큰 노드(foxglove · controller_server · slam · ekf · rplidar · realsense) ⑦ `ss -tn state established` 외부 피어(예: Foxglove 8765 에 붙은 PC).
- 출력: 원문 없음. SUMMARY 에 옮긴 것: AP 1 개(로밍 아님) · 커널 로그 없음 · 트래픽 ≈ 0.
- 쓰인 곳: '로밍 · 트래픽 포화 · 커널 오류' 를 배제.
- 결함: tx retries/failed · beacon loss 수치는 SUMMARY 에 안 옮겨져 **원천 소실**.

### wifi_fix.sh — 절전 끄기 (09-03, sudo · 사용자 고지)
- 하는 일: 현재 연결 이름을 `nmcli -t -f DEVICE,CONNECTION dev status` 로 찾고 → `sudo iw dev wlP1p1s0 set power_save off`(런타임) → `sudo nmcli con modify "<연결>" 802-11-wireless.powersave 2`(영구; 2 = 끔) → 확인 줄 'power_save now: … NM(영구): …'. 비밀번호는 `<PW>` 로 가림.
- 출력: 원문 없음. 효과 수치는 §2 표(SUMMARY 문장).
- 알려진 결함: **그 순간 연결된 프로파일(WEB_DEV_5G)에만** 영구 적용 — 다른 SSID 로 자동 전환되면 절전이 다시 켜진다(09-17 §17 에서 실제로 확인). 적용 전 기준선 측정이 없다(§5).
- 되돌리기: `nmcli con modify <연결> 802-11-wireless.powersave 0`(기본값 = 전역 설정 따름) · `iw … power_save on`.
- 지금 다시: 쓸 수 있음. 쓸 때는 모든 무선 프로파일에 같이.

### 8.1 3 시기 도구 (09-15 ~ 09-18)
공통: PC(WSL) 러너가 스크래치패드의 Jetson 스크립트를 `tr -d '\r'` 로 줄끝을 고친 뒤 `sshpass … scp` 로 `/tmp` 에 올리고 `ssh "bash /tmp/<스크립트>"` 로 돌린다. 09-15 러너의 원본 폴더(`82ce61d4…/scratchpad`)는 09-28 에 사라졌고 저장소 사본만 남음. 09-18 러너(`run_j428*` · `run_j429*`)는 sudo 비밀번호를 원격 명령줄 환경변수 `SPW=<PW>` 로 넘기고 스크립트 안 `S() { echo "$SPW" | sudo -S -p '' "$@"; }` 로 쓴다 — 저장소 사본은 가려져 있지만, 실행 순간 Jetson 프로세스 목록에 평문이 보이는 방식이다(보안 메모, [저장 공간 카드](storage-housekeeping.md) 보류 ③과 같은 줄기).
도구 계보: `wifi_diag*`(09-03) → `job324` · `job325`(09-16, 전날 syslog 창) → `job427` ~ `job427d`(09-17, syslog 전체 · 집계) → `job428*`(09-18, DFS · PMF) → `job429*` + `wifi_mon.sh`(상시 계측) → 09-23 `job529_wifi_collect.sh` · `job535_net_fixed.sh`(arping 패치) → 10-22 `chk_wifi_1022.sh`.

#### run_recon.sh — 복구 감시 (09-15, PC/WSL)
- 부른 형태: `bash run_recon.sh [시도 수=12]`. 왜: 끊긴 Jetson 이 돌아오면 바로 상태를 보려고.
- 하는 일: 5 s 마다 `ping -c 1 -W 2 192.168.0.101` 최대 N 회 → 응답하면 시각 출력 + `job323_state.sh` 를 올려 실행 → 아니면 '핑 실패 (N×5 s)'.
- 출력: 원문 없음. 결함: **옛 주소 하나만 두드림** — 이것이 §5.1 실수 1 의 도구 쪽 원인. 지금 다시: 쓰지 않음(→ 러너의 IP 자동 선택, 09-23 `run_jx.sh`).

#### job323_state.sh — 주행 흔적 확인 (09-15, Jetson)
- 하는 일: uptime · 주행 프로세스(s4run · avoid3 · bag record) 개수 · `/cmd_vel` hz 3 s · 휠 odom 선속도 · `tf2_echo map base_link` · `/tmp/nav2.log` 의 목표 줄(Received goal · succeeded/failed · Aborting) 4 개 · `/tmp/bag_mp2` 유무('없음 → 주행 시작 안 됨').
- 출력: 원문 없음. 09-16 엔 재부팅으로 `/tmp` 가 비어 판정 불가. 결함: bag 없음 = 시작 안 함 은 '재부팅 없음' 이 전제. 지금 다시: 형태만 참고.

#### run_usb.sh — USB 장치 모드 링크 진단 (09-16 오전, PC/WSL)
- 왜: Wi-Fi 두 주소가 다 안 될 때 Jetson 의 USB 가상 이더넷(192.168.55.1)으로 들어가려고. 사용자가 본 '로그인 직후 Connection reset' 재현도.
- 하는 일: ping 5 회 · TCP 22 배너 40 바이트(`/dev/tcp`) · ssh 3 회(`LogLevel=INFO` 로 stderr 포함, 각 25 s 제한) · `job324_diag.sh` 를 `bash --noprofile --norc` 로 실행(.bashrc 의심 배제).
- 출력: 원문 없음. 결과(SUMMARY): 3/3 성공 · 재현 안 됨. 지금 다시: 쓸 수 있음(USB 케이블이 PC 에 꽂혀 있을 때).

#### job324_diag.sh — 부팅 · 셸 · 네트워크 진단 (09-16, Jetson, sudo 없음)
- 하는 일: uptime · `free -m` · nproc → `~/.bashrc` 꼬리 25 줄 · `.profile` 류 → `journalctl -b -1 -p 3`(이전 부팅 오류) · OOM/hung/thermal/watchdog/무선 키워드 · 이전 부팅 마지막 20 줄 → 이번 부팅 오류 → `nmcli` 장치 · 활성 연결 · `ip -4 -br addr` · `iw dev` · 절전 → docker · 큰 ROS 프로세스 → sshd 로그 6 줄.
- 출력: 원문 없음. SUMMARY 에 옮긴 것: 766 MB/6.6 GB, journal 비영속(이전 부팅 못 봄), `.bashrc` 정상(`source ~/px4_ws/install/setup.bash` 추가), sshd `kex_exchange_identification`. 결함: `iw dev wlan0 get power_save` 는 인터페이스 이름이 틀림(`wlP1p1s0`) → 빈 출력. 지금 다시: 쓸 수 있음.

#### job325_post_incident.sh — 전날 사건 조회 (09-16, Jetson)
- 하는 일: `/tmp` 의 bag · 로그 잔존 → 전날 nav2 목표 줄 → **`/var/log/syslog` 의 `Sep 15 13:`~`14:` 줄 중 NM · wpa_supplicant 이벤트 20 줄** → 같은 창의 OOM · reboot · thermal 8 줄 → mavlink-router 상태 · micro-ROS 컨테이너 → 직렬 장치.
- 출력: 원문 없음. SUMMARY §3.1 의 14:03:13 reason 2 · 14:03:21 AUTH_FAILED · mavlink-router 크래시 루프 · 직렬 장치 없음이 여기서 나옴. 결함: `head -20` 이라 14:03~14:04 의 연속 실패 줄에서 잘려 **14:04:51 ALOPS 연결 줄까지 못 감**(추정 — 9 월 타임라인으로 보면 14:03:13 부터 20 줄째가 14:04 무렵) → 실수 1 의 직접 원인 후보. 지금 다시: 창 · 줄 수를 넓혀 쓸 수 있음.

#### job326_net_fix.sh — mavlink-router 끄기 · 우선순위 · WEB_DEV 복귀 (09-16 09:36, Jetson, sudo · 사용자 승인)
- 부른 형태: `bash job326_net_fix.sh <PW>`(첫 인자로 비밀번호).
- 하는 일: ① `systemctl disable --now mavlink-router` · 상태 확인 ② `nmcli con modify WEB_DEV_5G connection.autoconnect-priority 20` · ALOPS 5 · 목록 출력 ③ **nohup 으로 5 s 뒤** `nmcli con up WEB_DEV_5G` → `/tmp/nm_switch.log` 에 결과 · IP · 장치 상태(전환 순간 ssh 가 끊겨도 끝나게).
- 출력: 원문 없음, `/tmp/nm_switch.log` 는 **원천 소실**. 결과(SUMMARY): .101 복귀. 결함: nohup 줄 안에 비밀번호가 평문으로 들어가 Jetson 프로세스 목록에 남음. 계보: 09-23 `job535_net_fixed.sh`(DHCP 예약 · arping). 지금 다시: 우선순위 부분은 그대로 쓸 수 있음.

#### run_lan.sh — 172.30.1.8 러너 (09-16, PC/WSL)
- 하는 일: `JETSON_HOST`(기본 172.30.1.8)로 ping 2 · ssh `SSH_OK; uptime` · 인자로 받은 스크립트 업로드 · 120 s 실행 · 종료 코드 출력. 접속 시험을 먼저 하는 러너의 첫 형태. 계보 → `run_jn.sh`(10-08, `JETSON_HOST` 환경변수 관례가 여기서 시작).

#### job350_disc.sh · run_alt3.sh — 09-16 IP 전환 뒤 분리 확인 (Jetson)
- `job350_disc`: IP 목록 · agent 로그 · sensors/nav2 로그 끝 · **새 셸에서 옛 노드 토픽 수신 시험**(`/wheel_odom` · `/scan` `--once` 6 s, 헤더 개수) · 주요 프로세스 시작 시각 → 'wifi 전환 16:00:58'. 결과: 옛 노드 데이터 0. 출력 원문 없음.
- `run_alt3`: syslog 09-16 15:55~16:01 의 wpa_supplicant · `wlP1p1s0` 줄 10 개 + 다른 분석(job345). 출력 원문 없음.

#### job401_whydrop.sh · job402_ddssplit.sh — 09-17 끊김 직후 (Jetson)
- `job401`: 호스트 · uptime · IP · 현재 SSID → syslog `Sep 17 13:3[0-7]` 의 무선 줄 8 개 → 스택 프로세스 개수 → 로그 줄 수. **창이 13:30~13:37** 이라 13:38:42 reason 2 를 못 담는다 — SUMMARY '13:35:45' 의 출처일 수 있으나 출력이 없어 **미확인**.
- `job402`: UDP 전용 DDS 프로파일로 `ros2 daemon stop` 뒤 5 토픽 hz 7 s · `map→base_link`. 결과: 전부 안 보임. 출력 원문 없음.

#### job427_wifi.sh — Wi-Fi 상태 · syslog 전체 (09-17, Jetson, 읽기 전용 · sudo 없음)
- 부른 형태: `run_j427.sh`(호스트 기본 172.30.1.8, 180 s 제한). 왜: 사용자 요청 '끊기는 이유 · 새 IP 로 붙는 이유'.
- 하는 일: ① 현재 링크(`iw link`) · 절전 · IPv4 · 경로 · 드라이버(`/sys/class/net/<IF>/device/driver`)와 모듈 · MAC · `iw reg get` ② 저장 연결 목록(자동연결 · 우선순위) · 무선 프로파일마다 autoconnect · ssid · band · bssid · powersave · key-mgmt · pmf · ipv4.method(**psk · password · secret 줄은 grep -v 로 제거**) · NM conf 의 `wifi.` 줄 ③ 주변 AP 캐시 스캔 25 줄 ④ 10 s 동안 `/sys/class/net/<IF>/statistics` 의 tx/rx 바이트 · 패킷 · 멀티캐스트 · 드롭 · 오류 증가, 목적지별 소켓, 멀티캐스트 가입 그룹 ⑤ `last -x reboot` ⑥ **모든 `/var/log/syslog*` 에서 무선 이벤트 정규식**(CONNECTED · DISCONNECTED · TEMP-DISABLED · ASSOC/AUTH-REJECT · BEACON-LOSS · 4-Way 실패 · NM 활성화/상태/DHCP · reason=N), 파일당 150 줄 ⑦ dmesg · kern.log 무선 줄 30.
- 출력: [`j427_wifi.txt`](../debug_log/2026-09-17/outputs/j427_wifi.txt). 쓰인 곳: §17.3 트래픽 · §17.5 절전 · 국가 코드 · 링크 품질.
- 결함: ⑥ 이 파일당 150 줄이라 2 월부터 한 파일인 syslog 에선 앞쪽만 나옴 → 9 월은 `job427b` 로 다시. 지금 다시: 쓸 수 있음(읽기 전용).

#### job427b_wifi.sh — 9 월 타임라인 · 새 스캔 (09-17, Jetson)
- 하는 일: A syslog 크기 · 첫 줄 → B **9 월 1~19 일** wpa_supplicant 전 이벤트 + NM 핵심 줄을 `/tmp/wifi_sep.txt` 로 축약(호스트명 · PID 제거) → 그중 끊김 · 활성화 · DHCP · 실패 줄 220 개 → C 날짜별 DISCONNECTED(bssid · reason · locally_generated 개수) · TEMP-DISABLED · ASSOC-REJECT · 시작한 연결 → D `--rescan yes` 스캔 + `iw scan dump`(인증 방식 · MFP) → E `nmcli general` · NM · wpa_supplicant 버전 · `rtl88x2ce` 모듈 정보 · 드라이버 절전 파라미터.
- 출력: [`j427b_wifi.txt`](../debug_log/2026-09-17/outputs/j427b_wifi.txt). 쓰인 곳: §17.1 사건 표(세 사건의 줄 단위 순서) · 실수 1 판별.
- 결함: E 의 모듈 이름이 틀려(`rtl8822ce` 가 맞음) 드라이버 파라미터를 못 읽음(§5.1 모순 5). 줄은 파일 순서라 NTP 전 시각 줄이 섞여 시간순이 아닌 곳이 있다(모순 3). 지금 다시: 날짜 정규식만 바꿔 쓸 수 있음.

#### job427c_wifi.sh — 전체 기간 집계 · 끊김 ±90 s (09-17, Jetson)
- 하는 일: A `CTRL-EVENT-DISCONNECTED bssid=… reason=N( locally_generated=1)?` 를 전 기간 `sort | uniq -c` · AP 가 보낸 것(locally_generated 없음)만 날짜별 · `WRONG_KEY` · 4-Way 실패 날짜 · 연결 성공을 bssid × 월로 → B 세 reason 2 시각마다 같은 날 syslog 줄을 `date -d` 로 초로 바꿔 **−90 ~ +90 s** 줄(무선 반복 · 데스크톱 잡음 제외, 40 줄) → C 09-15~17 docker · veth 사건 시각(스택 기동과 끊김 대조).
- 출력: [`j427c_wifi.txt`](../debug_log/2026-09-17/outputs/j427c_wifi.txt). 쓰인 곳: §17.2 집계 표 · §17.3 드라이버 기각.
- 결함: B 는 40 줄 제한이라 09-15 창이 mavlink-router 재시작 줄로 거의 다 찼다(그 자체가 로그 잡음의 증거). 줄마다 `date` 를 부르는 awk 라 느림. 지금 다시: 쓸 수 있음.

#### job427d_wifi.sh — SSH 세션 빈도 대조 (09-17, Jetson)
- 하는 일: A syslog `systemd[1]: Started Session N of User jetson` 을 날짜별 · 10 분 칸별로 세어 날짜마다 총수 · 최대 10 분 칸 → B 세 끊김 전 60 분을 10 분 칸 7 개로 → C 09-14~17 WEB_DEV 연결 · reason 2 시각(유지 시간 계산용).
- 출력: [`j427d_wifi.txt`](../debug_log/2026-09-17/outputs/j427d_wifi.txt). 쓰인 곳: §17.3 SSH 기각 · §17.2 유지 시간. 결함: SUMMARY 는 09-17 만 인용(§5.1 모순 2). 지금 다시: 쓸 수 있음.

#### job428_wifi_dfs.sh · job428b_now.sh — DFS 흔적 · 현재 상태 (09-18, Jetson, 읽기 전용)
- 부른 형태: `run_j428b.sh` 가 둘을 올려 `job428b` → `job428`(400 s 제한) 순서로.
- `job428b`: 호스트 · uptime · 부팅 시각 · IPv4 · 링크(SSID · freq · 신호 · 비트레이트) · 절전 · 09-17 18:00 이후 무선 · NM 사건 40 줄.
- `job428`: A 8 월 25 일 ~ 9 월의 `STARTED-CHANNEL-SWITCH` · `CHANNEL-SWITCH` · `REGDOM-CHANGE` · `BEACON-LOSS` · `BSS-REMOVED` · DFS · Associated · CONNECTED 줄을 모아 종류별 개수(bssid 는 X 로) → B 세 reason 2 의 −60 ~ +20 s 무선 · 커널 줄 → C 정상 접속 전후의 채널 전환 줄 40 개.
- 출력: [`j428_wifi_dfs.txt`](../debug_log/2026-09-18/outputs/j428_wifi_dfs.txt). 쓰인 곳: §0 상태 · §4 정정(80 MHz 줄은 매 접속).
- 결함: **B 빈 출력**(§5.1 모순 4). `job428b` 의 '09-17 18:00 이후' 는 빈 출력 — 오늘 부팅 줄이 `Sep 17 16:37` 로 찍혀 창 밖(NTP 함정의 실례). A 의 종류별 표에 옛 호스트명 `alops-desktop` 줄이 따로 셈 → SUMMARY 의 42 · 15 는 `jetson-desktop` 줄만. 지금 다시: B 의 시각 변환을 고쳐야 함.

#### job428c_bss.sh · job428d_pmf.sh — 비콘 · PMF (09-18, Jetson, sudo 없음)
- `job428c`: `iw scan dump`(캐시)에서 AP(`…:1b:4c`) 블록의 freq · 신호 · Country · RSN(인증 · MFP) · HT/VHT/HE operation · CSA · Quiet 줄. 결과: VHT `channel width: 1 (80 MHz)` + seg1 42 · **seg2 50**(= 160 MHz 운용, §9 용어) · `MFP-capable` · Country KR. 출력 [`j428c_bss.txt`](../debug_log/2026-09-18/outputs/j428c_bss.txt). 한계: 'last seen 1684296 ms ago'(28 분 전 캐시).
- `job428d`: station dump(빈 출력 — 이 드라이버 미지원) · `wpa_cli status`(권한 거부) · `/run/wpa_supplicant` 권한 거부 · NM WEB_DEV 프로파일 key-mgmt · **pmf 0 (default)** · powersave 2 · 우선순위 20 · 드라이버 파라미터(모듈 이름 틀림). 출력 [`j428d_pmf.txt`](../debug_log/2026-09-18/outputs/j428d_pmf.txt). → 'PMF 는 sudo 없이 못 본다' → `job429_probe`.

#### job429_probe.sh — A 안 사전 점검 (09-18, Jetson, sudo · 설정 변경 없음)
- 부른 형태: `run_j429.sh job429_probe.sh`(공통 러너, `SPW` 로 sudo).
- 하는 일: 디스크 · syslog 크기 · logrotate 설정 목록 · `logrotate.timer` · cron 상태 → wpa_supplicant 실행 인자 → sudo 확인 → root `wpa_cli status`(psk · pmk 줄 제거) → `wpa_cli` 대화 모드에 `level 2`(debug) 를 파이프로 넣고 20 s 받으며 5 s 뒤 스캔 1 회 → 받은 줄 수 · `<수준>` 분포 → `iw scan freq 5180` 시간 · AP 블록.
- 출력: [`j429_probe.txt`](../debug_log/2026-09-18/outputs/j429_probe.txt). 결과: **pmf=1 · BIP** · 모니터 10 줄(수준 표시 0) · 136 ms · 160 MHz · `logrotate.timer inactive` · wpa_supplicant 실행 인자 `-u -s -O /run/wpa_supplicant`(`-s` = syslog 로 기록 — DEBUG 줄이 rsyslog 를 거치므로 rsyslog 규칙으로 따로 뺄 수 있었던 근거).

#### job429b_montest.sh · job429c_dbgrate.sh — 모니터 재시험 · DEBUG 양 (09-18, Jetson, sudo)
- `job429b`: 같은 모니터 시험을 `stdbuf -oL -eL` 줄 버퍼로. 결과 10 줄 · 분포 빈칸 → **모니터 방식 기각**. 출력 [`j429b_montest.txt`](../debug_log/2026-09-18/outputs/j429b_montest.txt).
- `job429c`: 원래 수준(INFO) 저장 → `wpa_cli log_level DEBUG` → 10 s 뒤 스캔 · 50 s 더 → 원래 수준 복귀 · 확인 → syslog 줄 · 바이트 증가 → 하루 추정(×1440) · 스캔/기타 줄 수 · 발췌 15 줄(psk · PMK · PTK 제거). 결과 +79 줄 · +8 KiB · ≈11 MiB/일, 복귀 INFO. 출력 [`j429c_dbgrate.txt`](../debug_log/2026-09-18/outputs/j429c_dbgrate.txt). 결함: §5.1 모순 7(유휴가 아님).

#### wifi_mon.sh — 상시 계측 루프 (09-18 설치, Jetson root, systemd `wifi-mon.service`)
- 왜: 끊김이 하루 한 번꼴이라 **사람이 없을 때 그 순간의 AP 비콘 폭 · 핸드셰이크 단계를 남기려고**(§4.1 판정 기준을 가를 자료).
- 하는 일(15 s 루프): ① wpa_supplicant 수준이 DEBUG 가 아니면 다시 DEBUG(재시작 · 재부팅 뒤 INFO 로 돌아가므로) ② `iw dev wlP1p1s0 link` 에서 bssid · ssid · freq · 신호 · rx/tx 비트레이트, IPv4, `wpa_cli status` 의 wpa_state · pmf · key_mgmt → `mon.log` 에 `LINK …` ③ bssid 가 바뀌면(끊김 = none 포함) `EVENT bssid A -> B` + 스냅샷 ④ WEB_DEV AP(`…:1b:4c`)에 붙어 있으면 4 바퀴(60 s)마다 `scan_ap 5180` → `BEACON ap_freq · ap_sig · vht_w · seg1 · seg2 · ht2 · csa · quiet` ⑤ 다른 AP 이면 40 바퀴(10 분)마다 전체 스캔 → `BEACON_ALL`(WEB_DEV 가 보이는지 · 폭) ⑥ 240 바퀴(1 h)마다 크기 회전: `mon.log` > 50 MB · `wpa_debug.log` > 300 MB 면 `.1` 로 옮김(후자는 rsyslog HUP).
- `scan_ap`: `timeout 10 iw … scan freq 5180`(전체는 20 s), 실패하면 2 s 뒤 한 번 더, 그래도 실패면 `scan_err=…`. awk 로 AP 블록의 `* channel width` · `center freq segment 1/2` · 'Channel Switch'(Extended 제외) · Quiet 를 뽑음.
- 스냅샷 `event_<시각>.txt`: iw link · wpa_cli status(psk · pmk 제거) · IP · nmcli 장치 · 전체 스캔 AP 블록 80 줄 · `wpa_debug.log` 직전 400 줄(psk= · PMK · PTK 제거) · syslog wpa/NM 직전 80 줄.
- 짝 설정 `/etc/rsyslog.d/25-wifi-mon.conf`(`job429d` 가 씀): `$programname == "wpa_supplicant" and $syslogseverity == 7` → `/var/log/wifi_mon/wpa_debug.log` 에만 쓰고 `stop`(syslog 에 안 섞음). INFO 이상(CTRL-EVENT-*)은 그대로 syslog.
- 출력: Jetson `/var/log/wifi_mon/{mon.log, wpa_debug.log, event_*.txt}`(디렉터리 2750 syslog:adm — 읽으려면 sudo 또는 adm 그룹). 저장소 사본은 09-18 판 [`2026-09-18/jobs/wifi_mon.sh`](../debug_log/2026-09-18/jobs/wifi_mon.sh)(timeout 패치 포함). 09-23 원본 사본은 그날 스크래치패드 `wifi_mon_0923/`(git 제외 — 지금 남았는지 미확인).
- 계보: 09-18 첫 판 → 같은 날 timeout 패치(첫 스캔 98 s 막힘) → 09-23 `arping -D` 중복 IP 검사 · `ARP_DUP` 줄 · 5 분 1 회 스냅샷(`2026-09-23/jobs/job535_net_fixed.sh` 안의 패치). 
- 알려진 결함: AP BSSID · 주파수가 상수(망이 바뀌면 의미 없음 — §2 이후 목록) · 시각은 NTP 전엔 틀림(09-21 §0 첫 스냅샷이 부팅 결합을 '사건' 으로 잡음 — 부팅 첫 결합도 bssid none → AP 변화라 스냅샷이 남는 설계) · 60 s 마다 연결 채널 스캔은 링크에 짧은 지연을 줄 수 있으나 **미측정** · DEBUG 상시 유지로 wpa_debug 가 최대 300 MB × 2.
- 지금 다시: **설치돼 돌고 있음**(10-27 · 10-28 프로세스 목록). 되돌리기 명령은 §4.1.

#### job429d_install.sh — 설치 (09-18, Jetson, sudo · 사용자 승인)
- 부른 형태: `run_j429d.sh` — `wifi_mon.sh` 와 함께 올려 `bash -n` 문법 검사 통과 뒤 실행.
- 하는 일(`set -e`): `/var/log/wifi_mon` 생성(syslog:adm 2750) → `/usr/local/sbin/wifi_mon.sh`(0755) → rsyslog 규칙 파일 작성 · 설치 → `wifi-mon.service`(`Restart=always` · `RestartSec=10` · `Nice=10` · `After=wpa_supplicant NetworkManager rsyslog`) → `rsyslogd -N1` 검사 → rsyslog 재시작 · daemon-reload · `enable --now` → 75 s 뒤 상태 · 수준 · mon.log 12 줄 · wpa_debug 줄 수 · syslog 에 DEBUG 가 새는지 · 디렉터리 목록.
- 출력: [`j429d_install.txt`](../debug_log/2026-09-18/outputs/j429d_install.txt). 결과: active · enabled · DEBUG · LINK 1 줄. 결함: 75 s 동안 BEACON 줄이 없었는데(첫 스캔 막힘) 이 도구는 그걸 판정하지 않음 → `job429e` 로 발견. 'wpa_debug.log 0 줄' 은 권한 문제(§5.1 모순 8).

#### job429e_check.sh · job429f_trace.sh · job429g_tail.sh — 첫 스캔 막힘 추적 (09-18, Jetson, sudo)
- `job429e`: mon.log 8 줄 · 서비스 MainPID 의 자식 · 손자 프로세스(상태 · 경과 · wchan) · 단독 `iw scan freq 5180` 시간. 결과: 자식 · 손자가 01:38(98 s) 째 그대로, 단독 스캔 127 ms → '루프 안의 스캔이 막힘'. 출력 [`j429e_check.txt`](../debug_log/2026-09-18/outputs/j429e_check.txt).
- `job429f`: 루프 프로세스의 wchan · 열린 fd, `scan_ap` 함수만 `sed` 로 떼어 `bash -x` 20 s. 결과: 단독으로는 1 회 정상(`ap_freq=5180 … seg2=50 … csa=0`). 출력 [`j429f_trace.txt`](../debug_log/2026-09-18/outputs/j429f_trace.txt). → 원인 '다른 스캔과 겹침' 은 **추정**(그때 스캔하던 다른 주체 확인 안 함).
- `job429g`: mon.log 15 줄 · 프로세스 트리 · `journalctl -u wifi-mon` 6 줄. 출력 원문 없음.

#### job429h_redeploy.sh — timeout 패치 재배포 (09-18, Jetson, sudo)
- 하는 일: `bash -n` → 설치 → `systemctl restart wifi-mon` → 80 s 뒤 mon.log 8 줄 · wpa_debug 크기 · 수준 · 서비스 상태. 결과: 11:03:09 · 11:04:10 BEACON 정상 · 23,232 B · DEBUG · active/enabled. 출력 [`j429h_redeploy.txt`](../debug_log/2026-09-18/outputs/j429h_redeploy.txt).

#### job429i_snaptest.sh · job429j_secret.sh — 스냅샷 시험 · 비밀 검사 (09-18, Jetson, sudo)
- `job429i`: 설치본에서 `snapshot()` 함수를 떼어 'TEST' 로 한 번 실행 → 새 `event_*` 를 `test_` 접두로 바꿈 → 크기 · 절 머리 · 'psk= · passphrase= · password' 개수 · wpa debug 발췌. 결과 41,158 B · 7 절 모두 · 검사 1. 출력 [`j429i_snaptest.txt`](../debug_log/2026-09-18/outputs/j429i_snaptest.txt). 결함: 줄 수 0 은 권한(§5.1 모순 8).
- `job429j`: 그 1 건을 값 가림(`<MASK>`) 처리해 보여 주고 `wpa_debug.log` 전체의 psk= · passphrase= 줄 수. 출력 **원문 없음** — 'WPS Device Password ID 뿐' 판정은 SUMMARY 문장만(§5.1 모순 9).

### 8.2 4 시기 도구 (09-23)
공통: PC(WSL) → `run_jx.sh`(또는 전용 `run_j5xx.sh`)가 스크래치패드의 스크립트를 CR 제거 뒤 Jetson `/tmp` 로 scp → ssh 로 `bash /tmp/<파일>`. 모두 **읽기 전용**이고, `job535` · `job536` 만 sudo(비밀번호는 저장소 사본에서 `<PW>`). 시각 범위(11:5x · 12:17~12:21 등)를 코드에 박아 넣어 **다른 날엔 그대로 못 쓴다**.

#### run_jx.sh — 범용 러너 (09-22 작성 · 09-23 IP 자동 선택 추가, PC/WSL)
- 부른 형태: `[JETSON_HOST=…] [JX_TIMEOUT=300] bash run_jx.sh <job파일> [인자…]`.
- 왜: 아침에 Jetson 이 ALOPS(172.30.1.8)로 넘어가 있어 러너마다 주소를 손으로 바꿔야 했다(§0.1 제안 ②).
- 하는 일: `JETSON_HOST` 가 비었으면 192.168.0.101 → 172.30.1.8 순으로 `ping -c1 -W1` 해 처음 응답하는 쪽 → `tr -d '\r'` → scp(실패면 종료) → `.py` 면 `python3`, 아니면 `bash` 로 원격 실행(UDP 전용 Fast DDS 프로파일 · humble · 워크스페이스 source), 전체 `timeout 300`.
- 출력: 원격 화면 그대로. 결함: 두 주소 다 무응답이면 .101 로 시도해 실패. 핑 응답이 Jetson 인지 확인하지 않는다 — 10-14 처럼 다른 기기가 .101 을 쓰면 엉뚱한 기기에 접속을 시도한다(그때는 SSH 신원 확인 끔(`StrictHostKeyChecking=no`)이라 경고도 없음). 계보: → `run_jn.sh`(10-08, `JX_WHY` · 실시간 로그) · 지금은 `JETSON_HOST=192.168.0.110` 고정 관례.

#### run_xfer_all_h.sh — 재부팅 뒤 `/tmp` 스크립트 재전송 (PC/WSL)
- 하는 일: 옛 스크래치패드(82ce61d4…)의 job 35 개를 `JETSON_HOST`(기본 .101)로 scp(3 회 재시도) → 원격에서 CR 제거 · `chmod` · `py_compile`. 09-10 판 `run_xfer_all.sh` 의 IP 고정만 변수로 바꾼 것. 결함: 옛 스크래치패드는 09-28 에 사라져 지금은 못 쓴다.

#### job529_wifi_collect.sh — 아침 끊김 회수 (09-23 09:45, Jetson, 읽기 전용)
- 왜: 사용자 요청 '백그라운드 로그 확인' — 09-18 에 설치한 wifi-mon 이 무엇을 남겼나.
- 하는 일: 지금 시각 · `uptime -s` · 활성 연결 → 두 프로파일 autoconnect · 우선순위 · 절전 → `nmcli dev wifi list` 의 두 SSID → `/var/log/wifi_mon/` 목록 · 서비스 상태 → `mon.log` 마지막 40 줄 → 최근 event 스냅샷 2 개 머리 25 줄 → `wpa_debug.log` 의 deauth · reason · CTRL-EVENT 줄(09-22 16:00 이후, 60 줄) → syslog NM · wpa 줄(80 줄).
- 출력: [`j529_wifi.txt`](../debug_log/2026-09-23/outputs/j529_wifi.txt). 쓰인 곳: §0.1 전날 갱신 · EVENT 쌍 · BEACON 160 MHz, §5.2 실수 3 판별(패치 전 LINK 간격 15.29 s).
- 결함: 부팅 블록 줄은 `Jan  1 09:0x`(1970) 표기라 'Sep 2[23]' 거르개에 안 걸림 → `job530` 을 따로 만듦.

#### job530_wifi_boot.sh — 부팅 직후 블록 (09-23, Jetson, 읽기 전용)
- 하는 일: `mon.log` 의 마지막 1970 블록 + 첫 2026 줄(awk) → `wpa_debug.log` · syslog 의 `Jan  1 09:0x` 줄 중 결합 · 인증 · NM 활성화 줄(각 `tail` 50~60) → `nmcli dev wifi rescan` 4 s 뒤 목록 → `journalctl -b -u NetworkManager` WEB_DEV 관련 30 줄.
- 출력: [`j530_wifi_boot.txt`](../debug_log/2026-09-23/outputs/j530_wifi_boot.txt). 쓰인 곳: §0.1 '4-way 완료 → DHCP 45 s → ip-config-unavailable → reason 3 locally_generated → ALOPS'.
- 결함: `tail -50` 이라 **세 번째 시도만** 원문에 남았다(§5.2 모순 11). 1970 시각을 실제 시각으로 바꾸지 않는다(모순 10).

#### job534_netprep.sh — 고정 IP 복귀 사전 확인 (09-23 10:0x, Jetson, 읽기 전용)
- 하는 일: `arping` · `tcpdump` 유무, `sudo -n true`(NOPASSWD 여부) → 두 프로파일 `ipv4.method` · `dad-timeout` · `dhcp-client-id` · `autoconnect-retries` · `ipv4.addresses` → `/usr/local/sbin/wifi_mon.sh` 줄 수와 LINK · sleep · snapshot 줄 → (네트워크와 무관) 카메라 점군 파라미터 · Hz.
- 출력: [`j534_netprep.txt`](../debug_log/2026-09-23/outputs/j534_netprep.txt) — arping · tcpdump 없음 · NOPASSWD no · 두 프로파일 auto · dad −1 · 89 줄. 쓰인 곳: `job535` 의 패치 위치(LINK 줄) · 설치 목록을 정함.

#### job535_net_fixed.sh + run_j535.sh — 적용 · 전환 (09-23 10:14, Jetson sudo · PC, 사용자 지시)
- 부른 형태: `bash run_j535.sh`(PC) — **172.30.1.8 로** 올려 실행(전환 전 주소), 그 뒤 PC 가 두 IP 를 3 s 마다 최대 120 s 핑, .101 이 응답하면 거기로(60 s 넘으면 아무 쪽이나) 붙어 활성 연결 · IP · `/tmp/net_switch.log` · NM 3 분 로그 · mon.log 꼬리.
- 하는 일(`job535`): `S()` = 표준입력으로 sudo 비밀번호를 주고 출력에서 `[sudo]` 줄을 거름. ① `apt-get install iputils-arping tcpdump`(timeout 90 — 머리 문구는 '60 s 한도') ② 두 프로파일 `nmcli con modify … ipv4.dad-timeout 3000` 뒤 값 확인 ③ `wifi_mon.sh` 에 ARP_DUP 가 없으면 python 으로 LINK `log` 줄 바로 뒤에 블록 삽입한 `/tmp/wifi_mon.new` 생성(`assert old in s`) → `bash -n && S cp && S systemctl restart wifi-mon && sleep 2 && echo 확인` ④ 3 s 뒤 `nmcli con up WEB_DEV_5G` 를 `nohup sudo` 백그라운드(이 세션은 끊김을 전제).
- 삽입 블록: IPv4 가 있고 arping 이 있으면 `timeout 5 arping -D -c 2 -w 2 -I $IF <내 IP>` 출력에서 'Unicast reply' 첫 줄 → 있으면 `ARP_DUP ip=… <줄>` 기록, 직전 스냅샷이 300 s 보다 오래면 `snapshot "arp dup …"`.
- 출력: [`j535_net.txt`](../debug_log/2026-09-23/outputs/j535_net.txt) — 설치 · dad 3000 × 2 · **'패치 생성' 뒤 확인 줄 없음** · 요청 10:14:30 · PC 4 s 뒤 .101 · NM 10:14:33.21 DHCP 시작 → 10:14:35.35 임대.
- 쓰인 곳: §5 결과(임대 2 s · 아침 무응답 재현 안 됨). 결함: **`S cp` 가 출력이 없어 파이프 끝 `grep -v` 가 종료 코드 1 → `&&` 사슬이 끊겨 서비스 재시작이 안 됨**(§5.2 실수 3). 같은 `S()` 형태는 09-18 도구들에도 있었다(그때는 출력이 있는 명령이라 드러나지 않음 — 추정, 09-18 도구는 이 기준으로 다시 보지 않음). 지금 다시: 쓰지 않음 — 패턴 경고용.

#### job536_moncheck.sh — 패치 적용 확인 (09-23 10:2x, Jetson sudo)
- 하는 일: 파일에 ARP_DUP 가 **없을 때만** 적용 · 재시작 → 파일 안 ARP_DUP 줄 수 · 서비스 상태 · mon.log 꼬리 2 줄 · mon.log 의 ARP_DUP 기록 수 · 수동 `arping -D -c 2 -w 2 … 192.168.0.101` 끝 줄 · 두 프로파일 DAD.
- 출력: [`j536_moncheck.txt`](../debug_log/2026-09-23/outputs/j536_moncheck.txt) — 줄 2 · active · 기록 0 · 'Received 0 response(s)' · 3000/3000.
- 결함: '파일에 있음' 과 '실행 중인 루프에 있음' 을 구분하지 않는다 — 서비스의 시작 시각(`ActiveEnterTimestamp`)이나 `START pid` 줄을 안 봄. 그래서 '적용됨' 으로 잘못 확인(실수 3). 수동 arping 1 회는 그 순간 충돌이 없다는 것만 보인다.

#### job539_dropchk.sh — 끊김 직후 요약 (09-23 12:06, Jetson, 읽기 전용)
- 부른 형태: `job540` 이 먼저 `bash /tmp/job539.sh > /tmp/j539.txt` 로 실행(PC 가 직접 부르지 않음 — 끊김 중이라 온보드로).
- 하는 일: 지금 연결 · IP → mon.log 11:45~11:59 중 **평범한 WEB_DEV LINK 줄을 정규식으로 뺀** 나머지 20 줄(변화 · EVENT · ARP_DUP 만) → ARP_DUP 누적 → wpa CTRL-EVENT · deauth 11:45~11:59 → NM `journalctl --since 11:40` 의 duplicate · dad · dhcp4 · state change → 커널 무선 줄 → 스택 프로세스 수.
- 출력: [`j539_drop.txt`](../debug_log/2026-09-23/outputs/j539_drop.txt) 앞부분. 결함: wpa 범위가 11:59 까지라 12:05 deauth 는 NM 절에서만 보인다. 거르개가 신호 `-5[0-9]` 만 '평범' 으로 보므로 −60 아래로 떨어진 줄만 남는다 — 비트레이트 변화(6.0 Mbit/s)는 정규식에 걸려 빠진다(`rx=[0-9.]+_MBit/s` 가 6.0 도 맞음) → `job543` 으로 다시 뽑음.

#### job540_trace.sh + run_j540.sh — 온보드 30 분 트레이스 (09-23 12:06:17 ~, Jetson · PC)
- 부른 형태: `run_j540.sh`(PC) 가 2 s 마다 최대 90 번 두 IP 를 핑해 붙는 즉시 `job539_unix.sh` · `job540_unix.sh`(CR 제거판)를 올리고 `setsid nohup bash /tmp/job540.sh &`.
- 왜: 다음 끊김에서 'Jetson → 공유기 핑도 죽는가(AP 전달 정지)' 를 가리려고(§11 계측 보강).
- 하는 일: 1 800 s 동안 2 s 마다 한 줄 — 시각 · `ip -4` 주소 · `iw link` 의 BSSID · 신호 · `ping -c1 -W1 192.168.0.1` 성공 ok/X · `ip neigh show 192.168.0.1` 의 MAC · 상태 → `/tmp/j540_trace.txt`.
- 출력: Jetson `/tmp/j540_trace.txt`(**원천 소실** — 발췌만 `j539` 뒷부분 · `j544`). 쓰인 곳: §12 'gw=ok 133/133'. 결함: 게이트웨이 = WEB_DEV AP 자신이라 AP 까지만 보증(모순 17). 30 분 뒤 끝나므로 14:13 · 14:25 끊김은 못 봄.

#### job541_fetch.sh — 트레이스 회수 (09-23 12:08 무렵, Jetson)
- 하는 일: `/tmp/j539.txt` 전문 → 트레이스에서 (IP, gw) 쌍이 바뀐 줄만 마지막 15 → 줄 수 · gw=X 횟수. 출력: `j539_drop.txt` 뒷부분('줄 수 74, gw=X 횟수 0' — 시작 직후 ≈ 2.5 분치).

#### job542_dropwin.sh · job543_mon.sh — 11:55~12:07 창 (09-23, Jetson, 읽기 전용)
- `job542`: mon.log(BEACON 제외 · 상태 변화 줄만) · wpa CTRL-EVENT · reason · SA Query · NM 의 `reason '…'` · dhcp4 줄 · 커널 줄. 출력 [`j542_dropwin.txt`](../debug_log/2026-09-23/outputs/j542_dropwin.txt). 결함: mon.log 절이 날짜를 안 걸러 다른 날 같은 시각 줄로 채워짐(모순 14). wpa 절도 `12:0[0-7]:|11:5[5-9]:` 만 보고 날짜를 안 거르지만, 이번 출력의 줄은 모두 `Sep 23` 이었다(원문 확인) — 다른 날 같은 시각 사건이 있었으면 섞였을 결함.
- `job543`: 날짜까지 붙여 `^2026-09-23 (11:5x|12:0[0-7])` mon.log 전체(BEACON 제외) + LINK 줄 수. 출력 [`j543_mon.txt`](../debug_log/2026-09-23/outputs/j543_mon.txt) — §11 LINK · rx 비트레이트 표, §5.2 실수 3 판별(패치 뒤 LINK 간격 15.19 s).

#### job544_drop2.sh — 12:19 두 번째 끊김 (09-23 12:2x, Jetson, 읽기 전용)
- 하는 일: 트레이스 12:17:00~12:21:30 전 줄 → wpa · NM · 커널 같은 창 → `journalctl -u ssh` 같은 창 → ARP_DUP 수.
- 출력: [`j544_drop2.txt`](../debug_log/2026-09-23/outputs/j544_drop2.txt) — gw=ok 133 · gw=X 0 · wpa/NM '-- No entries --' · sshd 12:21:59 `from 192.168.0.6`. 쓰인 곳: §12 '끊긴 것은 PC 쪽 NAT 경로'.

### 8.3 7 기 도구 (10-14 · 10-15)
#### run_detached.sh — 끊기는 연결에서 실행 (10-14 §8.5, PC/WSL, bash)
- 부른 형태: `bash run_detached.sh 스크립트 [함께 보낼 파일 …]`, 환경 `JX_WAIT`(기본 120 s) · `JETSON_HOST`(기본 **192.168.0.101** — 4 행). 비밀번호는 `run_jn.sh` 에서 읽음(이 파일엔 없음).
- 왜: §8.5 에서 주소가 수 초~수십 초 단위로 붙었다 떨어져 `scp` 한 번이 계속 실패 — 끊겨도 Jetson 쪽 실행은 끝까지 가게.
- 하는 일: 보낼 파일의 `
` 제거 → `try()`(4 s 간격 최대 8 회)로 `scp` → `try` 로 원격 `setsid nohup bash -c 'bash /tmp/X > /tmp/X.out 2>&1; touch /tmp/X.done'` → 5 s 마다 `.done` 확인(최대 `JX_WAIT`) → `try` 로 `.out` 읽기('[끝남]' 또는 '[아직 도는 중 또는 확인 실패]').
  ```bash
  try() { for i in 1 2 3 4 5 6 7 8; do "$@" && return 0; sleep 4; done; return 1; }
  ```
- 출력: 화면만. 쓰인 곳: §8.6 정지 시험(`chk_pad_relief.sh` → [`chk_pad_relief.txt`](../debug_log/2026-10-14/outputs/chk_pad_relief.txt)). 결함: 호스트 키 검사 끔(6 행 `StrictHostKeyChecking=no`) + 재시도 8 회 — **주소 충돌 중이면 같은 비밀번호를 여러 번 남의 기계로 보낼 수 있는 구조**(§8.4 의 우려와 정면으로 겹침). 기본 주소 .101(§6.3). 계보: 08-28 detach 실행 → 09 월 `run_detached` 류 → 10 월 `run_jn.sh`(JX_WHY · `/tmp/live/current.log`).

#### chk_after_reboot.sh — 재부팅 뒤 확인 (10-15 §1.1, Jetson, bash, 로버 안 움직임)
- 하는 일: 호스트 이름 · `/etc/nv_tegra_release` 첫 줄 · `~/ros2_ws/src/rover_navigation` · `~/maps/office/office_v3.posegraph` 수 · `uptime -p` · `uptime -s` · `/tmp` 의 `prep_fast.sh prep_patrol.sh prep_patrol_pad.sh pad_relief.py chk_prep.py job551_f0drive.sh` 유무 · `docker ps -a` · `wlan0` 주소 · `iwgetid -r`(SSID).
- 출력: 원천 소실(SUMMARY §1.1: jetson-desktop · R36.5.0 · 있음 · 1 · WEB_DEV_5G · 부팅 09:48:52 · 6 개 모두 없음 · microros_agent 실행 · isaac_ros_dev 정지). 한계: 로그인 뒤 확인(§5.3 실수 1). 재사용: 가능(재부팅 뒤 `/tmp` 점검용으로는 유효).

#### up_tools.sh — 도구 일괄 전송 (10-14 §8.6 · 재부팅 뒤, PC/WSL, `Docs/tools/`)
- 스크래치패드 `tools/` 의 `prep_fast.sh chk_prep.py prep_patrol.sh anal_rtps_*.py` 와 `up950/`(없으면 스크래치패드 뿌리)의 `job240_clean.sh job386_slamalive.py job440_startclear.py job451_paramsnap.py job453_runmeta.sh job956_gcmchk.py` 를 `
` 제거 뒤 Jetson `/tmp` 로 한 번에 `scp`, 끝에 `/tmp` 스크립트 수. 10-14 엔 `JETSON_HOST=172.30.1.8` 로 부름. 기본 주소는 11-02 에 .110 으로 고침(커밋 `9b3dca22`). 출력: 화면 한 줄(원문 없음).

## 9. 용어
- **Wi-Fi power save(절전)**: 무선 카드가 쉬는 동안 AP 에게 '잠든다' 고 알리고 비콘 몇 번에 한 번만 깨어나 쌓인 패킷을 받는 방식. 전력은 줄지만 바깥에서 오는 패킷(ARP 질문 · ping)에 수백 ms 늦게 답하거나 놓칠 수 있다. `iw dev <IF> get power_save` 로 상태를 본다.
- **NetworkManager(NM)**: Ubuntu 의 네트워크 관리 데몬. 저장된 '연결 프로파일'(SSID · 비밀번호 · IP 방식 · 절전 · 자동연결 우선순위)을 들고 있다가 자동으로 붙는다. `nmcli` 가 명령줄 도구. `802-11-wireless.powersave` 값: 0 = 기본(전역 따름) · 2 = 끔 · 3 = 켬. 연결 중인 망이 끊기면 다음 우선순위 프로파일로 옮겨 가며, 이때 IP 가 바뀐다.
- **ARP**: 같은 망 안에서 'IP 주소 → 장치 MAC 주소' 를 묻는 방송 질문. 공유기가 Jetson 에게 패킷을 넘기려면 먼저 ARP 로 Jetson 의 MAC 을 알아야 한다. 답이 없으면 공유기는 'host unreachable' 을 돌려준다(09-03 의 .6). 같은 IP 를 두 장치가 쓰면(IP 충돌) ARP 답이 엇갈린다(10-14).
- **망 구조(이 시기)**: PC(172.30.1.89) → PC 쪽 공유기(LAN 172.30.1.254 / WAN 192.168.0.6) → 192.168.0.x 망 → Jetson(WEB_DEV_5G, 192.168.0.101). PC 와 Jetson 은 다른 서브넷이고 가운데 공유기가 NAT 로 이어 준다. (3 시기에 밝혀진 것) WEB_DEV_5G 의 AP 는 ipTIME AX3000R(192.168.0.1, 5 GHz ch36 · 160 MHz), 예비 망 ALOPS_ROBOTICS_5G(ch153)는 **PC 와 같은 172.30.1.x** 라 Jetson 이 그쪽에 붙으면(172.30.1.8) NAT 를 안 거친다.
- **detach(setsid · nohup · disown)**: SSH 세션이 끊겨도 프로세스가 살아 있게 띄우는 방법 — [첫 SLAM 지도 §9](first-slam-map.md#9-용어).
- **deauth / 재인증 거부**: AP 가 클라이언트를 먼저 끊는 관리 프레임(reason 코드 포함), 그 뒤 같은 비밀번호로 다시 붙으려 할 때 AP 가 거절하는 것 — 09-15~17 사건의 양상.
- **deauth reason 코드(IEEE 802.11, wpa_supplicant `reason=N`)**: 끊는 쪽이 이유를 숫자로 붙인다. 이 카드에 나온 것 — **2** '이전 인증이 더 이상 유효하지 않음'(AP 가 이 단말의 인증 상태를 버림) · **3** '떠나는 중이라 끊음'(우리 쪽이 다른 망으로 옮길 때, `locally_generated=1` 이 같이 찍힘 = Jetson 이 보낸 것) · **23** 'IEEE 802.1X 인증 실패'(WPA2-PSK 에서는 4-way handshake 단계 실패 때 쓰임). `locally_generated=1` 이 **없으면 AP 가 보낸 것**. `ASSOC-REJECT status_code=8`(ALOPS 부팅 첫 시도)은 끊김이 아니라 결합 거절 상태 코드.
- **PSK(Pre-Shared Key)**: WPA2-개인용의 공유 비밀번호에서 만든 키. 저장 프로파일에 들어 있고, 이 카드의 도구들은 psk · passphrase 줄을 출력에서 지운다.
- **4-way handshake**: 결합(association) 뒤 AP 와 단말이 PSK 를 직접 보내지 않고 서로 같은 키를 가졌는지 확인하며 세션 키를 만드는 메시지 4 개(msg 1/4 AP → 2/4 단말 → 3/4 → 4/4). 2/4 를 받은 AP 가 키가 안 맞는다고 보면 끊는다 — 그래서 wpa_supplicant 는 실패 시 'pre-shared key may be incorrect'(추정 문구)를 찍는다. §4.1 판정 기준은 '어느 메시지까지 갔나' 로 공유기 쪽 거부와 키 불일치를 가른다.
- **PMF(802.11w, Protected Management Frames) · MFP · BIP · SA Query**: deauth 같은 관리 프레임에 서명을 붙여 위조 끊기 공격을 막는 기능. AP 비콘의 `MFP-capable` = 선택 지원, 협상되면 `wpa_cli status` 에 `pmf=1` · `mgmt_group_cipher=BIP`(방송 관리 프레임 서명 방식). PMF 상태에서는 이미 연관된 단말이 다시 결합하려 하면 AP 가 SA Query 로 '진짜 그 단말인지' 확인하며 잠시 거절('Association comeback')할 수 있다 — 양쪽이 보안 연관 상태를 서로 다르게 들고 있으면 재접속이 막힐 수 있다는 것이 후보 ⓑ 의 논리(일반론).
- **DFS(Dynamic Frequency Selection)**: 5 GHz 의 일부 채널(52~144)은 기상 · 군용 레이더와 함께 쓰므로, AP 가 레이더를 감지하면 그 채널을 즉시 비워야 한다(채널 · 폭 변경, 보통 CSA 로 예고). ch36 을 160 MHz 로 쓰면 36~64 를 묶으므로 DFS 채널 52~64 가 들어간다 → 레이더(또는 오감지) 한 번에 무선부를 재구성하며 단말이 끊길 수 있다는 것이 후보 ⓐ. **CSA(Channel Switch Announcement)** = 비콘에 '몇 비콘 뒤 채널을 옮긴다' 고 싣는 예고.
- **VHT operation 의 폭 읽기**: 비콘 `channel width: 1 (80 MHz)` 는 '80 MHz 이상' 이라는 뜻이고, `center freq segment 2` 가 0 이 아니면(여기선 50) 실제로는 160 MHz 운용이다(802.11ac 이후 표기). `iw` 가 괄호에 '80 MHz' 라고 찍어도 160 이다 — wifi-mon 의 BEACON 판정이 seg2 를 보는 이유.
- **규제 영역(`iw reg get`, country 00 / KR)**: 나라별로 쓸 수 있는 채널 · 출력 · DFS 규칙. Jetson 은 `country 00`(WORLD, DFS-UNSET)으로 떠 있어 보수적 규칙을 쓴다. 공유기는 KR.
- **NetworkManager 자동연결 우선순위(`connection.autoconnect-priority`)**: 자동연결 대상 프로파일이 여럿 보일 때 숫자가 큰 쪽부터 시도(기본 0, 같으면 최근 사용 순). **이미 연결된 동안에는 더 높은 쪽으로 옮기지 않는다** — 그래서 ALOPS 로 넘어간 뒤 WEB_DEV 가 회복돼도 재부팅 · 수동 `nmcli con up` 전까지 ALOPS 에 머문다. 인증이 반복 실패하면 NM 은 비밀번호가 필요하다고 보고 `no-secrets` 로 그 프로파일 활성화를 포기한다(대화형 비밀번호 입력 주체가 없으므로 재시도 안 함).
- **DHCP 임대(lease)**: 공유기가 단말 MAC 에 IP 를 일정 시간 빌려주는 것. 임대 시간의 절반쯤마다 갱신한다(여기 ALOPS 는 30 분마다 'new lease' 줄). 공유기는 보통 같은 MAC 에 같은 주소를 다시 준다(ALOPS → 172.30.1.8). 'DHCP 예약(고정 할당)' 은 그 대응을 공유기에 못 박는 것(09-23 · 10-15).
- **NTP 전 시각**: Jetson 은 부팅 직후 네트워크 시간 동기(NTP) 전까지 마지막으로 저장한 시각에서 시계를 이어 간다(추정 — 이 보드의 RTC 동작 확인 안 함). 그 사이 찍힌 syslog · wifi-mon 줄은 실제보다 이르다. 차이는 일정하지 않다(09-17 ≈40 분, 09-18 ≈17.6 h). 판정에 쓸 땐 `uptime -s` · NTP 동기 줄과 대조.
- **rsyslog · severity 7**: 프로그램이 syslog 로 보내는 줄에는 심각도(0 긴급 ~ 7 DEBUG)가 붙는다. `25-wifi-mon.conf` 는 wpa_supplicant 의 7 만 별도 파일로 보내고 `stop` 으로 syslog 에서 뺀다.
- **DHCP 예약 vs 정적 IP**: 예약 = 공유기 DHCP 서버가 그 MAC 에 늘 같은 주소를 주는 것(단말은 여전히 DHCP), 정적 = 단말 쪽에 주소를 박는 것. 09-23 사용자는 예약을 택했다. 예약은 **다른 기기가 그 주소를 스스로 쓰는 것**(정적 설정 · 다른 DHCP 서버)은 막지 못한다 — 10-14 의 충돌.
- **`ip-config-unavailable` · DHCP 45 s**: NM 은 무선 결합 · 인증 뒤 DHCP 요청을 보내고 45 s 안에 임대가 없으면 그 활성화를 실패로 접는다(`ip-config -> failed (reason 'ip-config-unavailable')`), 그 뒤 스스로 끊고(`reason 3 locally_generated`) 다음 프로파일로 간다. 즉 '무선은 붙었는데 IP 를 못 받음' 의 서명.
- **DAD(Duplicate Address Detection) · `ipv4.dad-timeout`**: 주소를 쓰기 전에 'IP 가 이 주소인 사람?' 을 ARP 로 물어(보내는 쪽 주소 0.0.0.0 — RFC 5227 방식) 응답이 있으면 충돌로 보고 쓰지 않는 검사. NM 값 −1 = 기본(이 Jetson 에서 실제로 몇 ms 인지 미확인), 3000 = 3 s 기다림.
- **`arping -D`**: 같은 DAD 질문을 명령줄에서 보내는 도구(iputils). 응답(`Unicast reply from <IP> [<MAC>]`)이 오면 그 주소를 다른 장치가 쓰고 있다는 뜻, 'Received 0 response(s)' 면 그 순간엔 없음. AP 가 이 단말의 프레임을 전달하지 않는 중이면 응답도 안 오므로 '0' 이 곧 '충돌 없음' 은 아니다.
- **AP 격리(client isolation)**: 같은 AP 에 붙은 무선 단말끼리 직접 통신을 막는 공유기 기능. 09-23 §14 에 PC 를 WEB_DEV 에 붙였을 때 Jetson ARP 가 안 된 것을 이것으로 **추정**했다(공유기 설정은 확인 안 함).
- **rx 비트레이트 · MCS**: `iw link` 의 `rx bitrate` 는 마지막으로 받은 프레임의 전송 속도. 6.0 Mbit/s 는 관리 · 기본 속도(비콘 등)라 데이터가 없을 때도 나오고, 175.6(MCS 2) · 390~780 은 데이터 프레임 속도. 그래서 '6.0 = 데이터 끊김' 은 단독으로는 약한 근거(§3.2).
- **IP 주소 충돌(7 기)**: 같은 망에서 두 기기가 같은 IPv4 주소를 쓰는 상태. 공유기 · 다른 기기는 ARP 답이 엇갈려 패킷을 한쪽으로만(또는 번갈아) 보낸다 — 10-14 §8.5 의 '수 초~수십 초 단위로 붙었다 떨어짐' 과 맞는 모양. 10-14 엔 다른 서버가 DHCP 로 .101 을 요청해 받았다(사용자).
- **SSH 호스트 키**: SSH 서버가 자기 신원을 증명하는 공개 키. 인증(비밀번호) 전에 받으므로, 저장해 둔 키와 비교하면 '이 주소에서 답하는 기계가 그 기계인가' 를 비밀번호를 보내기 전에 가릴 수 있다. 우리 스크립트는 `StrictHostKeyChecking=no` · `UserKnownHostsFile=/dev/null` 로 이 비교를 끈다.
- **USB 장치 모드 주소(192.168.55.1)**: Jetson 개발 키트를 USB 로 PC 에 꽂으면 생기는 가상 이더넷의 Jetson 쪽 주소. Wi-Fi 와 무관한 비상 접속로.
