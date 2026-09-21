#!/bin/bash
# nav2_params.yaml 배포(src+install) — CostCritic 교체 (09-18 §17). nav2 재기동 없음(다음 run_mp9prep 이 재기동). 설치본과 diff 로 바뀐 줄만 확인, 기존본 백업.
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
rm -f /tmp/nav2_params.yaml; tr -d '\r' < $NSPS/nav2_params_0921nv.yaml > /tmp/nav2_params.yaml && [ -s /tmp/nav2_params.yaml ] || exit 1
grep -q '"CostCritic"' /tmp/nav2_params.yaml || { echo "★ 전송본에 CostCritic 없음 — 옛 파일?"; exit 1; }
sshpass -p <PW> scp $O -q /tmp/nav2_params.yaml jetson@$H:/tmp/nav2_params.yaml || exit 1
timeout 60 sshpass -p <PW> ssh $O jetson@$H 'I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config; S=~/ros2_ws/src/rover_navigation/config; B=~/ros2_ws/.bak_20260918; mkdir -p $B
python3 -c "import yaml;d=yaml.safe_load(open(\"/tmp/nav2_params.yaml\"));m=d[\"controller_server\"][\"ros__parameters\"][\"FollowPathMPPI\"];print(\"yaml ok, critics =\", m[\"critics\"]);print(\"CostCritic =\", m[\"CostCritic\"])" || exit 1
echo "== 설치본 대비 diff (주석 제외) =="; diff <(grep -v "^\s*#" $I/nav2_params.yaml | sed "s/\s*#.*//") <(grep -v "^\s*#" /tmp/nav2_params.yaml | sed "s/\s*#.*//")
cp -p $I/nav2_params.yaml $B/install_nav2_params_before_nv.yaml; for d in $S $I; do cp /tmp/nav2_params.yaml $d/; done; md5sum $S/nav2_params.yaml $I/nav2_params.yaml /tmp/nav2_params.yaml | cut -c1-12 | tr "\n" " "; echo
echo "(실행 중 controller_server 는 옛 목록 — 다음 prep 재기동 때 반영)"'
