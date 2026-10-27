#!/bin/bash
# §29 SLAM 포크 단계별 시간 계측 판(기록만, 동작 불변) — 운용 ~/slam_ws 는 건드리지 않고 사본 ~/slam_dbg_ws 에 넣어 빌드. 로버 안 움직임.
#   계측: 위치 추정 laserCallback(odom 조회 · addScan 전체), addScan(ProcessLocalization · TF 계산/발행),
#         ProcessLocalization(순차 정합 MatchScan · AddVertex · AddEdges · TryCloseLoop · 버퍼 정리(RemoveNodeFromGraph)),
#         AddEdges 안(LinkChainToScan · LinkNearChains). 줄 머리 '[ROVER_T]' 로 stderr 에 — 처리한 스캔마다 1 줄씩.
set -e
W=~/slam_dbg_ws
if [ ! -d $W/src/slam_toolbox ]; then mkdir -p $W/src; cp -a ~/slam_ws/src/slam_toolbox $W/src/; fi
cd $W/src/slam_toolbox && git checkout -- lib/karto_sdk/src/Mapper.cpp src/slam_toolbox_localization.cpp 2>/dev/null || true
python3 - <<'PY'
import os
R = os.path.expanduser('~/slam_dbg_ws/src/slam_toolbox')
def sub(s, a, b, label):
    if s.count(a) != 1: raise SystemExit('기준 문자열 %d 개(%s) — 중단' % (s.count(a), label))
    return s.replace(a, b)
# --- Mapper.cpp ---
p = R + '/lib/karto_sdk/src/Mapper.cpp'; s = open(p).read()
s = sub(s, '#include <list>\n', '#include <list>\n#include <chrono>\n#include <cstdio>\n#define ROVER_NOW() std::chrono::steady_clock::now()\n#define ROVER_MS(a) std::chrono::duration<double, std::milli>(ROVER_NOW() - (a)).count()\n', 'include')
i0 = s.index('kt_bool Mapper::ProcessLocalization('); i1 = s.index('void Mapper::AddScanToLocalizationBuffer')
f = s[i0:i1]
f = sub(f, '  if (pScan == NULL) {\n    return false;\n  }\n', '  if (pScan == NULL) {\n    return false;\n  }\n  auto _t0 = ROVER_NOW(); double _tm = 0, _tv = 0, _te = 0, _tl = 0, _tb = 0;  // [rover 10-27 §29] 계측만\n', 'PL 시작')
f = sub(f, '    m_pSequentialScanMatcher->MatchScan(pScan,', '    auto _a1 = ROVER_NOW();\n    m_pSequentialScanMatcher->MatchScan(pScan,', 'PL match')
f = sub(f, '    pScan->SetSensorPose(bestPose);\n', '    pScan->SetSensorPose(bestPose);\n    _tm = ROVER_MS(_a1);\n', 'PL match 끝')
f = sub(f, '    scan_vertex = m_pGraph->AddVertex(pScan);\n    m_pGraph->AddEdges(pScan, cov);\n',
        '    auto _a2 = ROVER_NOW();\n    scan_vertex = m_pGraph->AddVertex(pScan);\n    _tv = ROVER_MS(_a2); auto _a3 = ROVER_NOW();\n    m_pGraph->AddEdges(pScan, cov);\n    _te = ROVER_MS(_a3);\n', 'PL graph')
f = sub(f, '        m_pGraph->TryCloseLoop(pScan, *iter);\n', '        auto _a4 = ROVER_NOW();\n        m_pGraph->TryCloseLoop(pScan, *iter);\n        _tl += ROVER_MS(_a4);\n', 'PL loop')
f = sub(f, '  AddScanToLocalizationBuffer(pScan, scan_vertex);\n\n  return true;',
        '  auto _a5 = ROVER_NOW();\n  AddScanToLocalizationBuffer(pScan, scan_vertex);\n  _tb = ROVER_MS(_a5);\n'
        '  fprintf(stderr, "[ROVER_T] PL t=%.3f match=%.1f vertex=%.1f edges=%.1f loop=%.1f buffer=%.1f total=%.1f\\n", pScan->GetTime(), _tm, _tv, _te, _tl, _tb, ROVER_MS(_t0));\n\n  return true;', 'PL 끝')
s = s[:i0] + f + s[i1:]
j0 = s.index('void MapperGraph::AddEdges('); j1 = s.index('kt_bool MapperGraph::TryCloseLoop(')
g = s[j0:j1]
g = sub(g, '    LinkChainToScan(pSensorManager->GetRunningScans(rSensorName), pScan, scanPose, rCovariance);\n',
        '    auto _b1 = ROVER_NOW();\n    LinkChainToScan(pSensorManager->GetRunningScans(rSensorName), pScan, scanPose, rCovariance);\n    fprintf(stderr, "[ROVER_T] AE chain=%.1f\\n", ROVER_MS(_b1));\n', 'AE chain')
g = sub(g, '  LinkNearChains(pScan, means, covariances);\n', '  auto _b2 = ROVER_NOW();\n  LinkNearChains(pScan, means, covariances);\n  fprintf(stderr, "[ROVER_T] AE near=%.1f nmeans=%zu\\n", ROVER_MS(_b2), means.size());\n', 'AE near')
s = s[:j0] + g + s[j1:]
open(p, 'w').write(s)
# --- slam_toolbox_localization.cpp ---
p = R + '/src/slam_toolbox_localization.cpp'; s = open(p).read()
s = sub(s, '#include <memory>\n', '#include <memory>\n#include <chrono>\n#include <cstdio>\n', 'loc include')
s = sub(s, '  scan_header = scan->header;\n  // no odom info\n  Pose2 pose;\n', '  scan_header = scan->header;\n  // no odom info\n  auto _c0 = std::chrono::steady_clock::now();  // [rover 10-27 §29] 계측만\n  Pose2 pose;\n', 'CB 시작')
s = sub(s, '  if (shouldProcessScan(scan, pose)) {\n    addScan(laser, scan, pose);\n  }\n',
        '  double _codom = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - _c0).count();\n'
        '  if (shouldProcessScan(scan, pose)) {\n    auto _c1 = std::chrono::steady_clock::now();\n    addScan(laser, scan, pose);\n'
        '    fprintf(stderr, "[ROVER_T] CB stamp=%.3f odom=%.1f add=%.1f\\n", rclcpp::Time(scan->header.stamp).seconds(), _codom, std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - _c1).count());\n  }\n', 'CB')
s = sub(s, '    processed = smapper_->getMapper()->ProcessLocalization(range_scan, &covariance);\n',
        '    auto _d0 = std::chrono::steady_clock::now();\n    processed = smapper_->getMapper()->ProcessLocalization(range_scan, &covariance);\n'
        '    fprintf(stderr, "[ROVER_T] AS proc=%.1f ok=%d\\n", std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - _d0).count(), (int)processed);\n', 'AS')
open(p, 'w').write(s)
print('계측 넣음')
PY
cd $W/src/slam_toolbox && git --no-pager diff --stat
set +e; source /opt/ros/humble/setup.bash; cd $W
T0=$(date +%s); nice -n 10 colcon build --packages-select slam_toolbox --cmake-args -DCMAKE_BUILD_TYPE=Release > /tmp/slam_dbg_build.log 2>&1; RC=$?
echo "빌드 rc $RC · $(( $(date +%s) - T0 )) s"; grep -aE "Finished|Failed|error:" /tmp/slam_dbg_build.log | tail -5
ls -la $W/install/slam_toolbox/lib/slam_toolbox/localization_slam_toolbox_node 2>&1
