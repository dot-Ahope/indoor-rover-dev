#!/bin/bash
# 10-01 §5: 사용자 승인 — cand_0930_cut590_nolc 를 office_v2 로 저장(복사, 원본·office_v1 유지). 같은 이름 있으면 중단.
set +u; D=/home/jetson/maps/office; S=cand_0930_cut590_nolc; N=office_v2
[ -e $D/$N.posegraph ] && { echo "이미 있음: $D/$N — 중단"; exit 1; }
cp $D/$S.posegraph $D/$N.posegraph && cp $D/$S.data $D/$N.data && cp $D/$S.pgm $D/$N.pgm
sed "s/^image: .*/image: $N.pgm/" $D/$S.yaml > $D/$N.yaml
cd $D && sha256sum $S.posegraph $N.posegraph $S.data $N.data $S.pgm $N.pgm | awk '{print substr($1,1,16), $2}'
ls -la $D/office_v*.*; cat $D/$N.yaml
