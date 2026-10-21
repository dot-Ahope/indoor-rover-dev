#!/bin/bash
# 옛 컨테이너 vs 시험 컨테이너 설정 차이 · 옛 cuVSLAM 기동 로그에도 NitrosContext 오류가 있나
f() { docker inspect $1 -f '{{json .Config.Env}}' | tr ',' '\n' | sort; docker inspect $1 -f 'ep={{json .Config.Entrypoint}} rt={{.HostConfig.Runtime}} ipc={{.HostConfig.IpcMode}} pid={{.HostConfig.PidMode}} shm={{.HostConfig.ShmSize}} priv={{.HostConfig.Privileged}} dev={{json .HostConfig.Devices}} grp={{json .HostConfig.GroupAdd}}'; docker inspect $1 -f '{{range .Mounts}}{{.Source}}:{{.Destination}}{{"\n"}}{{end}}' | sort; }
diff <(f isaac_ros_dev-aarch64-container) <(f isaac_rs_test)
echo "--- 옛 cuVSLAM 로그의 Nitros/Invalid"; for L in $(ls -t /tmp/cuvslam*.log /tmp/logkeep/*cuvslam* 2>/dev/null | head -3); do echo "$L"; grep -aE "NitrosContext|Invalid argument|Loaded node 'visual" $L | sed 's/\x1b\[[0-9;]*m//g' | cut -c1-200 | head -5; done
grep -n "docker exec" /tmp/cuvslam_up.sh 2>/dev/null | cut -c1-300 | head -5
