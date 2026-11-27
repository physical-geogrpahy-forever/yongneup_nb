"""산불잠재일수: (a) 산불잠재일수가 있는 격자의 비율, (b) 홀로세 토심 구간별 산불잠재일수,
(c) 홀로세 동안 산불잠재일수가 나타난 시점의 비율 (동적 지형 모델)."""
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import thesis_style as ts

# 사용법: python plot_firedays.py [STATE_CUBE.npz] [출력폴더]
_HERE = Path(__file__).resolve().parent
CUBE_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else _HERE.parent / "results" / "final_fab30_20261113" / "FINAL_STATE_CUBE.npz"
OUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else _HERE
STEM = "fig_firedays"

RES = 30.0
OUTLET_RC = (21, 29)
HOLOCENE_KA = 11.7
PARK_SPAN = (3.181, 0.515)               # Park et al. (2021) YN-C 화분 자료 연대 범위 (cal kyr BP)
FIRE_EPISODES = [(2.9, 2.7), (2.4, 2.3)]  # Park et al. (2021) 대형 목탄 산불 시기
DEPTH_BINS = [(0.0, 0.05), (0.05, 0.1), (0.1, 0.3), (0.3, 1.0), (1.0, np.inf)]
DEPTH_LABELS = ["< 0.05", "0.05–0.1", "0.1–0.3", "0.3–1", "≥ 1"]


def fire_fraction(cube, mode: str) -> np.ndarray:
    land = cube[f"{mode}__land"].astype(bool)
    fire = cube[f"{mode}__firedays_node"]
    return 100.0 * ((fire > 0) & land).sum(axis=(1, 2)) / land.sum(axis=(1, 2))


def main() -> None:
    cube = np.load(CUBE_PATH)
    ka = np.round(cube["times_ka"].astype(float), 1)
    order = np.argsort(-ka)
    dyn_frac, sta_frac = fire_fraction(cube, "dynamic"), fire_fraction(cube, "static")

    hol = ka <= HOLOCENE_KA
    land = cube["dynamic__land"].astype(bool)
    fire = cube["dynamic__firedays_node"]
    depth = cube["dynamic__soil_depth_m"]
    sel = land[hol] & np.isfinite(fire[hol])
    fv, hv = fire[hol][sel], depth[hol][sel]
    groups = [fv[(hv >= a) & (hv < b)] for a, b in DEPTH_BINS]
    freq = np.where(land[0], ((fire[hol] > 0) & land[hol]).mean(axis=0), np.nan)

    pd.DataFrame({"ka_BP": ka[order], "dynamic_fire_cell_pct": dyn_frac[order],
                  "static_fire_cell_pct": sta_frac[order]}).to_csv(
        OUT_DIR / f"{STEM}_cells.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"soil_depth_m": DEPTH_LABELS, "n": [len(g) for g in groups],
                  "median_firedays": [float(np.median(g)) for g in groups]}).to_csv(
        OUT_DIR / f"{STEM}_depth.csv", index=False, encoding="utf-8-sig")

    ts.setup()
    fig = plt.figure(figsize=(ts.WIDTH, 0.78 * ts.WIDTH), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.25], width_ratios=[1.15, 1])

    ax = fig.add_subplot(gs[0, :])
    ax.axvspan(*PARK_SPAN, color=ts.LIGHT, lw=0, zorder=0)
    for old, young in FIRE_EPISODES:
        ax.plot([old, young], [9.6, 9.6], color=ts.INK, lw=2.5, solid_capstyle="butt")
    ax.plot(ka[order], sta_frac[order], **ts.STA, label="정적 지형 모델", clip_on=False)
    ax.plot(ka[order], dyn_frac[order], **ts.DYN, label="동적 지형 모델")
    ax.set_xlim(21, 0)
    ax.set_xticks(np.arange(21, -0.1, -3))
    ax.set_xticks(np.arange(21, -0.1, -1), minor=True)
    ax.set_ylim(0, 10)
    ax.spines["bottom"].set_position(("outward", 4))
    ax.set_xlabel("연대 (ka BP)")
    ax.set_ylabel("산불잠재일수가 있는 격자 (%)")
    ax.legend(loc="upper left", handlelength=2.4)
    ts.panel(ax, "a")

    ax = fig.add_subplot(gs[1, 0])
    ax.boxplot(groups, widths=0.55, whis=(0, 100), patch_artist=True,
               boxprops=dict(facecolor=ts.LIGHT, edgecolor=ts.INK, lw=0.7),
               medianprops=dict(color=ts.INK, lw=1.2),
               whiskerprops=dict(color=ts.INK, lw=0.7), capprops=dict(color=ts.INK, lw=0.7))
    ax.set_xticks(range(1, len(DEPTH_LABELS) + 1), DEPTH_LABELS)
    ax.set_xlabel("토심 (m)")
    ax.set_ylabel("산불잠재일수 (일)")
    ax.set_ylim(0, 65)
    ts.panel(ax, "b")

    ax = fig.add_subplot(gs[1, 1])
    ny, nx = freq.shape
    ext = [0, nx * RES / 1000, 0, ny * RES / 1000]
    im = ax.imshow(np.where(freq > 0, freq * 100, np.nan), cmap="Reds", vmin=0, vmax=100,
                   extent=ext, origin="upper", interpolation="nearest")
    ax.imshow(np.where(land[0] & ~(freq > 0), 1.0, np.nan), cmap="gray", vmin=0, vmax=1.25,
              extent=ext, origin="upper", interpolation="nearest", alpha=0.18)
    ax.contour(land[0].astype(float), levels=[0.5], extent=ext, origin="upper", colors=ts.INK, linewidths=0.8)
    oi, oj = OUTLET_RC
    ax.plot((oj + 0.5) * RES / 1000, ext[3] - (oi + 0.5) * RES / 1000, marker="v", ms=5, color=ts.INK)
    ax.plot([0.08, 0.28], [0.08, 0.08], color=ts.INK, lw=1.4, solid_capstyle="butt")
    ax.text(0.18, 0.11, "200 m", ha="center", va="bottom", fontsize=7)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(True)
        sp.set_linewidth(0.6)
    cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02, aspect=22)
    cb.outline.set_linewidth(0.6)
    cb.set_label("산불잠재일수가 있는 시점 (%)")
    ts.panel(ax, "c")

    ts.save(fig, OUT_DIR, STEM)


if __name__ == "__main__":
    main()
