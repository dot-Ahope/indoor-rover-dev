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
        self.declare_parameter('min_range', 0.45)             # [m] 카메라 원점 기준. 실측 사각지대 0.40, 아티팩트 0.36~0.38
        self.declare_parameter('voxel', 0.05)                 # [m] 이웃 셈 격자 (코스트맵 해상도와 같게)
        self.declare_parameter('min_points_per_voxel', 3)     # 비산점 2~4점/프레임이 여러 복셀에 흩어짐 → 복셀당 1~2점
        self.declare_parameter('log_period', 10.0)
        self.min_range = float(self.get_parameter('min_range').value)
        self.voxel = float(self.get_parameter('voxel').value)
        self.min_pts = int(self.get_parameter('min_points_per_voxel').value)
        self.sub = self.create_subscription(PointCloud2, self.get_parameter('in_topic').value, self.cb, qos_profile_sensor_data)
        self.pub = self.create_publisher(PointCloud2, self.get_parameter('out_topic').value, qos_profile_sensor_data)
        self.stat = dict(frames=0, n_in=0, n_out=0, drop_range=0, drop_iso=0, t_ms=0.0)
        self.create_timer(float(self.get_parameter('log_period').value), self.log)
        self.get_logger().info('depth_relay: min_range %.2f m, voxel %.2f m, min_points_per_voxel %d' % (self.min_range, self.voxel, self.min_pts))

    def cb(self, msg):
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
        keep = finite & (r2 >= self.min_range * self.min_range)
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
            idx = idx[dense]
        out = PointCloud2()
        out.header = msg.header
        out.height = 1
        out.width = int(idx.size)
        out.fields = msg.fields
        out.is_bigendian = msg.is_bigendian
        out.point_step = step
        out.row_step = step * int(idx.size)
        out.is_dense = True
        out.data = buf[idx].tobytes()
        self.pub.publish(out)
        s = self.stat
        s['frames'] += 1; s['n_in'] += n; s['n_out'] += int(idx.size); s['drop_range'] += drop_range; s['drop_iso'] += drop_iso
        s['t_ms'] += (time.monotonic() - t0) * 1e3

    def log(self):
        s = self.stat
        if s['frames']:
            self.get_logger().info('%d 프레임: 입력 %.0f → 출력 %.0f 점/프레임, 근거리 제거 %.1f, 고립 제거 %.1f 점/프레임, %.1f ms/프레임'
                                   % (s['frames'], s['n_in'] / s['frames'], s['n_out'] / s['frames'], s['drop_range'] / s['frames'], s['drop_iso'] / s['frames'], s['t_ms'] / s['frames']))
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
