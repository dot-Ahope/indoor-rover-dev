#!/bin/bash
# chk_pub_filtered_1102 — publish_public.sh 를 push 직전에서 멈춘 마른 실행의 끝에서 부름: 필터된 공개 이력의 SSHPASS= 앞머리(값 첫 글자만) (벤더 기본값 검색어는 공개 파일에 쓰지 않으려 뺌 — 그날은 대화에서 따로 셈) (11-02 §8, PC)
git log -p --all --format= | grep -o 'SSHPASS=.\{0,3\}' | cut -c1-9 | sort | uniq -c
