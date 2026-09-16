#!/usr/bin/env python3
"""깊이 점군 릴레이 — 근거리 아티팩트와 실루엣 비산점(flying pixel)을 STVL 앞에서 걸러낸다 (2026-09-14).

왜 (Docs/debug_log/2026-09-14/SUMMARY.md §2.5, §2.7):
  1) 근거리 아티팩트: 정지 30 s 표본에서 17 % 프레임에 카메라 0.36~0.38 m(실측 사각지대 0.40 바로 안쪽), z 0.10~0.12 의 점이
     로버 정면 바닥(물체 없음)에 찍혔다. STVL mark_threshold 0 이라 1점이 5 cm 셀을 30 s 동안 LETHAL 로 만들고,
     로버가 전진하면 자기 진로 0.6 m 앞에 유령 셀 자취가 남아 RPP 가 "collision ahead" 로 멈춘다(inf1 입구 정체 무늬).
     절두체 근평면(min_z 0.55) 안쪽이라 frustum 소거도 닿지 않는다. 드라이버(realsense2_camera)에는 min_distance 필터가 없다.
  2) 비산점: 상자 윗모서리·옆모서리 실루엣의 혼합 화소가 상자 뒤(x +0.11~0.36)·뒤옆(y +0.12)에 프레임당 2~4점, 같은 프레임
     5 cm 안 이웃 ≤2 인 고립점 98~99 % 로 찍혀 코스트맵 상자를 실제보다 넓게 만든다(inf2 에서 창 0.27 → 0.05 m, v5 정체 셀).
     상자 본체는 프레임당 ~100점·고립 0 % 라 "복셀당 최소 점 수" 로 깨끗이 갈린다.

무엇을:
  /camera/camera/depth/color/points → (a) 카메라 원점 거리 < min_range 제거 (b) voxel 격자에서 점 수 < min_points_per_voxel 인 복셀의 점 제거
  → /camera/depth/points_filtered (프레임·stamp·필드 그대로, 바이트 행만 추린다 — 재직렬화 없음, 14k점 15Hz 에 수 ms).
  STVL depth_mark/depth_clear 는 이 토픽을 본다 (nav2_params.yaml).

무엇이 아닌가: 바닥 판정(min_obstacle_height)·절두체 소거는 그대로 STVL 몫. 실물 얇은 물체(의자 다리 2 cm @1 m ≈ 7 px 폭)는
  복셀당 3점 이상이라 살아남는다 — 살아남는지는 job312/job248 로 측정한다.
"""
import time
import array
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2


class DepthRelay(Node):
    def __init__(self):
        super().__init__('depth_relay')
        self.declare_parameter('in_topic', '/camera/camera/depth/color/points')
        self.declare_parameter('out_topic', '/camera/depth/points_filtered')
        self.declare_parameter('max_range', 4.0)              # [m] D455 원거리 잡음(6~7 m 군집, 09-16 job338) 제거 + 점 수 절감
        self.declare_parameter('min_range', 0.45)             # [m] 카메라 원점 기준. 실측 사각지대 0.40, 아티팩트 0.36~0.38
        self.declare_parameter('voxel', 0.05)                 # [m] 이웃 셈 격자 (코스트맵 해상도와 같게)
        self.declare_parameter('min_points_per_voxel', 3)     # 비산점 2~4점/프레임이 여러 복셀에 흩어짐 → 복셀당 1~2점
        # 2026-09-14 §2.21 시간 지속성: 상자 앞 0.24 m 바닥의 한 점(0.80,+0.08, z 0.07)이 25 % 프레임에만(3프레임에 1번) 찍히는데
        #   mark_threshold 0 + 감쇠 60 s 로 영구 LETHAL 이 되어 입구를 0.24 m 앞당겼다(spd2/tc3/tc4 정체 셀). 실물 표면은 거의 매 프레임
        #   보이므로 "최근 N 프레임 중 M 프레임 이상 같은 복셀에 점이 있어야 통과" 로 거른다(nvblox TSDF 가중의 조잡한 판). 상자 앞면 139점/프레임·100 % → 통과.
        self.declare_parameter('persist_frames', 5)          # N
        self.declare_parameter('persist_min', 3)             # M (≥ N/2). 25 % 출현 점이 5 중 3 을 넘을 확률 ≈ 10 %, 4 면 1.5 %
        self.declare_parameter('process_every', 1)           # CPU 절약용(2 면 7.5 Hz): 0.08 m/s 로버엔 충분
        self.declare_parameter('log_period', 10.0)
        self.min_range = float(self.get_parameter('min_range').value)
        self.max_range = float(self.get_parameter('max_range').value)
        self.voxel = float(self.get_parameter('voxel').value)
        self.min_pts = int(self.get_parameter('min_points_per_voxel').value)
        self.pf = int(self.get_parameter('persist_frames').value)
        self.pm = int(self.get_parameter('persist_min').value)
        self.every = max(1, int(self.get_parameter('process_every').value))
        self.hist = []          # 최근 프레임들의 복셀 키(np.int64 배열) 링버퍼
        self.frame_i = 0
        self.sub = self.create_subscription(PointCloud2, self.get_parameter('in_topic').value, self.cb, qos_profile_sensor_data)
        self.pub = self.create_publisher(PointCloud2, self.get_parameter('out_topic').value, qos_profile_sensor_data)
        self.stat = dict(frames=0, n_in=0, n_out=0, drop_range=0, drop_iso=0, t_ms=0.0)
        self.create_timer(float(self.get_parameter('log_period').value), self.log)
        self.get_logger().info('depth_relay: min_range %.2f m, voxel %.2f m, min_points_per_voxel %d' % (self.min_range, self.voxel, self.min_pts))

    def cb(self, msg):
        self.frame_i += 1
        if self.frame_i % self.every:
            return
        t0 = time.monotonic()
        n = msg.width * msg.height
        if n == 0:
            self.pub.publish(msg); return
        offs = {f.name: f.offset for f in msg.fields}
        step = msg.point_step
        buf = np.frombuffer(msg.data, dtype=np.uint8).reshape(n, step)
        # xyz 를 바이트 버퍼 위의 strided float32 뷰로 읽는다 (복사 없음)
        x = np.ndarray((n,), np.float32, buf, offs['x'], (step,))
        y = np.ndarray((n,), np.float32, buf, offs['y'], (step,))
        z = np.ndarray((n,), np.float32, buf, offs['z'], (step,))
        finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
        r2 = x * x + y * y + z * z
        keep = finite & (r2 >= self.min_range * self.min_range) & (r2 <= self.max_range * self.max_range)
        drop_range = int(finite.sum() - keep.sum())
        idx = np.nonzero(keep)[0]
        drop_iso = 0
        if idx.size and self.min_pts > 1:
            inv = 1.0 / self.voxel
            ix = np.floor(x[idx] * inv).astype(np.int64)
            iy = np.floor(y[idx] * inv).astype(np.int64)
            iz = np.floor(z[idx] * inv).astype(np.int64)
            key = (ix + (1 << 20)) * (1 << 42) + (iy + (1 << 20)) * (1 << 21) + (iz + (1 << 20))
            _, inverse, counts = np.unique(key, return_inverse=True, return_counts=True)
            dense = counts[inverse] >= self.min_pts
            drop_iso = int(idx.size - dense.sum())
            idx = idx[dense]; key = key[dense]
        drop_pers = 0
        if idx.size and self.pf > 1 and self.pm > 1:
            # 시간 지속성: 이 프레임을 포함한 최근 pf 프레임 중 pm 프레임 이상에 같은 복셀이 있어야 남긴다
            ukeys = np.unique(key)
            cnt = np.ones(ukeys.size, dtype=np.int32)
            for hk in self.hist[-(self.pf - 1):]:
                cnt += np.isin(ukeys, hk, assume_unique=True)
            ok = ukeys[cnt >= self.pm]
            keep2 = np.isin(key, ok)
            drop_pers = int(idx.size - keep2.sum())
            self.hist.append(ukeys)
            if len(self.hist) > self.pf - 1:
                self.hist.pop(0)
            idx = idx[keep2]
        out = PointCloud2()
        out.header = msg.header
        out.height = 1
        out.width = int(idx.size)
        out.fields = msg.fields
        out.is_bigendian = msg.is_bigendian
        out.point_step = step
        out.row_step = step * int(idx.size)
        out.is_dense = True
        # ★ 2026-09-16 (job339 cProfile): bytes 를 넣으면 생성 메시지의 setter 가 바이트마다 isinstance 검사를 해
        #   콜백 시간의 95 %(12 s 중 10.5 s)를 먹었다(프레임당 14k점×16B). array('B') 는 검사 없이 통과한다.
        out.data = array.array('B', buf[idx].tobytes())
        self.pub.publish(out)
        s = self.stat
        s['frames'] += 1; s['n_in'] += n; s['n_out'] += int(idx.size); s['drop_range'] += drop_range; s['drop_iso'] += drop_iso
        s['drop_pers'] = s.get('drop_pers', 0) + drop_pers
        s['t_ms'] += (time.monotonic() - t0) * 1e3

    def log(self):
        s = self.stat
        if s['frames']:
            self.get_logger().info('%d 프레임: 입력 %.0f → 출력 %.0f 점/프레임, 근거리 제거 %.1f, 고립 제거 %.1f, 비지속 제거 %.1f 점/프레임, %.1f ms/프레임'
                                   % (s['frames'], s['n_in'] / s['frames'], s['n_out'] / s['frames'], s['drop_range'] / s['frames'], s['drop_iso'] / s['frames'], s.get('drop_pers', 0) / s['frames'], s['t_ms'] / s['frames']))
        for k in s:
            s[k] = 0


def main():
    rclpy.init()
    node = DepthRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
