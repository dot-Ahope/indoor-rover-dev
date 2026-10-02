#!/bin/bash
# 10-02 §5: 10-01 F2 bag 12 개 풀기(~/bags/f2) → 증거 추출(/tmp/evid/*.npz)
source /opt/ros/humble/setup.bash; mkdir -p ~/bags/f2 /tmp/evid
for f in /tmp/f2bags/*.tgz; do tar -xzf $f -C ~/bags/f2 && rm $f; done
for b in ~/bags/f2/bag_f2a*; do n=$(basename $b); python3 -u /tmp/job805_evid.py $b /tmp/evid/${n#bag_}.npz 2>&1 | grep -av "^\[INFO"; done
du -sh /tmp/evid
