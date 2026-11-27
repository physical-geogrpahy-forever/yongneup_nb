"""3.5-2.0 ka 유역 최대 산불잠재일수(동적, 정적 지형 모델)와 연강수량."""
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import thesis_style as ts

# 사용법: python plot_firedays.py [STATE_CUBE.npz] [기후 CSV] [출력폴더]
_HERE = Path(__file__).resolve().parent
CUBE_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else _HERE.parent / "results" / "final_fab30_20261113" / "FINAL_STATE_CUBE.npz"
CLIMATE_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else _HERE.parent / "data" / "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"
OUT_DIR = Path(sys.argv[3]) if len(sys.argv) > 3 else _HERE
STEM = "fig_firedays_3p5_2p0ka"

KA_OLD, KA_YOUNG = 3.5, 2.0
# Park et al. (2021)의 대형 목탄 산불 시기 (cal kyr BP)
FIRE_EPISODES = [(2.9, 2.7), (2.4, 2.3)]


def max_firedays(cube, mode: str) -> np.ndarray:
    land = cube[f"{mode}__land"].astype(bool)
    fire = np.where(land, cube[f"{mode}__firedays_node"], np.nan)
    return np.nanmax(fire, axis=(1, 2))


def main() -> None:
    cube = np.load(CUBE_PATH)
    ka = np.round(cube["times_ka"].astype(float), 1)
    fire = pd.DataFrame({"ka_BP": ka,
                         "dynamic_max_firedays": max_firedays(cube, "dynamic"),
                         "static_max_firedays": max_firedays(cube, "static")})
    raw = pd.read_csv(CLIMATE_PATH)
    clim = pd.DataFrame({"ka_BP": raw["ka_bp"].round(1),
                         "precipitation_mm": sum(raw[f"pr_raw_{m:02d}"] for m in range(1, 13))})
    data = fire.merge(clim, on="ka_BP", how="left")
    data = data[(data["ka_BP"] <= KA_OLD) & (data["ka_BP"] >= KA_YOUNG)].sort_values("ka_BP", ascending=False)
    data.to_csv(OUT_DIR / f"{STEM}.csv", index=False, encoding="utf-8-sig")

    ts.setup()
    fig, axes = plt.subplots(2, 1, figsize=(ts.WIDTH, 0.55 * ts.WIDTH), sharex=True,
                             constrained_layout=True, gridspec_kw={"height_ratios": [1.4, 1]})
    for ax in axes:
        for old, young in FIRE_EPISODES:
            ax.axvspan(old, young, color=ts.LIGHT, lw=0, zorder=0)
    ax = axes[0]
    ax.plot(data["ka_BP"], data["static_max_firedays"], **ts.STA, label="정적 지형 모델", clip_on=False)
    ax.plot(data["ka_BP"], data["dynamic_max_firedays"], **ts.DYN, label="동적 지형 모델")
    ax.set_ylim(0, 60)
    ax.spines["bottom"].set_position(("outward", 4))
    ax.set_ylabel("최대 산불잠재일수 (일)")
    ax.legend(loc="center left", handlelength=2.4)
    ax = axes[1]
    ax.plot(data["ka_BP"], data["precipitation_mm"], color=ts.INK, lw=1.0)
    ax.set_ylabel("연강수량 (mm)")
    ax.set_xlabel("연대 (ka BP)")
    ax.set_xlim(KA_OLD, KA_YOUNG)
    ax.set_xticks(np.arange(KA_OLD, KA_YOUNG - 0.01, -0.5))
    ax.set_xticks(np.arange(KA_OLD, KA_YOUNG - 0.01, -0.1), minor=True)
    for ax, letter in zip(axes, "ab"):
        ts.panel(ax, letter)
    ts.save(fig, OUT_DIR, STEM)


if __name__ == "__main__":
    main()
