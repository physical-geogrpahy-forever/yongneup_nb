"""동적 지형 모델의 0 ka 토심 분포와 3 ka의 PFT7 우점 격자, 두 코어 위치."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from pyproj import Transformer

import thesis_style as ts

ROOT = Path(__file__).resolve().parents[1]
CUBE = ROOT / "results" / "final_fab30_20261113" / "FINAL_STATE_CUBE.npz"
OUT_DIR = Path(__file__).resolve().parent
STEM = "fig_soil_pft7_maps"

RES = 30.0
GRID_X0, GRID_Y0 = 122623.3057, 625198.8839  # 최종 모델 격자 왼쪽 위 모서리(EPSG:5187)
_TR = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True)
CORES = {
    "A": _TR.transform(128 + 7 / 60 + 30.2 / 3600, 38 + 12 / 60 + 57.4 / 3600),   # Jang et al.(2011)
    "B": _TR.transform(128 + 7 / 60 + 25.1 / 3600, 38 + 12 / 60 + 54.40 / 3600),  # Park et al.(2021) YN-C
}


def main() -> None:
    ts.setup()
    d = np.load(CUBE)
    t = d["times_ka"]
    i0 = int(np.argmin(abs(t - 0.0)))
    i3 = int(np.argmin(abs(t - 3.0)))
    land = d["dynamic__land"][i0]
    sd0 = np.where(land, d["dynamic__soil_depth_m"][i0], np.nan)
    pft7 = d["dynamic__optpft_node"][i3] == 7
    ny, nx = land.shape
    ext = [GRID_X0 / 1000, (GRID_X0 + nx * RES) / 1000, (GRID_Y0 - ny * RES) / 1000, GRID_Y0 / 1000]

    # 그림 범위: 유역 둘레 2격자
    rows = np.where(land.any(1))[0]
    cols = np.where(land.any(0))[0]
    xl = (ext[0] + (cols.min() - 2) * RES / 1000, ext[0] + (cols.max() + 3) * RES / 1000)
    yl = (ext[3] - (rows.max() + 3) * RES / 1000, ext[3] - (rows.min() - 2) * RES / 1000)

    fig, axes = plt.subplots(1, 2, figsize=(ts.WIDTH, 0.5 * ts.WIDTH), constrained_layout=True)

    ax = axes[0]
    im = ax.imshow(sd0, cmap="YlOrBr", vmin=0, vmax=4, extent=ext, origin="upper",
                   interpolation="nearest")
    cb = fig.colorbar(im, ax=ax, shrink=0.7, pad=0.02, aspect=25)
    cb.set_label("토심 (m)")
    cb.outline.set_linewidth(0.6)

    ax = axes[1]
    base = np.where(land, np.where(pft7, 1.0, 0.0), np.nan)
    ax.imshow(base, cmap=ListedColormap([ts.LIGHT, ts.INK]), vmin=0, vmax=1, extent=ext,
              origin="upper", interpolation="nearest")
    ax.plot([], [], marker="s", ms=6, color=ts.INK, ls="none", label=f"PFT7 우점 격자 ({int(pft7.sum())}개)")
    ax.plot([], [], marker="s", ms=6, color=ts.LIGHT, ls="none", label="그 밖의 격자")
    ax.legend(loc="lower left", handletextpad=0.4, borderaxespad=0.2)

    for ax, letter in zip(axes, "ab"):
        ax.contour(land.astype(float), levels=[0.5], extent=ext, origin="upper",
                   colors=ts.INK, linewidths=0.8)
        for lab, (x, y) in CORES.items():
            cx, cy = x / 1000, y / 1000
            ax.plot(cx, cy, marker="o", ms=5, mfc="white", mec=ts.INK, mew=0.9, ls="none", zorder=5)
            dx, ha = (0.03, "left") if lab == "A" else (-0.03, "right")
            ax.text(cx + dx, cy, lab, ha=ha, va="center", zorder=6,
                    bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none", alpha=0.8))
        ax.set_xlim(*xl)
        ax.set_ylim(*yl)
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
