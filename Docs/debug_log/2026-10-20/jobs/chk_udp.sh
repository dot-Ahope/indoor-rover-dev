#!/bin/bash
sysctl net.core.rmem_max net.core.rmem_default net.core.wmem_max net.ipv4.ipfrag_high_thresh net.ipv4.ipfrag_time 2>&1
docker inspect isaac_ros_dev-aarch64-container --format "net={{.HostConfig.NetworkMode}} ipc={{.HostConfig.IpcMode}}"
netstat -su 2>/dev/null | grep -iE "receive buffer|packet receive errors|reassembl" | head; cat /proc/net/snmp | grep -A1 "^Ip:" | tail -1 | awk "{print \"ReasmFails\", \$17}"
