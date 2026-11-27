"""유역 평균 고도, 토심, NPP의 시간 변화 (동적, 정적 지형 모델, 59.0 ha 유역)."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import thesis_style as ts

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results" / "final_fab30_20261113" / "reference_run"
OUT_DIR = Path(__file__).resolve().parent
STEM = "fig_mean_timeseries"

PANELS = [
    ("mean_elevation_m", "평균 고도 (m)"),
    ("mean_soil_depth_m", "평균 토심 (m)"),
    ("mean_npp", "평균 NPP (gC/m²/yr)"),
]


def load(case: str) -> pd.DataFrame:
    df = pd.read_csv(RUN / case / "summary_timeseries.csv", encoding="utf-8-sig")
    return df.sort_values("ka_bp", ascending=False)


def main() -> None:
    ts.setup()
    dyn, sta = load("model_dynamic"), load("model_static")
    fig, axes = plt.subplots(3, 1, figsize=(ts.WIDTH, 0.75 * ts.WIDTH), sharex=True,
                             constrained_layout=True)
    for ax, (col, label), letter in zip(axes, PANELS, "abc"):
        ax.plot(sta["ka_bp"], sta[col], **ts.STA, label="정적 지형 모델")
        ax.plot(dyn["ka_bp"], dyn[col], **ts.DYN, label="동적 지형 모델")
        ax.set_ylabel(label)
        ts.panel(ax, letter)
    axes[0].ticklabel_format(axis="y", useOffset=False, style="plain")
    axes[0].legend(loc="upper left", handlelength=2.4)
    axes[-1].set_xlabel("연대 (ka BP)")
    axes[-1].set_xlim(21, 0)
    axes[-1].set_xticks(np.arange(21, -0.1, -3))
    axes[-1].set_xticks(np.arange(21, -0.1, -1), minor=True)
    ts.save(fig, OUT_DIR, STEM)


if __name__ == "__main__":
    main()
