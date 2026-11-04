#!/bin/bash
# up_tools — 저장소 Docs/tools 의 Jetson 쪽 도구를 Jetson /tmp 로 전송(실행 안 함 · 로버 안 움직임). Jetson 재부팅 뒤 한 번.
#   부르는 곳: PC Git Bash 에서 `bash Docs/tools/up_tools.sh` (인자 없음). 환경 JETSON_HOST(기본 192.168.0.110) · RUNNER_DIR(run_jn.sh 있는 곳).
#   하는 일: ① 저장소 판을 RUNNER_DIR/tools 로 복사(CRLF 제거) ② 같은 곳에 전송 스크립트를 써서 WSL 에서 scp
#            ③ Jetson /tmp 의 파일 수 · prep_fast.sh 의 --follow-symlinks 줄 수(11-03 판이면 1 이상)를 출력.
#   비밀번호는 RUNNER_DIR/run_jn.sh 에서 읽는다(출력 · 기록 금지).
#   11-04 고침: 예전 판은 스크래치패드 tools/ 를 읽었는데 그 폴더가 10-22 에 사라져 옛 판이 올라갈 위험이 있었다
#   (문제 대장 drive-ops-1019-1023 카드) → 저장소 판을 직접 복사. 옛 up950 묶음(job240 · job386 …)은 뺐다 — 지금 prep · 러너는 안 씀.
set -e
R=$(cd "$(dirname "$0")/../.." && pwd)
W=${RUNNER_DIR:-C:/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad}
L=/mnt/c/${W#C:/}
H=${JETSON_HOST:-192.168.0.110}
FILES="prep_fast.sh prep_patrol.sh chk_prep.py chk_drive_gate.py anal_rtps_pcap.py anal_rtps_onset.py anal_rtps_acklag.py"
mkdir -p "$W/tools"
for f in $FILES; do tr -d '\r' < "$R/Docs/tools/$f" > "$W/tools/$f"; done
echo "  저장소 판 $(git -C "$R" log -1 --format=%h -- Docs/tools/prep_fast.sh) → $W/tools ($(echo $FILES | wc -w) 개)"
cat > "$W/tools/_xfer.sh" <<EOF
PW=\$(grep -o 'sshpass -p [^ ]*' $L/run_jn.sh | head -1 | awk '{print \$3}')
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
cd $L/tools || exit 1
sshpass -p "\$PW" scp \$O -q $FILES jetson@$H:/tmp/ || { echo "  전송 실패"; exit 1; }
sshpass -p "\$PW" ssh \$O jetson@$H 'cd /tmp; echo "  Jetson /tmp: \$(ls $FILES 2>/dev/null | wc -l) 개 · prep_fast --follow-symlinks 줄 \$(grep -c follow-symlinks prep_fast.sh)"'
EOF
MSYS_NO_PATHCONV=1 wsl -d Ubuntu-22.04 -u root --cd /tmp -- bash "$L/tools/_xfer.sh" 2>&1 | tr -d '\000' | grep -v '^w s l'
