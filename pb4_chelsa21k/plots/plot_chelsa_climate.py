"""CHELSA-TraCE21k 용늪 격자의 연평균 기온과 연강수량 (21 ka BP-현재)."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import thesis_style as ts

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv"
OUT_DIR = Path(__file__).resolve().parent
STEM = "fig_climate_chelsa"


def annual_climate(df: pd.DataFrame) -> pd.DataFrame:
    t = [((df[f"tasmin_raw_{m:02d}"] + df[f"tasmax_raw_{m:02d}"]) / 2.0) - 273.15 for m in range(1, 13)]
    p = [df[f"pr_raw_{m:02d}"] for m in range(1, 13)]
    return pd.DataFrame({
        "ka": df["ka_bp"],
        "t": pd.concat(t, axis=1).mean(axis=1),
        "p": pd.concat(p, axis=1).sum(axis=1),
    })


def main() -> None:
    ts.setup()
    c = annual_climate(pd.read_csv(DATA_PATH))
    fig, axes = plt.subplots(2, 1, figsize=(ts.WIDTH, 0.55 * ts.WIDTH), sharex=True,
                             constrained_layout=True)
    axes[0].plot(c["ka"], c["t"], color=ts.INK, lw=1.0)
    axes[0].set_ylabel("연평균 기온 (°C)")
    axes[1].plot(c["ka"], c["p"], color=ts.INK, lw=1.0)
    axes[1].set_ylabel("연강수량 (mm)")
    axes[1].set_xlabel("연대 (ka BP)")
    axes[1].set_xlim(21, 0)
    axes[1].set_xticks(np.arange(21, -0.1, -3))
    axes[1].set_xticks(np.arange(21, -0.1, -1), minor=True)
    for ax, letter in zip(axes, "ab"):
        ts.panel(ax, letter)
    ts.save(fig, OUT_DIR, STEM)


if __name__ == "__main__":
    main()
