# 2026-11-03 도구 사용 기록

규약 README §3.3. 로버 주행 없음.

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 뒤 판정 |
|---|---|---|---|---|---|
| §1 | 7 기 묶음 F 가 10-14 '원천 소실' 끝 방향을 bag 으로 다시 셈 | `2026-10-14/jobs/anal_path_endyaw.py` → `outputs/anal_path_endyaw_*.txt` | f2s1 지도 기준 0.0° · 남서(고치기 전) 컨트롤러 0.0° / 계획기 −101.3° | 남서 정체도 TruncatePath 결함 | ✔ |
| §3 | 러너 QoS 블록이 BAG_BE_TRAJ=0 에서도 /tf 를 넣는가 | 블록만 떼어 bash 실행(대화 안, 출력은 §3 에 요약) | 1 · 0 모두 `/tf:` 1 줄 | 고친 판이 맞음 | ✔ (실주행 미확인) |
| §3 | prep 의 PreferForward 편집이 링크를 살리는가 | `jobs/chk_prep_sed_1103.sh` → `outputs/chk_prep_sed_1103.txt` | 15.0 → 그대로 · 링크 유지 / 5.0 → 바꿈 · 링크 유지 | 고친 판이 맞음 | ✔ (Jetson 미확인) |
