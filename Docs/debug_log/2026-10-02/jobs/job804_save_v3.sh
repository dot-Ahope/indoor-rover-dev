#!/bin/bash
# 10-02 §4: 후보 cand_1002_f2a12_c276_nolc → office_v3 (사용자 승인). office_v1·v2 는 보존.
D=/home/jetson/maps/office; C=cand_1002_f2a12_c276_nolc
[ -e $D/office_v3.posegraph ] && { echo "이미 있음: office_v3"; exit 1; }
for e in posegraph data pgm; do cp $D/$C.$e $D/office_v3.$e; done
sed "s/^image: .*/image: office_v3.pgm/" $D/$C.yaml > $D/office_v3.yaml
for e in posegraph data pgm; do printf "  %-10s %s %s\n" $e $(sha256sum $D/$C.$e | cut -c1-16) $(sha256sum $D/office_v3.$e | cut -c1-16); done
cat $D/office_v3.yaml; ls -la $D/office_v3.*
