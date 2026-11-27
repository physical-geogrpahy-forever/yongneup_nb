"""용늪 유역(FABDEM 30 m)과 유출구, D8 기여면적.

results/final_fab30_20261113/tools/build_fabdem_basin_grid.py와 같은 절차를 따른다.
  1. FABDEM V1-2(EPSG:5187, 27.4 m)를 최종 모델 격자에 맞춘 30 m 격자로 쌍선형 보간
  2. 경계에서 시작하는 우선순위 채움(priority flood, 1e-4 m 증분)으로 와지 제거
  3. D8 최급경사 방향, 상류 격자 수 누적
  4. 최종 모델의 출구 격자에서 상류 유역 추적

사용법: python plot_basin_flow_maps.py [FABDEM tif] [출력폴더]
"""
from pathlib import Path
import heapq
import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from matplotlib.colors import LightSource, LogNorm
from matplotlib.ticker import FixedLocator, FuncFormatter

import matplotlib.patheffects as pe

import thesis_style as ts
from rasterio.warp import Resampling, reproject
from scipy.ndimage import distance_transform_edt

_HERE = Path(__file__).resolve().parent
DEM_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else _HERE.parent / "data" / "FABDEM_V1-2_yongneup_region_EPSG5187_27p4m.tif"
OUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else _HERE
STEM = "fig_basin_analysis"

# 최종 모델 격자(embedded_inputs/yongneup_exact20m/PB4STUDIO_EXACT_GRID.json)
RES = 30.0
GRID_X0, GRID_Y0 = 122623.3057, 625198.8839
GRID_SHAPE = (41, 36)
OUTLET_RC = (21, 29)
N_CELLS_EXPECTED = 656
CORE_XY = (123245.19, 624269.79)  # 용늪 지점(Jang et al., 2011의 좌표)
CRS = "EPSG:5187"

# 계산 창: 최종 격자 원점에서 정수 격자만큼 넓힌 2.4 km 범위
PAD = 30
WIN_X0 = GRID_X0 - PAD * RES
WIN_Y0 = GRID_Y0 + PAD * RES
WIN_SHAPE = (GRID_SHAPE[0] + 2 * PAD, GRID_SHAPE[1] + 2 * PAD)

N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def load_dem() -> tuple[np.ndarray, Affine]:
    T = Affine(RES, 0, WIN_X0, 0, -RES, WIN_Y0)
    z = np.full(WIN_SHAPE, np.nan)
    with rasterio.open(DEM_PATH) as s:
        reproject(rasterio.band(s, 1), z, dst_transform=T, dst_crs=CRS,
                  resampling=Resampling.bilinear, src_nodata=-9999, dst_nodata=np.nan)
    return z, T


def priority_flood(z: np.ndarray) -> np.ndarray:
    m = np.isfinite(z)
    ny, nx = z.shape
    F = np.full(z.shape, np.nan)
    done = np.zeros(z.shape, bool)
    pq = []
    for i in range(ny):
        for j in range(nx):
            edge = i in (0, ny - 1) or j in (0, nx - 1) or any(
                not m[i + a, j + b] for a, b in N8 if 0 <= i + a < ny and 0 <= j + b < nx)
            if m[i, j] and edge:
                F[i, j] = z[i, j]
                done[i, j] = True
                heapq.heappush(pq, (z[i, j], i, j))
    while pq:
        e, i, j = heapq.heappop(pq)
        for a, b in N8:
            p, q = i + a, j + b
            if 0 <= p < ny and 0 <= q < nx and m[p, q] and not done[p, q]:
                done[p, q] = True
                F[p, q] = max(z[p, q], e + 1e-4)
                heapq.heappush(pq, (F[p, q], p, q))
    return F


def d8(F: np.ndarray) -> np.ndarray:
    """수신 격자의 방향 번호(N8 인덱스), 없으면 -1."""
    ny, nx = F.shape
    d = -np.ones(F.shape, dtype=int)
    for i in range(ny):
        for j in range(nx):
            if not np.isfinite(F[i, j]):
                continue
            best, bs = -1, 0.0
            for k, (a, b) in enumerate(N8):
                p, q = i + a, j + b
                if 0 <= p < ny and 0 <= q < nx and np.isfinite(F[p, q]):
                    sl = (F[i, j] - F[p, q]) / np.hypot(a, b)
                    if sl > bs:
                        bs, best = sl, k
            d[i, j] = best
    return d


def accumulate(F: np.ndarray, d: np.ndarray) -> np.ndarray:
    ny, nx = F.shape
    acc = np.where(np.isfinite(F), 1.0, 0.0)
    order = np.argsort(-np.nan_to_num(F, nan=-1e9).ravel())
    for k in order:
        i, j = divmod(int(k), nx)
        if d[i, j] >= 0:
            a, b = N8[d[i, j]]
            acc[i + a, j + b] += acc[i, j]
    return acc


def catchment(d: np.ndarray, oi: int, oj: int) -> np.ndarray:
    ny, nx = d.shape
    basin = np.zeros(d.shape, bool)
    basin[oi, oj] = True
    stack = [(oi, oj)]
    while stack:
        i, j = stack.pop()
        for k, (a, b) in enumerate(N8):
            p, q = i - a, j - b  # (p,q)가 (i,j)로 흐르면 d[p,q]==k
            if 0 <= p < ny and 0 <= q < nx and not basin[p, q] and d[p, q] == k:
                basin[p, q] = True
                stack.append((p, q))
    return basin


def outline(ax, mask, extent, **kw):
    ax.contour(mask.astype(float), levels=[0.5], extent=extent, origin="upper", **kw)


def scalebar(ax, x0, y0, length_km=0.2):
    ax.plot([x0, x0 + length_km], [y0, y0], color=ts.INK, lw=1.6, solid_capstyle="butt")
    ax.text(x0 + length_km / 2, y0 + 0.025, f"{int(length_km * 1000)} m", ha="center", va="bottom")


def north(ax, x, y):
    ax.annotate("", xy=(x, y), xytext=(x, y - 0.12),
                arrowprops=dict(arrowstyle="-|>", color=ts.INK, lw=0.8, mutation_scale=9))
    ax.text(x, y - 0.14, "N", ha="center", va="top")


def main() -> None:
    ts.setup()
    z, T = load_dem()
    F = priority_flood(z)
    d = d8(F)
    acc = accumulate(F, d)
    oi, oj = OUTLET_RC[0] + PAD, OUTLET_RC[1] + PAD
    basin = catchment(d, oi, oj)
    n = int(basin.sum())
    print(f"유역 격자 {n}개, {n * RES * RES / 1e4:.2f} ha")
    if n != N_CELLS_EXPECTED:
        raise SystemExit(f"유역 격자 수가 모델 유역({N_CELLS_EXPECTED})과 다름: {n}")

    rows = np.where(basin.any(1))[0]
    cols = np.where(basin.any(0))[0]
    m = 5
    sl = (slice(rows.min() - m, rows.max() + m + 1), slice(cols.min() - m, cols.max() + m + 1))
    r1, c1 = sl[0].start, sl[1].start
    zc, bc, ac = z[sl], basin[sl], acc[sl]
    x0 = (T.c + c1 * RES) / 1000.0
    y1 = (T.f - r1 * RES) / 1000.0
    ext = [x0, x0 + zc.shape[1] * RES / 1000.0, y1 - zc.shape[0] * RES / 1000.0, y1]
    ox, oy = (T.c + (oj + 0.5) * RES) / 1000.0, (T.f - (oi + 0.5) * RES) / 1000.0
    cx, cy = CORE_XY[0] / 1000.0, CORE_XY[1] / 1000.0

    # 자료 범위 밖은 가장 가까운 격자 값으로 채워 음영 계산의 가장자리 효과를 없앤다
    idx = distance_transform_edt(~np.isfinite(zc), return_distances=False, return_indices=True)
    hs = LightSource(azdeg=315, altdeg=45).hillshade(zc[tuple(idx)], vert_exag=2.0, dx=RES, dy=RES)
    hs = np.ma.masked_where(~np.isfinite(zc), hs)
    veil = np.ma.masked_where(bc | ~np.isfinite(zc), np.ones_like(zc))
    halo = [pe.withStroke(linewidth=2.2, foreground="white")]

    fig, axes = plt.subplots(1, 2, figsize=(ts.WIDTH, 0.5 * ts.WIDTH), constrained_layout=True)

    ax = axes[0]
    ax.imshow(hs, cmap="gray", extent=ext, origin="upper", vmin=0, vmax=1)
    ax.imshow(veil, cmap="gray", vmin=0, vmax=1, alpha=0.45, extent=ext, origin="upper")
    cs = ax.contour(zc, levels=np.arange(1100, 1320, 20), extent=ext, origin="upper",
                    colors=ts.INK, linewidths=0.35)
    for t in ax.clabel(cs, levels=[l for l in cs.levels if l % 40 == 0], fontsize=6, fmt="%d", inline=True):
        t.set_path_effects(halo)
    outline(ax, bc, ext, colors=ts.INK, linewidths=1.0)
    scalebar(ax, ext[0] + 0.05, ext[2] + 0.05)
    north(ax, ext[1] - 0.06, ext[3] - 0.04)

    ax = axes[1]
    ax.imshow(hs, cmap="gray", extent=ext, origin="upper", vmin=0, vmax=1, alpha=0.35)
    area = np.where(bc, ac * RES * RES / 1e4, np.nan)
    im = ax.imshow(area, cmap="Blues", norm=LogNorm(vmin=0.09, vmax=60), extent=ext, origin="upper")
    outline(ax, bc, ext, colors=ts.INK, linewidths=1.0)
    cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02, aspect=25)
    ticks = [0.1, 1, 10, 50]
    cb.ax.yaxis.set_major_locator(FixedLocator(ticks))
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    cb.ax.minorticks_off()
    cb.outline.set_linewidth(0.6)
    cb.set_label("기여면적 (ha)")

    for ax, letter in zip(axes, "ab"):
        ax.plot(ox, oy, marker="v", ms=6, color=ts.INK, ls="none", zorder=5)
        ax.plot(cx, cy, marker="o", ms=5, mfc="white", mec=ts.INK, mew=0.9, ls="none", zorder=5)
        ax.text(ox + 0.03, oy + 0.03, "유출구", ha="left", va="bottom", zorder=6, path_effects=halo)
        ax.text(cx + 0.03, cy - 0.03, "용늪", ha="left", va="top", zorder=6, path_effects=halo)
        ax.set_xlim(ext[0], ext[1])
        ax.set_ylim(ext[2], ext[3])
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(True)
            sp.set_linewidth(0.6)
        ts.panel(ax, letter)

    ts.save(fig, OUT_DIR, STEM)


if __name__ == "__main__":
    main()
