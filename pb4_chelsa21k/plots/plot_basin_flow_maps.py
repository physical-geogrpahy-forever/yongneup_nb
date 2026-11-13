"""용늪 최종 유역(FABDEM 30 m)의 유역도, D8 흐름방향도, 누적흐름도.

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

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from matplotlib.colors import LightSource, LogNorm, LinearSegmentedColormap
from rasterio.warp import Resampling, reproject

_HERE = Path(__file__).resolve().parent
DEM_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else _HERE.parent / "data" / "FABDEM_V1-2_yongneup_region_EPSG5187_27p4m.tif"
OUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else _HERE
STEM = "YONGNEUP_FINAL_basin_flowdir_flowacc"

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

BLUE_SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def set_korean_font() -> None:
    candidates = ["Noto Sans CJK KR", "Noto Sans KR", "NanumGothic", "Malgun Gothic"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


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


def scalebar(ax, x0, y0, length_m=200):
    ax.plot([x0, x0 + length_m / 1000], [y0, y0], color="#1f1f1f", lw=2.5, solid_capstyle="butt")
    ax.text(x0 + length_m / 2000, y0 + 0.03, f"{length_m} m", ha="center", va="bottom", fontsize=8, color="#1f1f1f")


def north(ax, x, y):
    ax.annotate("N", xy=(x, y), xytext=(x, y - 0.12), ha="center", va="center", fontsize=9, color="#1f1f1f",
                arrowprops=dict(arrowstyle="-|>", color="#1f1f1f", lw=1.2))


def main() -> None:
    set_korean_font()
    z, T = load_dem()
    F = priority_flood(z)
    d = d8(F)
    acc = accumulate(F, d)
    oi, oj = OUTLET_RC[0] + PAD, OUTLET_RC[1] + PAD
    basin = catchment(d, oi, oj)
    n = int(basin.sum())
    print(f"유역 격자 {n}개, {n * RES * RES / 1e4:.2f} ha, 출구 누적 {acc[oi, oj]:.0f}개")
    if n != N_CELLS_EXPECTED:
        raise SystemExit(f"유역 격자 수가 최종 모델({N_CELLS_EXPECTED})과 다릅니다: {n}")

    # 그림 범위: 유역 주변 6격자
    rows = np.where(basin.any(1))[0]
    cols = np.where(basin.any(0))[0]
    m = 6
    r1, r2 = rows.min() - m, rows.max() + m + 1
    c1, c2 = cols.min() - m, cols.max() + m + 1
    sl = (slice(r1, r2), slice(c1, c2))
    zc, bc, dc, ac = z[sl], basin[sl], d[sl], acc[sl]
    x0 = (T.c + c1 * RES) / 1000.0
    y1 = (T.f - r1 * RES) / 1000.0
    ext = [x0, x0 + zc.shape[1] * RES / 1000.0, y1 - zc.shape[0] * RES / 1000.0, y1]
    ox, oy = (T.c + (oj + 0.5) * RES) / 1000.0, (T.f - (oi + 0.5) * RES) / 1000.0
    cx, cy = CORE_XY[0] / 1000.0, CORE_XY[1] / 1000.0

    ls = LightSource(azdeg=315, altdeg=45)
    hs = ls.hillshade(np.nan_to_num(zc, nan=np.nanmean(zc)), vert_exag=2.0, dx=RES, dy=RES)

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 6.2), constrained_layout=True)
    ink, muted = "#1f1f1f", "#5f5e5a"

    # (a) 유역
    ax = axes[0]
    ax.imshow(hs, cmap="gray", extent=ext, origin="upper", vmin=0, vmax=1, alpha=0.55)
    elev = ax.imshow(np.where(bc, zc, np.nan), cmap=LinearSegmentedColormap.from_list("e", BLUE_SEQ[:5][::-1]),
                     extent=ext, origin="upper", alpha=0.75)
    cs = ax.contour(zc, levels=np.arange(1100, 1320, 20), extent=ext, origin="upper",
                    colors=muted, linewidths=0.5)
    ax.clabel(cs, levels=cs.levels[::2], fontsize=7, fmt="%d", inline=True)
    outline(ax, bc, ext, colors=ink, linewidths=1.6)
    cb = fig.colorbar(elev, ax=ax, shrink=0.75, pad=0.02)
    cb.set_label("고도 (m)", color=ink)
    ax.set_title("(a) 유역 (656격자, 59.0 ha)", loc="left", fontsize=11, color=ink)

    # (b) D8 흐름방향
    ax = axes[1]
    ax.imshow(hs, cmap="gray", extent=ext, origin="upper", vmin=0, vmax=1, alpha=0.45)
    ii, jj = np.where(bc & (dc >= 0))
    U = np.array([N8[k][1] for k in dc[ii, jj]], float)
    V = np.array([-N8[k][0] for k in dc[ii, jj]], float)
    L = np.hypot(U, V)
    xs = ext[0] + (jj + 0.5) * RES / 1000.0
    ys = ext[3] - (ii + 0.5) * RES / 1000.0
    ax.quiver(xs, ys, U / L, V / L, color=BLUE_SEQ[5], scale=55, width=0.0032,
              headwidth=3.5, headlength=4, headaxislength=3.5, pivot="middle")
    outline(ax, bc, ext, colors=ink, linewidths=1.6)
    ax.set_title("(b) D8 흐름방향", loc="left", fontsize=11, color=ink)

    # (c) 누적흐름
    ax = axes[2]
    ax.imshow(hs, cmap="gray", extent=ext, origin="upper", vmin=0, vmax=1, alpha=0.45)
    area = np.where(bc, ac * RES * RES / 1e4, np.nan)
    im = ax.imshow(area, cmap=LinearSegmentedColormap.from_list("acc", BLUE_SEQ),
                   norm=LogNorm(vmin=RES * RES / 1e4, vmax=np.nanmax(area)), extent=ext, origin="upper")
    outline(ax, bc, ext, colors=ink, linewidths=1.6)
    cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
    cb.set_label("기여면적 (ha, 로그)", color=ink)
    ax.set_title("(c) 누적흐름(D8 기여면적)", loc="left", fontsize=11, color=ink)

    for ax in axes:
        ax.plot(ox, oy, marker="v", ms=9, color="#ffffff", mec=ink, mew=1.2, zorder=5)
        ax.plot(cx, cy, marker="*", ms=12, color="#ffffff", mec=ink, mew=1.0, zorder=5)
        ax.set_xlim(ext[0], ext[1])
        ax.set_ylim(ext[2], ext[3])
        ax.set_aspect("equal")
        ax.set_xlabel("X (km, EPSG:5187)", color=muted, fontsize=9)
        ax.tick_params(colors=muted, labelsize=8)
        for s in ax.spines.values():
            s.set_color("#c3c2bd")
        scalebar(ax, ext[0] + 0.06, ext[2] + 0.06)
        north(ax, ext[1] - 0.08, ext[3] - 0.06)
    axes[0].set_ylabel("Y (km, EPSG:5187)", color=muted, fontsize=9)
    axes[0].plot([], [], marker="v", ls="none", ms=8, color="#ffffff", mec=ink, label="유역 출구")
    axes[0].plot([], [], marker="*", ls="none", ms=10, color="#ffffff", mec=ink, label="용늪")
    axes[0].legend(loc="lower right", fontsize=8, frameon=True, framealpha=0.9)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{STEM}.png", dpi=300)
    fig.savefig(OUT_DIR / f"{STEM}.svg")
    print(OUT_DIR / f"{STEM}.png")


if __name__ == "__main__":
    main()
