#!/bin/bash
H=${JETSON_HOST:-172.30.1.8}
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
timeout 20 sshpass -p <PW> ssh $O jetson@$H 'ls -la /tmp/scan_now.npy; source /opt/ros/humble/setup.bash; rm -f /tmp/icp414.log; setsid nohup bash -c "python3 /tmp/job370_scanmatch.py /tmp/bag_mp11 /tmp/scan_now.npy 1.153 -0.021 > /tmp/icp414.log 2>&1; echo ICP_DONE >> /tmp/icp414.log" > /dev/null 2>&1 & echo started $(date +%T)'
for i in $(seq 1 60); do
  sleep 10
  OUT=$(timeout 15 sshpass -p <PW> ssh $O jetson@$H "cat /tmp/icp414.log 2>/dev/null")
  echo "$OUT" | grep -q ICP_DONE && { echo "경과 $((i*10)) s"; echo "$OUT" | grep -av "^\["; break; }
done
