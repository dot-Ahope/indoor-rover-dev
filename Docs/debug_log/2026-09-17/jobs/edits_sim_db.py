import sys
p = sys.argv[1]; NL = chr(10)
s = open(p, encoding='utf-8').read()
pairs = [
 ("         cycles=40, seed=1, label='')",
  "         db=0.0, promote=0.0, eps=0.003, track_b=0.443, prune=1.0," + NL + "         cycles=40, seed=1, label='')"),
 ("    elif topic == '/transformed_global_plan':" + NL + "        tplans.append((t, deserialize_message(data, Path)))",
  "    elif topic == '/transformed_global_plan':" + NL + "        tplans.append((t, deserialize_message(data, Path)))" + NL +
  "    elif topic == '/plan':" + NL + "        gplans.append((t, deserialize_message(data, Path)))"),
 ("ob, lcs, tplans, cmds = [], [], [], []",
  "ob, lcs, tplans, cmds, gplans, mo = [], [], [], [], [], []"),
 ("path = np.array([[q.pose.position.x, q.pose.position.y] for q in tp[1].poses])",
  "if tp is not None:" + NL +
  "    path = np.array([[q.pose.position.x, q.pose.position.y] for q in tp[1].poses])" + NL +
  "else:" + NL +
  "    # 09-17: visualize off 이면 /transformed_global_plan 이 없다 → /plan(map) 을 odom 으로 옮기고 로버 최근접점부터 prune m 만 남긴다" + NL +
  "    gp = latest(gplans, t); a = latest(mo, t)" + NL +
  "    G_ = np.array([[q.pose.position.x, q.pose.position.y] for q in gp[1].poses])" + NL +
  "    dx_, dy_ = G_[:, 0] - a[1], G_[:, 1] - a[2]; c_, s_ = math.cos(a[3]), math.sin(a[3])" + NL +
  "    O_ = np.stack([dx_ * c_ + dy_ * s_, -dx_ * s_ + dy_ * c_], 1)" + NL +
  "    k0 = int(np.argmin(np.hypot(O_[:, 0] - pose[1], O_[:, 1] - pose[2])))" + NL +
  "    seg = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(O_[k0:], axis=0).T))])" + NL +
  "    path = O_[k0:k0 + int(np.searchsorted(seg, P['prune'])) + 1]"),
 ("    v0, w0 = mean_v[0], mean_w[0]" + NL,
  "    v0, w0 = mean_v[0], mean_w[0]" + NL +
  "    if P['db'] > 0 or P['promote'] > 0:   # 09-17: 펌웨어 휠 속도 처리 모델 (microros_task 승격 → speed_controller 정지 문턱)" + NL +
  "        def fw(vw):" + NL +
  "            if abs(vw) < P['eps']: return 0.0" + NL +
  "            if abs(vw) < P['promote']: vw = math.copysign(P['promote'], vw)" + NL +
  "            return 0.0 if abs(vw) < P['db'] else vw" + NL +
  "        vl, vr = fw(v0 - w0 * P['track_b'] / 2), fw(v0 + w0 * P['track_b'] / 2)" + NL +
  "        v0, w0 = (vl + vr) / 2, (vr - vl) / P['track_b']" + NL),
]
for old, new in pairs:
    c = s.count(old); assert c == 1, (old[:50], c)
    s = s.replace(old, new)
# map->odom TF 수집 (tf 루프에 추가)
old = "            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link':"
assert s.count(old) == 1
s = s.replace(old, "            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom':" + NL +
              "                mo.append((tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9, tr.transform.translation.x, tr.transform.translation.y, yaw_of(tr.transform.rotation)))" + NL + old)
s = s.replace("ob.sort(); T0 = ob[0][0]", "ob.sort(); mo.sort(); T0 = ob[0][0]")
# 최종 출력에 목표까지 거리
old = "print('  → %d 주기(%.1f s) 후: 전진 %+.3f 횡 %+.3f 회전 %+.1f°, 최종 cmd v %+.3f w %+.3f' % (P['cycles'], P['cycles'] * P['dt'], dx, dy, math.degrees(wrap(rth - th0)), mean_v[0], mean_w[0]))"
assert s.count(old) == 1
s = s.replace(old, old + NL + "print('     목표(경로 끝, prune 창 안이면) 까지 거리 %.3f m (xy tol 0.15), 로버 odom (%.3f, %.3f)' % (math.hypot(path[-1][0] - rx, path[-1][1] - ry), rx, ry))")
open(p, 'w', encoding='utf-8', newline=NL).write(s); print('sim patched')
