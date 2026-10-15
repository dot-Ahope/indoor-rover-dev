# 2026-10-15 TOOLS

| 시각 · § | 상황 | 도구 | 나온 값 | 그때의 추론 |
|---|---|---|---|---|
| 아침 · §1 | 재부팅 뒤 Jetson 접속 | ping(WSL · PowerShell) · arp · `chk_after_reboot.sh`(접속 실패로 미실행) | 172.30.1.8 무응답 2 분, ARP 에 없음 | 부팅 중 또는 다른 망 ？ |
| 10:1x · §1.1 | 새 주소 192.168.0.110 접속 · 재부팅 뒤 준비 | ping · `chk_after_reboot.sh` · md5 비교 · `put_one.sh` | 신원 확인(jetson-desktop · R36.5 · ros2_ws · office_v3), /tmp 스크립트 6 개 없음 → 5 개 재전송 | 이 Jetson 맞음 ✔. 보드 세션은 prep 에서 확인 ？ |
| 10:2x · §2 | 기준선 판정 기준 선언 | — | — | 주행 전 선언 ✔ |
